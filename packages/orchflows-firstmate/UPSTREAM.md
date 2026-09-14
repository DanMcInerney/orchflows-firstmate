# Upstream provenance and deliberate differences

This standalone package began as a complete source copy of [DanMcInerney/orchflows](https://github.com/DanMcInerney/orchflows/tree/0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a) at commit `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a`, upstream manifest version `0.7.0`. The initial copy contained all 1,064 tracked files. Its preserved local checkout includes CRLF line endings in some text files whose Git blobs use LF; file retention does not imply byte identity to every raw Git blob. Git metadata is not embedded in this package. The upstream LICENSE and all existing third-party notices are retained.

The fork identifies as `orchflows-firstmate`, development version `0.1.0-dev.2`. It targets FirstMate running in Herdr only, with Claude Code and Codex CLI as worker harnesses. It has no direct native-host execution mode. The examined FirstMate revision is `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`; this is source provenance, not a supported compatibility tuple.

Deliberate foundation changes (version `0.1.0-dev.1`):

- Independent package, source catalog and home catalog names; independent `ORCHFLOWS_FIRSTMATE_HOME` / `~/.orchflows-firstmate` storage. Normal Orchflows homes, cores and recognized catalogs are protected.
- Setup leaves user host settings untouched unless `--concurrency` is explicitly selected. Existing opt-out, update recovery, library preservation, resolve and native-history mechanics are retained.
- Resolver alias `orchflows` selects only this fork's managed core. Both names are reserved against library collisions; native host skill aliases are not installed.
- Setup and doctor report package-only readiness and explicitly report the absent task-group integration. No fake adapter or successful execution preflight is provided.
- All five core skills are gated. Their intended FirstMate component-task contracts replace native child ownership; FirstMate remains the only Herdr lifecycle and delivery owner.
- Namespace-sensitive tests are adapted and focused isolation/readiness tests are added. Package documentation states the development boundary. Quoted upstream README, host documentation and skill bodies are inactive migration baselines.

All example libraries, their assets, licenses and tests remain upstream migration fixtures. Their native dispatch, package names, user-home writes, dependency loading, loops, artifact delivery and external tools require review and actual FirstMate trials before certification. Source links intentionally remain upstream links. Feature preservation is an implementation objective, not a claim that all workflows run in this release.

Deliberate Stage 1 changes (version `0.1.0-dev.2`):

- `scripts/firstmate.py` calls only FirstMate's experimental task-group controller. It negotiates protocol version 1, validates root/generation and exact retained package attachment, then submits, inspects or gathers one read-only Work result. It returns controller errors and explicitly uncertain transport outcomes without retries or fallback.
- Work admits that conditional experimental scope, with inherited harness/model/effort and retained core Make guidance. Broader Work and all four other core workflows remain gated. The complete example/library bytes and quoted upstream skill bodies are preserved.
- Setup/doctor describe the shipped experimental client while continuing to return package-only readiness and `execution_ready: false`. No host registration, settings change, Herdr calls, authentication probe or new scheduler is added.
- Isolated client protocol tests cover malformed/rejected responses, exact package binding, request validation, timeouts, error propagation and absence of fallback. They do not establish real worker integration.

FirstMate's matching experimental owner changes live outside this package, against the pinned FirstMate source; stock upstream lacks this protocol. Herdr endpoint control remains exclusively FirstMate's. Actual runtime and native worker evidence require separate exact-state records. Task-aware history and broader feature parity are still migration work.
