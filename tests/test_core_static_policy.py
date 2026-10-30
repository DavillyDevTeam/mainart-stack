"""Static policy checks for the first router-to-bug-fix slice.

These checks read shipped files. They do not score prompt wording.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_core_slice import forbidden_hits, violations


class CoreStaticPolicyTest(unittest.TestCase):
    def test_forbidden_scanner_catches_a_native_host_api(self) -> None:
        self.assertIn("spawn_subagent", forbidden_hits("then call spawn_subagent"))

    def test_shipped_slice_has_no_policy_violations(self) -> None:
        self.assertEqual(violations(ROOT), [])


if __name__ == "__main__":
    unittest.main()
