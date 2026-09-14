# Leaf authoring verification

This increment starts from merged PR #4, main commit d3cf51b. Source pins remain
FirstMate b182d0f908b78d08c7ccb8dce3775bdca8c5d657 and Orchflows
ca72258493480ddcfe73b3f01d0475ad532e4726. Current package identity is dev.8.

## Joined checks

The initial joined candidate passed 128 package and 155 Linux integration tests,
with ten explicit native Windows skips. Together with 26 driver checks, that
was 309 passed checks. The non-live authoring fixture a-27duy0cj passed preparation
and cleanup without reading authentication or launching a worker.

The owner regression exercises a newly authored library at the frozen component
input, retained dependencies, existing permission boundaries and retained output.
Driver regressions reject incomplete/failed/foreign-worker reads, untrialed
library changes, fabricated output and substituted validation.

## First actual trial: diagnostic, failed

Sonnet 5/high trial a-s450kuf1 authored a complete nine-file release-triage
library. A fresh read-only Work applied it to the declared input and returned
the correct JSON. Ordinary parent replacement occurred during that trial,
preserving the gathered author and accepted trial identities. The parent read
the complete leaf and dependencies again, gathered the trial, committed its
actual output and provenance, and obtained one Review of the exact joined tree.

The reviewer confused two different objects: request.result_digest hashes
canonical JSON of the complete retained result.json, while result.report_digest
hashes raw report bytes. The original trial record held the correct result
digest. The parent accepted the incorrect finding and substituted the report
digest during repair. Independent canonical recomputation confirms the mistake.

The original receipt failed committed provenance and four configured native-call
assertions. Formatted submit output hid the full returned identities, one
submission was interrupted by replacement without the required later replay,
Review gathering used redirected/compound shell syntax, and the final test
command appended cat. Full native reads before the durable first owner
acknowledgement were independently observed for all three results; that does
not turn the stricter original receipt into a pass.

Landing was skipped. The existing delivery guard preserved the unlanded branch
and root records. Components, the private lab and sentinel were retired; root
cleanup and delivered-code checks remain failed as expected for unlanded output.

A factual correction sent through the ordinary FirstMate inbox arrived after
the agent exited and was retained for recovery. Restoring the same private lab
through existing owners and attempting ordinary fm-control relaunch was refused:
the recorded endpoint had been removed by cleanup. The administrative attempt
launched no worker. Its separate receipt and the original failed receipt are
preserved unchanged; no endpoint binding or worktree was fabricated to bypass
that owner refusal.

## Clarification and new verification

The shared client contract now distinguishes the result and report digests.
The bounded authoring skill references it. Delivered trial evidence retains the
complete result JSON as well as exact output bytes so the two digests can be
verified independently after cleanup. A new regression reproduces the mistaken
substitution and requires failure. All 27 driver checks pass.

The targeted brief explicitly preserves full submit/gather responses, replays
accepted requests after replacement and keeps the final test command separate
from output inspection. The acceptance conditions were not relaxed. Native
read observation can reconstruct an already retired trial's expected bytes from
its exact retained Git input, with historical component metadata from its
immutable retained result; it does not recreate fleet records.

The refined joined candidate passed 128 package, 155 Linux integration and
27 driver checks (310 passed; ten native Windows skips). Fixture a-_g7f22l1
passed preparation and cleanup without authentication or model execution.

## Refined actual trial: useful evidence, strict acceptance failed

Trial a-mh9osxed used the same Sonnet 5/high profile. It authored and joined
the complete library, replaced the root while the fresh leaf trial ran,
preserved accepted/gathered identities, committed actual output and correctly
distinguished both digests, and obtained one Review of commit
c2d90821a55b747114add069505ceb9f06b46fc8.

That Review found duplicated classification rules between the leaf prose and
domain guidance, plus a trial-record sentence claiming the bare JSON report
itself demonstrated dependency reads. The root repaired those points in
45f79ddb27f272064742e30b4b5319135dcc859e. Because the leaf changed, it used
the existing repair phase to run a fresh read-only Work, repair-trial-v1.
That trial's exact input is the final commit and its JSON output is correct.
There was no second Review and no operator intervention in the live run.

The original receipt remains **failed**. This fixture deliberately expects one
unchanged library and three requests; the valid fourth repair Work therefore
fails its count and final-library assertions. Several shell calls also used
variables, formatting pipelines or compound commands that did not meet the
fixture's explicit literal-call/replay/final-check requirements. All four
results had full native report/result reads before durable owner acknowledgement,
but that does not satisfy the stricter configured first-call observations.

Landing was skipped. Ordinary cleanup retired all four components, the private
lab and sentinel, and left zero scoped processes. The existing guard retained
the root records and unlanded ready branch. Full cleanup and delivered-code
checks therefore remain failed. The final library and its original committed
trial evidence, Git objects, retained results and diagnostic are preserved in
ignored evidence storage. There is no dev.8 local-delivery acceptance pass.

## One independent development Review and repair/check pass

A fresh reviewer inspected frozen source commit
8565660b52022e836a3d9abce3c2b62a23ef7548, the package/catalog/owner changes,
the actual library and trial output. It independently passed all 27 driver
checks and the new owner regression. It found two P2 acceptance-observer gaps:

1. The reviewed snapshot could contain self-consistent but misattributed
   provenance while strict retained-identity checks applied only after repair.
   One shared verifier now compares actual retained output/result bytes and
   identities against both the reviewed and final snapshots.
2. Declared retained core guidance was absent from automated read checks.
   The observer now requires exact immutable core paths and full successful
   native content. The child's actual full Bash cat of core writing guidance
   is valid evidence, as independently verified; narrow shell-read recognition
   supports it without accepting staging copies, partial output or pipelines.

The same repair/check pass binds pre-Review root library reads to the frozen
trial input, since later prose repairs must not change the expected earlier
read bytes. Regressions cover provenance fabricated before Review and corrected
only afterward, internally consistent substituted reports/results, exact core
paths and failed/partial shell reads. **All 30 driver checks pass.** No second
development Review ran.

A separate read-only reassessment of the unchanged refined trace confirms
reviewed and final original-trial provenance, full declared dependency reads,
all four actual result digests and worker profiles, and a correct repair trial
on the exact final commit. It does not change the original receipt or turn the
broader sequence into the narrow fixture's pass, and launches no additional
model or landing operation.

The repair trial's output and identities live in retained FirstMate results and
the tasktmp diagnostic; the delivered repository files still describe the
original trial. The final package clarification explicitly requires committing
additional repair-trial output, retained result and provenance before readiness,
while keeping the original Review evidence. That clarification has package
checks but has not had another actual worker trial.

The final package clarification passed 128 package and 155 Linux integration
checks, with ten explicit native Windows skips. Together with the 30 driver
checks, **313 checks passed**. The exact final package differs from the live
trial's package; both identities are retained in [exact state](leaf-authoring-state.json).
Source pins and migration inventory remain unchanged. Earlier dev.7 evidence stays separately identified in
[local delivery verification](local-delivery-verification.md).

## Remaining work

Close this bounded authoring delivery case before claiming runtime readiness:
retain post-Review trial evidence with the final artifact and account precisely
for the observed repair Work when assessing the selected sequence. Literal-call
trace requirements and ordinary recovery after partial cleanup also remain
open. Do not replace the current owners or expand this into an exhaustive
harness program. General composing Build, nesting, SelfImprove,
unrelated-project portability, current Codex acceptance and native Windows are
not established by these trials.
