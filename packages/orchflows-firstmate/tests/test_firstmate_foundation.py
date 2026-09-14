"""Package isolation and readiness boundaries, without user-host writes or agents."""

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from test_home_setup import SCRIPT, orchflows, package, snapshot, write


class FirstMateFoundationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="orchflows-firstmate-boundary-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.home = self.root / "fork-home"
        self.normal = self.root / "normal-home"
        self.user = self.root / "user"
        self.source = self.root / "source"
        package(self.source, "orchflows-firstmate")
        write(self.source / "guidance/code.md", "Fixture guidance\n")
        write(self.source / "docs/architecture.md", "Fixture architecture\n")
        (self.source / "scripts").mkdir()
        for script in SCRIPT.parent.glob("*.py"):
            shutil.copy2(script, self.source / "scripts" / script.name)
        environment = patch.dict(os.environ, {
            "ORCHFLOWS_HOME": str(self.normal),
            "ORCHFLOWS_FIRSTMATE_HOME": str(self.home),
            "CODEX_HOME": str(self.root / "codex"),
            "CLAUDE_CONFIG_DIR": str(self.root / "claude"),
        })
        environment.start()
        self.addCleanup(environment.stop)

    def test_home_selection_uses_only_fork_environment_and_explicit_path(self):
        with patch.object(Path, "home", return_value=self.user):
            self.assertEqual(orchflows.home_path(), self.home)
            self.assertEqual(orchflows.home_path(self.root / "explicit"), self.root / "explicit")
            os.environ.pop("ORCHFLOWS_FIRSTMATE_HOME")
            self.assertEqual(orchflows.home_path(), self.user / ".orchflows-firstmate")
        self.assertFalse(self.normal.exists())

    def test_default_setup_does_not_read_or_write_host_settings_or_normal_home(self):
        write(self.normal / "libraries/personal/keep.txt", "Normal library")
        write(self.normal / ".agents/plugins/marketplace.json", '{"name":"orchflows-home"}')
        write(self.root / "codex/config.toml", "malformed = [\n")
        write(self.root / "claude/settings.json", "{malformed")
        before = {path: snapshot(self.root / path) for path in ("normal-home", "codex", "claude")}
        with patch.object(orchflows.host_config, "prepare_host_configs", side_effect=AssertionError("Read host settings")):
            result = orchflows.setup(self.home, self.source)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["host_config_status"], "skipped")
        self.assertEqual(result["host_configs"], {})
        self.assertEqual({path: snapshot(self.root / path) for path in before}, before)

    def test_explicit_normal_home_and_overlapping_destinations_are_rejected_without_writes(self):
        write(self.normal / "keep.txt", "Preserved")
        with patch.object(Path, "home", return_value=self.user):
            for home in (self.normal, self.normal / "nested", self.root, self.user / ".orchflows"):
                with self.subTest(home=home):
                    before = snapshot(self.root)
                    with self.assertRaisesRegex(ValueError, "overlaps the normal Orchflows home"):
                        orchflows.setup(home, self.source)
                    self.assertEqual(snapshot(self.root), before)

    def test_recognized_normal_catalogs_and_core_are_protected_at_other_paths(self):
        cases = (
            (".agents/plugins/marketplace.json", '{"name":"orchflows-home"}'),
            (".claude-plugin/marketplace.json", '{"name":"orchflows-local"}'),
            (".local/packages/orchflows/plugin.json", '{"name":"orchflows","version":"0.7.0"}'),
        )
        for number, (relative, contents) in enumerate(cases):
            with self.subTest(relative=relative):
                home = self.root / f"foreign-{number}"
                write(home / relative, contents)
                before = snapshot(home)
                with self.assertRaisesRegex(ValueError, "Normal Orchflows"):
                    orchflows.setup(home, self.source)
                self.assertEqual(snapshot(home), before)

    def test_core_alias_is_strictly_this_fork_and_never_falls_back(self):
        package(self.normal / ".local/packages/orchflows", "orchflows")
        result = orchflows.setup(self.home, self.source)
        canonical = orchflows.resolve(self.home, "orchflows-firstmate", skill="sample")
        self.assertEqual(orchflows.resolve(self.home, "orchflows", skill="sample"), canonical)
        self.assertEqual(canonical["name"], "orchflows-firstmate")
        self.assertEqual(canonical["package_root"], result["core"]["package_root"])
        for relative in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
            catalog = json.loads((self.home / relative).read_text())
            self.assertEqual(catalog["name"], "orchflows-firstmate-home")
            self.assertEqual([plugin["name"] for plugin in catalog["plugins"]], ["orchflows-firstmate"])
        Path(result["core"]["package_root"]).rename(self.home / ".local/packages/retained-core")
        for home in (self.home, self.normal):
            with self.subTest(home=home), self.assertRaisesRegex(ValueError, "No package manifest"):
                orchflows.resolve(home, "orchflows")

    def test_both_core_names_are_reserved_against_all_library_collisions(self):
        for number, reserved in enumerate(("orchflows", "orchflows-firstmate")):
            with self.subTest(reserved=reserved):
                home = self.root / f"collision-{number}"
                package(home / "libraries/shadow", reserved)
                before = snapshot(home / "libraries")
                result = orchflows.setup(home, self.source)
                self.assertEqual(result["status"], "partial")
                self.assertEqual(snapshot(home / "libraries"), before)
                self.assertIn(f"Ambiguous library name: {reserved}", " ".join(orchflows.doctor(home)["issues"]))
                for alias in ("orchflows", "orchflows-firstmate"):
                    with self.assertRaisesRegex(ValueError, "reserved"):
                        orchflows.resolve(home, alias)
                catalog = json.loads((home / ".agents/plugins/marketplace.json").read_text())
                self.assertEqual([entry["name"] for entry in catalog["plugins"]], ["orchflows-firstmate"])

    def test_reserved_example_names_and_normal_core_source_are_rejected_before_writes(self):
        for alias in ("orchflows", "orchflows-firstmate"):
            with self.subTest(alias=alias), self.assertRaisesRegex(ValueError, "reserved"):
                orchflows.setup(self.home, self.source, example=alias)
            self.assertFalse(self.home.exists())
        write(self.source / "plugin.json", '{"name":"orchflows","version":"0.7.0"}')
        with self.assertRaisesRegex(ValueError, "Core source must identify as orchflows-firstmate"):
            orchflows.setup(self.home, self.source)
        self.assertFalse(self.home.exists())

    def test_setup_and_doctor_never_claim_executable_integration(self):
        reports = [orchflows.doctor(self.home), orchflows.setup(self.home, self.source), orchflows.doctor(self.home)]
        self.assertEqual([report["status"] for report in reports], ["incomplete", "ready", "ready"])
        for report in reports:
            self.assertEqual(report["readiness_scope"], "package-only")
            self.assertEqual(report["integration"]["status"], "experimental-client")
            self.assertIs(report["integration"]["execution_ready"], False)
            self.assertEqual(report["integration"]["required_contract"], "firstmate-task-group")
            self.assertEqual(report["integration"]["implemented_scope"], "local-readonly-work")
        self.assertFalse((self.root / "codex").exists())
        self.assertFalse((self.root / "claude").exists())


if __name__ == "__main__":
    unittest.main()
