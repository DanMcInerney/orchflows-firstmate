---
name: orch-review
description: Request independent review by a fresh FirstMate component task; execution integration is pending.
---

**Execution blocked:** the experimental [FirstMate task-group contract](../../docs/architecture.md#firstmate-execution-gate) does not support this workflow. Report this missing capability and stop before running this workflow. Do not use native Agent/spawn tools, direct fleet/Herdr commands or normal Orchflows as a fallback. Package setup/doctor success does not satisfy this gate.

## Intended FirstMate contract (not executable)

Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Once the contract is implemented and the review deliverable is authorized, request a fresh FirstMate reviewer who did not make the candidate. Supply the intended outcome, exact candidate state, evidence, pinned guidance roots, allowed verification scope and [model/effort choices](../../docs/architecture.md#model-and-effort). The worker applies Review guidance and returns findings without making or delegating repairs. FirstMate owns isolation and lifecycle; component completion does not deliver the root task.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Launch a fresh native child who did not make the work to review without making or delegating repairs, applying the assignment's [model and effort](../../docs/architecture.md#model-and-effort) through native host controls. Give it the intended outcome, actual candidate state, resolved guidance paths and scoped caller choices; instruct it to read and apply the Review sections. Isolate per [hosts.md](../../docs/hosts.md) when concurrent edits or verification side effects need it.
