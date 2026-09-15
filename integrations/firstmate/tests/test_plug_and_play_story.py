"""Saved composition through real Linux owners; no live-model evidence.

Dispatch injects native Git worktrees and metadata using the existing fixture.
Publication, brief selection, profile preflight, retained catalogs/results,
composition guards and local landing use the prepared FirstMate owners.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
import unittest

import test_task_group as fixtures
from fm_orchflows import auto_attach, launch_context
from fm_orchflows_home import catalog, publish, resolve, workflow_home
from fm_task_group_launch import launch_check, launch_meta
from fm_task_group_store import GroupError, git, read_json


class PlugAndPlayStoryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.candidate = Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"])
        self.owner.code_root = self.candidate
        self.owner.spawn = self.spawn
        self.spawned = []
        self.base = self.fixture.base
        self.project = self.fixture.project
        self.fixture.git("branch", "-M", "main")
        (self.owner.home / "projects").mkdir()
        (self.owner.home / "projects/project").symlink_to(self.project, target_is_directory=True)
        self.package = self.base / "complete-package"
        source = Path(__file__).resolve().parents[3] / "packages/orchflows-firstmate"
        shutil.copytree(source, self.package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.author_project = self.base / "workflow-authoring"
        self.author_project.mkdir()
        git(self.author_project, "init", "-q", "-b", "main")
        git(self.author_project, "config", "user.email", "fixture@example.invalid")
        git(self.author_project, "config", "user.name", "Fixture")
        (self.author_project / "README.md").write_text("Saved workflow source.\n")
        git(self.author_project, "add", "README.md")
        git(self.author_project, "commit", "-qm", "initial authoring project")
        (self.owner.home / "projects/workflow-authoring").symlink_to(
            self.author_project, target_is_directory=True)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("FM_", "HERDR_", "ORCHFLOWS_"))}
        self.env.update(FM_HOME=str(self.owner.home), FM_ROOT_OVERRIDE=str(self.candidate), FM_SPAWN_NO_GUARD="1")
        self.root, self.generation = "release-run", "story-generation"

    def write_library(self, revision):
        """Fixture-authored library lands through ordinary local-only delivery."""
        task = "save-workflow-" + str(revision)
        worktree = self.base / (task + "-worktree")
        git(self.author_project, "worktree", "add", "-b", "fm/" + task, str(worktree), "HEAD")
        root = worktree / "libraries/release"
        preferences = {
            "assignments": {"prepare-maker": {"effort": "low"}},
            "operations": {"Work": {"model": "claude-sonnet-5", "effort": "medium"},
                           "Review": {"model": "claude-opus-4-6", "effort": "high"}},
        }
        manifest = {
            "name": "release", "version": str(revision), "skills": "./skills/",
            "firstmate": {"workflows": {"ship": {
                "composition": {"calls": [{"id": "prepare", "caller": "root"},
                                            {"id": "verify", "caller": "root"}]},
                "preferences": preferences,
            }}},
        }
        files = {
            "plugin.json": json.dumps(manifest, indent=2) + "\n",
            "README.md": "Prepare and verify a release through two dynamic calls.\n",
            "skills/ship/SKILL.md":
                "# Ship a release, revision " + str(revision) + "\n\n"
                "Read guidance/release.md and references/checklist.md from this library.\n"
                "Load orchflows:orch-dynamic-workflow in this caller for prepare, then verify.\n"
                "Each call makes scoped Work, joins/checks it, gets one fresh Review, "
                "and makes one repair/check pass. Pass workflow_call prepare or verify "
                "to the corresponding Work and Review requests.\n",
            "guidance/release.md": "Retain all release facts and their source.\n",
            "references/checklist.md": "Confirm prepared notes preserve every input fact.\n",
            "trials/input.txt": "Two crates remain. The release is ready.\n",
            "scripts/check.py": "import json,sys\nassert json.load(open(sys.argv[1]))['ready']\n",
        }
        for relative, text in files.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        (root / "assets").mkdir(exist_ok=True)
        (root / "assets/release.bin").write_bytes(bytes(range(256)) + bytes([revision]))
        git(worktree, "add", "libraries/release")
        git(worktree, "commit", "-qm", "deliver release workflow " + str(revision))
        metadata = {key: value for key, value in self.fixture.root_meta.items()
                    if not key.startswith("task_group_")}
        metadata.update(endpoint_task_id=task, kind="ship", mode="local-only", yolo="on",
                        worktree=str(worktree), project=str(self.author_project))
        self.fixture.save_meta(task, metadata)
        landed = subprocess.run(["bash", str(self.candidate / "bin/fm-merge-local.sh"), task],
                                env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(landed.returncode, 0, landed.stderr)
        self.assertEqual(git(self.author_project, "rev-parse", "main"), git(worktree, "rev-parse", "HEAD"))
        return git(self.author_project, "rev-parse", "HEAD"), self.author_project / "libraries/release"

    @staticmethod
    def files(root):
        return {path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*") if path.is_file()}

    def ordinary_brief(self, task):
        result = subprocess.run(
            ["bash", str(self.candidate / "bin/fm-brief.sh"), task, "project",
             "--mode", "local-only", "--orchflows-skill", "release:ship"],
            env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        brief = self.owner.task(task) / "brief.md"
        text = brief.read_text()
        self.assertIn("Orchflows selected skill: release:ship", text)
        self.assertIn("Delivery contract: mode=local-only", text)
        brief.write_text(text.replace("{TASK}", "Prepare and verify the release.")
                        .replace("{FIRSTMATE_SPEC}", "Invoke the selected saved release workflow."))

    def attach(self, task):
        self.ordinary_brief(task)
        self.assertEqual(auto_attach(self.owner, task, "ship", "herdr", "claude",
                                     self.project, workflow="default", mode="local-only"), "root")
        return self.owner.attachment(task)

    def spawn(self, caller, generation, child, project, harness, model, effort):
        """Inject only dispatch; retain FirstMate's request, metadata and result API."""
        binding, record, _ = self.owner.component_context(child)
        self.assertEqual(record["state"], "launching")
        self.assertEqual((record["harness"], record["model"], record["effort"]), (harness, model, effort))
        launch_check(self.owner, child, "scout", "herdr", harness, project)
        worktree = self.base / (child + "-worktree")
        git(project, "worktree", "add", "--detach", str(worktree), record["input_commit"])
        launch_check(self.owner, child, "scout", "herdr", harness, project, worktree)
        tasktmp = self.base / (child + "-tmp")
        tasktmp.mkdir()
        metadata = {
            "endpoint_task_id": child, "spawn_gen": "component-generation", "backend": "herdr",
            "kind": "scout", "harness": harness, "model": model, "effort": effort,
            "project": str(project), "worktree": str(worktree), "tasktmp": str(tasktmp),
            "herdr_session": "fixture-only", "herdr_workspace_id": child,
            "herdr_tab_id": "tab", "herdr_pane_id": "pane", "window": child,
        }
        metadata.update(self.fixture.fields(launch_meta(self.owner, child)))
        self.fixture.save_meta(child, metadata)
        self.spawned.append(child)
        return SimpleNamespace(returncode=0)

    def submit(self, request_id, workflow_call, primitive="Work", **controls):
        body = dict(request_id=request_id, workflow_call=workflow_call,
                    assignment="Apply the saved release workflow's " + workflow_call + " phase.",
                    primitive=primitive, writable=primitive == "Work", **controls)
        return self.owner.submit(self.root, self.generation, body), body

    def finish_and_gather(self, view, filename=None, content=None):
        child = view["request"]["child"]
        metadata = self.owner.meta(child)
        if filename:
            worktree = Path(metadata["worktree"])
            (worktree / filename).write_text(content, encoding="utf-8")
            git(worktree, "add", filename)
            git(worktree, "commit", "-qm", "fixture output " + filename)
        report = Path(metadata["tasktmp"]) / "report.md"
        payload = ("# Complete deterministic fixture report\n\n"
                   + "Observed release fact and its source.\n" * 300
                   + "\nFinal retained evidence marker.\n").encode()
        report.write_bytes(payload)
        completed = self.owner.complete(child, "component-generation", report)
        # Read complete retained artifacts before acknowledging consumption.
        self.assertEqual(Path(completed["report_path"]).read_bytes(), payload)
        self.assertEqual(read_json(Path(completed["result_path"])), completed["result"])
        gathered = self.owner.status(self.root, self.generation, gather=True,
                                     request_id=view["request"]["body"]["request_id"])
        self.assertTrue(gathered["request"]["gathered"])
        self.assertEqual(gathered["result"], completed["result"])
        if filename:
            git(self.worktree, "cherry-pick", completed["result"]["output_commit"])
        return completed

    def public_client(self, attachment, context, *arguments):
        # Exercise capability negotiation against the real prepared controller,
        # never the test client's mocked protocol. Replay cannot spawn a worker.
        client = Path(attachment["package_path"]) / "scripts/firstmate.py"
        result = subprocess.run(["python3", "-B", str(client), "--context", str(context), *arguments],
                                env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_create_save_reuse_two_phases_profiles_delivery_and_updated_snapshot(self):
        original_commit, library = self.write_library(1)
        expected = self.files(library)
        publication = publish(self.owner, self.author_project, "libraries/release",
                              original_commit, package=self.package)
        self.assertEqual(publication["commit"], original_commit)
        home = workflow_home(self.owner)
        self.assertEqual(home, self.owner.home / "data/.orchflows-home")
        self.assertEqual(self.files(home / "libraries/release"), expected)
        self.assertIn("release:ship", [item["identity"] for item in catalog(self.owner)["workflows"]])
        self.assertEqual(resolve(self.owner, "release:ship")["identity"], "release:ship")

        attachment = self.attach(self.root)
        self.assertEqual(attachment["selected_workflow"], "release:ship")
        retained = Path(attachment["package_path"]) / "firstmate-libraries/release"
        self.assertEqual(self.files(retained), expected)
        self.assertEqual(self.spawned, [], "loading a selected workflow must not dispatch")
        self.worktree = self.base / "release-run-worktree"
        git(self.project, "worktree", "add", "-b", "fm/" + self.root, str(self.worktree), "HEAD")
        root_meta = dict(self.fixture.root_meta, endpoint_task_id=self.root, kind="ship",
                         mode="local-only", yolo="on", spawn_gen=self.generation,
                         worktree=str(self.worktree), model="parent-session-model", effort="max")
        root_meta.update(self.fixture.fields(launch_meta(self.owner, self.root)))
        self.fixture.save_meta(self.root, root_meta)
        context_path = Path(launch_context(self.owner, self.root, self.generation))
        context_bytes = context_path.read_bytes()
        public = self.public_client(attachment, context_path, "status")
        self.assertEqual(public["attachment"]["composition"], attachment["composition"])
        self.assertEqual(public["requests"], [])

        maker, maker_body = self.submit("prepare-maker", "prepare", model="claude-sonnet-5",
                                       operation_defaults={"effort": "medium"})
        profile = maker["request"]["profile"]
        self.assertEqual((profile["model"], profile["effort"]), ("claude-sonnet-5", "medium"))
        self.assertEqual(profile["sources"], {"model": "caller-named", "effort": "caller-operation"})
        self.assertEqual(self.owner.meta(maker["request"]["child"])["model"], profile["model"])
        self.assertEqual(self.owner.meta(maker["request"]["child"])["effort"], profile["effort"])
        self.assertEqual(self.owner.submit(self.root, self.generation, maker_body)["request"], maker["request"])
        self.assertEqual(len(self.spawned), 1)
        request_path = self.base / "public-replay.json"
        request_path.write_text(json.dumps(maker_body))
        public = self.public_client(attachment, context_path, "submit", "--request", str(request_path))
        self.assertEqual(public["request"]["child"], maker["request"]["child"])
        self.assertEqual(public["request"]["profile"], profile)
        self.assertEqual(len(self.spawned), 1)
        with self.assertRaisesRegex(GroupError, "earlier authorized"):
            self.submit("premature-next-phase", "verify")
        with self.assertRaisesRegex(GroupError, "different body"):
            self.owner.submit(self.root, self.generation, {**maker_body, "effort": "high"})
        prepared = self.finish_and_gather(maker, "release-notes.md", "Two crates remain. The release is ready.\n")
        audit, _ = self.submit("prepare-review", "prepare", "Review")
        self.assertEqual(audit["request"]["input_commit"], git(self.worktree, "rev-parse", "HEAD"))
        self.assertEqual((audit["request"]["model"], audit["request"]["effort"]), ("claude-opus-4-6", "high"))
        self.assertEqual(audit["request"]["profile"]["sources"], {"model": "saved-operation", "effort": "saved-operation"})
        self.assertNotEqual(audit["request"]["child"], maker["request"]["child"])
        first_review = self.finish_and_gather(audit)
        with self.assertRaisesRegex(GroupError, "only one fresh"):
            self.submit("duplicate-prepare-review", "prepare", "Review")
        self.assertFalse(self.owner.waiting(self.root)["cleanup_allowed"])

        # Publish from the separately delivered authoring project during this run.
        changed_commit, library = self.write_library(2)
        changed = self.files(library)
        updated = publish(self.owner, self.author_project, "libraries/release", changed_commit)
        self.assertIn(str(self.project), updated["refreshed_projects"])
        future = self.attach("release-next")
        future_library = Path(future["package_path"]) / "firstmate-libraries/release"
        self.assertNotEqual(future["package_digest"], attachment["package_digest"])
        self.assertEqual(self.files(future_library), changed)
        self.assertEqual(self.files(retained), expected)
        self.assertEqual(self.owner.attachment(self.root), attachment)
        self.assertEqual(context_path.read_bytes(), context_bytes)
        self.assertEqual(len(self.spawned), 2, "publishing/selection must not start a worker")
        replay = self.owner.submit(self.root, self.generation, maker_body)
        self.assertEqual(replay["request"]["child"], maker["request"]["child"])
        self.assertEqual(replay["request"]["profile"], profile)
        self.assertEqual(replay["result"], prepared["result"])

        verify, _ = self.submit("verify-maker", "verify", effort="high")
        self.assertEqual(verify["request"]["phase"], "work")
        checked = self.finish_and_gather(verify, "release-check.json", '{"ready": true}\n')
        final_review, _ = self.submit("verify-review", "verify", "Review")
        self.assertNotEqual(final_review["request"]["child"], audit["request"]["child"])
        reviewed = self.finish_and_gather(final_review)
        self.assertEqual(len(self.spawned), 4)
        self.assertTrue(self.owner.waiting(self.root)["cleanup_allowed"])

        landed = subprocess.run(["bash", str(self.candidate / "bin/fm-merge-local.sh"), self.root],
                                env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(landed.returncode, 0, landed.stderr)
        self.assertEqual(git(self.project, "rev-parse", "main"), git(self.worktree, "rev-parse", "HEAD"))
        self.assertEqual((self.project / "release-notes.md").read_text(), "Two crates remain. The release is ready.\n")
        self.assertEqual(read_json(self.project / "release-check.json"), {"ready": True})
        check = subprocess.run(["python3", str(retained / "scripts/check.py"), str(self.project / "release-check.json")],
                               env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(check.returncode, 0, check.stderr)
        for completed in (prepared, first_review, checked, reviewed):
            self.assertEqual(read_json(Path(completed["result_path"])), completed["result"])
            self.assertIn(b"Final retained evidence marker.", Path(completed["report_path"]).read_bytes())
        for completed in (prepared, checked):
            self.assertEqual(git(self.project, "rev-parse", completed["result"]["output_ref"]), completed["result"]["output_commit"])
        self.assertEqual(self.files(retained), expected)


if __name__ == "__main__":
    unittest.main()
