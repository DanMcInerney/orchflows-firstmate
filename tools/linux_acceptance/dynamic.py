"""Targeted dynamic/custom trial; execution and cleanup use existing FirstMate owners."""
import hashlib
import json
import re
import tempfile
from pathlib import Path
import time

from .evidence import read_order, final_check_order
from .runtime import metadata
from .trial import Trial


def maker_relaunch_window(requests):
    """Require a gathered maker and another maker still running, not a later Review."""
    completed = [r for r in requests if r.get("primitive") == "Work" and r.get("gathered")]
    pending = [r for r in requests if r.get("primitive") == "Work" and r.get("state") == "launched"]
    return completed, pending


class DynamicTrial(Trial):
    @property
    def local_only(self):
        return getattr(self.args, "local_only", False)

    def root_flags(self, *, spawn=False):
        if self.local_only:
            return ["--mode", "local-only", *(["--yolo", "on"] if spawn else [])]
        return ["--scout"]

    def delivery_instructions(self):
        if self.local_only:
            return (
                "You are the ordinary ship root with local-only delivery. Keep the final joined output committed "
                "on your existing fm/<task-id> branch. Write your diagnostic delivery report only at "
                "your recorded tasktmp/dynamic-delivery.md; this report is evidence, while the branch is the deliverable. "
                "Follow the existing local-only Definition of done: do not push, open a PR, run no-mistakes or merge. "
                "When all required results are gathered, Review and the repair/check pass are complete, and the "
                "committed branch is clean, append exactly done: ready in branch fm/<task-id> using your actual task ID. "
                "Stop there; FirstMate owns subsequent landing and cleanup. ")
        return (
            "Remain the normal scout root and deliver the ordinary root report. Follow ordinary scout "
            "completion/captain-hold gate (--none only with no unresolved captain decisions), then append done. ")

    def prepare_root(self, project, session):
        home = self.namespace / "claude-fm"
        for name in ("data", "state", "config", "projects"):
            (home / name).mkdir(parents=True)
        self.write(home / "config/claude-permission-mode", "auto\n")
        self.write(home / "config/herdr-presentation-spaces", "off\n")
        for key, value in (("user.name", "Dynamic Fixture"), ("user.email", "fixture@example.invalid")):
            self.run(["git", "-C", project, "config", key, value])
        root = "accept-" + self.namespace.name.removeprefix("a-")
        env = {**self.env, "FM_HOME": str(home), "HERDR_SESSION": session}
        self.owner_home, self.root, self.worker_env = home, root, env
        self.active_homes.append((home, env))
        self.run(["tasks-axi", "add", root, "Compose two makers and an independent review",
                  "--kind", "ship" if self.local_only else "scout", "--repo", "acceptance-fixture", "--file", home / "data/backlog.md"],
                 env=env, cwd=home)
        self.owner("fm-brief.sh", root, "acceptance-fixture", *self.root_flags(), env=env)
        spec = (
            "Use the retained orch-dynamic-workflow skill through FirstMate. Produce two useful isolated Work "
            "results, join them in your assigned worktree, request one fresh independent Review of that exact "
            "clean candidate, then perform one repair/check pass without a second Review. "
            "Only components use component completion; you deliver through the ordinary root delivery contract below. "
            "Read retained skill/guidance paths from the launch catalog. Use only the retained scripts/firstmate.py "
            "client for submit/status/gather, relying on launch context. Every submit and gather must be a separate "
            "literal python3 -B ABSOLUTE_CLIENT_PATH command, with no wrappers, variables or compound shell syntax. "
            "Requests have exactly request_id,assignment,primitive,writable. Keep request files under tasktmp.\n\n"
            "Submit these two Work requests before gathering either (primitive Work, writable true). "
            "stock-maker-v1 owns stock.py and test_stock.py: add has_stock(counts), returning whether total_units(counts) "
            "is positive; test empty, all zero and positive inputs. label-maker-v1 owns labels.py and test_labels.py: "
            "add label_key(value), which strips and uppercases via normalize_code then replaces hyphens with underscores; "
            "test empty, whitespace and ' ab-7 ' -> 'AB_7'. "
            f"The label maker begins with a {self.args.component_delay}-second foreground sleep (timeout at least 420000 ms). "
            "Each maker reads Make guidance, edits only its own files, runs its tests with python3 -B -m unittest, "
            "commits its change on its assigned branch, and completes with a report describing checks and commit. "
            "No maker delegates. Submit each IDENTICAL request JSON twice consecutively, recording replay identity.\n\n"
            "Use status to reconcile all accepted requests. Once each result completes, read the ENTIRE retained "
            "report.md and result.json using native Read with no offset/limit BEFORE the first gather --request-id ID. "
            "Join each maker's commits using ordinary git cherry-pick of input_commit..output_commit in your worktree. "
            "Use Git history and tests to recognize an already joined result after relaunch; never duplicate accepted work. "
            "Once both results are gathered and joined, run python3 -B -m unittest discover -v and keep HEAD clean.\n\n"
            "Then submit final-review-v1 (primitive Review,writable false) for one fresh independent audit of your exact "
            "joined candidate, both functions and tests, applying Review guidance. It may run tests but cannot repair or "
            "delegate. Submit the identical review request twice. Read both retained files fully before gather. "
            "Make one repair/check pass from findings, committing any repairs; run the complete tests once more and write "
            "their output with exactly one literal command: python3 -B -m unittest discover -v > "
            "ABSOLUTE_TASKTMP/dynamic-final-check.txt 2>&1 (replace ABSOLUTE_TASKTMP with the actual path, "
            "no variables, compound commands or wrappers). No second Review. Report exact reviewed and final commits, "
            "request/child identities, joins, reviewer findings, repairs and final checks. "
            "Do not modify original project checkout or package, inspect credentials/history, use native children, open a PR "
            "or merge into the original branch. "
            + self.delivery_instructions() +
            "After relaunch use current context to reconcile all "
            "accepted requests and continue this same composition.\n"
        )
        if self.args.restart:
            spec += ("\nFor this recovery trial, gather and join each ready Work result immediately while the "
                     "other still runs. Do not wait for both Work results before gathering either. "
                     "Poll status in short steps; do not sleep longer than ten seconds in the root or "
                     "batch a long wait for the delayed maker with a ready-result check. The driver needs "
                     "one gathered result and one running maker to exercise ordinary root relaunch.\n")
        custom = self.args.custom_workflow
        library = self.namespace / "custom-library"
        if custom:
            skill = library / "skills" / "compose-fixture" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            self.write_json(library / "plugin.json", {"name": "acceptance", "version": "2.0.0", "skills": "./skills/"})
            self.write(library / "README.md", "Uses the exact retained core supplied by FirstMate.\n")
            self.write(skill, "---\nname: compose-fixture\ndescription: Compose two makers and one independent review.\n---\n\n"
                       "Load the retained core orch-dynamic-workflow skill and use its Work/Review composition for "
                       "the scoped two-function assignment in the task brief. Join the two committed maker results, "
                       "review that exact candidate once and make one repair/check pass. Apply guidance/code.md. "
                       "Include the receipt marker composed-catalog-accepted in the final report specified by the task brief.\n")
            spec = ("First use native Read to read and apply acceptance:compose-fixture from the retained catalog. "
                    "Its source changes after enablement; the retained copy is authoritative.\n\n" + spec)
        brief = home / "data" / root / "brief.md"
        self.write(brief, brief.read_text().replace("{TASK}", "Implement and verify stock and label helpers")
                   .replace("{FIRSTMATE_SPEC}", spec))
        args = ["python3", "-B", self.candidate / "bin/fm-task-group.py", "--home", home,
                "enable", "--package", self.package, "--project", project,
                "--workflow", "dynamic", "--review-policy", "workflow-review"]
        if custom:
            args.extend(["--library", library])
        enabled = self.run(args, env=env, timeout=300)
        self.write(self.out / "enable.json", enabled.stdout)
        if custom:
            self.write(library / "skills/compose-fixture/SKILL.md", "Changed source; do not use this replacement.\n")
        if (home / "data" / root / "task-group/attachment.json").exists():
            raise RuntimeError("Enablement attached a task before normal spawn")
        self.write(self.out / "root-brief.md", brief.read_text())
        self.receipt.update(scope="private Linux Claude dynamic composition acceptance", workflow="dynamic",
                            entrypoint="enabled-project", custom_workflow=custom,
                            root_delivery="ship/local-only" if self.local_only else "scout/report")
        return home, root, env

    def requests(self):
        directory = self.owner_home / "data" / self.root / "task-group/requests"
        return [json.loads(path.read_text()) for path in sorted(directory.glob("*.json"))]

    def run_component(self, project):
        self.sessions.append(self.session)
        self.lab("provision", self.session)
        home, root, env = self.prepare_root(project, self.session)
        result = {"root": root, "session": self.session, "workflow": "dynamic", "samples": [], "started_at": time.time()}
        self.receipt["runs"].append(result)
        self.start_watch()
        spawned = self.owner("fm-spawn.sh", root, project, *self.root_flags(spawn=True), "--backend", "herdr", "--harness", "claude",
                             "--orchflows-workflow", "dynamic", env=env, timeout=180, check=False)
        result["spawn_exit"] = spawned.returncode
        self.write(self.out / "spawn.log", spawned.stdout + spawned.stderr)
        deadline = time.monotonic() + self.args.timeout
        while spawned.returncode == 0 and time.monotonic() < deadline:
            if self.expiry is not None and time.time() > self.expiry - 60:
                raise RuntimeError("Token reached stop margin; no refresh attempted")
            requests = self.requests()
            states = {r["body"]["request_id"]: [r["state"], r.get("gathered", False)] for r in requests}
            result["samples"].append({"at": time.time(), "requests": states, "watcher_exit": self.watcher.poll()})
            completed, pending = maker_relaunch_window(requests)
            if self.args.restart and "replacement" not in result and completed and pending:
                old = metadata(home / "state" / (root + ".meta"))
                attachment_path = home / "data" / root / "task-group/attachment.json"
                delivery_before = {key: old.get(key) for key in ("kind", "mode", "task_group_delivery")}
                attachment_before = hashlib.sha256(attachment_path.read_bytes()).hexdigest()
                replaced = self.owner("fm-control.sh", root, "relaunch", "--note",
                    "Resume the exact dynamic composition. Read current status for every accepted request. "
                    "Keep gathered results and joined commits; use existing child IDs and current context. "
                    "Complete remaining Work, one Review and one repair/check pass; do not duplicate requests.",
                    env=env, timeout=180, check=False)
                result["replacement"] = {"exit": replaced.returncode, "before_generation": old.get("spawn_gen"),
                    "accepted": {r["body"]["request_id"]: r["child"] for r in requests},
                    "gathered_before": [r["body"]["request_id"] for r in completed],
                    "pending_work": {r["body"]["request_id"]: r["child"] for r in pending}}
                if self.local_only:
                    result["replacement"].update(delivery_before=delivery_before, attachment_before=attachment_before)
                self.write(self.out / "replacement.log", replaced.stdout + replaced.stderr)
            status = home / "state" / (root + ".status")
            lines = status.read_text().splitlines() if status.exists() else []
            print(f"Dynamic observation: {states}", flush=True)
            self.save()
            if (lines and lines[-1].startswith(("done:", "failed:", "blocked:", "needs-decision:"))) or any(
                    r["state"] == "uncertain" for r in requests):
                break
            time.sleep(10)
        self.collect_dynamic(result, project)
        if self.local_only:
            from .local_delivery import collect_ready, land
            collect_ready(self, result, project)
            if result["acceptance"]["passed"]:
                land(self, result, project)
        result["elapsed_seconds"] = round(time.time() - result["started_at"], 3)
        return result["acceptance"]["passed"]

    def collect_dynamic(self, result, project):
        home, root = self.owner_home, self.root
        metas = {p.stem: metadata(p) for p in (home / "state").glob("*.meta")}
        result["metadata"] = metas
        requests = self.requests()
        result["requests"] = requests
        group = home / "data" / root / "task-group"
        attachment = json.loads((group / "attachment.json").read_text()) if (group / "attachment.json").exists() else {}
        result["client_path"] = str(Path(attachment.get("package_path", "/nonexistent")) / "scripts/firstmate.py")
        if self.args.custom_workflow:
            result["custom_skill_path"] = str(Path(attachment.get("package_path", "/nonexistent")) /
                "firstmate-libraries/acceptance/skills/compose-fixture/SKILL.md")
        retained, reads, integrity = {}, {}, True
        for request in requests:
            request_id = request["body"]["request_id"]
            directory = group / "results" / request["child"]
            if request["state"] != "complete":
                integrity = False
                continue
            value = json.loads((directory / "result.json").read_text())
            retained[request_id] = value
            canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
            integrity &= hashlib.sha256(canonical).hexdigest() == request.get("result_digest")
            integrity &= hashlib.sha256((directory / "report.md").read_bytes()).hexdigest() == value.get("report_digest")
            for name in ("report.md", "result.json"):
                self.write(self.out / (request_id + "-" + name), (directory / name).read_text())
            reads[request_id] = read_order(self.namespace, home, {**result, "request": request})
        result["retained_results"], result["read_order"] = retained, reads
        parent = metas.get(root, {})
        worktree = Path(parent.get("worktree", "/nonexistent"))
        status = home / "state" / (root + ".status")
        lines = status.read_text().splitlines() if status.exists() else []
        report = (Path(parent.get("tasktmp", "/nonexistent")) / "dynamic-delivery.md" if self.local_only
                  else home / "data" / root / "report.md")
        report_text = report.read_text() if report.exists() else ""
        self.write(self.out / "root-report.md", report_text)
        expected = {"stock-maker-v1", "label-maker-v1", "final-review-v1"}
        checks = {"normal_spawn_attached": attachment.get("workflow") == "dynamic",
                  "root_spawn_succeeded": result["spawn_exit"] == 0,
                  "requested_worker_profile": len(metas) == 4 and all(
                      meta.get("harness") == "claude" and all(meta.get(key) == value
                          for key, value in self.receipt["worker_profile"].items())
                      for meta in metas.values()),
                  "ordinary_root_done": bool(lines) and lines[-1].startswith("done:"),
                  "two_work_one_review": set(retained) == expected and len(requests) == 3,
                  "all_results_gathered": len(requests) == 3 and all(r.get("gathered") for r in requests),
                  "retained_integrity": integrity and len(retained) == 3,
                  "full_reads_before_each_gather": len(reads) == 3 and all(r["read_both_before_first_gather"] and
                      r["read_both_before_owner_acknowledgement"] for r in reads.values()),
                  "same_child_replays": len(reads) == 3 and all(r["same_child_replay"] for r in reads.values()),
                  "context_only_calls": len(reads) == 3 and all(r["context_only_calls"] for r in reads.values()),
                  "input_checkout_unchanged": self.run(["git", "-C", project, "rev-parse", "HEAD"]).stdout.strip() == self.receipt["input_commit"]
                      and self.run(["git", "-C", project, "status", "--porcelain"]).stdout == ""}
        if worktree.is_dir():
            result["final_commit"] = self.run(["git", "-C", worktree, "rev-parse", "HEAD"]).stdout.strip()
            result["reviewed_commit"] = retained.get("final-review-v1", {}).get("input_commit")
            actual = self.run(["python3", "-B", "-c",
                "from stock import has_stock; from labels import label_key; assert not has_stock([]); "
                "assert not has_stock([0,0]); assert has_stock([0,3]); assert label_key(' ab-7 ')=='AB_7'; assert label_key('')==''"],
                cwd=worktree, check=False)
            tests = self.run(["python3", "-B", "-m", "unittest", "discover", "-v"], cwd=worktree, check=False)
            self.write(self.out / "final-tests.log", tests.stdout + tests.stderr)
            checks["joined_behavior_and_tests"] = actual.returncode == 0 and tests.returncode == 0 and "Ran 0 tests" not in tests.stderr
            checks["clean_final_candidate"] = self.run(["git", "-C", worktree, "status", "--porcelain"]).stdout == ""
            reviewed = result.get("reviewed_commit")
            reviewed_checks = self.check_reviewed_candidate(worktree, reviewed, retained)
            result["reviewed_candidate_checks"] = reviewed_checks
            checks["reviewed_joined_candidate"] = reviewed_checks["passed"]
            final_check = Path(parent.get("tasktmp", "/nonexistent")) / "dynamic-final-check.txt"
            final_order = final_check_order(self.namespace, home, result, final_check)
            result["final_check_order"] = final_order
            final_text = final_check.read_text() if final_check.is_file() else ""
            checks["root_final_check_receipt"] = final_order["passed"] and bool(
                re.search(r"Ran [1-9][0-9]* tests? in .*\n\nOK\s*$", final_text))
            if final_check.is_file():
                self.write(self.out / "root-final-check.txt", final_text)
        if self.args.custom_workflow:
            checks["retained_composed_custom_skill"] = "composed-catalog-accepted" in report_text and all(
                r["custom_skill_read_before_submit"] for r in reads.values()) and len(reads) == 3
        if self.args.restart:
            replacement = result.get("replacement", {})
            by_id = {r["body"]["request_id"]: r["child"] for r in requests}
            running = replacement.get("pending_work", {})
            checks["maker_running_at_relaunch"] = bool(running) and all(
                by_id.get(key) == child and key not in replacement.get("gathered_before", [])
                for key, child in running.items())
            checks["accepted_work_survived_relaunch"] = replacement.get("exit") == 0 and bool(replacement.get("gathered_before")) and (
                parent.get("spawn_gen") != replacement.get("before_generation")) and all(
                by_id.get(key) == value for key, value in replacement.get("accepted", {}).items())
        result["acceptance"] = {"passed": all(checks.values()), "checks": checks}


    def check_reviewed_candidate(self, worktree, reviewed, retained):
        """Execute the frozen Review tree and compare each maker's actual file bytes."""
        checks = {"distinct_candidate": bool(reviewed) and reviewed != self.receipt["input_commit"]}
        files = {}
        owners = {"stock-maker-v1": ("stock.py", "test_stock.py"),
                  "label-maker-v1": ("labels.py", "test_labels.py")}
        if not reviewed:
            return {"passed": False, "checks": checks, "files_sha256": files}
        with tempfile.TemporaryDirectory(prefix="reviewed-check-", dir=self.namespace) as directory:
            snapshot = Path(directory)
            for request_id, names in owners.items():
                output = retained.get(request_id, {}).get("output_commit")
                for name in names:
                    at_review = self.run(["git", "-C", worktree, "show", reviewed + ":" + name], check=False)
                    at_maker = (self.run(["git", "-C", worktree, "show", output + ":" + name], check=False)
                                if output else None)
                    checks[name + "_matches_maker"] = bool(at_maker) and at_review.returncode == 0 and (
                        at_maker.returncode == 0 and at_review.stdout == at_maker.stdout)
                    if at_review.returncode == 0:
                        (snapshot / name).write_text(at_review.stdout)
                        files[name] = hashlib.sha256(at_review.stdout.encode()).hexdigest()
            reviewed_env = {key: value for key, value in self.env.items() if key != "CLAUDE_CODE_OAUTH_TOKEN"}
            behavior = self.run(["python3", "-B", "-c",
                "from stock import has_stock; from labels import label_key; assert not has_stock([]); "
                "assert not has_stock([0,0]); assert has_stock([0,3]); assert label_key(' ab-7 ')=='AB_7'; assert label_key('')==''"],
                env=reviewed_env, cwd=snapshot, check=False)
            tests = self.run(["python3", "-B", "-m", "unittest", "discover", "-v"],
                             env=reviewed_env, cwd=snapshot, check=False)
            checks["reviewed_behavior"] = behavior.returncode == 0
            checks["reviewed_tests"] = tests.returncode == 0 and "Ran 0 tests" not in tests.stderr
            self.write(self.out / "reviewed-tests.log", tests.stdout + tests.stderr)
        return {"passed": all(checks.values()), "checks": checks, "files_sha256": files}


    def cleanup(self):
        super().cleanup()
        if self.local_only:
            from .local_delivery import check_landed_after_cleanup
            check_landed_after_cleanup(self)
        for result in self.receipt.get("runs", []):
            retained = result.get("retained_results", {})
            writers = {key: value for key, value in retained.items() if value.get("writable")}
            checks = {}
            for request_id, value in writers.items():
                ref = value.get("output_ref")
                try:
                    observed = self.run(["git", "-C", self.namespace / "project", "rev-parse", "--verify",
                                         ref + "^{commit}"], check=False) if ref else None
                    checks[request_id] = observed is not None and observed.returncode == 0 and observed.stdout.strip() == value.get("output_commit")
                except Exception as error:
                    checks[request_id] = False
                    self.receipt.setdefault("writer_ref_cleanup_errors", {})[request_id] = type(error).__name__
            result["writer_refs_after_cleanup"] = checks
            if set(checks) != {"stock-maker-v1", "label-maker-v1"} or not all(checks.values()):
                self.receipt["cleanup_passed"] = False
