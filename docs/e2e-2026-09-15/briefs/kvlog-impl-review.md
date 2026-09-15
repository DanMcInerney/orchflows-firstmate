This is the implement phase Review of the mixed-build:feature workflow: an independent read-only audit by a fresh agent who did not write the code. Do not edit any file, do not delegate. Your deliverable is findings with evidence in your report.

## Candidate

Branch BRANCH of this repository. In your scratch worktree run: git checkout --detach BRANCH (the branch exists locally; git branch -a lists it). Record the commit SHA you reviewed at the top of your report. Run the tests and the tool yourself; a read-only review may execute the candidate.

## Intended outcome

The spec at SPEC_REPORT_PATH, implemented in Python 3 standard library with passing unit tests. The captain's request above is the contract behind that spec.

## Read first, then apply the Review sections

- CORE_PATH/guidance/code.md (Review section)
- LIB_PATH/guidance/code.cli.md (Review section)

## Checks to perform

1. Run python3 -m unittest in the worktree and report the result verbatim.
2. Execute every acceptance checklist item from the spec that concerns the code (skip README items) and record pass or fail per item with the actual output for failures.
3. Contract conformance: every option, exit code, stdin and file input, --json shape and stderr behavior against the spec; quote deviations with file and line.
4. Code Review guidance: duplicated ownership, tests coupled through shared state, oversized files, error handling that swallows malformed input.
5. Anything that would break for a real user: crashes on edge cases the spec lists, wrong counts, wrong time-window filtering, timezone bugs.

Write the report at the path this brief names for a scout report. Order findings by impact with file and line references, and end with a verdict: ready, ready with the listed repairs, or not ready. Then follow the scout definition of done.