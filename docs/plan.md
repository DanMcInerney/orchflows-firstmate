# Plan: Orchflows as a FirstMate skill library

Written September 15, 2026. This replaces the dev.1 through dev.9 direction
recorded in [archive/research](../archive/research/).

## Goal

FirstMate keeps launching agents exactly as it does today. This library only
changes the pattern FirstMate follows when it does work: fresh agents for Work
and Review, composed through two terse skills into reusable workflows, with
optional model and effort per agent. Installing the library into the harness
that runs the FirstMate primary session is the whole integration. Nothing in
FirstMate is patched, and workers need no plugin.

## Principles kept from Orchflows

1. Two primitives. Work makes a result; Review judges it without fixing.
   Everything else is composition.
2. Terse skills. A skill names the assignment, its guidance and its checks; it
   links to contracts instead of restating them.
3. Workflows compose workflows. Loading a `SKILL.md` applies its instructions
   in the caller's context; only Work and Review create an agent.
4. Guidance is separate and layered: `guidance/<domain>.md` with dotted
   specializations, library extensions, removable model corrections.
5. Model and effort are optional, per assignment, in plain language.

## What FirstMate owns

Brief, spawn, worktree, watcher, steering, relaunch, recovery, cancellation,
delivery and merge authority. The two primitives tell the captain how to use
those owners; [docs/firstmate.md](../packages/orchflows-firstmate/docs/firstmate.md)
records the exact commands and checkpoints.

## Decisions

| Question | Decision |
| --- | --- |
| Who coordinates | The FirstMate primary session. It never edits a project, so the smallest workflow is one Work and one Review. |
| Work | A fresh ship crewmate for a change; a fresh scout for a read-only result. |
| Review | A fresh scout that checks the candidate out detached and reports findings only. |
| Join | No captain-side merge. One maker per landed change by default; parallel makers only for independent deliverables, or a joining Work. |
| Repair | Steer the maker when it can honor the fixer's settings, relaunch it with a new profile, or dispatch fresh Work. One pass, no second Review. |
| Review versus delivery mode | no-mistakes: the pipeline is the Review; a named reviewer runs before validation only when the request or saved workflow asks (decided after the September 15 trial). direct-PR: on the PR before merge. local-only: on `fm/<id>` before merge. |
| Model and effort defaults | `config/crew-dispatch.json` rules for the Orchflows Work and Review roles; request or saved-workflow settings override; FirstMate's effort fallback otherwise. |
| Default workflow | `captain.md` states it; the dynamic skill's description makes it the catch-all. |
| Invocation | Only `orch-dynamic-workflow` is model-invocable. Work, Review, build-workflow, examples and custom workflows are manual-only: `disable-model-invocation: true` on Claude Code and `policy.allow_implicit_invocation: false` in `agents/openai.yaml` on Codex, following upstream (adopted September 16). |
| Durable state | Phase and task IDs in the backlog item note. |
| Authoring | The home is a registered local-only FirstMate project; build-workflow dispatches a Work into it. |

## Work items

1. Retire `integrations/firstmate/`, `tools/`, the package client and its
   tests; archive the research docs.
2. Rewrite the five skills to upstream length with FirstMate primitives.
3. Rewrite `docs/architecture.md`, `hosts.md`, `home.md` and `history.md`;
   add `docs/firstmate.md` with install steps, the `captain.md` block,
   dispatch rules, delivery placement and durable state.
4. Reduce `scripts/orchflows.py` to setup, doctor and resolve.
5. Update manifests, README, AGENTS and UPSTREAM; keep guidance and example
   libraries unchanged.
6. Run the package tests and verify every core link resolves.

## Acceptance

- Install is a plugin registration plus two edits in the FirstMate home; no
  file under FirstMate's `bin/` or its `AGENTS.md` changes.
- Each skill is about 200 words or fewer and links rather than restates.
- A saved workflow is a `SKILL.md` that names its assignments, guidance and
  optional settings, nothing else.
- Package tests pass on Windows and Linux.

## Not done here

Done since, on local-only projects through a Claude Code primary: the dynamic
workflow, a workflow built by name and a saved workflow run by name (see the
trial records in the root README). Still untried: the Codex invocation policy
through a Codex primary; Pi and omp primaries beyond the `captain.md` pointer;
`direct-PR` and `no-mistakes` placements.
