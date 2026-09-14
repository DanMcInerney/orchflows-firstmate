# Integration solution options

**Historical scope:** this comparison preceded the user's request for a standalone FirstMate/Herdr-only variant with near feature parity. The current plan is [fundamental-design.md](fundamental-design.md), with [feature-parity.md](feature-parity.md) preserving the full feature target. The narrow native-crewmate recommendation below remains evidence, not the selected product architecture.

Research continuation: September 13, 2026 (America/New_York). This is a design proposal, not an implemented or approved integration. Read the [source findings](firstmate-contracts.md), [Orchflows findings](orchflows-contracts.md), and [evidence ledger](evidence.md) alongside it.

## Recommended direction

**Make Orchflows an optional way for a FirstMate crewmate to perform its assignment. FirstMate keeps responsibility for the fleet and delivery.** Prove this first through an explicit task brief using complete, pinned package roots; then consider a small, generic worker-workflow attachment contract in FirstMate and a separate Orchflows compatibility library.

This advances the earlier recommendation in three ways: native plugin registration need not block the first experiment; the dependency graph, rather than just a version string, must survive restart; and the first compositions should have one level of native children with tightly bounded write access. These are proposed constraints. No FirstMate-launched native child has been tested here.

The intended eventual experience is: install the compatibility package, explicitly enable a profile for selected assignments, continue using ordinary FirstMate requests, and update the default for new tasks while existing tasks retain their recorded package identity. Calling this plug-and-play requires the acceptance probes in [experiment-plan.md](experiment-plan.md), including failure and restart cases. A manual demonstration alone does not meet that standard.

## Compare the alternatives

Ranks reflect fit to that proposed experience, not measured quality or cost. They change if the user prioritizes independent fleet visibility for every child or prefers guidance reuse alone.

| Option | What it delivers | Changes needed | Main drawback / counterevidence | Rank / use |
| --- | --- | --- | --- | --- |
| A1. Explicit package roots in an ordinary brief | One crewmate follows a named composition from complete local core/library copies | Task instructions and preparation of those copies; potentially no upstream code change for a bounded trial | Instructions still need native tools; package-path visibility, status discipline and restart behavior remain unproven | Best first experiment; not automatic integration |
| A2. Host-native plugin invocation | Same task-level result with discoverable skill names | Register complete core/library packages in the actual worker's host configuration | User plugins, project settings, caches, duplicate skill names and remote homes can differ from the supervisor session | Useful comparison against A1 |
| B. Optional worker profile plus compatibility library | Reusable workflow selection, preflight, durable attachment, predictable upgrades | Small FirstMate selection/brief/lifecycle seam; external Orchflows library and package preparation | Can quietly become a second scheduler unless scope stays narrow; unknown child lifetime is a release blocker for unattended restart | 1, provisional product recommendation |
| D. Guidance-only attachment | Domain knowledge and task instructions without Orchflows Work/Review delegation | Complete resources supplied through existing brief, or the same optional attachment seam | Does not supply independent native Work/Review or workflow execution | 2, useful fallback product only if explicitly selected |
| C. Fleet-backed workflow composition | Every maker/reviewer is a separately supervised FirstMate task | FirstMate-oriented composition with task joins, artifact transfer, cross-worktree integration and cancellation | Conflicts with substituting fleet tasks for the existing native-child Work/Review contract; durable joins add substantial machinery | 3; pursue if fleet visibility is essential or native lifetime proves insufficient |
| E. Replace FirstMate supervision with Orchflows | One orchestration layer becomes the fleet controller | Rebuild or transfer FirstMate's durable authority, delivery and recovery contracts | Orchflows deliberately supplies instructions above host execution, with no scheduler; this removes the clearest benefit of FirstMate | Do not pursue for this scope |

For C, a separate FirstMate-specific composition could preserve Orchflows core unchanged and reuse guidance. It must be described honestly as a fleet composition, not an implementation of native `orch-work` merely because both delegate. Its review deliverable still needs FirstMate authorization. The smaller variant uses one existing fleet task per coarse phase and stores a report between phases; compare that before inventing a general graph executor.

Orchflows explicitly supports supplied roots and distinguishes reading a skill from registering it. FirstMate already separates human intent from its execution specification. Those contracts support A1 as an experiment, not as demonstrated interoperability. [Orchflows architecture](https://github.com/DanMcInerney/orchflows/blob/0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a/docs/architecture.md), [FirstMate brief composition](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-brief.sh#L340-L366).

## Ownership and attachment

| Concern | Proposed owner | Boundary |
| --- | --- | --- |
| Assignment, task kind, delivery mode, merge authority | FirstMate intake and current lifecycle | Workflow selection grants no additional project or delivery authority |
| Profile selection, installed identity, launch checks | FirstMate attachment seam | Resolve before launch; record effective worker profile after dispatch resolution |
| Workflow decisions and domain guidance | External Orchflows compatibility library | Calls unchanged Work/Review where the selected policy permits them |
| Native children and their tools | Actual worker harness | Certification applies to that launch/configuration, not its product name |
| Join, steering, child shutdown, result provenance | Crewmate | Children return results to the crewmate; only the crewmate reports to FirstMate |
| Durable package identity and outer task metadata | FirstMate home | Host-local paths are resolved from identity; remote machines provision independently |
| Outputs and candidate files | Authorized task workspace / existing report destination | No writes into packages; child output is collected before completion or teardown |

For the manual trial, put workflow selection, resolved roots and boundaries in `## Firstmate spec`. Keep the user's original request in `## Captain's intent`; do not add bridge mechanics to the no-mistakes acceptance intent. Do not edit only `launch-brief.md`: launch/relaunch regenerates it. FirstMate's current process-event extensions explicitly exclude instruction injection and worker-launch grants. Reusing their general idea of pinned packages is reasonable; pretending they already expose workflow hooks is not. [Intent and role owner](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-dod-lib.sh#L13-L38), [extension scope](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/extension-bindings.md#scope-and-design).

For B, prefer a generic optional workflow attachment over adding Orchflows-specific conditions throughout dispatch. The proposed resolved task record identifies: profile and contract version; task/workflow identity; full core and library digests; selected guidance order; task kind and review authorization; effective worker harness/model/effort; native child/depth limits; allowed input/output roots; and restart policy. Separate immutable assignment facts from a small mutable checkpoint. These are conceptual fields, not a supported schema or CLI.

## Resolve each friction point

| Friction | Proposed solution | Required limit or disproof test |
| --- | --- | --- |
| Supervisor bypass | Attach only to ordinary crewmates. Never route FirstMate primary/secondmate work through native Orchflows children | Verify selected supervisor enforcement separately; native-child exemption is harness-scoped evidence |
| Automatic extra review | Use a distinct work-only composition for normal ship tasks; select independent review only for an explicitly authorized review deliverable | Do not weaken `orch-dynamic-workflow` by silently deleting its final review |
| Workflow discovery | First trial uses explicit full-package roots; later compare native registration | Reading a file does not activate a plugin, and an available skill name does not prove package identity |
| Generic fallback in the wrong role | Explicitly choose the compatibility entrypoint and pass leaf assignments to children | Installing a dynamic fallback globally must not change supervisor policy or cause recursive composition |
| Host mismatch or missing dependencies | Preflight the final dispatched worker, package graph and effective controls | Refuse or route only to an already authorized compatible profile; never silently label ordinary execution an Orchflows run |
| Native nesting and resource multiplication | Start with a top-level crewmate spawning leaf children; one child at a time in the first probe | Do not assume every library composition flattens; certify depth, native limits and child shutdown for each supported profile |
| Shared workspace edits | Initial review probe has read-only children; first ship composition has one active writer | Parallel writers and child worktrees require a later ownership/integration/cleanup contract |
| FirstMate self-development | Exclude from the initial supported profile | Current appended role contract expressly forbids delegation; a brief-only exception does not solve this |
| Steering and cancellation | Parent receives and acknowledges FirstMate control, propagates changes, then records the generation used by collected results | Receipt by the parent is not proof children received or obeyed it; invalidate stale results |
| Completion | Aggregate only at the parent, with mode-specific status rules | Implementation done and CI-ready done are distinct; child completion emits neither |
| Crash/relaunch | Keep a compact parent checkpoint and reconcile actual child ownership before replacement work | If old children may still write and cannot be stopped or proven dead, block; a transcript or checkpoint is not process control |
| Scout promotion | Make workflow selection stage-specific and replay the accepted ship contract on subsequent relaunch | Initial profile excludes promotion; use a separately authorized ship task until stage-aware replay is proven |
| Exact review candidate | Record a commit, or HEAD plus staged/unstaged patch identity and relevant untracked-file digests | Freeze during review. Repairs create a new candidate; report what was reviewed and what changed afterward |
| Package updates | Retain immutable complete dependency snapshots and switch the default only for new tasks | A semantic version alone does not identify edited libraries; copying core alone does not freeze later home resolution |
| Remote homes | Inherit portable selection policy, then resolve/install/verify locally on each host | Environment allowlisting is not provisioning and caller paths are not portable |
| Non-code deliverables | Start with standalone text review reports; put material needed after teardown in the retained report | Media and editable multi-file projects require an explicit retained artifact destination; default scout scratch is disposable |
| Maintenance | Keep bridge instructions outside managed caches, with a small FirstMate contract and targeted compatibility probes | No automatic support claims for new upstream revisions without rerunning affected probes |

The FirstMate review restriction applies across no-mistakes and faster modes. A named review deliverable is the existing exception. For no-mistakes, a work-only composition ends at the existing implementation handoff; the same crewmate then follows the pipeline owner. Do not introduce a general delivery-provider API just to resolve this conflict. [Delivery policy](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/AGENTS.md#L336-L368), [dynamic workflow](https://github.com/DanMcInerney/orchflows/blob/0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a/skills/orch-dynamic-workflow/SKILL.md).

## Install, upgrade and recovery design

Separate three checks: complete package availability; actual worker loading and native tools; FirstMate policy/lifecycle compatibility. The existing Orchflows `doctor` addresses package structure. Its readiness result does not certify the latter two. Existing setup swaps a mutable managed core and refreshes catalogs; it does not retain a task's entire dependency graph or coordinate host caches. [Home contract](https://github.com/DanMcInerney/orchflows/blob/0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a/docs/home.md).

A proposed installation prepares a complete package set, verifies identities and dependencies, runs the appropriate worker smoke, and publishes an opt-in profile only after success. Keep `--skip-host-config` when using existing setup so ordinary installation does not silently change the user's concurrency. Do not copy authentication into snapshots or package manifests.

The first profiles should admit a small, explicitly inventoried dependency set. Orchflows library dependencies are currently prose, so automatic discovery and locking of arbitrary libraries would be additional scope; do not hide that work inside the word “resolve.”

A proposed update stages a new package set beside the old one and verifies it before switching the default. Running tasks retain their recorded roots and dependencies. Recovery either reconnects under that identity or explicitly restarts within it after old children have been reconciled. Disable prevents new selections; it does not remove files or dependencies still referenced by tasks. Rollback restores the previous default, without mutating active tasks. The exact storage, activation and garbage-collection implementation remains to be selected.

FirstMate already has a richer immutable package pattern in its process-event subsystem. Study that ownership model, but avoid copying the entire executable-extension machinery into a Markdown-only bridge without demonstrated need. A profile should remain an inspectable task attachment, not a new scheduler.

Upstream maintenance also has a concrete cost: FirstMate's contribution document requires its no-mistakes submission path and a current-head structured attestation, and identifies the owners of targeted lint/test and documentation checks. A future upstream patch must budget for that process. This is an inspected contribution contract, not evidence that maintainers accept the proposed seam. [FirstMate contribution policy](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/CONTRIBUTING.md#L5-L28).

## What would change the recommendation

- If real native children cannot be observed/stopped reliably after parent death, narrow B to bounded read-only work or promote C's coarse fleet-task composition.
- If explicit package roots fail under actual worker permissions or dependency resolution, certify native registration before proceeding; do not treat it as a drop-in substitute without testing.
- If guidance-only use matches the useful outcomes at lower operator cost, prefer D for those task types and reserve B for work benefiting from independent execution/review.
- If every child must appear as a fleet member, choose C explicitly and account for worktree joins, status routing and review policy in its scope.
- If FirstMate upstream does not want a generic seam, keep A as a documented local profile rather than maintain an invasive fork.

No quality, speed, token, or cost improvement has been measured. The [experiment plan](experiment-plan.md) includes a comparison that can establish whether the additional composition is worth operating.
