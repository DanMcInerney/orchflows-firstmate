# Dynamic composition increment verification

The dev.6 increment adds bounded Linux dynamic composition to the existing
FirstMate normal-launch seam. [The contract](dynamic-composition.md) describes
selection, per-request inputs/results, writer joins, exact Review and recovery.
[Exact state](dynamic-state.json) records source and candidate identities.

## Implemented scope

New Linux scouts can explicitly select dynamic against an enabled retained
package. Work and Review remain the two primitives. Multiple scoped Work
components run in FirstMate workspaces; clean writer output commits return to
the root for ordinary Git joins. One fresh Review freezes the root's clean
joined commit after earlier results are gathered. The root then makes its one
repair/check pass and delivers its ordinary scout report. Scoped repair Work
uses the same primitive and is part of that pass; a second Review refuses.

The existing spawn owner verifies its parent/spawn/project lock custody and
Treehouse slot claim before positioning a newly allocated component at the
accepted commit. Existing root worktrees, including joined commits and dirty
work, survive ordinary relaunch. Request identity, results and first gather
timestamps survive parent generation changes. Aggregate lifecycle checks every
pending component and refuses root cleanup before the required Review.

FirstMate's AGENTS and fm-dod policy owners carry the narrow selected-workflow
review exception. Self-development delegation stays excluded; no-mistakes
retains sole custody once validation starts. No additional dispatcher, scheduler,
recovery daemon, workspace allocator or direct Herdr interface was added.

Legacy Work/none and Review/explicit-audit attachments keep their original
single request, commands and retained package. Dynamic capability is explicitly
declared and negotiated. New custom skills compose the retained primitives;
loading a custom skill does not create another agent by itself.

## Executed fixtures

The joined candidate passed **124 package tests and 135 integration tests**,
with ten explicit native Windows skips. Fifteen acceptance-driver checks passed.
Those 274 checks are fixture evidence for the reviewed candidate. The repaired
candidate passed **124 package and 142 integration tests**, with the same ten
Windows skips, plus **19 driver checks** (285 passed checks). They cover real Linux
Git joins and ancestry, per-result identity/gather, replay under changed generation, dirty and
unrelated writer refusal, Review order/freshness, aggregate attention and cleanup,
ordinary shell lock/Treehouse custody, default selection and opt-out, legacy
compatibility, retained custom-skill recovery guidance across generations, and
per-request native-read observation.

Scoped makers also ran their targeted checks before joining. The prepared
candidate has 565 paths including one symlink, from sixteen inventoried
FirstMate deployables. The package has 1,091 files, retaining all 1,081 paths of
Orchflows ca72258493480ddcfe73b3f01d0475ad532e4726. FirstMate stays pinned to
b182d0f908b78d08c7ccb8dce3775bdca8c5d657. All candidates and disposable homes
use the Linux filesystem; shared repository files remain the edit source.

## Independent Review and repair

One fresh independent development reviewer inspected the frozen joined candidate
and reported three issues. The single repair/check pass addressed all three:

- A writer could edit before spawn returned, causing a postlaunch clean-input
  check to mislabel successful dispatch as uncertain. The fresh workspace check
  remains before execution; writable postlaunch checks validate published identity.
- A gathered writer result held only a SHA while ordinary cleanup could delete
  its remaining refs. Result publication now creates an immutable archival Git
  output_ref before marking complete. Gather and lifecycle verify that ref.
  It retains the full commit ancestry through component/root teardown; no automatic
  pruning is implemented. The regression removes task branches/worktrees, expires
  reflogs and prunes, then gathers/joins from a replacement generation.
- The live driver checked test filenames at Review input but tested behavior only
  at final HEAD. It now executes the actual frozen reviewed files, compares them
  with each retained maker's files, and observes a successful literal final test
  command after Review gathering. A placeholder-review reproduction now fails.

No second independent development Review ran. Runtime Review components in
acceptance trials are product behavior, not additional development review
passes. Design-loop was not used. The final fixture and live results are
recorded separately from the reviewed candidate.

## Actual Linux workers

The custom fixture a-scqbpo0v passed without launching any worker or reading
authentication. The reviewed, pre-repair candidate's dynamic trial a-tjnwb0k4
passed its original assertions and ordinary cleanup. Its custom/replacement
trial a-00axqo40 preserved accepted makers, joined and reviewed successfully,
but omitted the retained custom skill's report marker and failed acceptance.
The retained custom skill was actually read before submission. Both cleaned up
with no scoped processes. Their original driver checked reviewed test filenames
and final HEAD behavior; those receipts are not relabeled as the stronger final
acceptance contract.

The first repaired dynamic trial a-fmlnfse6 completed all work, reviewed the
actual joined tree, ran the final tests after gathering Review, and retained
both writer refs through ordinary teardown. Its original receipt failed because
the native observer rejected a literal client gather piped into a JSON formatter.
The corrected parser recognizes that first command while still requiring full
native reads before invocation and the durable owner acknowledgement. A separate
corrected assessment passes; the original failed receipt is unchanged. This is
an observer correction, not a rerun or a product change.

The repaired custom/replacement trial a-izu9pzrq again failed only the retained
custom skill's required report marker. All composition, reviewed-tree, final-test,
replacement and cleanup checks passed, including both output refs after teardown.
The scoped native observer saw the initial full custom-skill read but no replacement
reread. The launch and retained-library guidance now explicitly requires rereading
and reapplying the selected skill on relaunch and checking its deliverable and
validation requirements before root completion. This generic guidance repair is
part of the same repair/check pass; it adds no custom execution adapter. Trial a-ij7uubxj observed the required custom report marker but missed the
running-maker restart window, relaunched during Review under the older driver's
broader predicate, and received a further manual relaunch after an earlier
stalled observation. It failed the final-test receipt check. All results were
gathered, ordinary cleanup passed and both refs survived; this remains diagnostic
evidence, not a clean acceptance pass.

Trial a-ng35vxgl used explicit short polls, but the root guessed a report path
from component scratch provenance and hit a Claude outside-directory Read prompt.
The unneeded Read was cancelled through FirstMate and a retained-path correction
sent through its normal inbox; permissions were not broadened. That intervention
also excludes it from clean acceptance. It finished with a failed full-read-order
check; ordinary cleanup passed with both writer refs retained and no scoped
processes. The existing dynamic launch guidance now
requires reading the exact report_path/result_path returned by status, and owner
reconciliation if those retained paths are unavailable. The final driver also
requires an actually running Work at relaunch; a later Review cannot certify that
window.

The final candidate's trial **a-x6osytu8 passed all seventeen acceptance checks
without manual intervention** in 617.922 seconds. One Work was gathered while
the other Work was still running; ordinary fm-control relaunch retained both
request/child identities. The native observer confirmed complete retained custom
skill reads in the original and replacement root sessions, complete result reads
before each gather, and identical-request replay identities. The exact reviewed
files matched maker outputs and passed behavior/tests. The root then executed
its final tests after Review gathering and included the required retained custom
marker in its report. Ordinary teardown passed; both archival writer refs still
resolved and no scoped processes remained.

This final run uses candidate baa0b518142f215d0b7e3c6a7e7fa7dcffd31512771db4d4f431e1c0647b28e3
and package 50462e272be1537f741e59dab20d45aa98b6cab16c1caf50688aaff5ffcc52aa.
The exact state records the driver identity and immutable original receipt hash.
All earlier failed and assisted receipts remain separate.

## Remaining scope

This is a local Linux scout profile, with a 32-component admission bound, inherited
worker controls and a clean no-origin input repository. Ordinary scout delivery
retains a report; it is not ship/local-only code delivery. Ship delivery, nested
composition, Build/SelfImprove, component relaunch, general artifact/history
retention, representative optional libraries and full release parity remain open.

Current actual Codex composition, native background-tool retirement, a complete
supervisor wake/drain/rearm cycle, remote homes, promotion, bundle pruning and
general rollback remain unverified. Native Windows is deferred. Active user
installations and authentication caches are not modified. Historical dev.4/dev.5
receipts and the original dated assessment remain unchanged.
