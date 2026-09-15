"""Real package setup, Git publication and immutable launch inputs; no fleet."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_task_group as fixtures
from fm_orchflows import auto_attach, library_overlay
from fm_orchflows_home import (brief, catalog, publish, resolve, setup, workflow_home)
from fm_task_group_store import GroupError, read_json


PACKAGE = Path(__file__).resolve().parents[3] / "packages/orchflows-firstmate"


class WorkflowHomeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.project = self.fixture.project
        self.fixture.git("branch", "-M", "main")
        self.relative = "workflows/release"
        self.library = self.project / self.relative
        (self.library / "skills/release").mkdir(parents=True)
        (self.library / "plugin.json").write_text(json.dumps(
            {"name": "releases", "version": "1.0", "skills": "./skills/"}))
        (self.library / "skills/release/SKILL.md").write_text(
            "Read all release guidance, run Work, then independent Review.\n")
        (self.library / "guidance").mkdir()
        (self.library / "guidance/checks.md").write_text("Keep every issue identifier.\n")
        (self.library / "assets").mkdir()
        (self.library / "assets/example.bin").write_bytes(bytes(range(256)))
        self.fixture.git("add", ".")
        self.fixture.git("commit", "-qm", "deliver workflow")
        self.commit = self.fixture.git("rev-parse", "HEAD")
        self.environment = patch.dict(os.environ, {}, clear=False)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        for key in ("ORCHFLOWS_FIRSTMATE_HOME", "ORCHFLOWS_HOME", "ORCHFLOWS_FIRSTMATE_CONTEXT",
                    "FM_STATE_OVERRIDE", "FM_DATA_OVERRIDE", "FM_CONFIG_OVERRIDE", "FM_PROJECTS_OVERRIDE"):
            os.environ.pop(key, None)

    def publish(self, **kwargs):
        return publish(self.owner, self.project, self.relative, self.commit, PACKAGE, **kwargs)

    def selected_brief(self, task):
        directory = self.owner.task(task)
        directory.mkdir()
        (directory / "brief.md").write_text(brief(self.owner, "releases:release"))

    def test_publish_initializes_default_discovers_and_keeps_complete_library(self):
        result = self.publish()
        home = self.owner.home / "data/.orchflows-home"
        self.assertEqual(result["home"], str(home))
        self.assertFalse(self.owner.task("orchflows").exists())
        selected = resolve(self.owner, "releases:release")
        saved = Path(selected["package_root"])
        self.assertEqual((saved / "assets/example.bin").read_bytes(), bytes(range(256)))
        self.assertEqual((saved / "guidance/checks.md").read_text(), "Keep every issue identifier.\n")
        self.assertIn("releases:release", [item["identity"] for item in catalog(self.owner)["workflows"]])
        self.assertEqual(read_json(home / ".agents/plugins/marketplace.json")["name"],
                         "orchflows-firstmate-home")
        setup(self.owner)
        self.assertEqual((saved / "assets/example.bin").read_bytes(), bytes(range(256)))
        self.assertEqual(resolve(self.owner, "orchflows:orch-work")["name"], "orchflows-firstmate")

    def test_explicit_home_persists_and_environment_overrides_default(self):
        explicit = self.fixture.base / "personal-workflows"
        self.publish(explicit=explicit)
        self.assertEqual(workflow_home(self.owner), explicit)
        self.assertFalse((self.owner.home / "data/.orchflows-home").exists())
        other = self.fixture.base / "other-home"
        with patch.dict(os.environ, {"ORCHFLOWS_FIRSTMATE_HOME": str(other)}):
            self.assertEqual(workflow_home(self.owner), other)
            self.assertEqual(workflow_home(self.owner, explicit), explicit)

    def test_publish_refreshes_future_bundle_and_retains_existing_attachment(self):
        self.publish()
        self.selected_brief("selected")
        self.assertEqual(auto_attach(self.owner, "selected", "scout", "herdr", "claude", self.project), "root")
        previous = self.owner.attachment("selected")
        old_path = Path(previous["package_path"]) / "firstmate-libraries/releases/skills/release/SKILL.md"
        original = old_path.read_bytes()
        self.assertIn("Selected workflow releases:release: " + str(old_path), library_overlay(previous))
        skill = self.library / "skills/release/SKILL.md"
        skill.write_text("Updated complete workflow, still Work and Review.\n")
        self.fixture.git("add", ".")
        self.fixture.git("commit", "-qm", "deliver updated workflow")
        self.commit = self.fixture.git("rev-parse", "HEAD")
        result = self.publish()
        self.assertEqual(result["refreshed_projects"], [str(self.project)])
        self.assertEqual(self.owner.attachment("selected"), previous)
        self.assertEqual(old_path.read_bytes(), original)
        self.selected_brief("future")
        auto_attach(self.owner, "future", "scout", "herdr", "codex", self.project)
        future = self.owner.attachment("future")
        self.assertNotEqual(future["package_digest"], previous["package_digest"])
        self.assertEqual((Path(future["package_path"]) / "firstmate-libraries/releases/skills/release/SKILL.md").read_bytes(),
                         skill.read_bytes())

    def test_selection_refuses_no_mistakes_before_attachment_or_enablement(self):
        self.publish()
        self.selected_brief("restricted")
        with self.assertRaisesRegex(GroupError, "local-only"):
            auto_attach(self.owner, "restricted", "ship", "herdr", "claude", self.project, mode="no-mistakes")
        self.assertFalse(self.owner.group("restricted").exists())
        self.assertFalse((self.owner.home / "config/orchflows.json").exists())

    def test_publish_matches_existing_default_owner_origin_head_on_trunk(self):
        self.fixture.git("branch", "-m", "trunk")
        self.fixture.git("remote", "add", "origin", str(self.fixture.base / "unused-origin"))
        self.fixture.git("update-ref", "refs/remotes/origin/trunk", self.commit)
        self.fixture.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        self.assertEqual(self.publish()["commit"], self.commit)

    def test_publish_requires_committed_delivered_regular_blobs(self):
        (self.library / "skills/release/SKILL.md").write_text("Uncommitted edit\n")
        with self.assertRaisesRegex(GroupError, "dirty"):
            self.publish()
        self.fixture.git("checkout", "--", ".")
        self.fixture.git("checkout", "-qb", "fm/not-delivered")
        (self.library / "skills/release/SKILL.md").write_text("Not delivered\n")
        self.fixture.git("commit", "-qam", "undelivered workflow")
        self.commit = self.fixture.git("rev-parse", "HEAD")
        with self.assertRaises(GroupError):
            self.publish()
        self.fixture.git("checkout", "main")
        self.assertFalse((self.owner.home / "config/orchflows-home.json").exists())
        (self.library / "assets/link").symlink_to(self.project / "input.txt")
        self.fixture.git("add", ".")
        self.fixture.git("commit", "-qm", "historical symlink")
        self.commit = self.fixture.git("rev-parse", "HEAD")
        (self.library / "assets/link").unlink()
        self.fixture.git("commit", "-qam", "remove symlink")
        with self.assertRaisesRegex(GroupError, "regular committed Git blobs"):
            self.publish()
        self.assertFalse((self.owner.home / "config/orchflows-home.json").exists())

    def test_invalid_initial_library_name_does_not_create_home(self):
        manifest = self.library / "plugin.json"
        value = read_json(manifest)
        value["name"] = "Release"
        manifest.write_text(json.dumps(value))
        self.fixture.git("commit", "-qam", "invalid delivered library name")
        self.commit = self.fixture.git("rev-parse", "HEAD")
        with self.assertRaisesRegex(ValueError, "Invalid library name"):
            self.publish()
        self.assertFalse(workflow_home(self.owner).exists())
        self.assertFalse((self.owner.home / "config/orchflows-home.json").exists())
        value["name"] = "releases"
        manifest.write_text(json.dumps(value))
        self.fixture.git("commit", "-qam", "correct delivered library name")
        self.commit = self.fixture.git("rev-parse", "HEAD")
        self.assertEqual(self.publish()["library"], "releases")
        self.assertEqual(resolve(self.owner, "releases:release")["identity"], "releases:release")

    def test_invalid_names_preserve_existing_home_and_corrected_publish_succeeds(self):
        self.publish()
        home = workflow_home(self.owner)
        config = self.owner.home / "config/orchflows-home.json"

        def retained_bytes():
            return {str(path.relative_to(home)): path.read_bytes()
                    for path in home.rglob("*") if path.is_file()}

        for invalid in ("library", "skill"):
            with self.subTest(invalid=invalid):
                before, config_before = retained_bytes(), config.read_bytes()
                manifest = self.library / "plugin.json"
                if invalid == "library":
                    value = read_json(manifest)
                    value["name"] = "Release"
                    manifest.write_text(json.dumps(value))
                else:
                    (self.library / "skills/release").rename(self.library / "skills/Release")
                self.fixture.git("add", ".")
                self.fixture.git("commit", "-qm", "invalid delivered " + invalid + " name")
                self.commit = self.fixture.git("rev-parse", "HEAD")
                with self.assertRaisesRegex(ValueError, "Invalid " + invalid + " name"):
                    self.publish()
                self.assertEqual(retained_bytes(), before)
                self.assertEqual(config.read_bytes(), config_before)
                self.assertIn("releases:release",
                              [item["identity"] for item in catalog(self.owner)["workflows"]])
                self.assertFalse((home / "libraries/Release").exists())
                if invalid == "library":
                    value["name"] = "releases"
                    manifest.write_text(json.dumps(value))
                else:
                    (self.library / "skills/Release").rename(self.library / "skills/release")
                self.fixture.git("add", ".")
                self.fixture.git("commit", "-qm", "correct delivered " + invalid + " name")
                self.commit = self.fixture.git("rev-parse", "HEAD")
                self.assertEqual(self.publish()["library"], "releases")
                self.assertEqual(resolve(self.owner, "releases:release")["identity"], "releases:release")

    def test_home_overlap_and_selected_symlinks_refuse(self):
        with patch.dict(os.environ, {"ORCHFLOWS_HOME": str(self.fixture.base / "normal")}):
            with self.assertRaisesRegex(ValueError, "overlaps"):
                self.publish(explicit=self.fixture.base / "normal/nested")
        self.assertFalse((self.fixture.base / "normal").exists())
        self.publish()
        saved = Path(resolve(self.owner, "releases:release")["package_root"])
        (saved / "assets/link").symlink_to(self.project / "input.txt")
        with self.assertRaisesRegex(GroupError, "symlink"):
            resolve(self.owner, "releases:release")


if __name__ == "__main__":
    unittest.main()
