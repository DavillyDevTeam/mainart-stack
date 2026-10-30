"""Policy checks for the first router-to-bug-fix core slice.

Run from the repo root: python scripts/check_core_slice.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FORBIDDEN: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"spawn_subagent"), "spawn_subagent"),
    (re.compile(r"AskQuestion"), "AskQuestion"),
    (re.compile(r"AskUserQuestion"), "AskUserQuestion"),
    (re.compile(r"subagent_type"), "subagent_type"),
    (re.compile(r"~/\.cursor"), "~/.cursor"),
    (re.compile(r"~/\.grok"), "~/.grok"),
    (re.compile(r"~/\.claude"), "~/.claude"),
    (re.compile(r"disable-model-invocation"), "disable-model-invocation"),
    (re.compile(r"allow_implicit_invocation"), "allow_implicit_invocation"),
    (re.compile(r"user-invocable"), "user-invocable"),
    (re.compile(r"\bgrok-\d"), "grok-<version>"),
    (re.compile(r"claude-(opus|sonnet|haiku)"), "claude model id"),
    (re.compile(r"\bgpt-\d"), "gpt model id"),
    (re.compile(r"cursor-team-kit"), "cursor-team-kit"),
    (re.compile(r"control-ui"), "control-ui"),
    (re.compile(r"control-cli"), "control-cli"),
    (re.compile(r"(?<![\w/])/loop\b"), "/loop"),
    (re.compile(r"setup-pstack"), "setup-pstack"),
    (re.compile(r"TYPESAFE_API_KEY"), "TYPESAFE_API_KEY"),
    (re.compile(r"\bjev\b", re.IGNORECASE), "jev"),
    (re.compile(r"is_background\s*:"), "is_background"),
    (re.compile(r"(?m)^mode:\s*true\s*$"), "mode: true"),
    (re.compile(r"\bOrigin\b"), "Origin"),
)

NEW_CORE_FILES = frozenset(
    {
        "LICENSES/MIT-lauren-tan.txt",
        "LICENSES/MIT-matt-pocock.txt",
        "agents/playbook-runner.md",
        "skills/poteto-mode/router-policy.json",
        "skills/poteto-mode/playbooks/bug-fix.policy.json",
    }
)

REQUIRED = (
    "skills/poteto-mode/SKILL.md",
    "skills/poteto-mode/router-policy.json",
    "skills/poteto-mode/playbooks/bug-fix.md",
    "skills/poteto-mode/playbooks/bug-fix.policy.json",
    "skills/no-comments/SKILL.md",
    "skills/figure-it-out/SKILL.md",
    "skills/poteto-help/SKILL.md",
    "skills/correct/SKILL.md",
    "agents/playbook-runner.md",
    "agents/poteto-agent.md",
    "agents/comment-sicko.md",
    "LICENSES/MIT-lauren-tan.txt",
    "LICENSES/MIT-matt-pocock.txt",
)

VENDOR_ONLY_PREFIXES = (
    "skills/setup-pstack/",
    "skills/recall/",
    "skills/reflect/",
    "skills/automate-me/",
    "skills/show-me-your-work/",
    "skills/create-verification-skill/",
    "skills/maintain-verification-skill/",
    "skills/make-bot-ui/",
    "skills/poteto-mode/scripts/",
    "skills/poteto-mode/references/",
    "automations/",
    "docs/",
    ".cursor-plugin/",
    "assets/",
)

VENDOR_ONLY_FILES = frozenset(
    {
        "plugin.json",
        "README.md",
        "LICENSE",
        "skills/poteto-mode/playbooks/orchestrate.md",
        "skills/poteto-mode/playbooks/session-pickup.md",
        "skills/poteto-mode/playbooks/eval.md",
        "skills/poteto-mode/playbooks/authoring-a-skill.md",
    }
)

SLICE_SKILLS = (
    "no-comments",
    "figure-it-out",
    "poteto-help",
    "correct",
)


def forbidden_hits(text: str) -> list[str]:
    return [label for pattern, label in FORBIDDEN if pattern.search(text)]


def _notice_problems(text: str, holder: str) -> list[str]:
    problems: list[str] = []
    if f"Copyright (c) 2026 {holder}" not in text:
        problems.append(f"missing copyright for {holder}")
    if "Permission is hereby granted" not in text:
        problems.append(f"missing MIT permission grant for {holder}")
    if (
        "The above copyright notice and this permission notice shall be included"
        not in text
    ):
        problems.append(f"missing MIT notice condition for {holder}")
    return problems


def tdd_collision_problems(core: Path, vendor: Path) -> list[str]:
    """Packet-chain occupancy: Matt's tdd may live in core. pstack's copy may not."""

    vendor_tdd = vendor / "skills" / "tdd"
    core_tdd = core / "skills" / "tdd"
    if not vendor_tdd.is_dir():
        return [
            "vendor skills/tdd is missing, so collision exclusion cannot be checked"
        ]
    if not core_tdd.exists():
        return []
    problems: list[str] = []
    for path in sorted(core_tdd.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(core)
        vendor_file = vendor / relative
        if vendor_file.is_file() and path.read_bytes() == vendor_file.read_bytes():
            problems.append(
                f"pstack copy occupies packet-chain path: {relative.as_posix()}"
            )
    return problems


def violations(root: Path) -> list[str]:
    core = root / "core"
    vendor = root / "vendor" / "pstack"
    problems: list[str] = []
    problems.extend(tdd_collision_problems(core, vendor))

    for relative in REQUIRED:
        if not (core / relative).is_file():
            problems.append(f"missing slice file: core/{relative}")

    for path in sorted(core.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(core).as_posix()
        if relative.startswith(VENDOR_ONLY_PREFIXES) or relative in VENDOR_ONLY_FILES:
            problems.append(f"vendor-only path shipped in core: {relative}")
            continue
        vendor_file = vendor / relative
        if relative in NEW_CORE_FILES:
            if vendor_file.exists():
                problems.append(
                    f"new core file collides with a vendor path: {relative}"
                )
            continue
        if not vendor_file.is_file():
            problems.append(f"not a same-relative-path core copy: {relative}")

    vendor_principles = {
        path.name
        for path in (vendor / "skills").iterdir()
        if path.name.startswith("principle-")
    }
    core_principles = {
        path.name
        for path in (core / "skills").iterdir()
        if path.is_dir() and path.name.startswith("principle-")
    }
    if core_principles != vendor_principles or len(core_principles) != 24:
        problems.append(
            f"principle set drifted: core={len(core_principles)} vendor={len(vendor_principles)}"
        )

    for skill in SLICE_SKILLS:
        if not (vendor / "skills" / skill / "SKILL.md").is_file():
            problems.append(f"vendor skill missing: {skill}")

    procedure_roots = (core / "skills", core / "agents")
    for procedure_root in procedure_roots:
        for path in sorted(procedure_root.rglob("*")):
            if path.suffix not in {".md", ".json"}:
                continue
            for label in forbidden_hits(path.read_text()):
                problems.append(f"{path.relative_to(root).as_posix()}: {label}")

    never_block = core / "skills" / "principle-never-block-on-the-human" / "SKILL.md"
    if never_block.is_file():
        text = never_block.read_text()
        if "playbook" not in text or "must not suppress" not in text:
            problems.append(
                "principle-never-block-on-the-human can suppress HITL clarification"
            )

    bug_fix = core / "skills" / "poteto-mode" / "playbooks" / "bug-fix.md"
    if bug_fix.is_file():
        lowered = bug_fix.read_text().lower()
        if "skills/tdd" in lowered or 'skill tool with "tdd"' in lowered:
            problems.append("bug-fix invokes Matt tdd")

    problems.extend(_policy_problems(core))
    problems.extend(_license_problems(core))
    problems.extend(_invocation_problems(root, core))
    return problems


def _policy_problems(core: Path) -> list[str]:
    problems: list[str] = []
    policy_path = core / "skills" / "poteto-mode" / "router-policy.json"
    bug_path = core / "skills" / "poteto-mode" / "playbooks" / "bug-fix.policy.json"
    if not policy_path.is_file() or not bug_path.is_file():
        return problems
    policy = json.loads(policy_path.read_text())
    bug = json.loads(bug_path.read_text())
    if policy.get("canonical_token") != "mstack" or policy.get("aliases") != [
        "poteto-mode"
    ]:
        problems.append(
            "router policy tokens are not mstack plus the poteto-mode alias"
        )
    if policy.get("directory") != "poteto-mode":
        problems.append("router directory must stay poteto-mode")
    principles = policy.get("principles") or {}
    if (
        principles.get("apply_during") != "playbook"
        or principles.get("can_suppress_hitl") is not False
    ):
        problems.append("principles are not scoped to the playbook phase")
    judge = policy.get("judge") or {}
    if (
        judge.get("required") is not False
        or judge.get("overrides_explicit") is not False
        or judge.get("overrides_unscoped_gate") is not False
    ):
        problems.append("validation.judge is a gate in the router policy")
    testing = bug.get("testing") or {}
    if testing.get("cadence") != "cheap-failing-test-first":
        problems.append("bug-fix lost cheap failing-test-first")
    if testing.get("exception") != "impractical-or-expensive":
        problems.append("bug-fix lost the impractical or expensive test exception")
    if (
        testing.get("invokes_skill") is not None
        or bug.get("requires_packet") is not False
    ):
        problems.append("bug-fix calls Matt tdd or requires a tracker packet")
    return problems


def _license_problems(core: Path) -> list[str]:
    problems: list[str] = []
    lauren = core / "LICENSES" / "MIT-lauren-tan.txt"
    matt = core / "LICENSES" / "MIT-matt-pocock.txt"
    if lauren.is_file():
        problems.extend(_notice_problems(lauren.read_text(), "Lauren Tan"))
    else:
        problems.append("missing Lauren Tan MIT notice")
    if matt.is_file():
        problems.extend(_notice_problems(matt.read_text(), "Matt Pocock"))
    else:
        problems.append("missing Matt Pocock MIT notice")
    return problems


def _invocation_problems(root: Path, core: Path) -> list[str]:
    invocation_path = root / "hosts" / "grok" / "invocation.json"
    policy_path = core / "skills" / "poteto-mode" / "router-policy.json"
    if not invocation_path.is_file() or not policy_path.is_file():
        return ["missing Grok invocation map"]
    invocation = json.loads(invocation_path.read_text())
    policy = json.loads(policy_path.read_text())
    problems: list[str] = []
    if invocation.get("plugin_id") != "mainart-stack":
        problems.append("Grok plugin identity is not mainart-stack")
    if invocation.get("canonical_token") != policy.get("canonical_token"):
        problems.append("Grok canonical token drifted from the core router")
    if invocation.get("aliases") != policy.get("aliases"):
        problems.append("Grok aliases drifted from the core router")
    if invocation.get("core_skill") != "poteto-mode":
        problems.append("Grok tokens do not open poteto-mode")
    if invocation.get("implicit_invocation") is not False:
        problems.append("Grok router allows implicit invocation")
    runner = invocation.get("runner") or {}
    if (
        runner.get("role") != "playbook-runner"
        or runner.get("placement") != "in-session"
    ):
        problems.append("Grok does not adopt playbook-runner in-session")
    if invocation.get("nested_spawn_worker") is not False:
        problems.append("Grok permits nested spawn-worker")
    return problems


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    found = violations(root)
    if found:
        for problem in found:
            print(problem, file=sys.stderr)
        return 1
    print("core slice policy: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
