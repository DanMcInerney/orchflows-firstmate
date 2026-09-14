# Handoff: continue the plug-and-play FirstMate upgrade

## Latest direction and development rules

The user wants FirstMate to use Orchflows' Work/Review primitives, dynamic
workflow and custom/meta-workflows naturally. Orchflows owns skills, guidance
and composition. FirstMate owns agents, worktrees, communication, supervision,
recovery, cancellation, delivery and Claude/Codex integration on Herdr.

Reuse those owners; add only demonstrated missing glue. Do not build another
scheduler, recovery or writer service, direct Herdr adapter, native-child
fallback or exhaustive harness program. A FirstMate supervisor does not perform
project work merely because a selected workflow needs it.

Implementation remains authorized. Develop and verify through Ubuntu in WSL,
using Linux Python, Bash, Git and worker binaries. Keep the shared repository
as the edit source and disposable candidates/homes on the Linux filesystem.
Native Windows is deferred. Do not use design-loop.

Use the pinned upstream Orchflows dynamic development workflow: scoped makers
when useful, join/check, one fresh independent Review, then one repair/check
pass without another Review. Installed orchflows-light is not the source target
or this project's development workflow.

The user requested waiting for the in-flight PR before continuing. PR #3 merged
at 2026-09-14T18:51:03Z as d465c1a4d90e7144137a08073a79e5fd9c2cf451.
This increment started from that clean main checkout.

## What dev.7 implements

The [owner mapping](docs/firstmate-owner-mapping.md),
[normal-launch seam](docs/normal-launch.md) and
[dynamic composition](docs/dynamic-composition.md) remain the foundation.
The [local delivery contract](docs/local-delivery.md) adds:

- Explicit dynamic selection for an ordinary Linux Herdr ship/local-only task.
  Default ship selection keeps FirstMate's ordinary route. Unsupported selected
  modes refuse before task/workspace/endpoint allocation.
- Immutable kind, mode and fm/<task> branch identity in the existing attachment,
  task metadata and per-generation launch context. New capability/scope
  negotiation prevents retained scout clients from accepting ship delivery.
- The same multiple scoped Work requests, ordinary root Git joins, one Review
  of the exact clean joined candidate and one repair/check phase. Components
  remain scouts returning retained results to the parent.
- Ordinary root relaunch preserving selected delivery and accepted/gathered
  work. Changed delivery metadata, repository or branch requires reconciliation.
- The ordinary ready-in-branch completion signal and existing fm-merge-local
  owner for landing committed output. The worker does not merge or open a PR.
- Teardown protection for the promised branch even after a worktree branch
  switch. Existing backlog-close evidence and Treehouse claims support cleanup
  retries; the branch remains reachable until successful task-record removal.

The existing bounded Linux scout profile stays compatible. Both profiles keep
the 32-component bound, request-specific input/result identities, full retained
reads before gather, archival writer refs and aggregate lifecycle guards.
No-mistakes is not admitted; selected mode changes refuse. This increment does
not add a no-mistakes run parser or claim detection of a manually started
pipeline while metadata still claims local-only.

## Evidence and review

Read [local delivery verification](docs/local-delivery-verification.md) and
[exact state](docs/local-delivery-state.json) before runtime claims. The joined
candidate passed 128 package, 149 Linux integration and 23 driver checks.
One independent development Review found that switching to a landed worktree
branch could hide the unlanded promised delivery branch during cleanup.
The single repair/check pass fixed this at the existing teardown owner and
corrected stale package execution instructions. No second Review ran.

The first cleanup-repaired candidate passed 304 combined checks. Its actual
ordinary spawn attempt then exposed a pre-worker branch-ordering gap: the
pinned ship brief starts detached and tells the worker to create fm/<task>.
The same repair/check pass now allows only that pristine initial state and
keeps subsequent client, relaunch and delivery checks strict. The final
candidate passed **128 package, 154 Linux integration and 23 driver tests:
305 passed checks**, with ten explicit native Windows skips.

**Actual dev.7 local-only delivery is verified with a documented observer
correction and resumed cleanup.** Trial a-lf4thn46 used Sonnet 5/high as the user
requested. Native task/command/response records confirm that profile. Two makers,
ordinary root replacement while one maker ran, retained custom-skill rereading,
exact joined Review, final checks and ready-branch completion succeeded.

The original driver receipt failed because its observer treated a normal 2>&1
redirect as an extra gather argument. Full native reads preceded both the actual
first gather and durable owner acknowledgement. The repaired observer passes
all 25 pre-landing assertions on the unchanged trace. That original receipt
remains failed and unchanged; this is not a clean uninterrupted driver pass.

The existing fm-merge-local owner then landed the exact final commit. Initial
cleanup correctly refused ambiguous endpoint inspection after the earlier lab
shutdown. Restoring the same private lab through its existing owner proved the
retired endpoint absent; ordinary teardown then succeeded. Delivered code and
all six tests pass after cleanup, both writer refs survive, and no scoped
processes remain. These follow-ups launched no additional model. Final evidence
contains 26 acceptance assertions plus delivered-code/ref/cleanup checks.

The user refreshed the normal Ubuntu Claude login. Continue using the selected
current Ubuntu cache through the access-token-only driver; do not refresh/copy
it yourself. Acceptance now defaults to claude-sonnet-5 at high effort to avoid
unintended expensive model defaults. Product candidate/package checks and all
original/corrected/resumed receipt identities remain distinct in exact state.

Earlier dev.6 [dynamic verification](docs/dynamic-verification.md) remains exact
historical evidence. Driver preflight failures are preserved separately and
are not relabeled as worker trials. Authentication reads only the access token
from an explicitly selected current cache; it does not copy or reset rotating
credential caches. Active installations and pinned references remain untouched.
The original dated assessment and [dev.6 handoff](HANDOFF-through-dev6-2026-09-14.md)
are preserved.

## Next implementation work

1. **Exercise broader custom/meta composition through the same primitives.**
   Select a representative workflow-authoring or nested composition case that
   demonstrates the next missing interface. Retain complete libraries/guidance;
   introduce no workflow-specific runtime adapter. Verify its actual artifact
   and ordinary recovery, not only catalog availability.

2. **Use targeted compatibility evidence.**
   Current actual Codex composition, component continuation, native background
   retirement and the full supervisor wake/drain/rearm cycle remain open.
   Address a harness or lifecycle gap when it affects the selected feature;
   Linux Claude evidence does not certify these other cases.

3. **Extend delivery only at its existing owners when the selected case needs it.**
   Direct-PR/no-mistakes, promotion and broader policy combinations remain open.
   Preserve no-mistakes sole custody once validation begins; do not create an
   independent review or delivery pipeline.

Broader gaps include per-assignment controls, nesting, Build/SelfImprove,
artifact/history retention, optional-example runtime parity, remote homes,
installation/update/rollback and joint archival-ref/result pruning. Native
Windows stays deferred. Near feature parity remains the target.

## Source and ownership constraints

- Package: packages/orchflows-firstmate, version 0.1.0-dev.7; 1,091 files retaining
  all 1,081 paths of Orchflows ca72258493480ddcfe73b3f01d0475ad532e4726 (0.7.0).
- FirstMate pin: b182d0f908b78d08c7ccb8dce3775bdca8c5d657. Historical Orchflows
  research pin: 0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a. Current target reference
  remains ignored .scratch/orchflows-refresh-ca7225849348. Historical reference
  CRLF-only differences remain as found; do not normalize pinned source files.
- FirstMate changes belong in integrations/firstmate; package changes in the
  owned package. Nineteen inventoried deployable files, including six sequential patches,
  reproduce a 566-path candidate, including one symlink, through prepare.py.
  Patches 0005/0006 extend the existing spawn, merge and cleanup owners.
- Dynamic requests live under task-group/requests; legacy request.json remains.
  Output refs retain results; they do not establish another workspace owner.
- The Linux acceptance driver adds --local-only to its existing --dynamic,
  --custom-workflow and --restart paths. It reuses runtime/lab/auth/cleanup code.

Inspect Git status and preserve existing changes. Keep reusable document paths
portable and raw traces/disposable clones ignored or outside the repository.
Do not change active installations during package checks.

## Reading order

1. This handoff and [README](README.md).
2. [Local delivery contract](docs/local-delivery.md),
   [verification](docs/local-delivery-verification.md),
   [exact state](docs/local-delivery-state.json).
3. [Dynamic contract](docs/dynamic-composition.md), then its historical
   [verification](docs/dynamic-verification.md) and [state](docs/dynamic-state.json).
4. [Decisions](docs/decisions.md), [open work](docs/open-questions.md),
   [owner mapping](docs/firstmate-owner-mapping.md), [normal launch](docs/normal-launch.md).
5. [FirstMate contracts](docs/firstmate-contracts.md), affected pinned source
   owners and [client contract](packages/orchflows-firstmate/docs/firstmate-client.md).
6. [Fundamental design](docs/fundamental-design.md), [feature parity](docs/feature-parity.md),
   [Linux development](docs/linux-development.md) and [acceptance driver](docs/linux-acceptance.md).

Ignored native Linux dependencies are available through
--bin-dir .scratch/stage1-runtime/bin; they are not shipped dependencies.
