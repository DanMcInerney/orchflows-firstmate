# Handoff

## Direction (September 15, 2026)

The user redirected the project. FirstMate launches agents natively as it always has; this library supplies Orchflows' pattern for how that work is done: two terse composable skills, workflows built from workflows, per-agent model and effort, the dynamic workflow as FirstMate's default, and custom workflows that run only when named. Plug-and-play means nothing in FirstMate changes. [docs/plan.md](docs/plan.md) records the decisions and acceptance.

## Increment of September 15, 2026

That increment:

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

## Upstream sync and release preparation (September 16, 2026)

Synced with upstream Orchflows `f34f886e`, thirteen commits past the previous pin. Adopted: the invocation policy (only `orch-dynamic-workflow` is model-invocable; every other skill carries `disable-model-invocation: true` and a Codex `agents/openai.yaml` policy), the dynamic workflow's wait-for-the-reviewer wording, build-workflow's matched-conditions trial rule, and the example libraries copied byte-for-byte (benchmaker, software-factory, export-workflow and self-improve added; Nightbind removed as upstream did). `orch-self-improve` left the core in favor of the upstream `self-improve` example. Upstream's multi-host installers were not ported; `UPSTREAM.md` lists every difference. The package's copied `reports/` were removed, a root `LICENSE` was added, and the package is version `0.3.0`; its 32 tests pass on Windows (Python 3.14) and Ubuntu in WSL (Python 3.12). Docs now describe the policy in `docs/architecture.md#invocation`, `docs/hosts.md#invocation-policy` and the `captain.md` block.

## Trial of the synced library (September 16, 2026)

[docs/e2e-sync-2026-09-16.md](docs/e2e-sync-2026-09-16.md) records three requests to one stock FirstMate primary (Claude Code 2.1.269, Opus 5, Herdr 0.7.4 in Ubuntu under WSL) on the 0.3.0 package: a plain build ran the dynamic workflow through the Skill tool with a Codex review, one repair by steer and a landing in 18 minutes; a request naming `orch-build-workflow` had the primary read the manual-only skill by path, author the `quickfix` library, trial its `fix` workflow on roman as written, return findings to the author, take a clean final Codex review and land the library in 39 minutes; and `quickfix:fix` named by the captain was read from the home library path and landed a third change in 14 minutes. Every spawn carried explicit harness, model and effort; every landing went through a captain hold. The lab was rebuilt under `~/orchflows-e2e` because WSL clears `/tmp` when the VM restarts; `docs/e2e-sync-2026-09-16/driver/` holds the rebuild and pane scripts. `docs/firstmate.md` now says spawn takes the clone path.

## Next

0. Before making the repository public: decide whether to rewrite history to drop the Nightbind evidence blobs (most of the 28 MiB pack), and replace the GitHub description, which still says research and design.
1. Trial one `direct-PR` or `no-mistakes` project, and a saved workflow whose review returns repairs, so the repair-by-steer branch of a saved workflow runs through a model-driven primary.
2. Try a Codex primary once, which would exercise the `agents/openai.yaml` invocation policy through a Codex primary.
3. Record a primary's cost from a `--output-format stream-json` run if cost per request matters.

## Constraints

- No FirstMate changes, no subagents inside workers, no runtime in the package.
- Keep guidance and example libraries identical to upstream unless a trial shows a defect.
- `.sources/` and `.scratch/` are ignored local research copies and stay unchanged.
