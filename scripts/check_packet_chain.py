"""Static checks for the vendored Matt packet chain and Grok exposure."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __package__ in {None, ""}:
    sys.path.insert(0, str(ROOT))

from scripts.check_vendor import object_id


def tree_id_from_blobs(blobs: dict[str, bytes]) -> bytes:
    files: dict[str, bytes] = {}
    directories: dict[str, dict[str, bytes]] = {}
    for path, digest in blobs.items():
        if "/" not in path:
            files[path] = digest
        else:
            head, tail = path.split("/", 1)
            directories.setdefault(head, {})[tail] = digest
    entries: list[tuple[bytes, bytes]] = []
    for name, digest in files.items():
        encoded = os.fsencode(name)
        entries.append((encoded, b"100644 " + encoded + b"\0" + digest))
    for name, nested in directories.items():
        encoded = os.fsencode(name)
        digest = tree_id_from_blobs(nested)
        entries.append((encoded + b"/", b"40000 " + encoded + b"\0" + digest))
    return object_id("tree", b"".join(entry for _, entry in sorted(entries)))

PINNED_REVISION = "d1478fcb140db0b93c0c8df17bcfd311844749d0"

SKILL_FOLDER_HASHES = {
    "grill-with-docs": "eedaf2562c83155115e9c649fa3ecaac2e10e81d",
    "grill-me": "3df14e2d3a89459bf300614be9247e3ce74798f8",
    "to-spec": "136b9651747cfccbfbb7c50a6b0dfb757e7547d2",
    "to-tickets": "2dee20ad722a31c04ededf9f2d83842473573045",
    "wayfinder": "25da74eadc3e388b2f2a2cc716f3d44b2fb9dfe0",
    "triage": "4cb951d62ecccaed601cdc5f9a1b7b3d8a799635",
    "implement": "4804b466ab26c9b9d8d42917547db133d1f20a9f",
    "implement-spec": "200830c5d204c1fd29129af9d392c8a4c258b1b5",
    "setup-matt-pocock-skills": "b644b684781fd5baae57f6be000a180a4d4448d7",
    "grilling": "f551b6e0d219fdda0b6abf277f8f915b3127d1e9",
    "domain-modeling": "ea30ee454ba264543dbe40737973b1a5afb9f0e6",
    "prototype": "e41d92e171f074a2b6887d8f6faca4a15c83d1ca",
    "tdd": "667dbdd00c09d0e2189e082986e6a4d61a67c2a6",
    "code-review": "a8ef561571acbb611de8ff19ba6da75b197c63a8",
    "research": "2f8f36af48796faed5c687c75bb650071631a984",
}

COMPANIONS = (
    "domain-modeling/GLOSSARY-FORMAT.md",
    "domain-modeling/ADR-FORMAT.md",
    "prototype/LOGIC.md",
    "prototype/UI.md",
    "triage/AGENT-BRIEF.md",
    "triage/OUT-OF-SCOPE.md",
    "tdd/tests.md",
    "tdd/mocking.md",
    "setup-matt-pocock-skills/issue-tracker-github.md",
    "setup-matt-pocock-skills/issue-tracker-gitlab.md",
    "setup-matt-pocock-skills/issue-tracker-local.md",
    "setup-matt-pocock-skills/triage-labels.md",
    "setup-matt-pocock-skills/domain.md",
)

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

    for name, expected in SKILL_FOLDER_HASHES.items():
        skill = recorded.get(name)
        if not isinstance(skill, dict):
            found.append(f"missing provenance for {name}")
            continue
        if skill.get("tree") != expected:
            found.append(f"skillFolderHash mismatch for {name}")
        skill_root = root / "core/skills" / name
        skill_file = skill_root / "SKILL.md"
        if not skill_file.is_file():
            found.append(f"missing skill: core/skills/{name}/SKILL.md")
            continue
        files = skill.get("files")
        if not isinstance(files, dict):
            found.append(f"missing file inventory for {name}")
            continue
        omitted = skill.get("omitted", {})
        if not isinstance(omitted, dict):
            found.append(f"missing omitted inventory for {name}")
            omitted = {}
        blobs: dict[str, bytes] = {}
        complete = True
        for relative, digest in files.items():
            path = skill_root / relative
            if not path.is_file():
                found.append(f"missing copied file: core/skills/{name}/{relative}")
                complete = False
                continue
            actual = object_id("blob", path.read_bytes())
            if actual.hex() != digest:
                found.append(
                    f"blob mismatch: core/skills/{name}/{relative}"
                )
                complete = False
            blobs[relative] = actual
        for relative, digest in omitted.items():
            if not isinstance(digest, str):
                found.append(f"omitted blob missing for {name}/{relative}")
                complete = False
                continue
            if (skill_root / relative).exists():
                found.append(
                    "adapter metadata in core: "
                    f"core/skills/{name}/{relative}"
                )
                complete = False
            blobs[relative] = bytes.fromhex(digest)
        if complete:
            reconstructed = tree_id_from_blobs(blobs).hex()
            if reconstructed != expected:
                found.append(f"skillFolderHash mismatch for {name}")
        for path in skill_root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(skill_root).as_posix()
            if relative in files or relative in omitted:
                continue
            found.append(
                f"unexpected file in core: core/skills/{name}/{relative}"
            )

    for relative in COMPANIONS:
        path = root / "core/skills" / relative
        if not path.is_file():
            found.append(f"missing companion: core/skills/{relative}")

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
        f"{len(SKILL_FOLDER_HASHES)} skills, Grok HITL explicit"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
