# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Add durable project-specific notes here as they are discovered through real work.
- Single-file stdlib CLI: `tally.py` at the repo root, runnable as `python3 tally.py ...` or `python3 -m tally ...` (both must be invoked from the repo root). See `README.md` for usage, the word-definition/tokenization rule, tie-break ordering, output formats, and the exit-code scheme (0/1/2).
- Standard library only, by explicit project requirement — do not add third-party dependencies to this tool even where they'd simplify things.
- Tests: `python3 -m unittest` from the repo root (`tests/test_tally.py`). CLI behavior is tested via subprocess against temp files/stdin; keep new tests independent (own temp fixtures, no shared/global state).

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
