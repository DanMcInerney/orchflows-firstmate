"""Project activation uses real Git and retained package fixtures, no fleet."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import test_task_group as fixtures
from fm_orchflows import auto_attach, disable, enable, launch_context, library_overlay
from fm_task_group_launch import launch_check, launch_meta
from fm_task_group_store import GroupError, canonical, digest, package_inventory, read_json, write_json


class EnablementTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.package = self.fixture.package
        self.project = self.fixture.project
        for relative in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            path = self.package / relative
            path.parent.mkdir()
            path.write_bytes((self.package / "plugin.json").read_bytes())
        for relative in ("skills/orch-work/SKILL.md", "skills/orch-review/SKILL.md",
                         "scripts/firstmate.py", "scripts/package_identity.py"):
            path = self.package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Complete fixture " + relative + "\n")

    def attach(self, task="enabled", harness="claude"):
        return auto_attach(self.owner, task, "scout", "herdr", harness, self.project)

    def publish(self, task="enabled", generation="s1.123.4"):
        meta = {key: value for key, value in self.fixture.root_meta.items()
                if not key.startswith("task_group_")}
        meta.update(endpoint_task_id=task, spawn_gen=generation)
        meta.update(self.fixture.fields(launch_meta(self.owner, task)))
        self.fixture.save_meta(task, meta)
        return meta

    def library(self, name="custom-a"):
        root = self.fixture.base / name
        (root / "skills" / "inspect").mkdir(parents=True)
        (root / "plugin.json").write_text(json.dumps(
            {"name": name, "version": "1.0", "skills": "./skills/"}))
        (root / "skills/inspect/SKILL.md").write_text("Use one Work to inspect the input.\n")
        (root / "assets").mkdir()
        (root / "assets/input.bin").write_bytes(bytes(range(256)))
        return root

    def test_enable_normal_spawn_uses_exact_snapshot_without_dispatch(self):
        entry = enable(self.owner, self.package, self.project)
        self.assertEqual(read_json(self.owner.home / "config/orchflows.json"),
                         {"schema": 1, "projects": {str(self.project): entry}})
        self.assertEqual(self.attach(harness="codex"), "root")
        attachment = self.owner.attachment("enabled")
        self.assertEqual(attachment["package_digest"], entry["package_digest"])
        self.assertNotEqual(attachment["package_path"], entry["package_path"])
        self.assertEqual(Path(entry["package_path"]).stat().st_mode & 0o777, 0o555)
        launch_check(self.owner, "enabled", "scout", "herdr", "codex", self.project)
        self.assertEqual(self.fixture.calls, [])
        self.assertEqual(enable(self.owner, self.package, self.project), entry)
        self.assertFalse(list((self.owner.home / "data/.orchflows").glob(".enable-*")))

    def test_source_changes_reenable_and_disable_keep_old_task_identity(self):
        original = enable(self.owner, self.package, self.project)
        (self.package / "guidance.md").write_text("Changed future default\n")
        self.attach()
        retained = self.owner.attachment("enabled")
        self.assertEqual(retained["package_digest"], original["package_digest"])
        self.publish()
        updated = enable(self.owner, self.package, self.project, "Review", "explicit-audit")
        self.assertNotEqual(updated["package_digest"], original["package_digest"])
        self.assertEqual(self.attach(), "root")
        self.assertEqual(self.owner.attachment("enabled"), retained)
        self.assertEqual(self.attach("new-audit"), "root")
        self.assertEqual(self.owner.attachment("new-audit")["primitive"], "Review")
        self.assertTrue(disable(self.owner, self.project))
        self.assertFalse(disable(self.owner, self.project))
        self.assertEqual(self.attach(), "root")
        self.assertIsNone(self.attach("after-disable"))
        self.assertEqual(self.owner.attachment("enabled"), retained)
        self.assertTrue(Path(original["package_path"]).is_dir())
        self.publish(generation="s3.456.7")
        self.assertEqual(self.attach(), "root")
        launch_check(self.owner, "enabled", "scout", "herdr", "claude", self.project)

    def test_ordinary_existing_tasks_and_unmatched_projects_stay_ordinary(self):
        enable(self.owner, self.package, self.project)
        self.fixture.save_meta("ordinary", {"kind": "scout", "endpoint_task_id": "ordinary"})
        self.assertIsNone(self.attach("ordinary"))
        self.assertFalse(self.owner.group("ordinary").exists())
        self.assertIsNone(auto_attach(self.owner, "ship", "ship", "herdr", "claude", self.project))
        elsewhere = self.fixture.base / "elsewhere"
        elsewhere.mkdir()
        self.assertIsNone(auto_attach(self.owner, "unmatched", "scout", "tmux", "other", elsewhere))
        self.assertFalse(self.owner.task("ship").exists())
        self.assertFalse(self.owner.task("unmatched").exists())

    def test_manual_attachment_remains_compatible(self):
        enable(self.owner, self.package, self.project, "Review", "explicit-audit")
        before = self.owner.attachment("root")
        self.assertEqual(self.attach("root"), "root")
        self.assertEqual(self.owner.attachment("root"), before)
        self.assertEqual(before["primitive"], "Work")
        self.assertEqual(library_overlay(before), "")

    def test_unsupported_enabled_profiles_refuse_before_task_mutation(self):
        enable(self.owner, self.package, self.project)
        for backend, harness in (("tmux", "claude"), ("herdr", "other")):
            with self.subTest(backend=backend, harness=harness), self.assertRaises(GroupError):
                auto_attach(self.owner, "denied", "scout", backend, harness, self.project)
            self.assertFalse(self.owner.task("denied").exists())
        with patch("fm_orchflows.sys.platform", "darwin"), self.assertRaisesRegex(GroupError, "Linux"):
            self.attach("denied")
        with patch.dict(os.environ, {"FM_STATE_OVERRIDE": "/tmp/elsewhere"}):
            with self.assertRaisesRegex(GroupError, "custom"):
                self.attach("denied")
        self.assertFalse(self.owner.task("denied").exists())

    def test_enable_rejects_unsupported_policy_dirty_and_platform_before_publication(self):
        for primitive, policy in (("Dynamic", "none"), ("Review", "none")):
            with self.subTest(primitive=primitive), self.assertRaises(GroupError):
                enable(self.owner, self.package, self.project, primitive, policy)
        with patch("fm_orchflows.sys.platform", "darwin"), self.assertRaisesRegex(GroupError, "Linux"):
            enable(self.owner, self.package, self.project)
        (self.project / "input.txt").write_text("Dirty\n")
        with self.assertRaisesRegex(GroupError, "dirty"):
            enable(self.owner, self.package, self.project)
        self.fixture.git("checkout", "--", "input.txt")
        self.assertFalse((self.owner.home / "config").exists())
        self.assertFalse((self.owner.home / "data/.orchflows").exists())
        self.fixture.git("remote", "add", "origin", "https://example.invalid/project")
        entry = enable(self.owner, self.package, self.project)
        self.assertTrue(Path(entry["package_path"]).is_dir())

    def test_incomplete_or_inconsistent_package_is_refused(self):
        path = self.package / ".codex-plugin/plugin.json"
        path.write_text(json.dumps({"name": "orchflows-firstmate", "version": "different"}))
        with self.assertRaisesRegex(GroupError, "disagree"):
            enable(self.owner, self.package, self.project)
        path.write_bytes((self.package / "plugin.json").read_bytes())
        required = self.package / "skills/orch-review/SKILL.md"
        required.unlink()
        with self.assertRaisesRegex(GroupError, "missing path"):
            enable(self.owner, self.package, self.project)
        self.assertFalse((self.owner.home / "config").exists())

    def test_enabled_snapshot_tamper_refuses_new_attachment(self):
        entry = enable(self.owner, self.package, self.project)
        path = Path(entry["package_path"]) / "guidance.md"
        path.chmod(0o644)
        path.write_text("Tamper\n")
        with self.assertRaisesRegex(GroupError, "snapshot changed"):
            self.attach("denied")
        with self.assertRaisesRegex(GroupError, "snapshot changed"):
            enable(self.owner, self.package, self.project)
        self.assertFalse(self.owner.task("denied").exists())
        self.assertFalse(list((self.owner.home / "data/.orchflows").glob(".enable-*")))

    def test_libraries_preserve_order_bytes_and_real_paths_after_source_removal(self):
        first, second = self.library("z-custom"), self.library("a-custom")
        before = {str(path.relative_to(first)): path.read_bytes()
                  for path in first.rglob("*") if path.is_file()}
        enable(self.owner, self.package, self.project, libraries=(first, second))
        self.attach()
        attached = self.owner.attachment("enabled")
        retained = Path(attached["package_path"]) / "firstmate-libraries/z-custom"
        self.assertEqual({str(path.relative_to(retained)): path.read_bytes()
                          for path in retained.rglob("*") if path.is_file()}, before)
        (first / "skills/inspect/SKILL.md").unlink()
        (second / "plugin.json").unlink()
        overlay = library_overlay(attached)
        self.assertLess(overlay.index("- z-custom:"), overlay.index("- a-custom:"))
        self.assertIn(str(retained / "skills/inspect/SKILL.md"), overlay)
        self.assertIn("\n- z-custom:", overlay)
        self.assertIn("z-custom:inspect:", overlay)
        self.assertNotIn("\\n", overlay)
        self.assertIn("Core logical aliases orchflows and orchflows-firstmate resolve to " +
                      attached["package_path"], overlay)
        self.assertIn("Additional components, writers, Dynamic, Build and SelfImprove remain gated", overlay)
        self.assertEqual(digest(canonical(package_inventory(Path(attached["package_path"])))),
                         attached["package_digest"])

    def test_duplicate_reserved_inactive_and_symlink_libraries_refuse(self):
        library = self.library()
        for selected in ((library, library), (self.library("design-loop"),),
                         (self.library("orchflows"),)):
            with self.subTest(selected=selected), self.assertRaises(GroupError):
                enable(self.owner, self.package, self.project, libraries=selected)
        (library / "assets/link").symlink_to(self.project / "input.txt")
        with self.assertRaisesRegex(GroupError, "symlink"):
            enable(self.owner, self.package, self.project, libraries=(library,))
        self.assertFalse((self.owner.home / "config").exists())

    def test_reserved_source_catalog_and_invalid_library_catalog_are_refused(self):
        (self.package / "firstmate-libraries.json").write_text("{}")
        with self.assertRaisesRegex(GroupError, "reserved"):
            enable(self.owner, self.package, self.project)
        (self.package / "firstmate-libraries.json").unlink()
        enable(self.owner, self.package, self.project, libraries=(self.library(),))
        self.attach()
        attachment = self.owner.attachment("enabled")
        marker = Path(attachment["package_path"]) / "firstmate-libraries.json"
        marker.chmod(0o644)
        catalog = read_json(marker)
        catalog["libraries"][0]["skills"] = ["../external/SKILL.md"]
        marker.write_text(json.dumps(catalog))
        with self.assertRaisesRegex(GroupError, "skill path"):
            library_overlay(attachment)

    def test_context_is_exact_generation_immutable_and_requires_published_metadata(self):
        enable(self.owner, self.package, self.project)
        self.attach()
        with self.assertRaises(GroupError):
            launch_context(self.owner, "enabled", "s1.123.4")
        self.publish()
        first = Path(launch_context(self.owner, "enabled", "s1.123.4"))
        before = first.read_bytes()
        self.assertEqual(launch_context(self.owner, "enabled", "s1.123.4"), str(first))
        self.assertEqual(read_json(first), {
            "schema": 1, "firstmate_root": str(self.owner.code_root), "home": str(self.owner.home),
            "root": "enabled", "generation": "s1.123.4", "primitive": "Work",
            "package_path": self.owner.attachment("enabled")["package_path"]})
        self.assertEqual(first.stat().st_mode & 0o777, 0o444)
        self.publish(generation="s3.456.7")
        with self.assertRaisesRegex(GroupError, "stale"):
            launch_context(self.owner, "enabled", "s1.123.4")
        second = Path(launch_context(self.owner, "enabled", "s3.456.7"))
        self.assertNotEqual(second, first)
        self.assertEqual(first.read_bytes(), before)
        self.assertEqual(read_json(second)["generation"], "s3.456.7")

    def test_context_corruption_and_symlink_refuse_in_place(self):
        enable(self.owner, self.package, self.project)
        self.attach()
        self.publish()
        path = Path(launch_context(self.owner, "enabled", "s1.123.4"))
        path.chmod(0o644)
        for corrupted in ({**read_json(path), "generation": "other"}, {"schema": True}):
            path.write_text(json.dumps(corrupted))
            before = path.read_bytes()
            with self.assertRaisesRegex(GroupError, "context changed"):
                launch_context(self.owner, "enabled", "s1.123.4")
            self.assertEqual(path.read_bytes(), before)
        path.unlink()
        path.symlink_to(self.project / "input.txt")
        with self.assertRaisesRegex(GroupError, "symlink"):
            launch_context(self.owner, "enabled", "s1.123.4")

    def test_ordinary_and_component_tasks_receive_no_root_context(self):
        self.assertEqual(launch_context(self.owner, "ordinary", "irrelevant"), "")
        child = self.fixture.submit()["request"]["child"]
        self.assertEqual(launch_context(self.owner, child, "s2.345.6"), "")

    def test_malformed_configuration_cannot_attach_or_overwrite_defaults(self):
        entry = enable(self.owner, self.package, self.project)
        config = self.owner.home / "config/orchflows.json"
        write_json(config, {"schema": 1, "projects": {str(self.project): {
            **entry, "package_path": str(self.package)}}})
        before = config.read_bytes()
        with self.assertRaisesRegex(GroupError, "immutable identity"):
            self.attach("denied")
        with self.assertRaisesRegex(GroupError, "immutable identity"):
            enable(self.owner, self.package, self.project)
        self.assertEqual(config.read_bytes(), before)
        self.assertFalse(self.owner.task("denied").exists())

    def test_failed_snapshot_cleans_scoped_staging_without_config_publication(self):
        def failed_snapshot(source, target):
            target.mkdir()
            (target / "partial").write_bytes(b"partial")
            target.chmod(0o555)
            raise GroupError("injected snapshot failure")
        with patch("fm_orchflows.snapshot_package", side_effect=failed_snapshot):
            with self.assertRaisesRegex(GroupError, "snapshot failure"):
                enable(self.owner, self.package, self.project)
        self.assertFalse((self.owner.home / "config/orchflows.json").exists())
        self.assertFalse(list((self.owner.home / "data/.orchflows").glob(".enable-*")))
        self.assertFalse(list((self.owner.home / "data/.orchflows").glob("package-*")))

    def test_selected_metadata_requires_matching_capability_before_enable_or_attach(self):
        capability_path = self.package / "scripts/firstmate-client.json"
        dynamic_skill = self.package / "skills/orch-dynamic-workflow/SKILL.md"
        dynamic_skill.parent.mkdir(parents=True)
        dynamic_skill.write_text("Work, join/check, Review, repair/check.\\n")
        legacy = {"schema": 1, "launch_context_schema": 1, "workflows": ["dynamic"]}
        cases = [
            ("composition", {"calls": [{"id": "phase", "caller": "root"}]},
             {}, "scoped-composition-v1"),
            ("composition", {"calls": [{"id": "phase", "caller": "root"}]},
             {"assignment_controls": ["model-effort-v1"]}, "scoped-composition-v1"),
            ("workflow_preferences", {"operations": {"Work": {"effort": "high"}}},
             {}, "model-effort-v1"),
            ("workflow_preferences", {},
             {"composition": ["scoped-composition-v1"]}, "model-effort-v1"),
        ]
        marker = self.package / "firstmate-libraries.json"
        for field, value, advertised, expected in cases:
            with self.subTest(field=field, advertised=advertised):
                write_json(capability_path, {**legacy, **advertised})
                selection = {"identity": "orchflows:orch-dynamic-workflow", field: value}
                with self.assertRaisesRegex(GroupError, expected):
                    enable(self.owner, self.package, self.project, workflow="dynamic",
                           selection=selection, library_home=self.fixture.base)
                self.assertFalse((self.owner.home / "config/orchflows.json").exists())
                self.assertFalse((self.owner.home / "data/.orchflows").exists())
                write_json(marker, {"schema": 1, "libraries": [], "selected_workflow": selection})
                with self.assertRaisesRegex(GroupError, expected):
                    self.owner.attach("denied-capability", self.package, self.project,
                                      review_policy="workflow-review", workflow="dynamic")
                self.assertFalse(self.owner.group("denied-capability").exists())
                marker.unlink()
        write_json(capability_path, legacy)
        entry = enable(self.owner, self.package, self.project, workflow="dynamic")
        self.assertEqual(entry["workflow"], "dynamic")
        self.assertEqual(auto_attach(self.owner, "legacy-dynamic", "scout", "herdr",
                                     "claude", self.project), "root")

    def test_enabled_store_does_not_occupy_an_ordinary_task_id(self):
        enable(self.owner, self.package, self.project)
        self.assertFalse(self.owner.task("orchflows").exists())
        self.assertTrue((self.owner.home / "data/.orchflows").is_dir())


if __name__ == "__main__":
    unittest.main()
