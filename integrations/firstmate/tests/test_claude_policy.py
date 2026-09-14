"""Declared-file grants: real controller state, no Claude or fleet process."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

import test_task_group as fixtures
from fm_task_group_policy import claude_permissions, file_rule
from fm_task_group_store import GroupError


class ClaudePolicyTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.tmp = self.fixture.base / "task's scratch Ω & [literal]"
        self.tmp.mkdir()
        self.fixture.root_meta["tasktmp"] = str(self.tmp)
        self.fixture.save_meta("root", self.fixture.root_meta)

    def rule(self, tool, path, tree=False):
        return file_rule(self.owner.runtime, tool, path, tree=tree)

    def test_root_grants_declared_files_without_editing_project_or_package(self):
        policy = claude_permissions(self.owner, "root", "s1.123.4")
        self.assertEqual(set(policy), {"allow"})
        rules = policy["allow"]
        self.assertIn(self.rule("Read", self.fixture.attachment["package_path"], True), rules)
        self.assertIn(self.rule("Read", self.owner.home / "state/root.meta"), rules)
        self.assertIn(self.rule("Read", self.owner.group("root"), True), rules)
        edits = {value for value in rules if value.startswith("Edit(")}
        self.assertEqual(edits, {self.rule("Edit", self.tmp, True),
                                 self.rule("Edit", self.owner.home / "state/root.status"),
                                 self.rule("Edit", self.owner.task("root") / "report.md")})
        self.assertFalse(any(value.startswith("Bash") for value in rules))
        self.assertNotIn(self.rule("Read", self.owner.home, True), rules)
        self.assertNotIn(self.rule("Read", self.owner.code_root, True), rules)

    def test_component_cannot_edit_parent_report_or_read_parent_metadata(self):
        child = self.fixture.submit()["request"]["child"]
        policy = claude_permissions(self.owner, child, "s2.345.6")
        rules = policy["allow"]
        self.assertIn(self.rule("Read", self.owner.home / "state" / f"{child}.meta"), rules)
        self.assertNotIn(self.rule("Read", self.owner.home / "state/root.meta"), rules)
        self.assertNotIn(self.rule("Read", self.owner.group("root"), True), rules)
        self.assertNotIn(self.rule("Edit", self.owner.task("root") / "report.md"), rules)
        self.assertEqual(sum(value.startswith("Edit(") for value in rules), 2)

    def test_relaunch_requires_new_generation_and_rebuilds_permissions(self):
        before = claude_permissions(self.owner, "root", "s1.123.4")
        self.fixture.root_meta["spawn_gen"] = "s3.456.7"
        self.fixture.save_meta("root", self.fixture.root_meta)
        with self.assertRaises(GroupError):
            claude_permissions(self.owner, "root", "s1.123.4")
        self.assertEqual(claude_permissions(self.owner, "root", "s3.456.7"), before)

    def test_missing_tasktmp_and_other_harness_refuse(self):
        self.fixture.root_meta.pop("tasktmp")
        self.fixture.save_meta("root", self.fixture.root_meta)
        with self.assertRaisesRegex(GroupError, "tasktmp"):
            claude_permissions(self.owner, "root", "s1.123.4")
        self.fixture.root_meta.update(tasktmp=str(self.tmp), harness="codex")
        self.fixture.save_meta("root", self.fixture.root_meta)
        with self.assertRaisesRegex(GroupError, "Claude worker"):
            claude_permissions(self.owner, "root", "s1.123.4")

    def test_cli_preserves_unicode_and_literal_glob_characters(self):
        result = subprocess.run([sys.executable, "-B", str(fixtures.BIN / "fm-task-group.py"),
                                 "--home", str(self.owner.home), "launch-claude-permissions",
                                 "root", "--generation", "s1.123.4"],
                                capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        policy = json.loads(result.stdout)
        self.assertEqual(policy, claude_permissions(self.owner, "root", "s1.123.4"))
        rule = self.rule("Edit", self.tmp, True)
        self.assertIn(r"\[literal\]", rule)
        self.assertIn("Ω &", rule)

    @unittest.skipUnless(os.name == "posix" and shutil.which("jq"), "Bash launch settings with jq")
    def test_actual_launch_settings_expansion_preserves_mode_and_json_arguments(self):
        candidate = Path(os.environ.get("FM_STAGE1_FIRSTMATE_ROOT", ""))
        source = (candidate / "bin/fm-spawn.sh").read_text(encoding="utf-8")
        quote = "shell_quote() {" + source.split("shell_quote() {", 1)[1].split("\n}\n", 1)[0] + "\n}\n"
        settings = "CLAUDE_SETTINGS=" + source.split("\nCLAUDE_SETTINGS=", 1)[1].split('\nif [ "$HARNESS" = rovo ]', 1)[0]
        script = quote + '''
set -eu
fm_task_group_python() { "$PYTHON" -B "$@"; }
claude() { "$PYTHON" -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "$@"; }
LAUNCH='claude --permission-mode auto --settings __CLAUDESETTINGS__'
''' + settings + '\neval "$LAUNCH"\n'
        for bound in ("0", "1"):
            with self.subTest(bound=bound):
                env = dict(os.environ, PYTHON=sys.executable, HARNESS="claude", TASK_GROUP_BOUND=bound,
                           SCRIPT_DIR=str(fixtures.BIN), FM_HOME=str(self.owner.home),
                           ID="root", SPAWN_GEN="s1.123.4")
                result = subprocess.run(["bash", "-c", script], env=env, capture_output=True,
                                        text=True, encoding="utf-8", timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                argv = json.loads(result.stdout)
                self.assertEqual(argv[:3], ["--permission-mode", "auto", "--settings"])
                self.assertEqual(len(argv), 4)
                settings_value = json.loads(argv[3])
                self.assertEqual(settings_value["feedbackDrafts"], "off")
                self.assertEqual(settings_value["attribution"], {"commit": "", "pr": "", "sessionUrl": False})
                if bound == "1":
                    self.assertEqual(settings_value["permissions"], claude_permissions(self.owner, "root", "s1.123.4"))
                else:
                    self.assertNotIn("permissions", settings_value)

    @unittest.skipUnless(sys.platform == "linux" and shutil.which("jq"), "Linux Bash launch with jq")
    def test_linux_foreground_profile_is_applied_only_to_attached_claude_launches(self):
        source = (Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"]) / "bin/fm-spawn.sh").read_text()
        quote = "shell_quote() {" + source.split("shell_quote() {", 1)[1].split("\n}\n", 1)[0] + "\n}\n"
        settings = "CLAUDE_SETTINGS=" + source.split("\nCLAUDE_SETTINGS=", 1)[1].split(
            '\nif [ "$HARNESS" = rovo ]', 1)[0]
        script = quote + """
set -eu
fm_task_group_python() { "$PYTHON" -B "$@"; }
worker() { "$PYTHON" -c 'import json,os,sys; print(json.dumps({"argv":sys.argv[1:],"background":os.environ.get("CLAUDE_CODE_DISABLE_BACKGROUND_TASKS"),"timeout":os.environ.get("BASH_DEFAULT_TIMEOUT_MS")}))' "$@"; }
LAUNCH='worker --permission-mode auto --settings __CLAUDESETTINGS__'
""" + settings + '\neval "$LAUNCH"\n'
        for harness, bound in (("claude", "1"), ("claude", "0"), ("codex", "1")):
            with self.subTest(harness=harness, bound=bound):
                env = dict(os.environ, PYTHON=sys.executable, HARNESS=harness,
                           TASK_GROUP_BOUND=bound, SCRIPT_DIR=str(fixtures.BIN),
                           FM_HOME=str(self.owner.home), ID="root", SPAWN_GEN="s1.123.4",
                           CLAUDE_CODE_DISABLE_BACKGROUND_TASKS="0", BASH_DEFAULT_TIMEOUT_MS="1234")
                result = subprocess.run(["bash", "-c", script], env=env,
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                observed = json.loads(result.stdout)
                expected = ("1", "420000") if (harness, bound) == ("claude", "1") else ("0", "1234")
                self.assertEqual((observed["background"], observed["timeout"]), expected)
                self.assertEqual(observed["argv"][:3], ["--permission-mode", "auto", "--settings"])
                self.assertEqual(len(observed["argv"]), 4)
                self.assertEqual(env["CLAUDE_CODE_DISABLE_BACKGROUND_TASKS"], "0")

    @unittest.skipUnless(os.name == "nt", "native Windows permission normalization")
    def test_windows_rules_use_native_drive_not_msys_tmp_alias(self):
        rule = file_rule(self.owner.runtime, "Read", "/tmp", tree=True)
        self.assertRegex(rule, r"^Read\(//[a-z]/")
        self.assertNotIn("Read(//tmp/", rule)


if __name__ == "__main__":
    unittest.main()
