"""Origin-backed local delivery through the actual merge owner; no model workers."""
import subprocess
import unittest

import test_local_delivery as local
from fm_task_group_store import GroupError, clean_commit


class RegisteredProjectTests(unittest.TestCase):
    def setUp(self):
        self.flow = local.LocalDeliveryTests()
        self.flow.setUp()
        self.addCleanup(self.flow.doCleanups)
        self.fixture = self.flow.fixture
        self.remote = self.fixture.base / "origin.git"
        subprocess.run(["git", "clone", "--bare", "-q", str(self.fixture.project), str(self.remote)], check=True)
        self.fixture.git("remote", "add", "origin", str(self.remote))
        self.fixture.git("fetch", "-q", "origin")
        self.fixture.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")

    def test_origin_backed_work_review_and_ordinary_local_landing_never_push(self):
        initial = self.fixture.git("rev-parse", "main")
        self.assertEqual(clean_commit(self.fixture.project), initial)
        result = self.flow.ready_output()
        landed = self.flow.merge()
        self.assertEqual(landed.returncode, 0, landed.stderr)
        final = self.fixture.git("rev-parse", "main")
        self.assertNotEqual(final, initial)
        self.assertEqual(final, self.flow.git_at(self.flow.root_worktree, "rev-parse", "HEAD"))
        self.assertEqual(self.fixture.git("rev-parse", result["result"]["output_ref"]),
                         result["result"]["output_commit"])
        remote = subprocess.run(["git", "--git-dir", str(self.remote), "rev-parse", "main"],
                                check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual(remote, initial, "local-only landing must not push to origin")

    def test_origin_does_not_relax_dirty_or_nonregular_input_guards(self):
        (self.fixture.project / "dirty.txt").write_text("unfinished")
        with self.assertRaisesRegex(GroupError, "dirty"):
            clean_commit(self.fixture.project)
        (self.fixture.project / "dirty.txt").unlink()
        (self.fixture.project / "linked.txt").symlink_to("input.txt")
        self.fixture.git("add", "linked.txt")
        self.fixture.git("commit", "-qm", "unsupported tracked link")
        with self.assertRaisesRegex(GroupError, "symlinks"):
            clean_commit(self.fixture.project)


if __name__ == "__main__":
    unittest.main()
