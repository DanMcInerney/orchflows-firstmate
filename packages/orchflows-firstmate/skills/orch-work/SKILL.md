---
name: orch-work
description: Request a scoped Work result through FirstMate, including writers in an admitted Linux dynamic workflow.
---

**Conditional experimental execution:** follow the [FirstMate client contract](../../docs/firstmate-client.md). Run `python3 -B <snapshot>/scripts/firstmate.py status` in FirstMate's supplied launch environment before dispatch. It must confirm the current root generation, exact retained fork snapshot and an admitted Work or dynamic attachment. If a check fails, report the gap and stop. Package readiness and host plugin discovery do not satisfy this gate. Never use native Agent/spawn tools, direct fleet/Herdr commands or normal Orchflows as a fallback.

## Scoped Work

Only a normal Linux root scout may compose dynamic Work. Each component inherits the root's Claude or Codex harness, model and effort. FirstMate allocates its worktree and owns launch, waiting, recovery, result retention and cleanup. Components do not delegate or perform root delivery. A legacy single Work attachment still permits exactly one read-only component; a Review attachment cannot accept Work.

Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection), using the retained complete package and selected library roots. Give each maker clear file/result ownership, exact inputs, resolved Make guidance paths and the checks and evidence to return. For independent assignments, submit when their inputs are ready.

Write the request in the root's assigned temporary directory, outside the input and retained package. A dynamic request contains exactly `request_id`, `assignment`, `primitive: "Work"` and boolean `writable`. Set writable true only for an authorized project change; read-only investigation uses false. A legacy single Work request retains only request_id and assignment. Submit with `python3 -B <snapshot>/scripts/firstmate.py submit --request <request-file>`. FirstMate freezes the current clean root worktree commit for each new dynamic request. Commit and check root changes before requesting a dependent maker.

Keep each returned request and child identity. Inspect with `status --request-id <id>`; read the complete retained report and result before `gather --request-id <id>`. Dynamic results retain the exact input_commit and output_commit. Join useful writer commits into the root's own worktree with ordinary Git cherry-pick, resolve any conflicts there, and check the joined candidate. Do not treat a component's report or clean commit alone as a verified root result. The legacy single attachment also accepts status/gather without an ID.

An identical request replay retains its child; changing an accepted body is an error. On an uncertain launch, failed child or missing result, use FirstMate's existing reconciliation owner without creating a replacement through another tool. A relaunched root uses its new immutable context to recover the same requests. Keep the supplied context unchanged; an old launch must not substitute a newer generation.

Dynamic admits at most 32 total components, including its one Review and any repair Work. Nesting, component continuation, model/effort overrides, remote homes, ship delivery, Build and SelfImprove remain unsupported. Read-only is an instruction and result-validation contract, not an operating-system sandbox.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Launch a fresh native child to make the requested result, applying the assignment's [model and effort](../../docs/architecture.md#model-and-effort) through native host controls. Give it the assignment, intended workspace and input state, resolved guidance paths and scoped caller choices; instruct it to read and apply the Make sections. Isolate per [hosts.md](../../docs/hosts.md) when edits could overlap.
