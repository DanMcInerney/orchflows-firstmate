# Candidate approaches for investigation

These are brainstorming inputs, not approved designs. The initial assessment favors B; A can test it cheaply. C and D remain alternatives to evaluate rather than silently dismiss.

| Option | Shape | Potential benefit | Principal uncertainty | First discriminating experiment |
| --- | --- | --- | --- | --- |
| A. Explicit task invocation | Install complete Orchflows packages through a supported host and name a workflow in one FirstMate brief | Minimal upstream change; tests the actual worker boundary | Native tools and package discovery; review authorization; workspace rules | FirstMate launches one isolated worker with a deliberately requested knowledge/review assignment; worker resolves a package, creates a child and reports through normal status |
| B. Optional crewmate compatibility library | An Orchflows library plus FirstMate workflow selection, brief injection and readiness checks | Reusable workflows with ordinary fleet operation; potentially simple install/update UX | Stable attachment point, policy mapping, restart checkpoints and version availability | Repeat A through saved configuration, then steer and relaunch the worker while retaining the selected workflow/version |
| C. Fleet-backed Work/Review adapter | Map every workflow worker/reviewer to an ordinary FirstMate task | Independently visible durable tasks and broader harness routing | Changes Orchflows native-child contract; parent/child mapping, result transfer, cancellation, review policy and cleanup | Two linked maker tasks plus a scoped reviewer with durable joins, restart and exact result provenance |
| D. Guidance-first integration | Supply domain guidance and selected task instructions to FirstMate workers without full Orchflows orchestration | Small integration surface; may capture much of the practical value | Does it satisfy the user's desired workflow capability? Which benefits are lost? | Compare one representative task with baseline FirstMate and guidance-only use; evaluate result quality, operator effort and cost |

**Proposed ownership for B**

FirstMate retains intake, outer dispatch, task workspace, supervision, delivery mode and merge authority. The crewmate owns the selected composition, its children, artifact collection and FirstMate-facing messages. The native host executes the children. Orchflows supplies primitives, reusable compositions and guidance.

This partition is a hypothesis. Test whether enough inner state can be recovered without recreating a second fleet manager inside the worker.

**Review-policy choices to compare**

- Work-only composition handed to no-mistakes; the existing pipeline owns delivery review.
- Explicitly requested independent review as a scoped deliverable using unchanged `orch-review`.
- A documented new FirstMate policy permitting selected Orchflows review workflows.
- Guidance reuse without adding a review stage.

Do not silently remove the final review from `orch-dynamic-workflow`; use a distinct composition if it has a different contract. Do not label routine duplicate review as required merely because two packages are installed.

**Potential installation experience**

A user could install a compatibility package once, enable it for selected task types, continue making normal FirstMate requests, and update it through one documented command. That user experience is proposed: no such command, config field or workflow package currently exists in this repository.

Compare a FirstMate change, user-owned local brief/config material, and a host-native plugin entrypoint. Choose a documented attachment point rather than editing cached skills or repurposing the process-event extension API.

**Evaluation dimensions**

Compare setup steps, ongoing operator decisions, supported worker hosts, compatibility with review/delivery policy, state visibility, interrupted-work recovery, upgrade safety, changes required upstream, maintenance under upstream churn, and whether the resulting system still reflects Orchflows' lightweight architecture. Do not use additional agent count by itself as evidence of improvement.
