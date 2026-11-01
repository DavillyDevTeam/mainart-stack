"""Packet-chain import and Grok entry-point acceptance checks."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hosts.grok.packet_chain import (
    GrokPacketChain,
    ImplicitInvocationRejected,
)
from scripts.check_packet_chain import problems

PINNED_REVISION = "b645f47de3e17ed3bf60586c9bebb8092e0f79fd"
V131_TAG = "0b6cee10f260a2e048279cf737bfd3e37b1fce0b"

SKILL_FOLDER_HASHES = {
    "grill-with-docs": "eedaf2562c83155115e9c649fa3ecaac2e10e81d",
    "grill-me": "3df14e2d3a89459bf300614be9247e3ce74798f8",
    "to-spec": "136b9651747cfccbfbb7c50a6b0dfb757e7547d2",
    "to-tickets": "2dee20ad722a31c04ededf9f2d83842473573045",
    "wayfinder": "8ec0462658381bd1606d3f9db14ffc67df6a2a43",
    "triage": "4cb951d62ecccaed601cdc5f9a1b7b3d8a799635",
    "implement": "27a09574c533d4b9a66c7b2b43cdfeeeb9f415b5",
    "implement-spec": "0cfefc751d0cb64f0c948ffcb17e13b94e778f08",
    "setup-matt-pocock-skills": "0b280474a635c9c0efc2bcb2665c87163851bf14",
    "grilling": "f0732035b8b1b60ae39454e4191caef32fa91903",
    "domain-modeling": "ea30ee454ba264543dbe40737973b1a5afb9f0e6",
    "prototype": "e41d92e171f074a2b6887d8f6faca4a15c83d1ca",
    "tdd": "bf1bf5ffcd63aa8abce830f2955a853c121fb463",
    "code-review": "d8e341cee7980127dddda05159bedf25dc853615",
    "research": "0a6796c5667e95ed2301ba7381c123b4acb2ae1a",
}

EXPLICIT_HITL = (
    "grill-with-docs",
    "grill-me",
    "to-spec",
    "to-tickets",
    "wayfinder",
    "triage",
    "implement",
    "implement-spec",
    "setup-matt-pocock-skills",
)
PRIMITIVES = (
    "grilling",
    "domain-modeling",
    "prototype",
    "tdd",
    "code-review",
    "research",
)


def _copy_tree(root: Path) -> None:
    for directory in ("core", "vendor", "hosts"):
        src = ROOT / directory
        if src.exists():
            shutil.copytree(src, root / directory)


class PacketChainImportTest(unittest.TestCase):
    def test_provenance_records_the_pinned_revision_and_skill_folder_hashes(self) -> None:
        provenance = json.loads((ROOT / "vendor/matt-packet-chain-provenance.json").read_text())
        self.assertEqual(provenance["revision"], PINNED_REVISION)
        self.assertNotEqual(provenance["revision"], V131_TAG)
        recorded = {name: skill["tree"] for name, skill in provenance["skills"].items()}
        self.assertEqual(recorded, SKILL_FOLDER_HASHES)

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
                "skillFolderHash mismatch for tdd",
                problems(root),
            )

            provenance["skills"]["tdd"]["tree"] = SKILL_FOLDER_HASHES["tdd"]
            provenance_path.write_text(json.dumps(provenance))
            (root / "core/skills/tdd/tests.md").unlink()
            self.assertIn(
                "missing companion: core/skills/tdd/tests.md",
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


class GrokPacketChainInvocationTest(unittest.TestCase):
    def test_explicit_hitl_skills_run_only_when_the_user_invokes_them(self) -> None:
        host = GrokPacketChain.open(ROOT)
        for name in EXPLICIT_HITL:
            with self.subTest(name=name):
                result = host.invoke(name, explicit=True)
                self.assertTrue(result.available)
                self.assertEqual(result.mode, "explicit")
                self.assertEqual(result.qualified_name, f"/mainart-stack:{name}")
                self.assertTrue(result.disable_model_invocation)
                self.assertTrue(result.body.is_file())
                with self.assertRaises(ImplicitInvocationRejected):
                    host.invoke(name)

    def test_primitives_are_available_internally(self) -> None:
        host = GrokPacketChain.open(ROOT)
        for name in PRIMITIVES:
            with self.subTest(name=name):
                result = host.invoke(name, internal=True)
                self.assertTrue(result.available)
                self.assertEqual(result.mode, "internal")
                self.assertEqual(result.qualified_name, f"/mainart-stack:{name}")
                self.assertFalse(result.disable_model_invocation)
                self.assertTrue(result.body.is_file())

    def test_grilling_keeps_numbered_questions_in_plain_chat(self) -> None:
        host = GrokPacketChain.open(ROOT)
        self.assertEqual(host.grilling_channel, "plain-chat")
        self.assertTrue(host.numbered_questions)
        self.assertTrue(host.recommendations)
        grilling = (ROOT / "core/skills/grilling/SKILL.md").read_text()
        self.assertNotIn("AskUserQuestion", grilling)
        self.assertNotIn("AskQuestion", grilling)
        self.assertIn("number each question", grilling)
        self.assertIn("recommended answer", grilling)

    def test_invocation_metadata_lives_in_the_adapter(self) -> None:
        invocation = json.loads((ROOT / "hosts/grok/invocation.json").read_text())
        self.assertEqual(invocation["plugin_id"], "mainart-stack")
        self.assertEqual(invocation["qualification"], "/mainart-stack:{name}")
        self.assertFalse(invocation["hitl"]["implicit_invocation"])
        self.assertTrue(invocation["hitl"]["disable-model-invocation"])
        self.assertTrue(invocation["primitives"]["internally_available"])
        self.assertFalse(invocation["primitives"]["disable-model-invocation"])
        self.assertEqual(invocation["grilling"]["channel"], "plain-chat")
        self.assertEqual(
            set(invocation["hitl"]["skills"]),
            set(EXPLICIT_HITL),
        )
        self.assertEqual(
            set(invocation["primitives"]["skills"]),
            set(PRIMITIVES),
        )


if __name__ == "__main__":
    unittest.main()
