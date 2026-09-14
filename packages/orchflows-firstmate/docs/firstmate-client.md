# Experimental FirstMate Work client

This client implements the package side of protocol `firstmate-task-group`, version `1`, scope `local-readonly-work`. It requires the matching experimental FirstMate task-group controller. The upstream FirstMate revision alone does not provide this API. Controller negotiation establishes an interface, not authenticated worker access or a certified runtime tuple.

Stage 1 permits one read-only Work component from a local normal root scout in Herdr. FirstMate attaches a complete snapshot of this fork and a clean local Git input commit before launching the root. The project must have no origin. The component inherits the root's Claude/Codex harness, model and effort. Review, writers, nesting, multiple components, continuation, remote homes, model overrides and the other four core workflows remain gated. Example libraries remain inactive migration fixtures.

## Inputs and invocation

Use Python 3.11+ inside the same operating environment as FirstMate. A Windows Python process is not a bridge to a WSL fleet. The task attachment and launch context supply these explicit inputs:

| Input | Meaning |
| --- | --- |
| `<snapshot>` | The attachment's retained `package_path`; invoke its client, not the mutable source or an installed normal Orchflows package |
| `<firstmate-code>` | Prepared experimental FirstMate code root containing `bin/fm-task-group.py` |
| `<firstmate-home>` | Owning FirstMate home, distinct from the Orchflows package home |
| `<root>` / `<generation>` | Normal root scout ID and its current `spawn_gen`, including after replacement |
| `<request-file>` | UTF-8 JSON file in the root's assigned temporary directory, outside the input and package snapshot |

```sh
python -B <snapshot>/scripts/firstmate.py --firstmate-root <firstmate-code> --home <firstmate-home> --root <root> --generation <generation> status
python -B <snapshot>/scripts/firstmate.py --firstmate-root <firstmate-code> --home <firstmate-home> --root <root> --generation <generation> submit --request <request-file>
python -B <snapshot>/scripts/firstmate.py --firstmate-root <firstmate-code> --home <firstmate-home> --root <root> --generation <generation> gather
```

The request has exactly these two fields:

```json
{"request_id":"inspect-1","assignment":"Inspect the attached source without edits. Apply the named Make guidance from the retained package and return findings with file references."}
```

The assignment carries the concrete read-only result, exact input and resolved Make guidance paths. Do not embed unsupported dispatch controls in its prose. FirstMate accepts identifiers matching `[A-Za-z0-9][A-Za-z0-9_.-]{0,63}`, an assignment of at most 32,768 UTF-8 bytes without NUL, and a request file of at most 1 MiB. Unsupported JSON fields and duplicate keys refuse.

The client calls only the controller, using a subprocess argument list and explicit home. It first negotiates protocol, then asks FirstMate for status. Status checks the current root, generation and retained snapshot digest. The client also checks the returned scope and attachment, its own exact snapshot path, and consistent `orchflows-firstmate` identities in all three manifests. It cannot attach a task, allocate endpoints or directly launch a worker. Run with `-B`; the client also disables bytecode writes, because any added or modified snapshot file invalidates its binding.

## Results and failures

Successful commands return the controller's JSON view, including the root, generation, attachment and current request record. Retain the request's child handle. Status is an observation, and does not acknowledge completion. Once FirstMate reports a complete retained result, `gather` verifies its bytes and acknowledges it for later FirstMate cleanup. Use the returned `report_path` and `result_path`; the component result remains separate from the root's report and outer delivery.

FirstMate owns the one-component reservation and request identity. An identical repeat returns its recorded disposition; a changed body cannot reuse the same ID, and a different ID cannot bypass an existing reservation. A replacement root uses its current generation to inspect or gather the original request. The client never automatically retries or replaces a launch.

Controller errors pass through as JSON with their exit code. Client refusals exit `2`. A timeout or malformed reply after submission is uncertain: a component may already exist even when its handle was not returned. Inspect FirstMate status and use its recovery owner. Do not resubmit a changed request, launch through another tool or infer that killing the controller terminated its child. `--timeout SECONDS` sets a finite positive bound per controller call; the default is 420 seconds, allowing the current FirstMate bridge's 360-second bound. A slow launch may outlive the transport timeout.

The component uses FirstMate's separate `complete` command with its current child generation and a bounded report in its recorded task temporary directory, as specified by its launch overlay. The root uses its normal FirstMate reporting and delivery path. FirstMate alone handles waiting, notification, endpoint cleanup and recovery; this client installs no service and provides no alternate scheduler.

## Evidence boundary

Setup and doctor retain `readiness_scope: package-only` and `integration.execution_ready: false`. `integration.status: experimental-client` means the client is shipped. It does not mean this task has an attachment, Herdr is operational, either worker is authenticated, or all Orchflows features work. Protocol fixture tests establish client behavior; actual FirstMate owner tests and named-lab native worker results require separate records with their exact source/runtime identities.
