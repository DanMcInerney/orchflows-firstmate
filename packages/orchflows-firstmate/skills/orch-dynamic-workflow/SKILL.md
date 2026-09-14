---
name: orch-dynamic-workflow
description: Compose work and one final independent review inside a FirstMate task group; execution integration is pending.
---

**Execution blocked:** the experimental [FirstMate task-group contract](../../docs/architecture.md#firstmate-execution-gate) does not support this workflow. Report this missing capability and stop before running this workflow. Do not use native Agent/spawn tools, direct fleet/Herdr commands or normal Orchflows as a fallback. Package setup/doctor success does not satisfy this gate.

## Intended FirstMate contract (not executable)

Once the contract is implemented, establish the intended result and checks, resolve [guidance](../../docs/architecture.md#guidance-selection), dependencies and assignment choices, and compose the smallest useful workflow. The root crewmate may make an already-clear change when its scope/settings permit; independent assignments use [orch-work](../orch-work/SKILL.md) component tasks through FirstMate. Join and verify the candidate, then use [orch-review](../orch-review/SKILL.md) once, followed by one repair pass and its checks without another review. Preserve that review contract: FirstMate must explicitly authorize it for the current delivery stage. If the selected delivery policy disallows it, report the incompatibility rather than omit review. FirstMate retains final delivery and merge authority.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> State the intended result and its checks; investigate missing information. Select relevant [guidance](../../docs/architecture.md#guidance-selection) and resolve dependencies once. Carry the caller's [model and effort choices](../../docs/architecture.md#model-and-effort) through each assignment. Make an already-clear change directly when those settings permit; use [orch-work](../orch-work/SKILL.md) for investigation, shared prerequisites and independent deliverables, giving each maker clear ownership and running them concurrently once their inputs are ready.
>
> Join and verify the result. Use [orch-review](../orch-review/SKILL.md) once. Make one repair pass, giving each shared fix one owner with the current joined result and needed inputs. Continue makers whose context helps when they can honor the fixer's settings, make clear fixes directly when permitted, or use orch-work. The pass includes repairs and their checks, without another review. Verify the revision and report what was made, checked, and remains unresolved.
