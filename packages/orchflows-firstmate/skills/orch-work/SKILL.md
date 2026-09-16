---
name: orch-work
description: Dispatch a fresh FirstMate agent to make a requested result with relevant guidance.
disable-model-invocation: true
---

Reuse supplied guidance context or establish it per the [selection rule](../../docs/architecture.md#guidance-selection). Dispatch one fresh FirstMate agent per assignment through the ordinary brief and spawn owners: a ship in the project's delivery mode for a change, a scout for investigation or any read-only result. Apply the assignment's [model and effort](../../docs/architecture.md#model-and-effort) as explicit spawn flags.

Put the assignment, intended workspace and input state, resolved guidance paths and scoped caller choices in the brief; instruct the worker to read and apply the Make sections, to work alone without delegating, and to commit before reporting. Record the task ID and its role in the backlog item note. FirstMate's watcher, steering, recovery and delivery apply unchanged; the [FirstMate mapping](../../docs/firstmate.md) records the exact commands and checkpoints.
