"""Grok coordinator session, the observable router and playbook boundary.

The session reads the host-agnostic router policy and adopts playbook-runner
in-process. It does not spawn that role, and a worker cannot call spawn-worker.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict, cast

ROOT = Path(__file__).resolve().parents[2]
INVOCATION_PATH = Path(__file__).with_name("invocation.json")
POLICY_PATH = ROOT / "core/skills/poteto-mode/router-policy.json"
BUGFIX_POLICY_PATH = ROOT / "core/skills/poteto-mode/playbooks/bug-fix.policy.json"
SKILL_PATH = ROOT / "core/skills/poteto-mode/SKILL.md"
AGENTS = ROOT / "core/agents"

MODEL_ROLES = frozenset({"xhigh", "max", "fast"})
ISOLATIONS = frozenset({"isolated", "same-tree"})


class ClarificationRequired(Exception):
    """Engineering execution waits until Matt HITL clarifies the request."""


class NestedSpawnRejected(Exception):
    """A worker called spawn-worker. This host does not nest workers."""


class UnknownInvocation(Exception):
    """The token or explicit skill is outside this router surface."""


class UnknownRole(Exception):
    """The spawn-worker role is not one of the core agents."""


@dataclass(frozen=True)
class Prompt:
    """Facts about a request that the router can observe."""

    text: str
    data_shape: str | None = None
    repro: str | None = None
    metric: str | None = None
    acceptance: str | None = None
    reported_defect: bool = False

    @property
    def settled(self) -> bool:
        return any(
            isinstance(value, str) and value.strip()
            for value in (self.data_shape, self.repro, self.metric, self.acceptance)
        )


@dataclass(frozen=True)
class JudgeAdvice:
    """Optional validation.judge prior. Unbound advice is not a gate."""

    status: Literal["unbound", "answered"] = "unbound"
    workflow: Literal["hitl", "playbook"] | None = None
    playbook: str | None = None


@dataclass(frozen=True)
class Decision:
    workflow: Literal["hitl", "playbook"]
    name: str
    waits_for_clarification: bool
    creates_tracker_packet: bool
    principles_active: bool
    judge_changed_outcome: bool


@dataclass(frozen=True)
class PlaybookRun:
    playbook: str
    runner: str
    adopted_in_session: bool
    creates_tracker_packet: bool
    testing_cadence: str
    testing_exception: str
    invoked_skills: tuple[str, ...]
    principles_active: bool


@dataclass(frozen=True)
class SpawnHandle:
    kind: Literal["worker", "adopted"]
    role: str
    native_type: str
    isolation: str
    model_role: str | None
    depth: int

    def spawn_worker(
        self,
        role: str,
        prompt: str,
        isolation: str | None = None,
        model_role: str | None = None,
    ) -> SpawnHandle:
        raise NestedSpawnRejected(
            f"{role} at depth {self.depth} cannot spawn ({prompt!r}, {isolation}, {model_role})"
        )


class TestingContract(TypedDict):
    cadence: str
    exception: str
    invokes_skill: str | None


class BugfixPolicy(TypedDict):
    name: str
    match: str
    requires_packet: bool
    runner: str
    in_step_delegate: str
    testing: TestingContract


class PlaybookEntry(TypedDict):
    name: str
    match: str


class PrinciplesPolicy(TypedDict):
    apply_during: str
    can_suppress_hitl: bool


class JudgePolicy(TypedDict):
    required: bool
    overrides_explicit: bool
    overrides_unscoped_gate: bool


class RouterPolicy(TypedDict):
    directory: str
    canonical_token: str
    aliases: list[str]
    hitl_entry: str
    explicit_hitl: list[str]
    principles: PrinciplesPolicy
    judge: JudgePolicy
    playbooks: list[PlaybookEntry]


class RunnerBinding(TypedDict):
    role: str
    placement: str


class Invocation(TypedDict):
    plugin_id: str
    canonical_token: str
    aliases: list[str]
    core_skill: str
    implicit_invocation: bool
    runner: RunnerBinding
    nested_spawn_worker: bool


def _load_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise TypeError(f"{path} must be a JSON object")
    return data


def _description(path: Path) -> str:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise RuntimeError(f"{path} is missing frontmatter")
    end = text.find("\n---", 4)
    header = text[4:end]
    for line in header.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError(f"{path} is missing a description")


def _agent_roles() -> frozenset[str]:
    return frozenset(path.stem for path in AGENTS.glob("*.md"))


class GrokCoordinator:
    """One Grok coordinator session. Both router tokens open the same skill."""

    def __init__(
        self, token: str, policy: RouterPolicy, invocation: Invocation
    ) -> None:
        self.token = token
        self._policy = policy
        self._invocation = invocation
        self.runner: str | None = None
        self.adopted_in_session = False
        self._spawns: list[SpawnHandle] = []

    @classmethod
    def open(cls, token: str) -> GrokCoordinator:
        policy = cast(RouterPolicy, _load_json(POLICY_PATH))
        invocation = cast(Invocation, _load_json(INVOCATION_PATH))
        _require_agreement(policy, invocation)
        allowed = {invocation["canonical_token"], *invocation["aliases"]}
        if token not in allowed:
            raise UnknownInvocation(token)
        return cls(token, policy, invocation)

    @property
    def plugin_id(self) -> str:
        return str(self._invocation["plugin_id"])

    @property
    def core_skill(self) -> str:
        return str(self._invocation["core_skill"])

    @property
    def canonical_token(self) -> str:
        return str(self._invocation["canonical_token"])

    @property
    def aliases(self) -> tuple[str, ...]:
        return tuple(self._invocation["aliases"])

    @property
    def tokens(self) -> tuple[str, ...]:
        return (self.canonical_token, *self.aliases)

    @property
    def implicit_invocation(self) -> bool:
        return bool(self._invocation["implicit_invocation"])

    @property
    def description(self) -> str:
        return _description(SKILL_PATH)

    @property
    def spawned_roles(self) -> tuple[str, ...]:
        return tuple(handle.role for handle in self._spawns if handle.kind == "worker")

    def route(
        self,
        prompt: Prompt,
        *,
        explicit: str | None = None,
        judge: JudgeAdvice | None = None,
    ) -> Decision:
        advice = judge or JudgeAdvice()
        if advice.status not in {"unbound", "answered"}:
            raise ValueError(advice.status)
        if explicit is not None:
            if explicit in self._policy["explicit_hitl"]:
                return self._decision("hitl", explicit)
            included = self._included(explicit)
            if included is not None:
                return self._decision(
                    "playbook",
                    explicit,
                    creates_packet=bool(self._bugfix()["requires_packet"]),
                )
            raise UnknownInvocation(explicit)
        if prompt.settled and prompt.reported_defect and self._matches_bug_fix():
            return self._decision(
                "playbook",
                "bug-fix",
                creates_packet=bool(self._bugfix()["requires_packet"]),
            )
        return self._decision("hitl", str(self._policy["hitl_entry"]))

    def begin(self, decision: Decision) -> PlaybookRun:
        if decision.waits_for_clarification or decision.workflow != "playbook":
            raise ClarificationRequired(decision.name)
        bug = self._bugfix()
        if decision.name != bug["name"]:
            raise UnknownInvocation(decision.name)
        runner = self._invocation["runner"]["role"]
        if self._invocation["runner"]["placement"] != "in-session":
            raise RuntimeError("playbook-runner must be adopted in this session")
        self.runner = runner
        self.adopted_in_session = True
        testing = bug["testing"]
        invoked: tuple[str, ...] = ()
        skill = testing["invokes_skill"]
        if skill:
            invoked = (skill,)
        return PlaybookRun(
            playbook=str(bug["name"]),
            runner=runner,
            adopted_in_session=True,
            creates_tracker_packet=bool(bug["requires_packet"]),
            testing_cadence=str(testing["cadence"]),
            testing_exception=str(testing["exception"]),
            invoked_skills=invoked,
            principles_active=decision.principles_active,
        )

    def spawn_worker(
        self,
        role: str,
        prompt: str,
        isolation: str | None = None,
        model_role: str | None = None,
    ) -> SpawnHandle:
        if not prompt.strip():
            raise ValueError("prompt is required")
        if model_role is not None and model_role not in MODEL_ROLES:
            raise ValueError(model_role)
        if isolation is not None and isolation not in ISOLATIONS:
            raise ValueError(isolation)
        chosen = isolation or "same-tree"
        runner = self._invocation["runner"]["role"]
        if role == runner:
            self.runner = role
            self.adopted_in_session = True
            return SpawnHandle(
                kind="adopted",
                role=role,
                native_type=f"{self.plugin_id}:{role}",
                isolation=chosen,
                model_role=model_role,
                depth=0,
            )
        if role not in _agent_roles():
            raise UnknownRole(role)
        handle = SpawnHandle(
            kind="worker",
            role=role,
            native_type=f"{self.plugin_id}:{role}",
            isolation=chosen,
            model_role=model_role,
            depth=1,
        )
        self._spawns.append(handle)
        return handle

    def _included(self, name: str) -> PlaybookEntry | None:
        for item in self._policy["playbooks"]:
            if item["name"] == name:
                return item
        return None

    def _matches_bug_fix(self) -> bool:
        included = self._included("bug-fix")
        return included is not None and included["match"] == "reported-defect"

    def _bugfix(self) -> BugfixPolicy:
        return cast(BugfixPolicy, _load_json(BUGFIX_POLICY_PATH))

    def _decision(
        self,
        workflow: Literal["hitl", "playbook"],
        name: str,
        *,
        creates_packet: bool = False,
    ) -> Decision:
        principles = self._policy["principles"]
        active = workflow == "playbook" and principles["apply_during"] == "playbook"
        return Decision(
            workflow=workflow,
            name=name,
            waits_for_clarification=workflow == "hitl",
            creates_tracker_packet=creates_packet,
            principles_active=active,
            judge_changed_outcome=False,
        )


def _require_agreement(policy: RouterPolicy, invocation: Invocation) -> None:
    if (
        policy["canonical_token"] != "mstack"
        or invocation["canonical_token"] != "mstack"
    ):
        raise RuntimeError("canonical router token must be mstack")
    if policy["aliases"] != ["poteto-mode"] or invocation["aliases"] != ["poteto-mode"]:
        raise RuntimeError("poteto-mode is the only router alias")
    if (
        policy["directory"] != invocation["core_skill"]
        or invocation["core_skill"] != "poteto-mode"
    ):
        raise RuntimeError("router tokens must open the poteto-mode skill")
    if invocation["plugin_id"] != "mainart-stack":
        raise RuntimeError("plugin identity must stay mainart-stack")
    if invocation["implicit_invocation"] is not False:
        raise RuntimeError("the router is explicit-only")
    principles = policy["principles"]
    judge = policy["judge"]
    if principles["can_suppress_hitl"] is not False:
        raise RuntimeError("principles must not suppress HITL")
    if principles["apply_during"] != "playbook":
        raise RuntimeError("principles apply during the playbook phase")
    if judge["required"] is not False or judge["overrides_explicit"] is not False:
        raise RuntimeError("validation.judge cannot gate or override routing")
    if judge["overrides_unscoped_gate"] is not False:
        raise RuntimeError("validation.judge cannot replace the settled-what gate")
    if invocation["runner"]["placement"] != "in-session":
        raise RuntimeError("Grok adopts playbook-runner in the coordinator session")
    if invocation["nested_spawn_worker"] is not False:
        raise RuntimeError("Grok rejects nested spawn-worker")
