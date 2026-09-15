---
name: orch-review
description: Request one independent read-only Review for an authorized dynamic call or explicit audit through FirstMate.
---

**Conditional experimental execution:** follow the [FirstMate client contract](../../docs/firstmate-client.md). Run `python3 -B <snapshot>/scripts/firstmate.py status` with this caller's supplied immutable launch context. Confirm its current generation, retained package and Review/explicit-audit or dynamic/workflow-review authority. A legacy Work attachment does not authorize Review. Never use native children or direct fleet commands as fallback.

The reviewer must not have made the candidate. FirstMate launches a fresh read-only component with the independently resolved requested model and effort. Reviewing in the maker's session cannot satisfy a reviewer profile. Reuse supplied guidance or resolve it per the [selection rule](../../docs/architecture.md#guidance-selection). State the intended result, exact candidate, retained evidence, Review guidance and allowed read-only checks. Require supported findings without making or delegating repairs.

For dynamic, first read and gather the call's Work results, join their complete commit ranges in your own worktree, run checks and commit the exact clean candidate. Request `request_id`, `assignment`, `primitive: "Review"`, `writable: false` and the selected composition's `workflow_call`. Optional negotiated model/effort controls use the same precedence as [Work](../orch-work/SKILL.md). Each dynamic invocation permits exactly one independent Review. Another explicitly declared call has its own Review; it cannot reopen a finished call's review cycle.

A standalone Review/explicit-audit attachment remains one component inspecting its original immutable commit, with a request containing only request_id and assignment. Put request files in recorded tasktmp, then call `python3 -B <snapshot>/scripts/firstmate.py submit --request <request-file>`. Read the complete retained report and result before `gather --request-id <id>`; standalone Review also accepts gather without an ID.

After dynamic Review is gathered, perform one repair/check pass directly or through scoped Work. Do not request a second Review for that call or wait for repeated clean verdicts. Finish and gather the phase before starting the next authorized call. Keep all children within the shared capacity. FirstMate alone controls root delivery; components return to their caller.

Identical replay preserves the reviewer. Uncertain launch or absent results require existing FirstMate reconciliation. Reviewers cannot edit, repair or delegate. Once no-mistakes validation starts it alone owns review, fixes, checks and delivery; this workflow grants no additional dispatch authority. Component continuation, deeper delegation, remote homes, promotion and SelfImprove remain unsupported.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Launch a fresh native child who did not make the work to review without making or delegating repairs, applying the assignment's [model and effort](../../docs/architecture.md#model-and-effort) through native host controls. Give it the intended outcome, actual candidate state, resolved guidance paths and scoped caller choices; instruct it to read and apply the Review sections. Isolate per [hosts.md](../../docs/hosts.md) when concurrent edits or verification side effects need it.
