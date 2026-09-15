# Review increment verification

This increment uses the upstream Orchflows dynamic workflow as its development
process. Three independent makers own the Review client, FirstMate Review
admission/lifecycle, and Linux acceptance driver. The joined implementation
receives one fresh independent final Review and one repair pass without a
second review. Design-loop is not used.

The package is dev.4, adapting Orchflows
ca72258493480ddcfe73b3f01d0475ad532e4726. FirstMate remains pinned to
b182d0f908b78d08c7ccb8dce3775bdca8c5d657. The owned distribution adds one
primitive identity helper; all deployables are inventoried and prepared through
its existing preparation tool.

## Implemented boundary

[Review contract](review-contract.md) defines one read-only independent audit
of a clean frozen commit, admitted explicitly as Review/explicit-audit on Linux.
The fresh component receives Review guidance, cannot repair or dispatch, and
returns through FirstMate. The root alone delivers. Work/none and its old
record shapes remain compatible. Protocol version 1 advertises the additional
capability; the client must explicitly select Review and verify its attachment
before mutation. This is not multiple-component dynamic composition.

## Executed checks

The client maker ran 30 focused Linux tests, including 15 new Review cases.
The owner maker ran 40 focused Linux tests, including 16 new Review cases.
These controller/client fixtures do not establish live fleet readiness.
The joined Ubuntu/ext4 run passed all 99 package tests in 14.194 seconds and
88 integration tests in 45.404 seconds, with ten explicit native Windows skips
and no unexpected skips. Preparation reproduced the 564-path FirstMate
candidate (one symlink) from thirteen inventoried deployables. All 1,081
upstream paths are retained in the 1,088-file package. [Exact state](review-state.json)
records the aggregate hashes; raw checks are retained under ignored
.scratch/review-increment/check-e5r8a5r4. Actual Linux acceptance remains
separate from these fixture results.

## Independent review

One fresh independent reviewer found two material issues. The default Linux
acceptance namespace exceeded Unix socket pathname capacity, preventing Herdr
lab provision; failed operation diagnostics were also discarded. Repeated
gather overwrote its acknowledgement timestamp, allowing an early nonliteral
gather followed by reads and a later literal gather to fool the read observer.

The single repair pass shortens private paths, checks the selected session's
socket byte lengths before starting endpoints, retains scrubbed failed/timed-out
operation output, and preserves the first owner acknowledgement across gather
retries while updating the current parent generation. Regressions cover actual
Linux socket binding, early hidden gather, repeated acknowledgement under a new
generation for both Work and Review, and secret-free failure/timeout logs.
Repair checks passed all 99 package tests in 12.495 seconds and 90 integration
tests in 34.937 seconds, with ten native Windows skips. The live checks exposed
one more observer defect: it expected current: waiting while the actual owner
prints state: waiting. The same repair/check pass corrected that parser and
requires positive child activity. All thirteen driver checks passed in 0.521
seconds. No second independent review was run.


## Actual Linux attempts

The first Review attempt, acceptance-6uxr4n5v, failed during private named Herdr
lab provision before any root/component worker launched. A read-only native
status probe reproduced the Unix socket pathname-capacity error. Ordinary lab
and private sentinel teardown both returned zero, leaving no scoped processes.
Its failed receipt remains under ignored scratch evidence; it is not Review
runtime evidence.

The retry, acceptance-us29ugpk, used the reviewed product candidate and a
shorter explicit work root. It completed one real Claude Review, two successful
same-child submissions, complete native report/result reads before its single
gather, correct retained/root reports and ordinary scout delivery. All task
exit/teardown, lab and sentinel operations returned zero and left no scoped
processes. Its original receipt says failed solely because the observer
expected the wrong waiting label. That receipt is retained unchanged.

Reassessment of the retained samples with the repaired parser passed: 23
positive root-waiting/child-working samples spanned 395.338 seconds, with the
same live watcher and current beacon. Independently, the filtered actual
watcher trace contains 20 waiting classifications spanning 382.435 seconds.
The watcher stayed alive while the component was pending. This is a corrected
assessment of recorded observations, not a worker rerun.

The final repaired FirstMate candidate separately passed two real Claude cases:

| Trial | Requested case | Observed outcome |
| --- | --- | --- |
| a-7ysafo1o | Work with 60-second foreground child delay and FirstMate-owned parent replacement | Replacement returned zero while the child was pending; the new root retained the same child, read both files fully before gather, acknowledged under its new generation, handled the result notice and delivered the ordinary report. Component phase: 351.433 seconds |
| a-w469d47l | Explicit Review with no artificial delay | One fresh reviewer, identical-request replay, correct source findings, complete native reads before gather and ordinary root audit delivery. Component phase: 181.382 seconds |

Both final cases passed retained integrity, clean input/worktrees and all
ordinary cleanup operations, with no scoped processes remaining and no private
credential files. Their required steady waiting span was zero: the short Review
does not repeat the long watcher case, and the intentional replacement case
does not assert uninterrupted watcher health. Original receipts retain the
driver version that executed them; the later parser repair changes observation
assessment only, and future receipts explicitly include the requested threshold.

The runtime was native Ubuntu/WSL Python 3.12.3, Claude Code 2.1.269, Herdr 0.7.4
and Treehouse 2.0.1. Selected native process observations confirmed that the
long Review root/component and the Work replacement root/component received the
FirstMate-supplied foreground profile. The driver did not supply those flags.
Access-token-only process authentication was used; no credential/refresh cache
was copied or changed. Native transcript observers retained scoped event facts,
not transcript bodies, in the evidence directory.

[Exact state](review-state.json) distinguishes the reviewed candidate
d2769e99ee88c708b6efd7c8428b54fb8e817e0ed086b07d9256e6eb5def2d7a from the final
candidate 6c7e15b1991cb7c733b50ecc565147426f8d1134f4a8c443dcff639540503592.
The 1,088-file dev.4 package remained unchanged between them. Raw sanitized
evidence is retained under ignored .scratch/review-increment.

## Remaining scope

Dynamic workflow was used to develop this increment. The fork's multi-component
dynamic runtime, writer joins, review of dirty writer output, workflow repair
passes, nesting and optional-library execution remain gated. Actual Codex
Review/watcher acceptance, native background-tool activity/retirement and the
complete supervisor wake/drain/rearm lifecycle remain open. Native Windows is
deferred. Active installations and pinned research references were unchanged;
the original dated assessment and earlier trial identities are preserved.
