"""Source integration: real result custody, tasks-axi, pending-close and replay.

No endpoint or harness starts. The existing controller fixture injects its spawn
and notification boundary; this suite runs the actual teardown argument/guard
sections and the production pending-close owner against a private real backlog.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

SOURCE = Path(os.environ.get("FM_STAGE1_FIRSTMATE_ROOT", Path(__file__).resolve().parents[3] / ".scratch/stage1/firstmate"))
sys.path.insert(0, os.environ.get("FM_STAGE1_TESTS_ROOT", str(Path(__file__).resolve().parent)))
import test_task_group as fixtures


@unittest.skipUnless(os.name == "posix" and shutil.which("tasks-axi"), "requires POSIX and real tasks-axi")
class ComponentBacklogTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.home = self.fixture.home
        self.child = self.fixture.completed()["request"]["child"]
        (self.home / "config").mkdir()
        (self.home / ".tasks.toml").write_text('backend = "markdown"\n[markdown]\npath = "data/backlog.md"\n')
        self.backlog = self.home / "data/backlog.md"
        self.backlog.write_text("# Backlog\n\n## In flight\n\n## Queued\n\n## Done\n")
        private_home = self.fixture.base / "user-home"
        private_home.mkdir()
        self.env = dict(os.environ, HOME=str(private_home), CODE=str(SOURCE),
                        FM_HOME=str(self.home), STATE=str(self.home / "state"),
                        DATA=str(self.home / "data"), ID=self.child,
                        SCRIPT_DIR=str(SOURCE / "bin"), KIND="scout", MODE="", PR_URL="")
        for key in ("TASKS_AXI_FILE", "TASKS_AXI_BACKEND"):
            self.env.pop(key, None)
        self.cli("add", self.child, "Internal component", "--kind", "scout")
        self.cli("start", self.child)

    def cli(self, *args):
        return subprocess.run(["tasks-axi", *args, "--file", str(self.backlog)],
                              env=self.env, check=True, capture_output=True, text=True).stdout

    def gather(self):
        self.fixture.owner.status("root", "s1.123.4", gather=True)

    def run_owner(self, extra="", *, guarded=True):
        teardown = (SOURCE / "bin/fm-teardown.sh").read_text()
        guard = teardown.split('fm_task_group_guard "$FM_HOME"', 1)[1].split("TEARDOWN_META_KIND=", 1)[0]
        guard = 'fm_task_group_guard "$FM_HOME"' + guard
        args = teardown.split("backlog_done_args() {", 1)[1].split("\n}\n", 1)[0]
        script = '''set -eu
umask 022
. "$CODE/bin/fm-wake-lib.sh"
. "$CODE/bin/fm-tasks-axi-lib.sh"
. "$CODE/bin/fm-backlog-transition-lib.sh"
. "$CODE/bin/fm-task-group-state.sh"
trap 'rc=$?; [ "$rc" = 0 ] || printf "%s\\n" "$FM_BACKLOG_TRANSITION_ERROR" >&2; fm_lock_release "$STATE/$ID.meta.lock" || true' EXIT
fm_lock_acquire_wait "$STATE/$ID.meta.lock"
'''
        if guarded:
            script += guard
        script += "\nbacklog_done_args() {" + args + "\n}\n"
        script += extra
        return subprocess.run(["bash", "-c", script], env=self.env, capture_output=True, text=True, timeout=30)

    def test_legacy_component_note_is_rejected_before_any_record_mutation(self):
        result = self.run_owner('''
if fm_backlog_close_marker_write "$STATE" "$ID" "$DATA" s2.345.6 --note "component result retained and gathered by parent"; then exit 8; fi
printf '%s\\n' "$FM_BACKLOG_TRANSITION_ERROR"
''', guarded=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("invalid pending-close arguments", result.stdout)
        self.assertTrue((self.home / "state" / f"{self.child}.meta").exists())
        self.assertFalse((self.home / "state" / f"{self.child}.backlog-close").exists())
        self.assertIn("in_flight", self.cli("show", self.child))

    def test_gathered_report_survives_parent_retirement_and_interrupted_close(self):
        self.gather()
        (self.home / "state/root.meta").unlink()
        report = self.home / "data/root/task-group/results" / self.child / "report.md"
        original = report.read_bytes()
        result = self.run_owner('''
backlog_done_args
fm_backlog_close_marker_write "$STATE" "$ID" "$DATA" s2.345.6 "${BACKLOG_DONE_ARGS[@]}"
fm_backlog_close_marker_validate "$STATE/$ID.backlog-close" "$DATA" "$ID" "$STATE"
printf 'recorded=%s\\n' "${FM_BACKLOG_CLOSE_VALIDATED_ARGS[*]}"
# Simulate a crash after the pending close was published; recovery owns both halves.
fm_backlog_close_marker_replay "$STATE" "$STATE/$ID.backlog-close" "$DATA"
printf 'replay=%s\\n' "$FM_BACKLOG_CLOSE_REPLAY_RESULT"
fm_backlog_close_marker_replay "$STATE" "$STATE/$ID.backlog-close" "$DATA"
printf 'retry=%s\\n' "$FM_BACKLOG_CLOSE_REPLAY_RESULT"
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        relative = f"data/root/task-group/results/{self.child}/report.md"
        self.assertIn("recorded=--report " + relative, result.stdout)
        self.assertIn("replay=closed_incomplete", result.stdout)
        self.assertIn("retry=noop", result.stdout)
        self.assertIn("done", self.cli("show", self.child))
        self.assertIn(relative, self.backlog.read_text())
        self.assertFalse((self.home / "state" / f"{self.child}.meta").exists())
        self.assertFalse((self.home / "state" / f"{self.child}.backlog-close").exists())
        self.assertEqual(report.read_bytes(), original)
        self.assertFalse((self.home / "data" / self.child / "report.md").exists())

    def test_ungathered_or_corrupt_result_preserves_component_record_and_backlog(self):
        for scenario in ("ungathered", "corrupt"):
            if scenario == "corrupt":
                self.gather()
                report = self.home / "data/root/task-group/results" / self.child / "report.md"
                report.write_text("changed after gather")
            with self.subTest(scenario=scenario):
                result = self.run_owner("backlog_done_args\n")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("ungathered or uncertain work" if scenario == "ungathered" else
                              "requires reconciliation", result.stderr)
                self.assertTrue((self.home / "state" / f"{self.child}.meta").exists())
                self.assertIn("in_flight", self.cli("show", self.child))


if __name__ == "__main__":
    unittest.main(verbosity=2)
