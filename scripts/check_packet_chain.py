"""Static checks for the vendored Matt packet chain."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __package__ in {None, ""}:
    sys.path.insert(0, str(ROOT))

from scripts.check_vendor import git_files, git_tree

PINNED_REVISION = "d1478fcb140db0b93c0c8df17bcfd311844749d0"

UNSELECTED = (
    "ask-matt",
    "codebase-design",
    "handoff",
    "pr",
    "retro",
    "diagnosing-bugs",
    "improve-codebase-architecture",
    "wizard",
    "wait-what",
    "to-questionnaire",
    "writing-for-agents",
)

HITL = (
    "grill-with-docs",
    "grill-me",
    "to-spec",
    "to-tickets",
    "wayfinder",
    "triage",
    "implement",
    "implement-spec",
    "setup-matt-pocock-skills",
)
PRIMITIVES = (
    "grilling",
    "domain-modeling",
    "prototype",
    "tdd",
    "code-review",
    "research",
)
PACKET_CHAIN = HITL + PRIMITIVES


def problems(root: Path = ROOT) -> list[str]:
    found: list[str] = []
    provenance_path = root / "vendor/matt-packet-chain-provenance.json"
    try:
        provenance = json.loads(provenance_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        return [f"packet-chain provenance unreadable: {error}"]

    if provenance.get("revision") != PINNED_REVISION:
        found.append(
            "import revision is not "
            f"{PINNED_REVISION}: {provenance.get("revision")}"
        )

    recorded = provenance.get("skills")
    if not isinstance(recorded, dict):
        found.append("provenance skills map is missing")
        return found
    if set(recorded) != set(PACKET_CHAIN):
        found.append("provenance skill list does not match the packet chain")

    for name in PACKET_CHAIN:
        skill = recorded.get(name)
        if not isinstance(skill, dict):
            found.append(f"missing provenance for {name}")
            continue
        expected = skill.get("tree")
        try:
            actual = git_tree(f"core/skills/{name}")
        except subprocess.CalledProcessError:
            found.append(f"missing skill: core/skills/{name}")
            continue
        if actual != expected:
            found.append(f"tree mismatch for {name}")
        skill_root = root / "core/skills" / name
        expected_files = git_files(f"core/skills/{name}")
        actual_files = {
            path.relative_to(skill_root).as_posix()
            for path in skill_root.rglob("*")
            if path.is_file()
        } if skill_root.is_dir() else set()
        for relative in sorted(expected_files - actual_files):
            found.append(f"missing file: core/skills/{name}/{relative}")
        for relative in sorted(actual_files - expected_files):
            path = f"core/skills/{name}/{relative}"
            if Path(relative).name == "openai.yaml":
                found.append(f"adapter metadata in core: {path}")
            else:
                found.append(f"unexpected file in core: {path}")

    for yaml in (root / "core").rglob("openai.yaml"):
        found.append(
            "adapter metadata in core: " + yaml.relative_to(root).as_posix()
        )

    for name in UNSELECTED:
        if (root / "core/skills" / name).exists():
            found.append(f"unselected skill in core: skills/{name}")

    mit = root / "core/LICENSES/MIT-matt-pocock.txt"
    try:
        notice = mit.read_text()
    except OSError:
        found.append("missing Matt Pocock MIT notice")
    else:
        if "Copyright (c) 2026 Matt Pocock" not in notice:
            found.append("Matt Pocock copyright line missing")
        if "Permission is hereby granted" not in notice:
            found.append("Matt Pocock MIT permission notice missing")

    core_tdd = root / "core/skills/tdd/SKILL.md"
    vendor_tdd = root / "vendor/pstack/skills/tdd/SKILL.md"
    if core_tdd.is_file() and vendor_tdd.is_file():
        if core_tdd.read_bytes() == vendor_tdd.read_bytes():
            found.append("pstack copy occupies packet-chain path: skills/tdd/SKILL.md")
    elif not vendor_tdd.is_file():
        found.append("vendor skills/tdd is missing, so collision exclusion cannot be checked")

    found.extend(_invocation_problems(root))
    return found


def _invocation_problems(root: Path) -> list[str]:
    path = root / "hosts/grok/invocation.json"
    try:
        invocation = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        return [f"Grok invocation metadata unreadable: {error}"]
    found: list[str] = []
    if invocation.get("plugin_id") != "mainart-stack":
        found.append("Grok plugin_id is not mainart-stack")
    if invocation.get("qualification") != "/mainart-stack:{name}":
        found.append("Grok qualification is not /mainart-stack:{name}")
    hitl = invocation.get("hitl")
    primitives = invocation.get("primitives")
    grilling = invocation.get("grilling")
    if not isinstance(hitl, dict) or hitl.get("implicit_invocation") is not False:
        found.append("HITL implicit invocation is not disabled")
    if isinstance(hitl, dict) and hitl.get("disable-model-invocation") is not True:
        found.append("HITL disable-model-invocation is not true")
    if isinstance(hitl, dict) and set(hitl.get("skills", [])) != set(HITL):
        found.append("Grok HITL skill list does not match the packet chain")
    if not isinstance(primitives, dict) or primitives.get("internally_available") is not True:
        found.append("packet-chain primitives are not internally available")
    if isinstance(primitives, dict) and primitives.get("disable-model-invocation") is not False:
        found.append("primitive disable-model-invocation is not false")
    if isinstance(primitives, dict) and set(primitives.get("skills", [])) != set(PRIMITIVES):
        found.append("Grok primitive skill list does not match the packet chain")
    if not isinstance(grilling, dict) or grilling.get("channel") != "plain-chat":
        found.append("grilling is not preserved as plain chat")
    if not isinstance(grilling, dict) or not grilling.get("numbered_questions"):
        found.append("grilling numbered questions are not preserved")
    if not isinstance(grilling, dict) or not grilling.get("recommendations"):
        found.append("grilling recommendations are not preserved")
    grilling_skill = root / "core/skills/grilling/SKILL.md"
    if grilling_skill.is_file():
        text = grilling_skill.read_text()
        if "AskUserQuestion" in text or "AskQuestion" in text:
            found.append("grilling uses a structured question tool")
    return found


def main() -> int:
    found = problems(ROOT)
    if found:
        print("Packet-chain check failed:", file=sys.stderr)
        for item in found:
            print(f"  {item}", file=sys.stderr)
        return 1
    print(
        f"Packet chain {PINNED_REVISION[:7]}: "
        f"{len(PACKET_CHAIN)} skills, Grok HITL explicit"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
