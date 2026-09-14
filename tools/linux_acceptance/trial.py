"""One readonly component observed through ordinary FirstMate lifecycle owners."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time

from .evidence import assess, read_order
from .runtime import Runtime, metadata, process_identity


class Trial(Runtime):
    def __init__(self, *args):
        super().__init__(*args)
        self.watcher = None
        self.watcher_identity = None
        self.trace_thread = None

    def prepare_root(self, project, session):
        home = self.namespace / "claude-fm"
        for name in ("data", "state", "config", "projects"):
            (home / name).mkdir(parents=True)
        self.write(home / "config/claude-permission-mode", "auto\n")
        self.write(home / "config/herdr-presentation-spaces", "off\n")
        root = "accept-" + self.namespace.name.removeprefix("a-")
        env = {**self.env, "FM_HOME": str(home), "HERDR_SESSION": session}
        self.owner_home, self.root, self.worker_env = home, root, env
        self.active_homes.append((home, env))
        self.run(["tasks-axi", "add", root, "Inspect fixture through one readonly component",
                  "--kind", "scout", "--repo", "acceptance-fixture", "--file", home / "data/backlog.md"],
                 env=env, cwd=home)
        self.owner("fm-brief.sh", root, "acceptance-fixture", "--scout", env=env)
        primitive = self.args.primitive
        request_id = "inspect-fixture-" + primitive.lower() + "-v1"
        assignment = (
            f"Perform a read-only {primitive} of the two Python source files in your fixture worktree. "
            f"Begin with one foreground shell sleep of {self.args.component_delay} seconds, using a timeout "
            "of at least 420000 ms, so FirstMate can observe the active component. After it finishes, "
            "establish directly from source what total_units([]) returns in stock.py and what "
            "normalize_code(' ab-7 ') returns in labels.py. Cite file and line references and explain both. "
            "Do not edit project/package files, dependencies or Git state; do not delegate. Write your report "
            "only under your recorded tasktmp and complete using the FirstMate component completion contract."
        )
        if primitive == "Review":
            assignment += " This is an explicitly authorized independent source audit, not a code-making assignment."
        primitive_args = " --primitive Review" if primitive == "Review" else ""
        spec = (
            f"Use exactly one attached Orchflows {primitive} through FirstMate and incorporate its retained result. "
            f"Read the retained skills/orch-{primitive.lower()}/SKILL.md. Every submit/status/gather must use "
            f"the retained scripts/firstmate.py client{primitive_args}, attachment.package_path and your current "
            "spawn_gen; never invoke controller submit/status/gather directly. Write your request JSON only "
            f"under your tasktmp with request_id={request_id} and assignment equal to this exact text:\n\n"
            + json.dumps(assignment) + "\n\n"
            "Submit the identical JSON twice, each as one standalone literal Python client Bash invocation, and record both returned child identities. While pending, use "
            "client status and short foreground sleeps. If relaunched, reconcile the existing request under "
            "your new generation; never create another request or child. Before the FIRST gather, use native "
            "Read to read the ENTIRE retained report.md AND result.json with no offset/limit. Then gather in "
            "one standalone Bash invocation of literal absolute python3 -B retained/scripts/firstmate.py "
            "with literal arguments, this root and current generation. Do not use shell variables, aliases, "
            "compound commands or wrappers for gather. A notification does not authorize acknowledging an "
            "unread report. Produce the ordinary root scout report with both findings, source references, "
            "root/child/request identities and replay observation. Do not edit project/package/Git state, "
            "open a PR, merge, inspect credentials/harness history or use native delegation. This authorizes "
            "only your metadata/tasktmp/report/status, retained package, FirstMate client/owners/completion "
            "policy and fixture worktree. Follow the normal scout captain-hold completion gate, --none only "
            "when there are no unresolved captain decisions, then append done."
        )
        enabled = getattr(self.args, "enabled", False)
        custom = getattr(self.args, "custom_workflow", False)
        spec = spec.replace(
            f"client{primitive_args}, attachment.package_path and your current spawn_gen",
            "client using only the launch-provided ORCHFLOWS_FIRSTMATE_CONTEXT")
        spec = spec.replace("with literal arguments, this root and current generation.",
                            "with only the literal gather operation; no authority flags.")
        library = None
        if custom:
            library = self.namespace / "custom-library"
            skill = library / "skills" / "inspect-facts" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            self.write(library / "plugin.json", json.dumps(
                {"name": "acceptance", "version": "1.0.0", "skills": "./skills/"}))
            self.write(library / "README.md",
                       "Depends on the exact retained orchflows-firstmate core supplied by FirstMate.\n")
            self.write(skill, (
                "---\nname: inspect-facts\ndescription: Inspect fixture facts through one FirstMate primitive.\n---\n\n"
                "Read the admitted primitive skill in the retained core root from the launch catalog. "
                "Use that primitive once for the exact assignment and request ID supplied in the task brief. "
                "Apply core code Make guidance for Work or Review guidance for Review. "
                "Collect the retained result, then deliver the ordinary scout report. "
                "Include the literal receipt marker catalog-fixture-accepted in that report. "
                "No additional agents or repairs.\n"))
            spec = spec.replace(
                f"Read the retained skills/orch-{primitive.lower()}/SKILL.md.",
                "Read and apply the selected acceptance:inspect-facts custom workflow from the launch catalog using native Read.")
        path = home / "data" / root / "brief.md"
        self.write(path, path.read_text().replace("{TASK}", "Inspect the readonly fixture").replace("{FIRSTMATE_SPEC}", spec))
        args = ["python3", "-B", self.candidate / "bin/fm-task-group.py", "--home", home]
        args.extend(["enable"] if enabled else ["attach", root])
        args.extend(["--package", self.package, "--project", project])
        if library:
            args.extend(["--library", library])
        if primitive == "Review":
            args.extend(("--primitive", "Review", "--review-policy", "explicit-audit"))
        attached = self.run(args, env=env, timeout=300)
        self.write(self.out / ("enable.json" if enabled else "attach.json"), attached.stdout)
        self.receipt["entrypoint"] = "enabled-project" if enabled else "explicit-attachment"
        self.receipt["custom_workflow"] = custom
        if library:
            self.write(library / "skills/inspect-facts/SKILL.md",
                       "Source changed after enablement; this text must not replace the retained workflow.\n")
        if enabled and (home / "data" / root / "task-group/attachment.json").exists():
            raise RuntimeError("Enabled fixture attached a task before ordinary spawn")
        self.write(self.out / "root-brief.md", path.read_text())
        self.receipt["primitive"] = primitive
        self.receipt["request_id"] = request_id
        return home, root, env

    def start_watch(self):
        diagnostic = self.namespace / "watch-trace-env.sh"
        self.write(diagnostic, 'case "$0" in */bin/fm-watch.sh) PS4=\'+${EPOCHREALTIME}:${BASHPID}:\'; set -x ;; esac\n')
        reader, writer = os.pipe()
        env = {key: value for key, value in self.worker_env.items() if key != "CLAUDE_CODE_OAUTH_TOKEN"}
        env.update(BASH_ENV=str(diagnostic), BASH_XTRACEFD=str(writer))
        needles = ("task_group_watch_check ", "FM_TASK_GROUP_CLASS=", "FM_TASK_GROUP_DETAIL=",
                   "fm_wake_append ", "wake ", "POLL=", "STALE_ESCALATE_SECS=", "BUSY_TURN_MAX_SECS=")
        def trace():
            with os.fdopen(reader) as stream, (self.out / "watch-execution.trace").open("w") as output:
                for line in stream:
                    if any(needle in line for needle in needles):
                        output.write(self.clean(line))
                        output.flush()
        self.trace_thread = threading.Thread(target=trace, daemon=True)
        self.trace_thread.start()
        with (self.out / "watch-arm.stdout").open("w") as out, (self.out / "watch-arm.stderr").open("w") as err:
            self.watcher = subprocess.Popen(["bash", str(self.candidate / "bin/fm-watch-arm.sh")],
                                           env=env, cwd=self.owner_home, stdout=out, stderr=err,
                                           pass_fds=(writer,))
        os.close(writer)
        self.watcher_identity = process_identity(self.watcher.pid)
        for _ in range(80):
            if self.watcher.poll() is not None:
                raise RuntimeError("Ordinary watcher exited before root launch")
            if "watcher: started" in (self.out / "watch-arm.stdout").read_text():
                return
            time.sleep(0.2)
        raise RuntimeError("Ordinary watcher did not confirm its fresh beacon")

    def request(self):
        path = self.owner_home / "data" / self.root / "task-group/request.json"
        return json.loads(path.read_text()) if path.is_file() else {}

    def select_session(self):
        self.session = self.lab("name", self.args.primitive.lower()).stdout.strip()
        self.validate_session_paths(self.session)

    def run_component(self, project):
        session = self.session
        # Record the selected owned name before provisioning: partial provision
        # failures must still attempt the lab owner's guarded cleanup.
        self.sessions.append(session)
        self.lab("provision", session)
        home, root, env = self.prepare_root(project, session)
        result = {"root": root, "session": session, "watch_samples": [], "started_at": time.time()}
        self.receipt["runs"].append(result)
        self.start_watch()
        spawned = self.owner("fm-spawn.sh", root, project, "--scout", "--backend", "herdr",
                             "--harness", "claude", env=env, timeout=150, check=False)
        result["spawn_exit"] = spawned.returncode
        self.write(self.out / "spawn.log", spawned.stdout + spawned.stderr)
        deadline = time.monotonic() + self.args.timeout
        launched_at = None
        while spawned.returncode == 0 and time.monotonic() < deadline:
            if self.expiry is not None and time.time() > self.expiry - 60:
                raise RuntimeError("Access token reached its stop margin; no refresh attempted")
            request = self.request()
            sample = {"at": time.time(), "request_state": request.get("state"),
                      "gathered": request.get("gathered"), "arm_exit": self.watcher.poll()}
            beat, lock = home / "state/.last-watcher-beat", home / "state/.watch.lock/pid"
            sample["beacon_age_seconds"] = time.time() - beat.stat().st_mtime if beat.exists() else 1000000
            sample["watcher_lock"] = lock.read_text().strip() if lock.is_file() else None
            for role, task in (("root", root), ("child", request.get("child"))):
                if task:
                    current = self.owner("fm-crew-state.sh", task, env=env, timeout=35, check=False)
                    sample[role + "_current"] = current.stdout.strip()
                    sample[role + "_current_exit"] = current.returncode
            result["watch_samples"].append(sample)
            if request.get("state") == "launched" and launched_at is None:
                launched_at = time.monotonic()
            # Re-read the request immediately before replacement. The owner
            # validates generation and is solely responsible for the relaunch.
            if (self.args.restart and "replacement" not in result and launched_at is not None and
                    time.monotonic() - launched_at >= self.args.replace_after and self.request().get("state") == "launched"):
                parent = metadata(home / "state" / (root + ".meta"))
                replaced = self.owner("fm-control.sh", root, "relaunch", "--note",
                    "Resume this exact readonly assignment. Reconcile the retained request using your current "
                    "generation. Reuse the accepted child, read its entire report and result before gather; no new child.",
                    env=env, timeout=150, check=False)
                result["replacement"] = {"exit": replaced.returncode, "child": request.get("child"),
                                         "before_generation": parent.get("spawn_gen"), "at": time.time()}
                self.write(self.out / "replacement.log", replaced.stdout + replaced.stderr)
            # A result may publish while the current-owner calls run. It is a
            # valid final wake, not evidence of a pending-component watcher exit.
            latest = self.request()
            if self.watcher.poll() is not None and latest.get("state") != "complete":
                result["watcher_ended_while_pending"] = True
            status = home / "state" / (root + ".status")
            lines = status.read_text().splitlines() if status.exists() else []
            print(f"Observation: component={latest.get('state')} gathered={latest.get('gathered')} "
                  f"watcher_exit={self.watcher.poll()}", flush=True)
            self.save()
            if (lines and lines[-1].startswith(("done:", "failed:", "blocked:", "needs-decision:"))) or latest.get("state") == "uncertain":
                break
            time.sleep(15)
        self.collect(result, project)
        result["acceptance"] = assess(result, restart=self.args.restart,
                                      minimum_waiting_span=self.args.minimum_waiting_span)
        result["elapsed_seconds"] = round(time.time() - result["started_at"], 3)
        return result["acceptance"]["passed"]

    def collect(self, result, project):
        home, root = self.owner_home, self.root
        request = self.request()
        result["request"] = request
        attachment_path = home / "data" / root / "task-group/attachment.json"
        if attachment_path.exists():
            attachment = json.loads(attachment_path.read_text())
            if getattr(self.args, "enabled", False):
                result["enabled_project"] = True
            result["client_path"] = str(Path(attachment["package_path"]) / "scripts/firstmate.py")
            if getattr(self.args, "custom_workflow", False):
                result["custom_skill_path"] = str(Path(attachment["package_path"]) /
                    "firstmate-libraries/acceptance/skills/inspect-facts/SKILL.md")
        elif getattr(self.args, "enabled", False):
            result["enabled_project"] = False
        metas = {path.stem: metadata(path) for path in (home / "state").glob("*.meta")}
        result["metadata"] = metas
        result["component_count"] = sum(value.get("task_group_role") == "component" for value in metas.values())
        status = home / "state" / (root + ".status")
        result["root_status"] = status.read_text() if status.exists() else ""
        report = home / "data" / root / "report.md"
        text = report.read_text() if report.is_file() else ""
        result["source_findings_present"] = all(term in text for term in ("stock.py", "labels.py", "AB-7", "0"))
        self.write(self.out / "root-report.md", text)
        if getattr(self.args, "custom_workflow", False):
            result["custom_marker_present"] = "catalog-fixture-accepted" in text
        result["input_status"] = self.run(["git", "-C", project, "status", "--porcelain", "--untracked-files=all"]).stdout
        result["input_commit_unchanged"] = self.run(["git", "-C", project, "rev-parse", "HEAD"]).stdout.strip() == self.receipt["input_commit"]
        result["worktree_status"] = {}
        for task, meta in metas.items():
            worktree = Path(meta.get("worktree", "/nonexistent"))
            if worktree.is_dir():
                result["worktree_status"][task] = self.run(["git", "-C", worktree, "status", "--porcelain", "--untracked-files=all"]).stdout
        if request.get("state") == "complete":
            retained = home / "data" / root / "task-group/results" / request["child"]
            value = json.loads((retained / "result.json").read_text())
            digest = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
            report_digest = hashlib.sha256((retained / "report.md").read_bytes()).hexdigest()
            result["retained_integrity_matches"] = (digest == request.get("result_digest") and
                report_digest == value.get("report_digest") and value.get("root") == root and
                value.get("child") == request["child"] and value.get("primitive") == self.args.primitive)
            for name in ("report.md", "result.json"):
                self.write(self.out / ("component-" + name), (retained / name).read_text())
            result["read_order"] = read_order(self.namespace, home, result)

    def cleanup(self):
        try:
            if self.watcher and self.watcher.poll() is None:
                if process_identity(self.watcher.pid) != self.watcher_identity:
                    raise RuntimeError("Watcher arm process identity changed; refused signal")
                self.watcher.terminate()
                self.watcher.wait(timeout=45)
            if self.trace_thread:
                self.trace_thread.join(timeout=10)
        except Exception as error:
            self.receipt["watcher_cleanup_error"] = type(error).__name__
        finally:
            super().cleanup()
        if "watcher_cleanup_error" in self.receipt:
            self.receipt["cleanup_passed"] = False
