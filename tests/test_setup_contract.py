"""Observable seam: core setup / persist-model-roles / project pins.

Pre-agreed by issue 24 and the adapter contract checks in docs/spec.md.
Tests speak in host files, pin files, and delegated model-role mappings.
They do not assert prompt wording or private reasoning.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.host_setup import HOST_IDS, UnknownHost, configure
from hosts.grok.persist_model_roles import GrokModelRoles


class RecordingPersist:
    def __init__(self, defaults: dict[str, str] | None = None) -> None:
        self.defaults_map = defaults or {
            "xhigh": "adapter-xhigh",
            "max": "adapter-max",
            "fast": "adapter-fast",
        }
        self.persisted: dict[str, str] | None = None

    def defaults(self) -> dict[str, str]:
        return dict(self.defaults_map)

    def persist(self, mapping: Mapping[str, str]) -> dict[str, str]:
        self.persisted = dict(mapping)
        return dict(mapping)


def _project(hosts: dict[str, str] | None = None) -> tuple[Path, Path, RecordingPersist]:
    tmp = Path(tempfile.mkdtemp())
    project = tmp / "project"
    hosts_root = tmp / "hosts"
    project.mkdir()
    for host_id, pins in (hosts or {}).items():
        host_dir = hosts_root / host_id
        host_dir.mkdir(parents=True)
        (host_dir / "pins.yaml").write_text(pins)
    persist = RecordingPersist()
    return project, hosts_root, persist


class HostSelectionTest(unittest.TestCase):
    def test_setup_persists_local_host_as_gitignored_state(self) -> None:
        project, hosts_root, persist = _project({"grok": "{}\n"})

        result = configure(project, "grok", hosts_root=hosts_root, persist=persist)

        self.assertEqual((project / ".mainart/host").read_text(), "grok\n")
        self.assertEqual(result.host_id, "grok")
        gitignore = (project / ".gitignore").read_text().splitlines()
        self.assertIn(".mainart/host", gitignore)
        self.assertNotIn(".mainart/pins.yaml", gitignore)
        self.assertNotIn(".mainart/", gitignore)

    def test_unknown_host_is_rejected(self) -> None:
        project, hosts_root, persist = _project()

        with self.assertRaises(UnknownHost):
            configure(project, "cursor", hosts_root=hosts_root, persist=persist)

        self.assertFalse((project / ".mainart/host").exists())
        self.assertIsNone(persist.persisted)


class ProjectPinsTest(unittest.TestCase):
    def test_missing_pins_initialize_from_the_selected_host_defaults(self) -> None:
        grok_pins = "validation.judge: jev\n"
        project, hosts_root, persist = _project({"grok": grok_pins, "claude": "{}\n"})

        result = configure(project, "grok", hosts_root=hosts_root, persist=persist)

        pins = project / ".mainart/pins.yaml"
        self.assertEqual(pins.read_text(), grok_pins)
        self.assertTrue(result.pins_initialized)
        self.assertFalse(result.pins_preserved)
        gitignore = (project / ".gitignore").read_text()
        self.assertNotIn(".mainart/pins.yaml", gitignore.splitlines())

    def test_claude_and_codex_host_defaults_are_copied_when_pins_are_missing(self) -> None:
        claude_pins = "hosts:\n  claude:\n    validation.judge: jev\n"
        project, hosts_root, persist = _project(
            {"claude": claude_pins, "codex": "{}\n"}
        )

        claude = configure(project, "claude", hosts_root=hosts_root, persist=persist)
        self.assertEqual((project / ".mainart/host").read_text(), "claude\n")
        self.assertEqual((project / ".mainart/pins.yaml").read_text(), claude_pins)
        self.assertTrue(claude.pins_initialized)

        other = Path(tempfile.mkdtemp()) / "codex-project"
        other.mkdir()
        codex = configure(other, "codex", hosts_root=hosts_root, persist=persist)
        self.assertEqual((other / ".mainart/host").read_text(), "codex\n")
        self.assertEqual((other / ".mainart/pins.yaml").read_text(), "{}\n")
        self.assertTrue(codex.pins_initialized)

    def test_existing_pins_including_an_empty_file_are_preserved(self) -> None:
        project, hosts_root, persist = _project({"grok": "validation.judge: jev\n"})
        mainart = project / ".mainart"
        mainart.mkdir()
        pins = mainart / "pins.yaml"
        pins.write_text("")

        result = configure(project, "grok", hosts_root=hosts_root, persist=persist)

        self.assertEqual(pins.read_text(), "")
        self.assertFalse(result.pins_initialized)
        self.assertTrue(result.pins_preserved)

        pins.write_text("validation.judge: other\n")
        again = configure(project, "grok", hosts_root=hosts_root, persist=persist)
        self.assertEqual(pins.read_text(), "validation.judge: other\n")
        self.assertFalse(again.pins_initialized)
        self.assertTrue(again.pins_preserved)


class ModelRoleDelegationTest(unittest.TestCase):
    def test_setup_delegates_adapter_defaults_for_all_three_roles(self) -> None:
        project, hosts_root, persist = _project({"grok": "{}\n"})

        result = configure(project, "grok", hosts_root=hosts_root, persist=persist)

        self.assertEqual(
            persist.persisted,
            {"xhigh": "adapter-xhigh", "max": "adapter-max", "fast": "adapter-fast"},
        )
        self.assertEqual(result.model_roles, persist.persisted)
        self.assertEqual(tuple(result.model_roles), ("xhigh", "max", "fast"))

    def test_setup_passes_through_selected_ids_without_inventing_them(self) -> None:
        project, hosts_root, persist = _project({"grok": "{}\n"})
        chosen = {"xhigh": "host-a", "max": "host-b", "fast": "host-c"}

        result = configure(
            project,
            "grok",
            hosts_root=hosts_root,
            persist=persist,
            model_roles=chosen,
        )

        self.assertEqual(persist.persisted, chosen)
        self.assertEqual(result.model_roles, chosen)

    def test_incomplete_or_unknown_role_mapping_is_rejected(self) -> None:
        project, hosts_root, persist = _project({"grok": "{}\n"})

        with self.assertRaises(ValueError):
            configure(
                project,
                "grok",
                hosts_root=hosts_root,
                persist=persist,
                model_roles={"xhigh": "host-a", "max": "host-b"},
            )
        with self.assertRaises(ValueError):
            configure(
                project,
                "grok",
                hosts_root=hosts_root,
                persist=persist,
                model_roles={
                    "xhigh": "host-a",
                    "max": "host-b",
                    "fast": "host-c",
                    "strong": "host-d",
                },
            )
        self.assertIsNone(persist.persisted)


class GrokPersistModelRolesTest(unittest.TestCase):
    def test_grok_writes_all_three_role_models_and_keeps_other_config(self) -> None:
        config = Path(tempfile.mkdtemp()) / "config.toml"
        config.write_text('[models]\ndefault = "keep-me"\n')
        persist = GrokModelRoles(config)
        mapping = {
            "xhigh": "grok-test-xhigh",
            "max": "grok-test-max",
            "fast": "grok-test-fast",
        }

        written = persist.persist(mapping)

        text = config.read_text()
        self.assertEqual(written, mapping)
        self.assertIn('default = "keep-me"', text)
        self.assertIn("[subagents.roles.xhigh]", text)
        self.assertIn('model = "grok-test-xhigh"', text)
        self.assertIn("[subagents.roles.max]", text)
        self.assertIn('model = "grok-test-max"', text)
        self.assertIn("[subagents.roles.fast]", text)
        self.assertIn('model = "grok-test-fast"', text)

    def test_grok_persist_rejects_an_incomplete_mapping(self) -> None:
        persist = GrokModelRoles(Path(tempfile.mkdtemp()) / "config.toml")
        with self.assertRaises(ValueError):
            persist.persist({"xhigh": "only-one", "max": "two"})

    def test_grok_updates_an_existing_role_model(self) -> None:
        config = Path(tempfile.mkdtemp()) / "config.toml"
        config.write_text(
            '[subagents.roles.xhigh]\nmodel = "old-xhigh"\n\n[other]\nkeep = true\n'
        )
        persist = GrokModelRoles(config)

        persist.persist(
            {
                "xhigh": "new-xhigh",
                "max": "new-max",
                "fast": "new-fast",
            }
        )

        text = config.read_text()
        self.assertNotIn("old-xhigh", text)
        self.assertIn('model = "new-xhigh"', text)
        self.assertIn('model = "new-max"', text)
        self.assertIn("keep = true", text)

    def test_grok_defaults_are_adapter_owned_and_cover_the_three_roles(self) -> None:
        persist = GrokModelRoles(Path(tempfile.mkdtemp()) / "config.toml")
        defaults = persist.defaults()
        self.assertEqual(tuple(defaults), ("xhigh", "max", "fast"))
        self.assertEqual(defaults["xhigh"], "grok-4.7")
        self.assertEqual(defaults["max"], "grok-4.7")
        self.assertEqual(defaults["fast"], "grok-4.7")

    def test_setup_with_grok_persist_uses_adapter_defaults(self) -> None:
        project, hosts_root, _ = _project({"grok": "{}\n"})
        config = Path(tempfile.mkdtemp()) / "config.toml"
        persist = GrokModelRoles(config)

        result = configure(project, "grok", hosts_root=hosts_root, persist=persist)

        self.assertEqual(result.model_roles["xhigh"], "grok-4.7")
        self.assertEqual(result.model_roles["max"], "grok-4.7")
        self.assertEqual(result.model_roles["fast"], "grok-4.7")
        text = config.read_text()
        self.assertIn("[subagents.roles.xhigh]", text)
        self.assertIn("[subagents.roles.max]", text)
        self.assertIn("[subagents.roles.fast]", text)


class MattChecklistTest(unittest.TestCase):
    def test_setup_returns_the_human_matt_checklist_without_plugin_inspection(self) -> None:
        project, hosts_root, persist = _project({"grok": "{}\n"})

        result = configure(project, "grok", hosts_root=hosts_root, persist=persist)

        self.assertEqual(
            result.checklist,
            (
                "disable-or-uninstall-matt-plugin",
                "remove-duplicate-packet-chain-copies-for-bare-names",
                "dual-install-via-host-qualification",
            ),
        )


class CoreHasNoNativeHostDetailsTest(unittest.TestCase):
    def test_core_setup_does_not_embed_host_model_ids_or_config_paths(self) -> None:
        forbidden = (
            "grok-4",
            "claude-opus",
            "~/.grok",
            "spawn_subagent",
            "CLAUDE.md",
            "config.toml",
        )
        core_files = [ROOT / "core/host_setup.py"]
        setup_skill = ROOT / "core/skills/setup"
        if setup_skill.exists():
            core_files.extend(path for path in sorted(setup_skill.rglob("*")) if path.is_file())
        for path in core_files:
            if not path.is_file():
                continue
            text = path.read_text()
            for token in forbidden:
                self.assertNotIn(token, text, f"{path}: {token}")

    def test_setup_skill_may_auto_invoke_and_delegates_persist_model_roles(self) -> None:
        skill = (ROOT / "core/skills/setup/SKILL.md").read_text()
        frontmatter = skill.split("---", 2)[1]
        self.assertNotIn("disable-model-invocation", frontmatter)
        self.assertIn("persist-model-roles", skill)
        for host_id in HOST_IDS:
            self.assertIn(host_id, skill)
        self.assertTrue((ROOT / "core/skills/setup/SKILL.md").is_file())

    def test_later_adapters_keep_the_persist_interface_and_host_pin_defaults(self) -> None:
        for host_id in HOST_IDS:
            self.assertTrue(
                (ROOT / f"hosts/{host_id}/skills/persist-model-roles/SKILL.md").is_file()
            )
            self.assertTrue((ROOT / f"hosts/{host_id}/pins.yaml").is_file())
        gitignore = (ROOT / ".gitignore").read_text().splitlines()
        self.assertIn(".mainart/host", gitignore)
        self.assertNotIn(".mainart/pins.yaml", gitignore)


if __name__ == "__main__":
    unittest.main()




