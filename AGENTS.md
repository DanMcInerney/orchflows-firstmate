Read [HANDOFF.md](HANDOFF.md), then [docs/plan.md](docs/plan.md). The product is the package under `packages/orchflows-firstmate/`; its own [AGENTS.md](packages/orchflows-firstmate/AGENTS.md) governs work inside it.

This library changes nothing in FirstMate. Do not add patches to FirstMate, a controller, a client, native subagents inside workers, or any runtime this package would own. FirstMate owns agents, worktrees, steering, recovery and delivery. Keep skills terse and link to docs rather than restating them. Keep upstream guidance and example libraries byte-identical unless a trial shows a defect.

`archive/research/` is the retired dev.1 through dev.9 line. Read it for evidence, not direction. `.sources/` and `.scratch/` are ignored local research copies; leave them unchanged.

Run `python -B -m unittest discover -s packages/orchflows-firstmate/tests` before claiming a change works.
