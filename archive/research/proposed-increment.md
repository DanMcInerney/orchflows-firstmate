# Proposed first increment

**Superseded proposal:** the latest user request authorizes beginning modifications and specifies a standalone FirstMate/Herdr-only distribution. See [fundamental-design.md](fundamental-design.md) for the current staged implementation and [foundation-verification.md](foundation-verification.md) for completed foundation work. The research-only scope and native-child first-increment proposal below describe the earlier turn.

September 13, 2026. Proposal only. The user has authorized research and copying sources, not implementation. No files described below have been implemented.

## Start with a manual feasibility gate

Run the explicit, knowledge-only independent-review trial P01 in [experiment-plan.md](experiment-plan.md), using one ordinary FirstMate crewmate, one native reviewer and a retained text report. Supply complete core/library roots in the existing `## Firstmate spec`. Keep the original user request in `## Captain's intent` and retain FirstMate's current completion rules.

This trial can examine the key host boundary without first building an installer. The initial candidate is Claude Code under a dedicated local tmux setup; that choice is provisional, and its actual process/configuration must be verified. Windows CLI availability and WSL tmux discovery in this research do not establish that combination.

Stop the design from expanding if the child cannot be created, collected, controlled, or given the correct package inputs. Decide between a narrower guidance-only profile and a coarse fleet composition based on that result. Do not build a workflow registry to hide a failing native-host contract.

## Small implementation candidate, after feasibility

**Outcome:** an opt-in local worker profile selects one compatible Orchflows composition, persists its package identity through a supported relaunch, and reports through FirstMate's existing lifecycle. Start with a read-only review profile; add work-only ship behavior only after the delivery and child-lifetime probes pass.

| Side | Proposed work | Why it belongs there |
| --- | --- | --- |
| External Orchflows library | Narrow review entrypoint and, later, distinct work-only entrypoint; FirstMate guidance for status, steering, joins, workspace and artifact handling | Keeps host-neutral Work/Review and dynamic workflow contracts unchanged |
| FirstMate | Optional profile selection resolved after worker routing; validate task kind/review authorization; save immutable attachment identity with the durable task; render it from the existing brief/launch owner | FirstMate already owns task authority, launch and reconstruction |
| Package preparation | Resolve complete core and chosen library graph, retain identity and roots, verify required resources, expose readable readiness evidence | Setup and package doctor alone cannot certify actual worker capabilities or preserve active task dependencies |
| FirstMate recovery integration | Carry attachment and compact checkpoint into the supported relaunch note; require reconciliation of old child writers before replacement work | A fresh worker inherits files, not the old conversation or proof of native-child shutdown |
| Documentation / checks | One supported configuration tuple, explicit refusal cases, install/disable/update behavior, acceptance records | “Compatible” must refer to observed behavior and bounded scope |

Use one owner for the task attachment; do not scatter Orchflows conditionals across harness launch templates or repurpose process-event bindings. Unknown metadata currently surviving a relaunch is a useful implementation observation, not permission to rely on an undocumented field as the whole public contract. Exact field names, storage paths and installation commands remain design decisions.

## Boundaries

- One local FirstMate home and ordinary project; no supervisor replacement or FirstMate self-development.
- One level of native children, one child at a time initially. Review children read only; at most one active writer once ship behavior is enabled.
- Complete pinned packages; no edits to managed core/caches, implicit user-library writes, or automatic host concurrency changes.
- Explicitly authorized review deliverables. Ship work uses a separate work-only composition; the selected delivery path retains review and merge authority.
- Existing task shape only. Scout-to-ship promotion is unsupported until stage-aware attachment replay is designed and tested; a new authorized ship task can consume the report instead.
- Text reports and ordinary repository files. Multi-file media retention, extra child worktrees, remote secondmates, additional hosts and Codex Desktop backend support remain later scopes.
- Failure is visible. Missing capability, unsupported controls or uncertain surviving children cannot silently become ordinary execution or a successful workflow result.

## Minimal checkpoint proposal

Store the attachment identity, assignment generation, phase, child handles and intended access, known completed result references, candidate identity, pending decisions, and last observed join/shutdown status. Each mutable state entry names the evidence behind it. Keep long transcripts separate.

The checkpoint is a recovery aid, not a new agent registry or scheduler. It cannot assert that a child is dead. If the selected host cannot establish ownership and termination, the implementation must narrow its restart guarantee or block replacement writers. Retain old package sets while tasks reference them; default updates apply only to new tasks.

## Success criteria and next decision

P01–P02 establish actual package/native-child feasibility. The relevant P03–P09 and P12–P13 establish the first profile's authority, state, failure and update behavior. Inspect the final result independently and compare operator burden against guidance-only and baseline FirstMate through P14 before expanding the product.

The next decision is whether those observations justify the bounded profile or instead favor guidance-only / coarse fleet composition. This document does not select an architecture on the user's behalf or authorize coding.
