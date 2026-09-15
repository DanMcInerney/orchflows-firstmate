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

## End-to-end trial complete (September 15, 2026)

[docs/e2e-trial-2026-09-15.md](docs/e2e-trial-2026-09-15.md) records a live trial on stock FirstMate `b182d0f` with Herdr in Ubuntu/WSL. Half A: `orch-build-workflow` produced the `mixed-build:feature` library (Sonnet xhigh author, fresh Sonnet xhigh reviewer, one steer repair, `fm-merge-local.sh` landing, catalogs published). Half B: that workflow built `kvlog` through six FirstMate agents alternating Codex `gpt-5.6-luna` xhigh and Claude `claude-sonnet-5` xhigh, three steer repairs and two local-only landings; final artifact verified (20 tests, 17 acceptance items, README outputs exact). Evidence, briefs, steers and driver helpers are in `docs/e2e-2026-09-15/`; the trial record is committed into the library's `trials/`. The Linux trial state under `/tmp/orchflows-e2e` does not survive a reboot.

## Next

1. Fold the trial's lessons into `docs/firstmate.md`: local-only projects carry no origin remote; reviewers need the detached-checkout instruction; makers need "do not delegate" and a fresh `done` line after a repair steer; expect Codex first-run dialogs and `blocked:` lines from tooling limits.
2. Run one task through a model-driven FirstMate primary with the package installed, to show the primary itself follows the skills.
3. Decide whether no-mistakes projects keep Orchflows' own Review or treat no-mistakes as the Review; `docs/firstmate.md` documents both.

## Constraints

- No FirstMate changes, no subagents inside workers, no runtime in the package.
- Keep guidance and example libraries identical to upstream unless a trial shows a defect.
- `.sources/` and `.scratch/` are ignored local research copies and stay unchanged.
