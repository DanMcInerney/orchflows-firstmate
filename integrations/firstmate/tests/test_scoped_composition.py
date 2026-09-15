"""Selected caller-context phases and one-level Build trial owner checks."""
import copy
from pathlib import Path
from unittest.mock import patch
import unittest

import test_dynamic_owner as dynamic
from fm_task_group_store import GroupError, canonical, digest, write_json, read_json
from fm_task_group_launch import launch_overlay
from fm_task_group_composition import validate_composition


class ScopedCompositionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = dynamic.DynamicOwnerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.attachment = copy.deepcopy(self.fixture.attachment)
        self.attachment["composition"] = {"calls": [
            {"id": "prepare", "caller": "root"},
            {"id": "release", "caller": "root"},
            {"id": "trial", "caller": "trial-work"}]}
        # Fixture operator selects immutable composition before its first request.
        write_json(self.owner.group("flow") / "attachment.json", self.attachment)
        self.owner.spawn = self.spawn

    def spawn(self, caller, generation, child, *args):
        root = self.owner.root_for(caller)
        result = self.fixture.spawn(root, generation, child, *args)
        value = self.owner.meta(child)
        value["task_group_parent"] = caller
        self.fixture.fixture.save_meta(child, value)
        return result

    def submit(self, name, call="prepare", primitive="Work", caller="flow", writable=None):
        return self.owner.submit(caller, self.owner.meta(caller)["spawn_gen"],
                                 {"request_id": name, "assignment": "Scoped fixture work.",
                                  "primitive": primitive, "writable": primitive == "Work" if writable is None else writable,
                                  "workflow_call": call})

    def finish(self, request, caller="flow"):
        completed = self.fixture.complete(request)
        self.owner.status(caller, self.owner.meta(caller)["spawn_gen"],
                          gather=True, request_id=request["request"]["body"]["request_id"])
        return completed

    def test_two_dynamic_calls_have_distinct_reviews_and_repair_phases(self):
        with self.assertRaisesRegex(GroupError, "earlier authorized"):
            self.submit("too-early", "release")
        first = self.submit("prepare-work")
        self.finish(first)
        review = self.submit("prepare-review", primitive="Review")
        with self.assertRaisesRegex(GroupError, "gather Review"):
            self.submit("repair-too-early")
        self.finish(review)
        repair = self.submit("prepare-repair")
        self.assertEqual(repair["request"]["phase"], "repair")
        self.finish(repair)
        second = self.submit("release-work", "release")
        self.assertEqual(second["request"]["phase"], "work")
        self.finish(second)
        second_review = self.submit("release-review", "release", "Review")
        self.finish(second_review)
        self.assertNotEqual(review["request"]["child"], second_review["request"]["child"])
        with self.assertRaisesRegex(GroupError, "one fresh independent Review"):
            self.submit("release-extra-review", "release", "Review")
        with self.assertRaisesRegex(GroupError, "cannot reopen"):
            self.submit("prepare-late-repair")
        with self.assertRaisesRegex(GroupError, "cannot reopen"):
            self.submit("prepare-extra-review", "prepare", "Review")
        self.assertTrue(self.owner.waiting("flow")["composition_pending"], "unrun declared trial must block delivery")
        self.assertIn("prepare, release", launch_overlay(self.owner, "flow"))

    def test_build_trial_delegates_only_its_scope_and_returns_results_to_caller(self):
        trial = self.submit("trial-work")
        child = trial["request"]["child"]
        self.assertIn("authorized dynamic workflow_call IDs, in order, are: trial",
                      launch_overlay(self.owner, child))
        with self.assertRaisesRegex(GroupError, "finish every authorized"):
            self.fixture.complete(trial)
        with self.assertRaisesRegex(GroupError, "not authorized"):
            self.submit("foreign-call", "prepare", caller=child)
        nested = self.submit("trial-maker", "trial", caller=child)
        grandchild = nested["request"]["child"]
        self.assertEqual(nested["root"], child)
        self.assertEqual(self.owner.root_for(grandchild), "flow")
        self.assertEqual(self.owner.binding(grandchild)["parent"], child)
        self.assertEqual(self.owner.binding(grandchild)["group_root"], "flow")
        with self.assertRaisesRegex(GroupError, "another caller"):
            self.owner.status("flow", self.fixture.root_meta["spawn_gen"], gather=True, request_id="trial-maker")
        with self.assertRaisesRegex(GroupError, "no active scoped"):
            self.submit("too-deep", "trial", caller=grandchild)
        self.assertFalse(self.owner.waiting(child)["cleanup_allowed"])
        finished = self.finish(nested, child)
        self.assertEqual(finished["result"]["parent_at_completion"]["endpoint_task_id"], child)
        self.assertEqual(self.fixture.fixture.notices[-1][0], child)
        review = self.submit("trial-review", "trial", "Review", caller=child)
        self.finish(review, child)
        self.finish(trial)
        self.assertTrue(self.owner.waiting(child)["cleanup_allowed"])
        self.assertFalse(self.owner.waiting("flow")["cleanup_allowed"], "root phases remain incomplete")
        self.assertEqual(len(self.owner.requests("flow")), 3)
        self.assertEqual(len(self.owner.status("flow", self.fixture.root_meta["spawn_gen"])["requests"]), 1)

    def assert_no_assignment_scaffolding(self, request_id):
        child = "tg-" + digest(canonical(["flow", request_id]))[:20]
        self.assertFalse(self.owner.request_path("flow", request_id).exists())
        self.assertFalse(self.owner.task(child).exists())
        self.assertFalse((self.owner.home / "state" / (child + ".meta")).exists())

    def test_named_caller_refuses_readonly_work_and_review_before_acceptance(self):
        for primitive in ("Work", "Review"):
            with self.subTest(primitive=primitive):
                with self.assertRaisesRegex(GroupError, "root-owned writable Work"):
                    self.submit("trial-work", primitive=primitive, writable=False)
                self.assertEqual(self.owner.requests("flow"), [])
                self.assertEqual(self.fixture.records, [])
                self.assert_no_assignment_scaffolding("trial-work")
        accepted = self.submit("trial-work")
        self.assertEqual(accepted["request"]["state"], "launched")
        self.assertTrue(accepted["request"]["writable"])
        self.assertEqual(len(self.owner.requests("flow")), 1)

    def test_descendant_cannot_consume_another_named_caller_request_id(self):
        self.attachment["composition"]["calls"].append({"id": "repair-trial", "caller": "repair-work"})
        write_json(self.owner.group("flow") / "attachment.json", self.attachment)
        trial = self.submit("trial-work")
        caller = trial["request"]["child"]
        for primitive in ("Work", "Review"):
            with self.subTest(primitive=primitive):
                with self.assertRaisesRegex(GroupError, "root-owned writable Work"):
                    self.submit("repair-work", "trial", primitive=primitive, caller=caller)
                self.assertEqual(len(self.owner.requests("flow")), 1)
                self.assertEqual(len(self.fixture.records), 1)
                self.assert_no_assignment_scaffolding("repair-work")
        accepted = self.submit("repair-work")
        self.assertEqual(accepted["request"]["state"], "launched")
        self.assertEqual(accepted["request"]["parent"], "flow")
        self.assertEqual(len(self.owner.requests("flow")), 2)

    def test_selected_call_and_parent_bind_replay_and_current_generation(self):
        request = self.submit("phase-work")
        replay = self.submit("phase-work")
        self.assertEqual(request["request"], replay["request"])
        with self.assertRaisesRegex(GroupError, "different body"):
            self.submit("phase-work", "release")
        with self.assertRaisesRegex(GroupError, "not authorized"):
            self.submit("undeclared", "third")
        self.fixture.root_meta["mode"] = "no-mistakes"
        self.fixture.fixture.save_meta("flow", self.fixture.root_meta)
        with self.assertRaisesRegex(GroupError, "no-mistakes"):
            self.submit("custody-violation")

    def test_delegating_component_receives_own_context_during_launch(self):
        from fm_orchflows import launch_context
        observed = []
        def spawn_with_context(*args):
            result = self.spawn(*args)
            child = args[2]
            self.assertEqual(self.owner.component_context(child)[1]["state"], "launching")
            context = launch_context(self.owner, child, self.owner.meta(child)["spawn_gen"])
            observed.append(context)
            return result
        self.owner.spawn = spawn_with_context
        trial = self.submit("trial-work")
        child = trial["request"]["child"]
        context = read_json(observed[-1])
        self.assertEqual(context["root"], child)
        self.assertEqual(context["group_root"], "flow")
        self.assertEqual(context["generation"], "component-gen")
        self.assertEqual(Path(observed[-1]).parent, self.owner.task(child) / "orchflows-context")
        self.assertFalse((self.owner.group(child) / "attachment.json").exists())
        leaf = self.submit("ordinary-work")
        self.assertEqual(observed[-1], "", "nondelegating Work must not inherit its caller context")
        self.assertEqual(leaf["request"]["state"], "launched")

    def test_named_root_work_does_not_acquire_root_scope(self):
        child = self.submit("root")["request"]["child"]
        with self.assertRaisesRegex(GroupError, "no active scoped"):
            self.submit("escalate", "prepare", caller=child)
        self.assertNotIn("Authorized caller-context composition", launch_overlay(self.owner, child))

    def test_composition_descriptor_is_bounded_and_cannot_authorize_without_root(self):
        for bad in ({}, {"calls": []}, {"calls": [{"id": "x", "caller": "child"}]},
                    {"calls": [{"id": "x", "caller": "root"}] * 2},
                    {"calls": [{"id": "x", "caller": "root", "unlimited": True}]}):
            with self.subTest(bad=bad), self.assertRaises(GroupError):
                validate_composition(bad)


class DescendantLifecycleTests(unittest.TestCase):
    def test_component_supervision_observes_descendant_endpoints_and_guards_cleanup(self):
        import test_lifecycle_state as lifecycle
        import test_task_group as fixtures
        fixture = lifecycle.LifecycleStateTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.env["CODE"] = str(fixtures.BIN.parent)
        fixture.record.update(root="outer", component=True, child_task_id="root",
                              composition_pending=True)
        fixture.record["descendants"] = [
            dict(attached=True, root="outer", component=False, pending=True,
                 cleanup_allowed=False, child_task_id="child", child_generation="s1",
                 request_state="launched", result_ready=False, launch_active=False,
                 gathered=False)]
        fixture.write_query()
        self.assertTrue(fixture.current().startswith("waiting|"))
        out = fixture.run_bash(
            'if fm_task_group_guard "$FM_HOME" root "$STATE" teardown; then exit 9; fi; echo held')
        self.assertEqual(out, "held")
        (fixture.home / "state/child.meta").unlink()
        self.assertTrue(fixture.current().startswith("group-attention|"))


if __name__ == "__main__":
    unittest.main()
