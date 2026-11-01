"""Static policy checks for the first router-to-bug-fix slice.

These checks read shipped files. They do not score prompt wording.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hosts.grok.session import ClarificationRequired, GrokCoordinator, Prompt
from scripts.check_core_slice import (
    forbidden_hits,
    slice_copy_problems,
    tdd_collision_problems,
    violations,
)


def _copy_slice(root: Path) -> None:
    for directory in ("core", "vendor"):
        shutil.copytree(ROOT / directory, root / directory)
    invocation = root / "hosts/grok/invocation.json"
    invocation.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "hosts/grok/invocation.json", invocation)


class CoreStaticPolicyTest(unittest.TestCase):
    def test_forbidden_scanner_catches_a_native_host_api(self) -> None:
        self.assertIn("spawn_subagent", forbidden_hits("then call spawn_subagent"))

    def test_shipped_slice_has_no_policy_violations(self) -> None:
        self.assertEqual(violations(ROOT), [])

    def test_session_and_slice_check_reject_a_judge_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_slice(root)
            policy_path = root / "core/skills/poteto-mode/router-policy.json"
            with patch("hosts.grok.session.POLICY_PATH", policy_path):
                self.assertEqual(
                    GrokCoordinator.open("mstack").core_skill, "poteto-mode"
                )
                self.assertEqual(violations(root), [])

                policy = json.loads(policy_path.read_text())
                policy["judge"]["overrides_explicit"] = True
                policy_path.write_text(json.dumps(policy))

                problem = "validation.judge is a gate in the router policy"
                self.assertEqual(violations(root), [problem])
                with self.assertRaises(RuntimeError) as rejected:
                    GrokCoordinator.open("mstack")
                self.assertEqual(str(rejected.exception), problem)

    def test_procedure_rewording_preserves_clarification_and_testing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_slice(root)
            replacements = (
                ("must not suppress", "must never suppress"),
                (
                    "a data shape, a repro, a metric, or an acceptance",
                    "a schema, a reproduction, a measurement, or completion criteria",
                ),
                ("cheap failing-test-first", "write a low-cost failing test first"),
                ("impractical or expensive", "infeasible or costly"),
                ("Do not call the tdd skill", "Do not invoke skills/tdd"),
            )
            for path in (root / "core").rglob("*.md"):
                text = path.read_text()
                for original, replacement in replacements:
                    text = text.replace(original, replacement)
                path.write_text(text)

            self.assertEqual(violations(root), [])
            with patch.multiple(
                "hosts.grok.session",
                POLICY_PATH=root / "core/skills/poteto-mode/router-policy.json",
                BUGFIX_POLICY_PATH=(
                    root / "core/skills/poteto-mode/playbooks/bug-fix.policy.json"
                ),
                INVOCATION_PATH=root / "hosts/grok/invocation.json",
            ):
                session = GrokCoordinator.open("mstack")
                prompt = Prompt(text="Make the app better.")
                waiting = session.route(prompt)

                self.assertEqual(waiting.workflow, "hitl")
                self.assertFalse(waiting.principles_active)
                with self.assertRaises(ClarificationRequired):
                    session.begin(waiting)
                with self.assertRaises(ClarificationRequired):
                    session.spawn_worker("poteto-agent", "start coding")
                with self.assertRaises(ClarificationRequired):
                    session.overnight(mode="until", done="the defect is fixed")

                decision = session.route(prompt, explicit="bug-fix")
                run = session.begin(decision)

                self.assertTrue(run.principles_active)
                self.assertEqual(run.testing_cadence, "cheap-failing-test-first")
                self.assertEqual(run.testing_exception, "impractical-or-expensive")
                self.assertNotIn("tdd", run.invoked_skills)

    def test_session_and_slice_check_reject_principles_during_hitl(self) -> None:
        for field, value in (("apply_during", "hitl"), ("can_suppress_hitl", True)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _copy_slice(root)
                policy_path = root / "core/skills/poteto-mode/router-policy.json"
                policy = json.loads(policy_path.read_text())
                policy["principles"][field] = value
                policy_path.write_text(json.dumps(policy))

                problem = "principles are not scoped to the playbook phase"
                self.assertEqual(violations(root), [problem])
                with (
                    patch("hosts.grok.session.POLICY_PATH", policy_path),
                    self.assertRaises(RuntimeError) as rejected,
                ):
                    GrokCoordinator.open("mstack")
                self.assertEqual(str(rejected.exception), problem)

    def test_packet_chain_skills_and_companions_coexist_with_pstack_copies(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_slice(root)
            for skill in (
                "grill-with-docs",
                "grill-me",
                "to-spec",
                "to-tickets",
                "wayfinder",
                "triage",
                "implement",
                "implement-spec",
                "setup-matt-pocock-skills",
                "grilling",
                "domain-modeling",
                "prototype",
                "tdd",
                "code-review",
                "research",
            ):
                skill_root = root / "core/skills" / skill
                skill_root.mkdir()
                (skill_root / "SKILL.md").write_text(
                    f"---\nname: {skill}\n---\nMatt packet-chain procedure.\n"
                )
            for relative in (
                "tdd/tests.md",
                "tdd/mocking.md",
                "domain-modeling/GLOSSARY-FORMAT.md",
                "domain-modeling/ADR-FORMAT.md",
                "prototype/LOGIC.md",
                "prototype/UI.md",
                "triage/AGENT-BRIEF.md",
                "setup-matt-pocock-skills/templates/issue-tracker-github.md",
            ):
                companion = root / "core/skills" / relative
                companion.parent.mkdir(parents=True, exist_ok=True)
                companion.write_text("Matt packet-chain companion.\n")

            self.assertEqual(violations(root), [])

            tdd = root / "core/skills/tdd/SKILL.md"
            tdd.write_bytes((root / "vendor/pstack/skills/tdd/SKILL.md").read_bytes())
            self.assertIn(
                "pstack copy occupies packet-chain path: skills/tdd/SKILL.md",
                violations(root),
            )

    def test_packet_chain_exclusion_keeps_other_policy_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_slice(root)
            packet_skill = root / "core/skills/grill-with-docs/SKILL.md"
            packet_skill.parent.mkdir()
            packet_skill.write_text("Call spawn_subagent.\n")
            unknown_skill = root / "core/skills/unknown/SKILL.md"
            unknown_skill.parent.mkdir()
            unknown_skill.write_text("Unknown skill.\n")

            self.assertEqual(
                violations(root),
                [
                    "not a same-relative-path core copy: skills/unknown/SKILL.md",
                    "core/skills/grill-with-docs/SKILL.md: spawn_subagent",
                ],
            )

    def test_matt_tdd_may_occupy_core_but_a_pstack_copy_may_not(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vendor = root / "vendor"
            core = root / "core"
            vendor_skill = vendor / "skills" / "tdd"
            vendor_skill.mkdir(parents=True)
            (vendor_skill / "SKILL.md").write_text("pstack tdd\n")

            self.assertEqual(tdd_collision_problems(core, vendor), [])

            core_skill = core / "skills" / "tdd"
            core_skill.mkdir(parents=True)
            (core_skill / "SKILL.md").write_text("matt tdd\n")
            self.assertEqual(tdd_collision_problems(core, vendor), [])

            (core_skill / "SKILL.md").write_text("pstack tdd\n")
            problems = tdd_collision_problems(core, vendor)
            self.assertEqual(
                problems,
                ["pstack copy occupies packet-chain path: skills/tdd/SKILL.md"],
            )

    def test_slice_skill_keeps_rewritten_vendor_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vendor = root / "vendor"
            core = root / "core"
            vendor_skill = vendor / "skills" / "poteto-help"
            (vendor_skill / "references").mkdir(parents=True)
            (vendor_skill / "SKILL.md").write_text(
                "---\nname: poteto-help\n---\nvendor help\n"
            )
            (vendor_skill / "references" / "prompting.md").write_text(
                "vendor prompting\n"
            )
            core_skill = core / "skills" / "poteto-help"
            core_skill.mkdir(parents=True)
            (core_skill / "SKILL.md").write_text(
                "---\nname: poteto-help\n---\nrewritten help\n"
            )

            missing = slice_copy_problems(core, vendor)
            self.assertIn(
                "missing same-relative-path core copy: "
                "skills/poteto-help/references/prompting.md",
                missing,
            )

            copied = core_skill / "references"
            copied.mkdir()
            (copied / "prompting.md").write_text("vendor prompting\n")
            raw = slice_copy_problems(core, vendor)
            self.assertIn(
                "core copy is not rewritten: "
                "skills/poteto-help/references/prompting.md",
                raw,
            )


if __name__ == "__main__":
    unittest.main()
