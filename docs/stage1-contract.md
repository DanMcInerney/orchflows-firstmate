# Stage 1: one FirstMate-owned read-only Work component

This increment implements the first path in the fundamental design. It targets a local normal root scout in Herdr and one read-only maker component, using the root's Claude or Codex harness. Independent Review, writers, nesting, promotion, remote homes and full plug-and-play release remain later stages. Unsupported operations must refuse rather than acquire weaker semantics.

## Ownership and implementation layout

- `integrations/firstmate/` carries a reproducible patch and new FirstMate-owned command files against `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`. An isolated candidate is prepared under ignored storage; the pinned research checkout is never modified.
- `packages/orchflows-firstmate/` contains the client and workflow instructions. It calls the supported FirstMate task-group command and never launches a harness or calls Herdr itself.
- FirstMate owns group admission and its launch bridge, atomic child metadata, current-state classification, notification, recovery and cleanup. Existing launch/control/backend owners remain authoritative. There is no new service or scheduler.

Component execution reuses `kind=scout` worktree mechanics with an explicit `task_group_role=component` and `result_disposition=parent`. Its separate instructions and completion path prohibit ordinary scout delivery, scratch edits to the source, promotion and outer `done`. The normal root keeps the existing scout report/delivery contract.

The launch owner also converts declared package/task access into scoped native Claude Read/Edit permissions for the current generation. It preserves the existing mode and settings. This is needed because prose alone cannot authorize retained guidance outside the worker's working directory; grants do not turn the read-only component contract into an operating-system sandbox.

## Fixed initial scope and request contract

The administrator attaches one exact fork package and a clean local Git input commit before launching the root. Stage 1 rejects projects with an origin and dirty input state instead of silently following a moving branch. The complete package snapshot is retained under the root's task data; its content digest and input commit are checked again before actual worker launch.

The request JSON has exactly `request_id` and `assignment`. This endpoint means one read-only Work assignment; unsupported axes are rejected rather than ignored. The caller supplies the current root `spawn_gen` separately. Assignment identity excludes this ephemeral caller generation, allowing a replacement root to gather the original accepted request while rejecting submissions from its predecessor.

One accepted reservation consumes the group's one-component allowance even when its launch is uncertain or its metadata is absent. The child ID derives deterministically from the root and request ID. Reusing the same request ID and body returns the recorded child/result; changing that body refuses. A different request cannot create another component in this initial profile.

## Transactions and failure states

1. Validate parent metadata, attachment, input/package identity and supported scope.
2. Public submission acquires the parent's existing control and metadata locks in the FirstMate bridge and revalidates its generation/profile. The internal controller verifies that lock custody before taking the group lock and atomically reserving the request and launch-attempt record.
3. The nested launch bridge proves inherited lock custody from a live ancestor instead of reacquiring the parent locks. It invokes the ordinary child spawn transaction, whose fresh task-set lock acquisition refuses contention rather than waiting in reversed lock order.
4. Spawn validates the binding before endpoint creation and again after worktree allocation. It includes component fields in its own atomic metadata publication and regenerates the role overlay on launch.
5. A failed, timed-out or interrupted attempt remains uncertain. Missing child metadata cannot authorize another launch, because existing FirstMate rollback may remove metadata while retaining an endpoint. Unknown work remains visible for explicit reconciliation.
6. Component completion validates current child identity and unchanged source, collects a bounded report from the recorded task temporary directory, and publishes a retained report/hash/result before notifying the parent. Root completion is a separate operation.
7. Gathering verifies retained bytes and acknowledges the result. Cleanup is gated by acknowledgement, while ordinary FirstMate endpoint disappearance checks still apply.

The Linux launch observer additionally records and verifies the exact ordinary parent lock claims, owner/controller process identities, ancestry and generation while the accepted request is still launching. This proves an in-progress transaction, not a live child endpoint or retry permission. Unproved and uncertain launches remain attention. Native Windows worker launch and teardown refuse before task mutation until native custody exists; on POSIX, missing process-cleanup evidence preserves the attached task's records and outputs. See the [continuation verification](stage1-continuation-verification.md) for the measured failures and bounded repairs.

Routine no-verb status and turn-end signals may also absorb the authoritative group waiting class. Captain-relevant status, unreadable spans, ready results and unknown activity still surface; this does not broaden the general proof that a root itself is working.

Read-only is an instruction and result-validation contract within FirstMate's existing trusted-account model; it is not an operating-system sandbox. A successful report cannot prove detached commands stopped. The backend's actual liveness and teardown checks remain required.

## Acceptance fixed before completion

| Boundary | Required evidence |
| --- | --- |
| Distribution | Exact patch applies to pinned FirstMate without editing the source clone; fresh prepared candidate has the same overlay and patched bytes |
| Admission | One request/child under repeated and concurrent submission; changed-body, stale-parent, wrong-backend and unsupported-role rejection |
| Uncertain launch | Failure after reservation/publication never automatically creates another child; uncertain state survives command restart |
| Launch | Group fields and role rendered by actual spawn owner; fixed input verified after allocation; ordinary unbound tasks retain prior behavior |
| Result | Exact child incarnation, readonly input, bounded report retention/hash, tamper rejection, restart gathering and explicit acknowledgement |
| Supervision | Parent pending work remains unfinished; unknown/failed children stay actionable; component result does not become outer delivery; promotion and premature cleanup refuse |
| Runtime | Real named Herdr lab through the guarded helper, exact source/client/server/protocol/harness tuple and unchanged default-session tripwire |
| Native work | Same real source-inspection result through Claude and Codex workers, including parent restart and repeated request; missing authentication is an untested case, never a substituted synthetic pass |

Record unit tests, patched-owner fixture tests, Herdr process tests and actual model-worker results separately. Package or mocked transport checks cannot certify the final row. The Stage 0 verification record remains historical and immutable with respect to its recorded candidate identity.
