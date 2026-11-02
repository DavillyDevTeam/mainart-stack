"""Persist opaque model roles into Grok [subagents.roles.*] configuration."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from core.host_setup import MODEL_ROLES

DEFAULT_MODEL_ROLES = {
    "xhigh": "grok-4.7",
    "max": "grok-4.7",
    "fast": "grok-4.7",
}


class GrokModelRoles:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def defaults(self) -> dict[str, str]:
        return dict(DEFAULT_MODEL_ROLES)

    def persist(self, mapping: Mapping[str, str]) -> dict[str, str]:
        if set(mapping) != set(MODEL_ROLES):
            raise ValueError("model roles must be exactly xhigh, max, and fast")
        written = {role: mapping[role] for role in MODEL_ROLES}
        text = self.config_path.read_text() if self.config_path.exists() else ""
        for role, model in written.items():
            text = _upsert_role_model(text, role, model)
        if text and not text.endswith("\n"):
            text += "\n"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(text)
        return written


def _upsert_role_model(text: str, role: str, model: str) -> str:
    header = f"[subagents.roles.{role}]"
    model_line = f'model = "{model}"'
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.strip() == header), None)
    if start is None:
        prefix = "" if text == "" or text.endswith("\n") else "\n"
        blank = "\n" if text and not text.endswith("\n\n") else ""
        if text == "":
            return f"{header}\n{model_line}\n"
        return f"{text}{prefix}{blank}{header}\n{model_line}\n"
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("["):
            end = index
            break
    for index in range(start + 1, end):
        if lines[index].lstrip().startswith("model"):
            newline = "\n" if lines[index].endswith("\n") else ""
            lines[index] = model_line + newline
            return "".join(lines)
    lines.insert(start + 1, model_line + "\n")
    return "".join(lines)
