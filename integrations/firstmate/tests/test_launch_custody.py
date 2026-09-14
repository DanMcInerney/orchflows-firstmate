"""Real controller/parent locks/watcher owner; only child spawn and pane liveness are fixtures."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

SOURCE = Path(os.environ.get("FM_STAGE1_FIRSTMATE_ROOT", Path(__file__).resolve().parents[3] / ".scratch/stage1/prepared-repaired"))

SPAWN = r'''#!/usr/bin/env python3
import json,os,subprocess,sys,time
from pathlib import Path
home=Path(os.environ["FM_HOME"])
child=sys.argv[1]; project=Path(sys.argv[2])
with (home/"spawn-count").open("a") as f: f.write(child+"\n")
(home/"spawn-entered").touch()
while not (home/"release-spawn").exists(): time.sleep(.02)
if (home/"fail-spawn").exists(): sys.exit(7)
sys.path.insert(0,str(Path(__file__).parent))
from fm_task_group import TaskGroups
from fm_task_group_launch import launch_meta
owner=TaskGroups(home)
worktree=home/"component-worktree"; tasktmp=home/"component-tmp"
subprocess.run(["git","-C",str(project),"worktree","add","--detach",str(worktree)],check=True,capture_output=True)
tasktmp.mkdir()
record=owner.request("root")
meta=dict(endpoint_task_id=child,spawn_gen="s2.123",backend="herdr",kind="scout",harness="codex",model="default",effort="default",project=str(project),worktree=str(worktree),tasktmp=str(tasktmp),herdr_session="lab-fixture",herdr_workspace_id="w1",herdr_tab_id="t1",herdr_pane_id="p2",window="lab-fixture:w1:p2")
meta.update(dict(line.split("=",1) for line in launch_meta(owner,child).splitlines()))
(home/"state"/(child+".meta")).write_text("".join(k+"="+v+"\n" for k,v in meta.items()))
'''

@unittest.skipUnless(sys.platform.startswith("linux"), "Positive launch custody is Linux-only")
class LaunchCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="fm-launch-custody-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.code = self.base / "code"
        shutil.copytree(SOURCE / "bin", self.code / "bin")
        (self.code / "bin/fm-spawn.sh").write_text(SPAWN)
        (self.code / "bin/fm-spawn.sh").chmod(0o755)
        self.home = self.base / "home"
        for part in ("state", "data", "config"):
            (self.home / part).mkdir(parents=True)
        self.project = self.base / "project"
        self.project.mkdir()
        def git(*args):
            subprocess.run(["git", "-C", str(self.project), *args], check=True, capture_output=True)
        git("init", "-q"); git("config", "user.name", "Fixture"); git("config", "user.email", "fixture@example.invalid")
        (self.project / "input.txt").write_text("inspect me\n")
        git("add", "."); git("commit", "-qm", "fixture")
        self.package = self.base / "package"
        self.package.mkdir()
        (self.package / "plugin.json").write_text('{"name":"orchflows-firstmate"}')
        self.env = {k:v for k,v in os.environ.items() if not k.startswith(("FM_", "HERDR_"))}
        self.env.update(FM_HOME=str(self.home), FM_ROOT_OVERRIDE=str(self.code), CODE=str(self.code),
                        STATE=str(self.home / "state"), CHILD_CURRENT="state: working · source: pane · harness busy", ROOT_LIVE="alive")
        self.cli("attach", "root", "--package", str(self.package), "--project", str(self.project), check=True)
        meta=dict(endpoint_task_id="root",spawn_gen="s1.123",backend="herdr",kind="scout",harness="codex",model="default",effort="default",project=str(self.project),worktree=str(self.project),herdr_session="lab-fixture",herdr_workspace_id="w1",herdr_tab_id="t1",herdr_pane_id="p1",window="lab-fixture:w1:p1",task_group_role="root",task_group_epoch="1")
        self.meta = self.home / "state/root.meta"
        self.meta.write_text("".join(k+"="+v+"\n" for k,v in meta.items()))
        self.request = self.home / "request-input.json"
        self.request.write_text('{"request_id":"find-facts","assignment":"Read input.txt"}')
        self.record_path = self.home / "data/root/task-group/request.json"
        self.crew = self.home / "crew-state"
        self.crew.write_text('#!/usr/bin/env bash\nprintf "%s\n" "$CHILD_CURRENT"\n')
        self.crew.chmod(0o755)
        self.env["FM_CREW_STATE_BIN"] = str(self.crew)
        self.process = None
        self.addCleanup(self.stop)

    def cli(self, *args, check=False):
        return subprocess.run([sys.executable, "-B", str(self.code / "bin/fm-task-group.py"), "--home", str(self.home), *args], env=self.env, capture_output=True, text=True, timeout=20, check=check)

    def start(self):
        self.process = subprocess.Popen([sys.executable, "-B", str(self.code / "bin/fm-task-group.py"), "--home", str(self.home), "submit", "root", "--generation", "s1.123", "--request", str(self.request)], env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        deadline = time.monotonic()+10
        while not (self.home / "spawn-entered").exists():
            if self.process.poll() is not None:
                self.fail(str(self.process.communicate()))
            if time.monotonic()>deadline: self.fail("spawn fixture did not enter")
            time.sleep(.02)
        return self.record()

    def stop(self):
        if self.process is not None:
            try: os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            self.process.communicate(timeout=5)
            self.process = None

    def record(self):
        return json.loads(self.record_path.read_text())

    def write_record(self, value):
        self.record_path.write_text(json.dumps(value))

    def projection(self, watch=False):
        body = r'''
. "$CODE/bin/fm-watch.sh"
fm_backend_validate_task_endpoint() {
  [ -f "$1" ] || return 1
  FM_BACKEND_VALIDATED_BACKEND=herdr
  FM_BACKEND_VALIDATED_TARGET=$2
}
fm_backend_agent_state() { printf "%s" "$ROOT_LIVE"; }
wake() { printf "wake:%s\n" "$1"; }
fm_wake_append() { printf "%s\n" "$*" >> "$STATE/queued"; }
'''
        body += ('task_group_watch_check lab:root root\n' if watch else 'fm_task_group_current "$FM_HOME" root "$STATE"\nprintf "%s|%s" "$FM_TASK_GROUP_CLASS" "$FM_TASK_GROUP_DETAIL"\n')
        result = subprocess.run(["bash", "-c", body], env=self.env, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        return result.stdout.strip()

    def test_live_launch_before_metadata_then_launched_and_unknown_worker(self):
        record = self.start()
        self.assertEqual(record["state"], "launching")
        self.assertNotIn("child_generation", record)
        self.assertFalse((self.home / "state" / (record["child"]+".meta")).exists())
        self.assertTrue(self.projection().startswith("waiting|waiting for FirstMate component launch"))
        self.projection(watch=True)
        self.assertFalse((self.home / "state/queued").exists())
        self.env["ROOT_LIVE"] = "unknown"
        self.assertTrue(self.projection().startswith("group-attention|"))
        self.env["ROOT_LIVE"] = "alive"
        (self.home / "release-spawn").touch()
        output, error = self.process.communicate(timeout=20)
        self.assertEqual(self.process.returncode, 0, error)
        self.assertEqual(json.loads(output)["request"]["state"], "launched")
        self.assertTrue(self.projection().startswith("waiting|waiting for active component"))
        self.env["CHILD_CURRENT"] = "state: unknown · source: none · no activity"
        self.projection(watch=True); self.projection(watch=True)
        queued=(self.home / "state/queued").read_text().splitlines()
        self.assertEqual(len(queued), 1)
        self.assertIn("group-attention", queued[0])

    def test_missing_changed_or_unrelated_live_lock_owner_is_attention(self):
        record = self.start()
        custody = record["launch_custody"]
        for key in ("control_dir", "meta_dir"):
            pid = Path(custody[key]) / "pid"
            old = pid.read_text()
            try:
                pid.write_text(str(os.getpid()))
                self.assertTrue(self.projection().startswith("group-attention|"))
            finally: pid.write_text(old)
        lock = self.home / "state/.control-root.lock"
        target = os.readlink(lock)
        lock.unlink()
        try: self.assertTrue(self.projection().startswith("group-attention|"))
        finally: lock.symlink_to(target)
        forged = json.loads(json.dumps(record))
        forged["launch_custody"]["owner_identity"] = "a"*64
        self.write_record(forged)
        self.assertTrue(self.projection().startswith("group-attention|"))
        self.write_record(record)
        self.assertTrue(self.projection().startswith("waiting|"))

    def test_dead_lock_owner_and_old_missing_custody_record_are_attention(self):
        record = self.start()
        previous = dict(record)
        previous.pop("launch_custody")
        self.write_record(previous)
        self.assertTrue(self.projection().startswith("group-attention|"))
        self.write_record(record)
        os.kill(int(record["launch_custody"]["owner"]), signal.SIGKILL)
        self.assertTrue(self.projection().startswith("group-attention|"))
        self.assertEqual(self.record()["state"], "launching")

    def test_forged_live_controller_with_matching_identity_fails_ancestry(self):
        record = self.start()
        command='. "$CODE/bin/fm-wake-lib.sh"; fm_pid_identity "$CHECK_PID"'
        identity = subprocess.run(["bash", "-c", command], env=dict(self.env, CHECK_PID=str(os.getpid())), check=True, capture_output=True, text=True).stdout.rstrip("\n")
        record["launch_custody"].update(controller=str(os.getpid()),controller_identity=hashlib.sha256(identity.encode()).hexdigest())
        self.write_record(record)
        self.assertTrue(self.projection().startswith("group-attention|"))

    def test_dead_controller_or_new_parent_generation_is_attention(self):
        record = self.start()
        text = self.meta.read_text()
        self.meta.write_text(text.replace("spawn_gen=s1.123", "spawn_gen=s3.456"))
        self.assertTrue(self.projection().startswith("group-attention|"))
        self.meta.write_text(text)
        os.kill(int(record["launch_custody"]["controller"]), signal.SIGKILL)
        self.assertTrue(self.projection().startswith("group-attention|"))
        self.assertEqual(self.record()["state"], "launching")

    def test_uncertain_launch_never_borrows_custody_or_redispatches(self):
        record = self.start()
        changed = dict(record, state="uncertain", launch_error="fixture interrupted")
        self.write_record(changed)
        self.assertTrue(self.projection().startswith("group-attention|"))
        self.write_record(record)
        (self.home / "fail-spawn").touch(); (self.home / "release-spawn").touch()
        output, error = self.process.communicate(timeout=20)
        self.assertEqual(self.process.returncode, 0, error)
        self.assertEqual(json.loads(output)["request"]["state"], "uncertain")
        self.assertTrue(self.projection().startswith("group-attention|"))
        replay=self.cli("submit", "root", "--generation", "s1.123", "--request", str(self.request), check=True)
        self.assertEqual(json.loads(replay.stdout)["request"]["child"], record["child"])
        self.assertEqual((self.home / "spawn-count").read_text().splitlines(), [record["child"]])

if __name__ == "__main__": unittest.main()
