Read [HANDOFF.md](HANDOFF.md), then [docs/plan.md](docs/plan.md). The product is the package under `packages/orchflows-firstmate/`; its own [AGENTS.md](packages/orchflows-firstmate/AGENTS.md) governs work inside it.

This library changes nothing in FirstMate. Do not add patches to FirstMate, a controller, a client, native subagents inside workers, or any runtime this package would own. FirstMate owns agents, worktrees, steering, recovery and delivery. Build on FirstMate and never duplicate what it owns: agents, worktrees, steering, records, delivery. Keep skills terse and link to docs rather than restating them. Keep upstream guidance byte-identical unless a trial shows a defect. No example libraries ship here.

`archive/`, `.sources/` and `.scratch/` are ignored local research copies: the retired dev.1 through dev.9 line and the upstream sources. Read them for evidence, not direction, and leave them unchanged.

Run `python -B -m unittest discover -s packages/orchflows-firstmate/tests` before claiming a change works.
