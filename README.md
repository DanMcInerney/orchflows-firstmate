# orchflows-firstmate

Standalone Orchflows variant for **FirstMate running on Herdr**, with Claude Code and Codex CLI as worker harnesses. The target is near 1:1 feature parity with Orchflows, with revised execution and lifecycle ownership.

**Start with [HANDOFF.md](HANDOFF.md).** It contains the next-session assignment and reading order. No memory of the original conversation is required.

The selected design keeps workflow composition in a root crewmate and turns Work/Review into requests for FirstMate-owned component tasks. FirstMate owns every Herdr endpoint, task lifecycle and outer delivery gate. The first implementation adds one experimental read-only Work component; broader composition and feature parity remain staged work.

The owned source is [packages/orchflows-firstmate](packages/orchflows-firstmate/README.md). Package isolation and execution gating are the first implementation step; standalone execution outside FirstMate is not a supported mode. Normal Orchflows is not a runtime dependency.

| Document | Purpose |
| --- | --- |
| [Handoff](HANDOFF.md) | User intent, next assignment, expected outputs and completion criteria |
| [Fundamental design](docs/fundamental-design.md) | Selected architecture, required FirstMate changes, staged implementation and fixed runtime acceptance |
| [Feature parity](docs/feature-parity.md) | Every core feature and optional library, retained source versus migrated behavior |
| [Native worker trials](docs/stage1-native-trial.md) | Actual Codex/Claude attempts, retained result identities and runtime gaps |
| [Windows runtime boundary](docs/stage1-windows.md) | Implemented shell/path/lock boundary and remaining native worker acceptance |
| [Native Windows probes](docs/stage1-windows-native.md) | Real Herdr/Treehouse results, detached-process failure and required owner changes |
| [Acceptance continuation](docs/stage1-acceptance-continuation.md) | Corrected authentication design, Claude work and actual watcher observations |
| [Continuation verification](docs/stage1-continuation-verification.md) | Launch-custody repair, Windows admission/retention guards and combined checks |
| [Stage 1 verification](docs/stage1-verification.md) | Implemented scope, current checks and unresolved acceptance |
| [Stage 1 contract](docs/stage1-contract.md) | Current request, launch, result and lifecycle implementation boundaries |
| [Runtime preparation](docs/stage1-runtime.md) | Exact isolated Herdr and harness prerequisites, with executed evidence separated from claims |
| [FirstMate integration](integrations/firstmate/README.md) | Prepare the pinned experimental FirstMate candidate and run its checks |
| [Foundation verification](docs/foundation-verification.md) | Exact implemented scope, baseline/candidate checks and remaining runtime gaps |
| [Original assessment](docs/assessment-2026-09-13.md) | Preserved research report with commit-pinned primary sources |
| [Evidence and completed work](docs/evidence.md) | What was inspected, actually tested, independently reviewed, and left untested |
| [Open questions](docs/open-questions.md) | Prioritized uncertainties and evidence needed to resolve them |
| [Candidate approaches](docs/options.md) | Competing architectures and a first experiment for each |
| [Decision log](docs/decisions.md) | Established scope, provisional recommendations and future decisions |
| [Source manifest](docs/source-manifest.json) | Exact revisions and hashes for source verification |
| [Solution options](docs/solution-options.md) | Expanded architecture comparison, provisional ranking and friction remedies |
| [FirstMate contracts](docs/firstmate-contracts.md) | Briefs, metadata, promotion, lifecycle, environment and artifact source traces |
| [Orchflows contracts](docs/orchflows-contracts.md) | Complete packages, explicit roots, host limits, dependency snapshots and updates |
| [Experiment plan](docs/experiment-plan.md) | Fourteen bounded acceptance and failure probes; not yet run |
| [Proposed first increment](docs/proposed-increment.md) | Manual feasibility gate, then a bounded optional worker profile |
| [Source refresh](docs/source-refresh-2026-09-13.json) | Current clone identities, baseline blob verification and local host inventory |

Status: experimental Stage 1 with actual Claude and Codex Work results in WSL, including earlier Codex parent-replacement/gather evidence. The current 81-case integration suite passes with recorded platform skips. The repaired real Claude trial passed 345 seconds of uninterrupted ordinary watcher supervision, full reads before gather, root delivery and cleanup. Launch supervision uses live FirstMate transaction custody. Native Windows probes passed Herdr/Treehouse primitives but exposed a detached-process cleanup gap, so actual Windows workers now refuse until native custody is implemented. Only one read-only Work component is admitted; Review, writers, nesting and optional-library execution remain gated. This is not yet a plug-and-play release.

The initial evidence dates to September 13, 2026 (America/New_York). Refresh version-sensitive facts before designing against current upstreams, retaining the pinned baseline for comparison.

The earlier native-crewmate comparison is retained as research. The user's standalone, FirstMate/Herdr-only parity requirement supersedes that narrower recommendation. The current design replaces native child handles with FirstMate component handles and requires explicit task-group, result-retention, review-policy and recovery contracts.

The requested full Orchflows source copy is at `.sources/orchflows/`, including Git history, tests and examples, at `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a` (0.7.0). A full FirstMate research clone is at `.sources/firstmate/`, at the unchanged baseline `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`. Both are ignored local copies; they are not added to this repository's tracked source or installed into a host. See the source refresh to reproduce them elsewhere.
