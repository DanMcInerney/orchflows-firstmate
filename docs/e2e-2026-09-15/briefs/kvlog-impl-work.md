This is the implement phase of the mixed-build:feature workflow: one Orchflows Work as a ship in this project's delivery mode. Do not delegate to subagents; one agent owns this result.

## Inputs

- The spec report at SPEC_REPORT_PATH: read it in full and implement exactly what it specifies. Where the spec and the captain's request above disagree, the request wins; say so in your commit message.
- The reviewed repairs to that spec, if any, at SPEC_REVIEW_PATH (findings the spec author already addressed; read them so you know the decisions).

## Read first, then apply the Make sections

- CORE_PATH/guidance/code.md (Make section)
- LIB_PATH/guidance/code.cli.md (Make section)

## Assignment

Implement kvlog in this worktree per the spec's module layout and command-line contract, with the unit tests from the spec's test plan. Python 3 standard library only. Run the tests with python3 -m unittest and make them pass. Run every item of the spec's acceptance checklist that concerns the code (not the README) and fix what fails; list in your final status note any checklist item you could not satisfy and why. Do not write the README beyond a one-line placeholder; the docs-qa phase owns it.

Commit on your branch with a clear message, then follow this brief's local-only definition of done exactly.