"""Observable setup and doctor behavior on disposable homes: only the home changes, and only what it owns."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/orchflows.py"
SPEC = importlib.util.spec_from_file_location("orchflows", SCRIPT)
orchflows = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(orchflows)


def write(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def library(root: Path, name: str, version: str = "0.1.0") -> None:
    write(root / "plugin.json", json.dumps({"name": name, "version": version}))
    write(root / "skills/sample/SKILL.md", "---\nname: sample\ndescription: Test fixture.\ndisable-model-invocation: true\n---\nRun the fixture.\n")


def snapshot(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file() and ".git" not in path.parts}


class HomeSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="orchflows-firstmate-home-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.environment_patch = patch.dict(os.environ, {"CODEX_HOME": str(self.root / "codex"),
                                                         "CLAUDE_CONFIG_DIR": str(self.root / "claude"),
                                                         "ORCHFLOWS_FIRSTMATE_HOME": str(self.root / "env-home")})
        self.environment_patch.start()
        self.addCleanup(self.environment_patch.stop)
        self.home = self.root / "home"

    def cli(self, *arguments: str) -> subprocess.CompletedProcess:
        unrelated = self.root / "unrelated-project"
        unrelated.mkdir(exist_ok=True)
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *arguments], cwd=unrelated,
                              text=True, capture_output=True, timeout=45, check=False)

    def catalogs(self) -> dict[str, list[str]]:
        result = {}
        for relative in orchflows.CATALOGS:
            catalog = json.loads((self.home / relative).read_text(encoding="utf-8"))
            self.assertEqual(catalog["name"], "orchflows-firstmate-home")
            result[relative] = [entry["name"] for entry in catalog["plugins"]]
        return result

    def test_first_setup_creates_an_empty_home_that_doctor_accepts(self) -> None:
        result = orchflows.setup(self.home)
        self.assertEqual(result["status"], "ready", result)
        self.assertEqual(result["files"], {"README.md": "created", ".gitignore": "created",
                                           ".agents/plugins/marketplace.json": "written", ".claude-plugin/marketplace.json": "written"})
        self.assertEqual(result["libraries"], [])
        self.assertTrue((self.home / "libraries").is_dir())
        self.assertEqual(self.catalogs(), {relative: [] for relative in orchflows.CATALOGS})
        self.assertNotIn("runtime", result)
        self.assertFalse((self.home / ".local").exists(), "no managed core or runtime")
        self.assertEqual(orchflows.doctor(self.home)["status"], "ready")

    def test_setup_catalogs_valid_libraries_with_relative_paths_only(self) -> None:
        library(self.home / "libraries/quickfix", "quickfix", "0.1.1")
        library(self.home / "libraries/my-folder", "custom-research")
        result = orchflows.setup(self.home)
        self.assertEqual(result["status"], "ready", result)
        self.assertEqual([entry["name"] for entry in result["libraries"]], ["custom-research", "quickfix"])
        for relative in orchflows.CATALOGS:
            text = (self.home / relative).read_text(encoding="utf-8")
            catalog = json.loads(text)
            self.assertEqual({entry["name"]: entry["source"]["path"] if isinstance(entry["source"], dict) else entry["source"]
                              for entry in catalog["plugins"]},
                             {"custom-research": "./libraries/my-folder", "quickfix": "./libraries/quickfix"})
            self.assertNotIn(str(self.home), text)
        self.assertEqual(orchflows.doctor(self.home)["status"], "ready")

    def test_repeat_preserves_user_files_and_refreshes_only_the_catalogs(self) -> None:
        library(self.home / "libraries/quickfix", "quickfix")
        first = orchflows.setup(self.home)
        write(self.home / "README.md", "My user-owned README.\n")
        write(self.home / ".gitignore", "my-user-pattern\n")
        write(self.home / "libraries/quickfix/README.md", "My authored library.\n")
        write(self.home / "logs/saved.md", "My existing report.\n")
        library(self.home / "libraries/another", "another")
        before = snapshot(self.home)
        second = orchflows.setup(self.home)
        self.assertEqual(second["status"], "ready", second)
        self.assertEqual(second["files"]["README.md"], "preserved")
        self.assertEqual(second["files"][".gitignore"], "preserved")
        self.assertEqual(second["git"], "preserved" if first["git"] == "initialized" else first["git"])
        after = snapshot(self.home)
        changed = {name for name in before if before[name] != after.get(name)}
        self.assertEqual(changed, set(orchflows.CATALOGS), "only the catalogs changed")
        self.assertEqual(self.catalogs(), {relative: ["another", "quickfix"] for relative in orchflows.CATALOGS})
        self.assertEqual(orchflows.setup(self.home)["files"][".claude-plugin/marketplace.json"], "current")

    def test_setup_never_touches_host_settings_or_the_environment_home_when_home_is_explicit(self) -> None:
        write(self.root / "codex/config.toml", "malformed = [\n")
        result = self.cli("setup", "--home", str(self.home))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(Path(report["home"]), self.home)
        self.assertEqual((self.root / "codex/config.toml").read_text(), "malformed = [\n")
        self.assertFalse((self.root / "claude").exists())
        self.assertFalse((self.root / "env-home").exists())
        for arguments in (("--source", "x"), ("--example", "x"), ("--concurrency", "2")):
            self.assertEqual(self.cli("setup", *arguments).returncode, 2, arguments)
        self.assertEqual(self.cli("resolve", "quickfix").returncode, 2)

    def test_cli_defaults_to_the_environment_home_and_reports_issues_with_exit_1(self) -> None:
        env_home = self.root / "env-home"
        library(env_home / "libraries/first", "duplicate")
        library(env_home / "libraries/second", "duplicate")
        library(env_home / "libraries/shadow-core", "orchflows")
        write(env_home / "libraries/broken/plugin.json", "{broken")
        library(env_home / "libraries/valid", "valid")
        before = snapshot(env_home)
        result = self.cli("setup")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "partial")
        issues = " ".join(report["issues"])
        self.assertIn("Ambiguous library name: duplicate", issues)
        self.assertIn("Ambiguous library name: orchflows", issues)
        self.assertIn("Malformed package manifest", issues)
        self.assertEqual({name: value for name, value in snapshot(env_home).items() if name in before}, before)
        for relative in orchflows.CATALOGS:
            catalog = json.loads((env_home / relative).read_text(encoding="utf-8"))
            self.assertEqual([entry["name"] for entry in catalog["plugins"]], ["valid"])
        doctor = self.cli("doctor")
        self.assertEqual(doctor.returncode, 1)
        self.assertEqual(json.loads(doctor.stdout)["status"], "incomplete")

    def test_doctor_is_read_only_and_reports_stale_catalogs_that_setup_regenerates(self) -> None:
        library(self.home / "libraries/quickfix", "quickfix")
        orchflows.setup(self.home)
        library(self.home / "libraries/later", "later")
        write(self.home / ".claude-plugin/marketplace.json", '{"name":"orchflows-firstmate-home","plugins":[{"name":"external","source":"./elsewhere"}]}\n')
        before = snapshot(self.home)
        report = orchflows.doctor(self.home)
        self.assertEqual(report["status"], "incomplete")
        self.assertIn("rerun setup", " ".join(report["issues"]))
        self.assertEqual(report["checks"]["catalogs"][".claude-plugin/marketplace.json"], "stale")
        self.assertEqual(snapshot(self.home), before)
        self.assertEqual(orchflows.setup(self.home)["status"], "ready")
        self.assertEqual(self.catalogs(), {relative: ["later", "quickfix"] for relative in orchflows.CATALOGS})
        self.assertEqual(orchflows.doctor(self.home)["status"], "ready")
        missing = self.root / "does-not-exist"
        self.assertEqual(orchflows.doctor(missing)["status"], "incomplete")
        self.assertFalse(missing.exists())

    def test_setup_refuses_normal_orchflows_homes_and_catalogs_before_writing(self) -> None:
        with patch.dict(os.environ, {"ORCHFLOWS_HOME": str(self.root / "normal")}):
            for home in (self.root / "normal", self.root / "normal/nested"):
                with self.subTest(home=home), self.assertRaisesRegex(ValueError, "overlaps the normal Orchflows home"):
                    orchflows.setup(home)
                self.assertFalse(home.exists())
        write(self.home / ".claude-plugin/marketplace.json", '{"name":"orchflows-home","plugins":[]}\n')
        before = snapshot(self.home)
        with self.assertRaisesRegex(ValueError, "Normal Orchflows catalog is protected"):
            orchflows.setup(self.home)
        self.assertEqual(snapshot(self.home), before)
        result = self.cli("setup", "--home", str(self.home))
        self.assertEqual(result.returncode, 2)
        self.assertIn("protected", json.loads(result.stderr)["error"])

    def test_setup_never_writes_through_links(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        self.home.mkdir()
        try:
            (self.home / "libraries").symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"Symlink creation unavailable: {exc}")
        with self.assertRaisesRegex(ValueError, "does not write through links"):
            orchflows.setup(self.home)
        self.assertEqual(list(outside.iterdir()), [])
        (self.home / "libraries").unlink()
        (self.home / "libraries").mkdir()
        (self.home / "libraries/linked").symlink_to(outside, target_is_directory=True)
        library(outside, "linked")
        result = orchflows.setup(self.home)
        self.assertEqual(result["status"], "partial")
        self.assertIn("Library is a link", " ".join(result["issues"]))
        self.assertEqual(self.catalogs(), {relative: [] for relative in orchflows.CATALOGS})

    def test_home_git_ignores_artifacts_and_tracks_libraries(self) -> None:
        git = shutil.which("git")
        if not git:
            self.skipTest("Git unavailable")
        library(self.home / "libraries/quickfix", "quickfix")
        result = orchflows.setup(self.home)
        self.assertEqual(result["git"], "initialized")
        write(self.home / "artifacts/report.html", "Generated output")
        status = subprocess.run([git, "-C", str(self.home), "status", "--porcelain", "--untracked-files=all"],
                                text=True, capture_output=True, check=True).stdout
        self.assertIn("libraries/quickfix/skills/sample/SKILL.md", status)
        self.assertIn(".claude-plugin/marketplace.json", status)
        self.assertNotIn("artifacts/report.html", status)
        commits = subprocess.run([git, "-C", str(self.home), "rev-parse", "--verify", "HEAD"], text=True, capture_output=True, check=False)
        self.assertNotEqual(commits.returncode, 0, "setup never commits")


if __name__ == "__main__":
    unittest.main()
