# Handoff

## Direction (September 17, 2026)

FirstMate owns dispatch and execution, including every agent's harness, model and effort. This library supplies two terse composable skills, workflows built from workflows, layered guidance, the dynamic workflow as FirstMate's default, and custom workflows that run only when named. Workflows save no execution preferences; older saved profile and vendor settings are ignored and removed when a workflow is updated. Plug-and-play means no FirstMate code or dispatch-rule changes. [docs/plan.md](docs/plan.md) records the decisions and acceptance.

## Increment of September 15, 2026

That increment:

- Retired `integrations/firstmate/` (nine FirstMate patches plus the task-group controller, bridge and overlay), `tools/`, the package client `scripts/firstmate.py`, `host_config.py`, `native_logs.py` and their tests. Their research and evidence moved to the local, ignored `archive/research/`.
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

## FirstMate-first cut (September 16, 2026)

The user set the standing principle: build on FirstMate and avoid overlapping its functionality, and ship no example workflows. This cut removed `example-workflows/` (all ten upstream libraries), the managed core copy, the venv runtime, the `resolve` command and the `--source`/`--example` flags. The checkout is now the core that the host's plugin system installs and that `captain.md` names as `<core>`; `scripts/orchflows.py` keeps `setup` and `doctor` for the home, which holds only saved libraries and their catalogs. Package version `0.4.0`; the tests are rewritten around that shape. The September 16 trial ran on the previous install shape (core copied into the home); the skills and the captain.md block are unchanged, so only the `<core>` path differs.

## FirstMate-owned dispatch (September 17, 2026)

The user removed execution preferences from both dynamic and saved workflows. Package version `0.5.0` updates all four skills to use FirstMate's ordinary intake and recovery, removes the library's model policy, effort fallback, role-profile examples and repair-profile logic, and keeps the workflow composition and guidance. The architecture now ignores legacy saved harness/model/effort/vendor settings and authoring removes them when updating a workflow. `docs/firstmate.md` covers replacing the old captain block and reviewing any copied role rules without overwriting personal configuration. All three manifests carry the version bump for cache refresh.

FirstMate's dispatch owners were researched at `3eb5b6334a80e06083e3837f0032a5cec39b8e52`; neither FirstMate nor the ignored research copies were changed. Guidance and earlier trial artifacts are unchanged. The 15 package tests pass on Windows and Ubuntu/WSL, and all four skill bodies are under 200 words. The generic skill-creator validator rejects the pre-existing Claude `disable-model-invocation` frontmatter field; the package's own cross-host invocation tests pass, and that field is retained.

An independent read-only instruction check followed an unnamed dynamic request, the historical quickfix workflow with conflicting saved profiles and a repair, and authoring with run-specific execution settings. It kept routing with FirstMate, ignored legacy profile and cross-vendor constraints, and kept authoring-session settings out of saved workflows. Its two wording findings were fixed: the skills now consult the delivery-mode mapping before dispatching a reviewer, and build-workflow distinguishes slash-command registration from availability by path. This check launched no workers. The September 15–16 trials exercised the previous routing contract.

## Live E2E suite (September 17, 2026)

[tests/e2e/](tests/e2e/README.md) adds an opt-in WSL harness outside the package. Four cases ran through stock FirstMate `3eb5b63` with the 0.5.0 core: unnamed dynamic build, saved-workflow authoring plus trial, reuse in a fresh primary, and a dynamic regression change. All 462 independent artifact assertions and 149 non-resolver workflow assertions passed. Reviews found real defects; FirstMate handled repair steering, guarded local merges and cleanup. The generated library saved no execution settings and stayed unchanged during reuse. No example library or runtime ships in the package.

The strict suite failed 14 resolver assertions: 11 of 12 worker briefs had no native resolver call, plus three case-level failures. Typed routing was off without configuration; all workers actually used Opus 5, with low, medium or high effort. This does not validate cheaper-model routing. FirstMate and the core package stayed unchanged; full private logs and artifacts remain in `/var/tmp/orchflows-e2e-20260917` after guarded lab teardown. [docs/e2e-routing-2026-09-17.md](docs/e2e-routing-2026-09-17.md) records exact commits, findings, test-development interventions and limits. The 16 harness tests and 15 package tests pass on Windows and WSL.

## Next

1. Investigate the native resolver omissions without introducing a library routing owner. Trial existing configured smart routing and a saved workflow with legacy settings; newly authored workflows and fresh-session reuse are now covered live.
2. Flip the repository public. On September 16 the history was rewritten to drop the Nightbind snapshot (pack 28 MiB to 4.4 MiB, every commit's tree unchanged, merged feature branches pruned from the remote) and the GitHub description was replaced; the pre-rewrite history is kept in a local bundle outside the repository. Trial evidence keeps machine-local paths such as `/home/danhm/...`; no secrets are tracked.
3. Trial one `direct-PR` or `no-mistakes` project. The saved-workflow repair-by-steer branch is now covered by the September 17 live suite.
4. Try a Codex primary once, which would exercise the `agents/openai.yaml` invocation policy through a Codex primary.
5. Record a primary's cost from a `--output-format stream-json` run if cost per request matters.

## Constraints

- No FirstMate changes, no subagents inside workers, no runtime in the package.
- Build on FirstMate; never duplicate what it owns. Keep guidance identical to upstream unless a trial shows a defect. No example libraries.
- `.sources/` and `.scratch/` are ignored local research copies and stay unchanged.
