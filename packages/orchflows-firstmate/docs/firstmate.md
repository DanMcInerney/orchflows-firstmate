# FirstMate

This library runs Orchflows' pattern with FirstMate's own agents. The FirstMate primary session loads these skills and is the coordinator; every Work and Review is an ordinary crewmate or scout dispatched through `bin/fm-brief.sh` and `bin/fm-spawn.sh`. Nothing in FirstMate is patched. Workers need no plugin: their briefs carry absolute guidance and reference paths, which they read as files.

## Install

1. Install the checkout as a plugin in the harness that runs your FirstMate primary session, per [hosts](hosts.md#register-and-refresh), and run `python scripts/orchflows.py setup` once to create `~/.orchflows-firstmate` for the workflows you save.
2. Append the block below to `$FM_HOME/data/captain.md`. FirstMate prints that file in every session-start digest.
3. Register `~/.orchflows-firstmate` as a `local-only` FirstMate project with [no origin remote](#local-only-projects) so [orch-build-workflow](../skills/orch-build-workflow/SKILL.md) can ship saved workflows into it.

Start a new FirstMate session. FirstMate's existing dispatch configuration applies; this library needs no role rules or routing service. A remote secondmate needs steps 1 and 3 on its own host; secondmates inherit `captain-shared.md` rather than `captain.md`, so put the block there when they should follow it.

### captain.md block

```markdown
## Orchflows
- Run every ship and scout through orch-dynamic-workflow unless I name another workflow or say "plain". Run any other workflow only when I name it: invoke it by its slash command or read its SKILL.md by path.
- Use your normal dispatch and recovery for every workflow. Follow <core>/docs/architecture.md#model-and-effort for the boundary with saved workflows.
- Record each workflow's phase and task IDs in the backlog item note and resume from it after a restart.
- Read <core>/docs/firstmate.md before the first Orchflows dispatch of a session.
```

Replace `<core>` with the checkout path.

### Upgrading from 0.4 or earlier

[Refresh the core registration](hosts.md#register-and-refresh) and replace the old Orchflows block in `captain.md` (and `captain-shared.md` if used) with the block above, then start a new session. Keep saved workflows' assignments, guidance and dependencies; their old harness, model, effort and vendor-selection preferences no longer apply. Remove those preferences when next editing a workflow, including any repair instructions that exist only to enforce them.

If you copied the old example role rules into `crew-dispatch.json`, review them through FirstMate's normal configuration process: they remain active until you remove or change them. Preserve deliberate personal routing preferences. `setup` does not rewrite FirstMate configuration or saved workflows. Earlier trial records describe the previous routing contract and remain historical evidence.

## How a workflow runs

Follow the installed FirstMate's `AGENTS.md` dispatch contract and `harness-adapters` skill before spawning or recovering an agent. They own profile resolution, capability checks and concrete launch flags. Use each owner's current help for command syntax.

| Orchflows step | FirstMate action |
| --- | --- |
| Work, a change | ordinary ship intake, then `fm-brief.sh` and `fm-spawn.sh` with the project's delivery mode and merge posture |
| Work, read-only | ordinary scout intake, then `fm-brief.sh` and `fm-spawn.sh` |
| Review | ordinary scout intake and dispatch; the brief names the exact candidate, the detached checkout and findings only; see [brief wording](#brief-wording) |
| Assignment and guidance | the brief's `## Firstmate spec`: assignment, input state, absolute guidance paths, checks, and "read and apply the Make sections" or "the Review sections" |
| Wait | FirstMate's watcher; the captain acts on `done`, `needs-decision`, `blocked` and report events |
| Repair | `fm-send.sh` with the report path and verdict, the numbered repairs, any finding deliberately deferred, and a request for a fresh `done:` line; FirstMate owns recovery or relaunch when needed; a fresh Work receives the candidate and findings |
| Deliver | the project's delivery mode and merge authority, unchanged |
| State | the request's backlog item note: `orchflows: <workflow> phase=<phase> work=<id> (fm/<id> @<sha>) review=<id> (<verdict>) repair=<steer\|relaunch\|id> guidance=<domains>`; each task's own note names the workflow, phase and role |

Brief uses the registered project name; spawn requires its clone path under `$FM_HOME/projects/`. Phases are `plan`, `work`, `review`, `repair` and `deliver` for the dynamic workflow, or a saved workflow's own phase names. Run every owner from the FirstMate checkout with `FM_HOME` exported, never from a project worktree or a foreign checkout: the Treehouse lock path is hashed with a bare `git` call in the current directory, and teardown refuses when that call fails.

The brief's captain's-intent section keeps the captain's words; Orchflows context belongs in the Firstmate spec. A worker never sees this library's skills; it sees its assignment and the guidance files named in its brief.

### Brief wording

The Firstmate spec of every Orchflows agent opens with its identity, and the trial showed each line below was needed:

- A maker: "This is the `<phase>` phase of `<workflow>`: one Orchflows Work as a ship in this project's delivery mode. Do not delegate to subagents; one agent owns this result." It ends with "Commit on your branch with a clear message, then follow this brief's `<mode>` definition of done exactly." A read-only maker says "as a read-only scout" and "do not change project files".
- A reviewer: "an independent read-only audit by a fresh agent who did not make the candidate. Do not edit any file, do not delegate. Your deliverable is findings with evidence in your report." Its candidate section gives the exact ref and the command: "Branch `fm/<id>` of this repository. In your scratch worktree run: `git checkout --detach fm/<id>` (the branch exists locally; `git branch -a` lists it). Record the commit SHA you reviewed at the top of your report. You may run the tests and the tool." For a PR, `gh pr checkout`; for a report, the report path.
- Both: "Read first, then apply the Make sections" or "the Review sections", followed by absolute guidance paths, then the assignment, the numbered checks, and "end with a verdict: ready, ready with the listed repairs, or not ready" for a reviewer.
- A repair steer names the report path and asks the worker to read it in full, lists exactly the repairs to make, names any finding not to act on and why, forbids other changes, and ends with "append a fresh `done: ...` line to your status file". A steered worker that finishes without a new status line never wakes the captain.

Codex workers need the captain on their first launch in a project; FirstMate's `harness-adapters` skill owns those prompts and the captain follows it. A Codex worker may also report `blocked:` on a tooling limit, such as backticks in a shell command; answer by steer with a workaround, such as a committed script or the native file-edit tool.

## Delivery modes

| Mode | Review | Repair | Landing |
| --- | --- | --- | --- |
| `no-mistakes` | the no-mistakes run: trigger `/no-mistakes` on the maker after its implementation commit; dispatch no scout unless the request or a saved workflow names a reviewer, who then reviews the branch before validation | inside the run; a named reviewer's findings by steer before validation | no-mistakes owns fixes, push, PR and CI; merge authority as configured |
| `direct-PR` | a scout on the opened PR | steer the maker; it updates the PR | merge authority as configured |
| `local-only` | a scout on `fm/<id>` after `done: ready in branch` | steer the maker; it updates the branch | `fm-merge-local.sh` after captain approval |
| scout only | a scout on the report | steer the scout or dispatch a fresh scout | the report is the deliverable |

On a `no-mistakes` project the pipeline is the Review: FirstMate's captain contract gives no-mistakes sole ownership of review and fixes, and a second reviewer before it doubles the cost without a second landing. The `captain.md` block is therefore the standing request for an independent reviewer on `direct-PR`, `local-only` and scout work, where stock FirstMate would add none. Ask for a separate review deliverable, or save that assignment in a workflow, when a specific audit is needed before no-mistakes runs. FirstMate chooses that scout's execution profile; the workflow does not configure the pipeline's internal reviewers.

### Local-only projects

A local-only project must have no `origin` remote. When a worktree has an origin configured, `fm-spawn.sh` fetches it and resets the pooled worktree to `origin/<default>`; `fm-merge-local.sh` advances only local `main`, so every task after the first would start from a stale base. Remove the remote before registering the project; a purely local project created through FirstMate's `project-management` skill has none.

## Named workflows

Every skill except orch-dynamic-workflow is manual-only per the [invocation policy](hosts.md#invocation-policy). The captain runs one when the request names it: by its slash command, or by reading its `SKILL.md` from `<core>/skills/` or the resolved library path. Skills that a running workflow links are read as files.

## What this library does not do

It does not patch `bin/`, `AGENTS.md` or any FirstMate skill. It does not run subagents inside workers. It adds no controller, scheduler, snapshot or client. If a future FirstMate exposes a richer worker interface, these skills change, not FirstMate.
