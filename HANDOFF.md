# Handoff

## Direction (September 15, 2026)

The user redirected the project. FirstMate launches agents natively as it always has; this library supplies Orchflows' pattern for how that work is done: two terse composable skills, workflows built from workflows, per-agent model and effort, the dynamic workflow as FirstMate's default, and custom workflows that run only when named. Plug-and-play means nothing in FirstMate changes. [docs/plan.md](docs/plan.md) records the decisions and acceptance.

## State

This increment:

- Retired `integrations/firstmate/` (nine FirstMate patches plus the task-group controller, bridge and overlay), `tools/`, the package client `scripts/firstmate.py`, `host_config.py`, `native_logs.py` and their tests. Their research and evidence moved to [archive/research](archive/research/README.md).
- Rewrote the five skills at upstream length. Work and Review dispatch fresh FirstMate crewmates and scouts through `fm-brief.sh` and `fm-spawn.sh`; the dynamic workflow adds FirstMate's constraints; build-workflow ships into the home library; self-improve reads FirstMate task records.
- Rewrote `docs/architecture.md`, `hosts.md`, `home.md`, `history.md` and added `docs/firstmate.md` (install, `captain.md` block, dispatch rules, command mapping, delivery modes, durable state).
- Reduced `scripts/orchflows.py` to setup, doctor and resolve. Guidance and example libraries are unchanged from upstream.
- Package version `0.2.0`. The 29 package tests pass on Windows (Python 3.14) and Ubuntu in WSL (Python 3.12), including the installed-core link check.

## Next

1. Trial the dynamic workflow through a real FirstMate primary on a disposable project: one Work ship in local-only mode, one Review scout, one steer. Record the brief text that worked and fold improvements into `docs/firstmate.md`.
2. Author a two-phase saved workflow with orch-build-workflow into the home and run it by name.
3. Confirm or rule out a manual-only skill flag for a Codex primary; the Claude Code flag is documented in `docs/hosts.md`.
4. Decide whether no-mistakes projects should keep Orchflows' own Review or treat no-mistakes as the Review; `docs/firstmate.md` documents both.

## Constraints

- No FirstMate changes, no subagents inside workers, no runtime in the package.
- Keep guidance and example libraries identical to upstream unless a trial shows a defect.
- `.sources/` and `.scratch/` are ignored local research copies and stay unchanged.
