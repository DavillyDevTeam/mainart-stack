"""Policy checks for the first router-to-bug-fix core slice.

Run from the repo root: python scripts/check_core_slice.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.slice_agreement import agreement_problems

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

FENCE_FILES = (
    "skills/poteto-mode/SKILL.md",
    "skills/figure-it-out/SKILL.md",
    "skills/poteto-help/SKILL.md",
    "skills/correct/SKILL.md",
    "skills/no-comments/SKILL.md",
    "agents/playbook-runner.md",
    "skills/principle-never-block-on-the-human/SKILL.md",
)

SIGNAL_PROSE = {
    "data_shape": "data shape",
    "repro": "repro",
    "metric": "metric",
    "acceptance": "acceptance",
}


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

    problems.extend(slice_copy_problems(core, vendor))
    problems.extend(procedure_alignment_problems(core))
    problems.extend(_agreement_problems(root, core))
    problems.extend(_license_problems(core))
    return problems


def _skill_name(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    for line in text[4:end].splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


def slice_copy_problems(core: Path, vendor: Path) -> list[str]:
    """A slice skill keeps every vendor sibling, rewritten rather than copied raw."""

    problems: list[str] = []
    for skill in SLICE_SKILLS:
        vendor_root = vendor / "skills" / skill
        if not vendor_root.is_dir():
            continue
        for path in sorted(vendor_root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(vendor).as_posix()
            if (
                relative.startswith(VENDOR_ONLY_PREFIXES)
                or relative in VENDOR_ONLY_FILES
            ):
                continue
            core_file = core / relative
            if not core_file.is_file():
                problems.append(f"missing same-relative-path core copy: {relative}")
                continue
            if core_file.read_bytes() == path.read_bytes():
                problems.append(f"core copy is not rewritten: {relative}")
            vendor_name = _skill_name(path.read_text())
            core_name = _skill_name(core_file.read_text())
            if vendor_name is not None and vendor_name != core_name:
                problems.append(f"core copy renamed the skill: {relative}")
    return problems


def procedure_alignment_problems(core: Path) -> list[str]:
    """Prose that restates the policy must keep the policy's words."""

    problems: list[str] = []
    router_path = core / "skills" / "poteto-mode" / "SKILL.md"
    if router_path.is_file():
        router = router_path.read_text().lower()
        for phrase in SIGNAL_PROSE.values():
            if phrase not in router:
                problems.append(f"router prose dropped the settled signal {phrase}")
    for relative in (
        "skills/poteto-mode/playbooks/bug-fix.md",
        "agents/playbook-runner.md",
    ):
        path = core / relative
        if not path.is_file():
            continue
        text = path.read_text().lower()
        if (
            "cheap failing-test-first" not in text
            or "impractical or expensive" not in text
        ):
            problems.append(f"{relative} drifted from the bug-fix testing contract")
    for relative in FENCE_FILES:
        path = core / relative
        if not path.is_file() or "must not suppress" not in path.read_text():
            problems.append(f"{relative} dropped the HITL fence")
    return problems


def _agreement_problems(root: Path, core: Path) -> list[str]:
    invocation_path = root / "hosts" / "grok" / "invocation.json"
    policy_path = core / "skills" / "poteto-mode" / "router-policy.json"
    bug_path = core / "skills" / "poteto-mode" / "playbooks" / "bug-fix.policy.json"
    if not invocation_path.is_file() or not policy_path.is_file():
        return ["missing Grok invocation map"]
    if not bug_path.is_file():
        return ["missing bug-fix policy"]
    loaded = [
        json.loads(path.read_text())
        for path in (policy_path, invocation_path, bug_path)
    ]
    if not all(isinstance(item, dict) for item in loaded):
        return ["router agreement inputs must be JSON objects"]
    policy, invocation, bugfix = loaded
    return agreement_problems(policy, invocation, bugfix)


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
