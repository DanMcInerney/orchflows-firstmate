# Feature parity and migration inventory

The target is a standalone Orchflows distribution used **only through FirstMate on Herdr**, with Claude Code and Codex as worker harnesses. This replaces the earlier narrow add-on scope. Source coverage, package mechanics and working fleet execution are separate claims.

The complete baseline is Orchflows `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a`, version 0.7.0: 1,064 files, five core skills, seven guidance files, three core Python modules and five optional example libraries containing eleven additional skills. The owned source is `packages/orchflows-firstmate/`; `.sources/orchflows/` stays an unchanged research reference. [Upstream tree](https://github.com/DanMcInerney/orchflows/tree/0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a).

## Core parity target

| Feature | Behavior to preserve | Fundamental adaptation | Current implementation |
| --- | --- | --- | --- |
| Work | Fresh maker, explicit task/context, selected guidance/model/effort, bounded result | Request a FirstMate-owned component; return a durable logical assignment handle, not a native child handle | One read-only component implemented; real Claude/Codex result and gather observed in WSL, with earlier Codex parent replacement. [Continuation](stage1-acceptance-continuation.md) separates watcher/read-order outcomes. Native Windows workers refuse pending process custody |
| Review | Fresh independent reviewer, scoped findings, no repairs | Separate component with reviewed-state identity and explicit review authorization | Source retained; workflow execution gated pending adapter |
| Dynamic workflow | Investigation, dependency-aware parallel work, join, one review, one repair pass | Root crewmate composes; FirstMate owns component lifecycle; workflow review policy reconciles with root delivery | Source retained; workflow execution gated pending adapter |
| Build workflow | Create workflows/guidance/libraries, trial them, review and refine | Author in assigned workspace; collect package artifact and publish/install through the selected authorized delivery | Source retained; workflow execution gated pending adapter |
| Self-improve | Bounded history inspection, source checks, corrections, trial and independent review | Group history joins several host sessions; target checkout/library and delivery authority are explicit | Native history mechanics retained; group-history correlation not implemented |
| Layered guidance | Dotted specificity, core then selected-library order, deduplication, missing-domain errors | Resolve within the task's pinned package set; preserve logical domain names | Guidance files retained unchanged |
| Model and effort | Per-setting caller precedence, assignment overrides, repair settings, unsupported-value errors | FirstMate dispatch uses effective worker controls; continue or replace by explicit capability | Existing intent contract retained; fleet realization pending |
| Native history CLI | Find/inspect/read, paging, dates, exact event expansion, read-only behavior | Remains a host transcript reader; new task-group index supplies exact session IDs | Existing module and fixtures retained |
| Home setup | Complete package, runtime, editable libraries, recovery on failed swap | Own home/package/catalog identity; host configuration edits become explicit | Implemented in package foundation; verify against disposable-home tests |
| Resolve and doctor | Complete resource resolution, containment, duplicate detection, package checks | Logical core alias resolves only to this fork; distinguish package readiness from execution readiness | Package checks preserved; experimental controller capability is negotiated separately |
| Host manifests | Claude and Codex can discover the distribution | Independent namespace and catalogs; never substitute the normal Orchflows installation | Package manifests present; no user installation or worker discovery trial |
| Updates | Preserve user libraries and recover from a failed core swap | Retain complete task-pinned dependency sets across active tasks; activate new defaults separately | Existing package swap retained; one complete immutable task snapshot implemented; shared version store remains planned |

“Preserve” concerns observable workflow behavior, not the original native-agent transport. Parallelism, nested composition, independent review and one repair pass remain target features; they are not removed to make the first probe easier. A smaller first probe is a staging decision, not a claim of full parity.

## Optional libraries

All optional library source, assets, tests and notices are retained as migration fixtures. Their upstream manifests/references still describe upstream dependencies; they are not certified FirstMate entrypoints. Loading one must not escape into the separately installed normal Orchflows core.

| Library / baseline version | Skills | Main migration work | Required representative demonstration |
| --- | --- | --- | --- |
| `3d-browser-game` 0.2.0 | `3d-browser-game`, `make-blender-game-assets`, `playtest-3d-browser-game` | Retained editable/binary artifacts, renderer/browser tools in component workers, exact candidate under playtest | Produce a small game, independently playtest the same candidate, preserve editable assets |
| `evolve` 0.1.1 | `evolve` | Durable component handles and checkpoints, evaluator/candidate isolation, bounded fan-out, safe continuation after restart | Resume one interrupted two-candidate comparison without duplicate promotion or replacement writers |
| `research-acquire` 0.5.1 | `research-acquire` | Worker-visible runtimes/network capabilities and retained acquisition evidence | Bounded acquisition with inspectable coverage/gaps and a resumable read |
| `short-video` 0.3.0 | `short-video`, `make-short-video`, `review-short-video` | Media tools, artifact collection before teardown, exact exported state and independent review | Produce a small original export plus editable source, then review those exact exports |
| `social-search` 0.8.0 | `social-search`, `search-site`, `rank-evidence` | Parallel fleet components, evidence gathering, one independent ranker, optional acquisition dependency | Two bounded source searches, joined evidence, fresh ranked assessment with provenance |

The baseline versions and skills come from the root manifests and tracked `SKILL.md` files at the pinned revision. A copied example is source availability, not evidence of runtime compatibility.

## Deliberate differences

1. The package is `orchflows-firstmate`, with its own home and registry identity. Normal Orchflows is neither a runtime dependency nor a fallback.
2. The product executes only inside the FirstMate/Herdr contract. Administrators can inspect, package and resolve files outside a running fleet; doing so does not authorize workflow execution.
3. Work/Review will create FirstMate-owned components. Neither the root worker nor a component receives arbitrary fleet-control authority. Herdr access remains behind FirstMate's backend dispatcher.
4. Root delivery remains separate from component completion. A component returns its result without opening a PR, running the root's delivery pipeline or granting a merge.
5. Selecting the full dynamic workflow must explicitly authorize its independent review within FirstMate policy. A work-only mode must have a different name and cannot be reported as full dynamic parity.
6. Shared concurrent writes become explicitly owned candidates and joins. Equivalent outcomes are required, not identical incidental filesystem layout.
7. Default installation preserves host concurrency settings. Any explicit tuning must describe the actual host control; it is not a fleet-wide budget.

## Evidence and acceptance

The baseline core suite ran from the pinned source with disposable fixtures: **Windows: 61 tests, 60 passed and one POSIX-mode skip; WSL Ubuntu: all 61 passed**. It covers setup, host configuration and native history; it does not exercise the optional libraries end to end or any FirstMate worker. Raw output is under ignored `.scratch/standalone-foundation/baseline-tests.log` and `baseline-tests-linux.log`.

The package foundation must retain the complete baseline file set, preserve the original examples/assets/notices, pass the inherited tests after explicit namespace/default-behavior adaptations, and pass new isolation tests. [Foundation verification](foundation-verification.md) records the exact candidate and results. [Fundamental design](fundamental-design.md) defines subsequent runtime gates.

Full feature parity can be claimed only after the core compositions and representative library cases run through FirstMate-owned Herdr endpoints under both requested worker harnesses. No such claim is made for this foundation.
