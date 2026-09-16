---
name: orch-build-workflow
description: Create or improve workflows, domain guidance and specializations; try them through FirstMate and refine from observed use.
disable-model-invocation: true
---

Name the recurring request and useful result. Follow [architecture](../../docs/architecture.md) for placement and dependencies. Use [orch-dynamic-workflow](../orch-dynamic-workflow/SKILL.md) with `orchflows` and `writing` guidance; the author is a Work agent shipping into the [home library](../../docs/home.md#authoring), never FirstMate itself.

A workflow lists its Work and Review assignments in dispatch order, each with its assignment, guidance domains, inputs and checks, and states what runs concurrently. Preserve [model and effort preferences](../../docs/architecture.md#model-and-effort) beside assignments when the user asks the workflow to use them; otherwise leave them unspecified. Give every skill, including helpers, the [manual-only invocation settings](../../docs/hosts.md#invocation-policy) and verify the primary's host honors them before delivery.

Trial the behavior being built or changed before final review: run the workflow through FirstMate on a bounded request in a disposable project, letting the workflow supply the composition. Support a behavioral improvement claim with old and new versions on the same task under matched conditions. For guidance alone, apply it to representative work that exercises the intended preference. Record author preparation, intervention and unexercised behavior as trial limits. Return trial findings to the maker before final review; give the final reviewer the candidate and trial record. [Register the library](../../docs/hosts.md#register-and-refresh) before claiming a workflow is available by name.
