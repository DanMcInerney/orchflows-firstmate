---
name: orch-review
description: Request a fresh independent read-only audit through an explicitly admitted FirstMate Review or Linux dynamic workflow.
---

**Conditional experimental execution:** follow the [FirstMate client contract](../../docs/firstmate-client.md). Run `python3 -B <snapshot>/scripts/firstmate.py status` in FirstMate's supplied launch environment before dispatch. It must confirm the current root generation, exact retained package and either Review/explicit-audit or dynamic/workflow-review authority. A legacy Work attachment does not authorize Review. Report a missing capability and stop; never use native children, direct fleet/Herdr commands or normal Orchflows as a fallback.

## One fresh independent audit

The reviewer must not have made the candidate. FirstMate launches a fresh read-only component with the root's inherited Claude or Codex harness, model and effort. Reuse supplied guidance or resolve it per the [selection rule](../../docs/architecture.md#guidance-selection). The assignment states the intended result, exact candidate, relevant evidence, retained Review guidance and allowed read-only checks. Instruct the reviewer to return supported findings without making or delegating repairs.

For an admitted dynamic workflow, first read and gather every accepted Work result, join the selected commits in the root worktree, run relevant checks and commit the exact clean candidate. Dynamic permits one Review, selected with a request containing exactly `request_id`, `assignment`, `primitive: "Review"` and `writable: false`. FirstMate freezes the root's current clean commit as this review's input_commit. The attachment's earlier input commit is not the later joined candidate.

For a standalone Review/explicit-audit attachment, the request remains exactly request_id and assignment. Its one component audits the attachment's original immutable clean commit; the ordinary root deliverable is the audit report.

Write the request in the root's assigned temporary directory, outside project and retained package. Submit with `python3 -B <snapshot>/scripts/firstmate.py submit --request <request-file>`. Use the supplied ORCHFLOWS_FIRSTMATE_CONTEXT without overriding authority fields. Keep the returned request and child identity. Read the full retained report and result before `gather --request-id <id>`; standalone Review also accepts gather without an ID.

After dynamic Review is gathered, make one repair/check pass on the joined candidate, directly in the authorized root worktree or through scoped Work requests. Do not request another Review. FirstMate's ordinary root reporting and delivery owners remain authoritative; component completion does not complete the root, and this profile does not authorize ship/no-mistakes review gates.

Identical replays preserve the original child, including after root relaunch with a new immutable context. Uncertain launch, failed reviewer or missing results require FirstMate reconciliation, without a replacement from another tool. Reviewers cannot edit, repair or delegate. Nesting, component continuation, model overrides, remote homes, Build and SelfImprove remain unsupported. Read-only is an instruction and result-validation contract, not an operating-system sandbox.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Launch a fresh native child who did not make the work to review without making or delegating repairs, applying the assignment's [model and effort](../../docs/architecture.md#model-and-effort) through native host controls. Give it the intended outcome, actual candidate state, resolved guidance paths and scoped caller choices; instruct it to read and apply the Review sections. Isolate per [hosts.md](../../docs/hosts.md) when concurrent edits or verification side effects need it.
