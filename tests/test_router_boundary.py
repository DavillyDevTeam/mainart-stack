"""Observable seam: Grok coordinator route / begin / spawn-worker.

Pre-agreed by issue 25 and the primary acceptance scenarios R1, R2, R5,
and R10 in docs/spec.md. Tests speak in workflow outcomes. They do not
assert prompt wording or private reasoning.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hosts.grok.session import (
    ClarificationRequired,
    GrokCoordinator,
    JudgeAdvice,
    NestedSpawnRejected,
    Prompt,
    UnknownInvocation,
    UnknownRole,
)

ROUTER_DESCRIPTION = (
    "The mode skill that classifies an unscoped request as Matt HITL or a "
    "pstack playbook. Explicit skills and named playbooks skip it."
)

SETTLED_DEFECT = Prompt(
    text="The saved record disappears after refresh.",
    repro="Save a record, refresh the page, and the record is gone.",
    acceptance="The saved record is present after refresh.",
    reported_defect=True,
)

UNSETTLED = Prompt(text="Make the app better.")


class RouterBoundaryTest(unittest.TestCase):
    def test_r1_unscoped_unsettled_request_waits_for_hitl(self) -> None:
        session = GrokCoordinator.open("mstack")

        decision = session.route(UNSETTLED)

        self.assertEqual(decision.workflow, "hitl")
        self.assertEqual(decision.name, "grill-with-docs")
        self.assertTrue(decision.waits_for_clarification)
        self.assertFalse(decision.principles_active)
        self.assertFalse(decision.creates_tracker_packet)
        with self.assertRaises(ClarificationRequired):
            session.begin(decision)
        self.assertIsNone(session.runner)
        self.assertEqual(session.spawned_roles, ())

    def test_r1_defect_without_a_settled_signal_still_waits(self) -> None:
        session = GrokCoordinator.open("mstack")
        prompt = Prompt(text="The save button is broken.", reported_defect=True)

        decision = session.route(prompt)

        self.assertEqual(decision.workflow, "hitl")
        self.assertEqual(decision.name, "grill-with-docs")
        self.assertTrue(decision.waits_for_clarification)

    def test_r2_settled_defect_selects_bug_fix_without_a_packet(self) -> None:
        session = GrokCoordinator.open("mstack")

        decision = session.route(SETTLED_DEFECT, judge=JudgeAdvice(status="unbound"))

        self.assertEqual(decision.workflow, "playbook")
        self.assertEqual(decision.name, "bug-fix")
        self.assertFalse(decision.creates_tracker_packet)
        self.assertFalse(decision.waits_for_clarification)
        self.assertTrue(decision.principles_active)
        self.assertFalse(decision.judge_changed_outcome)

        run = session.begin(decision)

        self.assertEqual(run.playbook, "bug-fix")
        self.assertEqual(run.runner, "playbook-runner")
        self.assertTrue(run.adopted_in_session)
        self.assertTrue(session.adopted_in_session)
        self.assertEqual(session.runner, "playbook-runner")
        self.assertFalse(run.creates_tracker_packet)
        self.assertEqual(run.testing_cadence, "cheap-failing-test-first")
        self.assertEqual(run.testing_exception, "impractical-or-expensive")
        self.assertNotIn("tdd", run.invoked_skills)
        self.assertEqual(session.spawned_roles, ())

    def test_settled_non_defect_does_not_use_bug_fix(self) -> None:
        session = GrokCoordinator.open("mstack")
        prompt = Prompt(
            text="Add an export button.",
            acceptance="A member can download a CSV of their records.",
            reported_defect=False,
        )

        decision = session.route(prompt)

        self.assertEqual(decision.workflow, "hitl")
        self.assertEqual(decision.name, "grill-with-docs")

    def test_r5_explicit_hitl_survives_a_disagreeing_judge(self) -> None:
        session = GrokCoordinator.open("mstack")
        disagree = JudgeAdvice(
            status="answered", workflow="playbook", playbook="bug-fix"
        )

        decision = session.route(
            SETTLED_DEFECT, explicit="grill-with-docs", judge=disagree
        )

        self.assertEqual(decision.workflow, "hitl")
        self.assertEqual(decision.name, "grill-with-docs")
        self.assertTrue(decision.waits_for_clarification)
        self.assertFalse(decision.judge_changed_outcome)
        self.assertFalse(decision.principles_active)

    def test_r5_explicit_bug_fix_survives_a_disagreeing_judge(self) -> None:
        session = GrokCoordinator.open("poteto-mode")
        disagree = JudgeAdvice(status="answered", workflow="hitl")

        decision = session.route(UNSETTLED, explicit="bug-fix", judge=disagree)

        self.assertEqual(decision.workflow, "playbook")
        self.assertEqual(decision.name, "bug-fix")
        self.assertFalse(decision.waits_for_clarification)
        self.assertFalse(decision.judge_changed_outcome)
        run = session.begin(decision)
        self.assertEqual(run.testing_cadence, "cheap-failing-test-first")
        self.assertNotIn("tdd", run.invoked_skills)

    def test_r10_mstack_and_poteto_mode_classify_the_same(self) -> None:
        prompts = (
            UNSETTLED,
            SETTLED_DEFECT,
            Prompt(
                text="Export is slow.",
                metric="Export p95 is under 300ms on the fixture set.",
                reported_defect=True,
            ),
        )

        for prompt in prompts:
            via_canonical = GrokCoordinator.open("mstack").route(
                prompt, judge=JudgeAdvice(status="unbound")
            )
            via_alias = GrokCoordinator.open("poteto-mode").route(
                prompt, judge=JudgeAdvice(status="answered", workflow="hitl")
            )
            self.assertEqual(via_canonical, via_alias)

    def test_identity_tokens_and_description(self) -> None:
        session = GrokCoordinator.open("mstack")

        self.assertEqual(session.plugin_id, "mainart-stack")
        self.assertEqual(session.core_skill, "poteto-mode")
        self.assertEqual(session.canonical_token, "mstack")
        self.assertEqual(session.aliases, ("poteto-mode",))
        self.assertEqual(session.tokens, ("mstack", "poteto-mode"))
        self.assertFalse(session.implicit_invocation)
        self.assertEqual(session.description, ROUTER_DESCRIPTION)
        self.assertEqual(GrokCoordinator.open("poteto-mode").core_skill, "poteto-mode")

        with self.assertRaises(UnknownInvocation):
            GrokCoordinator.open("mainart")
        with self.assertRaises(UnknownInvocation):
            GrokCoordinator.open("router")
        with self.assertRaises(UnknownInvocation):
            session.route(SETTLED_DEFECT, explicit="feature")

    def test_playbook_runner_is_adopted_and_workers_cannot_nest(self) -> None:
        session = GrokCoordinator.open("mstack")
        decision = session.route(SETTLED_DEFECT)
        session.begin(decision)

        adopted = session.spawn_worker("playbook-runner", "execute bug-fix")

        self.assertEqual(adopted.kind, "adopted")
        self.assertEqual(adopted.role, "playbook-runner")
        self.assertEqual(session.spawned_roles, ())
        self.assertTrue(session.adopted_in_session)

        worker = session.spawn_worker(
            "poteto-agent", "land the failing repro, then the fix"
        )

        self.assertEqual(worker.kind, "worker")
        self.assertEqual(worker.native_type, "mainart-stack:poteto-agent")
        self.assertEqual(worker.isolation, "same-tree")
        self.assertEqual(worker.depth, 1)
        self.assertEqual(session.spawned_roles, ("poteto-agent",))
        with self.assertRaises(NestedSpawnRejected):
            worker.spawn_worker("poteto-agent", "keep going")
        with self.assertRaises(UnknownRole):
            session.spawn_worker("generalPurpose", "no")
        with self.assertRaises(ValueError):
            session.spawn_worker("poteto-agent", "edit", model_role="grok-4.7")

        isolated = session.spawn_worker(
            "comment-sicko",
            "review comments",
            isolation="isolated",
            model_role="fast",
        )
        self.assertEqual(isolated.isolation, "isolated")
        self.assertEqual(isolated.model_role, "fast")
        self.assertEqual(isolated.native_type, "mainart-stack:comment-sicko")


if __name__ == "__main__":
    unittest.main()
