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

## Model-driven primary trial complete (September 15, 2026)

[docs/e2e-primary-2026-09-15.md](docs/e2e-primary-2026-09-15.md) records a stock FirstMate primary (Claude Code 2.1.269, Opus 5, launched in the clone with `--plugin-dir <core> --setting-sources project,local`) taking one plain-language request on a fresh local-only project and running the dynamic workflow unprompted: one Sonnet xhigh maker, one Codex luna xhigh reviewer who found a real defect, one repair steer with a fresh `done` line, a captain hold for the merge, `fm-merge-local.sh` and teardown, in 16 minutes over 21 watcher wakes. Its briefs follow the wording now in `docs/firstmate.md` almost verbatim. Evidence, including the extracted captain transcript, is in `docs/e2e-primary-2026-09-15/`.

The same increment folded the first trial's lessons into `docs/firstmate.md` (brief wording, repair steers, the no-origin rule for local-only projects, Codex first-run prompts and `blocked:` lines, running owners from the checkout, the backlog note format), added "work alone without delegating" to `orch-work` and `orch-review`, and decided that on `no-mistakes` projects the pipeline is the Review unless the request or a saved workflow names a reviewer. `docs/plan.md` records the decision. Skill bodies stay under 200 words; the 29 tests pass.

## Next

1. Trial a saved workflow run by name through a model-driven primary, and one `direct-PR` or `no-mistakes` project, to cover the placements the two trials left untried.
2. Try a Codex primary once, which would also settle the manual-only skill flag question in `docs/hosts.md`.
3. Record a primary's cost from a `--output-format stream-json` run if cost per request matters.

## Constraints

- No FirstMate changes, no subagents inside workers, no runtime in the package.
- Keep guidance and example libraries identical to upstream unless a trial shows a defect.
- `.sources/` and `.scratch/` are ignored local research copies and stay unchanged.
