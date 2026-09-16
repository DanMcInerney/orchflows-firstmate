# orchflows-firstmate

Orchflows' pattern for [FirstMate](https://github.com/kunchenguid/firstmate): fresh agents for Work and Review, two terse composable skills, reusable workflows with optional model and effort per agent. FirstMate launches every agent exactly as it does today and keeps every record; this library only changes the pattern the first mate follows and never duplicates what FirstMate owns.

The installable package is [packages/orchflows-firstmate](packages/orchflows-firstmate/README.md). Install the checkout as a plugin in the harness that runs your FirstMate primary session, add one block to `data/captain.md`, and optionally two rules to `config/crew-dispatch.json`. No FirstMate file is patched, workers need no plugin, and no example libraries ship: you build workflows by asking. Full steps: [FirstMate integration](packages/orchflows-firstmate/docs/firstmate.md).

| Document | Purpose |
| --- | --- |
| [Plan](docs/plan.md) | Goal, principles, decisions and acceptance for the current design |
| [Handoff](HANDOFF.md) | Status and next steps |
| [Package README](packages/orchflows-firstmate/README.md) | Install and usage |
| [Architecture](packages/orchflows-firstmate/docs/architecture.md) | Primitives, ownership, model and effort, guidance selection |
| [FirstMate mapping](packages/orchflows-firstmate/docs/firstmate.md) | Commands, checkpoints, delivery modes, durable state |
| [Provenance](packages/orchflows-firstmate/UPSTREAM.md) | Upstream pin and deliberate differences |
| [End-to-end trial](docs/e2e-trial-2026-09-15.md) | A saved workflow built and run through stock FirstMate, with evidence |
| [Primary trial](docs/e2e-primary-2026-09-15.md) | A model-driven FirstMate primary running the dynamic workflow unprompted |
| [Sync trial](docs/e2e-sync-2026-09-16.md) | The synced library under the invocation policy: dynamic run, a workflow built by name, then run by name |
| [Archived research](archive/research/README.md) | The retired dev.1 through dev.9 component-engine line and its evidence |

Upstream Orchflows is synced at `f34f886e72e320ce4da5ddb3d3e06237f13b6d8b`; FirstMate was studied at `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`. Neither is vendored here. MIT licensed; see [LICENSE](LICENSE).
