# Reassessment: the smallest useful FirstMate upgrade

September 14, 2026. This is a source-backed design reassessment, not a new
runtime release. It supersedes the previous next-milestone queue, while retaining
all existing runtime evidence and the feature migration inventory.

## Conclusion

Yes: the product contract and development priorities have become too complicated.
The recent increments concentrated on increasingly specific leaf-authoring and
acceptance sequences while per-assignment controls and ordinary saved-workflow
reuse remained unfinished. Much of the existing adapter correctly calls
FirstMate's owners; that useful glue should be retained.

The product is two execution primitives, Work and Review, plus instructions that
compose them. Dynamic, Build, SelfImprove and user workflows are compositions,
not new executors. FirstMate supplies the agents and their lifecycle.
Upstream dynamic itself is two paragraphs: perform useful work, join/check,
one independent Review, then one repair/check pass. [Upstream dynamic][dynamic]

## What FirstMate actually owns

Inspected FirstMate: `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`.
Inspected Orchflows: `ca72258493480ddcfe73b3f01d0475ad532e4726`.
Owned implementation reviewed at `1e41a6d0e9dd4880389a23989ffa36c78cad5b9c`
(package dev.8). These are pinned-source findings, not a claim about a later
upstream release.

| Step | Existing owner and behavior |
| --- | --- |
| Intake and selection | FirstMate interprets the task and its dispatch rules, choosing concrete harness/model/effort. Scripts do not interpret natural-language model preferences. [Dispatch][dispatch] |
| Instructions | `fm-brief.sh` creates the durable Captain's intent and Firstmate spec; `fm-spawn.sh` renders the current launch/role overlays. Workflow selection belongs in that existing route. |
| Launch | `fm-spawn.sh` accepts per-agent `--harness`, `--model`, `--effort`; uses its Herdr backend, obtains a Treehouse worktree and claims the slot, installs harness hooks, publishes task metadata, then launches the selected CLI. [Spawn][spawn] |
| Communication | `fm-send.sh` records task-inbox messages before ringing the worker; the existing watcher handles pending delivery. Component results need a return-to-parent binding and consumption record, not another inbox service. [Send][send] |
| Recovery | `fm-control.sh` preserves a worktree checkpoint and progress note and calls ordinary spawn/relaunch. Replacement is a fresh conversation in the retained worktree; it is not restoration of a native conversation. [Control][control] |
| Supervision | Crew-state, watch, classify and supervise owners interpret live task state. The current adapter projects outstanding/gathered component work into those owners. |
| Delivery | `fm-dod-lib.sh`, merge-local and teardown own the selected root's completion, merge authority and cleanup. A Work component returns to its caller; it does not deliver the outer task. |

FirstMate has two distinct delegation surfaces. Its primary/secondmates dispatch
fleet workers with records, endpoints and supervision. Ordinary crewmates may
also have harness-native subagent tools: the upstream subagent guard deliberately
exempts linked task worktrees. Those native children do not thereby acquire fleet
records. Use the first surface through our scoped component seam; keep the
native guard and do not turn workflow workers into unrestricted supervisors.
[Subagent guard][guard]

The existing glue is justified where ordinary FirstMate lacks the relationship:
which parent requested this component, whether a repeated request already
launched, where its result survives, whether the parent gathered it, and whether
the root is waiting for it. Endpoint state, worktree allocation, process control,
message retry and merging remain with their current owners.

## 1. Forward model and effort per assignment

**Existing support:** FirstMate already emits the launch flags. Our adapter
blocks access to it:

- [Package client](../packages/orchflows-firstmate/scripts/firstmate.py) lines
  28, 251–271 and 317–321 accept exactly four dynamic request fields.
- [Task-group owner](../integrations/firstmate/overlay/bin/fm_task_group.py)
  lines 242–243 copies harness/model/effort from the parent.
- [Spawn bridge](../integrations/firstmate/overlay/bin/fm-task-group-spawn.sh)
  lines 117–119 requires those choices to equal the parent's.

**Small change:** add optional assignment controls to the existing request,
validate and record the resolved selection before admission, include it in
request identity, and pass it to the existing spawn owner. Validate launch
against the accepted child request, replacing the parent-equality assumption.
Replays retain that accepted selection. Keep legacy requests working and
negotiate new client capability before relying on it.

Resolve model and effort independently, preserving Orchflows precedence:

1. Current caller's named-assignment choice.
2. Current caller's operation default.
3. Saved workflow's named-assignment preference.
4. Saved workflow's operation default.
5. FirstMate's applicable dispatch/default resolution.

Do not turn the authoring session's own model into a saved workflow preference.
A workflow's requested reviewer model also cannot be satisfied by reviewing in
the maker's existing session. [Orchflows controls][controls]

Harness selection stays with FirstMate. A model name must be interpreted for
the chosen harness, not used to guess a provider or credential store. Unspecified
controls defer to FirstMate; carrying a root setting to children should reflect
an applicable task-wide preference, not an accidental metadata copy.

There is one demonstrated compatibility issue at the existing launch owner:
the pinned FirstMate accepts Codex `max` effort in task metadata but emits no
effort flag for it. Claude `high` emits `--effort high`; Codex `high` emits
`model_reasoning_effort="high"`. Explicit workflow controls must either be
honored or refused before launch. Put that check in FirstMate's existing
model/effort owner for attached workflow assignments; do not create a second
Claude/Codex launcher or assume metadata proves the effective setting.
[Flag implementation][flags]

## 2. Save libraries in a FirstMate-owned home

**Proposed default**, using the existing package home layout:

```text
$FM_HOME/
  data/.orchflows-home/                  editable workflow home
    libraries/<library>/
      plugin.json
      skills/<workflow>/SKILL.md
      guidance/
      references/
      trials/
    .local/                       existing setup-managed files
  data/.orchflows/                 existing immutable enabled bundles
  config/orchflows.json            existing project enablement
```

The hidden home name avoids FirstMate's ordinary task-ID namespace:
a task named orchflows is valid and would place its brief under data/orchflows.
Keep user libraries outside data/<task-id>; no task-ID reservation change is
needed for the proposed hidden directory. [Task-ID owner][taskids],
[brief directory][briefdir]

The folder location is a recommendation, not an implemented default or a user
decision. The fork currently defaults to `~/.orchflows-firstmate`, and already
supports an explicit `--home` or `ORCHFLOWS_FIRSTMATE_HOME`. Normal Orchflows'
`~/.orchflows` is protected against overlapping setup.
[Home identity](../packages/orchflows-firstmate/scripts/package_identity.py)

There is no need for a workflow database or new save format. Build creates an
ordinary library directory. Existing `setup` refreshes catalogs while preserving
user libraries; `resolve` loads a library or skill. Libraries retain guidance,
references, scripts and assets, not just SKILL.md files. Identity remains
`<library>:<skill>`. [Upstream home][home]

**Missing connection:** make the chosen workflow home visible to FirstMate
intake, resolve a selected workflow into the ordinary brief, and feed its complete
selected libraries to existing enablement/snapshot code. The running worker
reads the retained catalog through its launch context. Native slash-command
registration is optional UI convenience; it is not required to execute the
selected instructions.

For "create and save this workflow", author and trial in the worker's assigned
worktree, then use a narrow FirstMate-owned publication step to copy the finished
library into the configured home and refresh its catalog. Current worker write
permissions do not make arbitrary home writes valid. Reuse package validation,
catalog generation and normal delivery; do not create an artifact service.
Expose this as one product operation rather than requiring users to assemble
setup, publication, enablement and brief paths themselves.

Newly launched tasks should see the newly published library after the selected
bundle is refreshed. Active tasks keep the package/library snapshot they began
with; they must not silently change when the author edits a file. The existing
`fm_orchflows.enable` and task attachments already supply this separation.
The two directories above are editable source and retained run inputs.

## 3. Compose workflows without inventing another runtime

Loading another workflow's SKILL.md normally continues in the same agent
context. Only Work or Review starts another agent. Consequently:

- A saved release workflow calling dynamic, which calls Work/Review, can use
  the existing root client. This basic composition is already admitted.
- A larger workflow calling two dynamic phases needs each phase's independent
  review policy; it does not require nested agents.
- A Work assignment that itself runs a delegating workflow does need a scoped
  child-to-grandchild request through FirstMate. That is distinct from reading
  another skill in the same context.

The current task-group owner hardcodes **one Review across the entire root**
(lines 221–227), and treats all later Work as repair (247–248). That is a bounded
dynamic profile, not a generic implementation of both primitives. A larger
authorized composition cannot reuse dynamic twice under it. The component
overlay also forbids all Work/Review calls, and the fork's Build skill permits
only non-delegating leaf authoring.

Move composition rules back to their intended scope. Preserve one Review per
dynamic invocation; allow only the reviews/loops the selected caller composition
authorizes. If owner enforcement needs a workflow-call identifier, keep it as
compact scope in existing task records, not a scheduler or new workflow engine.
Do not simply remove every review guard.

Restore Build's ability to author a composing workflow and trial that workflow
through the same primitives. First support caller-context composition; add the
small scoped descendant seam when a representative trial actually delegates
inside a Work component. Preserve parent/result bindings, group capacity and
FirstMate lifecycle ownership. Larger composition remains part of the core goal,
not a permanently excluded optional feature. [Architecture][architecture]

## 4. Keep FirstMate's skills

Do not remove or reimplement harness-adapters, dispatch/quota selection,
recovery, supervision, project management, secondmate provisioning or delivery
skills in Orchflows.

Add a thin FirstMate routing/catalog integration and the Orchflows skill package.
FirstMate's internal `.agents/skills` is supervisor material; user workflow
libraries belong in the configured library home, and selected workflow
instructions go to task workers. Copying a skill into an arbitrary FirstMate
folder does not make it available to those workers.
[Loaded surfaces][surfaces]

There is a real policy conflict to resolve at the existing policy owner:
upstream FirstMate's fast paths normally forbid an added independent reviewer.
Our patches already provide an explicit exception for the bounded dynamic
profile. Generalize that selection deliberately so an Orchflows workflow may
perform its authorized Review. Keep no-mistakes' sole validation custody when
that pipeline is selected; do not silently stack both review/fix systems or
delete the pipeline. FirstMate self-development has its own explicit
no-delegation role contract and remains a separate compatibility case.
[Policy][policy], [current patch](../integrations/firstmate/patches/0004-dynamic-composition.patch)

## What to keep, simplify and do next

| Keep | Simplify or complete |
| --- | --- |
| Existing spawn, Treehouse, Herdr, inbox, recovery, supervision and delivery owners | Forward assignment controls through them |
| Request deduplication, generation checks, retained results and parent consumption | Remove parent-only control inheritance and whole-root dynamic assumptions |
| Complete package/library retention and migration inventory | Connect editable library home, publication, discovery and bundle refresh |
| Existing tests and historical receipts | Use behavior-based targeted checks; exact shell formatting is an observer issue, not a product milestone |
| Full upstream source and optional examples | Stop treating preserved file counts as evidence of working composition |

**Next product milestone:** create a useful composed workflow, save it in the
chosen home, and invoke it by identity from a larger workflow through ordinary
FirstMate intake. Demonstrate different assignment model/effort choices reaching
the actual agents, the required independent reviews, retained output and normal
root delivery. Then edit the saved workflow and prove a new run sees the update
while an existing run keeps its original instructions.

Implement controls and home/discovery first, then remove the demonstrated
composition barriers. Extend only the existing owners affected by that story.
Verify request replay, selected controls, save/resolve, review scope and one
representative real run. Obtain actual evidence for both worker harnesses before
claiming both supported; target compatibility failures where they occur.
The current Git admission also requires a clean no-origin project and forbids
tracked symlinks and submodules:
[clean_commit](../integrations/firstmate/overlay/bin/fm_task_group_store.py)
lines 172–185. These lab-profile restrictions are not general FirstMate
compatibility. Before describing the upgrade as drop-in for ordinary projects,
exercise the intended registered project shape and delivery through FirstMate's
existing owners, and revise only the demonstrated incompatible admission.
Do not remove FirstMate's own local-only or repository-safety rules blindly.

A full restart/cancellation matrix, every optional library, native Windows and
all delivery modes do not have to precede this milestone.

## Checks in this reassessment

- Confirmed both pinned upstream HEADs and a clean owned checkout at the starting
  commit. Read the actual owners listed above, rather than adopting upstream
  supervisor instructions.
- Ran seven Linux source-boundary probes: standard dynamic request accepted;
  model, effort and harness request fields each rejected; extracted pure
  FirstMate effort function emitted Claude/high and Codex/high flags and omitted
  Codex/max. The function extraction executed no spawn top-level code.
- Ran a disposable Linux package-home smoke check: setup with host configuration
  skipped, write a personal workflow, rerun setup, resolve it and resolve logical
  orchflows to fork dev.8; both libraries appeared in the generated catalog.
  No worker, native registration or active home was involved.
- One fresh independent Review found a collision between the initial proposed
  data/orchflows path and the ordinary task-ID namespace. The single repair
  pass changes the recommendation to data/.orchflows-home, corrects the spawn
  bridge citation, and makes current Git admission limits explicit. No second
  Review ran.
- Runtime/package code is unchanged. Prior qualified Claude composition/delivery
  evidence remains in [repair verification](leaf-repair-verification.md).
  Per-assignment profiles, home publication/discovery and broader composition
  above are proposed work, not newly validated capabilities.

[dynamic]: https://github.com/DanMcInerney/orchflows/blob/ca72258493480ddcfe73b3f01d0475ad532e4726/skills/orch-dynamic-workflow/SKILL.md
[architecture]: https://github.com/DanMcInerney/orchflows/blob/ca72258493480ddcfe73b3f01d0475ad532e4726/docs/architecture.md
[controls]: https://github.com/DanMcInerney/orchflows/blob/ca72258493480ddcfe73b3f01d0475ad532e4726/docs/architecture.md#L32-L38
[home]: https://github.com/DanMcInerney/orchflows/blob/ca72258493480ddcfe73b3f01d0475ad532e4726/docs/home.md
[dispatch]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.agents/skills/harness-adapters/references/common/dispatch.md
[spawn]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-spawn.sh
[flags]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-spawn.sh#L1983-L2008
[guard]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-subagent-pretool-check.sh#L174-L190
[send]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-send.sh#L941-L1014
[control]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-control.sh#L690-L802
[surfaces]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/AGENTS.md#L63-L67
[policy]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/AGENTS.md#L337-L342

[taskids]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-pr-lib.sh#L92-L110
[briefdir]: https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-brief.sh#L186-L188
