# Integration experiment plan

**Prior architecture probes:** this plan targets the earlier native-crewmate integration. The user has since selected a standalone FirstMate/Herdr-only product; [fundamental-design.md](fundamental-design.md) defines its FirstMate-owned component probes. P01–P14 remain useful background and failure cases, but native-child success or a tmux-only test cannot certify the new Herdr product.

September 13, 2026. These probes are specifications for later work, not tests executed in this research session. The [evidence ledger](evidence.md) and [source refresh](source-refresh-2026-09-13.json) record the checks actually performed. No bridge, installed profile, or FirstMate fleet trial exists.

## Fixed inputs and reporting

Use FirstMate `b182d0f908b78d08c7ccb8dce3775bdca8c5d657` and Orchflows `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a` initially. Keep the original Orchflows baseline `86aabd91071fa07a05cf970db2e73909184a1955` available for comparison. The newer commit changes only the evolve example, so it is not evidence of changed host integration.

Each run records: probe ID; exact project/bridge/package revisions and complete dependency digests; OS/backend/harness versions; resolved profile and sanitized launch arguments; effective host configuration sources; allowed input/output roots; model/effort and child limits requested versus observed; expected/actual result; evidence references; failure state; and cleanup result. Keep credentials and raw private host configuration out of the record. Save disposable fixtures and raw traces under ignored `artifacts/` or outside this repository; put portable summaries in `docs/evidence.md`.

Establish a disposable FirstMate home and an ordinary fixture repository, distinct from FirstMate's own source. Use the existing supported setup for a dedicated tmux environment. Do not assume a backend that can spawn also supports verified exit/relaunch: the current control contract requires recovery-grade classification for those operations. Prepare complete source/package directories and explicitly designate those as read-only inputs in the brief. Host authentication and actual harness execution must be established in that environment before a worker probe starts.

Current local observation: Windows reports Claude Code 2.1.233 and Codex CLI 0.144.0. WSL Ubuntu resolves bash, tmux, git, gh and python3; `codex` resolves to a Windows-mounted npm shim, and `claude` was not found by that shell. No authentication, Linux Codex execution, plugin visibility or integrated worker readiness was tested. This is an environment inventory, not a supported-host result.

## First discriminating trial

**P01 — explicit review through a real crewmate (Q02–Q05, Q09, Q13).** The fixture contains a short design document with a known inconsistency and enough evidence to resolve it. The request explicitly asks for a knowledge-only independent review and a standalone text report. No source edits, pushes, PRs or media dependencies are needed.

Using a prepared disposable home, the existing command shape is:

```sh
# Variables refer only to the prepared disposable home and fixture repository.
"$FM_HOME/bin/fm-brief.sh" orch-probe-review fixture --scout
# Fill both existing placeholders in data/orch-probe-review/brief.md.
# Put the actual review request in Captain's intent, and the following
# package/tool/workspace instructions in Firstmate spec.
"$FM_HOME/bin/fm-spawn.sh" orch-probe-review "$FIXTURE_REPO" --scout --harness claude --backend tmux
```

The proposed spec says: read `orch-review` from the supplied complete core root; use the supplied research guidance; create exactly one fresh native reviewer who did not make the fixture; allow read-only fixture/package access; collect the actual child response; include its provenance and reviewed candidate identity in the retained report; follow the existing FirstMate completion gate and status path. Do not invent a new installed skill name for this trial. Required core-relative documents must be readable from the actual worker and child.

Pass requires observed worker launch, actual native child creation/collection, correct finding, exact package root/revision evidence, standalone retained report, no extra reviewer, and parent-only FirstMate status. Listing tools or stating that delegation happened is insufficient: preserve native tool events or another host-owned execution record. Missing tools must produce a clear blocked result without claiming review completion.

Run P01 first with explicit roots (A1). Then repeat in a separate fresh host configuration using normal native package registration (A2), recording the actual resolved cache and manifest identity. This comparison isolates discovery friction. It does not imply that registration fixes lifecycle behavior.

## Acceptance and failure probes

| ID | Questions / purpose | Procedure and inputs | Required observation / failure condition |
| --- | --- | --- | --- |
| P02 | Q03, Q12: actual worker controls | In the same launch, inventory exposed native tools and effective settings; request one supported child model/effort; try one unsupported combination in a separate bounded task. Exercise one-child limit and one-level depth explicitly | Requested controls are honored through native fields/configuration or rejected before dependent work. A model name in a prompt is not proof. Record docs claims separately from tool evidence |
| P03 | Q02, Q06: authority and review | Inspect generated supervisor/ordinary/self-development briefs. Run an ordinary work-only task under each delivery mode after its bridge exists; count independent review invocations. Try selecting the profile for FirstMate self-development | Ordinary work adds no separate review gate. Explicit review stays scoped. Self-development is refused until its later role contract supports the exception. Supervisor still uses the fleet |
| P04 | Q04, Q07: durable attachment | Launch with package set A. Change the default to B, stop/relaunch the task through the supported control owner with a note, then inspect the replacement's actual inputs | Same task retains A, original intent and effective workflow contract. Loss of package identity, silent B selection or an ephemeral launch-only attachment fails |
| P05 | Q07, Q08: child lifetime | Interrupt parent while a read-only child is active; verify child state, then separately exit/relaunch the parent. Only after that succeeds repeat with a serialized disposable writer and a bounded visible write activity | Replacement does not start writing until old writers are joined/stopped or proven gone. Unknown child identity/lifetime blocks. Parent exit alone cannot certify descendants stopped |
| P06 | Q08: steering and decisions | Send a changed requirement through the existing durable inbox during child work and during review. Track parent receipt, child receipt and result generation. Open a keyed decision and supply its resolution | Messages are processed in order; old-generation results are excluded; all relevant children receive the change or are stopped; done does not silently clear an unresolved decision |
| P07 | Q02, Q08: no-mistakes handoff | After work-only implementation, collect children and observe first done. Continue the same crewmate through the selected pipeline. Introduce a pipeline finding and a separate human decision gate | First done means implementation only; pipeline owns active-run fixes; final done includes CI-green PR evidence. No child writes during active validation; no auto-answering decision gates |
| P08 | Q05, Q09: candidate provenance | Review a frozen fixture, then alter an untracked relevant file, an unstaged file, and the committed candidate in separate cases. Introduce a failed child before the join | Evidence identifies the exact reviewed state. Changed or partial candidates cannot inherit a clean review. One repair pass reports its changed state without claiming a second independent review |
| P09 | Q10: install, update, rollback | After an installer exists, install twice in disposable host homes containing user libraries/settings; stage B while A runs; interrupt before and after activation; disable and roll back | Existing libraries/settings preserved, no automatic global concurrency changes, active A still reads A's full graph, failed B never becomes a successful default, rollback restores selection, referenced packages are retained |
| P10 | Q11, Q13: environment and fallback | Use different caller and existing-pane ORCHFLOWS_HOME values; repeat with nondefault host config, an absent dependency, and a remote secondmate missing its package | Worker proves actual resolved values/paths; stale daemon environment does not pass by name alone. Unsupported routes block or use an already authorized compatible profile. Remote package installation is independently evidenced |
| P11 | Q04, Q08, Q14: promotion | Begin with scout review workflow, promote under an explicitly authorized ship request, then relaunch after promotion | Ship contract replaces scout execution semantics and survives relaunch. Original scout spec is not replayed as current work. Until supported, profile rejects promotion and uses a new ship task with report context |
| P12 | Q14: retained artifacts | Complete a text scout with child evidence; validate its standalone report after normal teardown. Separately propose a multi-file media/design fixture | Report survives with its necessary evidence. Media remains unsupported until an explicit durable artifact route exists; a link into deleted scratch does not pass |
| P13 | Q03, Q10, Q12, Q16: compatibility drift | Rerun affected probes after changing FirstMate, host CLI, package/library contents or profile configuration. Include unchanged semantic version with changed bytes and duplicate unqualified orch-* skill names | Exact identity/configuration changes invalidate the appropriate readiness record. Discovery cannot substitute light 0.6.3 for source core 0.7.0. No broad compatibility range is claimed from one passing tuple |
| P14 | Q01, Q16: value versus baseline | Use the same small research, review and implementation assignments for baseline FirstMate, guidance-only D, and B. Keep task intent, outer profile and delivery mode fixed; record authorized child usage separately | Compare useful outcomes, missed requirements, operator interventions, elapsed time and available usage. Report missing cost/usage evidence; do not infer benefit from more agents |

P03 and P07 require an implemented work-only composition and a configured delivery fixture. P09 requires the proposed installation machinery. These are future acceptance tests, not commands that can validate the current documentation-only state. Remote and media cases are later expansion gates; an initial supported scope may refuse them clearly rather than implement them.

## Concrete control sequence and evidence boundaries

For P04–P06, use the existing supported control entrypoints on the exact disposable task, with a task-specific note file:

```sh
"$FM_HOME/bin/fm-control.sh" orch-probe-review interrupt
"$FM_HOME/bin/fm-control.sh" orch-probe-review relaunch --note-file "$PROBE_NOTE"
```

Use `fm-send.sh`/the current inbox owner for conversational steering, following that revision's help. Do not emulate cancellation by typing text and observing an idle prompt. FirstMate's control source distinguishes interrupt delivery, acknowledged cancellation and proven parent exit. Neither these scripts nor an Orchflows history record establishes native-child lifetime by itself. [Control contract](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-control.sh#L10-L81).

Before cleanup, collect all required report/candidate/child evidence and check the normal FirstMate hold and teardown conditions. Leave unknown or unlanded work preserved. The experiment report must say whether cleanup was completed, refused, or intentionally deferred, and why.

## Release gates

1. **Research result:** current deliverable. Every Q01–Q16 has a source-based answer, a provisional proposal, or a discriminating probe. No runtime certification.
2. **Manual feasibility:** P01–P02 succeed for one actual worker configuration, with the authority portion of P03 verified. Label manual invocation only.
3. **Bounded local profile:** relevant P03–P09 and P12–P13 pass on one supported backend/worker tuple. Unsupported promotion, remote execution, nesting and media fail explicitly. Restart/stop guarantees must match what the host demonstrated.
4. **Broader installation claim:** native registration, remote provisioning, additional harnesses and retained media pass their own probes. P14 provides evidence before claiming practical improvement over ordinary FirstMate.
