# Upstream provenance and deliberate differences

This standalone package began as a complete source copy of [DanMcInerney/orchflows](https://github.com/DanMcInerney/orchflows/tree/0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a) at commit `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a`, upstream manifest version `0.7.0`. The initial copy contained all 1,064 tracked files. Its preserved local checkout includes CRLF line endings in some text files whose Git blobs use LF; file retention does not imply byte identity to every raw Git blob. Git metadata is not embedded in this package. The upstream LICENSE and all existing third-party notices are retained.

The fork identifies as `orchflows-firstmate`, development version `0.1.0-dev.9`. It targets FirstMate running in Herdr only, with Claude Code and Codex CLI as worker harnesses. It has no direct native-host execution mode. The examined FirstMate revision is `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`; this is source provenance, not a supported compatibility tuple.

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

Deliberate source refresh (version `0.1.0-dev.3`):

- The current source target is [Orchflows `ca72258493480ddcfe73b3f01d0475ad532e4726`](https://github.com/DanMcInerney/orchflows/tree/ca72258493480ddcfe73b3f01d0475ad532e4726), still upstream version `0.7.0`, observed on September 14, 2026. The original copy identity above remains historical provenance.
- Imported all 17 added `example-workflows/design-loop/` files byte-for-byte from their Git blobs and refreshed the inactive upstream README quotation. This retains all 1,081 upstream paths plus the six fork additions, for 1,087 package files.
- The experimental `design-loop` library remains inactive migration source. It was not invoked, enabled, registered or installed as a library during this refresh. Its upstream trial specifications are not executed checks.
- Fork manifests advance to `0.1.0-dev.3`; the five core skills, runtime scripts, tests and FirstMate integration are unchanged. Package checks and retained-attachment checks do not extend the earlier runtime evidence to this new package identity.

Deliberate Review increment (version 0.1.0-dev.4):

- The client negotiates the selected Work or Review primitive, preserving legacy Work behavior. Review requires an advertised capability and exact explicit-audit attachment before dispatch.
- Review instructions now permit a fresh FirstMate-owned read-only reviewer of the immutable input commit. They prohibit repairs, native children and outer delivery by the component.
- Package readiness reports both implemented scopes while retaining execution_ready=false and package-only readiness. Dynamic composition, writers, Build and SelfImprove remain gated.
- All upstream examples remain unchanged migration source. This increment uses the upstream dynamic workflow as a development process; it does not invoke the fork's gated dynamic workflow or enable design-loop.

Deliberate normal-launch increment (version 0.1.0-dev.5):

- Work/Review use a validated immutable FirstMate launch context by default; explicit client arguments remain available for existing callers.
- Selected custom skills may compose one admitted read-only primitive through retained library roots. Additional components and the other core workflows remain gated.
- Matching FirstMate enablement, catalog rendering and relaunch-context publication live in integrations/firstmate; no package-owned dispatch or recovery mechanism is added.
- The full upstream source and inactive examples are retained. Controller/client fixtures and actual workers are recorded separately.

Deliberate bounded dynamic increment (version 0.1.0-dev.6):

- Capability metadata declares dynamic support without changing launch-context schema 1. Legacy retained context clients and two-field Work/Review requests remain supported.
- A validated dynamic attachment admits explicit Work/Review and writable choices, request-selected status/gather, retained writer commit identities and one fresh Review followed by one repair/check pass.
- Work, Review and dynamic skill guidance now describes that bounded Linux normal-scout profile. Custom skills reuse the same primitives; nesting, ship delivery, Build, SelfImprove and design-loop remain gated.
- Package readiness still reports package-only and execution_ready=false. Client fixtures are separate from owner checks and actual worker evidence; FirstMate alone owns launch, workspace allocation, lifecycle and delivery.
- All 1,081 upstream paths and existing migration inventories remain retained at ca72258493480ddcfe73b3f01d0475ad532e4726. This increment does not refresh upstream sources or modify optional example libraries.

Deliberate local-only root delivery increment (version 0.1.0-dev.7):

- Package/client and FirstMate capabilities explicitly negotiate `ship-local-only`; immutable root delivery includes kind, mode and ordinary `fm/<id>` branch. Legacy contexts and scout attachments retain their contract.
- Dynamic/Work/Review guidance includes explicitly selected Linux ship/local-only roots, with components returning to their parent and only the root following ordinary ready-branch delivery. Direct-PR, no-mistakes, promotion, nesting and self-development remain excluded.
- FirstMate spawn/relaunch, task-group guard and local merge owners validate the selected delivery; this package introduces no writer or delivery service.

Deliberate bounded leaf-authoring increment:

- Adapts orch-build-workflow from the same pinned Orchflows ca72258493480ddcfe73b3f01d0475ad532e4726 source to complete non-delegating leaf/guidance libraries in explicitly selected Linux dynamic ship/local-only roots. It reuses Work, joined commits, one Review and the existing repair/check pass.
- The fresh leaf trial uses its frozen worktree and declared retained dependencies. Actual output and trial findings join the final candidate; recovery reuses accepted requests and rechecks authoring requirements. No runtime protocol or capability is added.
- The matching FirstMate catalog points to this bounded contract. General composing/nested Build, SelfImprove, native registration and implicit user-home installation remain unavailable. Unrelated-project reuse uses existing outer FirstMate enablement/spawn owners and is separate evidence unless performed before final Review.
- Original quoted skills, all upstream paths and optional library bytes remain retained. Source inspection and package/owner checks do not certify actual authoring behavior; exact worker evidence is recorded separately.


Deliberate plug-and-play increment (version 0.1.0-dev.9):

- Adds negotiated assignment model/effort controls, resolved independently through FirstMate and retained with request identity. Legacy requests preserve their previous contract.
- FirstMate owns editable workflow-home setup, complete library publication, identity selection at brief intake, and immutable library bundles for launched tasks.
- Selected composition descriptors authorize bounded dynamic call scopes and descendant assignments. Each dynamic invocation retains one independent Review and one repair/check phase; loading instructions remains in the caller context.
- The existing FirstMate launch, worktree, inbox, lifecycle and local-delivery owners remain authoritative. Native Windows and other delivery modes remain deferred.
- All upstream paths and optional examples remain retained at ca72258493480ddcfe73b3f01d0475ad532e4726. Package checks, owner fixtures and actual worker evidence are recorded separately in the integration verification.
