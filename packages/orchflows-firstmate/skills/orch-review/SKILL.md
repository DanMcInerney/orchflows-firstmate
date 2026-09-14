---
name: orch-review
description: Request one experimental read-only independent audit through an explicitly authorized FirstMate task group in Herdr.
---

**Conditional experimental execution:** follow the [FirstMate client contract](../../docs/firstmate-client.md). Run the exact retained client with `--primitive Review status` before dispatch. It must negotiate advertised Review and `explicit-audit` support, validate the current root generation and exact fork snapshot, and confirm a read-only Review attachment with `review_policy: explicit-audit`. FirstMate validates the live worker profile. If any check fails, report the gap and stop. Package readiness, an available native Agent/spawn tool or an existing Work attachment does not authorize review. Never use native children, direct fleet/Herdr commands or normal Orchflows as a fallback.

## Single read-only audit

Only a normal local root scout explicitly attached by FirstMate for Review may request this audit. The one fresh reviewer inherits the root's Claude or Codex harness, model and effort, and reviews the attachment's immutable clean input commit. The reviewer must not have made that candidate. The root's deliverable is the requested audit report; this does not add a review gate to ordinary FirstMate delivery.

Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection), using the retained complete package's guidance. Write a request file in the root's assigned temporary directory with exactly `request_id` and `assignment`. Name the intended outcome, exact input commit, evidence, resolved Review guidance paths and allowed read-only verification. Instruct the reviewer to apply the Review sections and return supported findings without making or delegating repairs. Keep outputs outside the input and retained package.

Submit through the retained `scripts/firstmate.py` with `--primitive Review`, the explicit FirstMate code root, home, root ID and current generation. Keep the returned child identity. Use the same primitive and identity inputs for `status` and `gather`. FirstMate owns launch, waiting, result retention, recovery and cleanup. Read the full retained report and result files before gathering; gathering acknowledges completion and permits later cleanup. Then produce the ordinary root scout audit report through FirstMate. Component completion is not outer delivery.

A reservation consumes the group's one component. An identical replay keeps that child; changed assignments or a second request refuse. After root replacement, use the current generation to inspect and gather the original result. Uncertain launches, failed children and missing results require FirstMate reconciliation; never launch a replacement through another tool.

Writers, repairs, children, multiple components, model overrides, remote homes and dynamic/build/self-improve compositions remain unsupported in this attachment. Read-only is an instruction and result-validation contract, not an operating-system sandbox. Claude uses the supported Linux foreground profile; native background-tool supervision remains unverified.

## Upstream migration baseline (inactive)

The quoted original instructions below are retained for comparison; their native-child behavior does not apply to this fork.

> Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Launch a fresh native child who did not make the work to review without making or delegating repairs, applying the assignment's [model and effort](../../docs/architecture.md#model-and-effort) through native host controls. Give it the intended outcome, actual candidate state, resolved guidance paths and scoped caller choices; instruct it to read and apply the Review sections. Isolate per [hosts.md](../../docs/hosts.md) when concurrent edits or verification side effects need it.
