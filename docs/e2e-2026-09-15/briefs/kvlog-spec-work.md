This is the spec phase of the mixed-build:feature workflow: one Orchflows Work as a read-only scout. Do not change project files, do not delegate to subagents; one agent owns this result. Your deliverable is the design and acceptance checklist in your report.

## Read first, then apply the Make sections

- CORE_PATH/guidance/writing.md (Make section)
- CORE_PATH/guidance/code.md (Make section)
- LIB_PATH/guidance/code.cli.md (Make section; it specializes code for command-line tools)

## Assignment

Design kvlog from the captain's request above, for a Python 3 standard-library implementation. Inspect the repository in your worktree (it holds only a README stub). Write the report with these sections:

1. Scope and non-goals, in a few sentences.
2. Command-line contract: every option with its default and effect, input sources (files and stdin), output format for the human summary and for --json (give the exact JSON shape with field names), exit codes 0, 1 and 2 with their triggers, and what goes to stderr.
3. Module layout: files to create, the public functions and their responsibilities, and where parsing, filtering, aggregation and rendering live. Keep it to what a single maker can build in one sitting.
4. Edge cases the implementation must handle: blank lines, malformed JSON with the line number, missing required keys, extra keys, timezone-aware timestamps, an empty input, --top larger than the number of distinct errors, --since or --until that exclude everything.
5. Test plan: the unit tests to write, by name, each with what it proves.
6. Acceptance checklist: numbered, each item a command to run and the exact observable result, covering every option, every exit code, stdin and file input, --json shape, and the README. The docs-qa reviewer will execute this list against the delivered artifact, so make every item mechanically checkable.

Keep decisions concrete; where the request is silent, decide and say so. Write the report at the path this brief names for a scout report, then follow the scout definition of done.