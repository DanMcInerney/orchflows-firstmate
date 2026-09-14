"""Bounded leaf authoring on the shared dynamic acceptance lifecycle."""
from datetime import datetime
import hashlib
import json
import shlex
from pathlib import Path
import tempfile

from .authoring_fixture import INPUT, EXPECTED, LIBRARY, SKILL, REQUIRED, TESTS, spec
from .dynamic import DynamicTrial
from .local_delivery import _extend


TRIAL_FILES = ("trial-output.json", "trial-result.json", "trial-record.json")


def shell_read_target(command):
    """Recognize a full final cat, optionally preceded by harmless listings."""
    lines = [line.strip() for line in command.splitlines() if line.strip()]
    if not lines:
        return None
    try:
        for line in lines[:-1]:
            words = shlex.split(line)
            if (not words or words[0] not in ("ls", "echo")
                    or any(char in line for char in ";&|<>$" + chr(96))):
                return None
        final = lines[-1]
        if final.endswith(" 2>/dev/null"):
            final = final[:-len(" 2>/dev/null")]
        if any(char in final for char in ";&|<>$" + chr(96)):
            return None
        words = shlex.split(final)
    except ValueError:
        return None
    if len(words) == 3 and words[:2] == ["cat", "--"]:
        words.pop(1)
    return words[1] if len(words) == 2 and words[0] == "cat" else None

def full_reads(namespace, cwd, targets, *, after=0, before=float("inf"), expected_contents=None, shell_targets=()):
    """Observe complete successful native reads, scoped to one worker workspace."""
    expected = (expected_contents if expected_contents is not None else
                {str(path): (path.read_text() if path.is_file() else "") for path in targets})
    observed = {}
    for transcript in (namespace / "claude/projects").rglob("*.jsonl"):
        if transcript.is_symlink() or not transcript.resolve().is_relative_to(namespace):
            continue
        pending = {}
        for line in transcript.read_text().splitlines():
            try:
                record = json.loads(line)
                at = datetime.fromisoformat(record.get("timestamp", "")).timestamp()
            except (ValueError, TypeError):
                continue
            if record.get("cwd") != str(cwd) or record.get("isSidechain") is True:
                continue
            content = record.get("message", {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                value = block.get("input", {})
                if (block.get("type") == "tool_use" and block.get("name") == "Read"
                        and value.get("file_path") in expected and after <= at < before
                        and value.get("offset") in (None, 1) and value.get("limit") is None):
                    pending[block.get("id")] = (value["file_path"], at, "Read")
                elif (block.get("type") == "tool_use" and block.get("name") == "Bash"
                      and after <= at < before):
                    target = shell_read_target(value.get("command", ""))
                    if target in expected and target in shell_targets:
                        pending[block.get("id")] = (target, at, "Bash/cat")
                elif block.get("type") == "tool_result" and block.get("tool_use_id") in pending:
                    target, invoked, method = pending.pop(block["tool_use_id"])
                    payload = block.get("content", "")
                    if isinstance(payload, list):
                        payload = "\n".join(part.get("text", "") for part in payload if isinstance(part, dict))
                    body = expected[target]
                    complete = isinstance(payload, str) and bool(body) and all(
                        text.strip() in payload for text in body.splitlines() if text.strip())
                    if method == "Bash/cat":
                        native = record.get("toolUseResult", {})
                        stdout = native.get("stdout", "")
                        complete = (complete and native.get("interrupted") is False
                                    and isinstance(stdout, str)
                                    and body.strip() in stdout.replace("\r\n", "\n"))
                    if block.get("is_error") is not True and invoked <= at < before and complete:
                        observed[target] = {"invoked_at": invoked, "completed_at": at, "method": method,
                                            "sha256": hashlib.sha256(body.encode()).hexdigest()}
    return {"passed": bool(expected) and set(observed) == set(expected), "reads": observed,
            "missing": sorted(set(expected) - set(observed))}


class AuthoringTrial(DynamicTrial):
    expected_requests = {"author-maker-v1", "leaf-trial-v1", "final-review-v1"}
    writer_requests = {"author-maker-v1"}
    title = "Author and trial a complete non-delegating leaf workflow library"

    def fixture(self):
        project = self.namespace / "project"
        self.write_json(project / "release-input.json", INPUT)
        self.write(project / "test_delivery.py", TESTS)
        self.run(["git", "init", "-b", "main", project])
        self.run(["git", "-C", project, "add", "."])
        self.run(["git", "-C", project, "-c", "user.name=Authoring Fixture",
                  "-c", "user.email=fixture@example.invalid", "commit", "-m", "Declared authoring fixture"])
        self.receipt["input_commit"] = self.run(["git", "-C", project, "rev-parse", "HEAD"]).stdout.strip()
        self.receipt["input_files"] = {name: hashlib.sha256((project / name).read_bytes()).hexdigest()
                                       for name in ("release-input.json", "test_delivery.py")}
        return project

    def prepare_root(self, project, session):
        result = super().prepare_root(project, session)
        self.receipt.update(scope="private Linux Claude same-project leaf authoring acceptance",
                            authoring="non-delegating-leaf", portability_tested=False)
        return result

    def composition_spec(self):
        return spec(self.args.component_delay, self.delivery_instructions())

    def check_behavior(self, worktree):
        # Execute independent checks and refuse replacement of the fixture test.
        code = ("import json; from pathlib import Path; "
                f"assert Path('test_delivery.py').read_text() == {TESTS!r}; "
                f"assert json.loads(Path('release-input.json').read_text()) == {INPUT!r}; "
                f"assert json.loads(Path('trial-output.json').read_text()) == {EXPECTED!r}")
        return self.run(["python3", "-B", "-c", code], cwd=worktree, check=False)

    def git_text(self, worktree, *args):
        reply = self.run(["git", "-C", worktree, *args], check=False)
        return reply.stdout.strip() if reply.returncode == 0 else None

    def regular_evidence_blobs(self, worktree, names, revision="HEAD"):
        """Read Git modes, not filesystem targets, for delivered evidence."""
        blobs = {}
        for name in names:
            entry = self.git_text(worktree, "ls-tree", revision, "--", name)
            if not entry:
                continue
            metadata, separator, path = entry.partition("\t")
            fields = metadata.split()
            if (separator and path == name and len(fields) == 3
                    and fields[0] in ("100644", "100755") and fields[1] == "blob"):
                blobs[name] = fields[2]
        return blobs

    def committed_evidence_files(self, worktree, names):
        blobs = self.regular_evidence_blobs(worktree, names)
        return set(blobs) == set(names) and all(
            (worktree / name).is_file() and not (worktree / name).is_symlink()
            and self.git_text(worktree, "hash-object", "--no-filters", "--", name) == blob
            for name, blob in blobs.items())

    def check_trial_provenance(self, worktree, retained, *, request_id="leaf-trial-v1",
                               prefix="trial", extra_identities=None):
        """Bind either delivered snapshot to the same immutable owner evidence."""
        author = retained.get("author-maker-v1", {})
        trial = retained.get(request_id, {})
        names = ("trial_json_from_fresh_worker", "exact_trial_output_committed",
                 "exact_retained_trial_result_committed", "committed_trial_identities")
        checks = dict.fromkeys(names, False)
        child = trial.get("child")
        if not child:
            return checks
        report = self.owner_home / "data" / self.root / "task-group/results" / child / "report.md"
        try:
            payload = report.read_bytes()
            result_bytes = report.with_name("result.json").read_bytes()
            canonical = json.dumps(trial, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
            identities = {
                "author_output_commit": author.get("output_commit"),
                "trial_input_commit": trial.get("input_commit"), "trial_child": child,
                "request_id": request_id,
                "result_digest": hashlib.sha256(canonical).hexdigest(),
                "report_digest": trial.get("report_digest"),
            }
            identities.update(extra_identities or {})
            record = json.loads((worktree / (prefix + "-record.json")).read_text())
            checks.update(
                trial_json_from_fresh_worker=json.loads(payload) == EXPECTED,
                exact_trial_output_committed=(worktree / (prefix + "-output.json")).read_bytes() == payload,
                exact_retained_trial_result_committed=(worktree / (prefix + "-result.json")).read_bytes() == result_bytes
                    and json.loads(result_bytes) == trial,
                committed_trial_identities=all(value and record.get(key) == value
                                               for key, value in identities.items()))
        except (OSError, ValueError):
            pass
        return checks

    def check_reviewed_candidate(self, worktree, reviewed, retained):
        author = retained.get("author-maker-v1", {})
        trial = retained.get("leaf-trial-v1", {})
        checks = {"distinct_candidate": bool(reviewed) and reviewed != self.receipt["input_commit"],
                  "reviewed_trial_evidence_regular_blobs": bool(reviewed) and set(
                      self.regular_evidence_blobs(worktree, TRIAL_FILES, reviewed)) == set(TRIAL_FILES)}
        trees = {}
        for label, commit in (("author", author.get("output_commit")),
                              ("trial", trial.get("input_commit")), ("reviewed", reviewed)):
            trees[label] = self.git_text(worktree, "rev-parse", commit + ":" + LIBRARY) if commit else None
        checks["same_authored_trialed_reviewed_library"] = bool(trees.get("author")) and len(set(trees.values())) == 1
        hashes = {}
        if reviewed:
            with tempfile.TemporaryDirectory(prefix="authored-review-", dir=self.namespace) as temp:
                snapshot = Path(temp)
                names = self.git_text(worktree, "ls-tree", "-r", "--name-only", reviewed)
                for name in (names or "").splitlines():
                    path = Path(name)
                    if path.is_absolute() or ".." in path.parts:
                        raise ValueError("Review contains an invalid fixture path")
                    reply = self.run(["git", "-C", worktree, "show", reviewed + ":" + name], check=False)
                    if reply.returncode:
                        continue
                    target = snapshot / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(reply.stdout)
                    hashes[name] = hashlib.sha256(reply.stdout.encode()).hexdigest()
                checks.update({"reviewed_" + key: value for key, value
                               in self.check_trial_provenance(snapshot, retained).items()})
                behavior = self.check_behavior(snapshot)
                tests = self.run(["python3", "-B", "-m", "unittest", "discover", "-v"], cwd=snapshot, check=False)
                checks["reviewed_behavior"] = behavior.returncode == 0
                checks["reviewed_tests"] = tests.returncode == 0 and "Ran 0 tests" not in tests.stderr
                self.write(self.out / "reviewed-tests.log", tests.stdout + tests.stderr)
        return {"passed": all(checks.values()), "checks": checks, "library_trees": trees, "files_sha256": hashes}

    def collect_dynamic(self, result, project):
        super().collect_dynamic(result, project)
        metas, retained = result["metadata"], result["retained_results"]
        parent = metas.get(self.root, {})
        worktree = Path(parent.get("worktree", "/nonexistent"))
        requests = {r["body"]["request_id"]: r for r in result["requests"]}
        trial = retained.get("leaf-trial-v1", {})
        author = retained.get("author-maker-v1", {})
        review_request = requests.get("final-review-v1", {})
        child = trial.get("child")
        child_tree = Path(metas.get(child, {}).get("worktree", "/nonexistent"))
        checks = {
            "author_writer_and_fresh_readonly_trial": author.get("writable") is True
                and trial.get("writable") is False and trial.get("primitive") == "Work"
                and bool(child) and child != author.get("child"),
        }
        checks.update(self.check_trial_provenance(worktree, retained))
        checks["trial_evidence_regular_committed_blobs"] = self.committed_evidence_files(worktree, TRIAL_FILES)
        package = Path(result["client_path"]).parents[1]
        relative_targets = [LIBRARY + "/" + SKILL, LIBRARY + "/references/library-context.md",
                            LIBRARY + "/guidance/release.md", "release-input.json"]
        expected_contents = {}
        for relative in relative_targets:
            reply = (self.run(["git", "-C", project, "show", trial["input_commit"] + ":" + relative],
                              check=False) if trial.get("input_commit") else None)
            expected_contents[str(child_tree / relative)] = reply.stdout if reply and reply.returncode == 0 else ""
        writing = package / "guidance/writing.md"
        expected_contents[str(writing)] = writing.read_text() if writing.is_file() else ""
        child_reads = full_reads(self.namespace, child_tree,
            [child_tree / p for p in relative_targets] + [writing],
            before=requests.get("leaf-trial-v1", {}).get("gathered_at", 0),
            expected_contents=expected_contents, shell_targets={str(writing)})
        checks["fresh_trial_read_declared_context"] = child_reads["passed"]
        result["leaf_trial_native_reads"] = child_reads
        root_targets = [package / "skills/orch-build-workflow/SKILL.md",
                        package / "guidance/orchflows.md", package / "guidance/writing.md",
                        worktree / LIBRARY / SKILL, worktree / LIBRARY / "references/library-context.md",
                        worktree / LIBRARY / "guidance/release.md"]
        after = result.get("replacement", {}).get("requested_at", 0) if self.args.restart else 0
        root_expected = {str(target): target.read_text() if target.is_file() else ""
                         for target in root_targets}
        # The pre-Review reads concern the trial input, even if later repairs
        # change the final worktree's leaf prose.
        for relative in relative_targets[:-1]:
            root_expected[str(worktree / relative)] = expected_contents[str(child_tree / relative)]
        root_reads = full_reads(self.namespace, worktree, root_targets, after=after,
                               before=review_request.get("accepted_at", 0),
                               expected_contents=root_expected)
        checks["authoring_context_reapplied_before_review"] = root_reads["passed"]
        result["authoring_root_native_reads"] = root_reads
        checks.update(self.final_library_checks(worktree, result))
        trial_request = requests.get("leaf-trial-v1", {})
        checks["trial_gathered_before_review"] = (isinstance(trial_request.get("gathered_at"), (int, float))
            and trial_request["gathered_at"] < review_request.get("accepted_at", 0))
        _extend(result, checks)


    def final_library_checks(self, worktree, result):
        trial = result["retained_results"].get("leaf-trial-v1", {})
        final_tree = self.git_text(worktree, "rev-parse", "HEAD:" + LIBRARY)
        trial_tree = (self.git_text(worktree, "rev-parse", trial["input_commit"] + ":" + LIBRARY)
                      if trial.get("input_commit") else None)
        return {"final_library_has_exact_trial_evidence": bool(trial_tree) and final_tree == trial_tree}
