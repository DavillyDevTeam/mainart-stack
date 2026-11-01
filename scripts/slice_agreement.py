"""Fail-closed agreement for the router slice.

The Grok session and the core-slice check both call this module.
A core-slice rule change does not edit the host session.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, cast

CHEAP_FAILING_TEST_FIRST: Literal["cheap-failing-test-first"] = (
    "cheap-failing-test-first"
)
IMPRACTICAL_OR_EXPENSIVE: Literal["impractical-or-expensive"] = (
    "impractical-or-expensive"
)
SETTLED_SIGNALS = ("data_shape", "repro", "metric", "acceptance")
GOAL_CONTINUATION_CAP = 8


def _section(data: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = data.get(key)
    if isinstance(value, dict):
        return cast(Mapping[str, object], value)
    return {}


def agreement_problems(
    policy: Mapping[str, object],
    invocation: Mapping[str, object],
    bugfix: Mapping[str, object],
) -> list[str]:
    """Shared fail-closed gate for the session and the core-slice check."""

    problems: list[str] = []
    if policy.get("canonical_token") != "mstack" or policy.get("aliases") != [
        "poteto-mode"
    ]:
        problems.append(
            "router policy tokens are not mstack plus the poteto-mode alias"
        )
    if policy.get("directory") != "poteto-mode":
        problems.append("router directory must stay poteto-mode")
    settled = _section(policy, "settled_what")
    if settled.get("signals") != list(SETTLED_SIGNALS):
        problems.append(
            "settled-what signals are not data shape, repro, metric, and acceptance"
        )
    principles = _section(policy, "principles")
    if (
        principles.get("apply_during") != "playbook"
        or principles.get("can_suppress_hitl") is not False
    ):
        problems.append("principles are not scoped to the playbook phase")
    judge = _section(policy, "judge")
    if (
        judge.get("required") is not False
        or judge.get("overrides_explicit") is not False
        or judge.get("overrides_unscoped_gate") is not False
    ):
        problems.append("validation.judge is a gate in the router policy")
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
    runner = _section(invocation, "runner")
    if (
        runner.get("role") != "playbook-runner"
        or runner.get("placement") != "in-session"
    ):
        problems.append("Grok does not adopt playbook-runner in-session")
    if invocation.get("nested_spawn_worker") is not False:
        problems.append("Grok permits nested spawn-worker")
    testing = _section(bugfix, "testing")
    if testing.get("cadence") != CHEAP_FAILING_TEST_FIRST:
        problems.append("bug-fix lost cheap failing-test-first")
    if testing.get("exception") != IMPRACTICAL_OR_EXPENSIVE:
        problems.append("bug-fix lost the impractical or expensive test exception")
    if (
        testing.get("invokes_skill") is not None
        or bugfix.get("requires_packet") is not False
    ):
        problems.append("bug-fix calls Matt tdd or requires a tracker packet")
    return problems
