"""Grok coordinator session, the observable router and playbook boundary.

The session reads the host-agnostic router policy and adopts playbook-runner
in-process. It does not spawn that role, and a worker cannot call spawn-worker.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict, cast

from scripts.slice_agreement import (
    CHEAP_FAILING_TEST_FIRST,
    GOAL_CONTINUATION_CAP,
    IMPRACTICAL_OR_EXPENSIVE,
    SETTLED_SIGNALS,
    agreement_problems,
)

ROOT = Path(__file__).resolve().parents[2]
INVOCATION_PATH = Path(__file__).with_name("invocation.json")
POLICY_PATH = ROOT / "core/skills/poteto-mode/router-policy.json"
BUGFIX_POLICY_PATH = ROOT / "core/skills/poteto-mode/playbooks/bug-fix.policy.json"
SKILL_PATH = ROOT / "core/skills/poteto-mode/SKILL.md"
AGENTS = ROOT / "core/agents"

ModelRole = Literal["xhigh", "max", "fast"]
Isolation = Literal["isolated", "same-tree"]
TestingCadence = Literal["cheap-failing-test-first"]
TestingException = Literal["impractical-or-expensive"]
HostPlacement = Literal["worktree", "same-tree"]
NativeIsolation = Literal["worktree", "none"]
Workflow = Literal["hitl", "playbook"]
OvernightDriver = Literal["/goal", "/loop"]

MODEL_ROLES = frozenset({"xhigh", "max", "fast"})
ISOLATIONS = frozenset({"isolated", "same-tree"})


@dataclass(frozen=True)
class OvernightRequest:
    mode: Literal["until", "every"]
    driver: OvernightDriver
    continuation_cap: int | None
    done: str | None = None
    interval: str | None = None
    prompt: str | None = None
    resumes_after_process_death: bool = False


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
            isinstance(getattr(self, name), str) and getattr(self, name).strip()
            for name in SETTLED_SIGNALS
        )


@dataclass(frozen=True)
class JudgeAdvice:
    """Optional validation.judge prior. Unbound advice is not a gate."""

    status: Literal["unbound", "answered"] = "unbound"
    workflow: Workflow | None = None
    playbook: str | None = None


@dataclass(frozen=True)
class Decision:
    workflow: Workflow
    name: str
    waits_for_clarification: bool
    creates_tracker_packet: bool
    principles_active: bool
    judge_changed_outcome: bool
    judge_disagreed: bool


@dataclass(frozen=True)
class PlaybookRun:
    playbook: str
    runner: str
    adopted_in_session: bool
    creates_tracker_packet: bool
    testing_cadence: TestingCadence
    testing_exception: TestingException
    invoked_skills: tuple[str, ...]
    principles_active: bool


@dataclass(frozen=True)
class SpawnHandle:
    kind: Literal["worker", "adopted"]
    role: str
    native_type: str
    isolation: Isolation
    model_role: ModelRole | None
    depth: int
    placement: HostPlacement
    native_isolation: NativeIsolation
    model_config_key: str | None

    def spawn_worker(
        self,
        role: str,
        prompt: str,
        isolation: Isolation | None = None,
        model_role: ModelRole | None = None,
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


class SettledWhatPolicy(TypedDict):
    signals: list[str]


class RouterPolicy(TypedDict):
    directory: str
    canonical_token: str
    aliases: list[str]
    hitl_entry: str
    explicit_hitl: list[str]
    settled_what: SettledWhatPolicy
    principles: PrinciplesPolicy
    judge: JudgePolicy
    playbooks: list[PlaybookEntry]


class RunnerPlacement(TypedDict):
    role: str
    placement: str


class Invocation(TypedDict):
    plugin_id: str
    canonical_token: str
    aliases: list[str]
    core_skill: str
    implicit_invocation: bool
    runner: RunnerPlacement
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
        self,
        token: str,
        policy: RouterPolicy,
        invocation: Invocation,
        bugfix: BugfixPolicy,
    ) -> None:
        self.token = token
        self._policy = policy
        self._invocation = invocation
        self._bugfix_policy = bugfix
        self.runner: str | None = None
        self.adopted_in_session = False
        self._outcome: Decision | None = None
        self._spawns: list[SpawnHandle] = []
        self._overnights: list[OvernightRequest] = []

    @classmethod
    def open(cls, token: str) -> GrokCoordinator:
        policy = cast(RouterPolicy, _load_json(POLICY_PATH))
        invocation = cast(Invocation, _load_json(INVOCATION_PATH))
        bugfix = cast(BugfixPolicy, _load_json(BUGFIX_POLICY_PATH))
        problems = agreement_problems(
            cast(Mapping[str, object], policy),
            cast(Mapping[str, object], invocation),
            cast(Mapping[str, object], bugfix),
        )
        if problems:
            raise RuntimeError("; ".join(problems))
        allowed = {invocation["canonical_token"], *invocation["aliases"]}
        if token not in allowed:
            raise UnknownInvocation(token)
        return cls(token, policy, invocation, bugfix)

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
        if advice.workflow not in {None, "hitl", "playbook"}:
            raise ValueError(advice.workflow)
        if advice.playbook is not None and not advice.playbook.strip():
            raise ValueError("empty playbook advice")
        if explicit is not None:
            if explicit in self._policy["explicit_hitl"]:
                return self._remember(self._decision("hitl", explicit, advice))
            included = self._included(explicit)
            if included is not None:
                return self._remember(
                    self._decision(
                        "playbook",
                        explicit,
                        advice,
                        creates_packet=bool(self._bugfix()["requires_packet"]),
                    )
                )
            raise UnknownInvocation(explicit)
        if prompt.settled and prompt.reported_defect and self._matches_bug_fix():
            return self._remember(
                self._decision(
                    "playbook",
                    "bug-fix",
                    advice,
                    creates_packet=bool(self._bugfix()["requires_packet"]),
                )
            )
        return self._remember(
            self._decision("hitl", str(self._policy["hitl_entry"]), advice)
        )

    def begin(self, decision: Decision) -> PlaybookRun:
        self._hold_for_clarification()
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
            testing_cadence=CHEAP_FAILING_TEST_FIRST,
            testing_exception=IMPRACTICAL_OR_EXPENSIVE,
            invoked_skills=invoked,
            principles_active=decision.principles_active,
        )

    def spawn_worker(
        self,
        role: str,
        prompt: str,
        isolation: Isolation | None = None,
        model_role: ModelRole | None = None,
    ) -> SpawnHandle:
        self._hold_for_clarification()
        if not prompt.strip():
            raise ValueError("prompt is required")
        chosen = _isolation(isolation)
        role_token = _model_role(model_role)
        runner = self._invocation["runner"]["role"]
        if role == runner:
            self.runner = role
            self.adopted_in_session = True
            return self._handle("adopted", role, chosen, role_token, 0)
        if role not in _agent_roles():
            raise UnknownRole(role)
        handle = self._handle("worker", role, chosen, role_token, 1)
        self._spawns.append(handle)
        return handle

    def overnight(
        self,
        *,
        mode: Literal["until", "every"],
        done: str | None = None,
        interval: str | None = None,
        prompt: str | None = None,
    ) -> OvernightRequest:
        """Record an overnight request. until is /goal with a cap; every is /loop."""

        self._hold_for_clarification()
        if mode == "until":
            if (
                not isinstance(done, str)
                or not done.strip()
                or interval is not None
                or prompt is not None
            ):
                raise ValueError("until carries a done condition and nothing else")
            request = OvernightRequest(
                mode="until",
                driver="/goal",
                continuation_cap=GOAL_CONTINUATION_CAP,
                done=done,
            )
        elif mode == "every":
            if (
                done is not None
                or not isinstance(interval, str)
                or not interval.strip()
                or not isinstance(prompt, str)
                or not prompt.strip()
            ):
                raise ValueError("every carries an interval and a prompt")
            request = OvernightRequest(
                mode="every",
                driver="/loop",
                continuation_cap=None,
                interval=interval,
                prompt=prompt,
            )
        else:
            raise ValueError(mode)
        self._overnights.append(request)
        return request

    def _included(self, name: str) -> PlaybookEntry | None:
        for item in self._policy["playbooks"]:
            if item["name"] == name:
                return item
        return None

    def _matches_bug_fix(self) -> bool:
        included = self._included("bug-fix")
        return included is not None and included["match"] == "reported-defect"

    def _bugfix(self) -> BugfixPolicy:
        return self._bugfix_policy

    def _decision(
        self,
        workflow: Workflow,
        name: str,
        advice: JudgeAdvice,
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
            judge_disagreed=_judge_disagreed(advice, workflow, name),
        )

    def _handle(
        self,
        kind: Literal["worker", "adopted"],
        role: str,
        isolation: Isolation,
        model_role: ModelRole | None,
        depth: int,
    ) -> SpawnHandle:
        return SpawnHandle(
            kind=kind,
            role=role,
            native_type=f"{self.plugin_id}:{role}",
            isolation=isolation,
            model_role=model_role,
            depth=depth,
            placement=_placement(isolation),
            native_isolation=_native_isolation(isolation),
            model_config_key=_model_config_key(model_role),
        )

    def _remember(self, decision: Decision) -> Decision:
        self._outcome = decision
        return decision

    def _hold_for_clarification(self) -> None:
        if self._outcome is not None and self._outcome.waits_for_clarification:
            raise ClarificationRequired(self._outcome.name)


def _isolation(value: str | None) -> Isolation:
    if value is None:
        return "same-tree"
    if value not in ISOLATIONS:
        raise ValueError(value)
    return cast(Isolation, value)


def _model_role(value: str | None) -> ModelRole | None:
    if value is None:
        return None
    if value not in MODEL_ROLES:
        raise ValueError(value)
    return cast(ModelRole, value)


def _placement(isolation: Isolation) -> HostPlacement:
    if isolation == "isolated":
        return "worktree"
    return "same-tree"


def _native_isolation(isolation: Isolation) -> NativeIsolation:
    if isolation == "isolated":
        return "worktree"
    return "none"


def _model_config_key(model_role: ModelRole | None) -> str | None:
    if model_role is None:
        return None
    return f"[subagents.roles.{model_role}].model"


def _judge_disagreed(advice: JudgeAdvice, workflow: Workflow, name: str) -> bool:
    if advice.status != "answered":
        return False
    workflow_differs = advice.workflow is not None and advice.workflow != workflow
    playbook_differs = advice.playbook is not None and advice.playbook != name
    return workflow_differs or playbook_differs
