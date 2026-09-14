---
name: orch-work
description: Request one experimental read-only Work result through an attached FirstMate task group in Herdr.
---

**Conditional experimental execution:** follow the [FirstMate client contract](../../docs/firstmate-client.md). Before dispatch, run the exact retained client with `--primitive Work status`. It must negotiate the real controller and validate the current root generation, exact retained fork snapshot and read-only Work attachment. A Review attachment cannot accept Work. If any input or check is missing, report the gap and stop. Package readiness, environment variables and host plugin discovery do not satisfy this gate. Never use native Agent/spawn tools, direct fleet/Herdr commands or normal Orchflows as a fallback.

## Stage 1 Work

Only a normal local root scout attached by FirstMate may request one read-only maker component in Herdr. It inherits the root's Claude or Codex harness, model and effort. Editing, independent Review, multiple components, nesting, continuation, model/effort overrides, remote homes and broader composed workflows remain unsupported; refuse a request requiring them. Read-only is an instruction and result-validation contract, not an operating-system sandbox.

Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection), using only the retained complete package's guidance. Write a request file in the root's assigned temporary directory with exactly `request_id` and `assignment`. The assignment names the read-only result, exact input, applicable Make guidance paths and evidence to return. Do not place this file inside the retained package or input repository. Submit it through `scripts/firstmate.py` from the attachment, with `--primitive Work`, the explicit FirstMate code root, home, root ID and current generation.

Keep the returned FirstMate child identity. FirstMate owns launch, waiting, recovery and completion. Use client `status` to inspect current state, always with `--primitive Work`. Read the complete retained report and result files before `gather` verifies and acknowledges the result. Report uncertain launches, failed children and missing results without starting replacements. Reusing a request ID with a changed assignment is an error; a consumed group cannot accept a second request. A restarted root uses its new generation to inspect and gather the original assignment. Component completion does not complete or deliver the root task.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Launch a fresh native child to make the requested result, applying the assignment's [model and effort](../../docs/architecture.md#model-and-effort) through native host controls. Give it the assignment, intended workspace and input state, resolved guidance paths and scoped caller choices; instruct it to read and apply the Make sections. Isolate per [hosts.md](../../docs/hosts.md) when edits could overlap.
