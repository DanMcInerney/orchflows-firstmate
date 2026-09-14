# Open questions and research plan

All questions start open. Priority indicates investigation order, not an implementation commitment. Link new findings and experiments from the answer column or add a dated note below the relevant row.

**P0: choose a viable integration boundary**

| ID | Question | Why it matters | Evidence needed / possible directions | Current answer |
| --- | --- | --- | --- | --- |
| Q01 | What does plug-and-play mean for the first release: manual invocation, automatic task routing, or every child visible in the fleet? | These are different products and engineering scopes | Compare options A–D; specify supported task types, hosts, operator steps and desired upgrade behavior | Open; worker-level add-on is provisional |
| Q02 | How should Orchflows review relate to no-mistakes, direct-PR and local-only? | An unconditional dynamic workflow conflicts with the recorded delivery policy | Read current policy and generated briefs; compare work-only composition, explicitly requested review, and a new policy; verify actual status transitions | Open; do not assume extra review is authorized |
| Q03 | Which exact FirstMate-launched workers can discover Orchflows and create the necessary native children? | A supported CLI name or successful package installation proves neither | Launch a disposable worker; inventory tools and effective plugin roots, native depth, model/effort controls and permissions; test one real child and collect its output | Unverified; Claude candidate first, Codex launch separately |
| Q04 | Where should workflow selection and instructions attach, and can a useful version avoid upstream changes? | Existing extension bindings do not support workflow injection | Trace brief assembly and launch/relaunch; test explicit Firstmate spec instructions; compare separate config, dispatch-schema extension and host-native entrypoint | Existing brief is a plausible manual seam; automatic integration unresolved |

**P1: lifecycle, authority and isolation**

| ID | Question | Why it matters | Evidence needed / possible directions | Current answer |
| --- | --- | --- | --- | --- |
| Q05 | What files, branches and worktrees may children use, and who integrates and removes them? | Existing briefs confine writes; ordinary parallel workflows may allocate other workspaces | Begin with one writer/read-only children; compare explicitly authorized descendant worktrees; test combined candidate revision and cleanup after failure | Open |
| Q06 | How should the role boundary work when the task edits FirstMate itself? | Injected self-development instructions forbid delegation even though generic task worktrees allow native children | Examine precedence and a narrow exception distinguishing subordinate work from supervisor identity; retain contributor rules | Open; do not enable implicitly |
| Q07 | What must be checkpointed to recover an interrupted worker? | FirstMate outer-task durability does not prove recovery of native children or their results | Record task/workflow/version, child state, result revisions and outstanding joins; interrupt/relaunch; compare restart-from-checkpoint with explicit restart-from-scratch | No recovery experiment executed |
| Q08 | How do steering, decisions, cancellation and completion propagate between the two layers? | A child can keep acting on obsolete instructions or emit misleading completion | Trace durable inbox acknowledgements and control actions; test steering during work and review; preserve implementation-done versus CI-ready-done in no-mistakes | Source boundary known; mapping unimplemented |
| Q09 | What result contract preserves the exact candidate, evidence and review provenance? | A review can assess stale code or an incomplete merge of child changes | Define artifact paths, candidate revision/uncommitted-state handling, errors and final handoff; test a changed candidate and failed child | Open |

**P1: install and upgrade experience**

| ID | Question | Why it matters | Evidence needed / possible directions | Current answer |
| --- | --- | --- | --- | --- |
| Q10 | How should package versions, plugin caches and active tasks behave across updates and rollback? | Filesystem swap recovery is only one part of the transaction | Compare task-pinned versions, retained old packages, new-session activation, interrupted install recovery and uninstall/disable behavior | Existing core setup mechanics tested; integration model open |
| Q11 | What reaches the actual worker environment and each remote secondmate host? | Terminal daemons, custom host homes and allowlists can differ from the caller | Probe resolved ORCHFLOWS_HOME/host configuration, library dependencies and package paths; inspect inheritance allowlist; provision each host explicitly | No local-to-worker or remote installation test |
| Q12 | How should child limits and model/effort choices compose with FirstMate quota-aware dispatch? | Fleet concurrency multiplies inner work; recorded effort may differ from actual launch | Verify effective native controls, unsupported-value behavior, repair settings and total fan-out; avoid silently overriding user concurrency | Existing setup has --skip-host-config; integration resource policy open |

**P2: wider capabilities and maintainability**

| ID | Question | Why it matters | Evidence needed / possible directions | Current answer |
| --- | --- | --- | --- | --- |
| Q13 | What should happen for unsupported harnesses, unavailable skills or missing library dependencies? | Silent fallback can make an ordinary run look like an Orchflows run | Compare refusal, explicit reduced capability and an already-authorized compatible worker route; probe registry/readiness errors | No compatibility matrix |
| Q14 | Are research, design, media and reusable workflow-authoring tasks valid deliverables under FirstMate's task/output conventions? | Orchflows covers more than coding, and authoring defaults to a user library | Trace scout/report and artifact retention; choose explicit output/library locations; test a non-code deliverable without losing it at teardown | Source-based concern only |
| Q15 | Is Codex Desktop support required, and can it remain a separate project? | FirstMate documents a missing supported shell-to-Desktop transport | Recheck current backend boundary; separate Desktop endpoint lifecycle from Codex CLI workers; assess necessity before expanding scope | No Desktop backend established |
| Q16 | How much upstream change and continuing maintenance would each option require? | Private-local customization, reusable package distribution and upstream adoption have different constraints | Review licenses and contribution requirements before redistributing code; compare public contract stability, ownership, test burden and compatible version ranges; evaluate representative baseline-vs-candidate tasks | Not investigated in depth; no maintainers contacted |

The detailed source entrypoints for these questions are in [evidence.md](evidence.md). The existing suggestions are in [options.md](options.md). A claimed answer should identify whether it is a documented contract, a source-code observation, a live result, a recommendation or a user choice.

**Suggested probe record**

For each experiment record the question IDs, exact source revisions, OS/backend/harness versions, sanitized launch/configuration description, task and workspace scope, expected observation, actual result, artifact references, failure/recovery outcome, limitations and next action. A skipped probe remains a gap.
