# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Add durable project-specific notes here as they are discovered through real work.
- Entry point is `roman.py` at the repository root, runnable as `python3 roman.py ...`; see `README.md` for usage. Standard library only, no third-party dependencies.
- Tests live in `tests/test_roman.py` and run with `python3 -m unittest` from the repository root. `tests/__init__.py` must stay present — without it, bare `python3 -m unittest` silently discovers 0 tests on this Python version (3.12.3), even though `unittest discover` documents namespace-package support.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
