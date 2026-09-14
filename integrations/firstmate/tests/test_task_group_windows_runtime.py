"""Native Windows boundary tests; no Herdr process, harness or auth is used.

Real Git Bash, native Python, Git worktrees and original FirstMate lock/inbox
owners are exercised. Only fm-spawn and the backend inbox doorbell are fixtures.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROTOTYPE = Path(__file__).resolve().parents[1]
REPOSITORY = next((parent for parent in PROTOTYPE.parents
                   if (parent / ".sources/firstmate/bin").is_dir()), PROTOTYPE.parents[1])
BIN = PROTOTYPE / "overlay/bin"
SOURCE = Path(os.environ.get("FIRSTMATE_TEST_SOURCE", REPOSITORY / ".sources/firstmate"))
sys.path.insert(0, str(BIN))
from fm_task_group_runtime import Runtime, RuntimeBoundaryError

GIT_BASH = os.environ.get("FIRSTMATE_WINDOWS_TEST_BASH", "C:/Program Files/Git/usr/bin/bash.exe")

SPAWN_FIXTURE = r'''import json,os,subprocess,sys
from pathlib import Path
from fm_task_group import TaskGroups
from fm_task_group_launch import launch_check,launch_meta
from fm_task_group_runtime import runtime
r=runtime()
h=r.native(os.environ['FM_HOME'])
code=Path(__file__).resolve().parent.parent
owner=TaskGroups(h,code)
child=sys.argv[1]
project=r.native(sys.argv[2])
parent='root'
record=owner.request(parent)
proof={'child':child,'owner':os.environ['FM_TASK_GROUP_LOCK_OWNER'],
       'control_pid':(h/'state/.control-root.lock/pid').read_text().strip(),
       'meta_pid':(h/'state/.meta-root.lock/pid').read_text().strip(),
       'accepted_state':record['state']}
with (h/'spawn-calls.jsonl').open('a',encoding='utf-8') as trace:
    trace.write(json.dumps(proof)+'\n')
assert proof['owner']==proof['control_pid']==proof['meta_pid']
if os.environ.get('WINDOWS_FIXTURE_SPAWN_EXIT'):
    raise SystemExit(int(os.environ['WINDOWS_FIXTURE_SPAWN_EXIT']))
launch_check(owner,child,'scout','herdr','codex',project)
worktree=h.parent/(child+' workspace')
subprocess.run(['git','-C',str(project),'worktree','add','--detach',str(worktree),record['input_commit']],check=True,capture_output=True)
launch_check(owner,child,'scout','herdr','codex',project,worktree)
tasktmp=h.parent/(child+' report tmp')
tasktmp.mkdir()
meta=dict(line.split('=',1) for line in launch_meta(owner,child).splitlines())
meta.update(endpoint_task_id=child,spawn_gen='child.1',backend='herdr',kind='scout',harness='codex',
            model='default',effort='default',project=r.shell(project),worktree=r.shell(worktree),
            tasktmp=r.shell(tasktmp),herdr_session='fm-lab-fixture',herdr_workspace_id='w-child',
            herdr_tab_id='t-child',herdr_pane_id='p-child',window='fm-lab-fixture:p-child')
(h/'state'/(child+'.meta')).write_text(''.join(k+'='+v+'\n' for k,v in meta.items()),encoding='utf-8',newline='')
'''


@unittest.skipUnless(os.name == "nt" and Path(GIT_BASH).is_file(), "requires explicit native Windows Git Bash")
class WindowsRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = Runtime(GIT_BASH, sys.executable)
        self.temporary = tempfile.TemporaryDirectory(prefix="fm native ' café-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.code, self.home = self.base / "code", self.base / "owning home"
        shutil.copytree(SOURCE / "bin", self.code / "bin")
        for path in BIN.iterdir():
            if path.is_file() and path.suffix in (".py", ".sh"):
                shutil.copyfile(path, self.code / "bin" / path.name)
        for name in ("state", "data", "config"):
            (self.home / name).mkdir(parents=True)
        self.environment = {key: value for key, value in os.environ.items()
                            if not key.startswith(("FM_", "HERDR_", "MSYS2_"))}
        self.environment.update(FM_TASK_GROUP_BASH=GIT_BASH, FM_TASK_GROUP_PYTHON=sys.executable,
                                GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
                                GIT_CONFIG_NOSYSTEM="1", PYTHONDONTWRITEBYTECODE="1")
        self.project = self.base / "project ' café"
        self.project.mkdir()
        for args in (("init", "-q"), ("config", "user.name", "Fixture"),
                     ("config", "user.email", "fixture@example.invalid")):
            self.git(*args)
        (self.project / "facts.txt").write_text("first fact\nsecond fact\n", encoding="utf-8")
        self.git("add", "facts.txt")
        self.git("commit", "-qm", "fixture")
        self.package = self.base / "package snapshot input"
        self.package.mkdir()
        for manifest in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
            path = self.package / manifest
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"name": "orchflows-firstmate", "version": "fixture"}))
        (self.package / "scripts").mkdir()
        shutil.copyfile(REPOSITORY / "packages/orchflows-firstmate/scripts/firstmate.py", self.package / "scripts/firstmate.py")
        (self.package / "guide.md").write_text("Read source and report evidence.")
        self.call("attach", "root", "--project", str(self.project), "--package", str(self.package))
        self.meta = {"endpoint_task_id": "root", "spawn_gen": "root.1", "backend": "herdr", "kind": "scout",
                     "harness": "codex", "model": "default", "effort": "default", "task_group_role": "root",
                     "task_group_epoch": "1", "project": self.runtime.shell(self.project),
                     "worktree": self.runtime.shell(self.project), "tasktmp": self.runtime.shell(self.base),
                     "herdr_session": "fm-lab-fixture", "herdr_workspace_id": "w-root",
                     "herdr_tab_id": "t-root", "herdr_pane_id": "p-root", "window": "fm-lab-fixture:p-root"}
        self.save_meta()
        self.request = self.base / "request ' café.json"
        self.request.write_text(json.dumps({"request_id": "facts", "assignment": "Read facts.txt and report both facts."}), encoding="utf-8")
        (self.code / "bin/spawn-fixture.py").write_text(SPAWN_FIXTURE, encoding="utf-8", newline="")
        (self.code / "bin/fm-spawn.sh").write_text('#!/usr/bin/env bash\n. "$FM_ROOT_OVERRIDE/bin/fm-task-group-runtime.sh"\nfm_task_group_python "$FM_ROOT_OVERRIDE/bin/spawn-fixture.py" "$@"\n', encoding="utf-8", newline="")
        # Keep the real inbox admission/locking implementation. Substitute only
        # its backend signal so no test can contact a Herdr session.
        with (self.code / "bin/fm-task-inbox-lib.sh").open("a", encoding="utf-8", newline="") as target:
            target.write('\nfm_task_inbox_ring() { printf "%s\\n" "$*" > "$FM_HOME/fixture-doorbell.txt"; return 0; }\n')

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.project), *args], env=self.environment,
                              capture_output=True, check=True, encoding="utf-8").stdout.strip()

    def save_meta(self):
        (self.home / "state/root.meta").write_text("".join(f"{key}={value}\n" for key, value in self.meta.items()), encoding="utf-8", newline="")

    def call(self, *args, expected=0, environment=None):
        result = subprocess.run([sys.executable, "-B", str(self.code / "bin/fm-task-group.py"),
                                 "--home", str(self.home), *args], env=environment or self.environment,
                                capture_output=True, encoding="utf-8", timeout=90)
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return json.loads(result.stdout or result.stderr)

    def submit(self, **kwargs):
        return self.call("submit", "root", "--generation", self.meta["spawn_gen"], "--request", str(self.request), **kwargs)

    def calls(self):
        path = self.home / "spawn-calls.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []

    def test_native_public_submit_proves_custody_and_preserves_posix_metadata(self):
        client = self.home / "data/root/task-group/package/scripts/firstmate.py"
        output = subprocess.run([sys.executable, "-B", str(client), "--firstmate-root", str(self.code),
                                 "--home", str(self.home), "--root", "root", "--generation", "root.1",
                                 "--timeout", "90", "submit", "--request", str(self.request)],
                                env=self.environment, capture_output=True, encoding="utf-8", timeout=90)
        self.assertEqual(output.returncode, 0, output.stderr or output.stdout)
        result = json.loads(output.stdout)
        self.assertEqual(result["request"]["state"], "launched", result["request"])
        proof = self.calls()
        self.assertEqual(len(proof), 1)
        self.assertEqual(proof[0]["owner"], proof[0]["control_pid"])
        self.assertEqual(proof[0]["owner"], proof[0]["meta_pid"])
        self.assertEqual(proof[0]["accepted_state"], "launching")
        self.assertEqual(result["request"]["launch_meta"]["project"], self.meta["project"])
        self.assertTrue(result["request"]["launch_meta"]["worktree"].startswith("/"))
        self.assertEqual(Path(result["attachment"]["project"]), self.project)
        self.assertEqual(list((self.home / "state").glob("*.lock")), [])
        replay = self.submit()
        self.assertEqual(replay["request"]["child"], result["request"]["child"])
        self.assertEqual(len(self.calls()), 1)

    def test_failure_keeps_uncertain_request_and_never_relaunches(self):
        environment = dict(self.environment, WINDOWS_FIXTURE_SPAWN_EXIT="9")
        first = self.submit(environment=environment)
        self.assertEqual(first["request"]["state"], "uncertain")
        self.assertEqual(len(self.calls()), 1)
        replay = self.submit()
        self.assertEqual(replay["request"]["state"], "uncertain")
        self.assertEqual(replay["request"]["child"], first["request"]["child"])
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(list((self.home / "state").glob("*.lock")), [])

    def test_complete_notify_and_gather_use_real_inbox_owner(self):
        result = self.submit()
        self.assertEqual(result["request"]["state"], "launched", result["request"])
        child = result["request"]["child"]
        report = self.runtime.native(result["request"]["launch_meta"]["tasktmp"]) / "evidence ' café.md"
        report.write_text("facts.txt:1 and facts.txt:2 contain the two facts.\n", encoding="utf-8")
        # Accept the existing raw MSYS tasktmp/report spelling too.
        complete = self.call("complete", child, "--generation", "child.1", "--report", self.runtime.shell(report))
        self.assertEqual(complete["request"]["state"], "complete")
        self.assertFalse(complete["request"]["notification_pending"], complete["request"])
        self.assertTrue((self.home / "fixture-doorbell.txt").is_file())
        self.assertTrue(self.call("waiting", "root")["pending"])
        acknowledged = self.call("gather", "root", "--generation", "root.1")
        self.assertTrue(acknowledged["request"]["gathered"])
        self.assertTrue(self.call("waiting", child)["cleanup_allowed"])
        self.assertEqual(Path(complete["report_path"]).read_bytes(), report.read_bytes())

    def test_missing_runtime_and_wsl_bash_rejected_before_admission(self):
        environment = dict(self.environment)
        environment.pop("FM_TASK_GROUP_BASH")
        error = self.submit(environment=environment, expected=2)
        self.assertIn("explicit FM_TASK_GROUP_BASH", error["error"])
        bad = dict(self.environment, FM_TASK_GROUP_BASH="C:/Windows/System32/bash.exe")
        self.submit(environment=bad, expected=2)
        self.assertFalse((self.home / "data/root/task-group/request.json").exists())
        self.assertEqual(self.calls(), [])

    def test_forged_lock_environment_and_stale_parent_cannot_admit(self):
        forged = dict(self.environment, FM_TASK_GROUP_LOCK_OWNER=str(os.getpid()),
                      FM_TASK_GROUP_LOCK_ROOT="root", FM_TASK_GROUP_LOCK_HOME=self.runtime.shell(self.home))
        error = self.call("internal-submit", "root", "--generation", "root.1", "--request", str(self.request), environment=forged, expected=2)
        self.assertIn("lock custody", error["error"])
        # Public stale generation is denied by the actual FirstMate shell owner.
        result = subprocess.run([sys.executable, "-B", str(self.code / "bin/fm-task-group.py"),
                                 "--home", str(self.home), "submit", "root", "--generation", "stale",
                                 "--request", str(self.request)], env=self.environment, capture_output=True,
                                encoding="utf-8", timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stale", result.stderr)
        self.assertFalse((self.home / "data/root/task-group/request.json").exists())
        self.assertEqual(self.calls(), [])

    def test_typed_path_roundtrip_and_runtime_identity_are_pinned(self):
        path = self.project / "future file ' café.md"
        self.assertEqual(self.runtime.native(self.runtime.shell(path)), path)
        attachment = json.loads((self.home / "data/root/task-group/attachment.json").read_text())
        self.assertEqual(attachment["runtime"], self.runtime.identity)
        attachment["runtime"]["executables"]["python"]["sha256"] = "0" * 64
        (self.home / "data/root/task-group/attachment.json").write_text(json.dumps(attachment))
        error = self.call("status", "root", "--generation", "root.1", expected=2)
        self.assertIn("runtime differs", error["error"])

    def test_actual_unrelated_live_lock_owner_blocks_admission_and_forged_custody(self):
        holder = self.base / "hold-root-locks.sh"
        holder.write_text('''#!/usr/bin/env bash
set -euo pipefail
. "$FM_ROOT_OVERRIDE/bin/fm-wake-lib.sh"
control="$FM_HOME/state/.control-root.lock"
meta=$(fm_meta_lock_path "$FM_HOME/state/root.meta")
fm_lock_try_acquire "$control"
fm_lock_try_acquire "$meta"
trap 'fm_lock_release "$meta"; fm_lock_release "$control"' EXIT
fm_current_pid owner
printf '%s\\n' "$owner"
IFS= read -r finish
''', encoding="utf-8", newline="")
        environment = self.runtime.environment(self.environment, home=self.home, code_root=self.code)
        process = subprocess.Popen([self.runtime.bash, "--noprofile", "--norc", self.runtime.shell(holder)],
                                   env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, encoding="utf-8")
        try:
            owner = process.stdout.readline().strip()
            self.assertTrue(owner.isdecimal(), owner)
            forged = dict(self.environment, FM_TASK_GROUP_LOCK_OWNER=owner,
                          FM_TASK_GROUP_LOCK_ROOT="root", FM_TASK_GROUP_LOCK_HOME=self.runtime.shell(self.home))
            rejected = self.call("internal-submit", "root", "--generation", "root.1", "--request", str(self.request),
                                 environment=forged, expected=2)
            self.assertIn("lock custody", rejected["error"])
            outcome = subprocess.run([sys.executable, "-B", str(self.code / "bin/fm-task-group.py"),
                                      "--home", str(self.home), "submit", "root", "--generation", "root.1",
                                      "--request", str(self.request)], env=self.environment, capture_output=True,
                                     encoding="utf-8", timeout=30)
            self.assertNotEqual(outcome.returncode, 0)
            self.assertIn("parent lifecycle operation", outcome.stderr)
            self.assertFalse((self.home / "data/root/task-group/request.json").exists())
            self.assertEqual(self.calls(), [])
        finally:
            process.communicate("release\n", timeout=10)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(list((self.home / "state").glob("*.lock")), [])


if __name__ == "__main__":
    unittest.main()
