"""FirstMate-owned bounded component admission and retained result owner.

This is an experimental controller, not a fleet-readiness probe. Only FirstMate's
shell bridge may dispatch; tests can explicitly inject that external boundary.
"""
import os
import json
import re
from pathlib import Path
import subprocess
import time
from fm_task_group_runtime import runtime
from fm_task_group_primitives import (admit, attachment_primitive, component_fields, is_dynamic, scope,
                                      validate_metadata, validate_record)

from fm_task_group_store import (GroupError, canonical, clean_commit, clean_descendant, digest, git, group_lock,
                                 identifier, metadata, package_inventory, read_bytes,
                                 read_json, retained_output_ref, retain_output, safe_path, snapshot_package,
                                 verify_retained_output, write_bytes, write_json)


class TaskGroups:
    def __init__(self, home, code_root=None, spawn=None, notify=None):
        self.runtime = runtime()
        if not home:
            raise GroupError("explicit --home or FM_HOME is required")
        self.home = safe_path(home, directory=True)
        self.code_root = safe_path(code_root or Path(__file__).resolve().parent.parent, directory=True)
        self.spawn = spawn or self._spawn
        self.notify = notify or self._notify
        for folder in ("state", "data"):
            safe_path(self.home / folder, directory=True)

    def task(self, task):
        return safe_path(self.home / "data" / identifier(task, "task ID"), exists=False)

    def group(self, root):
        return safe_path(self.task(root) / "task-group", exists=False)

    def meta(self, task):
        return metadata(self.home / "state" / (identifier(task, "task ID") + ".meta"))

    def binding(self, task):
        path = self.task(task) / "task-group-component.json"
        return read_json(path) if path.exists() or path.is_symlink() else None

    def attachment(self, root, verify=True):
        value = read_json(self.group(root) / "attachment.json")
        if value.get("root") != root or value.get("epoch") != 1 or value.get("schema") != 1:
            raise GroupError("invalid task-group attachment identity")
        attachment_primitive(value)
        if self.runtime.windows and value.get("runtime") != self.runtime.identity:
            raise GroupError("Windows runtime differs from immutable task attachment")
        if verify:
            actual = digest(canonical(package_inventory(self.group(root) / "package")))
            if actual != value.get("package_digest"):
                raise GroupError("attached package snapshot changed")
        return value

    def root_meta(self, root, generation):
        identifier(generation, "generation")
        value = self.meta(root)
        if self.binding(root) or value.get("task_group_role") != "root":
            raise GroupError("caller must be an attached normal root scout")
        if value.get("backend") != "herdr" or value.get("kind") != "scout":
            raise GroupError("Stage 1 root requires backend=herdr kind=scout")
        if value.get("harness") not in ("claude", "codex"):
            raise GroupError("Stage 1 root requires Claude or Codex CLI")
        if value.get("spawn_gen") != generation or value.get("task_group_epoch") != "1":
            raise GroupError("stale parent generation or attachment epoch")
        if value.get("endpoint_task_id") != root:
            raise GroupError("root task metadata identity mismatch")
        attachment = self.attachment(root)
        validate_metadata(value, attachment)
        if safe_path(value.get("project", ""), directory=True) != Path(attachment["project"]):
            raise GroupError("root project differs from attachment")
        return value, attachment

    def request_path(self, root, request_id=None):
        attachment = self.attachment(root, verify=False)
        if is_dynamic(attachment):
            if request_id is None:
                raise GroupError("dynamic component operation requires request_id")
            return safe_path(self.group(root) / "requests" / (identifier(request_id, "request ID") + ".json"), exists=False)
        return self.group(root) / "request.json"

    def requests(self, root):
        attachment = self.attachment(root, verify=False)
        if not is_dynamic(attachment):
            record = self.request(root)
            return [record] if record else []
        directory = safe_path(self.group(root) / "requests", directory=True, exists=False)
        if not directory.exists():
            return []
        # Publication is atomic; lock-free lifecycle readers may see its temporary file.
        paths = [path for path in sorted(directory.iterdir())
                 if not re.fullmatch(r"\.publish-[a-z0-9_]{8}", path.name)]
        if len(paths) > attachment["max_components"]:
            raise GroupError("saved requests exceed attachment component bound")
        values = []
        for path in paths:
            if path.suffix != ".json":
                raise GroupError("unexpected record in component request directory")
            record = self.request(root, path.stem)
            if record is None:
                raise GroupError("component request disappeared")
            values.append(record)
        return sorted(values, key=lambda item: (item["accepted_at"], item["body"]["request_id"]))

    def request(self, root, request_id=None):
        attachment = self.attachment(root, verify=False)
        path = self.request_path(root, request_id)
        if not path.exists() and not path.is_symlink():
            return None
        value = read_json(path)
        body = self.request_body(value.get("body"), attachment)
        expected_child = "tg-" + digest(canonical([root, body["request_id"]]))[:20]
        if (value.get("root") != root or value.get("epoch") != 1 or
                value.get("body_hash") != digest(canonical(body)) or value.get("child") != expected_child or
                value.get("state") not in ("launching", "uncertain", "launched", "complete") or
                type(value.get("gathered")) is not bool or
                (value["gathered"] and value["state"] != "complete")):
            raise GroupError("invalid saved component request")
        if request_id is not None and body["request_id"] != request_id:
            raise GroupError("saved request ID differs from requested identity")
        validate_record(value, attachment)
        return value

    @staticmethod
    def request_body(body, attachment=None):
        basic = {"request_id", "assignment"}
        dynamic = basic | {"primitive", "writable"}
        if not isinstance(body, dict):
            raise GroupError("request must contain only request_id and assignment")
        if attachment is None:
            permitted = (basic, dynamic)
        else:
            permitted = (dynamic,) if is_dynamic(attachment) else (basic,)
        if set(body) not in permitted:
            raise GroupError("request must contain only request_id and assignment; dynamic workflow additionally requires primitive and writable")
        if set(body) == dynamic:
            component_fields(body, {"workflow": "dynamic"})
        identifier(body["request_id"], "request ID")
        assignment = body["assignment"]
        if (not isinstance(assignment, str) or not assignment.strip() or
                len(assignment.encode("utf-8")) > 32768 or "\x00" in assignment):
            raise GroupError("assignment must be nonempty text of at most 32768 UTF-8 bytes")
        return body

    def attach(self, root, package, project, primitive="Work", review_policy="none", workflow=None):
        # Policy refusal precedes the group lock, which can create persistent directories.
        admit(primitive, review_policy, workflow)
        root = identifier(root, "root ID")
        package = safe_path(package, directory=True)
        project = safe_path(project, directory=True)
        if workflow == "dynamic" and (self.code_root / "bin/fm-spawn.sh").is_file():
            # FirstMate self-development remains owned by its ordinary delivery
            # policy. An alternate worktree cannot bypass the exact repository identity.
            common = git(self.code_root, "rev-parse", "--path-format=absolute", "--git-common-dir",
                         accepted=(0, 128))
            if common and safe_path(common, directory=True) == safe_path(
                    git(project, "rev-parse", "--path-format=absolute", "--git-common-dir"), directory=True):
                raise GroupError("dynamic workflow is not admitted for FirstMate self-development")
        with group_lock(self.group(root)):
            if self.binding(root) or (self.home / "state" / f"{root}.meta").exists():
                raise GroupError("attach before the normal root's first launch")
            path = self.group(root) / "attachment.json"
            if path.exists():
                old = self.attachment(root)
                if (workflow != old.get("workflow") or primitive != old["primitive"] or review_policy != old.get("review_policy", "none") or
                        str(project) != old["project"] or digest(canonical(package_inventory(package))) != old["package_digest"]):
                    raise GroupError("attachment is immutable")
                clean_commit(project, old["input_commit"])
                return old
            commit = clean_commit(project)
            target = self.group(root) / "package"
            if target.exists():
                raise GroupError("incomplete package attachment remains; inspect it before another attach")
            package_digest = snapshot_package(package, target)
            clean_commit(project, commit)
            value = {"schema": 1, "root": root, "epoch": 1, "primitive": primitive,
                     "readonly": True, "max_components": 1, "project": str(project),
                     "input_commit": commit, "package_digest": package_digest,
                     "package_path": str(target), "attached_at": time.time()}
            if workflow == "dynamic":
                value.update(workflow=workflow, readonly=False, max_components=32, review_policy=review_policy)
            elif primitive == "Review":
                value["review_policy"] = review_policy
            if self.runtime.windows:
                value["runtime"] = self.runtime.identity
            write_json(path, value, exclusive=True)
            return value

    def submit(self, root, generation, body):
        body = self.request_body(body)
        with group_lock(self.group(root)):
            parent, attachment = self.root_meta(root, generation)
            body = self.request_body(body, attachment)
            dynamic = is_dynamic(attachment)
            records = self.requests(root)
            previous = self.request(root, body["request_id"]) if dynamic else (records[0] if records else None)
            if previous:
                if previous["body"]["request_id"] != body["request_id"]:
                    raise GroupError("Stage 1 allows only one component assignment per attachment")
                if previous["body_hash"] != digest(canonical(body)):
                    raise GroupError("request ID already used for a different body")
                return self._view(root, previous)
            if dynamic:
                if len(records) >= attachment["max_components"]:
                    raise GroupError("dynamic workflow component bound reached")
                reviews = [item for item in records if item["primitive"] == "Review"]
                if body["primitive"] == "Review":
                    if reviews:
                        raise GroupError("dynamic workflow permits only one fresh independent Review")
                    if any(not item.get("gathered") for item in records):
                        raise GroupError("gather all accepted Work results before Review")
                elif reviews and not reviews[0].get("gathered"):
                    raise GroupError("gather Review before the single repair/check phase")
                # Verify every retained result before allowing a later phase.
                for item in records:
                    self._view(root, item)
                input_commit = clean_descendant(parent.get("worktree", ""), attachment["input_commit"])
            else:
                input_commit = clean_commit(attachment["project"], attachment["input_commit"])
            child = "tg-" + digest(canonical([root, body["request_id"]]))[:20]
            child_dir = self.task(child)
            if child_dir.exists() or (self.home / "state" / f"{child}.meta").exists():
                raise GroupError("component task ID already exists outside this request")
            record = {"schema": 1, "root": root, "epoch": 1, "child": child, "body": body,
                      "body_hash": digest(canonical(body)), "accepted_parent_gen": generation,
                      "state": "launching", "gathered": False, "accepted_at": time.time(),
                      "harness": parent["harness"], "model": parent.get("model", "default"),
                      "effort": parent.get("effort", "default"), "package_digest": attachment["package_digest"],
                      "input_commit": input_commit}
            record.update(component_fields(record, attachment))
            if dynamic:
                record["phase"] = ("review" if body["primitive"] == "Review"
                                   else "repair" if reviews else "work")
            if self.spawn == self._spawn:
                record["launch_custody"] = self.launch_custody(root, generation)
            path = self.request_path(root, body["request_id"])
            path.parent.mkdir(parents=True, exist_ok=True)
            # Acceptance precedes all child scaffolding and every external side effect.
            write_json(path, record, exclusive=True)
            try:
                child_dir.mkdir()
                binding = {"schema": 1, "parent": root, "child": child, "epoch": 1,
                           "request_id": body["request_id"], "body_hash": record["body_hash"],
                           "accepted_parent_gen": generation}
                write_json(child_dir / "task-group-component.json", binding, exclusive=True)
                from fm_task_group_launch import component_brief
                write_bytes(child_dir / "brief.md", component_brief(self, binding, record, attachment).encode("utf-8"), exclusive=True)
                result = self.spawn(root, generation, child, attachment["project"], record["harness"], record["model"], record["effort"])
                if result.returncode != 0:
                    raise GroupError(f"FirstMate spawn bridge exited {result.returncode}")
                child_meta = self.component_meta(child, binding, record)
                # The launch owner positioned and checked the input before the
                # worker started. A writer may already have edited or committed
                # by the time spawn returns; endpoint metadata remains authoritative.
                if not record.get("writable"):
                    clean_commit(child_meta["worktree"], record["input_commit"])
                record.update(state="launched", child_generation=child_meta["spawn_gen"], launch_meta=child_meta)
            except (GroupError, OSError, subprocess.SubprocessError) as error:
                record.update(state="uncertain", launch_error=str(error)[:1024])
            write_json(path, record)
            return self._view(root, record)

    def launch_custody(self, root, generation, evidence=None):
        # Linux observation reuses FirstMate's process incarnation and symlink
        # lock owners. Other runtimes remain attention until they have an
        # independently verified launch-custody implementation.
        import sys
        if not sys.platform.startswith("linux"):
            return None if evidence is None else False
        bridge = safe_path(self.code_root / "bin" / "fm-task-group-spawn.sh")
        mode = "--capture-lock" if evidence is None else "--observe-lock"
        result = self.runtime.run(
            bridge, [mode, root, generation],
            env=self.runtime.environment(home=self.home, code_root=self.code_root),
            input=None if evidence is None else canonical(evidence),
            capture_output=True, timeout=10, check=False)
        if evidence is not None:
            return result.returncode == 0
        if result.returncode or len(result.stdout) > 32768:
            raise GroupError("launch transaction has no verifiable parent lock custody")
        return json.loads(result.stdout)

    def _spawn(self, root, generation, child, project, harness, model, effort):
        bridge = safe_path(self.code_root / "bin" / "fm-task-group-spawn.sh")
        environment = self.runtime.environment(home=self.home, code_root=self.code_root)
        # No caller-controlled CLI or environment escape hatch for an alternate runner.
        for name in ("FM_STATE_OVERRIDE", "FM_DATA_OVERRIDE", "FM_PROJECTS_OVERRIDE", "FM_CONFIG_OVERRIDE"):
            environment.pop(name, None)
        # Keep FirstMate's exact shell project spelling after root_meta verified
        # the same filesystem identity against the native attachment path.
        project = self.meta(root)["project"]
        return self.runtime.run(bridge, [root, generation, child, project, harness, model, effort],
                                env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=300, check=False)

    def component_context(self, child):
        binding = self.binding(child)
        if not binding:
            raise GroupError("task is not a task-group component")
        root = identifier(binding.get("parent"), "component parent")
        attachment = self.attachment(root)
        record = self.request(root, binding.get("request_id"))
        expected = {"schema": 1, "parent": root, "child": child, "epoch": 1,
                    "request_id": record["body"]["request_id"] if record else None,
                    "body_hash": record["body_hash"] if record else None,
                    "accepted_parent_gen": record["accepted_parent_gen"] if record else None}
        if binding != expected or not record or record["child"] != child:
            raise GroupError("component binding differs from accepted request")
        return binding, record, attachment

    def component_meta(self, child, binding, record):
        value = self.meta(child)
        expected = {"endpoint_task_id": child, "backend": "herdr", "kind": "scout",
                    "harness": record["harness"], "task_group_role": "component",
                    "task_group_parent": binding["parent"], "task_group_request": binding["request_id"],
                    "task_group_hash": binding["body_hash"], "task_group_epoch": "1",
                    "result_disposition": "parent", "model": record["model"], "effort": record["effort"]}
        if any(value.get(key) != item for key, item in expected.items()):
            raise GroupError("component launch metadata does not bind the accepted task, request and controls")
        if record.get("launch_meta"):
            keys = ("spawn_gen", "window", "herdr_session", "herdr_workspace_id", "herdr_tab_id",
                    "herdr_pane_id", "worktree", "tasktmp", "project")
            if any(value.get(key) != record["launch_meta"].get(key) for key in keys):
                raise GroupError("component endpoint or workspace identity changed since accepted launch")
        identifier(value.get("spawn_gen"), "component generation")
        if any(not value.get(key) for key in ("herdr_session", "herdr_workspace_id", "herdr_tab_id", "herdr_pane_id", "window")):
            raise GroupError("component metadata lacks exact Herdr endpoint identity")
        attachment = self.attachment(binding["parent"])
        validate_record(record, attachment)
        validate_metadata(value, attachment, record)
        if safe_path(value.get("project", ""), directory=True) != Path(attachment["project"]):
            raise GroupError("component project mismatch")
        worktree = safe_path(value.get("worktree", ""), directory=True)
        if worktree == Path(attachment["project"]):
            raise GroupError("component must use its own worktree")
        safe_path(value.get("tasktmp", ""), directory=True)
        return value

    def _view(self, root, record):
        meta_path = self.home / "state" / f"{root}.meta"
        current = self.meta(root) if meta_path.exists() or meta_path.is_symlink() else {}
        attachment = self.attachment(root)
        value = {"attached": True, "root": root, "epoch": 1,
                 "generation": current.get("spawn_gen"), "protocol": "firstmate-task-group",
                 "version": 1, "experimental": True, "scope": scope(attachment), "attachment": attachment,
                 "request_path": str(self.request_path(root, record["body"]["request_id"])) if record else None, "request": record}
        if record and record["state"] == "complete":
            directory = self.group(root) / "results" / record["child"]
            result = read_json(directory / "result.json")
            validate_record(result, attachment, result=True, request=record)
            payload = read_bytes(directory / "report.md", 512 * 1024)
            if digest(canonical(result)) != record.get("result_digest") or digest(payload) != result.get("report_digest"):
                raise GroupError("retained component result integrity check failed")
            if record.get("writable"):
                expected_ref = retained_output_ref(self.home, root, record["epoch"], record["child"])
                if result.get("output_ref") != expected_ref:
                    raise GroupError("retained writer output ref identity differs from accepted request")
                verify_retained_output(attachment["project"], expected_ref,
                                       result["output_commit"], record["input_commit"])
            value.update(result=result, report_path=str(directory / "report.md"), result_path=str(directory / "result.json"))
        return value

    def status(self, root, generation, gather=False, request_id=None):
        with group_lock(self.group(root)):
            _, attachment = self.root_meta(root, generation)
            if is_dynamic(attachment) and request_id is None:
                if gather:
                    raise GroupError("dynamic gather requires request_id")
                value = self._view(root, None)
                value["requests"] = [self._view(root, record) for record in self.requests(root)]
                return value
            record = self.request(root, request_id)
            value = self._view(root, record)
            if gather:
                if not record or record["state"] != "complete":
                    raise GroupError("component has no complete retained result to gather")
                # Keep the first acknowledgement observable across retries/recovery.
                record.setdefault("gathered_at", time.time())
                record.update(gathered=True, gathered_parent_gen=generation)
                write_json(self.request_path(root, record["body"]["request_id"]), record)
                value = self._view(root, record)
        return value

    def complete(self, child, generation, report):
        value = self._complete(child, generation, report)
        return self.notify_result(value["root"], value["request"]["body"]["request_id"])

    def _complete(self, child, generation, report):
        binding, _, _ = self.component_context(child)
        root = binding["parent"]
        with group_lock(self.group(root)):
            binding, record, attachment = self.component_context(child)
            value = self.component_meta(child, binding, record)
            if value["spawn_gen"] != generation or record.get("child_generation") != generation:
                raise GroupError("stale or unconfirmed component generation")
            if record["state"] not in ("launched", "complete"):
                raise GroupError("uncertain component launch requires owner reconciliation")
            output_commit = (clean_descendant(value["worktree"], record["input_commit"])
                             if record.get("writable") else clean_commit(value["worktree"], record["input_commit"]))
            report = safe_path(report)
            tasktmp = safe_path(value["tasktmp"], directory=True)
            if report == tasktmp or not report.is_relative_to(tasktmp):
                raise GroupError("report must be a regular file within recorded tasktmp")
            payload = read_bytes(report, 512 * 1024)
            try:
                nonempty = payload.decode("utf-8").strip()
            except UnicodeError as error:
                raise GroupError("report must be UTF-8 text") from error
            if not nonempty or b"\x00" in payload:
                raise GroupError("report must be nonempty text")
            if record["state"] == "complete":
                previous = self._view(root, record)
                if (digest(payload) != previous["result"]["report_digest"] or
                        (record.get("writable") and output_commit != previous["result"]["output_commit"])):
                    raise GroupError("component result is immutable")
                return previous
            parent = self.meta(root)
            self.root_meta(root, parent.get("spawn_gen", ""))
            directory = self.group(root) / "results" / child
            directory.mkdir(parents=True, exist_ok=True)
            result = {"schema": 1, "root": root, "child": child, "request_id": binding["request_id"],
                      "body_hash": binding["body_hash"], "epoch": 1, "primitive": "Work", "readonly": True,
                      "accepted_parent_gen": binding["accepted_parent_gen"], "parent_at_completion": parent,
                      "component_meta": value, "input_commit": record["input_commit"],
                      "package_digest": attachment["package_digest"], "report_digest": digest(payload),
                      "report_bytes": len(payload), "completed_at": time.time(),
                      "native_session_id": None,
                      "identity_limit": "Herdr endpoint and spawn generation recorded; native transcript session not verified"}
            result.update(component_fields(record, attachment))
            if record.get("writable"):
                result["output_commit"] = output_commit
                result["output_ref"] = retain_output(
                    attachment["project"],
                    retained_output_ref(self.home, root, record["epoch"], child),
                    output_commit, record["input_commit"])
            # A crash before request publication leaves retained output but no fabricated completion.
            write_bytes(directory / "report.md", payload)
            write_json(directory / "result.json", result)
            record.update(state="complete", result_digest=digest(canonical(result)))
            write_json(self.request_path(root, record["body"]["request_id"]), record)
            return self._view(root, record)

    def _notify(self, root, generation, request_id, result_digest):
        helper = safe_path(self.code_root / "bin" / "fm-task-group-state.sh")
        return self.runtime.run(helper, ["notify", str(self.home), root, generation, request_id, result_digest],
                                path_indexes=(1,), env=self.runtime.environment(home=self.home, code_root=self.code_root),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30, check=False)

    def notify_result(self, root, request_id=None):
        # Do not hold the group lock while the inbox owner obtains root meta custody.
        with group_lock(self.group(root)):
            record = self.request(root, request_id)
            if not record or record["state"] != "complete" or record.get("gathered"):
                return self._view(root, record)
            self._view(root, record)
            parent = self.meta(root)
            generation = parent.get("spawn_gen", "")
            self.root_meta(root, generation)
            expected = record["result_digest"]
        try:
            notice = self.notify(root, generation, record["body"]["request_id"], expected)
            delivered = notice.returncode == 0
            notice_error = None if delivered else f"FirstMate inbox owner exited {notice.returncode}"
        except (GroupError, OSError, subprocess.SubprocessError) as error:
            delivered, notice_error = False, str(error)[:1024]
        with group_lock(self.group(root)):
            record = self.request(root, request_id)
            if record.get("result_digest") == expected:
                record.update(notification_pending=not delivered, notification_error=notice_error)
                write_json(self.request_path(root, record["body"]["request_id"]), record)
            return self._view(root, record)

    def waiting(self, task, _retry=True):
        from fm_task_group_launch import role
        task_role = role(self, task)
        binding = self.binding(task)
        if not task_role:
            return {"attached": False, "pending": False, "component": False, "cleanup_allowed": True}
        root = binding["parent"] if binding else task
        attachment = self.attachment(root)
        if binding:
            _, record, _ = self.component_context(task)
            return self._waiting_record(root, record, True, _retry)
        records = self.requests(root)
        if not is_dynamic(attachment):
            return self._waiting_record(root, records[0] if records else None, False, _retry)
        states = [self._waiting_record(root, record, False, _retry) for record in records]
        pending = [state for state in states if state["pending"]]
        composition_pending = not any(record["primitive"] == "Review" and record.get("gathered")
                                      for record in records)
        return {"attached": True, "pending": bool(pending), "component": False,
                "composition_pending": composition_pending,
                "cleanup_allowed": not pending and not composition_pending, "root": root, "requests": states,
                "launch_active": False, "request_state": "aggregate",
                "request_id": None, "child_task_id": None, "child_generation": None,
                "result_digest": None,
                "result_ready": bool(pending) and all(state["result_ready"] for state in pending),
                "gathered": bool(states) and not pending}

    def _waiting_record(self, root, record, component, retry):
        self._view(root, record)  # Corruption never clears a lifecycle guard.
        pending = bool(record and not record.get("gathered"))
        launching = False
        if (not component and record and record["state"] == "launching"
                and isinstance(record.get("launch_custody"), dict)):
            try:
                self.root_meta(root, record["accepted_parent_gen"])
                launching = self.launch_custody(root, record["accepted_parent_gen"], record["launch_custody"])
                current = self.request(root, record["body"]["request_id"])
                if current != record:
                    if retry:
                        return self._waiting_record(root, current, component, False)
                    launching = False
            except (GroupError, OSError, ValueError, subprocess.SubprocessError):
                launching = False
        return {"attached": True, "pending": pending, "component": component,
                "cleanup_allowed": not pending, "root": root,
                "launch_active": launching,
                "request_state": record["state"] if record else "attached",
                "request_id": record["body"]["request_id"] if record else None,
                "child_task_id": record["child"] if record else None,
                "child_generation": record.get("child_generation") if record else None,
                "result_digest": record.get("result_digest") if record else None,
                "result_ready": bool(record and record["state"] == "complete"),
                "gathered": bool(record and record.get("gathered"))}
