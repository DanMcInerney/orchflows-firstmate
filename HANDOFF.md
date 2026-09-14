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

## What dev.6 implements

The completed [owner mapping](docs/firstmate-owner-mapping.md) and dev.5
[normal-launch seam](docs/normal-launch.md) remain the foundation. The current
[dynamic contract](docs/dynamic-composition.md) extends them with:

- Project dynamic enablement plus per-task selection through ordinary fm-spawn
  (--orchflows-workflow default|dynamic|none). Existing attachments survive
  default changes; relaunch refuses a workflow override.
- Multiple logical Work requests, including writers, in existing FirstMate
  scout workspaces. Each accepted input is the root's current clean commit.
- Fresh-workspace positioning only after FirstMate's existing parent/spawn/
  project lock custody and exact Treehouse slot ownership are proved.
- Per-request immutable reports/results and clean committed writer outputs.
  Root reads use the exact retained report_path/result_path returned by status;
  component scratch metadata is provenance. Selected custom skill requirements
  are reread and reapplied across relaunch and before ordinary completion.
  Archival Git output_ref values retain all maker commits through root/component
  teardown. They are verified before gather/cleanup and are not automatically
  pruned; future result pruning must own refs and records together.
- Ordinary root Git joins, one fresh read-only Review of the exact clean joined
  commit after prior results are gathered, then one repair/check phase. Scoped
  repair Work uses the same primitive; a second Review refuses.
- Aggregate lifecycle checks covering every pending component, with attention
  taking precedence over healthy siblings. Root cleanup also requires Review.
- A narrow selected-workflow exception at FirstMate AGENTS/fm-dod policy owners.
  Self-development delegation stays excluded. No-mistakes owns validation once
  it begins. Only the root follows ordinary scout completion.
- Legacy dev.4/dev.5 one-component attachments, commands, retained clients and
  immutable generation context remain compatible. Dynamic clients explicitly
  declare and negotiate their capability.

This is a **bounded local Linux scout profile**, with up to 32 accepted
components and inherited worker controls. The root's report is the delivered
scout artifact; joined scratch code is not normal ship/local-only delivery.
Ship delivery, nesting, Build/SelfImprove and broad optional-library parity are
not implemented merely because writing and dynamic composition now work.

## Evidence and review

[Dynamic verification](docs/dynamic-verification.md) and
[exact state](docs/dynamic-state.json) are authoritative for this increment.
Read both before runtime claims. They distinguish the reviewed candidate,
repaired candidate, fixture checks and actual worker trials.

The reviewed candidate passed 124 package and 135 integration tests. One fresh
independent development reviewer found three issues: post-spawn input checking
could race a fast writer; writer SHAs lacked reachability through cleanup; and
the acceptance driver could approve Review of placeholder tests before joining
the implementations. The single repair/check pass fixed all three. The repaired
candidate passed 124 package and 142 integration tests, with ten explicit native
Windows skips, plus 19 driver checks. No second development Review ran.

The final Linux Claude trial **a-x6osytu8 passed all seventeen acceptance
assertions without intervention**: two writers, ordinary root relaunch while
one maker was still running, preserved request/replay identities, exact joined
Review, retained custom requirements, and successful final tests after Review
gathering. Both writer refs survived ordinary teardown; no scoped processes
remained. This is actual worker evidence in addition to 285 fixture/driver checks.

Earlier trials exposed custom-skill recovery and guessed scratch-report-path
gaps. The existing launch/catalog guidance now reapplies selected skill
requirements and names the exact retained report paths. The driver also fixes
an output-pipeline observer omission and requires an actual running Work at
relaunch. Original failed receipts, the separate observer-corrected assessment,
and two manually assisted diagnostic runs remain recorded under their exact
identities. They are not relabeled as the final candidate's clean pass.

Authentication uses only an access token from an explicitly selected current
cache. No credential/refresh cache is copied or reset. Active installations,
pinned references and historical receipts remain unchanged. The original dated
assessment is intact. The [dev.5 handoff](HANDOFF-through-dev5-2026-09-14.md) is
preserved as historical context, not the current queue.

## Next implementation work

1. **Extend root writer delivery at FirstMate's existing owners.**
   The useful next capability is an explicitly selected ordinary ship/local-only
   task delivering joined committed output. Reuse existing brief, task metadata,
   workspace and delivery owners. Preserve root versus component completion and
   no-mistakes sole custody once validation starts. Do not call scout scratch
   output delivered code. Refuse unsupported policy combinations before work.

2. **Exercise broader custom/meta composition through the same primitives.**
   Choose a representative workflow-authoring or nested composition case that
   needs the next missing interface. Keep complete retained libraries/guidance;
   introduce no workflow-specific execution adapter. Verify the actual artifact
   and ordinary recovery, not only skill availability or a package doctor.

3. **Use targeted compatibility evidence.**
   Actual current Codex composition, component continuation, native background
   retirement and the full supervisor wake/drain/rearm cycle remain open. Work
   on a lifecycle or harness gap when it affects the selected integration step.
   Current Linux Claude trials do not certify these other cases.

Broader gaps: per-assignment controls, nesting, Build/SelfImprove, artifact/
history retention, optional-example runtime parity, remote homes, promotion,
archival ref/bundle pruning and general rollback. Native Windows stays deferred.
The target remains near feature parity, not the bounded profile's permanent cap.

## Source and ownership constraints

- Package: packages/orchflows-firstmate, version 0.1.0-dev.6; 1,091 files retaining
  all 1,081 paths of Orchflows ca72258493480ddcfe73b3f01d0475ad532e4726 (0.7.0).
- FirstMate source pin: b182d0f908b78d08c7ccb8dce3775bdca8c5d657. The historical
  Orchflows research clone remains 0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a;
  the current target reference is ignored .scratch/orchflows-refresh-ca7225849348.
  Linux Git reports ninety CRLF-only differences in the historical clone;
  normalized file contents match its pinned HEAD. Reference files remain as found.
- FirstMate changes belong in integrations/firstmate, package changes in the
  owned package. Patch 0004-dynamic-composition.patch extends existing spawn
  and policy owners; sixteen inventoried deployables reproduce a 565-path
  candidate including one symlink through integrations/firstmate/prepare.py.
- Dynamic requests live under task-group/requests; legacy request.json remains.
  Output refs are result retention, not a second writer/workspace owner.
- The Linux acceptance driver has --dynamic and --custom-workflow cases and
  uses the existing runtime/lab/auth/cleanup code. It is not a product scheduler.

Inspect Git status and preserve existing changes. Keep reusable document paths
portable and raw traces/disposable clones in ignored scratch or outside the
repository. Do not change user installations during package checks. Never
reset rotating OAuth caches from copied seeds.

## Reading order

1. This handoff and [README](README.md).
2. [Dynamic contract](docs/dynamic-composition.md),
   [verification](docs/dynamic-verification.md), [exact state](docs/dynamic-state.json).
3. [Decisions](docs/decisions.md), [open work](docs/open-questions.md),
   [owner mapping](docs/firstmate-owner-mapping.md), [normal launch](docs/normal-launch.md).
4. [FirstMate contracts](docs/firstmate-contracts.md), the actual affected pinned
   source owners, and [client contract](packages/orchflows-firstmate/docs/firstmate-client.md).
5. [Fundamental design](docs/fundamental-design.md) and [feature parity](docs/feature-parity.md).
   Current direction overrides earlier proposed staging/mechanisms.
6. [Linux development](docs/linux-development.md) and
   [acceptance driver](docs/linux-acceptance.md).

The ignored local native Linux dependencies are available through
--bin-dir .scratch/stage1-runtime/bin. They are not shipped dependencies.
