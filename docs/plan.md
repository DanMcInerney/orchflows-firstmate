# Plan: Orchflows as a FirstMate skill library

Written September 15, 2026; updated September 17 for FirstMate-owned dispatch.
This replaces the dev.1 through dev.9 direction recorded in the local, ignored
`archive/research/`.

## Goal

FirstMate keeps launching agents exactly as it does today. This library only
changes the pattern FirstMate follows when it does work: fresh agents for Work
and Review, composed through two terse skills into reusable workflows.
FirstMate chooses every agent's harness, model and effort through its normal
dispatch. Install the library in the primary's harness and select it through
the captain preference block. Nothing in FirstMate is patched, no dispatch
configuration is required by the library, and workers need no plugin.

## Principles kept from Orchflows

1. Two primitives. Work makes a result; Review judges it without fixing.
   Everything else is composition.
2. Terse skills. A skill names the assignment, its guidance and its checks; it
   links to contracts instead of restating them.
3. Workflows compose workflows. Loading a `SKILL.md` applies its instructions
   in the caller's context; only Work and Review create an agent.
4. Guidance is separate and layered: `guidance/<domain>.md` with dotted
   specializations, library extensions, removable model corrections.
5. Saved workflows describe assignments, guidance, dependencies and checks.
   Unlike upstream Orchflows, they carry no execution preferences.

## What FirstMate owns

Harness, model and effort selection, quota, brief, spawn, worktree, watcher,
steering, relaunch, recovery, cancellation, delivery and merge authority.
The two primitives use those owners;
[docs/firstmate.md](../packages/orchflows-firstmate/docs/firstmate.md)
records the mapping and checkpoints, and installed FirstMate owns command syntax.

## Decisions

| Question | Decision |
| --- | --- |
| Who coordinates | The FirstMate primary session. It never edits a project, so the smallest workflow is one Work and one Review. |
| Work | A fresh ship crewmate for a change; a fresh scout for a read-only result. |
| Review | A fresh scout that checks the candidate out detached and reports findings only. |
| Join | No captain-side merge. One maker per landed change by default; parallel makers only for independent deliverables, or a joining Work. |
| Repair | Return findings through FirstMate's steering and recovery, or dispatch fresh Work with the candidate and findings. One pass, no second Review. |
| Review versus delivery mode | no-mistakes: the pipeline is the Review; a named reviewer runs before validation only when the request or saved workflow asks (decided after the September 15 trial). direct-PR: on the PR before merge. local-only: on `fm/<id>` before merge. |
| Execution settings (September 17) | FirstMate owns harness, model and effort for every assignment. Workflows supply no defaults or overrides. Ignore legacy saved execution settings; remove them when updating a workflow. Current-request and local configuration preferences remain FirstMate's responsibility. |
| Default workflow | `captain.md` states it; the dynamic skill's description makes it the catch-all. |
| Invocation | Only `orch-dynamic-workflow` is model-invocable. Work, Review, build-workflow and custom workflows are manual-only: `disable-model-invocation: true` on Claude Code and `policy.allow_implicit_invocation: false` in `agents/openai.yaml` on Codex, following upstream (adopted September 16). |
| Durable state | Phase and task IDs in the backlog item note. |
| Authoring | The home is a registered local-only FirstMate project; build-workflow dispatches a Work into it. |
| Scope (September 16) | Build on FirstMate and never duplicate what it owns. No example libraries ship; the checkout is the core; the home holds only saved libraries and their catalogs; the CLI is `setup` and `doctor`. |

## September 17 scope

1. Remove the library's model policy, effort fallback, saved overrides and
   repair-profile selection instructions from the four skills and live docs.
2. Route every Work and Review through installed FirstMate's ordinary intake;
   keep assignment context, independent review, guidance and workflow state.
3. Update authoring to produce workflows without execution settings, and
   document migration of old saved settings and copied captain/dispatch rules.
4. Bump the package and host manifests so cached skills can refresh. Keep
   guidance and historical trial evidence unchanged.
5. Run package checks and distinguish instruction validation from live trials.

## Acceptance

- Install uses plugin registration, a captain preference block and a local-only
  library project. No FirstMate code, adapter, routing service or dispatch-rule
  change is required.
- Each skill is about 200 words or fewer and links rather than restates.
- A saved workflow is a `SKILL.md` that names its assignments, guidance,
  dependencies and checks, with no harness, model, effort or vendor selection.
- Package tests pass on Windows and Linux.

## Not done here

The [September 17 live suite](e2e-routing-2026-09-17.md) exercised the routing
simplification on local-only projects: dynamic work, authoring plus a trial,
saved-workflow reuse in a fresh Claude primary, review repairs and a dynamic
regression change. Artifact and composition assertions passed. Strict native
resolver assertions failed; all workers used Opus 5 with varying effort, so
configured multi-model routing remains unverified. Legacy saved-profile migration
also remains untried live. Still untried: the Codex invocation policy
through a Codex primary; Pi and omp primaries beyond the `captain.md` pointer;
`direct-PR` and `no-mistakes` placements.
