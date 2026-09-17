# Upstream provenance and deliberate differences

This package began as a complete copy of [DanMcInerney/orchflows](https://github.com/DanMcInerney/orchflows) at `ca72258493480ddcfe73b3f01d0475ad532e4726` and was last synced with upstream at [`f34f886e72e320ce4da5ddb3d3e06237f13b6d8b`](https://github.com/DanMcInerney/orchflows/tree/f34f886e72e320ce4da5ddb3d3e06237f13b6d8b), upstream version `0.7.0`. The upstream LICENSE and third-party notices are retained. FirstMate was studied at `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`; this package changes nothing in FirstMate.

Dispatch ownership was rechecked against FirstMate `3eb5b6334a80e06083e3837f0032a5cec39b8e52` on September 17, 2026. The recorded integration trials predate the routing simplification in 0.5.0.

Deliberate differences (version `0.5.0`):

- The two primitives dispatch fresh FirstMate agents through `fm-brief.sh` and `fm-spawn.sh` instead of native subagents. The coordinator is the FirstMate primary session and never edits a project.
- The dynamic workflow adds FirstMate's constraints: one maker per landed change, no captain-side join, repair by steer or relaunch, Review placed per delivery mode, workflow state in the backlog note.
- FirstMate owns harness, model and effort selection for every assignment, including repairs. Dynamic and saved workflows carry no execution preferences; old saved settings are ignored and removed when a workflow is updated. The library adds no role defaults, model policy or routing dependency. Execution preferences stay in FirstMate's current request or configuration.
- `docs/firstmate.md` replaces the native host controls in `docs/hosts.md`; `docs/history.md` reads FirstMate task records instead of native transcripts. The `history` CLI and host concurrency settings are removed.
- Independent package, catalog and home names: `orchflows-firstmate`, `orchflows-firstmate-home`, `ORCHFLOWS_FIRSTMATE_HOME` and `~/.orchflows-firstmate`. Normal Orchflows homes and catalogs are protected.
- The checkout is the core and the host's plugin system installs it. `scripts/orchflows.py` keeps only `setup` and `doctor` for the home that holds saved libraries: no managed core copy, runtime, resolver, `--example`, host installers, or the Antigravity, Kimi Code, Grok Build and ZCode support. Only the harness running the FirstMate primary loads these skills; `docs/hosts.md` covers Codex and Claude Code with a path fallback for other primaries. The core carries no `.kimi-plugin` manifest or root `marketplace.json`.
- No example libraries ship here. Upstream's examples compose native subagents and were never trialed through FirstMate; a FirstMate captain builds workflows with `orch-build-workflow` instead. Self-improve is not carried either: FirstMate keeps the task records that `docs/history.md` points at, and an improvement pass is an ordinary request.
- Upstream's `benchmarks/` snapshot and its retired `reports/` are not carried.

Kept in step with upstream:

- Invocation policy: only `orch-dynamic-workflow` is model-invocable; Work, Review, build-workflow and every saved workflow are manual-only through `disable-model-invocation` and `agents/openai.yaml`.
- Guidance is byte-identical to upstream.

An earlier development line (`0.1.0-dev.1` through `dev.9`) implemented FirstMate-owned component tasks through patches to FirstMate and a package client. It is retired; its research and evidence are kept outside the published repository.
