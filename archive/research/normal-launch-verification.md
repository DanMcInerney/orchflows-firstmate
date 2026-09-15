# Normal launch increment verification

The dev.5 continuation implements a bounded normal-entrypoint integration:
enable a project once, then use the retained Work/Review skill or a selected
custom skill through ordinary FirstMate scout launch and recovery.
[Usage](normal-launch.md) and the [owner mapping](firstmate-owner-mapping.md)
describe the implementation and its ownership boundaries.

## Implemented and preserved

FirstMate's existing spawn transaction applies the project's immutable package
default and renders the retained core/custom library catalog. Its metadata
publication supplies immutable per-generation client context. The package
client uses that context without assembling controller/home/root/generation
flags; it still negotiates the actual controller and validates the exact
attachment before mutation.

Complete selected libraries survive changes to their source. Existing task
attachments, accepted requests and results survive default updates, disablement
and root relaunch. Existing task-group admission, worktree allocation, inbox
delivery, supervision, recovery and root completion owners remain in use.

The package is 0.1.0-dev.5, retaining all 1,081 upstream paths from
ca72258493480ddcfe73b3f01d0475ad532e4726 in 1,090 files. FirstMate remains pinned
to b182d0f908b78d08c7ccb8dce3775bdca8c5d657. Fifteen inventoried deployables
reproduce a 565-path candidate with one symlink through prepare.py.
[Exact state](normal-launch-state.json) records all aggregate identities.

## Executed Linux checks

The unchanged dev.4 baseline first passed 99 package and 90 integration tests.
The client maker passed 42 focused tests, and the enablement maker passed 17.
The joined candidate passed 111 package and 108 integration tests. After the
independent-review repair, 111 package and 112 integration tests passed.
Fourteen targeted acceptance-driver checks also passed: **237 passed checks**
on the final increment, plus ten explicitly deferred native Windows skips.

The checks cover project enablement and refusal, retained package/library
integrity, new-default versus existing-task behavior, generation fencing,
actual shell quoting/environment filtering, Review authorization, normal
request/result lifecycle regression and the exact dev.4 compatibility client.
They are fixtures; actual workers are recorded separately below.

## One independent review and one repair pass

Development used the pinned upstream Orchflows dynamic workflow: fresh scoped
makers, joined checks, one fresh independent reviewer, then one repair/check
pass. The reviewer made no edits or delegated repairs. No second review ran,
and design-loop was not used.

The reviewer found one high-impact compatibility issue: the new owner gave
context-only commands to retained dev.4 clients that still require explicit
authority arguments. The repair adds declarative client capability metadata.
New enablement requires context support; existing attachments without it keep
their original explicit launch commands and do not receive a root context.
Unknown capability metadata refuses explicitly.

A hash-checked copy of the exact dev.4 client exercises status and gather
against the repaired controller after the parent's generation changes. It
gathers the same accepted child under the replacement generation. The fixture
is test-only and is not deployed into FirstMate candidates.

## Actual Linux trials

The first custom no-live fixture, a-f5377zgh, failed before any worker launch:
the driver had not created its library directory. Its failed receipt remains
unchanged. The driver was corrected and a-p95qhpu_ passed fixture preparation,
including no task attachment before ordinary spawn. Both cleaned up with no
scoped processes.

The reviewed, pre-compatibility-repair candidate passed enabled custom Work
with ordinary FirstMate root replacement (a-d2go0e7s). This is separate evidence
from the final repaired candidate.

| Final repaired trial | Case | Observed outcome |
| --- | --- | --- |
| a-0fxacane | Enabled custom Work, 60-second foreground component delay, ordinary root replacement | Spawn created the attachment; the worker read the retained custom skill after its source changed, reused the same child across relaunch, used context-only calls, fully read report/result before gather and delivered the custom marker in its ordinary scout report |
| a-zid8sve5 | Project enabled as Review/explicit-audit, no artificial delay | One fresh read-only reviewer audited the frozen clean input; the root used context-only calls, replayed the same child, fully read report/result before gather and delivered its ordinary audit report |

Both final trials passed every required assertion, ordinary task/lab cleanup
and scoped process checks. No private credential files or scoped processes
remained. Authentication used only an access token from the selected current
cache; no credential/refresh cache was copied or reset.

The native tuple was Ubuntu/WSL Python 3.12.3, Claude Code 2.1.269, Herdr 0.7.4
and Treehouse 2.0.1. The tested commands used the ordinary FirstMate owners.
The acceptance driver did not supply a new worker execution or recovery route.

These short trials required zero steady-watcher duration. Intentional
replacement does not assert uninterrupted watcher health; a normal watcher
exit after a retained result is not a pending-component failure. They do not
replace the earlier long-watcher evidence or establish a complete supervisor
wake/drain/rearm cycle. Exact thresholds, outcomes, read-order facts, source
identities and original receipt hashes are in the state file; sanitized raw
evidence is under ignored .scratch/normal-launch-increment.

## Remaining scope

A selected custom skill can compose the one admitted read-only Work or Review.
The project default still selects that primitive for new matching scouts.
Full dynamic Work-to-Review composition, multiple components, writer joins,
nested work, Build/SelfImprove and broader custom/meta/optional-example parity
remain gated. Natural per-task workflow policy selection must be reconciled
at FirstMate's existing intake/role/delivery policy owners.

Current actual Codex normal-launch/Review/watcher acceptance, native background
tool retirement, complete supervisor wake/drain/rearm, remote homes, promotion,
bundle pruning and general rollback remain open. Native Windows is deferred.
Active installations, pinned references, the original dated assessment and
historical dev.4 receipts were preserved.
