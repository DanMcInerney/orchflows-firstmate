---
name: orch-build-workflow
description: Create and trial reusable FirstMate workflow compositions; execution integration is pending.
---

**Execution blocked:** the experimental [FirstMate task-group contract](../../docs/architecture.md#firstmate-execution-gate) does not support this workflow. Report this missing capability and stop before running this workflow. Do not use native Agent/spawn tools, direct fleet/Herdr commands or normal Orchflows as a fallback. Package setup/doctor success does not satisfy this gate.

## Intended FirstMate contract (not executable)

Once the contract is implemented, name the recurring request and useful result. Use [orch-dynamic-workflow](../orch-dynamic-workflow/SKILL.md) with `orchflows` and `writing` guidance; preserve explicitly requested assignment preferences. Author in the task-assigned source workspace. Trials must run through FirstMate in disposable component workspaces, exercising declared inputs and dependencies before final review. Give trial findings to the maker, repair and rerun affected behavior, then pass the candidate and trial evidence to the independent reviewer. Publishing a library to a user home is a separately authorized delivery operation. Package validation or native-host trials alone cannot certify a FirstMate workflow.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> Name the recurring request and useful result. Follow [architecture](../../docs/architecture.md) for placement and dependencies. Use [orch-dynamic-workflow](../orch-dynamic-workflow/SKILL.md) with `orchflows` and `writing` guidance.
>
> Preserve [model and effort preferences](../../docs/architecture.md#model-and-effort) beside assignments when the user asks the resulting workflow to use them; otherwise leave them unspecified.
>
> Its verification includes a trial before final review. Run a workflow on a bounded request in a disposable workspace; for portable workflows, use an unrelated project, an ordinary brief and declared dependencies. Let the workflow supply the orchestration. For guidance alone, apply it to representative work that exercises the intended preference. Record author preparation, intervention and unexercised behavior as trial limits.
>
> Return trial findings to the maker before final review; simplify or repair and rerun affected behavior as needed. Give the final reviewer the candidate and trial record. Check [host registration](../../docs/hosts.md#register-and-refresh) before claiming a skill is available by name.
