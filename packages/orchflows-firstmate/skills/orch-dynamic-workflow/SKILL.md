---
name: orch-dynamic-workflow
description: Compose scoped Work, join an exact candidate, then request one independent Review and one repair/check pass through FirstMate.
---

**Conditional experimental execution:** run `python3 -B <snapshot>/scripts/firstmate.py status` in FirstMate's supplied launch environment and follow the [client contract](../../docs/firstmate-client.md). Execution requires a normal Linux root scout or explicitly selected ship/local-only root with the exact retained fork and an attachment declaring `workflow: dynamic`, `primitive: Work`, `review_policy: workflow-review`, `readonly: false` and `max_components: 32`. The controller must advertise dynamic, Work, Review and workflow-review. A ship root additionally requires the package and controller to advertise `root_deliveries: ["ship-local-only"]` and retain `root_delivery: {kind: "ship", mode: "local-only", branch: "fm/<id>"}`. Missing delivery identity preserves the scout contract. A single Work or standalone Review attachment cannot run this composition. Report unsupported requirements and stop; never use native Agent/spawn tools, direct fleet/Herdr commands or normal Orchflows as a fallback.

## Bounded Linux dynamic composition

State the intended result and checks, investigate missing information, and resolve the relevant [guidance](../../docs/architecture.md#guidance-selection) and retained dependencies once. Choose the smallest useful composition. The authorized root crewmate can make an already-clear change in its own assigned worktree. Use [orch-work](../orch-work/SKILL.md) for useful independent assignments, with clear ownership, applicable Make guidance and ready inputs. This never permits a FirstMate supervisor to perform project work.

Each new request freezes the root's current clean committed input through FirstMate. Use distinct stable request IDs and explicit Work/Review and writable choices in the request JSON. FirstMate owns component allocation, worktrees, inherited worker settings, inbox notification, recovery and cancellation. Status without an ID lists the retained requests; status/gather with --request-id selects one. A root relaunch keeps accepted work and uses its new immutable launch context. Read each complete report and result before gathering. Do not launch replacements after an uncertain outcome.

Join accepted writer commits in the root worktree with ordinary Git cherry-pick, resolve conflicts, and verify the combined result. Gather every prior component before Review; commit the exact clean candidate. Use [orch-review](../orch-review/SKILL.md) once with the intended outcome, actual candidate and retained Review guidance. The fresh reviewer returns findings without repairs or delegation.

Gather that review, then make one repair pass and its checks, directly where authorized or through scoped new Work components. Do not request a second Review. Keep total components within 32, reserving capacity for the reviewer and needed repair work. Verify the final revision and follow the immutable root delivery contract. A scout delivers its ordinary report. A ship/local-only root commits the complete clean result on `fm/<id>`, records `done: ready in branch fm/<id>` and stops; requested diagnostics belong in recorded tasktmp. Components only return results to their parent. FirstMate retains its ordinary merge authority and guarded local fast-forward owner.

A selected retained custom workflow may compose these same bounded primitives and guidance; it gets no separate adapter or runtime. The current profile does not admit nested components, component continuation, model/effort overrides, remote homes, direct-PR or no-mistakes delivery, promotion, Build, SelfImprove or design-loop. Once no-mistakes validation begins it alone owns review, fixes, checks and delivery; do not dispatch more Work or Review. Unsupported requirements must remain visible instead of being silently omitted.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> State the intended result and its checks; investigate missing information. Select relevant [guidance](../../docs/architecture.md#guidance-selection) and resolve dependencies once. Carry the caller's [model and effort choices](../../docs/architecture.md#model-and-effort) through each assignment. Make an already-clear change directly when those settings permit; use [orch-work](../orch-work/SKILL.md) for investigation, shared prerequisites and independent deliverables, giving each maker clear ownership and running them concurrently once their inputs are ready.
>
> Join and verify the result. Use [orch-review](../orch-review/SKILL.md) once. Make one repair pass, giving each shared fix one owner with the current joined result and needed inputs. Continue makers whose context helps when they can honor the fixer's settings, make clear fixes directly when permitted, or use orch-work. The pass includes repairs and their checks, without another review. Verify the revision and report what was made, checked, and remains unresolved.
