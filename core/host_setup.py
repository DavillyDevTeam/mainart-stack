"""Host-agnostic first-run setup: local host, model roles, and project pins."""

from __future__ import annotations

import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol, cast

HOST_IDS = ("grok", "claude", "codex")
HostId = Literal["grok", "claude", "codex"]
MODEL_ROLES = ("xhigh", "max", "fast")
HOST_GITIGNORE = ".mainart/host"
CHECKLIST = (
    "disable-or-uninstall-matt-plugin",
    "remove-duplicate-packet-chain-copies-for-bare-names",
    "dual-install-via-host-qualification",
)


class UnknownHost(ValueError):
    """The requested host id is outside grok, claude, and codex."""


class ModelRolePersistence(Protocol):
    def defaults(self) -> Mapping[str, str]:
        """Adapter-owned host model ids for xhigh, max, and fast."""

    def persist(self, mapping: Mapping[str, str]) -> Mapping[str, str]:
        """Write the three role mappings in the host's own configuration."""


@dataclass(frozen=True)
class SetupResult:
    host_id: HostId
    host_path: Path
    pins_path: Path
    pins_initialized: bool
    pins_preserved: bool
    model_roles: Mapping[str, str]
    checklist: tuple[str, ...]


def configure(
    project: Path,
    host_id: str,
    *,
    hosts_root: Path,
    persist: ModelRolePersistence,
    model_roles: Mapping[str, str] | None = None,
) -> SetupResult:
    if host_id not in HOST_IDS:
        raise UnknownHost(host_id)
    selected = cast(HostId, host_id)
    resolved = _resolve_model_roles(persist, model_roles)
    mainart = project / ".mainart"
    mainart.mkdir(parents=True, exist_ok=True)
    host_path = mainart / "host"
    host_path.write_text(f"{selected}\n")
    _ensure_host_gitignored(project)
    persisted = dict(persist.persist(resolved))
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
        model_roles=persisted,
        checklist=CHECKLIST,
    )


def _resolve_model_roles(
    persist: ModelRolePersistence,
    model_roles: Mapping[str, str] | None,
) -> dict[str, str]:
    resolved = dict(persist.defaults() if model_roles is None else model_roles)
    if set(resolved) != set(MODEL_ROLES):
        raise ValueError("model roles must be exactly xhigh, max, and fast")
    return {role: resolved[role] for role in MODEL_ROLES}


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
