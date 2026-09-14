# Next-session handoff

**Your assignment is to research and brainstorm practical ways to make Orchflows a simple installation and upgrade for FirstMate.** Evaluate the important alternatives and close the highest-impact unknowns before selecting an implementation. This repository contains the preceding investigation; no prior conversation is required.

The user's original question was whether Orchflows could be a plug-and-play upgrade to kunchenguid's FirstMate, which complexities prevent seamless use, and what either project would need to change. The user then explicitly requested this private repository, the research, the unanswered questions, and this handoff for the next research/brainstorming session.

**Read in this order**

1. [README.md](README.md) for repository status.
2. [Original assessment](docs/assessment-2026-09-13.md) for the findings and recommended direction.
3. [Evidence](docs/evidence.md) and [source manifest](docs/source-manifest.json) for provenance and actual checks.
4. [Open questions](docs/open-questions.md), [options](docs/options.md), and [decisions](docs/decisions.md).

**What is already established**

The investigation examined FirstMate at `b182d0f908b78d08c7ccb8dce3775bdca8c5d657` and Orchflows 0.7.0 at `86aabd91071fa07a05cf970db2e73909184a1955`. The report contains source-backed evidence for these boundaries:

- FirstMate supervisors dispatch through the fleet. Native children inside ordinary crewmate worktrees are explicitly allowed; primary enforcement is harness-specific.
- FirstMate's delivery policy conflicts with automatically adding Orchflows dynamic workflow's independent review.
- Worker briefs restrict workspace access. FirstMate self-development has an additional no-delegation role instruction.
- FirstMate's existing extension API is for process-event adapters; it is not an existing workflow-injection API.
- Host plugin registration, actual worker capabilities, environment propagation and remote provisioning remain separate concerns.
- FirstMate's no-mistakes path uses two distinct `done` stages. Child completion is not a universal final-delivery signal.
- FirstMate documents no supported Codex Desktop backend. Codex CLI worker integration is a different question.

The provisional recommendation is an optional compatibility library in a normal crewmate, leaving the core Orchflows Work/Review contracts intact. A work-only composition before the existing delivery gate and explicitly authorized independent-review workflows are possible ways to address review policy. Neither approach has been implemented or demonstrated.

**Work already completed**

Public account/repository inspection, local source inspection of both pinned projects, a FirstMate-specific investigator's findings, 31 passing existing Orchflows packaging/installed-CLI tests in disposable environments, and one independent review of the original assessment. Its one finding was corrected: supervisor policy must be distinguished from mechanical enforcement across harnesses. See the evidence document for exact commands and limitations.

Do not repeat the entire account survey or treat successful setup tests as an integration trial. No bridge, installer, production configuration change, or live FirstMate fleet experiment exists yet.

**Suggested sequence**

1. Rehydrate the pinned sources using the evidence document. Record current upstream heads separately and examine changes to the cited interfaces; do not silently replace the baseline.
2. Resolve Q01–Q04 first: product scope, review ownership, actual worker capability and workflow attachment. Use source reads and, where available, a disposable real-worker probe.
3. Compare the options in [docs/options.md](docs/options.md). Identify the smallest useful scope for each, changes required on each side, update burden, failure handling and unanswered questions.
4. Work through the remaining question groups. Several can be answered from source without launching agents: configuration inheritance, brief assembly, delivery transitions and package refresh.
5. Propose bounded experiments that could disprove the preferred option. Record actual tool availability, exact launch command/configuration, revisions, output references and gaps for any experiment you run.
6. Produce a ranked recommendation and a first-increment proposal. The next step requested by the user is research and brainstorming; production implementation is a subsequent scope decision.

For a host-dependent test, establish the available FirstMate runtime backend, worker harness, authentication/configuration scope and native delegation tools. A Desktop session exposing child tools is not proof that a FirstMate terminal worker exposes them. If a live environment is unavailable, continue source research and return a concrete experiment specification instead of labeling the capability supported.

**Expected outputs in this repository**

- Update `docs/open-questions.md` with answers, sources, experiment results and still-open gaps.
- Add `docs/solution-options.md`: a reasoned comparison of the candidate approaches, including counterevidence and a provisional ranking.
- Add `docs/experiment-plan.md`: reproducible acceptance probes with inputs, expected results and failure cases.
- Add `docs/proposed-increment.md`: a bounded first implementation candidate, explicit non-goals, changes on both sides and success criteria.
- Update `docs/decisions.md` and `docs/evidence.md` for newly established facts. Distinguish proposed choices from user decisions and validated behavior.

These output paths are planned deliverables, not files that already exist.

**Research completion criteria**

A new reader can explain what “plug-and-play” means for the proposed release, which hosts it supports, how review policy works, who owns each lifecycle step, how install/update/relaunch preserve the selected workflow, and which claims remain unverified. Each high-priority question has an evidence-based answer or a precise experiment capable of answering it. The recommendation compares real alternatives and does not assume the initial worker-level proposal is correct.

**Copyable next-session prompt**

> Read HANDOFF.md and its linked documents. Continue the Orchflows–FirstMate feasibility research and brainstorm competing solutions to the open questions. Refresh the relevant upstream contracts while preserving the recorded baseline. Prioritize product scope, review ownership, actual worker capabilities and an installation/brief attachment point. Compare the candidate architectures, specify bounded experiments, and produce the research outputs listed in HANDOFF.md. Treat the existing recommendation as provisional, clearly separate observed behavior from source claims and proposals, and focus this session on research and design.
