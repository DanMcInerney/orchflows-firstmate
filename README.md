# orchflows-firstmate

Orchflows' pattern for [FirstMate](https://github.com/kunchenguid/firstmate): fresh agents for Work and Review, two terse composable skills, reusable workflows and layered guidance. FirstMate chooses every agent's harness, model and effort through its normal dispatch and keeps every record; this library supplies the workflow composition.

The installable package is [packages/orchflows-firstmate](packages/orchflows-firstmate/README.md). Install the checkout as a plugin in the harness that runs your FirstMate primary session and add one block to `data/captain.md`. FirstMate's code and dispatch configuration stay unchanged, workers need no plugin, and no example libraries ship: you build workflows by asking. Full steps: [FirstMate integration](packages/orchflows-firstmate/docs/firstmate.md). Existing installations: [upgrade from 0.4 or earlier](packages/orchflows-firstmate/docs/firstmate.md#upgrading-from-04-or-earlier).

| Document | Purpose |
| --- | --- |
| [Plan](docs/plan.md) | Goal, principles, decisions and acceptance for the current design |
| [Handoff](HANDOFF.md) | Status and next steps |
| [Package README](packages/orchflows-firstmate/README.md) | Install and usage |
| [Architecture](packages/orchflows-firstmate/docs/architecture.md) | Primitives, ownership, model and effort, guidance selection |
| [FirstMate mapping](packages/orchflows-firstmate/docs/firstmate.md) | Dispatch owners, checkpoints, delivery modes, durable state |
| [Provenance](packages/orchflows-firstmate/UPSTREAM.md) | Upstream pin and deliberate differences |
| [Live E2E tests](tests/e2e/README.md) | Repeatable WSL scenarios, independent artifact checks and native execution evidence |
| [Routing E2E results](docs/e2e-routing-2026-09-17.md) | 0.5.0 dynamic, authoring and fresh-session reuse results; native resolver omissions retained as failures |
| [End-to-end trial](docs/e2e-trial-2026-09-15.md) | A saved workflow built and run through stock FirstMate, with evidence |
| [Primary trial](docs/e2e-primary-2026-09-15.md) | A model-driven FirstMate primary running the dynamic workflow unprompted |
| [Sync trial](docs/e2e-sync-2026-09-16.md) | The synced library under the invocation policy: dynamic run, a workflow built by name, then run by name |

Upstream Orchflows is synced at `f34f886e72e320ce4da5ddb3d3e06237f13b6d8b`. September 15–16 trials used FirstMate `b182d0f908b78d08c7ccb8dce3775bdca8c5d657` before the routing simplification. The September 17 live suite tested 0.5.0 against stock FirstMate `3eb5b6334a80e06083e3837f0032a5cec39b8e52`: artifact and composition checks passed; strict resolver traces failed. Neither upstream is vendored here. MIT licensed; see [LICENSE](LICENSE).
