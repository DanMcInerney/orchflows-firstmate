This is the docs-qa phase of the mixed-build:feature workflow: one Orchflows Work as a ship in this project's delivery mode. Do not delegate to subagents; one agent owns this result.

## Inputs

- The spec report at SPEC_REPORT_PATH, in particular its acceptance checklist and command-line contract.
- The implementation already merged on main in this repository; the implement-phase Review at IMPL_REVIEW_PATH lists what was checked and repaired.

## Read first, then apply the Make sections

- CORE_PATH/guidance/writing.md (Make section)
- LIB_PATH/guidance/code.cli.md (Make section)

## Assignment

1. Write README.md: what kvlog does in two sentences, install (none beyond Python 3), usage with real commands and their real output produced by running the tool on a small sample file you add under examples/, every option with its default, the --json shape, exit codes, and how to run the tests. Every command in the README must actually work; paste real output, not invented output.
2. Run the complete acceptance checklist from the spec, every item, and record the result in ACCEPTANCE.md as a table: item number, command, expected, actual, pass or fail. Fix any code defect you find that is needed to make an item pass, keeping the fix minimal and covered by a unit test; do not redesign anything.
3. Run python3 -m unittest and make sure it passes.

Commit on your branch with a clear message, then follow this brief's local-only definition of done exactly.