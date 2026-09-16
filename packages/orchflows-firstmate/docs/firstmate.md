# FirstMate

This library runs Orchflows' pattern with FirstMate's own agents. The FirstMate primary session loads these skills and is the coordinator; every Work and Review is an ordinary crewmate or scout dispatched through `bin/fm-brief.sh` and `bin/fm-spawn.sh`. Nothing in FirstMate is patched. Workers need no plugin: their briefs carry absolute guidance and reference paths, which they read as files.

## Install

1. Install this package into the harness that runs your FirstMate primary session, per [hosts](hosts.md#register-and-refresh), and run `python scripts/orchflows.py setup` once to create `~/.orchflows-firstmate` for your own libraries.
2. Append the block below to `$FM_HOME/data/captain.md`. FirstMate prints that file in every session-start digest.
3. Optionally add the role defaults below to `$FM_HOME/config/crew-dispatch.json`. FirstMate's bootstrap validates the file, and its quota ranker applies to any profile array.
4. Register `~/.orchflows-firstmate` as a `local-only` FirstMate project with [no origin remote](#local-only-projects) so [orch-build-workflow](../skills/orch-build-workflow/SKILL.md) can ship saved workflows into it.

Start a new FirstMate session. A remote secondmate needs steps 1 and 4 on its own host; secondmates inherit `captain-shared.md` rather than `captain.md`, so put the block there when they should follow it.

### captain.md block

```markdown
## Orchflows
- Run every ship and scout through orch-dynamic-workflow unless I name another workflow or say "plain". Run any other workflow only when I name it: invoke it by its slash command or read its SKILL.md by path.
- Resolve each agent's model and effort per <core>/docs/architecture.md#model-and-effort: my request, then the saved workflow, then the Orchflows rules in crew-dispatch.json, then your effort fallback.
- Record each workflow's phase and task IDs in the backlog item note and resume from it after a restart.
- Read <core>/docs/firstmate.md before the first Orchflows dispatch of a session.
```

Replace `<core>` with the installed package path from [hosts](hosts.md#register-and-refresh).

### crew-dispatch.json roles

```json
{
  "rules": [
    {
      "when": "Orchflows Work: a maker with a clear, bounded assignment",
      "use": {"harness": "claude", "model": "claude-sonnet-5", "effort": "xhigh"},
      "why": "A cheaper model; the assignment and guidance carry the judgment"
    },
    {
      "when": "Orchflows Review or investigation: a fresh reviewer, or a scout resolving ambiguity before work",
      "use": {"harness": "claude", "model": "claude-fable-5-1", "effort": "high"},
      "why": "The strongest model where judgment matters most"
    }
  ],
  "default": {"harness": "claude"}
}
```

Use models and efforts your harnesses accept; FirstMate omits an effort a harness cannot take and records it in task metadata. A `use` array makes the choice quota-aware. Rules may name different harnesses per role, because every agent is its own spawn.

## How a workflow runs

| Orchflows step | FirstMate action |
| --- | --- |
| Work, a change | `fm-brief.sh <id> <repo> --mode <mode>`, then `fm-spawn.sh <id> <project-path> --mode <mode> --yolo <on\|off> --harness H --model M --effort E` |
| Work, read-only | `fm-brief.sh <id> <repo> --scout`, then `fm-spawn.sh <id> <project-path> --scout --harness H --model M --effort E` |
| Review | a scout spawned the same way, whose brief names the exact candidate, the detached checkout and findings only; see [brief wording](#brief-wording) |
| Assignment and guidance | the brief's `## Firstmate spec`: assignment, input state, absolute guidance paths, checks, and "read and apply the Make sections" or "the Review sections" |
| Wait | FirstMate's watcher; the captain acts on `done`, `needs-decision`, `blocked` and report events |
| Repair | `fm-send.sh <id>` with the report path and verdict, the numbered repairs, any finding deliberately deferred, and a request for a fresh `done:` line; `fm-control.sh <id> relaunch --model M --effort E` when the fixer's profile differs; or a fresh Work |
| Deliver | the project's delivery mode and merge authority, unchanged |
| State | the request's backlog item note: `orchflows: <workflow> phase=<phase> work=<id> (fm/<id> @<sha>) review=<id> (<verdict>) repair=<steer\|relaunch\|id> guidance=<domains>`; each task's own note names the workflow, phase and role |

`<repo>` is the registered project name; `<project-path>` is its clone under `$FM_HOME/projects/`, which spawn requires as a path. Phases are `plan`, `work`, `review`, `repair` and `deliver` for the dynamic workflow, or a saved workflow's own phase names. Run every owner from the FirstMate checkout with `FM_HOME` exported, never from a project worktree or a foreign checkout: the Treehouse lock path is hashed with a bare `git` call in the current directory, and teardown refuses when that call fails.

The brief's captain's-intent section keeps the captain's words; Orchflows context belongs in the Firstmate spec. A worker never sees this library's skills; it sees its assignment and the guidance files named in its brief.

### Brief wording

The Firstmate spec of every Orchflows agent opens with its identity, and the trial showed each line below was needed:

- A maker: "This is the `<phase>` phase of `<workflow>`: one Orchflows Work as a ship in this project's delivery mode. Do not delegate to subagents; one agent owns this result." It ends with "Commit on your branch with a clear message, then follow this brief's `<mode>` definition of done exactly." A read-only maker says "as a read-only scout" and "do not change project files".
- A reviewer: "an independent read-only audit by a fresh agent who did not make the candidate. Do not edit any file, do not delegate. Your deliverable is findings with evidence in your report." Its candidate section gives the exact ref and the command: "Branch `fm/<id>` of this repository. In your scratch worktree run: `git checkout --detach fm/<id>` (the branch exists locally; `git branch -a` lists it). Record the commit SHA you reviewed at the top of your report. You may run the tests and the tool." For a PR, `gh pr checkout`; for a report, the report path.
- Both: "Read first, then apply the Make sections" or "the Review sections", followed by absolute guidance paths, then the assignment, the numbered checks, and "end with a verdict: ready, ready with the listed repairs, or not ready" for a reviewer.
- A repair steer names the report path and asks the worker to read it in full, lists exactly the repairs to make, names any finding not to act on and why, forbids other changes, and ends with "append a fresh `done: ...` line to your status file". A steered worker that finishes without a new status line never wakes the captain.

Codex workers need the captain on their first launch in a project: the repository trust prompt, which FirstMate's `harness-adapters` reference covers, and on Codex 0.154 or later a one-time review of new or changed hooks. Answer the first with `fm-send.sh <id> --key Enter` and the second in the worker's pane; later Codex tasks in that project start unattended. A Codex worker may also report `blocked:` on a tooling limit, such as backticks in a shell command; answer by steer with a workaround, such as a committed script or the native file-edit tool.

## Delivery modes

| Mode | Review | Repair | Landing |
| --- | --- | --- | --- |
| `no-mistakes` | the no-mistakes run: trigger `/no-mistakes` on the maker after its implementation commit; dispatch no scout unless the request or a saved workflow names a reviewer, who then reviews the branch before validation | inside the run; a named reviewer's findings by steer before validation | no-mistakes owns fixes, push, PR and CI; merge authority as configured |
| `direct-PR` | a scout on the opened PR | steer the maker; it updates the PR | merge authority as configured |
| `local-only` | a scout on `fm/<id>` after `done: ready in branch` | steer the maker; it updates the branch | `fm-merge-local.sh` after captain approval |
| scout only | a scout on the report | steer the scout or dispatch a fresh scout | the report is the deliverable |

On a `no-mistakes` project the pipeline is the Review: FirstMate's captain contract gives no-mistakes sole ownership of review and fixes, and a second reviewer before it doubles the cost without a second landing. The `captain.md` block is therefore the standing request for an independent reviewer on `direct-PR`, `local-only` and scout work, where stock FirstMate would add none. Ask for a named reviewer, or save one in a workflow, when a different model or vendor should judge the code before no-mistakes runs.

### Local-only projects

A local-only project must have no `origin` remote. When a worktree has an origin configured, `fm-spawn.sh` fetches it and resets the pooled worktree to `origin/<default>`; `fm-merge-local.sh` advances only local `main`, so every task after the first would start from a stale base. Remove the remote before registering the project; a purely local project created through FirstMate's `project-management` skill has none.

## Named workflows

Every skill except orch-dynamic-workflow is manual-only per the [invocation policy](hosts.md#invocation-policy). The captain runs one when the request names it: by its slash command, or by reading its `SKILL.md` from `<core>/skills/` or the resolved library path. Skills that a running workflow links are read as files.

## What this library does not do

It does not patch `bin/`, `AGENTS.md` or any FirstMate skill. It does not run subagents inside workers. It adds no controller, scheduler, snapshot or client. If a future FirstMate exposes a richer worker interface, these skills change, not FirstMate.
