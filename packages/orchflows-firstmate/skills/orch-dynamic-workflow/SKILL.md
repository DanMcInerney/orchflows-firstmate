---
name: orch-dynamic-workflow
description: Use when no more specific workflow is named. Coordinate FirstMate agents for the work and one final independent review.
disable-model-invocation: false
---

State the intended result and its checks; when unresolved uncertainty could change what to build, investigate first with a read-only [Work](../orch-work/SKILL.md). Select relevant [guidance](../../docs/architecture.md#guidance-selection) and resolve dependencies once. FirstMate owns [model and effort](../../docs/architecture.md#model-and-effort). FirstMate makes no change itself: the smallest workflow is one Work and one [Review](../orch-review/SKILL.md).

Prefer one maker per landed change. Use several makers only for independent deliverables that land separately, or add a joining Work that integrates their branches. Dispatch makers concurrently once their inputs are ready. Record every task ID and the current phase in the backlog item note and resume from it after any restart.

When the candidate is committed and reviewable, follow the project's [review and delivery checkpoint](../../docs/firstmate.md#delivery-modes). For a separate Review, let the reviewer finish and read its report before one repair pass: return the findings to the maker through FirstMate's steering and recovery procedures, or dispatch fresh Work with the joined result. The pass includes checks and no second review. Let FirstMate deliver; report what was made, checked and remains unresolved.
