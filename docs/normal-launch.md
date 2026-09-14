# Project enablement through ordinary FirstMate launch

The dev.7 [local-only root extension](local-delivery.md) builds on this contract.
[Current verification](local-delivery-verification.md) records its scope and
executed evidence; earlier increment restrictions below are historical context.

The dev.6 continuation extends this seam to bounded Linux dynamic composition;
see [dynamic contract](dynamic-composition.md) and [current verification](dynamic-verification.md).
Earlier one-component restrictions below describe the dev.5 baseline.

The dev.5 integration removes manual per-task attachment for the current
read-only profile. Enable the fork once for a local project, then create briefs
and launch scouts through FirstMate's ordinary entrypoints. This is a concrete
step toward the clarified plug-and-play target, not full workflow parity.

## Enable and invoke

Use the FirstMate candidate produced by integrations/firstmate/prepare.py and
a disposable Linux home with its ordinary data, state, config and projects
directories. The project must satisfy the existing clean, no-origin Git input
contract. Select optional custom library roots in guidance order:

~~~sh
python3 -B "$FIRSTMATE_CODE/bin/fm-task-group.py" --home "$FM_HOME" enable \
  --package "$FORK_SOURCE" --project "$PROJECT" \
  --library "$CUSTOM_LIBRARY"
~~~

Omit --library when no custom library is needed. Work is the default. For an
explicit audit profile, select both --primitive Review and
--review-policy explicit-audit when enabling. This selects one primitive for
future scouts of that project; it does not infer Review permission from a
workflow's prose.

The normal FirstMate supervisor continues to own task intake, brief preparation,
dispatch controls and fm-spawn.sh. It can put the desired primitive or a selected
library skill name in the ordinary Firstmate spec. No attach command, package
path, controller path or generation value needs to be inserted per task.

New enablement requires the fork's scripts/firstmate-client.json capability
declaration. Existing attachments without that declaration keep their original
explicit client commands; their accepted requests remain recoverable after an
owner upgrade.

The launch owner supplies the retained core skill, selected library catalog and
ORCHFLOWS_FIRSTMATE_CONTEXT. The root invokes its retained client with only an
operation and request input:

~~~sh
python3 -B "$RETAINED_PACKAGE/scripts/firstmate.py" submit --request "$REQUEST_JSON"
python3 -B "$RETAINED_PACKAGE/scripts/firstmate.py" status
python3 -B "$RETAINED_PACKAGE/scripts/firstmate.py" gather
~~~

The request still has request_id and assignment. Read the complete report and
result before gather. A component uses FirstMate's completion contract; the root
delivers its ordinary scout report. See the [client contract](../packages/orchflows-firstmate/docs/firstmate-client.md).

## What FirstMate retains

The FirstMate configuration is local to this home: config/orchflows.json maps
canonical project paths to immutable package bundles and primitive policy.
Enablement copies the complete fork and each selected library, including its
guidance, references and assets, into data/.orchflows. It seals the bundle and
publishes the default only after checking its complete inventory. Logical
orchflows dependencies resolve to the retained fork; library roots are supplied
explicitly in caller-selected order.

Ordinary spawn applies a matching default under its existing launch transaction,
before worktree/endpoint allocation. Existing bindings and task metadata take
precedence over defaults. Each task retains its own existing attachment snapshot.
FirstMate's current metadata generation produces a distinct read-only context
file; relaunch supplies a new file rather than rewriting the old generation.

Re-enable from the owned source to activate a new default for future tasks.
Source edits, re-enablement or disablement do not replace active task snapshots,
accepted requests or results:

~~~sh
python3 -B "$FIRSTMATE_CODE/bin/fm-task-group.py" --home "$FM_HOME" disable \
  --project "$PROJECT"
~~~

This increment retains enabled bundles; automatic pruning and a general
install/update/rollback interface remain future work. Nothing is registered into
the user's active Claude/Codex plugin catalogs or normal Orchflows installation.

## Current scope

Automatic attachment applies to new scouts in an enabled project, using Linux
Herdr and Claude/Codex. Existing ordinary tasks, unmatched projects and ship or
secondmate tasks retain their existing route. Unsupported enabled scout
harnesses, backends and path overrides refuse explicitly.

A selected custom skill may compose the one admitted read-only Work or Review.
It may not add a second component, write the project, delegate from a component,
or bypass the package gate with native tools. Multi-component Dynamic, Build,
SelfImprove and broader custom/meta workflows remain unavailable. The
experimental design-loop example remains inactive and cannot be selected.

A project's Review profile is an explicitly selected standalone audit.
Composition-selected review in ordinary ship/no-mistakes delivery still needs
a change at FirstMate's existing policy owner, as identified in the
[owner mapping](firstmate-owner-mapping.md). No duplicate review gate or
new supervisor, recovery loop, scheduler or Herdr interface was added.

[Verification](normal-launch-verification.md) distinguishes source behavior,
fixtures and actual worker observations.
