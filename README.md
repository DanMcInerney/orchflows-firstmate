# orchflows-firstmate

Standalone Orchflows variant for **FirstMate running on Herdr**, with Claude
Code and Codex CLI as worker harnesses. The target is near feature parity with
Orchflows through FirstMate's existing agent, workspace, communication, recovery,
supervision and delivery owners.

The current owned package is **0.1.0-dev.7**, retaining all 1,081 source paths at
Orchflows ca72258493480ddcfe73b3f01d0475ad532e4726 (0.7.0). The experimental
design-loop library remains inactive migration source and is not used.

**Current increment:** an explicitly selected ordinary Linux ship/local-only
root can compose Work, join committed results, request one fresh Review of the
exact clean joined candidate, make one repair/check pass, and deliver its
ordinary ready branch. FirstMate's existing local merge and teardown owners
protect that delivery. Dynamic scouts and retained legacy clients preserve
their previous contracts. See [local delivery](docs/local-delivery.md) and
[current verification](docs/local-delivery-verification.md).

Enable the fork and selected complete custom libraries once; select dynamic
through ordinary FirstMate spawn. The retained package client uses immutable
launch context. FirstMate alone owns every component and Herdr endpoint.
No global installation is performed by package checks.

**Start with [HANDOFF.md](HANDOFF.md).** Develop and verify inside Ubuntu/WSL,
with disposable candidates and homes on the Linux filesystem. The shared
repository is the edit source; native Windows is deferred. The development
workflow is the pinned upstream Orchflows dynamic workflow: scoped makers,
joined checks, one fresh independent Review and one repair/check pass.

The owned source is [packages/orchflows-firstmate](packages/orchflows-firstmate/README.md).
Direct-PR/no-mistakes delivery, nesting, Build/SelfImprove, broader custom/meta
and optional-library execution, current Codex runtime evidence and release
installation/update/rollback remain open. Source coverage and package checks
are distinct from actual fleet execution.

| Document | Purpose |
| --- | --- |
| [Handoff](HANDOFF.md) | User intent, next assignment, expected outputs and completion criteria |
| [Fundamental design](docs/fundamental-design.md) | Selected architecture, required FirstMate changes, staged implementation and fixed runtime acceptance |
| [Local delivery verification](docs/local-delivery-verification.md) | Current delivery checks, independent Review and actual worker evidence |
| [Dynamic verification](docs/dynamic-verification.md) | Historical dev.6 scout composition, workers, review and repair evidence |
| [Review verification](docs/review-verification.md) | Historical bounded Review and recovery evidence |
| [Linux acceptance driver](docs/linux-acceptance.md) | Reproduce private Claude Work/Review and parent-replacement trials |
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

Status: experimental bounded Linux dynamic integration for scouts and explicitly
selected ship/local-only roots. [Current verification](docs/local-delivery-verification.md)
records exactly what was checked and run; it is not a general release or full
feature-parity claim.

The initial evidence dates to September 13, 2026 (America/New_York). Refresh version-sensitive facts before designing against current upstreams, retaining the pinned baseline for comparison.

The earlier native-crewmate comparison is retained as research. The user's standalone, FirstMate/Herdr-only parity requirement supersedes that narrower recommendation. The current design replaces native child handles with FirstMate component handles and requires explicit task-group, result-retention, review-policy and recovery contracts.

The requested full Orchflows source copy is at `.sources/orchflows/`, including Git history, tests and examples, at `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a` (0.7.0). A full FirstMate research clone is at `.sources/firstmate/`, at the unchanged baseline `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`. Both are ignored local copies; they are not added to this repository's tracked source or installed into a host. See the source refresh to reproduce them elsewhere.
