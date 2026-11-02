"""Persist opaque model roles into Grok [subagents.roles.*] configuration."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from pathlib import Path

ROLES = ("xhigh", "max", "fast")
DEFAULT_MODEL_ROLES = {
    "xhigh": "grok-4.7",
    "max": "grok-4.7",
    "fast": "grok-4.7",
}
DEFAULT_CONFIG_PATH = Path.home() / ".grok" / "config.toml"
_MODEL_KEY = re.compile(r"^[ \t]*model[ \t]*=")
_NEXT_TABLE = re.compile(r"^[ \t]*\[")
_TRIPLE_DOUBLE = '"' * 3
_TRIPLE_SINGLE = "'" * 3


class GrokModelRoles:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = DEFAULT_CONFIG_PATH if config_path is None else config_path

    def defaults(self) -> dict[str, str]:
        return dict(DEFAULT_MODEL_ROLES)

    def persist(self, mapping: Mapping[str, str]) -> dict[str, str]:
        written = _require_roles(mapping)
        text = self.config_path.read_text() if self.config_path.exists() else ""
        if text.strip():
            _parse_toml(text)
        for role, model in written.items():
            text = _upsert_role_model(text, role, model)
        if text and not text.endswith("\n"):
            text += "\n"
        _validate_written(text, written)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(text)
        return written


def _require_roles(mapping: Mapping[str, str]) -> dict[str, str]:
    if set(mapping) != set(ROLES):
        raise ValueError("model roles must be exactly xhigh, max, and fast")
    return {role: mapping[role] for role in ROLES}


def _table_header(role: str) -> re.Pattern[str]:
    name = re.escape(role)
    return re.compile(
        rf'^[ \t]*\[\s*subagents\.roles\.(?:"{name}"|\'{name}\'|{name})\s*\][ \t]*(#.*)?$'
    )


def _advance_multiline(state: str | None, content: str) -> str | None:
    index = 0
    while index < len(content):
        if state is None:
            if content.startswith(_TRIPLE_DOUBLE, index):
                state = _TRIPLE_DOUBLE
                index += 3
                continue
            if content.startswith(_TRIPLE_SINGLE, index):
                state = _TRIPLE_SINGLE
                index += 3
                continue
            index += 1
            continue
        if content.startswith(state, index):
            state = None
            index += 3
            continue
        index += 1
    return state


def _upsert_role_model(text: str, role: str, model: str) -> str:
    header = f"[subagents.roles.{role}]"
    model_line = f'model = "{model}"'
    lines = text.splitlines(keepends=True)
    header_re = _table_header(role)
    start = None
    state: str | None = None
    for index, line in enumerate(lines):
        content = line.rstrip("\n\r")
        if state is None and header_re.match(content):
            start = index
            break
        state = _advance_multiline(state, content)
    if start is None:
        block = f"{header}\n{model_line}\n"
        if text == "":
            return block
        if not text.endswith("\n"):
            text += "\n"
        if not text.endswith("\n\n"):
            text += "\n"
        return text + block
    if not lines[start].endswith("\n"):
        lines[start] += "\n"
    end = len(lines)
    state = _advance_multiline(None, lines[start].rstrip("\n\r"))
    for index in range(start + 1, len(lines)):
        content = lines[index].rstrip("\n\r")
        if state is None and _NEXT_TABLE.match(lines[index]):
            end = index
            break
        state = _advance_multiline(state, content)
    state = _advance_multiline(None, lines[start].rstrip("\n\r"))
    for index in range(start + 1, end):
        content = lines[index].rstrip("\n\r")
        if state is None and _MODEL_KEY.match(lines[index]):
            indent = re.match(r"^[ \t]*", lines[index])
            pad = indent.group(0) if indent else ""
            newline = "\n" if lines[index].endswith("\n") else ""
            lines[index] = f"{pad}{model_line}{newline}"
            return "".join(lines)
        state = _advance_multiline(state, content)
    indent = re.match(r"^[ \t]*", lines[start])
    pad = indent.group(0) if indent else ""
    lines.insert(start + 1, f"{pad}{model_line}\n")
    return "".join(lines)


def _parse_toml(text: str) -> dict[str, object]:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"Grok config is not valid TOML: {error}") from error


def _validate_written(text: str, written: Mapping[str, str]) -> None:
    parsed = _parse_toml(text)
    subagents = parsed.get("subagents")
    if not isinstance(subagents, dict):
        raise ValueError("Grok config missing subagents.roles after persist")  # noqa: TRY004
    roles = subagents.get("roles")
    if not isinstance(roles, dict):
        raise ValueError("Grok config missing subagents.roles after persist")  # noqa: TRY004
    for role, model in written.items():
        table = roles.get(role)
        if not isinstance(table, dict) or table.get("model") != model:
            raise ValueError(f"Grok config did not persist {role}")
