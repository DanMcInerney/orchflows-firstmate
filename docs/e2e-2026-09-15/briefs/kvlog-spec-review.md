This is the spec phase Review of the mixed-build:feature workflow: an independent read-only audit by a fresh agent who did not write the spec. Do not edit any file, do not delegate. Your deliverable is findings with evidence in your report.

## Candidate

The spec report at SPEC_REPORT_PATH (read it in full). The repository in your worktree holds only a README stub; the spec is the whole candidate.

## Intended outcome

A design and acceptance checklist that a single maker can implement without asking questions, and that a later reviewer can execute mechanically against the delivered tool. The captain's request above is the contract the spec must satisfy.

## Read first, then apply the Review sections

- CORE_PATH/guidance/writing.md (Review section)
- CORE_PATH/guidance/code.md (Review section)
- LIB_PATH/guidance/code.cli.md (Review section)

## Checks to perform

1. Every requirement in the captain's request is covered: files and stdin, the five summary parts, --json, --top N, --since, --until, --help, exit codes 0, 1 with the line number on stderr, and 2, unit tests under python3 -m unittest, a README, no third-party dependencies. Quote any requirement the spec drops or contradicts.
2. Ambiguities a maker would have to guess: option semantics, JSON field names and types, tie-breaking for top errors, inclusive or exclusive time bounds, timezone handling, behavior on empty input.
3. The acceptance checklist: is every item a concrete command with an exact expected result? Flag items a reviewer could not execute or could not judge.
4. Anything in the design that violates the code or code.cli guidance, or is more machinery than the request needs.

Write the report at the path this brief names for a scout report. Order findings by impact with a quote or section reference for each, and end with a verdict: ready, ready with the listed repairs, or not ready. Then follow the scout definition of done.