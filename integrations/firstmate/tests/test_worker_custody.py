"""Stage 1 worker custody refusals at actual FirstMate launch/cleanup owners.

These tests do not start a harness or certify native endpoint custody. Native
entrypoint tests run complete scripts; reap tests use their exact owning function
and destructive-boundary blocks, retaining real disposable filesystem records.
"""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"])
BASH = (Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/usr/bin/bash.exe"
        if os.name == "nt" else Path(shutil.which("bash")))


class WorkerCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fm-custody-", ignore_cleanup_errors=True)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.project = self.base / "project"
        self.worktree = self.base / "worktree"
        self.tasktmp = self.base / "tasktmp"
        for path in (self.home / "state", self.home / "data/root/task-group",
                     self.home / "config", self.project, self.worktree, self.tasktmp):
            path.mkdir(parents=True)
        (self.home / "data/root/task-group/attachment.json").write_text('{"retained":"fixture"}')
        (self.home / "state/root.meta").write_text(
            f"kind=scout\nbackend=herdr\ntask_group_role=root\nspawn_gen=s1\nworktree={self.worktree}\n")
        (self.project / "input.txt").write_text("unchanged input")
        (self.worktree / "work.txt").write_text("retained work")
        (self.tasktmp / "report.md").write_text("retained report")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("FM_", "HERDR_"))}
        self.env.update(FM_HOME=self.shell_path(self.home), FM_ROOT_OVERRIDE=self.shell_path(SOURCE),
                        SCRIPT_DIR=self.shell_path(SOURCE / "bin"), STATE=self.shell_path(self.home / "state"),
                        DATA=self.shell_path(self.home / "data"), ID="root", BACKEND="herdr", KIND="scout",
                        WT=self.shell_path(self.worktree), TASK_TMP=self.shell_path(self.tasktmp),
                        T="fm-lab-custody:p1", FM_SPAWN_NO_GUARD="1", TEARDOWN_TASK_GROUP_BOUND="1",
                        _FM_UNAME="Linux" if os.name == "nt" else "MINGW64_NT-fake",
                        HOME=self.shell_path(self.base), MSYS="winsymlinks:nativestrict")
        # Only the inherited watcher doorbell is disabled. No native platform
        # override can bypass the worker custody guard in the actual spawn owner.
        if os.name == "nt":
            self.env["PATH"] = str(BASH.parent) + os.pathsep + self.env["PATH"]
        self.before = self.snapshot()

    def shell_path(self, path):
        if os.name != "nt":
            return str(path)
        return subprocess.check_output([str(BASH.with_name("cygpath.exe")), "-u", str(path)], text=True).strip()

    def snapshot(self):
        return {p.relative_to(self.base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.base.rglob("*") if p.is_file()}

    def run_shell(self, script, timeout=20):
        with tempfile.TemporaryDirectory(prefix="fm-custody-script-") as directory:
            path = Path(directory) / "run.sh"
            path.write_text(script, encoding="utf-8", newline="\n")
            return subprocess.run([str(BASH), "--noprofile", "--norc", self.shell_path(path)],
                                  cwd=self.base, env=self.env, capture_output=True, text=True, timeout=timeout)

    def reap_owner(self):
        text = (SOURCE / "bin/fm-teardown.sh").read_text(encoding="utf-8")
        return "pids_with_cwd_under() {" + text.split("pids_with_cwd_under() {", 1)[1].split(
            "\nrequire_orca_worktree_path_match()", 1)[0]

    def reap_transaction(self):
        text = (SOURCE / "bin/fm-teardown.sh").read_text(encoding="utf-8")
        start = text.index('if [ "$KIND" != secondmate ] && teardown_owns_worktree; then',
                           text.index("# Every landed/discard-work refusal above"))
        return text[start:text.index("\n# Fix 3", start)]

    def missing_lsof(self):
        return """
command() {
  if [ "$1" = -v ] && [ "${2:-}" = lsof ]; then return 1; fi
  builtin command "$@"
}
"""

    def assert_retained(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), self.before)
        self.assertTrue(self.worktree.is_dir())
        self.assertTrue(self.tasktmp.is_dir())

    @unittest.skipUnless(os.name == "nt", "native Windows complete entrypoint")
    def test_native_spawn_and_relaunch_refuse_before_worker_mutations(self):
        for binding in ("attachment", "component", "metadata"):
            group = self.home / "data/root/task-group"
            component = self.home / "data/root/task-group-component.json"
            meta = self.home / "state/root.meta"
            if binding == "attachment":
                meta.unlink()  # First launch: only the admission attachment exists.
            elif binding == "component":
                shutil.rmtree(group)
                component.write_text('{"retained":"component"}')
            else:
                component.unlink()
                meta.write_text("kind=scout\nbackend=herdr\ntask_group_role=root\nspawn_gen=s1\n")
            self.before = self.snapshot()
            for relaunch in (False, True):
                with self.subTest(binding=binding, relaunch=relaunch):
                    command = ('"$SCRIPT_DIR/fm-spawn.sh" root --relaunch' if relaunch else
                               '"$SCRIPT_DIR/fm-spawn.sh" root "' + self.shell_path(self.project) +
                               '" --scout --backend herdr')
                    result = self.run_shell(command)
                    self.assert_retained(result)
                    self.assertIn("native Windows Stage 1 task-group spawn", result.stderr)
                    self.assertIn("Controller/bridge fixture support does not enable real workers", result.stderr)

    @unittest.skipUnless(os.name == "nt", "native Windows complete entrypoint")
    def test_native_teardown_and_force_retain_all_task_records(self):
        for force in ("", " --force"):
            with self.subTest(force=force):
                result = self.run_shell('"$SCRIPT_DIR/fm-teardown.sh" root' + force)
                self.assert_retained(result)
                self.assertIn("native Windows Stage 1 task-group teardown", result.stderr)

    def test_platform_guard_uses_real_host_and_preserves_unbound_tasks(self):
        script = '. "$SCRIPT_DIR/fm-task-group-runtime.sh"\n'
        script += 'fm_task_group_native_worker_guard "$FM_HOME" "$ID" "$STATE" spawn\n'
        result = self.run_shell(script)
        self.assertEqual(result.returncode, 1 if os.name == "nt" else 0, result.stderr)
        shutil.rmtree(self.home / "data/root/task-group")
        (self.home / "state/root.meta").write_text("kind=scout\nbackend=herdr\n")
        result = self.run_shell(script)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_lsof_refuses_cleanup_even_under_force_and_conditional_call(self):
        for force, owns in (("", "1"), ("--force", "1"), ("--force", "0")):
            with self.subTest(force=force, owns=owns):
                self.env.update(FORCE=force, OWNS_WORKTREE=owns)
                result = self.run_shell("set -eu\n" + self.reap_owner() + self.missing_lsof() + """
teardown_owns_worktree() { [ "$OWNS_WORKTREE" = 1 ]; }
conclude_task_no_mistakes_run() { :; }
""" + self.reap_transaction() + """
# Reaching destructive continuation would lose these real fixture artifacts.
rm -f "$STATE/$ID.meta" "$WT/work.txt" "$TASK_TMP/report.md"
""")
                self.assert_retained(result)
                self.assertIn("Stage 1 task-group cleanup", result.stderr)
                conditional = self.run_shell(self.reap_owner() + self.missing_lsof() + """
if reap_task_worktree_processes worktree "$WT" "$TASK_TMP"; then exit 91; else exit "$?"; fi
""")
                self.assertEqual(conditional.returncode, 1, conditional.stderr)

    def test_backend_fallback_refusal_status_is_propagated(self):
        result = self.run_shell(self.reap_owner() + self.missing_lsof() + """
reap_task_backend_process_group() { return 73; }
if reap_task_worktree_processes worktree "$WT"; then exit 91; else exit "$?"; fi
""")
        self.assertEqual(result.returncode, 73, result.stderr)

    def test_ordinary_herdr_missing_lsof_retains_upstream_behavior(self):
        self.env["TEARDOWN_TASK_GROUP_BOUND"] = "0"
        result = self.run_shell(self.reap_owner() + self.missing_lsof() +
                                'reap_task_worktree_processes worktree "$WT"\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("warning: lsof is unavailable", result.stderr)

    @unittest.skipUnless(os.name == "posix" and shutil.which("lsof"), "real POSIX lsof cleanup")
    def test_real_lsof_reaps_owned_process_and_preserves_unrelated_tripwire(self):
        owned = subprocess.Popen(["sleep", "60"], cwd=self.worktree)
        tripwire = subprocess.Popen(["sleep", "60"], cwd=self.project)
        def stop(process):
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=5)
        self.addCleanup(stop, tripwire)
        self.addCleanup(stop, owned)
        result = self.run_shell("set -eu\n" + self.reap_owner() +
                                'reap_task_worktree_processes worktree "$WT" "$TASK_TMP"\n', timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIsNotNone(owned.poll())
        self.assertIsNone(tripwire.poll())
        self.assertEqual(self.snapshot(), self.before)

    def test_lsof_scan_failure_retains_task_records(self):
        result = self.run_shell("set -eu\n" + self.reap_owner() + """
lsof() { return 19; }
teardown_owns_worktree() { return 0; }
conclude_task_no_mistakes_run() { :; }
""" + self.reap_transaction() + 'rm -f "$STATE/$ID.meta" "$WT/work.txt" "$TASK_TMP/report.md"\n')
        self.assert_retained(result)
        self.assertIn("lsof failed", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
