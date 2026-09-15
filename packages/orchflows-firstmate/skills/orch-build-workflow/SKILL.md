---
name: orch-build-workflow
description: Author, trial and save a reusable workflow or guidance library through authorized FirstMate composition.
---

**Conditional experimental execution:** follow the [client contract](../../docs/firstmate-client.md) and confirm the exact retained dynamic ship/local-only attachment. Build uses the same Work and Review primitives. Composing trials require the selected outer workflow to authorize the trial Work request ID and its dynamic call IDs at intake; instructions alone cannot add runtime scope.

Name the recurring request and useful result. Follow [architecture](../../docs/architecture.md) for placement and dependencies. Use [dynamic](../orch-dynamic-workflow/SKILL.md) with orchflows and writing guidance. Author the complete library inside your assigned worktree, including inputs, output contract, dependencies, guidance, references and assets. Preserve model/effort preferences only when the user asks to save them; the authoring session's model is not a saved preference.

When the workflow composes dynamic calls, declare its bounded authorization in `plugin.json` under `firstmate.workflows.<skill>.composition.calls`: each entry has a unique `id` and `caller` (`root` or the stable request ID of a writable root Work assignment). The caller passes that id as workflow_call. Declare saved preferences in the same skill's `preferences` object and library dependencies in `libraries`. Loading another workflow normally stays in the same context. Only a trial that delegates within Work needs a named descendant caller; only one descendant level is admitted.

Join and check the draft before a fresh Work trials it from the exact clean commit. Supply the ordinary request, candidate library location, retained dependency roots and expected output location. Let the trial read its full skill and determine the work; do not duplicate its instructions in the assignment. A leaf trial works directly. An authorized composing trial uses its own supplied client context and only its declared calls, joins and checks results, performs each independent Review and repair/check pass, then returns its complete result to the authoring caller.

Read and gather the full trial result. Return findings to the authoring work before its final Review and repair or rerun affected behavior as needed. Commit actual output and retained trial evidence outside the library, with candidate identity, input/dependency resolution, checks, preparation, intervention and unexercised behavior. Preserve the [distinct result and report digests](../../docs/firstmate-client.md#trial-digest-meanings). Same-project trial evidence does not establish portability.

Give the authoring call's final reviewer the clean candidate and committed trial evidence, then perform its one repair/check pass. If that pass changes the trialed library, rerun affected behavior under an already authorized trial scope and commit its actual output and retained provenance. Do not repeat a call's Review or silently invent a new trial scope. Preserve original reviewed evidence. On relaunch, reread this skill and retained selected instructions and continue from accepted results.

For a requested save, follow FirstMate's narrow workflow publication operation through ordinary delivery: FirstMate validates and copies the complete committed library into its configured editable workflow home and refreshes its catalog. Worker write permission does not grant arbitrary home writes. New launches resolve a refreshed snapshot; active tasks retain the snapshot with which they started. The workflow identity is `<library>:<skill>`. Publication and later reuse need their own evidence; Git delivery alone does not install a library.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> Name the recurring request and useful result. Follow [architecture](../../docs/architecture.md) for placement and dependencies. Use [orch-dynamic-workflow](../orch-dynamic-workflow/SKILL.md) with `orchflows` and `writing` guidance.
>
> Preserve [model and effort preferences](../../docs/architecture.md#model-and-effort) beside assignments when the user asks the resulting workflow to use them; otherwise leave them unspecified.
>
> Its verification includes a trial before final review. Run a workflow on a bounded request in a disposable workspace; for portable workflows, use an unrelated project, an ordinary brief and declared dependencies. Let the workflow supply the orchestration. For guidance alone, apply it to representative work that exercises the intended preference. Record author preparation, intervention and unexercised behavior as trial limits.
>
> Return trial findings to the maker before final review; simplify or repair and rerun affected behavior as needed. Give the final reviewer the candidate and trial record. Check [host registration](../../docs/hosts.md#register-and-refresh) before claiming a skill is available by name.
