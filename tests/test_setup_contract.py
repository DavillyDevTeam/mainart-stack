"""Observable seam: core setup / persist-model-roles / project pins.

Pre-agreed by issue 24 and the adapter contract checks in docs/spec.md.
Tests speak in host files, pin files, shim directories, and Grok config.
They do not assert prompt wording, private reasoning, or deferred frontmatter keys.
"""

from __future__ import annotations

import inspect
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.host_setup import (
    HOST_IDS,
    MissingPersistShim,
    UnknownHost,
    configure,
)
from hosts.grok.persist_model_roles import GrokModelRoles


def _project(hosts: dict[str, str] | None = None) -> tuple[Path, Path]:
    tmp = Path(tempfile.mkdtemp())
    project = tmp / "project"
    hosts_root = tmp / "hosts"
    project.mkdir()
    for host_id, pins in (hosts or {}).items():
        host_dir = hosts_root / host_id
        skill = host_dir / "skills" / "persist-model-roles"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# persist-model-roles\n")
        (host_dir / "pins.yaml").write_text(pins)
    return project, hosts_root


class HostSelectionTest(unittest.TestCase):
    def test_setup_persists_local_host_as_gitignored_state(self) -> None:
        project, hosts_root = _project({"grok": "{}\n"})

        result = configure(project, "grok", hosts_root=hosts_root)

        self.assertEqual((project / ".mainart/host").read_text(), "grok\n")
        self.assertEqual(result.host_id, "grok")
        gitignore = (project / ".gitignore").read_text().splitlines()
        self.assertIn(".mainart/host", gitignore)
        self.assertNotIn(".mainart/pins.yaml", gitignore)
        self.assertNotIn(".mainart/", gitignore)

    def test_unknown_host_is_rejected(self) -> None:
        project, hosts_root = _project()

        with self.assertRaises(UnknownHost):
            configure(project, "cursor", hosts_root=hosts_root)

        self.assertFalse((project / ".mainart/host").exists())

    def test_missing_persist_shim_is_rejected(self) -> None:
        project, hosts_root = _project()
        host_dir = hosts_root / "grok"
        host_dir.mkdir(parents=True)
        (host_dir / "pins.yaml").write_text("{}\n")

        with self.assertRaises(MissingPersistShim):
            configure(project, "grok", hosts_root=hosts_root)


class ProjectPinsTest(unittest.TestCase):
    def test_missing_pins_initialize_from_the_selected_host_defaults(self) -> None:
        grok_pins = "validation.judge: jev\n"
        project, hosts_root = _project({"grok": grok_pins, "claude": "{}\n"})

        result = configure(project, "grok", hosts_root=hosts_root)

        pins = project / ".mainart/pins.yaml"
        self.assertEqual(pins.read_text(), grok_pins)
        self.assertTrue(result.pins_initialized)
        self.assertFalse(result.pins_preserved)
        gitignore = (project / ".gitignore").read_text()
        self.assertNotIn(".mainart/pins.yaml", gitignore.splitlines())

    def test_claude_and_codex_host_defaults_are_copied_when_pins_are_missing(self) -> None:
        claude_pins = "hosts:\n  claude:\n    validation.judge: jev\n"
        project, hosts_root = _project(
            {"claude": claude_pins, "codex": "{}\n"}
        )

        claude = configure(project, "claude", hosts_root=hosts_root)
        self.assertEqual((project / ".mainart/host").read_text(), "claude\n")
        self.assertEqual((project / ".mainart/pins.yaml").read_text(), claude_pins)
        self.assertTrue(claude.pins_initialized)

        other = Path(tempfile.mkdtemp()) / "codex-project"
        other.mkdir()
        codex = configure(other, "codex", hosts_root=hosts_root)
        self.assertEqual((other / ".mainart/host").read_text(), "codex\n")
        self.assertEqual((other / ".mainart/pins.yaml").read_text(), "{}\n")
        self.assertTrue(codex.pins_initialized)

    def test_existing_pins_including_an_empty_file_are_preserved(self) -> None:
        project, hosts_root = _project({"grok": "validation.judge: jev\n"})
        mainart = project / ".mainart"
        mainart.mkdir()
        pins = mainart / "pins.yaml"
        pins.write_text("")

        result = configure(project, "grok", hosts_root=hosts_root)

        self.assertEqual(pins.read_text(), "")
        self.assertFalse(result.pins_initialized)
        self.assertTrue(result.pins_preserved)

        pins.write_text("validation.judge: other\n")
        again = configure(project, "grok", hosts_root=hosts_root)
        self.assertEqual(pins.read_text(), "validation.judge: other\n")
        self.assertFalse(again.pins_initialized)
        self.assertTrue(again.pins_preserved)


class ModelRoleDelegationTest(unittest.TestCase):
    def test_setup_skill_tools_the_selected_host_persist_shim(self) -> None:
        project, hosts_root = _project({"grok": "{}\n"})

        result = configure(project, "grok", hosts_root=hosts_root)

        self.assertEqual(
            result.persist_skill,
            hosts_root / "grok" / "skills" / "persist-model-roles",
        )
        self.assertTrue((result.persist_skill / "SKILL.md").is_file())

    def test_configure_does_not_accept_an_in_process_persist_double(self) -> None:
        parameters = inspect.signature(configure).parameters
        self.assertNotIn("persist", parameters)
        self.assertNotIn("model_roles", parameters)
        source = (ROOT / "core/host_setup.py").read_text()
        self.assertNotIn("ModelRolePersistence", source)
        self.assertNotIn("Protocol", source)


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
        parsed = tomllib.loads(text)
        self.assertEqual(parsed["models"]["default"], "keep-me")
        self.assertEqual(parsed["subagents"]["roles"]["xhigh"]["model"], "grok-test-xhigh")
        self.assertEqual(parsed["subagents"]["roles"]["max"]["model"], "grok-test-max")
        self.assertEqual(parsed["subagents"]["roles"]["fast"]["model"], "grok-test-fast")

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
        parsed = tomllib.loads(text)
        self.assertEqual(parsed["subagents"]["roles"]["xhigh"]["model"], "new-xhigh")
        self.assertEqual(parsed["other"]["keep"], True)

    def test_grok_updates_commented_headers_without_duplicating_tables(self) -> None:
        config = Path(tempfile.mkdtemp()) / "config.toml"
        config.write_text(
            '[subagents.roles.xhigh] # preferred\nmodel = "old"\n'
        )
        persist = GrokModelRoles(config)

        persist.persist(
            {
                "xhigh": "new",
                "max": "new-max",
                "fast": "new-fast",
            }
        )

        text = config.read_text()
        self.assertEqual(text.count("[subagents.roles.xhigh]"), 1)
        self.assertIn("# preferred", text)
        parsed = tomllib.loads(text)
        self.assertEqual(parsed["subagents"]["roles"]["xhigh"]["model"], "new")

    def test_grok_preserves_unrelated_model_prefix_keys(self) -> None:
        config = Path(tempfile.mkdtemp()) / "config.toml"
        config.write_text(
            '[subagents.roles.xhigh]\nmodel_path = "/weights"\nmodel = "old"\n'
        )
        persist = GrokModelRoles(config)

        persist.persist(
            {
                "xhigh": "new",
                "max": "new-max",
                "fast": "new-fast",
            }
        )

        parsed = tomllib.loads(config.read_text())
        self.assertEqual(parsed["subagents"]["roles"]["xhigh"]["model_path"], "/weights")
        self.assertEqual(parsed["subagents"]["roles"]["xhigh"]["model"], "new")

    def test_grok_updates_indented_tables(self) -> None:
        config = Path(tempfile.mkdtemp()) / "config.toml"
        config.write_text(
            '  [subagents.roles.xhigh]\n  model = "old"\n'
        )
        persist = GrokModelRoles(config)

        persist.persist(
            {
                "xhigh": "new",
                "max": "new-max",
                "fast": "new-fast",
            }
        )

        parsed = tomllib.loads(config.read_text())
        self.assertEqual(parsed["subagents"]["roles"]["xhigh"]["model"], "new")
        self.assertEqual(config.read_text().count("[subagents.roles.xhigh]"), 1)

    def test_grok_updates_quoted_and_spaced_headers_without_duplicating(self) -> None:
        mapping = {
            "xhigh": "new-xhigh",
            "max": "new-max",
            "fast": "new-fast",
        }
        for existing in (
            '[subagents.roles."xhigh"]\nmodel = "old"\n',
            '[ subagents.roles.xhigh ]\nmodel = "old"\n',
        ):
            config = Path(tempfile.mkdtemp()) / "config.toml"
            config.write_text(existing)
            GrokModelRoles(config).persist(mapping)
            parsed = tomllib.loads(config.read_text())
            self.assertEqual(parsed["subagents"]["roles"]["xhigh"]["model"], "new-xhigh")
            self.assertEqual(parsed["subagents"]["roles"]["max"]["model"], "new-max")
            self.assertEqual(
                config.read_text().count("subagents.roles"), 3
            )

    def test_grok_inserts_a_newline_after_a_header_at_eof(self) -> None:
        config = Path(tempfile.mkdtemp()) / "config.toml"
        config.write_text("[subagents.roles.xhigh]")
        GrokModelRoles(config).persist(
            {
                "xhigh": "new-xhigh",
                "max": "new-max",
                "fast": "new-fast",
            }
        )
        parsed = tomllib.loads(config.read_text())
        self.assertEqual(parsed["subagents"]["roles"]["xhigh"]["model"], "new-xhigh")

    def test_grok_does_not_treat_model_lines_inside_multiline_strings_as_keys(self) -> None:
        config = Path(tempfile.mkdtemp()) / "config.toml"
        config.write_text(
            '[subagents.roles.xhigh]\n'
            'description = """\n'
            'model = "example"\n'
            '"""\n'
            'model = "old-xhigh"\n'
        )
        GrokModelRoles(config).persist(
            {
                "xhigh": "new-xhigh",
                "max": "new-max",
                "fast": "new-fast",
            }
        )
        text = config.read_text()
        parsed = tomllib.loads(text)
        self.assertIn('model = "example"', parsed["subagents"]["roles"]["xhigh"]["description"])
        self.assertEqual(parsed["subagents"]["roles"]["xhigh"]["model"], "new-xhigh")

    def test_grok_default_config_path_is_the_host_user_config(self) -> None:
        persist = GrokModelRoles()
        self.assertEqual(persist.config_path, Path.home() / ".grok" / "config.toml")

    def test_grok_defaults_are_adapter_owned_and_cover_the_three_roles(self) -> None:
        persist = GrokModelRoles(Path(tempfile.mkdtemp()) / "config.toml")
        defaults = persist.defaults()
        self.assertEqual(tuple(defaults), ("xhigh", "max", "fast"))
        self.assertEqual(defaults["xhigh"], "grok-4.7")
        self.assertEqual(defaults["max"], "grok-4.7")
        self.assertEqual(defaults["fast"], "grok-4.7")

    def test_adapter_persist_does_not_import_core_role_names(self) -> None:
        source = (ROOT / "hosts/grok/persist_model_roles.py").read_text()
        self.assertNotIn("from core.host_setup import", source)
        self.assertNotIn("core.host_setup", source)


class MattChecklistTest(unittest.TestCase):
    def test_setup_returns_the_human_matt_checklist_without_plugin_inspection(self) -> None:
        project, hosts_root = _project({"grok": "{}\n"})

        result = configure(project, "grok", hosts_root=hosts_root)

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
            "/mainart-stack:tdd",
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

    def test_setup_skill_delegates_persist_model_roles_without_freezing_frontmatter(self) -> None:
        skill = (ROOT / "core/skills/setup/SKILL.md").read_text()
        self.assertIn("Skill-tool `persist-model-roles`", skill)
        self.assertIn("qualification syntax", skill)
        for host_id in HOST_IDS:
            self.assertIn(host_id, skill)

    def test_later_adapters_keep_the_persist_shim_and_host_pin_defaults(self) -> None:
        for host_id in HOST_IDS:
            self.assertTrue(
                (ROOT / f"hosts/{host_id}/skills/persist-model-roles/SKILL.md").is_file()
            )
            self.assertTrue((ROOT / f"hosts/{host_id}/pins.yaml").is_file())
        gitignore = (ROOT / ".gitignore").read_text().splitlines()
        self.assertIn(".mainart/host", gitignore)
        self.assertNotIn(".mainart/pins.yaml", gitignore)

    def test_grok_marks_persist_model_roles_as_a_non_slash_shim(self) -> None:
        invocation = json.loads((ROOT / "hosts/grok/invocation.json").read_text())
        shims = invocation["shims"]
        self.assertFalse(shims["user-invocable"])
        self.assertFalse(shims["implicit_invocation"])
        self.assertIn("persist-model-roles", shims["skills"])
        for host_id in HOST_IDS:
            text = (ROOT / f"hosts/{host_id}/skills/persist-model-roles/SKILL.md").read_text()
            self.assertIn("not a slash front door", text)


if __name__ == "__main__":
    unittest.main()
