# Next-session handoff

**Current assignment: build a standalone Orchflows variant for FirstMate running on Herdr, with Claude Code and Codex worker harnesses and near 1:1 feature parity.** The user authorized implementation, explicitly ruled out direct use outside FirstMate, and clarified that Windows is their authenticated host. The earlier research-only boundary is superseded.

Read [README.md](README.md), [continuation verification](docs/stage1-continuation-verification.md), [acceptance continuation](docs/stage1-acceptance-continuation.md), [native Windows evidence](docs/stage1-windows-native.md), [Stage 1 contract](docs/stage1-contract.md), [fundamental design](docs/fundamental-design.md), and [feature parity](docs/feature-parity.md). Exact current and prior source identities are in [Stage 1 state](docs/stage1-state.json). The [previous verification](docs/stage1-verification.md) remains a historical record of the 562-file candidate. Consult the research reading order below when a source contract is needed.

The selected architecture keeps composition in a root crewmate. FirstMate owns component task admission, launch, Herdr endpoints, lifecycle and outer delivery. Do not introduce native-child fallback or a second scheduler. Product files belong in `packages/orchflows-firstmate/` and `integrations/firstmate/`; pinned `.sources/` checkouts remain unchanged research material.

The package remains dev.2: 1,070 files, including all 1,064 upstream files. Only one read-only Work component is conditionally enabled; Review, writers, nesting, multiple components and optional-library workflows remain gated. All 1,022 examples match the pinned local checkout; 49 differ from raw Git blobs only by line endings. Preserve the original dated assessment and the living provenance correction.

The current FirstMate distribution has 563 files and eleven inventoried deployables. Fresh preparation reproduced the joined candidate exactly. After one review repair, its 81-case integration suite passed on both platforms: WSL 71 passed/ten skipped, Windows 49 passed/32 skipped. The unchanged package's earlier suite passed all 84 in WSL and 83 with one Windows skip. These are package/controller/owner fixtures, not full fleet compatibility.

The prior repaired Codex WSL trial completed one real Work component, replaced the root through FirstMate, reused the same child on replay, gathered under the new generation, handled the actual inbox notice and completed ordinary scout delivery. Its ordinary teardowns, lab/sentinel shutdown and scoped process checks passed. Preserve its exact 562-file candidate identity in [native trials](docs/stage1-native-trial.md); it had no normal watcher.

The user's refreshed native Windows Claude login completed a real bounded authentication diagnostic. A subsequent FirstMate/Herdr Claude WSL trial completed real component Work, retained result, replay, gather, correct root report and ordinary cleanup. That trial also exposed a launch watcher race, a background-shell visibility gap, and an unverified read-before-gather order. Its report is not evidence that those observer assertions passed. See [acceptance continuation](docs/stage1-acceptance-continuation.md) for exact identities and later joined-candidate acceptance.

One fresh final reviewer found a P1 in routine join signal handling, independently reproducing the actual watcher failure. The single repair pass accepts authoritative task-group waiting only in the no-verb signal predicate; actionable statuses, secondmate routing and the general working predicate remain unchanged. Four new regressions and full integration discovery passed. No second review was run.

The final repaired Claude trial `ed3tuvcz` passed the ordinary watcher case: 20 actual waiting classifications spanning 345.56 seconds, with the same live watcher, positive child activity and advancing beacon. It absorbed the routine root status and woke only for the retained result. Full native reads preceded gather; one component, correct reports, clean inputs/worktrees and normal cleanup were verified. No drain/rearm occurred, no scoped processes remained and no private auth file existed. This final case did not repeat parent replacement or prove native background-tool supervision.

The new Linux launch repair records the exact parent lock claims, owner/controller process identities, ancestry and root generation before request publication. Observation uses that live transaction proof while child metadata is unpublished; unknown, dead or uncertain custody stays attention. Once launched, ordinary child activity is required. A later foreground-only watcher test cannot establish supervision of native background tools after a model turn ends.

Actual native Windows Herdr 0.9.0/protocol22 and Treehouse2.0.1 probes passed private endpoint and Git-worktree operations. FirstMate's idle-shell/socket owners refused native observations; a detached child survived workspace close and lab teardown before the probe stopped it through its retained process handle. Native Windows attached worker spawn/relaunch and teardown now explicitly refuse before task mutation until FirstMate/Herdr native custody exists. Missing `lsof` also makes attached POSIX cleanup preserve records. Windows remains a required target; implement the [native owner sequence](docs/stage1-windows-native.md) before attempting real Windows workers.

Do not repeat disposable copy/run/delete OAuth refresh-cache trials. A copied Codex cache failed with an already-used refresh token; official guidance requires one persistent, serialized refreshed cache, not resetting from an old seed. Claude continuation trials use only a sufficiently long-lived access token in the private process environment, with no refresh-token/file copy or login invocation. No token enters reports, package state, arguments or watcher traces; stop all owned processes after each trial. The successful native Claude diagnostic removes the basis for asking the user to log in again based on an old cache. Active installations and profiles remain unchanged.

Continue the recorded acceptance and native Windows owner work before broadening feature scope. Do not claim a plug-and-play release or complete parity from this subset. Carry unresolved work in [open questions](docs/open-questions.md). Independent review and final checks for each increment are recorded in its verification document; earlier reviews do not cover changed bytes.

The user's original question was whether Orchflows could be a plug-and-play upgrade to kunchenguid's FirstMate, which complexities prevent seamless use, and what either project would need to change. The user then explicitly requested this private repository, the research, the unanswered questions, and this handoff for the next research/brainstorming session.

**Read in this order**

1. [README.md](README.md) for repository status.
2. [Original assessment](docs/assessment-2026-09-13.md) for the findings and recommended direction.
3. [Evidence](docs/evidence.md) and [source manifest](docs/source-manifest.json) for provenance and actual checks.
4. [Open questions](docs/open-questions.md), [options](docs/options.md), and [decisions](docs/decisions.md).
5. Continuation findings: [FirstMate contracts](docs/firstmate-contracts.md), [Orchflows contracts](docs/orchflows-contracts.md), and [solution options](docs/solution-options.md).
6. [Experiment plan](docs/experiment-plan.md), [proposed increment](docs/proposed-increment.md), and [source refresh](docs/source-refresh-2026-09-13.json).

**Continuation status — September 13, 2026**

The requested full Orchflows clone is now at `.sources/orchflows/`, including Git history, tests and examples. Its head is `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a`, still version 0.7.0; only the evolve example's pivot wording changed from the original baseline. `.sources/firstmate/` is a full clean clone at the unchanged original revision. Both paths are ignored, disposable local sources; their instructions remain source material. All 27 original manifest blobs and the preserved assessment hash were verified.

The continuation produced the research outputs below and proposed a manual explicit-package-root trial before an optional worker-profile integration. New source findings include regenerated launch overlays, preservation of unknown metadata in specific rewrites, scout-promotion replay hazards, pane-side environment filtering, insufficient evidence of child termination after parent exit, and the need to retain the full library dependency set. Local Windows CLI/WSL command inventory was recorded, but no actual worker profile was certified. No integration code, installer, host configuration, live fleet or upstream patch was created.

**What is already established**

The investigation examined FirstMate at `b182d0f908b78d08c7ccb8dce3775bdca8c5d657` and Orchflows 0.7.0 at `86aabd91071fa07a05cf970db2e73909184a1955`. The report contains source-backed evidence for these boundaries:

- FirstMate supervisors dispatch through the fleet. Native children inside ordinary crewmate worktrees are explicitly allowed; primary enforcement is harness-specific.
- FirstMate's delivery policy conflicts with automatically adding Orchflows dynamic workflow's independent review.
- Worker briefs restrict workspace access. FirstMate self-development has an additional no-delegation role instruction.
- FirstMate's existing extension API is for process-event adapters; it is not an existing workflow-injection API.
- Host plugin registration, actual worker capabilities, environment propagation and remote provisioning remain separate concerns.
- FirstMate's no-mistakes path uses two distinct `done` stages. Child completion is not a universal final-delivery signal.
- FirstMate documents no supported Codex Desktop backend. Codex CLI worker integration is a different question.

The historical provisional recommendation was an optional compatibility library in a normal crewmate, leaving the core Orchflows Work/Review contracts intact. The current standalone parity design supersedes that transport choice. Work-only composition before the existing delivery gate and explicitly authorized independent-review workflows remain policy options to test.

**Work already completed**

Public account/repository inspection, local source inspection of both pinned projects, a FirstMate-specific investigator's findings, 31 passing existing Orchflows packaging/installed-CLI tests in disposable environments, and one independent review of the original assessment. Its one finding was corrected: supervisor policy must be distinguished from mechanical enforcement across harnesses. See the evidence document for exact commands and limitations.

The paragraphs in this historical research section describe that earlier state. Current Stage 1 work is recorded above and in its verification document; do not repeat the account survey or mistake package checks for live compatibility.

**Historical research sequence**

1. Read the continuation outputs and verify source identities. Rehydrate only if local copies are absent; record later upstream changes separately from both recorded revisions.
2. If further research is requested, refine the remaining design choices and counterevidence rather than repeating the account survey or unchanged packaging tests.
3. If a live feasibility experiment is requested, establish the actual disposable backend/harness/configuration first, then run P01–P02 with an explicitly authorized review deliverable. Compare explicit roots against native registration.
4. Resolve child lifetime, policy enforcement, promotion replay and package retention before claiming reliable automatic integration. Use the relevant P03–P13 probes as scoped in the experiment plan.
5. Use P14 to compare practical value against baseline FirstMate and guidance-only use. Revise the ranking if native lifecycle limitations or operator burden favor another option.
6. At the time of this earlier research, implementation was a subsequent scope decision. The new current assignment above supersedes that limitation.

For a host-dependent test, establish the available FirstMate runtime backend, worker harness, authentication/configuration scope and native delegation tools. A Desktop session exposing child tools is not proof that a FirstMate terminal worker exposes them. If a live environment is unavailable, continue source research and return a concrete experiment specification instead of labeling the capability supported.

**Continuation outputs now in this repository**

- Update `docs/open-questions.md` with answers, sources, experiment results and still-open gaps.
- Add `docs/solution-options.md`: a reasoned comparison of the candidate approaches, including counterevidence and a provisional ranking.
- Add `docs/experiment-plan.md`: reproducible acceptance probes with inputs, expected results and failure cases.
- Add `docs/proposed-increment.md`: a bounded first implementation candidate, explicit non-goals, changes on both sides and success criteria.
- Update `docs/decisions.md` and `docs/evidence.md` for newly established facts. Distinguish proposed choices from user decisions and validated behavior.

These outputs now exist. They contain source-based findings and proposed experiments/designs, not a working integration. The original dated assessment remains intact.

**Research completion criteria**

A new reader can explain what “plug-and-play” means for the proposed release, which hosts it supports, how review policy works, who owns each lifecycle step, how install/update/relaunch preserve the selected workflow, and which claims remain unverified. Each high-priority question has an evidence-based answer or a precise experiment capable of answering it. The recommendation compares real alternatives and does not assume the initial worker-level proposal is correct.

**Copyable next-session prompt**

> Read HANDOFF.md, README.md, docs/stage1-continuation-verification.md, docs/stage1-acceptance-continuation.md, docs/stage1-windows-native.md and docs/feature-parity.md. Continue the standalone FirstMate/Herdr-only implementation with Claude and Codex workers. Preserve the already implemented read-only Work path and its exact trial identities; do not restart its package foundation or repeat invalid OAuth-cache trials. Prioritize the native Windows endpoint/lock/process-custody owners and verified detached-child retirement before enabling actual Windows workers. Complete the remaining cross-harness/restart and native background-tool acceptance, then extend independent Review, writers and later parity stages. FirstMate alone owns dispatch, lifecycle and outer delivery. Keep owned package/integration code separate from pinned research sources, retain uncertainty and artifacts, and leave active installations unchanged during ordinary tests.
