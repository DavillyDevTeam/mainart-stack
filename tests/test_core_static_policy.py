"""Static policy checks for the first router-to-bug-fix slice.

These checks read shipped files. They do not score prompt wording.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_core_slice import forbidden_hits, tdd_collision_problems, violations


class CoreStaticPolicyTest(unittest.TestCase):
    def test_forbidden_scanner_catches_a_native_host_api(self) -> None:
        self.assertIn("spawn_subagent", forbidden_hits("then call spawn_subagent"))

    def test_shipped_slice_has_no_policy_violations(self) -> None:
        self.assertEqual(violations(ROOT), [])

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


if __name__ == "__main__":
    unittest.main()
