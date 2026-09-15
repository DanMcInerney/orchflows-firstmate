# Handoff: make Orchflows a plug-and-play FirstMate upgrade

## Latest user direction

The user wants FirstMate to use Orchflows' Work and Review primitives, dynamic
workflow, and custom/meta-workflows as naturally as Claude or Codex uses original
Orchflows. Orchflows owns skills, guidance and composition. FirstMate owns agents,
worktrees, communication, supervision, recovery, cancellation, delivery and
Claude/Codex integration on Herdr.

Reuse those existing owners. Do not build a replacement runtime, duplicate
recovery or writer system, direct Herdr adapter, native-child fallback, or an
exhaustive harness program. A FirstMate supervisor may not perform project work
merely because a workflow needs it.

Implementation remains authorized. Develop and verify entirely through Ubuntu
in WSL, using Linux Python, Bash, Git and worker binaries. Keep the shared
checkout as the edit source and candidates/disposable homes on the Linux
filesystem. Native Windows is deferred. Do not use design-loop.

Use upstream Orchflows dynamic workflow for development: ready scoped makers
when useful, join and check, one fresh independent Review, then one repair/check
pass without another Review. The installed orchflows-light is not the source
target or the development workflow for this project.

## What the dev.5 continuation implemented

The [owner mapping](docs/firstmate-owner-mapping.md) audits every baseline added
helper and record against actual FirstMate owners. Scoped request identity,
parent/child binding, retained results, acknowledgement and input/package
provenance remain necessary workflow context. Dispatch, workspace allocation,
current task metadata, inbox delivery, recovery and outer completion remain with
the existing FirstMate owners. The pinned subagent guard is not a worker-facing
fleet child API.

The [normal launch seam](docs/normal-launch.md) now provides:

- One-time project enablement of the fork and selected complete custom libraries.
  FirstMate stores immutable bundles under data/.orchflows and maps local project
  paths in config/orchflows.json. No active user installation is changed.
- Ordinary fm-spawn.sh applies a matching default to a new scout before
  endpoint/worktree allocation. Existing attachments and task metadata take
  precedence over changed or disabled defaults.
- Launch briefs contain retained core and library skill paths. Selected library
  order and complete guidance/reference/asset files survive source changes.
- New clients use immutable per-generation context supplied by the existing
  spawn/relaunch owner. Workers no longer construct controller/home/root/
  generation flags for each call.
- Client capability metadata selects the invocation contract. New enablement
  requires declared context support. Retained dev.4 attachments keep their
  explicit commands across owner upgrades and relaunches.

The current project profile still admits exactly one read-only Work or one
explicitly authorized Linux Review. A selected custom skill may compose that
one admitted primitive. This is useful normal-entrypoint integration, not full
dynamic/custom/meta parity. Do not widen gates merely to advertise compatibility.

## Current evidence

[Normal launch verification](docs/normal-launch-verification.md) and
[exact state](docs/normal-launch-state.json) are authoritative for this increment.
They distinguish the reviewed candidate, the compatibility repair, fixtures and
actual Linux worker trials. Read them before making runtime claims.

The repaired fixture run passed 111 package and 112 integration tests, with ten
explicit native Windows skips; fourteen acceptance-driver checks passed.
The independent reviewer found one high-impact issue: new short commands broke
retained dev.4 clients. One repair pass added capability selection and an exact
dev.4-client status/gather regression under a changed parent generation. No
second independent Review was performed.

The first actual enabled custom Work/replacement trial passed before that
compatibility repair. Final repaired Work/replacement and Review observations
are recorded in the verification documents. The custom trial changes its
library source after enablement and requires the worker to read the retained
skill before submitting, then include its instruction-specific receipt marker
in the ordinary root report.

Historical dev.4 receipts remain unchanged in [Review verification](docs/review-verification.md)
and [review state](docs/review-state.json), including the separately corrected
long-watcher assessment. Do not conflate those candidates with dev.5.

## Next implementation work

1. **Extend the existing primitive seam to actual dynamic composition.**
   The mapping is complete for this baseline; do not start another broad
   architecture survey. Inspect only the owners needed to let a root request
   more than one useful Work result, join an exact candidate, request one fresh
   independent Review and make the single repair/check pass. Replace the
   one-request restriction with the smallest tested extension of the current
   FirstMate-owned request/result context. Reuse normal worktree allocation and
   result/inbox delivery. Do not make another scheduler or recovery daemon.

2. **Reconcile composition-selected review and writer delivery at their owners.**
   Project enablement currently selects Work or Review for all future scouts of
   that project. A natural per-task dynamic invocation needs policy and
   primitive selection through normal FirstMate intake/brief/launch contracts.
   FirstMate's pinned AGENTS policy prohibits routine independent review under
   ordinary delivery; fm-dod-lib owns role/delivery prose and self-development
   restrictions. Make an explicit narrow owner change for a selected workflow's
   review. Keep no-mistakes sole ownership once validation starts, and preserve
   root delivery versus component completion.

3. **Demonstrate a dynamic and a representative composed custom workflow.**
   Use the implemented enablement/catalog/context route in a disposable Linux
   home. A custom one-primitive wrapper is already supported; broader custom and
   meta workflows must compose the same improved primitives rather than get
   workflow-specific adapter code. Exercise useful writing/join/review where
   needed through FirstMate's workspaces. Relaunch through fm-control.sh and
   retain accepted work. Target changed interfaces; do not turn this into a
   general Claude/Codex integration project.

4. **Review once and repair once for that new increment.**
   Keep the upstream feature inventory, living evidence and remaining queue
   accurate. A copied skill, package doctor or mocked launch is not proof of
   working fleet parity.

Known gaps: full dynamic Work-to-Review composition, writer joins, nesting,
Build/SelfImprove and broader custom/meta execution; automatic bundle pruning
and general rollback; optional-example runtime parity; current actual Codex
normal-launch/Review/watcher acceptance; native background-tool retirement; full
supervisor wake/drain/rearm cycle; remote homes and promotion. Native Windows
remains deferred. Investigate a lifecycle or harness gap when it affects the
selected integration step.

## Owned files and source constraints

- Package: packages/orchflows-firstmate, version 0.1.0-dev.5. It retains all
  1,081 paths from the observed upstream target, now in 1,090 files.
- New package capability declaration: scripts/firstmate-client.json.
  scripts/firstmate.py validates launch context without adopting a newer
  generation from mutable metadata.
- FirstMate glue: integrations/firstmate/overlay/bin/fm_orchflows.py,
  fm-task-group.py, fm_task_group_launch.py and existing adjacent owners.
  Patch 0003-normal-workflow-launch.patch extends fm-spawn.sh.
- The distribution has fifteen inventoried deployables and a 565-path candidate
  including one symlink. Reproduce it with integrations/firstmate/prepare.py.
- The exact dev.4 compatibility client is retained as a hash-checked test fixture
  under integrations/firstmate/tests/fixtures. It is not installed in candidates.
- The targeted Linux acceptance driver has --enabled and --custom-workflow
  options. It uses existing private lab, auth and cleanup support.

Source pins remain Orchflows ca72258493480ddcfe73b3f01d0475ad532e4726 (0.7.0)
and FirstMate b182d0f908b78d08c7ccb8dce3775bdca8c5d657. The historical Orchflows
research clone is 0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a. The newer reference
is ignored .scratch/orchflows-refresh-ca7225849348. Preserve those references;
record later upstream refreshes separately.

Inspect Git status before editing and preserve the current changes. Keep
reusable documents portable, raw traces and disposable clones in ignored
scratch or outside the repository, the original dated assessment unchanged,
and active installations/authentication profiles untouched. Never reset
rotating OAuth caches from copied seeds. The acceptance driver may select only
an access token from an explicitly chosen current cache; it copies no
credential or refresh-token file.

## Reading order

1. This handoff and [README](README.md).
2. [Decisions](docs/decisions.md), [open work](docs/open-questions.md),
   [owner mapping](docs/firstmate-owner-mapping.md), [normal launch](docs/normal-launch.md).
3. [Current verification](docs/normal-launch-verification.md) and
   [exact state](docs/normal-launch-state.json).
4. [FirstMate contracts](docs/firstmate-contracts.md), actual pinned source owners,
   [Review contract](docs/review-contract.md), [client contract](packages/orchflows-firstmate/docs/firstmate-client.md).
5. [Fundamental design](docs/fundamental-design.md) and [feature parity](docs/feature-parity.md).
   The latest user direction overrides older proposed staging/mechanisms.
6. [Linux development](docs/linux-development.md) and
   [acceptance driver](docs/linux-acceptance.md).

Local native dependencies can be supplied with
--bin-dir .scratch/stage1-runtime/bin. They are ignored local tooling, not
shipped dependencies. The [older handoff](HANDOFF-through-dev4-2026-09-14.md)
is historical context, not the next-work queue.
