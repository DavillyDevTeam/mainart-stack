"""Grok exposure of packet-chain entry points."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ADAPTER_ROOT = Path(__file__).resolve().parent
REPO_ROOT = ADAPTER_ROOT.parents[1]
INVOCATION_PATH = ADAPTER_ROOT / "invocation.json"


class ImplicitInvocationRejected(RuntimeError):
    """HITL skills require an explicit user invocation."""


@dataclass(frozen=True)
class InvocationResult:
    available: bool
    mode: str
    skill: str
    qualified_name: str
    disable_model_invocation: bool
    body: Path


def _string_list(block: dict[str, object], key: str) -> set[str]:
    value = block[key]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"{key} must be a list of strings")
    return set(value)


def _object_map(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload[key]
    if not isinstance(value, dict):
        raise TypeError(f"{key} must be an object")
    return value


class GrokPacketChain:
    def __init__(self, invocation: dict[str, object], root: Path) -> None:
        self._root = root
        self._invocation = invocation
        qualification = invocation["qualification"]
        if not isinstance(qualification, str):
            raise TypeError("qualification must be a string")
        self._qualification = qualification
        core_root = invocation["core_root"]
        if not isinstance(core_root, str):
            raise TypeError("core_root must be a string")
        self._core_root = core_root
        hitl = _object_map(invocation, "hitl")
        self._hitl_skills = _string_list(hitl, "skills")
        self._hitl_disable_model = bool(hitl["disable-model-invocation"])
        primitives = _object_map(invocation, "primitives")
        self._primitive_skills = _string_list(primitives, "skills")
        self._primitives_available = bool(primitives["internally_available"])
        self._primitive_disable_model = bool(primitives["disable-model-invocation"])
        grilling = _object_map(invocation, "grilling")
        channel = grilling["channel"]
        if not isinstance(channel, str):
            raise TypeError("grilling.channel must be a string")
        self._grilling_channel = channel
        self._numbered_questions = bool(grilling["numbered_questions"])
        self._recommendations = bool(grilling["recommendations"])

    @classmethod
    def open(cls, root: Path | None = None) -> GrokPacketChain:
        base = root if root is not None else REPO_ROOT
        path = base / "hosts/grok/invocation.json"
        payload = json.loads(path.read_text())
        if not isinstance(payload, dict):
            raise TypeError("invocation metadata must be an object")
        return cls(payload, base)

    def invoke(
        self, name: str, *, explicit: bool = False, internal: bool = False
    ) -> InvocationResult:
        body = self._root / self._core_root / name / "SKILL.md"
        qualified = self._qualification.format(name=name)
        if name in self._hitl_skills:
            if not explicit:
                raise ImplicitInvocationRejected(name)
            if not body.is_file():
                raise FileNotFoundError(body)
            return InvocationResult(
                True,
                "explicit",
                name,
                qualified,
                self._hitl_disable_model,
                body,
            )
        if name in self._primitive_skills:
            if not self._primitives_available:
                raise RuntimeError(f"{name} is not internally available")
            if not body.is_file():
                raise FileNotFoundError(body)
            mode = "internal" if internal or not explicit else "explicit"
            return InvocationResult(
                True,
                mode,
                name,
                qualified,
                self._primitive_disable_model,
                body,
            )
        raise KeyError(name)

    @property
    def grilling_channel(self) -> str:
        return self._grilling_channel

    @property
    def numbered_questions(self) -> bool:
        return self._numbered_questions

    @property
    def recommendations(self) -> bool:
        return self._recommendations
