"""No-verb signal and actionable-span owners with explicit current-state fixtures.

The real ordinary watcher loop is covered separately by the native trial. These
tests exercise its shared predicates without starting a fleet or model worker.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SOURCE = Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"])


@unittest.skipUnless(os.name == "posix", "POSIX watcher signal predicates")
class SignalWaitingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fm-group-signals-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        for name in ("state", "current", "config", "data"):
            (self.home / name).mkdir()
        for task in ("root", "other", "mate"):
            kind = "secondmate" if task == "mate" else "scout"
            (self.home / f"state/{task}.meta").write_text(f"kind={kind}\n", encoding="utf-8")
            (self.home / f"state/{task}.status").write_text("working: submitted and polling\n", encoding="utf-8")
            (self.home / f"state/{task}.turn-ended").touch()
            self.current(task, "waiting", "task-group")
        crew = self.home / "crew-state"
        crew.write_text('#!/usr/bin/env bash\ncat "$FM_HOME/current/$1"\n', encoding="utf-8")
        crew.chmod(0o755)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("FM_", "HERDR_"))}
        self.env.update(FM_HOME=str(self.home), FM_ROOT_OVERRIDE=str(SOURCE),
                        STATE=str(self.home / "state"), CODE=str(SOURCE),
                        FM_CREW_STATE_BIN=str(crew), FM_GATE_REFUSE_BYPASS="1")

    def current(self, task, state, source):
        (self.home / "current" / task).write_text(
            f"state: {state} · source: {source} · fixture observation\n", encoding="utf-8")

    def shell(self, body):
        result = subprocess.run(["bash", "-c", '. "$CODE/bin/fm-watch.sh"\n' + body],
                                env=self.env, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def test_routine_status_and_turn_end_absorb_without_claiming_root_working(self):
        self.assertEqual(self.shell(r'''
if signal_files_actionable "$STATE/root.status"; then exit 81; fi
signal_crew_provably_working "$STATE/root.status" || exit 82
signal_crew_provably_working "$STATE/root.turn-ended" || exit 83
signal_crew_provably_working "$STATE/root.status" "$STATE/root.turn-ended" || exit 84
if crew_is_provably_working root; then exit 85; fi
printf absorbed
'''), "absorbed")

    def test_unknown_ready_failed_or_non_group_waits_do_not_absorb(self):
        cases = (("group-attention", "task-group"), ("group-ready", "task-group"),
                 ("component-ready", "task-group"), ("unknown", "none"),
                 ("failed", "pane"), ("done", "status-log"), ("paused", "status-log"),
                 ("waiting", "status-log"), ("waiting", "pane"), ("working", "status-log"))
        for state, source in cases:
            with self.subTest(state=state, source=source):
                self.current("root", state, source)
                self.assertEqual(self.shell(r'''
if signal_crew_provably_working "$STATE/root.status"; then exit 81; fi
if signal_crew_provably_working "$STATE/root.turn-ended"; then exit 82; fi
printf surfaced
'''), "surfaced")

    def test_actionable_events_and_unreadable_span_win_over_waiting(self):
        status = self.home / "state/root.status"
        for event in ("needs-decision: choose the next action", "blocked: missing input",
                      "done: retained report", "failed: component failed"):
            with self.subTest(event=event):
                # An actionable event must survive a newer routine note.
                status.write_text(event + "\nworking: still polling\n", encoding="utf-8")
                self.assertEqual(self.shell(r'''
signal_files_actionable "$STATE/root.status" || exit 81
signal_crew_provably_working "$STATE/root.status" || exit 82
printf actionable-first
'''), "actionable-first")
        status.unlink()
        status.mkdir()
        self.assertEqual(self.shell(r'''
signal_files_actionable "$STATE/root.status" || exit 81
printf unreadable-surfaces
'''), "unreadable-surfaces")

    def test_mixed_batches_and_secondmate_exclusion_keep_existing_semantics(self):
        self.current("other", "working", "pane")
        self.assertEqual(self.shell(r'''
signal_crew_provably_working "$STATE/root.status" "$STATE/other.turn-ended" || exit 81
if signal_crew_provably_working "$STATE/root.status" "$STATE/mate.status"; then exit 82; fi
if signal_crew_provably_working; then exit 83; fi
printf bounded
'''), "bounded")
        self.current("other", "unknown", "none")
        self.assertEqual(self.shell(r'''
if signal_crew_provably_working "$STATE/root.status" "$STATE/other.turn-ended"; then exit 81; fi
printf mixed-surfaces
'''), "mixed-surfaces")
        self.current("mate", "working", "pane")
        self.assertEqual(self.shell(r'''
if signal_crew_provably_working "$STATE/mate.status"; then exit 81; fi
signal_crew_provably_working "$STATE/mate.turn-ended" || exit 82
printf mate-routing-preserved
'''), "mate-routing-preserved")


if __name__ == "__main__":
    unittest.main()
