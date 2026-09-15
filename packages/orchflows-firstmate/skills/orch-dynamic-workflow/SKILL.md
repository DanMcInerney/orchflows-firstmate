---
name: orch-dynamic-workflow
description: Compose Work, join/check, one independent Review and one repair/check pass in the current caller context.
---

**Conditional experimental execution:** run `python3 -B <snapshot>/scripts/firstmate.py status` with FirstMate's supplied launch context and follow the [client contract](../../docs/firstmate-client.md). Require the retained dynamic Work/workflow-review attachment and controller capabilities. An ordinary root scout or explicitly selected ship/local-only root may call this workflow. A writable root Work may call it only under its immutable selected composition's named caller scope. Loading this SKILL.md continues in that caller's context; only Work or Review creates another agent. Native children and direct fleet commands are not fallback executors.

State the intended result and checks; investigate missing information. Select relevant [guidance](../../docs/architecture.md#guidance-selection) and resolve retained dependencies once. Carry the caller's model and effort choices through each assignment, using negotiated controls and saved preferences independently per axis. Make an already-clear change directly when authorized; use [Work](../orch-work/SKILL.md) for investigation, shared prerequisites and independent deliverables, with clear ownership and ready inputs.

Each request uses a stable request_id and its authorized workflow_call. A legacy dynamic attachment without a composition has one implicit call named `dynamic`. A selected larger workflow may declare several call IDs in its library metadata; each call belongs to the root or a named writable root Work request. Calls by the same caller run in declared order. Workers cannot add calls, elevate scope or acquire supervisor authority. The entire group has at most 32 accepted requests, including descendants, reviews and repairs.

Join and verify the result in your own FirstMate worktree. Read and gather the call's retained Work reports and results, cherry-pick complete writer commit ranges, resolve conflicts and check the exact clean candidate. Use [Review](../orch-review/SKILL.md) once for this invocation. Gather that Review and perform one repair pass and its checks, directly where authorized or through scoped Work. Do not repeat this call's Review. A later authorized call starts a separate dynamic invocation after this phase is complete.

On relaunch, reread the selected retained workflow and recover accepted requests using the new immutable context. Preserve accepted results and joined work; an uncertain launch does not authorize a replacement. FirstMate owns every agent, workspace, notification, recovery, cancellation and delivery action. Components return to their caller only after all their authorized descendant calls are finished and gathered.

Verify the final result against the selected workflow before ordinary root completion. Scouts deliver their report; ship/local-only roots keep the complete clean committed output on `fm/<id>`, record `done: ready in branch fm/<id>` and stop for FirstMate's ordinary merge owner. [Build](../orch-build-workflow/SKILL.md) can author and trial composed workflows within the same scopes. No-mistakes retains sole validation custody once selected; this profile does not dispatch into or replace it. Component continuation, deeper delegation, remote homes, promotion, other delivery modes and SelfImprove remain gated.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> State the intended result and its checks; investigate missing information. Select relevant [guidance](../../docs/architecture.md#guidance-selection) and resolve dependencies once. Carry the caller's [model and effort choices](../../docs/architecture.md#model-and-effort) through each assignment. Make an already-clear change directly when those settings permit; use [orch-work](../orch-work/SKILL.md) for investigation, shared prerequisites and independent deliverables, giving each maker clear ownership and running them concurrently once their inputs are ready.
>
> Join and verify the result. Use [orch-review](../orch-review/SKILL.md) once. Make one repair pass, giving each shared fix one owner with the current joined result and needed inputs. Continue makers whose context helps when they can honor the fixer's settings, make clear fixes directly when permitted, or use orch-work. The pass includes repairs and their checks, without another review. Verify the revision and report what was made, checked, and remains unresolved.
