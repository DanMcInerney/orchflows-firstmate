# Dynamic composition with ordinary local-only delivery

The dev.7 increment extends the [dynamic scout contract](dynamic-composition.md)
to an explicitly selected Linux Herdr ship task with local-only delivery.
Work and Review still run through FirstMate's existing component, workspace,
inbox and recovery owners. The root joins the committed results, reviews the
exact clean joined candidate once, makes one repair/check pass, and delivers
its ordinary ready branch. [Verification](local-delivery-verification.md)
distinguishes fixtures, independent development Review and actual workers.

## Select the task

Enable the complete retained package and any selected custom libraries through
the existing project configuration owner. Prepare the ordinary local-only brief,
with the intended workflow in the Firstmate spec, then explicitly select dynamic
at spawn:

~~~sh
python3 -B "$FIRSTMATE_CODE/bin/fm-task-group.py" --home "$FM_HOME" enable \
  --package "$FORK_SOURCE" --project "$PROJECT" --workflow dynamic

"$FIRSTMATE_CODE/bin/fm-brief.sh" "$TASK" "$PROJECT_NAME" --mode local-only
# Fill Captain's intent and Firstmate spec in the ordinary source brief.
"$FIRSTMATE_CODE/bin/fm-spawn.sh" "$TASK" "$PROJECT" \
  --mode local-only --yolo off --backend herdr --harness claude \
  --orchflows-workflow dynamic
~~~

The project retains the clean local Git/no-origin restrictions. Supply the
ordinary Herdr session and project registration appropriate to the owning home.
Claude and Codex remain FirstMate harness choices; current actual acceptance is
identified separately. New ship tasks with default selection keep their ordinary
route, including in a dynamically enabled project. Explicit dynamic selection
with direct-PR, no-mistakes, secondmate or another unsupported profile refuses
before allocation. Promotion and FirstMate self-development remain excluded.

## Retained contract and recovery

The ship attachment adds root_delivery with kind ship, mode local-only and the
exact branch fm/<task>. Its metadata records task_group_delivery=ship-local-only.
The package capability and controller protocol explicitly advertise
root_deliveries [ship-local-only]; the returned scope is
local-dynamic-ship-local-only. Legacy clients and scout attachments retain their
previous invocation and delivery contract.

Ordinary relaunch keeps the attachment, worktree, accepted requests, gathered
results and joined or unfinished work. Each generation receives its own immutable
launch context. Changing a default cannot change an existing task's delivery.
The ordinary ship brief starts a fresh root detached at its clean admitted input
and instructs the worker to create fm/<task> first. Launch permits that precise
initial state. Client dispatch and subsequent relaunch require the promised
branch. A changed root kind, delivery mode or branch requires reconciliation
rather than silently authorizing another delivery path.

The same request-specific input commits, retained report/result paths, writer
output refs, one fresh Review and one repair/check phase apply. Components remain
scouts with return-to-parent disposition. A component's completion is never a
ship-ready signal. Loading a custom skill still composes the same primitives.

## Ready branch, landing and cleanup

Only the root follows the existing fm-dod local-only contract: the final output
is committed on fm/<task>, with a clean branch ready to fast-forward onto the
local default branch. The root emits done: ready in branch fm/<task> and stops.
It does not push, open a PR or merge. Scout scratch output and a diagnostic report
do not substitute for the ready branch.

The configured merge authority remains FirstMate's. Its existing fm-merge-local.sh
entrypoint checks the attached composition before the ordinary guarded landing.
Ungathered or uncertain components, missing required Review, a changed delivery
binding or invalid candidate cannot bypass that gate. No parallel merger or
delivery service is introduced. Ordinary teardown checks that the immutable
fm/<task> ref landed in local default independently of the worktree's current
branch, and validates the attached repository. It retains that delivery ref
through detach, slot return and task-record cleanup, then retires it only after
successful metadata removal. Interrupted cleanup uses existing exact-generation
backlog-close evidence and Treehouse slot ownership; no new journal is added.

No-mistakes is not an admitted delivery mode for this profile. Its existing
validation owner retains sole custody. This increment enforces its selected-task
boundary by refusing no-mistakes admission and rejecting delivery-mode changes;
it adds no pipeline run parser or state owner.

## Remaining scope

Direct-PR/no-mistakes integration, promotion, nested components, Build/SelfImprove,
general artifact/history retention, component continuation, broader custom/meta
workflows, current Codex runtime acceptance and installation/update/rollback
remain separate work. This is one delivery extension to the bounded local
profile, not a full feature-parity or live-release claim.
