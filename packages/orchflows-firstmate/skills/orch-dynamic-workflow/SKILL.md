---
name: orch-dynamic-workflow
description: Use when no more specific workflow is named. Coordinate FirstMate agents for the work and one final independent review.
disable-model-invocation: false
---

State the intended result and its checks; when unresolved uncertainty could change what to build, investigate first with a read-only [Work](../orch-work/SKILL.md). Select relevant [guidance](../../docs/architecture.md#guidance-selection) and resolve dependencies once. Resolve each assignment's [model and effort](../../docs/architecture.md#model-and-effort). FirstMate makes no change itself: the smallest workflow is one Work and one [Review](../orch-review/SKILL.md).

Prefer one maker per landed change. Use several makers only for independent deliverables that land separately, or add a joining Work that integrates their branches. Dispatch makers concurrently once their inputs are ready. Record every task ID and the current phase in the backlog item note and resume from it after any restart.

When the candidate is committed and reviewable, use Review once; let the reviewer finish and read its report before any repair. Make one repair pass: steer the maker with the findings when it can honor the fixer's settings, relaunch it with the fixer's model and effort, or dispatch fresh Work with the joined result. The pass includes checks and no second review. Let the project's delivery mode land the result; report what was made, checked and remains unresolved.
