# Upstream provenance and deliberate differences

This package began as a complete copy of [DanMcInerney/orchflows](https://github.com/DanMcInerney/orchflows/tree/ca72258493480ddcfe73b3f01d0475ad532e4726) at `ca72258493480ddcfe73b3f01d0475ad532e4726`, upstream version `0.7.0`. The upstream LICENSE and third-party notices are retained. FirstMate was studied at `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`; this package changes nothing in FirstMate.

Deliberate differences (version `0.2.0`):

- The two primitives dispatch fresh FirstMate agents through `fm-brief.sh` and `fm-spawn.sh` instead of native subagents. The coordinator is the FirstMate primary session and never edits a project.
- The dynamic workflow adds FirstMate's constraints: one maker per landed change, no captain-side join, repair by steer or relaunch, Review placed per delivery mode, workflow state in the backlog note.
- Model and effort resolve through FirstMate's dispatch rules and effort fallback after request and saved-workflow settings. Any verified harness may serve any agent.
- `docs/firstmate.md` replaces the native host controls in `docs/hosts.md`; `docs/history.md` reads FirstMate task records instead of native transcripts. The `history` CLI and host concurrency settings are removed.
- Independent package, catalog and home names: `orchflows-firstmate`, `orchflows-firstmate-home`, `ORCHFLOWS_FIRSTMATE_HOME` and `~/.orchflows-firstmate`. The resolver alias `orchflows` selects only this package's core. Normal Orchflows homes and catalogs are protected.
- Custom workflows are manual-only; built-ins stay model-invocable.

Guidance is byte-identical to upstream. Example libraries are retained byte-for-byte; they compose the same two primitives and should run through FirstMate unchanged, but none has been trialed there yet, so treat each as an example until a trial says otherwise.

An earlier development line (`0.1.0-dev.1` through `dev.9`) implemented FirstMate-owned component tasks through patches to FirstMate and a package client. It is retired; its research and evidence are archived under the repository's `archive/research/` directory.
