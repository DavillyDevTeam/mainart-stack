"""Packet-chain import acceptance checks."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_packet_chain import problems
from scripts.check_vendor import git_tree

PINNED_REVISION = "d1478fcb140db0b93c0c8df17bcfd311844749d0"
V131_TAG = "0b6cee10f260a2e048279cf737bfd3e37b1fce0b"

def _copy_tree(root: Path) -> None:
    for directory in ("core", "vendor", "hosts"):
        src = ROOT / directory
        if src.exists():
            shutil.copytree(src, root / directory)


class PacketChainImportTest(unittest.TestCase):
    def test_provenance_records_the_pinned_revision_and_skill_folder_hashes(self) -> None:
        provenance = json.loads((ROOT / "vendor/matt-packet-chain-provenance.json").read_text())
        self.assertEqual(provenance["revision"], PINNED_REVISION)
        self.assertEqual(provenance["version"], "1.3.2")
        self.assertNotEqual(provenance["revision"], V131_TAG)
        recorded = {name: skill["tree"] for name, skill in provenance["skills"].items()}
        actual = {name: git_tree(f"core/skills/{name}") for name in recorded}
        self.assertEqual(recorded, actual)

    def test_shipped_import_has_no_problems(self) -> None:
        self.assertEqual(problems(ROOT), [])

    def test_core_keeps_matt_tdd_and_leaves_pstack_tdd_in_the_vendor_tree(self) -> None:
        core_tdd = (ROOT / "core/skills/tdd/SKILL.md").read_bytes()
        vendor_tdd = (ROOT / "vendor/pstack/skills/tdd/SKILL.md").read_bytes()
        self.assertNotEqual(core_tdd, vendor_tdd)
        self.assertIn(b"name: tdd", core_tdd)

    def test_checker_rejects_a_hash_mismatch_and_a_missing_companion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_tree(root)
            self.assertEqual(problems(root), [])

            provenance_path = root / "vendor/matt-packet-chain-provenance.json"
            provenance = json.loads(provenance_path.read_text())
            provenance["skills"]["tdd"]["tree"] = "0" * 40
            provenance_path.write_text(json.dumps(provenance))
            self.assertIn(
                "tree mismatch for tdd",
                problems(root),
            )

            provenance["skills"]["tdd"]["tree"] = git_tree("core/skills/tdd")
            provenance_path.write_text(json.dumps(provenance))
            (root / "core/skills/tdd/tests.md").unlink()
            self.assertIn(
                "missing file: core/skills/tdd/tests.md",
                problems(root),
            )

    def test_checker_rejects_adapter_metadata_and_unselected_skills_in_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_tree(root)
            yaml = root / "core/skills/grilling/agents/openai.yaml"
            yaml.parent.mkdir(parents=True)
            yaml.write_text("interface: {}")
            self.assertIn(
                "adapter metadata in core: core/skills/grilling/agents/openai.yaml",
                problems(root),
            )
            yaml.unlink()
            (root / "core/skills/ask-matt").mkdir()
            (root / "core/skills/ask-matt/SKILL.md").write_text("---\nname: ask-matt\n---\n")
            self.assertIn("unselected skill in core: skills/ask-matt", problems(root))
            (root / "core/skills/ask-matt/SKILL.md").unlink()
            (root / "core/skills/ask-matt").rmdir()
            (root / "core/skills/codebase-design").mkdir()
            (root / "core/skills/codebase-design/SKILL.md").write_text(
                "---\nname: codebase-design\n---\n"
            )
            self.assertIn(
                "unselected skill in core: skills/codebase-design",
                problems(root),
            )
            (root / "core/skills/codebase-design/SKILL.md").unlink()
            (root / "core/skills/codebase-design").rmdir()
            extra = root / "core/skills/grilling/NOTES.md"
            extra.write_text("not in the pin\n")
            self.assertIn(
                "unexpected file in core: core/skills/grilling/NOTES.md",
                problems(root),
            )


if __name__ == "__main__":
    unittest.main()
