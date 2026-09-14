# FirstMate owner mapping for the plug-and-play upgrade

The dev.6 continuation extends this seam to bounded Linux dynamic composition;
see [dynamic contract](dynamic-composition.md) and [current verification](dynamic-verification.md).
Earlier one-component restrictions below describe the dev.5 baseline.

Source inspection, September 14, 2026. FirstMate is pinned at
[b182d0f908b78d08c7ccb8dce3775bdca8c5d657][fm-pin]; Orchflows behavior is read at
[ca72258493480ddcfe73b3f01d0475ad532e4726][orch-pin].
The adapter baseline is the thirteen deployables inventoried for dev.4 in
[the integration manifest](../integrations/firstmate/manifest.json), before
this continuation's implementation. This document evaluates that baseline;
it does not certify changes made concurrently with the inspection.

**Keep the existing FirstMate execution path and the small amount of workflow
identity it lacks. Change normal availability and the primitive-facing
contract. Do not add a scheduler, recovery daemon, harness launcher or independent
workspace allocator.** The pinned upstream supplies ordinary fleet tasks and
native-tool guards; it does not expose a crewmate-scoped parent/component
request/result API. Merely naming its existing subagent system does not supply
that missing API.

Upstream agent instructions below are analyzed source contracts. They do not
make this development agent a FirstMate supervisor. No active installation or
pinned source was changed for this mapping.

## Existing owners and the actual gaps

| Orchflows operation | Existing FirstMate owner and source behavior | Smallest integration change / boundary |
| --- | --- | --- |
| Enable once; discover skills and libraries | The clone is FirstMate's distribution. Internal skills are loaded from `.agents/skills/`; `.claude/skills` is the compatibility symlink, while public `skills/` is installer-facing. Session bootstrap and the internal skill list live in [README][fm-readme] and [AGENTS][fm-agents]. | Add a discoverable FirstMate-owned enablement/configuration entrypoint and resolve the complete fork plus selected libraries there. No existing upstream Orchflows setup API was found. Do not install ordinary Orchflows or activate design-loop. |
| Make instructions available to ordinary workers and replacements | [fm-brief.sh][fm-brief] owns the durable Captain's intent / Firstmate spec scaffold. [fm-spawn.sh][fm-spawn] regenerates `launch-brief.md` and appends current role/delivery overlays on both fresh launch and relaunch. Project-local skills are discovered from the worker worktree; they do not automatically come from the FirstMate primary's skill directory. | Resolve an enabled workflow profile through this launch owner, pin the selected complete package graph per task, and render a task-local skill index/context. Package/controller paths and current generation can be supplied behind a stable task-local command. Keep the source brief's provenance intact. |
| Work: fresh maker, concrete assignment, Make guidance, requested controls | [AGENTS dispatch][fm-agents] routes fleet work through brief then spawn. [fm-harness.sh][fm-harness] resolves profiles; [fm-spawn.sh][fm-spawn] validates explicit harness/model/effort and allocates task identity, endpoint and workspace. | Keep scoped admission that maps one Work request to a new ordinary FirstMate launch. Pass resolved guidance and input/output scope. The current adapter inherits root controls; it does not yet support independent caller-selected controls, writers or multiple requests. |
| Review: fresh independent reviewer of the accepted candidate, without repairs | The same launch owner can create a fresh worker. [Policy][fm-policy] prohibits routine added independent review outside the selected delivery contract, with explicit audit/knowledge-only exceptions. [fm-dod-lib.sh][fm-dod] owns worker role and delivery prose. | Keep primitive identity, exact candidate identity and return-to-parent disposition. Authorize workflow-selected review at the existing policy owner and render matching worker instructions. Current Review/explicit-audit is a separate bounded knowledge deliverable; it cannot stand in for Work then Review or justify a duplicate no-mistakes review gate. |
| Isolated writes and joining makers | [Spawn][fm-spawn] owns task-set, spawn, metadata and Treehouse project/slot locks, worktree allocation, isolation assertions, rollback and publication. Each normal ship/scout uses its own task worktree. [Policy][fm-agents] allows independently reconcilable parallel work. | Reuse those worktrees for makers. A composing crewmate joins commits/artifacts in its authorized workspace; the supervisor does not integrate project edits. Missing glue is candidate/output disposition and scope, not another allocator or writer lease system. Current no-origin clean-input/read-only gates still apply until changed and checked. |
| Gather, steer and ask for a decision | [fm-send.sh][fm-send] owns text delivery. [fm-task-inbox-lib.sh][fm-inbox] owns numeric records, body deduplication, handled acknowledgment and re-ring/escalation. Existing report/status channels support ordinary scout delivery; marked secondmate requests have a separate [pending-reply owner][fm-pending]. | Keep a durable component result tied to the accepted request, then notify through the existing task inbox. A retained result and its gather acknowledgment are distinct from inbox handling and root done. Future child steering should delegate to fm-send and correlate accepted assignment versions; do not copy its delivery/retry queue. The secondmate correlation owner is not already a crewmate component API. |
| Relaunch, continuation and cancellation | [fm-control.sh][fm-control] owns interrupt, exit and transactional relaunch, using the recorded endpoint and generation. It writes a checkpoint/progress note, exits the old agent, and calls spawn --relaunch. Relaunch starts a fresh conversation. | Keep only workflow selection, accepted request/result and pending join context for replay. Use current metadata and the ordinary controller for worker lifecycle. Root replacement already reuses the same component in the recorded dev.4 trial. Component relaunch is explicitly rejected by the current adapter; enabling it needs reconciled incarnation context, not a new recovery engine. Interrupted outer activity does not prove detached tools stopped. |
| Waiting, failure and wake behavior | [fm-crew-state.sh][fm-crew] owns current classification; [fm-watch.sh][fm-watch], [fm-classify-lib.sh][fm-classify] and [fm-supervise-daemon.sh][fm-supervise] consume current state and durable events. | Keep a shared projection of workflow pending/ready context into those owners. Derive live endpoint and task state from FirstMate. No separate Orchflows poller, wake service or cached liveness state. The existing launch-custody check addresses a measured window before child publication; it is not child health or retry permission. |
| Final delivery and cleanup | [fm-dod-lib.sh][fm-dod] owns ship mode contracts. Scouts retain a report and pass the captain-hold completion gate. [fm-teardown.sh][fm-teardown] owns branch/report checks, process retirement, backlog completion and deletion. | Preserve root-only outer delivery; keep components from ordinary scout done and outer merge/PR paths. Keep gather/uncertainty guards at cleanup. For writable/artifact-producing components extend the result disposition and retention seam rather than treating every component as an independent finished ship/scout. |
| Dynamic, custom and meta-workflows | [Upstream dynamic][orch-dynamic] composes ready Work, joins/checks, performs one independent Review, and makes one repair/check pass without a second Review. Core/library resolution and guidance remain in the complete Orchflows package. | Custom workflows must call the same Work/Review interface, with selected dependency roots carried once. FirstMate has no need for a new executor per workflow. Multiple requests, supported controls, writes, continued work and retained history remain missing portions of that shared interface; discoverability alone does not implement them. |

The [subagent guard][fm-subagent] is specifically a primary/secondmate
PreToolUse fence against work that bypasses fleet records. Linked task worktrees
are excluded, so native children can remain available to ordinary upstream
crewmates. That permission is not a fleet child implementation and is not the
transport for this fork. The guard's named `fm-scout.sh` route is conditional;
that file is absent at this pin, so the inspected fallback is
`fm-brief.sh` followed by `fm-spawn.sh`.

For FirstMate self-development, the last-appended worker role specifically
prohibits delegation. Any supported bounded composition exception belongs in
`fm_brief_worker_role`, preserving contributor guidance and the prohibition on
adopting the supervisor role. A stronger sentence in an earlier skill/spec
cannot resolve that conflict.

## Added records: keep, change, remove

Paths below are relative to the owning FirstMate home. The source owners are
[TaskGroups](../integrations/firstmate/overlay/bin/fm_task_group.py),
[launch callbacks](../integrations/firstmate/overlay/bin/fm_task_group_launch.py),
[store](../integrations/firstmate/overlay/bin/fm_task_group_store.py) and
[state projection](../integrations/firstmate/overlay/bin/fm-task-group-state.sh).

| Existing added record or fields | Disposition | Reason and single owner |
| --- | --- | --- |
| `data/<root>/task-group/attachment.json`: schema, root, epoch, primitive/review policy, readonly, max_components, package path/digest, input commit, project, timestamp; Windows runtime identity when present | **Keep identity; change activation and scope** | FirstMate ordinary metadata does not retain a complete workflow package or exact read-only input. The descriptor is necessary task context. Manual prelaunch attach and immutable one-primitive/one-component bounds are experimental restrictions, not the final operator interface. Resolve defaults once during ordinary admission and preserve task-pinned values on relaunch. |
| `task-group/package/` retained complete source snapshot | **Keep; extend deliberately** | Protects active tasks from mutable installed roots. Current snapshot retains core only; selected library dependency closure requires a task-pinned resolver path. Do not replace it with skill-only copying or package re-resolution on every restart. |
| `task-group/request.json`: request body/hash, root/child edge, epoch, acceptance generation/time, package/input identities, requested primitive and controls | **Keep minimal request identity; change one-request shape when composition is implemented** | Existing fleet metadata does not deduplicate a component request after a lost reply or express the logical parent assignment. Stable request identity prevents duplicate launches. Controls here are accepted assignment evidence; actual launch controls still come from spawn metadata. |
| Request `state=launching/uncertain/launched/complete`, `launch_error`, `launch_custody`, child generation and `launch_meta` | **Keep transaction uncertainty; change duplicated live-state interpretation** | These describe adapter acceptance/publication, not a second task lifecycle. The metadata copy can preserve launch provenance and detect changed identity; do not treat its endpoint/workspace/control fields as current authority. Read current `.meta` and FirstMate state. The current immutable comparison prevents component relaunch, so a later continuation API must reconcile through fm-control rather than accumulate a new task-state machine. |
| Request `gathered`, `gathered_at`, `gathered_parent_gen`, `result_digest` | **Keep** | Distinguishes complete retained evidence from accepted parent consumption and controls premature cleanup. First acknowledgment time remains immutable across retries; replacement generation is recorded separately. Existing inbox handling alone cannot prove result gathering. |
| Request `notification_pending`, `notification_error` | **Keep as notification outcome only; remove any temptation to add another retry queue** | The actual durable queue and re-ring behavior already belong to task-inbox/watch. These fields record enqueue outcome; they do not authorize delivery or result acceptance. |
| `data/<child>/task-group-component.json`: parent/child, epoch, request ID/hash and accepted parent generation | **Keep compact binding** | A parent edge and accepted assignment are absent from ordinary task metadata. This early binding lets spawn validate its scope before launch metadata exists. Redundant identity fields provide consistency checks; they are not a second endpoint record. |
| Added `.meta` keys: `task_group_role`, `task_group_epoch`, component parent/request/hash, optional primitive, `result_disposition=parent` | **Keep as owner-published references** | Published under spawn's existing metadata lock. They make role, request and delivery routing visible to existing owners. Detailed mutable workflow state remains outside the ordinary metadata schema; no external postlaunch metadata writer is needed. |
| `task-group/results/<child>/report.md` and `result.json`: immutable report digest/size, request/package/input identity, component/root-at-completion metadata snapshots, timestamp, unverified native-session marker | **Keep result and provenance; avoid live-state duplication** | Ordinary scout report semantics do not mean return-to-parent. Metadata snapshots are historical evidence; null native session and its limitation must remain honest. Broader artifact manifests/history are later extensions when an actual workflow requires them. |
| `data/<child>/brief.md` and generated launch overlays | **Keep normal brief ownership; change repeated manual commands** | Reuse FirstMate's source/generated brief distinction. Embed assignment and component disposition, expose a stable task-local primitive command, and keep current generation lookup behind it. Do not duplicate mutable workflow instructions in independently edited source and launch files. |
| `task-group/.lock`, atomic `.publish-*` temporaries and shell custody evidence | **Keep scoped persistence/transaction protection** | Group locking serializes request/result JSON while existing FirstMate control/meta/task-set locks protect lifecycle publication. These locks have different protected data. Preserve tested lock order; they do not allocate work or schedule recovery. |

There is no source-backed reason to delete a durable dev.4 record wholesale
before its replacement is exercised. The justified removals are duplicate
authority and manual caller plumbing: raw controller paths/generations in the
workflow interface, independent interpretations of current endpoint state, and
any proposed scheduler/recovery/writer machinery already owned by FirstMate.
Historical evidence snapshots should not be removed merely because the same
field also exists in current metadata.

## Every dev.4 deployable

This inventory covers all eleven added helpers and both patch deployables.
Keep/change directions apply to responsibilities, not an instruction to rewrite
tested code without a demonstrated integration need.

| Deployable | Assessment |
| --- | --- |
| [fm-task-group.py](../integrations/firstmate/overlay/bin/fm-task-group.py) | **Keep owner CLI; change public ergonomics.** Protocol negotiation, generation checks and calls under parent lock custody belong here. Add a stable task-context interface instead of making each workflow construct home/root/controller/generation arguments. No direct Herdr calls. |
| [fm_task_group.py](../integrations/firstmate/overlay/bin/fm_task_group.py) | **Keep bounded admission, dedup, result retention and gather.** Reuse spawn/inbox as it already does. Change one-slot/one-primitive logic only alongside actual composition checks. Keep launching/uncertain as transaction outcomes; no new child scheduler or automatic retry. |
| [fm_task_group_launch.py](../integrations/firstmate/overlay/bin/fm_task_group_launch.py) | **Keep callbacks inside spawn.** This is the right owner seam for availability and replay. Change manual attach-only discovery and command prose; preserve role, input, guidance, result disposition and generation validation. |
| [fm_task_group_primitives.py](../integrations/firstmate/overlay/bin/fm_task_group_primitives.py) | **Keep shared primitive identity validation.** Change admission only when the selected workflow's review is reconciled with FirstMate policy. Review independence and no-repair semantics must not be hidden as free-form prompt options. |
| [fm_task_group_policy.py](../integrations/firstmate/overlay/bin/fm_task_group_policy.py) | **Keep FirstMate-owned launch permission translation.** This supplies declared extra file reads/writes to Claude through existing spawn settings; it is not the fleet review-policy owner and not a new harness integration. Extend only for measured new retained paths. |
| [fm_task_group_store.py](../integrations/firstmate/overlay/bin/fm_task_group_store.py) | **Keep bounded JSON, hashes, snapshot publication and group locking.** Clean no-origin/no-symlink/no-submodule input rules are current admission restrictions; change them only for a verified new input/candidate contract. Do not generalize this helper into a workspace service. |
| [fm_task_group_runtime.py](../integrations/firstmate/overlay/bin/fm_task_group_runtime.py) | **Keep Linux subprocess/path bridge and retained Windows refusal groundwork.** Windows conversion/process-parent code is deferred compatibility work. It must not become another launcher or cause Windows acceptance to become this milestone. |
| [fm-task-group-runtime.sh](../integrations/firstmate/overlay/bin/fm-task-group-runtime.sh) | **Keep lightweight presence/entrypoint and native-Windows refusal guards.** Ordinary tasks stay on the upstream path; visibly corrupt/missing bindings do not become ordinary tasks. |
| [fm-task-group-spawn.sh](../integrations/firstmate/overlay/bin/fm-task-group-spawn.sh) | **Keep narrow locked delegation to fm-spawn.** It reuses existing parent control/meta locks, backlog applicability, task admission and exact parent Herdr session. Change the hardcoded scout/read-only profile when the accepted component disposition expands; never allocate an endpoint/worktree here. |
| [fm-task-group-custody.sh](../integrations/firstmate/overlay/bin/fm-task-group-custody.sh) | **Keep measured launch-window proof.** Reuses fm_pid_identity/alive and existing lock claims. It does not prove harness/tool custody; avoid extending it into a parallel process-control system. |
| [fm-task-group-state.sh](../integrations/firstmate/overlay/bin/fm-task-group-state.sh) | **Keep shared projection, completion/cleanup guards and inbox notification adapter.** Existing crew-state/backend validation supply activity evidence and task-inbox owns dedup/re-ringing. The adapter's pending/ready context is missing upstream; copy no general classifier or event queue into it. |
| [0001-readonly-task-groups.patch](../integrations/firstmate/patches/0001-readonly-task-groups.patch) | **Keep owner hooks in spawn, crew-state, classify, watch, supervise, promote and teardown.** They route component outcomes and prevent premature root cleanup. Consolidate only demonstrated duplicated interpretations into the shared projection; do not replace the existing watch/control owners. |
| [0002-linux-foreground-claude.patch](../integrations/firstmate/patches/0002-linux-foreground-claude.patch) | **Keep bounded measured profile at spawn.** Disables native background tasks and supplies the recorded foreground timeout for bound Linux Claude workers. This is a tested workaround, not background-tool retirement support or a reason to build a broader harness matrix now. |

## Concrete next glue and verification boundary

The narrow implementation path is: enable an explicit FirstMate workflow
profile once; resolve its retained package/library roots through ordinary
launch; expose Work/Review through a stable task-context client; and keep the
existing spawn, inbox, control, state and delivery owners behind it. New tasks
can adopt a changed default while relaunched tasks retain their accepted
selection. Configuration inheritance must use [the existing declared
allowlist][fm-inherit]; local absolute package paths must not be mistaken for
remote provisioning.

A representative dynamic workflow additionally needs multiple logical
requests, an exact joined candidate for its reviewer, supported Work outputs,
and a policy contract for its one workflow-selected Review. A custom workflow
then reuses those same primitives. The current one-component client cannot
demonstrate those outcomes simply by exposing more skill files.

Verification should check the changed interface and owner boundary: ordinary
launch without manual attachment; worker-visible guidance/dependencies and
permissions; useful Work plus exact-candidate independent Review and gathering;
normal root delivery; and ordinary relaunch retaining the accepted request and
selection. Existing dev.4 real Claude Work/Review and root-replacement evidence
is recorded in [Review verification](review-verification.md). It does not
establish these new entrypoints, dynamic/custom runtime, component relaunch,
Codex Review, writers or a complete supervisor wake/drain/rearm cycle.

This mapping used Linux source reads and confirmed the FirstMate source HEAD.
It made no live worker calls and ran no product tests. Parent implementation
and joined verification must report their executed outcomes separately in the
evidence and feature inventory.

[fm-pin]: https://github.com/kunchenguid/firstmate/tree/b182d0f908b78d08c7ccb8dce3775bdca8c5d657
[orch-pin]: https://github.com/DanMcInerney/orchflows/tree/ca72258493480ddcfe73b3f01d0475ad532e4726
[fm-readme]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/README.md#L200-L210
[fm-agents]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/AGENTS.md
[fm-brief]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-brief.sh#L348-L355
[fm-spawn]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-spawn.sh
[fm-harness]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-harness.sh
[fm-policy]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/AGENTS.md#L337-L342
[fm-dod]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-dod-lib.sh
[fm-send]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-send.sh
[fm-inbox]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-task-inbox-lib.sh#L164-L237
[fm-pending]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-pending-reply-lib.sh
[fm-control]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-control.sh#L499-L508
[fm-crew]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-crew-state.sh
[fm-watch]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-watch.sh
[fm-classify]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-classify-lib.sh
[fm-supervise]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-supervise-daemon.sh
[fm-teardown]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-teardown.sh
[fm-subagent]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-subagent-pretool-check.sh#L160-L198
[fm-inherit]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-config-inherit-lib.sh#L29-L69
[orch-dynamic]: https://github.com/DanMcInerney/orchflows/blob/ca72258493480ddcfe73b3f01d0475ad532e4726/skills/orch-dynamic-workflow/SKILL.md

## Selected dev.5 implementation

The continuation implemented the normal-launch change from this mapping:
fm_orchflows.py owns project defaults, immutable package/library preparation and
launch context; patch 0003 calls it from the existing fm-spawn transaction.
The existing request, result, inbox, watcher and recovery owners remain in use.
The hidden data/.orchflows store avoids the ordinary task-ID namespace.

The client reads a launch-bound context instead of assembling controller and
generation arguments. Capability metadata keeps retained dev.4 clients on their
original explicit invocation contract. See [normal launch](normal-launch.md)
and [verification](normal-launch-verification.md). This is single-primitive
custom-workflow integration; the broader composition/policy changes above remain
unfinished.
