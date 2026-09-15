# FirstMate

This library runs Orchflows' pattern with FirstMate's own agents. The FirstMate primary session loads these skills and is the coordinator; every Work and Review is an ordinary crewmate or scout dispatched through `bin/fm-brief.sh` and `bin/fm-spawn.sh`. Nothing in FirstMate is patched. Workers need no plugin: their briefs carry absolute guidance and reference paths, which they read as files.

## Install

1. Install this package into the harness that runs your FirstMate primary session, per [hosts](hosts.md#register-and-refresh), and run `python scripts/orchflows.py setup` once to create `~/.orchflows-firstmate` for your own libraries.
2. Append the block below to `$FM_HOME/data/captain.md`. FirstMate prints that file in every session-start digest.
3. Optionally add the role defaults below to `$FM_HOME/config/crew-dispatch.json`. FirstMate's bootstrap validates the file, and its quota ranker applies to any profile array.
4. Register `~/.orchflows-firstmate` as a `local-only` FirstMate project so [orch-build-workflow](../skills/orch-build-workflow/SKILL.md) can ship saved workflows into it.

Start a new FirstMate session. A remote secondmate needs steps 1 and 4 on its own host; secondmates inherit `captain-shared.md` rather than `captain.md`, so put the block there when they should follow it.

### captain.md block

```markdown
## Orchflows
- Run every ship and scout through orch-dynamic-workflow unless I name another workflow or say "plain". Run a custom workflow only when I name it.
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
| Work, a change | `fm-brief.sh <id> <repo> --mode <mode>`, then `fm-spawn.sh <id> <project> --mode <mode> --yolo <on\|off> --harness H --model M --effort E` |
| Work, read-only | `fm-brief.sh <id> <repo> --scout`, then `fm-spawn.sh <id> <project> --scout --harness H --model M --effort E` |
| Review | a scout whose brief names the candidate branch, PR or commit and asks for a detached checkout, the Review sections, and findings only |
| Assignment and guidance | the brief's `## Firstmate spec`: assignment, input state, absolute guidance paths, checks, and "read and apply the Make sections" or "the Review sections" |
| Wait | FirstMate's watcher; the captain acts on `done`, `needs-decision` and report events |
| Repair | `fm-send.sh` with the findings; `fm-control.sh <id> relaunch --model M --effort E` when the fixer's profile differs; or a fresh Work |
| Deliver | the project's delivery mode and merge authority, unchanged |
| State | backlog item note: `orchflows: <workflow> phase=<plan\|work\|review\|repair\|deliver> work=<ids> review=<id> repair=<id> guidance=<domains>` |

The brief's captain's-intent section keeps the captain's words; Orchflows context belongs in the Firstmate spec. A worker never sees this library's skills; it sees its assignment and the guidance files named in its brief. A reviewer checks the candidate out detached (`git checkout --detach <ref>`, or `gh pr checkout` for a PR) in the scratch worktree FirstMate allocated.

## Delivery modes

| Mode | Review placement | Repair | Landing |
| --- | --- | --- | --- |
| `no-mistakes` | after the maker's implementation commit, before FirstMate triggers validation | steer the maker, then trigger `/no-mistakes` on the same worker | no-mistakes owns review, fixes, push, PR and CI from that point; dispatch nothing else into it |
| `direct-PR` | on the opened PR | steer the maker; it updates the PR | merge authority as configured |
| `local-only` | on `fm/<id>` after `done: ready in branch` | steer the maker; it updates the branch | `fm-merge-local.sh` after captain approval |
| scout only | on the report | steer the scout or dispatch a fresh scout | the report is the deliverable |

In `no-mistakes` projects the pattern reviews twice. When one review is enough, say so in the request and the dynamic workflow treats no-mistakes as its Review.

Stock FirstMate's captain contract prefers not to add an independent reviewer on the fast paths. The `captain.md` block is the captain's standing request for one; keep it there rather than arguing case by case.

## Manual-only workflows

See [hosts](hosts.md#manual-only-workflows). The captain runs a custom workflow only when the request names it, by reading its `SKILL.md` from the resolved library path.

## What this library does not do

It does not patch `bin/`, `AGENTS.md` or any FirstMate skill. It does not run subagents inside workers. It adds no controller, scheduler, snapshot or client. If a future FirstMate exposes a richer worker interface, these skills change, not FirstMate.
