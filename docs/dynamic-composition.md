# Dynamic composition through FirstMate owners

The dev.6 increment extends the existing normal-launch seam to a bounded Linux
scout composition. Work and Review remain the two primitives. The root can
request multiple useful Work results, join committed writer output in its own
FirstMate worktree, request one fresh independent Review of the exact clean
candidate, then make one repair/check pass without another Review. A selected
custom skill can compose that same route; it needs no workflow-specific adapter.

This is a local scout profile. Ship delivery, promotion, nesting, component
relaunch, Build/SelfImprove and broader optional-library parity remain outside
this increment. FirstMate continues to own endpoint allocation, worktrees,
current metadata, inbox delivery, supervision, recovery and outer completion.
There is no new scheduler, recovery service, native-child route or direct Herdr
adapter. Actual results belong in [verification](dynamic-verification.md).

## Enable and select

Enable the retained fork and optional complete custom libraries for a clean,
no-origin local project in a disposable FirstMate Linux home:

~~~sh
python3 -B "$FIRSTMATE_CODE/bin/fm-task-group.py" --home "$FM_HOME" enable \
  --package "$FORK_SOURCE" --project "$PROJECT" --workflow dynamic \
  --review-policy workflow-review --library "$CUSTOM_LIBRARY"
~~~

Omit --library when none is selected. Explicit dynamic selection supplies its
workflow-review policy when the policy option is omitted. Conflicting audit
selection refuses. Capability metadata must declare dynamic support; a retained
older client is never silently given a new invocation contract.

Use ordinary FirstMate brief/intake and spawn. New scouts can choose
--orchflows-workflow dynamic, retain the enabled default with default, or decline
an attachment with none. Dynamic selection requires an enabled complete package.
Existing attachments remain authoritative; relaunch does not replace their
selection. --relaunch rejects an explicit workflow override. The selected
custom workflow belongs in the ordinary Firstmate spec and retained catalog.

This policy is implemented at FirstMate's existing AGENTS/fm-dod owners, scoped
to this attached Linux scout. It does not authorize self-development delegation,
ship delivery or a second review gate. Once no-mistakes validation starts,
no-mistakes retains sole custody of review, fixes, checks and delivery.

## Requests, joins and Review

The launch-bound context is still immutable per generation. Use the retained
package client with no controller/home/root/generation flags:

~~~sh
python3 -B "$RETAINED_PACKAGE/scripts/firstmate.py" submit --request "$REQUEST_JSON"
python3 -B "$RETAINED_PACKAGE/scripts/firstmate.py" status
python3 -B "$RETAINED_PACKAGE/scripts/firstmate.py" status --request-id maker-a
python3 -B "$RETAINED_PACKAGE/scripts/firstmate.py" gather --request-id maker-a
~~~

Dynamic request JSON has exactly these fields:

~~~json
{"request_id":"maker-a","assignment":"Make and check the assigned change in your isolated worktree; commit and return evidence.","primitive":"Work","writable":true}
~~~

A read-only Work uses writable false. Review also requires writable false. The
attachment records workflow dynamic, Work/workflow-review, readonly false and a
32-component admission bound. The bound includes the one reviewer and any
repair Work; it is not a concurrency scheduler or a claimed upstream limit.
The root chooses ready assignments and supplies complete guidance and context.

FirstMate captures each request's input_commit from the root's clean current
worktree, verifies its ancestry from the admitted project input, and records the
request before dispatch. The existing spawn owner creates each component's
worktree, then positions that fresh workspace at the accepted commit. Existing
workspaces and the original project checkout are not candidate staging areas.

A writer completes with a clean committed descendant of its input. FirstMate
retains output_commit with the report and input/package/request identities.
Writer results also retain an immutable output_ref in the shared Git database.
FirstMate publishes that ref before the result, and validates it before gather
or cleanup. It preserves the full output ancestry through component/root
teardown. These archival refs are not pruned automatically; a future explicit
result-pruning owner must manage refs and retained records together. A missing
or changed ref requires owner reconciliation.

The root reads the complete report and result at the exact report_path and
result_path returned by status --request-id before gathering, then inspects and
joins the output with ordinary Git in its assigned worktree. Component tasktmp
and worktree metadata are provenance, not parent report locations; do not guess
scratch paths or broaden read permissions. Missing retained paths require
reconciliation through the existing owner. For a linear
maker result, cherry-pick input_commit..output_commit. On recovery, inspect Git
history and the actual files before repeating an already completed join.
FirstMate's normal worktree owner provides isolation; no second writer or join
service was introduced.

Review is admitted only after all preceding results have been gathered. It
captures the root's clean joined HEAD, launches a fresh read-only component and
retains the exact reviewed commit and reviewer metadata. An accepted Review
reserves the only reviewer even if its launch is uncertain. A second Review
refuses. After its result is gathered, the root performs the one repair/check
phase, directly or using scoped Work, and reports reviewed and final commits
separately. Review never makes or delegates repairs.

## Durable results and lifecycle

Legacy one-component attachments keep task-group/request.json and their two-field
request body. Dynamic groups store requests by ID under task-group/requests.
An exact retry returns the original child and disposition. A changed body cannot
reuse that ID. An uncertain launch never grants permission for a replacement.

Dynamic status without an ID returns all request views. Gather requires an ID;
it acknowledges that result alone, preserving the first acknowledgement time.
Per-result inbox notifications use FirstMate's existing durable inbox owner.
The group lifecycle projection checks every ungathered component, giving
attention precedence over a healthy sibling. Root cleanup also requires the
workflow's Review to have been gathered. Component completion never becomes
root completion.

Ordinary fm-control.sh relaunch supplies a new immutable generation context.
The replacement root retains accepted requests, gathered evidence and its
existing joined or unfinished working tree. It reconciles from those records
and Git, without replacing children. Old generation calls remain fenced.
Component relaunch, generalized cancellation and the full supervisor
wake/drain/rearm cycle remain separate work.

The implementation preserves historical dev.4/dev.5 receipts. Package and
fixture checks establish their tested interfaces; a named live trial is needed
to establish actual worker behavior.

## Selected skill recovery

On initial launch and relaunch, the existing root launch/catalog guidance requires
reading the selected retained custom skill and its dependency guidance before
continuing. Reapply its deliverable and validation requirements to accepted
results and remaining work. Before ordinary completion, reread the skill and
check its required report content, artifacts and checks against the delivered
result. Retained catalog availability alone did not preserve these obligations
in two actual replacement trials; this guidance addresses that observed gap.
