---
name: orch-work
description: Request scoped Work through FirstMate using the caller's accepted workflow and assignment controls.
---

**Conditional experimental execution:** follow the [FirstMate client contract](../../docs/firstmate-client.md). Run `python3 -B <snapshot>/scripts/firstmate.py status` in FirstMate's supplied launch environment before dispatch. Confirm the current caller generation, exact retained fork snapshot and admitted Work or dynamic attachment. Native Agent/spawn tools, direct fleet/Herdr commands and normal Orchflows are not fallback executors.

Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Give each maker clear ownership, exact inputs, resolved Make guidance paths and the checks and evidence to return. Submit independent assignments when their inputs are ready. FirstMate owns the selected harness, launch, worktree, inbox, recovery, result retention and cleanup.

A dynamic request requires `request_id`, `assignment`, `primitive: "Work"` and boolean `writable`. A selected composition also specifies the authorized `workflow_call`. With negotiated controls, optional `model`, `effort`, `assignment_name` and `operation_defaults` carry assignment choices through FirstMate. Resolve model and effort independently: current named choice, current operation default, saved named preference, saved operation default, then applicable FirstMate defaults. Explicit unsupported settings are refused. A legacy single Work request remains read-only and contains only request_id and assignment.

Write request files in the caller's recorded tasktmp. Submit with `python3 -B <snapshot>/scripts/firstmate.py submit --request <request-file>`. Each new dynamic request freezes the caller's current clean worktree commit. Commit and check your own changes before dependent work. Set writable true only for assigned project changes.

Inspect with `status --request-id <id>`; read the full retained report and result before `gather --request-id <id>`. Join the entire retained input_commit..output_commit range into your own assigned worktree with ordinary Git cherry-pick, resolve conflicts and check the combined result. Gather acknowledges evidence; it does not join commits. Identical replay preserves the accepted child and profile. An uncertain launch stays pending through FirstMate reconciliation. After relaunch use the new immutable context and preserve accepted results.

Root callers share a maximum of 32 components with their descendants and reserve capacity for every required Review and repair. A writable root Work assignment can itself invoke Work/Review only when its request ID is named as a caller by the immutable selected composition. It may use only its declared call IDs, one level deep; it must gather and finish those calls before returning its own result. Read-only Work and Review cannot delegate. Components return to their actual caller and never perform outer delivery.

Component continuation, deeper delegation, remote homes, promotion, other ship modes and SelfImprove remain unsupported. Read-only is an instruction and result-validation contract, not an operating-system sandbox.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Launch a fresh native child to make the requested result, applying the assignment's [model and effort](../../docs/architecture.md#model-and-effort) through native host controls. Give it the assignment, intended workspace and input state, resolved guidance paths and scoped caller choices; instruct it to read and apply the Make sections. Isolate per [hosts.md](../../docs/hosts.md) when edits could overlap.
