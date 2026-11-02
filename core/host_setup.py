"""Host-agnostic first-run setup: local host and project pins."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

HOST_IDS = ("grok", "claude", "codex")
HostId = Literal["grok", "claude", "codex"]
HOST_GITIGNORE = ".mainart/host"
PERSIST_MODEL_ROLES = "persist-model-roles"
CHECKLIST = (
    "disable-or-uninstall-matt-plugin",
    "remove-duplicate-packet-chain-copies-for-bare-names",
    "dual-install-via-host-qualification",
)


class UnknownHost(ValueError):
    """The requested host id is outside grok, claude, and codex."""


class MissingPersistShim(FileNotFoundError):
    """The selected host has no persist-model-roles skill directory."""


@dataclass(frozen=True)
class SetupResult:
    host_id: HostId
    host_path: Path
    pins_path: Path
    pins_initialized: bool
    pins_preserved: bool
    persist_skill: Path
    checklist: tuple[str, ...]


def configure(
    project: Path,
    host_id: str,
    *,
    hosts_root: Path,
) -> SetupResult:
    if host_id not in HOST_IDS:
        raise UnknownHost(host_id)
    selected = cast(HostId, host_id)
    persist_skill = _require_persist_shim(hosts_root, selected)
    mainart = project / ".mainart"
    mainart.mkdir(parents=True, exist_ok=True)
    host_path = mainart / "host"
    host_path.write_text(f"{selected}\n")
    _ensure_host_gitignored(project)
    pins_path = mainart / "pins.yaml"
    pins_initialized, pins_preserved = _initialize_pins(
        pins_path, hosts_root / selected / "pins.yaml"
    )
    return SetupResult(
        host_id=selected,
        host_path=host_path,
        pins_path=pins_path,
        pins_initialized=pins_initialized,
        pins_preserved=pins_preserved,
        persist_skill=persist_skill,
        checklist=CHECKLIST,
    )


def _require_persist_shim(hosts_root: Path, host_id: HostId) -> Path:
    persist_skill = hosts_root / host_id / "skills" / PERSIST_MODEL_ROLES
    if not persist_skill.is_dir():
        raise MissingPersistShim(str(persist_skill))
    return persist_skill


def _initialize_pins(project_pins: Path, host_pins: Path) -> tuple[bool, bool]:
    if project_pins.exists():
        return False, True
    shutil.copyfile(host_pins, project_pins)
    return True, False


def _ensure_host_gitignored(project: Path) -> None:
    gitignore = project / ".gitignore"
    existing = gitignore.read_text() if gitignore.exists() else ""
    lines = existing.splitlines()
    if HOST_GITIGNORE not in lines:
        prefix = "" if existing == "" or existing.endswith("\n") else "\n"
        gitignore.write_text(f"{existing}{prefix}{HOST_GITIGNORE}\n")
