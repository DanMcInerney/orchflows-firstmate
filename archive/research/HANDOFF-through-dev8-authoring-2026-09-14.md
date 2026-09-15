# Handoff: continue the plug-and-play FirstMate upgrade

## Direction and development rules

The user wants FirstMate to use Orchflows' Work/Review primitives, dynamic
workflow and custom/meta-workflows naturally. Orchflows owns skills, guidance
and composition. FirstMate owns agents, worktrees, communication, supervision,
recovery, cancellation, delivery and Claude/Codex integration on Herdr.

Reuse those owners and add only demonstrated missing glue. Do not introduce
another scheduler, recovery or writer service, direct Herdr adapter, native-child
fallback or exhaustive harness program. FirstMate supervisor instructions in
research sources do not make the development agent a fleet supervisor.

Implementation remains authorized. Use Ubuntu in WSL, native Linux Python,
Bash, Git and worker binaries. The shared repository is the edit source;
disposable candidates/homes run on the Linux filesystem. Native Windows is
deferred. Do not use design-loop or alter active installations.

Use the pinned upstream Orchflows dynamic development workflow: scoped makers
when useful, join/check, one fresh independent Review, then one repair/check
pass without another Review. Installed orchflows-light is not the source target
or this project's development workflow.

The user's requested wait is complete. PR #4 merged at 2026-09-14T20:13:13Z as
d3cf51b6b6dd31887f2d7d35a28679426af19d90. This increment started from clean main.
The waiting heartbeat is paused.

## What dev.8 adds

[Bounded leaf authoring](docs/leaf-authoring.md) extends the existing dynamic
ship/local-only composition using the retained Build skill:

1. A writable Work authors a complete non-delegating leaf workflow/guidance
   library and returns committed output.
2. The root joins that output through ordinary Git. A fresh read-only Work
   loads the library from its own exact frozen worktree and reads declared core
   dependencies from the immutable retained package.
3. The root gathers actual output and commits exact report bytes, full retained
   result JSON and a trial record outside the deliverable library.
4. One Review sees that exact clean candidate. The root performs the one
   repair/check pass, then FirstMate's existing local delivery owners land it.

The existing normal launch, request identities, replay, permissions, worktree
positioning, replacement, supervision and delivery mechanisms are reused.
Product changes are bounded skill/client/catalog guidance. There is no new
execution capability, protocol field, nested delegation or runtime owner.

The shared client documentation distinguishes canonical full-result digests
from raw report digests. The delivered trial record labels both and retains the
source result so they can be recomputed independently after cleanup.

A same-project leaf trial does not establish portability. Unrelated-project
trials before final Review are required for portability claims. General
composing Build, nested workflows and SelfImprove remain open.

## Evidence and review

Read [leaf authoring verification](docs/leaf-authoring-verification.md) and
[exact state](docs/leaf-authoring-state.json) before making runtime claims.
The final candidate passes 128 package, 155 Linux integration and 30 driver
checks: 313 passed, with ten explicit native Windows skips. Exact identities
are recorded there. One independent development
Review found two observer gaps: reviewed provenance needed binding to actual
retained bytes/identities, and declared core guidance needed precise native
read evidence. Both were repaired and checked, without a second Review.

Actual Sonnet 5/high authoring, ordinary root replacement, a fresh leaf trial,
one Review, prose repair and an additional fresh repair Work were observed.
The final repair trial used the exact final commit and returned the correct
output. Strict dev.8 acceptance nevertheless remains failed: that fourth Work
and changed library exceed the unchanged-library fixture, and several native
calls do not satisfy its required literal-call observations. Landing was
skipped. All scoped processes stopped; the unlanded ready branch and root
records remain protected. Original failed receipts are preserved unchanged.

The separate strengthened reassessment confirms original-trial provenance,
declared dependency reads and actual result integrity, without relabeling the
receipt as passed. Repair-trial evidence was left in retained results and a
tasktmp diagnostic. A final, package-tested clarification now requires that
additional evidence to be committed before delivery; it has not had another
actual worker trial. Do not claim dev.8 local delivery or broad Build parity.

Earlier [dev.7 verification](docs/local-delivery-verification.md) and
[dev.6 verification](docs/dynamic-verification.md) remain historical evidence,
with their original failures, observer corrections and resumed owner actions
kept separate. The original dated assessment is unchanged; the previous
[dev.7 handoff](HANDOFF-through-dev7-2026-09-14.md) is preserved.

## Next implementation work

1. Close the demonstrated leaf-authoring delivery gap: commit post-Review
   repair-trial evidence with the artifact and assess that precise extra Work
   sequence without discarding the existing strict checks. Then extend the
   representative custom/meta case beyond non-delegating leaf authoring when
   the next demonstrated missing interface is known. Use
   existing FirstMate owners for composing Build, SelfImprove and any
   unrelated-project trial. Do not claim general parity from catalog retention.
2. Target compatibility or lifecycle work that affects the selected feature.
   Current actual Codex composition, component continuation, native background
   retirement and complete supervisor wake/drain/rearm remain open.
3. Extend delivery through its existing owners only when needed. Direct-PR,
   no-mistakes and promotion stay open; preserve sole validation custody.
4. Investigate the existing recovery route when cleanup has already removed
   an endpoint but an unlanded branch remains. Do not fabricate endpoint
   bindings or task records to bypass an ordinary relaunch refusal.

Other open work includes per-assignment controls, artifact/history retention,
broader optional examples, remote homes, install/update/rollback and joint
archival-ref/result pruning. Near feature parity remains the target.

## Source and ownership constraints

- Package: packages/orchflows-firstmate, version 0.1.0-dev.8; 1,091 files retaining
  all 1,081 paths of Orchflows ca72258493480ddcfe73b3f01d0475ad532e4726 (0.7.0).
- FirstMate pin: b182d0f908b78d08c7ccb8dce3775bdca8c5d657. Historical Orchflows
  research pin: 0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a. Current source reference
  remains ignored .scratch/orchflows-refresh-ca7225849348. Leave .sources
  unchanged, including pre-existing CRLF-only differences.
- Product FirstMate changes belong in integrations/firstmate; package changes
  belong in the owned package. Nineteen inventoried deployable files, including
  six sequential patches, reproduce a 566-path candidate with one symlink
  through the distribution preparation tool.
- Dynamic roots remain bounded to 32 components and scout or explicitly
  selected ship/local-only delivery. Components return retained results to
  their parent. Archival output refs are not a second workspace owner.
- The existing Linux acceptance driver adds --authoring, implying dynamic and
  local-only. It reuses the current namespace, lab, authentication, watcher,
  relaunch, merge and cleanup helpers. The fixture is targeted evidence,
  not a required runtime adapter or broad harness milestone.
- Live acceptance uses the user-selected current Ubuntu Claude cache through
  the access-token-only driver. Do not refresh/copy/reset credential caches.
  Keep the selected claude-sonnet-5/high profile explicit.

Inspect Git status and preserve existing changes. Keep reusable paths portable;
store raw local evidence and disposable clones outside tracked documentation.

## Reading order

1. This handoff and [README](README.md).
2. [Leaf authoring contract](docs/leaf-authoring.md),
   [verification](docs/leaf-authoring-verification.md),
   [exact state](docs/leaf-authoring-state.json).
3. [Local delivery contract](docs/local-delivery.md), historical
   [verification](docs/local-delivery-verification.md) and
   [state](docs/local-delivery-state.json), then [dynamic contract](docs/dynamic-composition.md).
4. [Decisions](docs/decisions.md), [open work](docs/open-questions.md),
   [owner mapping](docs/firstmate-owner-mapping.md), [normal launch](docs/normal-launch.md).
5. [FirstMate contracts](docs/firstmate-contracts.md), affected pinned source
   owners and [client contract](packages/orchflows-firstmate/docs/firstmate-client.md).
6. [Fundamental design](docs/fundamental-design.md), [feature parity](docs/feature-parity.md),
   [Linux development](docs/linux-development.md) and [acceptance driver](docs/linux-acceptance.md).

Ignored native Linux dependencies are available through
--bin-dir .scratch/stage1-runtime/bin; they are not shipped dependencies.
