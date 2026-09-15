# orchflows-firstmate

Orchflows' pattern for [FirstMate](https://github.com/kunchenguid/firstmate): fresh agents for Work and Review, two terse composable skills, reusable workflows with optional model and effort per agent. FirstMate launches every agent exactly as it does today; this library only changes the pattern the first mate follows.

The installable package is [packages/orchflows-firstmate](packages/orchflows-firstmate/README.md). Install it into the harness that runs your FirstMate primary session, add one block to `data/captain.md`, and optionally two rules to `config/crew-dispatch.json`. No FirstMate file is patched and workers need no plugin. Full steps: [FirstMate integration](packages/orchflows-firstmate/docs/firstmate.md).

| Document | Purpose |
| --- | --- |
| [Plan](docs/plan.md) | Goal, principles, decisions and acceptance for the current design |
| [Handoff](HANDOFF.md) | Status and next steps |
| [Package README](packages/orchflows-firstmate/README.md) | Install and usage |
| [Architecture](packages/orchflows-firstmate/docs/architecture.md) | Primitives, ownership, model and effort, guidance selection |
| [FirstMate mapping](packages/orchflows-firstmate/docs/firstmate.md) | Commands, checkpoints, delivery modes, durable state |
| [Provenance](packages/orchflows-firstmate/UPSTREAM.md) | Upstream pin and deliberate differences |
| [Archived research](archive/research/README.md) | The retired dev.1 through dev.9 component-engine line and its evidence |

Upstream Orchflows is pinned at `ca72258493480ddcfe73b3f01d0475ad532e4726`; FirstMate was studied at `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`. Neither is vendored here.
