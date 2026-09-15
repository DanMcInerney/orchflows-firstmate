# Plug-and-play workflow integration

This dev.9 implementation follows the [source reassessment](plug-and-play-reassessment.md).
FirstMate remains pinned to `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`;
Orchflows source remains `ca72258493480ddcfe73b3f01d0475ad532e4726`.
The package retains the upstream source and optional-library migration inventory.
Implementation, fixture checks and actual workers are separate evidence.

## Assignment controls

Dynamic Work/Review requests can carry optional `model` and `effort` choices.
Each field resolves independently, in this order:

1. The caller's named-assignment choice (`model` or `effort`).
2. The caller's operation default (`operation_defaults`).
3. The saved workflow's preference for `assignment_name` (default: request ID).
4. The saved workflow's operation preference (`Work` or `Review`).
5. FirstMate's applicable configured defaults.

FirstMate selects the harness. The adapter never guesses a provider from a model
name. Accepted controls and their provenance join request identity and survive
replay. Existing FirstMate profile validation must honor explicit settings or
refuse before admission; metadata alone cannot establish an effective flag.
Legacy clients retain their negotiated contract.

## Save and select a workflow

FirstMate's editable home defaults to `$FM_HOME/data/.orchflows-home`, outside
ordinary task brief directories. Explicit configuration can select a dedicated
home. Package setup preserves user libraries and maintains existing catalogs;
normal Orchflows homes remain protected. No new library format or database is
introduced.

Author a complete library in the assigned worktree, trial it and deliver its
committed result through ordinary FirstMate owners. The FirstMate publication
operation copies the selected committed library into the configured home,
refreshes its catalog and updates applicable project bundles. Worker write
permissions do not authorize arbitrary home writes.

Ordinary brief intake selects `--orchflows-skill library:skill`. The launch owner
resolves that selection with its complete dependency libraries and retains the
selected instructions, explicit preferences and composition scope. Editing or
republishing the home changes future tasks. Running tasks and replacements keep
their original snapshot.

### Owner commands

~~~sh
python3 -B "$FIRSTMATE_CODE/bin/fm-orchflows-home.py" --home "$FM_HOME" setup --package "$FORK_SOURCE"
python3 -B "$FIRSTMATE_CODE/bin/fm-orchflows-home.py" --home "$FM_HOME" catalog
python3 -B "$FIRSTMATE_CODE/bin/fm-orchflows-home.py" --home "$FM_HOME" publish \
  --project "$PROJECT" --library release-library --commit "$DELIVERED_COMMIT"
"$FIRSTMATE_CODE/bin/fm-brief.sh" "$TASK" "$PROJECT_NAME" \
  --mode local-only --orchflows-skill release:ship
~~~

Fill Captain's intent and Firstmate spec normally, then use ordinary FirstMate
spawn with the selected mode and worker profile. The selected skill supplies
workflow attachment through that owner path.

## Composition scope

Loading a workflow's instructions continues in the caller context. Only Work
or Review launches a FirstMate component. A selected workflow can authorize
multiple required dynamic invocations; each has its own call identifier and permits one
independent Review followed by one repair/check pass. Review is read-only and
requires prior results in that invocation to be gathered.

A root-owned writable Work trial can request one level of descendants only for the call scopes explicitly assigned to it. Review and read-only Work cannot delegate. Calls run in their declared order for each caller; every selected call must complete its Review before root delivery. Descendants share the existing root group bound of
32 total components. Records preserve the actual parent, retained group and
result-consumption relationship. The existing lifecycle and delivery owners
wait for required descendant results and reviews. Workflow instructions confer
no general supervisor authority.

FirstMate's no-mistakes pipeline keeps sole validation custody; this increment
retains its refusal for incompatible workflow delivery selections. FirstMate
self-development and native Windows remain separate compatibility cases.

## Ordinary repository compatibility

The adapter now admits an `origin` remote. The pinned local merge owner already
selects its default branch using `origin/HEAD` and performs a local fast-forward.
The targeted regression exercises Work, Review, result gathering and that actual
merge owner with a disposable bare origin, asserting that the remote is unchanged.
A subsequent root starts from its retained local input even when local delivery
has advanced beyond `origin/main`: the existing launch-position owner places the
new clean detached worktree after ordinary remote freshening. It requires the
current spawn/project locks and owned Treehouse slot. Existing roots retain their
joined and dirty work on relaunch. Clean input, exact worktree identity, ancestry,
tracked-symlink/submodule limits and FirstMate delivery authority still apply. This is one repository shape,
not a general drop-in compatibility claim.

## Verification

Joined Linux checks, the one independent development Review and actual worker
outcomes are recorded in [verification](plug-and-play-verification.md). Prior
strict and qualified leaf-authoring receipts remain unchanged. This increment
does not certify every optional library, current Codex composition, portability,
remote homes, direct-PR/no-mistakes delivery, installation/update/rollback or
full feature parity.
