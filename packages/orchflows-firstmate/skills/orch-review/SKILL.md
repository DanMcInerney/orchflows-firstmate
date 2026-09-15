---
name: orch-review
description: Dispatch a fresh FirstMate scout who did not make the work to review it, without repairs.
---

Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Dispatch one fresh scout who did not make the candidate, applying the assignment's [model and effort](../../docs/architecture.md#model-and-effort) as explicit spawn flags. Name the exact candidate: the branch, PR or commit and the intended outcome. Give it the resolved guidance paths and scoped caller choices; instruct it to check the candidate out detached in its own worktree, read and apply the Review sections, and return findings with evidence in its report, working alone, without making or delegating repairs.

Read the report when FirstMate signals the scout done. Findings are evidence for the caller's one repair pass, never authorization. Place the review at the checkpoint its [delivery mode](../../docs/firstmate.md#delivery-modes) defines.
