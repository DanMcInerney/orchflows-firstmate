"""Source integration fixtures only: no fleet, Herdr server, or agent is started.

Run on POSIX with FM_STAGE1_FIRSTMATE_ROOT pointing at the prepared candidate.
Controller JSON and endpoint/current-state observations are explicit test doubles.
The existing watcher/away functions, lifecycle guards and inbox writer are real.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SOURCE = Path(os.environ.get("FM_STAGE1_FIRSTMATE_ROOT", Path(__file__).resolve().parents[3] / ".scratch/stage1/firstmate"))

STUBS = r'''
python3() {
  if [ "${1##*/}" = fm-task-group.py ]; then cat "$QUERY"; else command python3 "$@"; fi
}
export -f python3
fm_meta_get() { sed -n "s/^$2=//p" "$1" | tail -1; }
fm_backend_validate_task_endpoint() {
  [ -f "$1" ] || return 1
  FM_BACKEND_VALIDATED_BACKEND=herdr
  FM_BACKEND_VALIDATED_TARGET=$2
}
fm_backend_agent_state() {
  if [ "$2" = root ]; then printf '%s' "$ROOT_LIVE"; else printf '%s' "$CHILD_LIVE"; fi
}
'''


@unittest.skipUnless(os.name == "posix", "Bash lifecycle fixtures require POSIX")
class LifecycleStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fm-group-lifecycle-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        for part in ("state", "config", "data/root/task-group", "data/child", "tools/bin"):
            (self.home / part).mkdir(parents=True, exist_ok=True)
        self.query = self.home / "query.json"
        self.record = dict(attached=True, component=False, pending=True, cleanup_allowed=False,
                           child_task_id="child", child_generation="s1", result_ready=False)
        self.write_query()
        for task in ("root", "child"):
            (self.home / "state" / f"{task}.meta").write_text(
                f"kind=scout\nspawn_gen=s1\nwindow=lab:{task}\nendpoint_task_id={task}\nbackend=herdr\n")
        self.crew = self.home / "crew-state"
        self.crew.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$CHILD_CURRENT"\n')
        self.crew.chmod(0o755)
        guard = self.home / "tools/bin/fm-guard.sh"
        guard.write_text("#!/usr/bin/env bash\nexit 0\n")
        guard.chmod(0o755)
        self.env = dict(os.environ, CODE=str(SOURCE), FM_HOME=str(self.home),
                        STATE=str(self.home / "state"), QUERY=str(self.query),
                        FM_STATE_OVERRIDE=str(self.home / "state"),
                        FM_DATA_OVERRIDE=str(self.home / "data"),
                        FM_CONFIG_OVERRIDE=str(self.home / "config"),
                        FM_CREW_STATE_BIN=str(self.crew), ROOT_LIVE="alive", CHILD_LIVE="alive",
                        CHILD_CURRENT="state: working · source: pane · harness busy",
                        FM_GATE_REFUSE_BYPASS="1")

    def write_query(self):
        self.query.write_text(json.dumps(self.record))

    def run_bash(self, body, *, source="fm-task-group-state.sh", env=None):
        script = f'. "$CODE/bin/{source}"\n' + STUBS + "\n" + body
        result = subprocess.run(["bash", "-c", script], env=env or self.env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def current(self):
        return self.run_bash('fm_task_group_current "$FM_HOME" root "$STATE"; printf "%s|%s" "$FM_TASK_GROUP_CLASS" "$FM_TASK_GROUP_DETAIL"')

    def test_active_child_is_explicit_waiting(self):
        self.assertTrue(self.current().startswith("waiting|waiting for active component child"))

    def test_unknown_or_dead_root_or_child_is_attention(self):
        for key in ("ROOT_LIVE", "CHILD_LIVE"):
            for value in ("unknown", "dead", "missing"):
                with self.subTest(key=key, value=value):
                    self.env[key] = value
                    self.assertTrue(self.current().startswith("group-attention|"))
            self.env[key] = "alive"

    def test_status_only_or_failed_child_is_not_healthy_waiting(self):
        for state, source in (("working", "status-log"), ("failed", "status-log"),
                              ("blocked", "status-log"), ("unknown", "pane"), ("done", "status-log")):
            self.env["CHILD_CURRENT"] = f"state: {state} · source: {source} · fixture"
            self.assertTrue(self.current().startswith("group-attention|"))

    def test_generation_change_or_missing_child_is_attention(self):
        self.record["child_generation"] = "old-generation"
        self.write_query()
        self.assertTrue(self.current().startswith("group-attention|"))
        (self.home / "state/child.meta").unlink()
        self.assertTrue(self.current().startswith("group-attention|"))

    def test_result_ready_is_not_outer_done_or_cleanup_permission(self):
        self.record["result_ready"] = True
        self.write_query()
        self.assertTrue(self.current().startswith("group-ready|"))
        out = self.run_bash('if fm_task_group_guard "$FM_HOME" root "$STATE" teardown; then exit 9; fi; echo held')
        self.assertEqual(out, "held")

    def test_gather_ack_restores_root_lifecycle(self):
        self.assertEqual(self.run_bash('fm_task_group_event_scoped "$FM_HOME" root "$STATE"; echo scoped'), "scoped")
        self.record.update(pending=False, result_ready=True, cleanup_allowed=True)
        self.write_query()
        out = self.run_bash('fm_task_group_guard "$FM_HOME" root "$STATE" teardown; if fm_task_group_current "$FM_HOME" root "$STATE"; then exit 9; fi; if fm_task_group_event_scoped "$FM_HOME" root "$STATE"; then exit 10; fi; echo ordinary')
        self.assertEqual(out, "ordinary")

    def test_component_result_has_separate_disposition(self):
        self.record.update(component=True, result_ready=True)
        self.write_query()
        self.assertTrue(self.current().startswith("component-ready|"))
        out = self.run_bash('if fm_task_group_guard "$FM_HOME" root "$STATE" promote; then exit 9; fi; echo refused')
        self.assertEqual(out, "refused")

    def test_malformed_or_disappeared_binding_fails_closed(self):
        for value in ('{}', '{"attached":false,"component":false,"pending":false,"cleanup_allowed":true}',
                      '{"attached":true,"component":false,"pending":true,"cleanup_allowed":true}', 'not json'):
            self.query.write_text(value)
            self.assertTrue(self.current().startswith("group-attention|"))
            self.assertEqual(self.run_bash('if fm_task_group_guard "$FM_HOME" root "$STATE" teardown; then exit 9; fi; echo refused'), "refused")

    def test_unbound_tasks_do_not_query_controller(self):
        (self.home / "data/root/task-group").rmdir()
        self.query.unlink()
        self.assertEqual(self.run_bash('fm_task_group_guard "$FM_HOME" root "$STATE" teardown; if fm_task_group_current "$FM_HOME" root "$STATE"; then exit 9; fi; echo ordinary'), "ordinary")

    def test_watcher_waiting_and_unknown_transition(self):
        body = r'''
wake() { printf 'wake:%s\n' "$1"; }
fm_wake_append() { printf '%s\n' "$*" >> "$STATE/queued"; }
task_group_watch_check lab:root root
[ ! -e "$STATE/queued" ] || exit 8
CHILD_LIVE=unknown
task_group_watch_check lab:root root
task_group_watch_check lab:root root
[ "$(wc -l < "$STATE/queued")" -eq 1 ] || exit 9
cat "$STATE/queued"
'''
        out = self.run_bash(body, source="fm-watch.sh")
        self.assertIn("group-attention", out)
        self.assertNotIn("possible wedge", out)

    def test_away_classifier_uses_same_wait_and_attention(self):
        body = r'''
window_to_task() { printf root; }
classify_stale lab:root "$STATE"; printf '\n'
CHILD_LIVE=unknown
classify_stale lab:root "$STATE"
'''
        out = self.run_bash(body, source="fm-supervise-daemon.sh")
        self.assertIn("self|waiting:", out)
        self.assertIn("escalate|group-attention:", out)

    def test_real_lifecycle_entrypoints_refuse_before_delivery_or_cleanup(self):
        env = dict(self.env, FM_ROOT_OVERRIDE=str(self.home / "tools"))
        body = r'''
export -f python3
if bash "$CODE/bin/fm-promote.sh" root --mode local-only --yolo off > "$STATE/promote.out" 2>&1; then exit 8; fi
grep -q 'Stage 1 task-group' "$STATE/promote.out" || { cat "$STATE/promote.out"; exit 9; }
if bash "$CODE/bin/fm-teardown.sh" root --force > "$STATE/teardown.out" 2>&1; then exit 10; fi
grep -q 'ungathered or uncertain' "$STATE/teardown.out" || { cat "$STATE/teardown.out"; exit 11; }
[ -f "$STATE/root.meta" ] || exit 12
[ ! -f "$FM_HOME/data/root/ship-instructions.md" ] || exit 13
echo preserved
'''
        self.assertEqual(self.run_bash(body, env=env), "preserved")

    def test_result_notice_deduplicates_lost_reply_and_handled_record(self):
        body = r'''
. "$CODE/bin/fm-wake-lib.sh"
. "$CODE/bin/fm-task-inbox-lib.sh"
''' + STUBS + r'''
fm_task_inbox_ring() { return 2; } # Lost doorbell is not lost durable admission.
digest=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
first=$(fm_task_group_notify "$FM_HOME" root s1 request-1 "$digest") || exit 8
second=$(fm_task_group_notify "$FM_HOME" root s1 request-1 "$digest") || exit 9
[ "$first" = "$second" ] || exit 10
mv "$first" "$STATE/root.inbox/handled/"
third=$(fm_task_group_notify "$FM_HOME" root s1 request-1 "$digest") || exit 11
[ "$third" = "$STATE/root.inbox/handled/${first##*/}" ] || exit 12
[ "$(find "$STATE/root.inbox" -name '*.msg' | wc -l)" -eq 1 ] || exit 13
if fm_task_group_notify "$FM_HOME" root old-generation request-2 "$digest"; then exit 14; fi
[ "$(find "$STATE/root.inbox" -name '*.msg' | wc -l)" -eq 1 ] || exit 15
echo one-durable-message
'''
        self.assertEqual(self.run_bash(body), "one-durable-message")


if __name__ == "__main__":
    unittest.main()
