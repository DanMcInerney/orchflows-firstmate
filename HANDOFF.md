# Handoff: make Orchflows a plug-and-play FirstMate upgrade

## Latest user clarification takes precedence

The user wants FirstMate to use Orchflows' two primitive skills, dynamic workflow,
and custom workflows in the same way Claude or Codex uses original Orchflows.
The upgrade should use FirstMate's existing subagent, communication, worktree,
supervision, recovery, cancellation and delivery systems throughout.

Orchflows supplies the skills, guidance and workflow composition. FirstMate
supplies execution and lifecycle behavior on Herdr, including Claude/Codex
harness integration. The intended experience is install/enable once, then invoke
workflows naturally through FirstMate. Manual per-task attachment, controller
paths and generation flags are intermediate machinery, not the intended user
interface.

This clarifies the architecture and changes the next-work priority. The previous
assistant put too much emphasis on new recovery/writer mechanisms and exhaustive
Claude/Codex acceptance. Do not continue that roadmap automatically. Even code
placed under integrations/firstmate must reuse existing owners wherever possible;
putting a duplicate system there does not satisfy the user's request.

Implementation is already authorized. This turn only wrote the handoff; no
product code changed after the dev.4 verification. Continue implementation when
the next conversation asks to proceed, without reopening the settled scope.

## Desired mapping

| Orchflows capability | FirstMate integration |
| --- | --- |
| orch-work | Request a fresh maker through FirstMate's existing agent/task system, preserving assignment, guidance, controls and result semantics |
| orch-review | Request a fresh independent reviewer through the same system; the reviewer did not make the candidate and does not make or delegate repairs |
| orch-dynamic-workflow | Preserve the upstream composition: ready work, supported parallelism, join, one independent Review, then one repair/check pass without a second Review |
| Custom workflows and meta-workflows | Keep composing the same primitives and resolving guidance/libraries; avoid separate integration code for every workflow |
| Restart, steering, cancellation and completion | Carry the necessary workflow context through FirstMate's existing records and lifecycle owners |

Retain upstream behavior wherever it does not depend on native agent transport.
Keep model/effort and tool capability handling with FirstMate. Small end-to-end
checks must verify that instructions, permissions, results and resumed context
actually reach workers, but this is not a new Claude/Codex integration project.
If a required FirstMate operation is unavailable to the relevant agent role,
show the source-backed gap and make the smallest necessary change at its owner.
Do not invent an API or assume a supervisor may perform project work.

## What to do next

1. **Inspect the actual FirstMate integration points and current adapter.**
   Trace normal skill/instruction loading, delegation, result collection,
   relaunch and delivery. Make a concise mapping from each Orchflows operation
   to the existing FirstMate owner. For each added task-group record/helper,
   distinguish necessary workflow context from duplicated FirstMate task state
   or control logic. Preserve useful working code; simplify or replace redundant
   pieces only with evidence and relevant regression checks.

2. **Implement normal skill/workflow availability and the primitive adapter.**
   Select the existing FirstMate setup/brief/launch extension points, then wire
   the fork's package and selected custom libraries into ordinary workers and
   relaunches. Work and Review should use FirstMate operations behind a stable
   workflow-facing interface. The operator should not manually attach each
   task or construct controller commands. Preserve FirstMate's role and delivery
   contracts; reconcile workflow-selected independent review at the existing
   policy owner rather than silently dropping it or adding duplicate reviews.

3. **Demonstrate a normal workflow through that integration.**
   In a disposable Linux FirstMate installation, enable the upgrade once and
   invoke a small dynamic workflow plus a representative custom workflow.
   Exercise useful Work, exact-candidate independent Review, result collection
   and normal delivery through FirstMate. Use its existing workspace allocation
   for writing when needed. Relaunch through the ordinary FirstMate recovery
   owner and verify that the workflow resumes with the same accepted work.
   Fix only the adapter or measured missing behavior at the appropriate owner.

4. **Review the joined implementation once and repair once.**
   Use upstream Orchflows dynamic workflow for this development, as previously
   requested: scoped makers when useful, joined checks, one fresh independent
   reviewer, and one repair/check pass. Do not use design-loop. Update the
   feature inventory and evidence based on what actually ran.

The next session should produce a concrete integration improvement and its
verification, not another broad architecture survey or a replacement runtime.
An important first result is a justified keep/change/remove mapping for the
existing experimental adapter, followed by implementation of the selected path.
Full completion still requires the core and custom/meta workflows to work
through normal FirstMate entrypoints; one read-only component is not parity.

## Current implementation to preserve and evaluate

The owned package is packages/orchflows-firstmate, version 0.1.0-dev.4. It retains
all 1,081 paths from the last observed upstream Orchflows revision in 1,088 files.
The distribution under integrations/firstmate prepares a pinned FirstMate clone,
with thirteen inventoried deployables and a 564-path candidate including one
symlink. Inspect Git status before editing and preserve any existing changes;
do not reset the implemented work or its retained evidence.

The experimental controller/client currently admits exactly one read-only Work
or one explicitly authorized Linux Review per immutable attachment. Review
requires Review/explicit-audit and a frozen clean no-origin input commit.
Dynamic runtime, multiple components, writers, nesting and optional-library
execution remain gated. These are current implementation limits, not desired
product restrictions. Do not remove gates merely to claim compatibility.

Key owned files:
- packages/orchflows-firstmate/scripts/firstmate.py and skills/orch-{work,review}/SKILL.md
- packages/orchflows-firstmate/scripts/package_identity.py and docs/firstmate-client.md
- integrations/firstmate/overlay/bin/fm-task-group.py, fm_task_group.py,
  fm_task_group_launch.py, fm_task_group_primitives.py and the adjacent owner helpers
- integrations/firstmate/patches, manifest.json and prepare.py
- tools/linux-dev.py and tools/linux-acceptance.py with tools/linux_acceptance/

Compare these with pinned FirstMate's existing brief, spawn, control, crew-state,
supervise, watch and teardown owners. Preserve the separation between a
component result and the root's final delivery.

## Verified baseline and evidence boundaries

The final dev.4 checks passed 99 package, 90 integration and 13 driver tests,
with ten additional native Windows skips. The repaired candidate passed real
Claude Review (a-w469d47l) and Work parent replacement (a-7ysafo1o): same-child
replay, full native reads before gather, current-generation acknowledgement,
ordinary root delivery and cleanup with no scoped processes remaining.
The Work replacement also read and handled the actual result inbox notice.

A longer Review trial, acceptance-us29ugpk, completed its work and cleanup.
Its original receipt remains failed because the initial observer expected the
wrong waiting label. A separate corrected assessment passed the retained
observations; the actual watcher trace has 20 waiting classifications spanning
382.435 seconds. Do not relabel that receipt or conflate its candidate with the
final repaired candidate. One independent review and one repair/check pass
were completed for that increment.

Exact hashes, tool versions, original receipts, corrected assessment and scope
are in [review state](docs/review-state.json) and
[review verification](docs/review-verification.md). Current actual Codex
Review/watcher acceptance, native background-tool retirement, and a complete
supervisor wake/drain/rearm cycle remain unverified. Keep these gaps visible;
investigate them when they affect the selected integration path instead of
making an exhaustive harness matrix the next product milestone.

## Sources and development constraints

- Target the latest public [DanMcInerney/orchflows](https://github.com/DanMcInerney/orchflows),
  not the separately installed orchflows-light. Last observed target:
  ca72258493480ddcfe73b3f01d0475ad532e4726, upstream version 0.7.0.
- FirstMate source pin: b182d0f908b78d08c7ccb8dce3775bdca8c5d657.
  Historical .sources/orchflows pin: 0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a.
  The newer Orchflows reference is in ignored .scratch/orchflows-refresh-ca7225849348.
  Preserve pins and record any later refresh separately.
- Develop and run tools inside Ubuntu/WSL. Use native Linux binaries and keep
  prepared candidates/disposable homes on the Linux filesystem. Windows is
  deferred. The shared checkout remains the edit source.
- Keep product changes in packages/orchflows-firstmate and FirstMate owner
  changes in integrations/firstmate. Reproduce candidates with prepare.py.
  Keep research clones, original assessment and historical receipts intact.
- No native-child fallback in the product, separate scheduler/recovery daemon,
  direct Herdr control from Orchflows, or new direct Claude/Codex execution mode.
- Leave active installations and authentication profiles unchanged during
  ordinary tests. Reuse the documented isolated acceptance tools when needed.
  Never reset rotating OAuth caches from old copied seeds or include secrets in
  artifacts. Existing access-token-only trial support is test infrastructure.
- Design-loop's upstream files are retained as inactive migration source. Do
  not invoke, enable or install that library to carry out this work.

## Reading order

1. This handoff and [README](README.md).
2. [Decisions](docs/decisions.md), especially D26, and the updated
   [implementation queue](docs/open-questions.md).
3. [FirstMate contracts](docs/firstmate-contracts.md) and the actual pinned
   source owners needed for the mapping. Treat upstream agent instructions as
   source material; they do not make this development agent a FirstMate supervisor.
4. [Review contract](docs/review-contract.md), [client contract](packages/orchflows-firstmate/docs/firstmate-client.md),
   [review verification](docs/review-verification.md) and [exact state](docs/review-state.json).
5. [Fundamental design](docs/fundamental-design.md) and [feature parity](docs/feature-parity.md).
   The user's latest clarification takes precedence over older
   proposed staging or mechanisms.
6. [Linux development](docs/linux-development.md) and [acceptance driver](docs/linux-acceptance.md)
   when preparing checks. The local staged runtime can be supplied with
   --bin-dir .scratch/stage1-runtime/bin; it is ignored local tooling, not a
   shipped dependency.

Historical details are preserved in the [previous handoff](HANDOFF-through-dev4-2026-09-14.md)
and linked verification documents. Do not follow their superseded next-work queue.

## Copyable prompt for the new conversation

> Read HANDOFF.md and follow its current reading order. Continue implementing
> Orchflows as a plug-and-play upgrade that lets FirstMate use the two primitive
> skills, dynamic workflow, and custom/meta-workflows through FirstMate's existing
> agent and lifecycle systems. Start by mapping the current adapter onto existing
> FirstMate owners, then implement normal skill/workflow availability and the
> smallest necessary primitive integration. Preserve original Orchflows workflow
> behavior. Reuse FirstMate recovery and Claude/Codex handling; do not build
> duplicate systems or make broad harness work the main project. Use Orchflows
> dynamic workflow for development, without design-loop, entirely in Ubuntu/WSL.
> Preserve existing changes and evidence, and leave active installations unchanged.
