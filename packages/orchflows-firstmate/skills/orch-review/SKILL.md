---
name: orch-review
description: Dispatch a fresh FirstMate scout who did not make the work to review it, without repairs.
disable-model-invocation: true
---

Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Place Review per the [delivery-mode mapping](../../docs/firstmate.md#delivery-modes). If the pipeline supplies it, let FirstMate run the pipeline. Otherwise dispatch one fresh scout who did not make the candidate through FirstMate's ordinary intake, brief and spawn owners. FirstMate owns [model and effort](../../docs/architecture.md#model-and-effort). Name the exact candidate: the branch, PR or commit and the intended outcome. Give it the resolved guidance paths and scoped caller choices; instruct it to check the candidate out detached in its own worktree, read and apply the Review sections, and return findings with evidence in its report, working alone, without making or delegating repairs.

Read the report when FirstMate signals the scout done. Findings are evidence for the caller's one repair pass, never authorization.
