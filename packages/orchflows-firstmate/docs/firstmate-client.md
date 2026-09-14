# Experimental FirstMate Work and Review client

This client implements the package side of protocol `firstmate-task-group`, version `1`, scopes `local-readonly-work`, `local-readonly-review`, `local-dynamic` and `local-dynamic-ship-local-only`. It requires the matching experimental FirstMate task-group controller. The upstream FirstMate revision alone does not provide this API. Controller negotiation establishes an interface, not authenticated worker access or a certified runtime tuple.

The client supports legacy one-component read-only Work/Review attachments and an explicitly admitted bounded dynamic workflow from a normal Linux root scout or explicitly selected ordinary ship/local-only root. FirstMate retains the complete fork, selected custom libraries and accepted input commits. The component inherits the root's Claude/Codex harness, model and effort. The project must satisfy FirstMate's clean local Git/no-origin admission. [Bounded leaf authoring](#bounded-leaf-authoring) uses the existing dynamic local-only profile. Nesting, component continuation, model overrides, remote homes, direct-PR and no-mistakes delivery, promotion, general composing Build and SelfImprove remain gated. Optional examples remain migration source rather than certified workflows.

## Primitive and review authority

FirstMate records Work or Review in each launch context. The returned attachment
selects legacy single-primitive or dynamic behavior; a dynamic context remains Work. For Review it must see the
controller's advertised Review capability and the same selected primitive and
policy in the attachment. A legacy Work attachment cannot be upgraded by changing the request body,
a prompt, an environment variable or a client flag.

FirstMate's administrator admits a standalone audit before the root launches:

~~~sh
python3 "$FIRSTMATE_CODE/bin/fm-task-group.py" --home "$FM_HOME" attach "$ROOT_TASK" \
  --package "$PACKAGE" --project "$PROJECT" \
  --primitive Review --review-policy explicit-audit
~~~

This audits the frozen clean Git input commit in a fresh component. It does not
compose Work followed by Review in the same attachment, freeze a dirty writer
candidate, or authorize repairs. The reviewer applies the retained package's
Review guidance and returns findings without changing project files. Only the
root writes and delivers its ordinary scout audit report.

## Explicit local-only root delivery

An ordinary ship selects dynamic explicitly through FirstMate's existing spawn
owner with `--mode local-only --orchflows-workflow dynamic`. New default ship
tasks remain unchanged. Package capability metadata and controller protocol must
both advertise `root_deliveries: ["ship-local-only"]`. A retained dev.6 package
cannot acquire ship behavior by enabling or attaching it again.

The attachment and exact-generation launch context retain
`root_delivery: {"kind":"ship","mode":"local-only","branch":"fm/<id>"}`.
Root metadata records `task_group_delivery=ship-local-only`; current root kind,
mode and actual symbolic branch must match the attachment across status, replay,
new requests, gathering and relaunch. Missing root delivery preserves the scout
contract. The ship view uses `local-dynamic-ship-local-only`, which retained
scout-only clients refuse.

Work and Review components remain scouts returning committed results or reports
to their parent. Only the root delivers: commit the complete clean joined result
on `fm/<id>`, record `done: ready in branch fm/<id>` and stop. Requested diagnostic
reports use recorded tasktmp. FirstMate's existing merge authority and
`fm-merge-local.sh` land the branch; the existing task-group guard refuses pending
results, unfinished Review and incompatible delivery before landing. No-mistakes
owns all validation once it begins; this selected profile cannot switch to that
pipeline or dispatch through changed delivery metadata.

## Bounded dynamic profile

New dynamic enablement requires scripts/firstmate-client.json declaring schema 1,
launch_context_schema 1 and workflows ["dynamic"]. Retained dev.5 capability
metadata still selects its original context contract; a missing declaration
retains the older explicit client route. The controller handshake keeps protocol
version 1 and local-readonly-work scope, adding workflows ["dynamic"] and
review_policies containing workflow-review alongside advertised Work and Review.

The returned dynamic view uses scope local-dynamic. Its attachment must have
exactly the supported profile values: workflow dynamic, primitive Work,
review_policy workflow-review, readonly false and max_components 32. Existing
root, epoch, package path and digest checks still apply. Linux is required.
These checks admit this profile only; arbitrary workflow names and expanded
component limits refuse.

Write a dynamic request with exactly four fields:

~~~json
{"request_id":"maker-1","assignment":"Implement the assigned change with retained Make guidance and return check evidence.","primitive":"Work","writable":true}
~~~

Read-only investigation selects Work/writable false. The one independent audit
selects Review/writable false. Review cannot be writable. Per-request primitive
selection belongs in this JSON; the client's authority flag --primitive remains
the launch attachment primitive and cannot override context. Other dispatch
controls remain unsupported.

FirstMate freezes the current clean root worktree commit for every new request.
Each request retains its own input_commit; a writer must commit its result and
returns output_commit. Read and gather the result, then use ordinary Git in the
root's assigned worktree to join the intended commit range. For example, inspect
the commits between input_commit and output_commit before cherry-picking that
range. Resolve conflicts and verify the joined candidate there. The package does
not own a separate writer or merge mechanism.

Status without an ID returns an aggregate requests list of full request views.
Use stable request IDs to select results:

~~~sh
python3 -B <snapshot>/scripts/firstmate.py status --request-id maker-1
python3 -B <snapshot>/scripts/firstmate.py gather --request-id maker-1
~~~

Dynamic gather always requires --request-id. Read the complete selected report
and result first. Gather every prior Work, join useful output, run checks and
commit the exact clean candidate before requesting the fresh independent Review.
Its input_commit identifies that candidate. Gather the Review, then make one
repair/check pass directly or through scoped Work requests; a second Review is
not admitted. Keep total components within 32, including Review and repair work.

A selected complete custom skill can compose the same bounded primitives with
the same policy and limits. FirstMate's existing intake, spawn, worktree, inbox,
recovery and delivery owners remain authoritative. Component completion returns
to the root; it does not run root delivery or introduce ship/no-mistakes review
gates.

## Bounded leaf authoring

[orch-build-workflow](../skills/orch-build-workflow/SKILL.md) composes existing
Work/Review requests in an explicitly selected dynamic ship/local-only root.
It authors a complete library whose leaf skill performs its assignment without
delegating; the library may include domain guidance and declared dependencies.
This adds no primitive, attachment mode, capability, runtime or installation
authority. This Build composition in scouts, composing or nested trials and SelfImprove
remain unavailable.

The root joins the authored library and commits its clean candidate before a
fresh Work trials the leaf. That component reads the candidate library from its
own frozen worktree and resolves its declared dependencies from the retained
package roots. Its assignment names repository-relative input/library locations
and the supplied retained roots; it must not use the parent worktree's absolute
paths, a mutable source catalog or an undeclared user home. Loading the leaf
does not create an attachment or authorize delegation.

A read-only trial keeps project and Git state unchanged and writes its complete
text output and findings in its recorded tasktmp report. The existing complete,
status and gather operations retain that report. The root commits the actual
output and trial evidence outside the deliverable library before final Review;
links to disposable component files do not retain an artifact. Library
trials/ may contain reusable requests and expected behavior. Any needed
writable trial remains a scoped Work whose complete output is committed and
joined through the same owner.

Return trial findings to authoring before the one final Review. Component
continuation is unavailable: the authorized root can refine the candidate, or
fresh Work can receive it and the committed trial record. After relaunch, use
the new launch context to recover the same accepted requests and reread the
authoring requirements and trial evidence before resuming. The final Review
identifies the clean joined library and evidence commit; then the existing
repair/check and ready-branch delivery contract applies. If the repair changes
the trialed library, rerun affected behavior through fresh Work and commit that
trial's actual output, retained result and identities before readiness. Preserve
the original Review evidence and identify the repaired candidate separately.
A tasktmp-only diagnostic does not retain the repair trial with the delivered
library. This is the same repair/check pass, without another Review.

An outer caller may arrange an unrelated-project trial through ordinary
FirstMate enablement and spawn using the complete authored library. The
authoring root cannot launch that fleet task itself. A portability claim
requires that evidence before final Review; a later reuse trial is reported
separately. This bounded case does not establish general Build parity,
native registration by skill name or implicit user-home publication.

### Trial digest meanings

request.result_digest identifies the entire retained result.json: SHA-256
of its UTF-8 canonical JSON (sorted keys, compact separators, ensure_ascii=False).
result.report_digest identifies the raw retained report bytes. They are
different digests and must not be substituted for each other during review or
repair. Label both explicitly in trial provenance. When evidence must be
verifiable after task cleanup, commit the retained result JSON alongside the
exact trial output, outside the deliverable library, so both digests can be
checked from the delivered files. Findings must be checked against the digest's
declared object before changing a correct value.

## Inputs and invocation

Use Python 3.11+ inside the same operating environment as FirstMate. A Windows
Python process is not a bridge to a WSL fleet. FirstMate's spawn owner supplies
`ORCHFLOWS_FIRSTMATE_CONTEXT` and identifies the exact retained package snapshot
in the launch instructions. Workers use its client directly:

```sh
python3 -B <snapshot>/scripts/firstmate.py status
python3 -B <snapshot>/scripts/firstmate.py submit --request <request-file>
python3 -B <snapshot>/scripts/firstmate.py gather
```

Place the UTF-8 request file in the root's assigned temporary directory, outside
the input and package snapshot. Inspect status before dispatch: legacy Work requires Work; standalone Review
requires Review/explicit-audit; dynamic requires its exact workflow-review profile. The environment
provides invocation context, not authorization.

FirstMate publishes one immutable context file per launch after publishing that
launch's metadata. Relaunch receives a new context with the new generation and
the same retained attachment. An old worker keeps its original generation and
must refuse when FirstMate considers it stale. The client never replaces that
generation by reading mutable task metadata.

The context is a regular UTF-8 JSON file of at most 16 KiB with exactly these
fields; duplicate keys, unknown fields and symlinks refuse:

| Field | Meaning |
| --- | --- |
| `schema` | Integer `1` |
| `firstmate_root` | Absolute canonical prepared FirstMate directory containing `bin/fm-task-group.py` |
| `home` | Absolute canonical owning FirstMate directory, distinct from the package home |
| `root` | Attached normal root task ID |
| `generation` | This launch's `spawn_gen` |
| `primitive` | `Work` or `Review`, matching the admitted attachment; dynamic uses Work |
| `package_path` | Absolute canonical retained snapshot directory; it must equal the running client's package root |

All directory fields must exist and contain no symlinks. Root and generation
must be valid FirstMate identifiers. The client validates this context before
contacting the controller. `--context <context-file>` explicitly selects a launch
context instead of the environment value.

The previous explicit invocation remains available for administrator fixtures
and older integrations. Without launch context it defaults to Work; an explicit
audit supplies `--primitive Review`:

```sh
python3 -B <snapshot>/scripts/firstmate.py --firstmate-root <firstmate-code> --home <firstmate-home> --root <root> --generation <generation> status
```

The same explicit inputs work for submit and gather. A context cannot be mixed
with any manual authority flag (`--firstmate-root`, `--home`, `--root`,
`--generation` or `--primitive`), including when the context comes from the
environment. Missing context and incomplete explicit authority refuse.

A legacy single Work/Review request has exactly these two fields:

```json
{"request_id":"inspect-1","assignment":"Inspect the attached source without edits. Apply the named Make guidance from the retained package and return findings with file references."}
```

The assignment carries the concrete read-only result, exact input and resolved Make guidance paths for Work, or Review guidance paths for an audit. Do not embed unsupported dispatch controls in its prose. FirstMate accepts identifiers matching `[A-Za-z0-9][A-Za-z0-9_.-]{0,63}`, an assignment of at most 32,768 UTF-8 bytes without NUL, and a request file of at most 1 MiB. Unsupported JSON fields and duplicate keys refuse.

The client calls only the controller, using a subprocess argument list and explicit home. It first negotiates protocol, then asks FirstMate for status. Status checks the current root, generation and retained snapshot digest. The client also checks the returned scope and attachment, its own exact snapshot path, and consistent `orchflows-firstmate` identities in all three manifests. It cannot attach a task, allocate endpoints or directly launch a worker. Run with `-B`; the client also disables bytecode writes, because any added or modified snapshot file invalidates its binding.

## Results and failures

Successful commands return the controller's JSON view, including the root, generation, attachment and current request record. Retain the request's child handle. Status is an observation, and does not acknowledge completion. Once FirstMate reports a complete retained result, `gather` verifies its bytes and acknowledges it for later FirstMate cleanup. Use the returned `report_path` and `result_path`; the component result remains separate from the root's report and outer delivery.

FirstMate owns component reservations and request identity. An identical repeat returns its recorded disposition; a changed body cannot reuse the same ID. Legacy attachments retain one reservation, while dynamic admits multiple distinct IDs within its bounded policy. A replacement root uses its newly supplied launch context to inspect or gather the original request. The client never automatically retries or replaces a launch.

Controller errors pass through as JSON with their exit code. Client refusals exit `2`. A timeout or malformed reply after submission is uncertain: a component may already exist even when its handle was not returned. Inspect FirstMate status and use its recovery owner. Do not resubmit a changed request, launch through another tool or infer that killing the controller terminated its child. `--timeout SECONDS` sets a finite positive bound per controller call; the default is 420 seconds, allowing the current FirstMate bridge's 360-second bound. A slow launch may outlive the transport timeout.

The component uses FirstMate's separate `complete` command with its current child generation and a bounded report in its recorded task temporary directory, as specified by its launch overlay. The root uses its normal FirstMate reporting and delivery path. FirstMate alone handles waiting, notification, endpoint cleanup and recovery; this client installs no service and provides no alternate scheduler.

Writer results also retain an immutable output_ref in the shared Git database. FirstMate publishes that ref before the result, and validates it before gather or cleanup. It preserves the full output ancestry through component/root teardown. These archival refs are not pruned automatically; a future explicit result-pruning owner must manage refs and retained records together. A missing or changed ref requires owner reconciliation.

## Evidence boundary

Setup and doctor retain `readiness_scope: package-only` and `integration.execution_ready: false`. `integration.status: experimental-client` means the client is shipped. It does not mean this task has an attachment, Herdr is operational, either worker is authenticated, or all Orchflows features work. Protocol fixture tests establish client behavior; actual FirstMate owner tests and named-lab native worker results require separate records with their exact source/runtime identities.
