"""Bounded composition owner fixtures, with real Linux Git and injected dispatch.

These checks exercise request/result/lifecycle contracts, not live fleet readiness.
"""
import json
from pathlib import Path
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import test_task_group as fixtures
import test_lifecycle_state as lifecycle
from fm_task_group_store import GroupError, canonical, digest, read_json, retained_output_ref, write_json


class DynamicOwnerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.attachment = self.owner.attach("flow", self.fixture.package, self.fixture.project,
                                            "Work", "workflow-review", workflow="dynamic")
        self.root_worktree = self.fixture.base / "root-worktree"
        self.fixture.git("worktree", "add", "--detach", str(self.root_worktree), self.attachment["input_commit"])
        self.root_meta = dict(self.fixture.root_meta, endpoint_task_id="flow",
                              worktree=str(self.root_worktree), task_group_primitive="Work",
                              task_group_workflow="dynamic")
        self.fixture.save_meta("flow", self.root_meta)
        self.owner.spawn = self.spawn
        self.records = []

    def spawn(self, root, generation, child, project, harness, model, effort):
        binding = self.owner.binding(child)
        record = self.owner.request(root, binding["request_id"])
        self.assertEqual(record["state"], "launching")
        self.records.append(record)
        worktree = self.fixture.base / (child + "-worktree")
        self.fixture.git("worktree", "add", "--detach", str(worktree), record["input_commit"])
        tasktmp = self.fixture.base / (child + "-tmp")
        tasktmp.mkdir()
        value = {"endpoint_task_id": child, "spawn_gen": "component-gen", "backend": "herdr",
                 "kind": "scout", "harness": harness, "model": model, "effort": effort,
                 "project": str(project), "worktree": str(worktree), "tasktmp": str(tasktmp),
                 "herdr_session": "fixture-lab", "herdr_workspace_id": child, "herdr_tab_id": "tab",
                 "herdr_pane_id": "pane", "window": child, "task_group_role": "component",
                 "task_group_parent": root, "task_group_request": binding["request_id"],
                 "task_group_hash": binding["body_hash"], "task_group_epoch": "1",
                 "result_disposition": "parent", "task_group_workflow": "dynamic",
                 "task_group_primitive": record["primitive"],
                 "task_group_writable": str(record["writable"]).lower()}
        self.fixture.save_meta(child, value)
        return SimpleNamespace(returncode=0)

    def submit(self, request_id="maker-a", primitive="Work", writable=True, assignment="Implement scoped change."):
        return self.owner.submit("flow", self.root_meta["spawn_gen"],
                                 dict(request_id=request_id, assignment=assignment,
                                      primitive=primitive, writable=writable))

    def gather(self, request_id):
        return self.owner.status("flow", self.root_meta["spawn_gen"], gather=True, request_id=request_id)

    def commit(self, worktree, name, text="scoped output"):
        (Path(worktree) / name).write_text(text)
        self.git_at(worktree, "add", name)
        self.git_at(worktree, "commit", "-qm", "fixture " + name)
        return self.git_at(worktree, "rev-parse", "HEAD")

    def git_at(self, worktree, *args):
        return subprocess.run(["git", "-C", str(worktree), *args], check=True,
                              capture_output=True).stdout.decode().strip()

    def complete(self, request, filename=None):
        child = request["request"]["child"]
        if filename:
            self.commit(self.owner.meta(child)["worktree"], filename)
        return self.owner.complete(child, "component-gen", self.fixture.report(child))

    def test_two_writers_join_exact_candidate_then_one_review_and_repair(self):
        first, second = self.submit(), self.submit("maker-b")
        self.assertNotEqual(first["request"]["child"], second["request"]["child"])
        self.assertEqual(first["request"]["input_commit"], second["request"]["input_commit"])
        outputs = [self.complete(first, "a.txt"), self.complete(second, "b.txt")]
        with self.assertRaisesRegex(GroupError, "gather all"):
            self.submit("audit", "Review", False)
        status = self.owner.status("flow", self.root_meta["spawn_gen"])
        self.assertEqual(len(status["requests"]), 2)
        with self.assertRaisesRegex(GroupError, "requires request_id"):
            self.owner.status("flow", self.root_meta["spawn_gen"], gather=True)
        for result in outputs:
            self.gather(result["result"]["request_id"])
            self.git_at(self.root_worktree, "cherry-pick", result["result"]["output_commit"])
        joined = self.git_at(self.root_worktree, "rev-parse", "HEAD")
        self.assertNotEqual(joined, self.attachment["input_commit"])
        self.assertEqual(self.fixture.git("rev-parse", "HEAD"), self.attachment["input_commit"])
        self.assertFalse(self.owner.waiting("flow")["pending"])
        self.assertTrue(self.owner.waiting("flow")["composition_pending"])
        self.assertFalse(self.owner.waiting("flow")["cleanup_allowed"])
        review = self.submit("audit", "Review", False)
        self.assertEqual(review["request"]["input_commit"], joined)
        self.assertEqual(review["request"]["phase"], "review")
        with self.assertRaisesRegex(GroupError, "gather Review"):
            self.submit("repair")
        audit = self.complete(review)
        self.assertNotIn("output_commit", audit["result"])
        self.assertTrue(audit["result"]["readonly"])
        self.gather("audit")
        with self.assertRaisesRegex(GroupError, "only one fresh"):
            self.submit("second-audit", "Review", False)
        repair = self.submit("repair")
        self.assertEqual(repair["request"]["phase"], "repair")
        self.assertFalse(self.owner.waiting("flow")["cleanup_allowed"])
        self.complete(repair, "repair.txt")
        self.gather("repair")
        self.assertTrue(self.owner.waiting("flow")["cleanup_allowed"])
        self.assertEqual(len(self.records), 4)
        self.assertEqual({notice[2] for notice in self.fixture.notices}, {"maker-a", "maker-b", "audit", "repair"})

    def test_writer_may_edit_or_commit_before_dispatch_returns(self):
        for mode in ("edit", "commit"):
            def early_writer(*args):
                result = self.spawn(*args)
                worktree = Path(self.owner.meta(args[2])["worktree"])
                if mode == "edit":
                    (worktree / "early.txt").write_text("started before spawn returned")
                else:
                    self.commit(worktree, "early.txt")
                return result
            self.owner.spawn = early_writer
            request = self.submit("early-" + mode)
            self.assertEqual(request["request"]["state"], "launched")
            self.assertEqual(request["request"]["child_generation"], "component-gen")
            worktree = self.owner.meta(request["request"]["child"])["worktree"]
            if mode == "edit":
                self.git_at(worktree, "add", "early.txt")
                self.git_at(worktree, "commit", "-qm", "finish early writer")
            completed = self.complete(request)
            self.assertEqual(completed["result"]["output_commit"], self.git_at(worktree, "rev-parse", "HEAD"))

    def test_writer_output_ancestry_survives_component_teardown_prune_and_replacement(self):
        request = self.submit()
        child = request["request"]["child"]
        worktree = self.owner.meta(child)["worktree"]
        self.git_at(worktree, "switch", "-c", "fixture-writer")
        first_commit = self.commit(worktree, "first.txt")
        completed = self.complete(request, "second.txt")
        output = completed["result"]["output_commit"]
        archive = completed["result"]["output_ref"]
        self.gather("maker-a")
        # Simulate normal branch retirement/worktree pool reset after gather.
        disposable = self.commit(worktree, "unretained.txt")
        self.git_at(worktree, "switch", "--detach", request["request"]["input_commit"])
        self.fixture.git("branch", "-D", "fixture-writer")
        self.fixture.git("worktree", "remove", worktree)
        self.fixture.git("reflog", "expire", "--expire=now", "--all")
        self.fixture.git("gc", "--prune=now")
        missing = subprocess.run(["git", "-C", str(self.fixture.project), "cat-file", "-e", disposable],
                                 capture_output=True)
        self.assertNotEqual(missing.returncode, 0, "disposable unretained commit must really be pruned")
        self.assertEqual(self.fixture.git("rev-parse", archive), output)
        self.assertEqual(self.fixture.git("show", first_commit + ":first.txt"), "scoped output")
        self.assertEqual(self.fixture.git("show", output + ":second.txt"), "scoped output")
        self.root_meta["spawn_gen"] = "replacement-root"
        self.fixture.save_meta("flow", self.root_meta)
        replacement = self.gather("maker-a")
        self.assertEqual(replacement["result"], completed["result"])
        # A replacement can join the whole retained ancestry after child removal.
        commits = self.git_at(self.root_worktree, "rev-list", "--reverse",
                              request["request"]["input_commit"] + ".." + output).splitlines()
        self.git_at(self.root_worktree, "cherry-pick", *commits)
        self.assertTrue((self.root_worktree / "first.txt").is_file())
        self.assertTrue((self.root_worktree / "second.txt").is_file())
        # The archive also outlives retirement of the root workspace.
        self.git_at(self.root_worktree, "reset", "--hard", self.attachment["input_commit"])
        self.fixture.git("worktree", "remove", str(self.root_worktree))
        self.fixture.git("reflog", "expire", "--expire=now", "--all")
        self.fixture.git("gc", "--prune=now")
        self.assertEqual(self.fixture.git("rev-parse", archive), output)
        self.assertEqual(self.fixture.git("show", output + ":second.txt"), "scoped output")

    def test_missing_changed_or_symbolic_archive_blocks_gather_and_lifecycle(self):
        completed = self.complete(self.submit(), "output.txt")
        archive, output = completed["result"]["output_ref"], completed["result"]["output_commit"]
        for corruption in ("missing", "changed", "symbolic"):
            with self.subTest(corruption=corruption):
                self.fixture.git("update-ref", "--no-deref", "-d", archive)
                if corruption == "changed":
                    self.fixture.git("update-ref", archive, self.attachment["input_commit"])
                elif corruption == "symbolic":
                    self.fixture.git("symbolic-ref", archive, self.fixture.git("symbolic-ref", "HEAD"))
                with self.assertRaisesRegex(GroupError, "output ref"):
                    self.gather("maker-a")
                with self.assertRaisesRegex(GroupError, "output ref"):
                    self.owner.waiting("flow")
                with self.assertRaisesRegex(GroupError, "output ref"):
                    self.owner.waiting(completed["result"]["child"])
                self.fixture.git("update-ref", "--no-deref", "-d", archive)
                self.fixture.git("update-ref", archive, output)
        self.gather("maker-a")
        self.fixture.git("update-ref", "-d", archive)
        with self.assertRaisesRegex(GroupError, "output ref"):
            self.owner.waiting("flow")

    def test_existing_different_archive_is_never_overwritten(self):
        request = self.submit()
        child = request["request"]["child"]
        self.commit(self.owner.meta(child)["worktree"], "output.txt")
        archive = retained_output_ref(self.owner.home, "flow", 1, child)
        self.fixture.git("update-ref", archive, self.attachment["input_commit"])
        with self.assertRaisesRegex(GroupError, "ref is immutable"):
            self.complete(request)
        self.assertEqual(self.fixture.git("rev-parse", archive), self.attachment["input_commit"])
        self.assertEqual(self.owner.request("flow", "maker-a")["state"], "launched")
        self.assertFalse((self.owner.group("flow") / "results" / child / "result.json").exists())

    def test_noop_writer_archive_and_completion_retry_are_idempotent(self):
        request = self.submit()
        completed = self.complete(request)
        self.assertEqual(completed["result"]["output_commit"], request["request"]["input_commit"])
        self.assertEqual(self.fixture.git("rev-parse", completed["result"]["output_ref"]),
                         request["request"]["input_commit"])
        self.assertEqual(self.complete(request)["result"], completed["result"])
        self.assertTrue(self.gather("maker-a")["request"]["gathered"])

    def test_interrupted_result_publication_reuses_exact_archive(self):
        request = self.submit()
        child = request["request"]["child"]
        self.commit(self.owner.meta(child)["worktree"], "output.txt")
        def interrupted(path, value, **kwargs):
            if Path(path).name == "result.json":
                raise OSError("fixture interrupted publication")
            return write_json(path, value, **kwargs)
        with patch("fm_task_group.write_json", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "interrupted publication"):
                self.complete(request)
        archive = retained_output_ref(self.owner.home, "flow", 1, child)
        retained = self.fixture.git("rev-parse", archive)
        self.assertEqual(self.owner.request("flow", "maker-a")["state"], "launched")
        completed = self.complete(request)
        self.assertEqual(completed["result"]["output_ref"], archive)
        self.assertEqual(completed["result"]["output_commit"], retained)

    def test_replay_identity_survives_new_generation_and_root_candidate_change(self):
        first = self.submit()
        self.commit(self.root_worktree, "root-progress.txt")
        self.root_meta["spawn_gen"] = "replacement-root"
        self.fixture.save_meta("flow", self.root_meta)
        self.assertEqual(self.submit()["request"], first["request"])
        with self.assertRaisesRegex(GroupError, "different body"):
            self.submit(assignment="different")
        with self.assertRaisesRegex(GroupError, "different body"):
            self.submit(writable=False)
        with self.assertRaisesRegex(GroupError, "stale parent"):
            self.owner.status("flow", "s1.123.4")
        completed = self.complete(first, "retained.txt")
        with patch("fm_task_group.time.time", return_value=100):
            gathered = self.gather("maker-a")
        with patch("fm_task_group.time.time", return_value=200):
            replay = self.gather("maker-a")
        self.assertEqual(gathered["request"]["gathered_at"], replay["request"]["gathered_at"])
        self.assertEqual(replay["request"]["gathered_parent_gen"], "replacement-root")
        self.assertEqual(replay["result"], completed["result"])
        self.assertEqual(len(self.records), 1)

    def test_dynamic_schema_is_explicit_and_legacy_attachment_stays_readonly(self):
        for change in ({}, {"primitive": "Review"}, {"primitive": "Review", "writable": True},
                       {"primitive": "Work", "writable": "true"},
                       {"primitive": "Work", "writable": False, "model": "other"}):
            body = dict(self.fixture.body, **change)
            with self.subTest(change=change), self.assertRaises(GroupError):
                self.owner.submit("flow", self.root_meta["spawn_gen"], body)
        with self.assertRaises(GroupError):
            self.owner.submit("root", self.fixture.root_meta["spawn_gen"],
                              dict(self.fixture.body, primitive="Work", writable=True))
        self.assertFalse((self.owner.group("flow") / "requests").exists())
        self.assertEqual(self.owner.requests("flow"), [])

    def test_writer_dirty_unrelated_and_changed_output_are_refused(self):
        request = self.submit()
        child = request["request"]["child"]
        worktree = Path(self.owner.meta(child)["worktree"])
        (worktree / "dirty.txt").write_text("unfinished")
        with self.assertRaisesRegex(GroupError, "dirty"):
            self.complete(request)
        self.git_at(worktree, "add", "dirty.txt")
        self.git_at(worktree, "commit", "-qm", "scoped output")
        completed = self.complete(request)
        self.assertEqual(completed["result"]["output_commit"], self.git_at(worktree, "rev-parse", "HEAD"))
        self.commit(worktree, "late.txt")
        with self.assertRaisesRegex(GroupError, "immutable"):
            self.complete(request)
        other = self.submit("unrelated")
        other_tree = self.owner.meta(other["request"]["child"])["worktree"]
        self.git_at(other_tree, "switch", "--orphan", "unrelated-output")
        self.commit(other_tree, "unrelated.txt")
        with self.assertRaises(GroupError):
            self.complete(other)
        self.assertEqual(self.owner.request("flow", "unrelated")["state"], "launched")

    def test_readonly_work_and_review_cannot_publish_committed_changes(self):
        work = self.submit("inspect", writable=False)
        child = work["request"]["child"]
        self.commit(self.owner.meta(child)["worktree"], "forbidden.txt")
        with self.assertRaisesRegex(GroupError, "commit changed"):
            self.complete(work)
        self.git_at(self.owner.meta(child)["worktree"], "reset", "--hard", work["request"]["input_commit"])
        self.complete(work)
        self.gather("inspect")
        review = self.submit("audit", "Review", False)
        child = review["request"]["child"]
        self.commit(self.owner.meta(child)["worktree"], "repair-forbidden.txt")
        with self.assertRaisesRegex(GroupError, "commit changed"):
            self.complete(review)

    def test_dirty_root_refuses_new_requests_but_retained_results_still_gather(self):
        request = self.submit()
        self.complete(request, "finished.txt")
        (self.root_worktree / "dirty-root.txt").write_text("join unfinished")
        self.gather("maker-a")
        with self.assertRaisesRegex(GroupError, "dirty"):
            self.submit("audit", "Review", False)
        self.assertEqual(len(self.records), 1)

    def test_request_and_result_identities_do_not_cross_components(self):
        first, second = self.submit(), self.submit("maker-b")
        a, b = self.complete(first, "a.txt"), self.complete(second, "b.txt")
        self.assertEqual(self.owner.component_context(b["result"]["child"])[1]["body"]["request_id"], "maker-b")
        bad_result = dict(a["result"], request_id="maker-b")
        write_json(Path(a["result_path"]), bad_result)
        record = dict(a["request"], result_digest=digest(canonical(bad_result)))
        write_json(self.owner.request_path("flow", "maker-a"), record)
        with self.assertRaisesRegex(GroupError, "request identity"):
            self.gather("maker-a")
        with self.assertRaises(GroupError):
            self.owner.waiting("flow")
        self.assertTrue(self.gather("maker-b")["request"]["gathered"])

    def test_uncertain_component_survives_another_result_gather(self):
        self.owner.spawn = lambda *args: SimpleNamespace(returncode=1)
        uncertain = self.submit("uncertain")
        self.owner.spawn = self.spawn
        good = self.submit("good", writable=False)
        self.complete(good)
        self.gather("good")
        state = self.owner.waiting("flow")
        self.assertTrue(state["pending"])
        self.assertFalse(state["cleanup_allowed"])
        self.assertEqual([item["request_state"] for item in state["requests"]], ["uncertain", "complete"])
        self.assertEqual(self.submit("uncertain")["request"]["child"], uncertain["request"]["child"])
        with self.assertRaisesRegex(GroupError, "gather all"):
            self.submit("audit", "Review", False)

    def test_request_file_name_must_match_body_identity(self):
        request = self.submit()
        path = self.owner.request_path("flow", "wrong")
        write_json(path, request["request"])
        with self.assertRaisesRegex(GroupError, "saved request ID"):
            self.owner.status("flow", self.root_meta["spawn_gen"])

    def test_exact_self_development_repository_refuses_before_task_mutation(self):
        code = self.fixture.project / "bin"
        code.mkdir()
        (code / "fm-spawn.sh").write_text("FirstMate runtime fixture")
        self.owner.code_root = self.fixture.project
        with self.assertRaisesRegex(GroupError, "self-development"):
            self.owner.attach("self-denied", self.fixture.package, self.root_worktree,
                              "Work", "workflow-review", workflow="dynamic")
        self.assertFalse(self.owner.task("self-denied").exists())

    def test_atomic_publication_temporary_does_not_invent_lifecycle_attention(self):
        request = self.submit()
        temporary = self.owner.request_path("flow", "maker-a").parent / ".publish-abcd1234"
        temporary.write_text("unfinished atomic publication")
        state = self.owner.waiting("flow")
        self.assertEqual(len(state["requests"]), 1)
        self.assertEqual(state["requests"][0]["child_task_id"], request["request"]["child"])

    def test_fresh_dynamic_root_cannot_teardown_before_review(self):
        state = self.owner.waiting("flow")
        self.assertFalse(state["pending"])
        self.assertTrue(state["composition_pending"])
        self.assertFalse(state["cleanup_allowed"])


class DynamicLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.fixture = lifecycle.LifecycleStateTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.env["CODE"] = str(fixtures.BIN.parent)
        self.fixture.record.update(root="root", request_state="aggregate", launch_active=False,
                                   composition_pending=True, child_task_id=None, child_generation=None)
        self.fixture.record["requests"] = [self.member("child"), self.member("second")]
        (self.fixture.home / "state/second.meta").write_text(
            "kind=scout\nspawn_gen=s1\nendpoint_task_id=second\nbackend=herdr\n")
        self.fixture.write_query()

    @staticmethod
    def member(child, state="launched", gathered=False):
        return dict(attached=True, root="root", component=False, pending=not gathered,
                    cleanup_allowed=gathered, child_task_id=child, child_generation="s1",
                    request_state=state, result_ready=state=="complete",
                    launch_active=False, gathered=gathered)

    def test_every_pending_endpoint_is_checked_and_one_failure_is_attention(self):
        self.assertTrue(self.fixture.current().startswith("waiting|"))
        (self.fixture.home / "state/second.meta").unlink()
        self.assertTrue(self.fixture.current().startswith("group-attention|"))

    def test_gathered_first_result_cannot_hide_later_uncertain_component(self):
        self.fixture.record["requests"] = [self.member("child", "complete", True),
                                           self.member("second", "uncertain")]
        self.fixture.record["requests"][1]["child_generation"] = None
        self.fixture.write_query()
        self.assertTrue(self.fixture.current().startswith("group-attention|"))

    def test_all_retained_results_are_ready_but_teardown_stays_guarded(self):
        self.fixture.record["requests"] = [self.member("child", "complete"), self.member("second", "complete")]
        self.fixture.record["result_ready"] = True
        self.fixture.write_query()
        self.assertTrue(self.fixture.current().startswith("group-ready|"))
        out = self.fixture.run_bash(
            'if fm_task_group_guard "$FM_HOME" root "$STATE" teardown; then exit 9; fi; echo held')
        self.assertEqual(out, "held")

    def test_empty_dynamic_composition_is_working_but_delivery_and_teardown_guarded(self):
        self.fixture.record.update(requests=[], pending=False, result_ready=False)
        self.fixture.write_query()
        out = self.fixture.run_bash(
            'if fm_task_group_current "$FM_HOME" root "$STATE"; then exit 9; fi; '
            'fm_task_group_event_scoped "$FM_HOME" root "$STATE" || exit 10; '
            'if fm_task_group_guard "$FM_HOME" root "$STATE" teardown; then exit 11; fi; echo held')
        self.assertEqual(out, "held")


if __name__ == "__main__":
    unittest.main()
