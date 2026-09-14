# Open questions and research plan

**Current scope change:** the user has now authorized beginning implementation of a standalone FirstMate/Herdr-only distribution, preserving near feature parity and supporting Claude/Codex workers. The rows below retain the earlier narrow integration research; [fundamental-design.md](fundamental-design.md) and [feature-parity.md](feature-parity.md) define the replacement architecture and runtime acceptance work. Native-child compatibility is no longer the planned Work/Review transport. Herdr component ownership, scoped task-group requests, review authorization and result collection now carry those requirements. Earlier initial exclusions are rollout limits, not permission to drop parity features permanently.

Updated September 14, 2026 during Stage 1 verification. **Source** means an inspected implementation or documented contract; **Proposed** is an unvalidated design; **Runtime open** requires an actual FirstMate-launched worker. No runtime integration question is closed by package tests or this research session's native children.

## Current implementation queue

The latest user clarification supersedes the earlier harness/recovery-first
queue. The product should let FirstMate use Orchflows' two primitives, dynamic
workflow and custom/meta-workflows through its existing systems. FirstMate owns
Claude/Codex integration, dispatch, workspaces, communication, supervision,
recovery and delivery. New code must address a demonstrated missing interface
or workflow-context requirement, rather than duplicate those mechanisms.

Follow the [current handoff](../HANDOFF.md). Development remains Ubuntu/WSL,
Linux first; native Windows is deferred. The dev.4 package adapts upstream
ca72258493480ddcfe73b3f01d0475ad532e4726. Existing read-only Work/Review evidence
is preserved in [verification](review-verification.md); the added design-loop
source remains inactive and must not be used for this work.

| Order | Next work | Evidence or deliverable required |
| --- | --- | --- |
| 1 | Map existing FirstMate owners and audit the experimental adapter | Identify how Work/Review can use existing delegation, result and lifecycle operations. For added records/helpers, justify necessary workflow context or plan a tested simplification of duplicated task/control state |
| 2 | Normal skill/workflow availability and primitive integration | Enable the package and selected libraries once in a disposable FirstMate setup; ordinary workers and relaunches discover the correct skills without manual per-task attachment. Resolve any role or review-policy gap at its existing FirstMate owner |
| 3 | Representative dynamic and custom workflow | Preserve upstream Work/Review semantics, candidate identity, join/review/repair behavior and root delivery through FirstMate. Use existing workspace/write mechanisms where required; custom workflows should compose the same primitives |
| 4 | Targeted recovery and harness compatibility checks | Invoke ordinary FirstMate recovery and verify workflow context/results survive. Test the changed interface with supported workers; investigate a harness issue only where it affects this path |
| Later | Broader parity and release | Extend demonstrated behavior across core/custom/meta workflows and representative optional libraries, with an actual install/update route and precise supported-runtime evidence |

Known gaps remain: actual Codex Review/watcher acceptance, native background-tool
activity/retirement, the full supervisor wake/drain/rearm cycle, writer joins,
nested work, retained artifacts/history and optional-library parity. The prior
foreground Claude and parent-replacement evidence does not close them.
Native Windows custody remains deferred. Preserve the observed failures and
refusal guards; these gaps do not automatically make rebuilding those systems
the next milestone.

The existing one-component Work/Review limits remain enforced until their
replacement is implemented and verified. [Fundamental design](fundamental-design.md)
contains earlier proposals to reassess under D26, and [feature parity](feature-parity.md)
tracks the outcome requirements independently from source availability.

## Earlier research questions and source answers

**P0: choose a viable integration boundary**

| ID | Question | Why it matters | Evidence needed / possible directions | Current answer |
| --- | --- | --- | --- | --- |
| Q01 | What does plug-and-play mean for the first release: manual invocation, automatic task routing, or every child visible in the fleet? | These are different products and engineering scopes | Compare options A–D; specify supported task types, hosts, operator steps and desired upgrade behavior | Proposed: manual explicit-root review trial, then opt-in local worker profiles; full child fleet visibility is a different product. [Ranking](solution-options.md), P14 |
| Q02 | How should Orchflows review relate to no-mistakes, direct-PR and local-only? | An unconditional dynamic workflow conflicts with the recorded delivery policy | Read current policy and generated briefs; compare work-only composition, explicitly requested review, and a new policy; verify actual status transitions | Source restriction confirmed. Proposed: unchanged dynamic contract, distinct work-only ship composition, explicit review deliverable. Runtime open: P01/P03/P07 |
| Q03 | Which exact FirstMate-launched workers can discover Orchflows and create the necessary native children? | A supported CLI name or successful package installation proves neither | Launch a disposable worker; inventory tools and effective plugin roots, native depth, model/effort controls and permissions; test one real child and collect its output | Runtime open: P01/P02/P13. Local CLI inventory and refreshed host docs recorded, no certified worker. Claude candidate first; Codex CLI separately. [Host findings](orchflows-contracts.md) |
| Q04 | Where should workflow selection and instructions attach, and can a useful version avoid upstream changes? | Existing extension bindings do not support workflow injection | Trace brief assembly and launch/relaunch; test explicit Firstmate spec instructions; compare separate config, dispatch-schema extension and host-native entrypoint | Source: original Firstmate spec is durable; launch overlay regenerates; unknown metadata survives specific rewrites without a supported schema. Proposed generic opt-in seam. Promotion needs stage-aware replay. [Trace](firstmate-contracts.md), P04/P11 |

**P1: lifecycle, authority and isolation**

| ID | Question | Why it matters | Evidence needed / possible directions | Current answer |
| --- | --- | --- | --- | --- |
| Q05 | What files, branches and worktrees may children use, and who integrates and removes them? | Existing briefs confine writes; ordinary parallel workflows may allocate other workspaces | Begin with one writer/read-only children; compare explicitly authorized descendant worktrees; test combined candidate revision and cleanup after failure | Source boundaries confirmed. Proposed read-only review children, then one active writer in assigned worktree; parent owns joins. Extra worktrees deferred. [Trace](firstmate-contracts.md), P05/P08 |
| Q06 | How should the role boundary work when the task edits FirstMate itself? | Injected self-development instructions forbid delegation even though generic task worktrees allow native children | Examine precedence and a narrow exception distinguishing subordinate work from supervisor identity; retain contributor rules | Source: last-appended role contract supersedes earlier role wording and forbids delegation. Proposed initial exclusion; later narrow change at its single owner. [Trace](firstmate-contracts.md), P03 |
| Q07 | What must be checkpointed to recover an interrupted worker? | FirstMate outer-task durability does not prove recovery of native children or their results | Record task/workflow/version, child state, result revisions and outstanding joins; interrupt/relaunch; compare restart-from-checkpoint with explicit restart-from-scratch | Source: relaunch is a fresh conversation; HEAD/dirty flag is not exact candidate state. Proposed compact attachment/phase/child/result/steering checkpoint; unknown old writers block replacement. [Increment](proposed-increment.md), P04/P05 |
| Q08 | How do steering, decisions, cancellation and completion propagate between the two layers? | A child can keep acting on obsolete instructions or emit misleading completion | Trace durable inbox acknowledgements and control actions; test steering during work and review; preserve implementation-done versus CI-ready-done in no-mistakes | Source mapping traced. Proposed parent-only status/inbox ownership, child generation tracking and exact decision resolution; preserve both no-mistakes done stages. Runtime open: P05–P07/P11 |
| Q09 | What result contract preserves the exact candidate, evidence and review provenance? | A review can assess stale code or an incomplete merge of child changes | Define artifact paths, candidate revision/uncommitted-state handling, errors and final handoff; test a changed candidate and failed child | Proposed commit or complete relevant dirty-state identity, child/reviewer identity, assignment generation, executed checks and retained outputs; distinguish reviewed and repaired candidate. [Solutions](solution-options.md), P08 |

**P1: install and upgrade experience**

| ID | Question | Why it matters | Evidence needed / possible directions | Current answer |
| --- | --- | --- | --- | --- |
| Q10 | How should package versions, plugin caches and active tasks behave across updates and rollback? | Filesystem swap recovery is only one part of the transaction | Compare task-pinned versions, retained old packages, new-session activation, interrupted install recovery and uninstall/disable behavior | Source: successful setup removes previous core; resolve has no version selection. Proposed retained complete core/library graph, atomic default activation for new tasks, reference-aware retention. Integration unimplemented: P04/P09/P13 |
| Q11 | What reaches the actual worker environment and each remote secondmate host? | Terminal daemons, custom host homes and allowlists can differ from the caller | Probe resolved ORCHFLOWS_HOME/host configuration, library dependencies and package paths; inspect inheritance allowlist; provision each host explicitly | Source: allowlist retains pane-shell values; CLAUDE_CONFIG_DIR has explicit forwarding; workflow config is absent from inherited set. Proposed portable policy plus independent host provisioning. Runtime open: P10 |
| Q12 | How should child limits and model/effort choices compose with FirstMate quota-aware dispatch? | Fleet concurrency multiplies inner work; recorded effort may differ from actual launch | Verify effective native controls, unsupported-value behavior, repair settings and total fan-out; avoid silently overriding user concurrency | Proposed separate outer/inner choices, explicit one-child/one-level initial bound, skip host-config writes. Refreshed Claude docs distinguish depth/subagent/tool limits; runtime open: P02/P13. [Findings](orchflows-contracts.md) |

**P2: wider capabilities and maintainability**

| ID | Question | Why it matters | Evidence needed / possible directions | Current answer |
| --- | --- | --- | --- | --- |
| Q13 | What should happen for unsupported harnesses, unavailable skills or missing library dependencies? | Silent fallback can make an ordinary run look like an Orchflows run | Compare refusal, explicit reduced capability and an already-authorized compatible worker route; probe registry/readiness errors | Proposed refuse required missing capabilities; explicitly selected guidance-only mode or already-authorized compatible route may proceed. Capability matrix remains unverified: P01/P02/P10/P13 |
| Q14 | Are research, design, media and reusable workflow-authoring tasks valid deliverables under FirstMate's task/output conventions? | Orchflows covers more than coding, and authoring defaults to a user library | Trace scout/report and artifact retention; choose explicit output/library locations; test a non-code deliverable without losing it at teardown | Source: standalone scout report survives; scratch, inbox and journals are disposable. Proposed report-contained text first; media/library files need explicit retention or ship delivery. [Trace](firstmate-contracts.md), P11/P12 |
| Q15 | Is Codex Desktop support required, and can it remain a separate project? | FirstMate documents a missing supported shell-to-Desktop transport | Recheck current backend boundary; separate Desktop endpoint lifecycle from Codex CLI workers; assess necessity before expanding scope | Source unchanged: no selectable Desktop backend; shell-to-visible-endpoint transport remains separate. Proposed exclusion. A future backend must demonstrate create/send/read/stop/status lifecycle before entering compatibility probes |
| Q16 | How much upstream change and continuing maintenance would each option require? | Private-local customization, reusable package distribution and upstream adoption have different constraints | Review licenses and contribution requirements before redistributing code; compare public contract stability, ownership, test burden and compatible version ranges; evaluate representative baseline-vs-candidate tasks | Options compared; narrow external library + generic FirstMate seam favored provisionally. Root MIT license files inventoried, no distribution/legal conclusion or maintainer acceptance. Performance/cost unmeasured: P13/P14 |

Detailed source entrypoints are in [evidence.md](evidence.md), [FirstMate contracts](firstmate-contracts.md), and [Orchflows contracts](orchflows-contracts.md). The expanded comparison is [solution-options.md](solution-options.md); P01–P14 refer to [experiment-plan.md](experiment-plan.md). The original brainstorming inputs remain in [options.md](options.md). Proposed choices still require a later scope decision; runtime gaps remain explicit.

**Suggested probe record**

For each experiment record the question IDs, exact source revisions, OS/backend/harness versions, sanitized launch/configuration description, task and workspace scope, expected observation, actual result, artifact references, failure/recovery outcome, limitations and next action. A skipped probe remains a gap.
