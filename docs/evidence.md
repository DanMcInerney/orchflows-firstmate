# Evidence and completed work

This document preserves what the originating session established. The [original assessment](assessment-2026-09-13.md) remains the dated narrative record; this file can accumulate later evidence.

## Bounded leaf authoring  September 14, 2026

After PR #4 merged as d3cf51b6b6dd31887f2d7d35a28679426af19d90, dev.8
clarifies bounded non-delegating leaf authoring through existing dynamic
ship/local-only Work/Review. No new runtime owner or capability was added.

Actual Sonnet 5/high trials produced a complete library, exercised ordinary
parent replacement, applied the leaf in fresh read-only Work and obtained
Review. The refined run also used a fresh repair Work against its exact final
commit. Both original receipts remain failed; dev.8 local landing is not
certified. The initial diagnostic exposed digest confusion. The refined case
exceeded its narrow three-request/unchanged-library fixture and missed required
native-call observations; repair-trial evidence was not committed with the final
artifact. Cleanup retained both unlanded roots, with zero scoped processes.

One independent development Review found and prompted two observer repairs.
The final pass has 30 passing driver checks; exact package/integration checks,
runtime identities, failed receipts, separate strengthened reassessment and
remaining limits are in [verification](leaf-authoring-verification.md) and
[exact state](leaf-authoring-state.json). The final package clarification requires
committed repair-trial evidence before delivery and is not yet live-tested.

## Upstream target clarification — September 14, 2026

The user explicitly confirmed the latest [DanMcInerney/orchflows](https://github.com/DanMcInerney/orchflows) as the source to adapt, superseding their preceding local `orchflows-light` reference. The product remains a modified Orchflows with near feature parity, executed through FirstMate on Herdr with Claude Code and Codex workers.

**Executed source checks:** `git ls-remote https://github.com/DanMcInerney/orchflows.git HEAD refs/heads/main` returned `ca72258493480ddcfe73b3f01d0475ad532e4726` for both refs. A separate clone under ignored `.scratch/orchflows-refresh-ca7225849348/` was checked out detached at that exact revision. Comparing Git trees with the implemented `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a` baseline showed one added commit, 17 added files under `example-workflows/design-loop/`, and one changed root README. Core skills and runtime scripts have no changes in this delta. The root manifest remains 0.7.0; the added library manifest is 0.1.0 with eight skills. Its README explicitly describes the packaged example as experimental and untested.

**Initial source-check boundary:** that check acquired and inspected source only. The user subsequently authorized the refresh and said not to use design-loop for the work. Package dev.3 now imports all 17 added files as inactive migration source, updates the inactive README quotation and advances the three fork manifests. Core skills, scripts, tests and the FirstMate distribution are unchanged. The new source was not invoked, enabled or installed as a library. [Refresh verification](upstream-refresh-verification.md) and [current package state](upstream-refresh-state.json) record actual checks. Pinned `.sources/` references, active installations and earlier runtime records remain unchanged; package checks do not establish design-loop execution or seamless fleet compatibility.

**Source baseline**

| Project | Repository | Examined revision | Scope |
| --- | --- | --- | --- |
| FirstMate | https://github.com/kunchenguid/firstmate | b182d0f908b78d08c7ccb8dce3775bdca8c5d657 | Shallow clone of then-current main; source and documentation inspection only |
| Orchflows | https://github.com/DanMcInerney/orchflows | 86aabd91071fa07a05cf970db2e73909184a1955 | User's clean checkout, manifest version 0.7.0; source inspection and existing packaging tests |

The original search results contained older descriptions. Conclusions were checked against the pinned local source, not merely search snippets. Account inspection identified the relevant FirstMate/no-mistakes/treehouse ecosystem; no broad claim about every repository was made.

[Source manifest](source-manifest.json) contains SHA-256 values for the local source bytes available during handoff preparation. Git checkouts may normalize line endings, so use the manifest's Git blob IDs for cross-platform byte identity; working-copy hashes describe the inspected copies. Upstream code is not vendored into this documentation repository.

**Source entrypoints**

| Topic | FirstMate evidence | Orchflows comparison |
| --- | --- | --- |
| Responsibilities and architecture | [VISION.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/VISION.md), [docs/architecture.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/architecture.md) | [docs/architecture.md](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/architecture.md) |
| Supervisor policy, native-child exemption and enforcement gaps | [docs/subagent-guard.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/subagent-guard.md) | [orch-work](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/skills/orch-work/SKILL.md), [orch-review](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/skills/orch-review/SKILL.md) |
| Review ownership and delivery modes | [AGENTS.md, selected delivery path](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/AGENTS.md#selected-delivery-path-and-merge-authority) | [dynamic workflow](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/skills/orch-dynamic-workflow/SKILL.md) |
| Brief composition, workspaces and status | [bin/fm-brief.sh](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-brief.sh), [bin/fm-dod-lib.sh](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-dod-lib.sh) | [hosts: isolation](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/hosts.md#isolation) |
| Actual launch templates | [bin/fm-spawn.sh](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-spawn.sh#L1514-L1564) | [host registration and controls](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/hosts.md) |
| Harness-specific evidence | [Claude adapter](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.agents/skills/harness-adapters/references/harness/claude.md), [Codex adapter](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.agents/skills/harness-adapters/references/harness/codex.md) | [host contracts](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/hosts.md) |
| Dispatch and environment | [docs/configuration.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/configuration.md) | [home and package resolution](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/home.md) |
| Existing extension API | [docs/extension-bindings.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/extension-bindings.md) | [package layout](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/architecture.md#a-library) |
| Updates and secondmates | [updatefirstmate skill](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.agents/skills/updatefirstmate/SKILL.md), [inheritance owner](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-config-inherit-lib.sh), [provisioning contract](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.agents/skills/secondmate-provisioning/SKILL.md) | [setup CLI](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/scripts/orchflows.py), [host settings](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/scripts/host_config.py) |
| Desktop limitation | [docs/codex-app-backend.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/codex-app-backend.md) | Orchflows does not provide a FirstMate backend transport |
| Native history and recovery evidence | FirstMate durable state is distinct from native child state | [docs/history.md](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/history.md); a transcript is evidence, not a live process registry |

**Checks actually executed in the originating investigation**

From the pinned Orchflows checkout, on Windows PowerShell with Python 3.14.6:

```text
python -B -m unittest discover -s tests -p test_home_setup.py
Ran 29 tests in 9.946s
OK

python -B -m unittest discover -s tests -p test_home_cli.py
Ran 2 tests in 4.292s
OK
```

The test code was inspected before execution. It redirects setup and host settings into disposable directories. The tests exercise existing setup, preservation, recovery and installed-CLI behavior. No user's active host plugin configuration was installed or refreshed. Raw test logs were not saved as independent artifacts during that session; the transcript reported the outputs above.

A local reference check also verified that all 17 source-file references in the final original assessment resolved to files in the pinned checkouts and that numeric line anchors were in range. It was not an HTTP-link or heading-anchor validation.

**Independent investigation and review**

A native child investigated FirstMate contracts while the coordinator inspected Orchflows and joined the findings. A fresh child reviewed the complete original assessment without making repairs. It found one substantive wording issue: the report implied primary delegation enforcement across all harnesses, whereas the source only establishes verified Claude wiring and documents other gaps. The coordinator corrected the finding and the related acceptance check. No second review was run.

A legacy Claude adapter reference mentions `--setting-sources project,local`; the examined current `fm-spawn.sh` launch template does not contain that flag. The report therefore does not claim that current FirstMate universally excludes user plugins.

FirstMate records a Codex CLI tool inventory without subagents; the originating Codex Desktop session itself exposed native child tools. This is conflicting deployment evidence, not proof that either source describes every Codex worker. The required FirstMate worker launch remains untested.

**What was not done**

No integrated FirstMate task, native worker capability probe inside a FirstMate-launched process, live supervision/recovery test, package registration test in a crewmate, remote secondmate install, update/rollback experiment across both systems, implementation, upstream PR, or maintainer outreach. No complete license/distribution review or performance/cost comparison. The original work was feasibility research.

**Rehydrate the evidence without relying on previous machine paths**

Clone the two public repositories into disposable directories; these commands download source without running project installers or hooks:

```sh
git clone --no-checkout https://github.com/kunchenguid/firstmate.git firstmate
git -C firstmate checkout --detach b182d0f908b78d08c7ccb8dce3775bdca8c5d657

git clone --no-checkout https://github.com/DanMcInerney/orchflows.git orchflows
git -C orchflows checkout --detach 86aabd91071fa07a05cf970db2e73909184a1955
```

Use separate checkout locations or recorded refs for contemporary upstream research. Verify each `git rev-parse HEAD` before reproducing claims or checks. The original local directories and temporary clone are not dependencies of this handoff.

**Handoff preservation**

The original report was copied unchanged into this repository. Its recorded SHA-256 is `b2e10533790e2886cf3d94479afe48edff58a1a317e38eca6aa160cafa64528c`. Its phrase “this investigation” refers to the originating session described above. New questions and candidate approaches in this repository are proposed follow-up work, not additional completed research.

## Continuation research — September 13, 2026

The user requested fresh FirstMate and Orchflows research, reading this library, a complete Orchflows copy inside this workspace, and solutions to the integration friction points. That turn's scope was research and brainstorming; no implementation was authorized or performed in that turn. The subsequent implementation increment is recorded separately below. The dated original assessment and original source manifest remain unchanged.

### Acquisition and verification actually performed

Both public GitHub repository pages were opened, and full, non-shallow source clones were acquired inside the existing ignored `.sources/` directory:

```text
git clone https://github.com/DanMcInerney/orchflows.git .sources/orchflows
git clone https://github.com/kunchenguid/firstmate.git .sources/firstmate
```

The Orchflows copy includes the complete checked-out repository, Git history, tests and examples, rather than only its shipped skills. It has 1,064 tracked files and 2,419 commits reachable from the checked-out head. No submodules were reported by `git submodule status`. FirstMate has 553 tracked files and 632 commits reachable from its checked-out head. Both clones initially and after research had empty `git status --short` output. They are local research copies excluded from the parent repository by its existing ignore rules; the source itself is not committed or published here.

| Project | Original baseline | Observed remote-default checkout | Difference |
| --- | --- | --- | --- |
| FirstMate | `b182d0f908b78d08c7ccb8dce3775bdca8c5d657` | `b182d0f908b78d08c7ccb8dce3775bdca8c5d657` | None |
| Orchflows | `86aabd91071fa07a05cf970db2e73909184a1955` | `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a` | One commit, one changed line in `example-workflows/evolve/skills/evolve/SKILL.md`; clarifies how external failures affect the pivot counter |

Both Orchflows revisions declare version 0.7.0. No cited core integration interface changed between them. A Git revision/content identity is therefore more precise than the version label alone. [Exact change](https://github.com/DanMcInerney/orchflows/commit/0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a).

Executed read-only checks included `git rev-parse HEAD`, `git rev-parse --is-shallow-repository`, `git rev-list --count HEAD`, `git ls-files`, baseline-to-head `git log`/`git diff`, `git submodule status`, and parent `git check-ignore`. All 27 original manifest Git blob IDs were rechecked against their pinned revisions successfully. The original assessment's SHA-256 still matches the recorded value. [Machine-readable refresh](source-refresh-2026-09-13.json) records those identities, counts and file checks. No upstream installers or integration code were run.

### Local host inventory actually performed

Read-only command discovery/version calls found Windows Claude Code 2.1.233 and Codex CLI 0.144.0. PowerShell did not discover tmux on its PATH. WSL lists Ubuntu and docker-desktop; an Ubuntu shell found bash, tmux, git, gh and python3, plus a Codex npm shim under a mounted Windows path, but did not find Claude. These are command-discovery observations, not execution/authentication checks for a Linux worker. No credentials were inspected, no FirstMate home bootstrapped, no actual worker launched, and no host plugin/configuration changed. The [experiment plan](experiment-plan.md) records the remaining prerequisites.

### New source observations and inferences

| Finding | Classification and source |
| --- | --- |
| The durable Firstmate spec can carry an explicit package/workflow for a manual trial; launch overlays are regenerated, including on relaunch | Source observation; feasibility of actual loading remains a proposal. [FirstMate trace](firstmate-contracts.md#q04-attachment-and-durable-instructions) |
| Unknown metadata keys survive the inspected ordinary relaunch and promotion rewrites | Source observation, not an existing supported workflow schema, external-writer API or universal preservation guarantee. [Metadata trace](firstmate-contracts.md#durable-task-metadata-a-seam-with-limits) |
| Promotion demotes scout spec to investigation context while retaining the original brief; later relaunch reads that brief | Source-derived integration replay hazard, not a reproduced FirstMate runtime bug. [Promotion trace](firstmate-contracts.md#q04-attachment-and-durable-instructions) |
| FirstMate's appended self-development role rule supersedes earlier role text and forbids delegation | Source contract; a brief-only exception does not solve it. [Role trace](firstmate-contracts.md#q05q06-workspace-and-role-boundaries) |
| Relaunch is a fresh conversation in the existing worktree; parent endpoint exit does not establish native-child termination | Source observation and bounded inference; native-child recovery remains untested. [Recovery trace](firstmate-contracts.md#q07-recovery-and-cancellation-are-distinct-from-durable-results) |
| Environment allowlisting retains destination-pane values; explicit CLAUDE_CONFIG_DIR forwarding is a distinct mechanism | Source observation; caller ORCHFLOWS_HOME forwarding cannot be assumed. [Environment trace](firstmate-contracts.md#q11-and-fallback-inheritance-does-not-provision-a-host) |
| Native plugin discovery is only one supported Orchflows resolution route; supplied complete roots are another | Documented contract; no FirstMate path-loading trial. [Package findings](orchflows-contracts.md#package-identity-paths-and-discovery) |
| Successful core setup deletes the prior copy, resolve does not request versions, and library dependencies are declared in prose | Source observation; retained dependency snapshots require new integration behavior. [Package freezing](orchflows-contracts.md#freezing-a-tasks-entire-input-package), [upgrade trace](orchflows-contracts.md#upgrade-and-rollback-mechanics) |
| This session uses installed Orchflows Light 0.6.3, while the copied public source is Orchflows 0.7.0 | Local manifest/skill observation; these research children do not prove that FirstMate can run the source package. [Identity findings](orchflows-contracts.md#package-identity-paths-and-discovery) |
| Root MIT LICENSE files exist in both pinned repositories, with additional selected-library notices inventoried | File inventory only; no legal compatibility conclusion, redistribution or maintainer acceptance. [Orchflows inventory](orchflows-contracts.md#distribution-facts-and-smallest-useful-scope) |

A refreshed Claude primary documentation page describes configurable nested subagents and a concurrent-subagent limit separately from tool concurrency. Current Codex documentation describes local subagents. These are **external documentation claims**, not new FirstMate worker measurements; they do not erase FirstMate's older empirical tool inventory or certify this session's installed CLIs. [Host-doc findings and primary links](orchflows-contracts.md#composition-and-native-depth). Orchflows also contains its own model/effort trial report; it is upstream-reported evidence, not a trial executed here.

### Deliverables and verification scope

New research deliverables are [FirstMate contracts](firstmate-contracts.md), [Orchflows contracts](orchflows-contracts.md), [ranked solution options](solution-options.md), [experiment plan](experiment-plan.md), and [proposed increment](proposed-increment.md). All Q01–Q16 now distinguish source answers, proposals and remaining runtime checks. Recommendations remain provisional in the decision log.

Two bounded native researchers investigated source contracts while the coordinator compared architectures and wrote the experiment/increment proposals. Their source documents contain no repairs to either upstream. The existing 31 packaging tests were not repeated: the relevant source is unchanged, and they would not close the new worker/lifecycle gaps. Documentation and pinned-reference verification are separate from runtime validation.

A fresh independent reviewer examined the joined research against the pinned sources and current primary host documentation, without making changes. It returned no material findings. The coordinator's reference check found two link defects (one local heading, one source line range), which were corrected in one repair pass. No second review was run. The final checks cover 12 Markdown documents, 78 local links/anchors and 105 commit-pinned source file/line references; they check local source identity and numeric range, not the semantic sufficiency of every citation or every external HTTP/heading target. The local check receipt is under ignored `.scratch/document-checks.json`.

Both full clones also passed `git fsck --full --no-reflogs` with exit 0 and no diagnostics. `git diff --check` passed, and the original assessment and original manifest have no Git diff. All workspace changes for this task are research Markdown/JSON records and ignored source/check artifacts. There is still no integration runtime result.


## Standalone foundation increment — September 13, 2026

### Scope and design decisions

The user authorized beginning modifications and requested a fundamental plan for a standalone variant with near Orchflows feature parity. A subsequent explicit answer restricted workflow execution to **FirstMate/Herdr only**, with Claude Code and Codex as worker harnesses. This supersedes the earlier research-only and native-crewmate add-on scope. [Decisions D10–D13](decisions.md) distinguish the user decisions from the selected, unvalidated architecture.

The [fundamental design](fundamental-design.md) keeps composition in a root crewmate and changes Work/Review into requests for FirstMate-owned component tasks. FirstMate owns admission, endpoint lifecycle, quotas, workspace allocation, reconciliation and outer delivery. Task-group requests, a component role/result disposition, group-aware parent waiting and retention need real FirstMate changes. These are proposed contracts, not capabilities inferred from existing extension bindings or unknown metadata preservation. No native fallback or separate Orchflows scheduler is selected.

### Source acquisition and implementation actually performed

Both upstream default HEADs were checked again with `git ls-remote origin HEAD`; they remained the pinned continuation revisions. A complete `git archive` of Orchflows `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a` was expanded into the owned `packages/orchflows-firstmate/` tree, containing all 1,064 original files without Git metadata. The complete ignored clone retains the original history. Existing research files were first copied and hashed into ignored verification storage.

The fork now has an independent package/catalog identity and home (`ORCHFLOWS_FIRSTMATE_HOME`, default `~/.orchflows-firstmate`). Setup protects recognized normal Orchflows homes/cores/catalogs, changes host concurrency only by explicit request, and reports package readiness separately from the unimplemented integration. Resolver alias `orchflows` resolves only the fork's core, with both names reserved against library collisions. All five core skills state the missing execution contract and stop before workflow work. No task-group schema, pretend preflight, FirstMate patch or Herdr adapter was added.

The [source inventory](foundation-state.json) records the exact candidate aggregate and every deliberate file divergence. All 1,022 files under `example-workflows/`, including their assets and notices, are byte-identical to upstream. Core host-configuration and native-history implementation modules are unchanged. Preserved examples and quoted upstream instructions are migration source, not certified runtime entrypoints. [Feature parity](feature-parity.md) inventories all core and optional behavior still to demonstrate.

### Checks actually performed and their limits

The baseline core suite ran with disposable fixture homes: Windows Python completed 61 tests (60 pass, one POSIX-mode skip); WSL Ubuntu passed all 61. The package maker ran the adapted candidate suite: Windows Python 3.14.6 completed 69 tests (68 pass, one POSIX-mode skip), and WSL Python 3.12.3 passed all 69. The eight added tests exercise isolation, alias collisions and honest readiness. The plugin manifest validator and all five core skill frontmatter validators passed. These are local packaging/history checks, not FirstMate lifecycle or optional-library feature trials.

A fresh native caller tried the exact gated dynamic workflow on an unrelated reading-list fixture. It read the gate, reported the absent task-group integration and stopped without creating the requested output, making changes or spawning children. The coordinator independently checked the unchanged input SHA-256 and missing output. This is one observed negative instruction-gate trial; it does not prove automatic discovery, sandbox enforcement or successful execution under either FirstMate worker harness. Exact identities and test records are in [foundation verification](foundation-verification.md).

Read-only runtime inventory found no Herdr executable in the inspected Windows/WSL shells. No FirstMate home or Herdr session was created, no live worker was launched, and no user plugin registration or active host configuration was changed. A prepared named Herdr lab and the actual FirstMate component seam are still needed for the first positive integration acceptance case.


One fresh independent reviewer assessed the joined foundation and plan without making changes. It found no material issues after a second pass for shared causes, independently passed all eight new boundary tests, and reverified package/source retention and candidate/design identities. No repairs were needed and no second review was run. The coordinator also checked 16 root Markdown files, 120 local links/headings and 111 pinned source-file/numeric-range references without errors. These reference checks do not prove citation semantics or remote HTTP/heading availability. Both research clones remained clean, the original assessment hash was unchanged, and the preserved assessment/source manifest had no Git diff. The package remained at the exact reviewed identity; final evidence and handoff records were then completed.


## Stage 1 implementation — September 14, 2026

The user asked to continue implementation and clarified that their authenticated host is Windows. The experimental subset is now one read-only Work component through FirstMate/Herdr, while near full feature parity remains the target. [Stage 1 contract](stage1-contract.md) records the scope and predeclared acceptance; [verification](stage1-verification.md) separates current tests from live work.

The package client, exact retained-package verification and conditional Work instructions are implemented in `packages/orchflows-firstmate/`. The FirstMate-owned controller, request/result store, launch bridge and lifecycle patches are distributed in `integrations/firstmate/`. A clean pinned FirstMate checkout can be prepared without changing `.sources/` or a live home. One accepted request consumes the component allowance even after an uncertain launch. Parent generation, component endpoint, input commit and retained report digest are recorded; native transcript identity is explicitly unverified.

Executed checks now include the 84-case package suite on Windows/WSL, 46 integration fixtures with platform skips stated in verification, fresh preparation and byte comparison, plugin/skill validation, and inherited brief/spawn/relaunch behavior suites. The long watcher suite's held-worker timing failure remains recorded despite a passing targeted baseline/candidate comparison. These are fixture results, not a claim of full lifecycle or Windows worker support.

A private Herdr lifecycle smoke test passed with the exact staged tuple in [runtime preparation](stage1-runtime.md). Initial actual Codex work returned and gathered one component result and produced a normal root scout report; subsequent repaired-candidate results are recorded below. Early real trials separately exposed mount-copy latency, disposable Codex project trust, a missing staged Codex companion executable, and fresh Claude onboarding prerequisites. None was replaced by a synthetic worker pass. Exact worker receipts and cleanup evidence belong with their runtime record.

### Source retention clarification

The current state is recorded in [stage1-state.json](stage1-state.json). All 1,064 original files remain, with six added files; all 1,022 example files are byte-identical to the pinned **local checkout**. Comparing directly with Git blobs reveals 49 example text files with checkout CRLF endings instead of blob LF endings. Earlier foundation wording that said byte-identical to upstream or a Git archive did not distinguish this checkout normalization. There are no Stage 1 edits to example content. The original dated assessment and historical foundation candidate hash are preserved; this living correction narrows the earlier provenance claim.


The joined repair added the native Windows runtime boundary and used FirstMate's existing report-reference format for component backlog closure. The original pending-close failure was reproduced before repair; real tasks-axi marker/replay checks passed afterward. A fresh prepared candidate matched all 561 files. That integration suite ran 56 cases on each platform: WSL 49 passed/seven Windows skips; Windows 36 passed/20 POSIX or dependency skips. These superseded the earlier 46-case fixture count, not the earlier native-trial identities. [Windows boundary evidence](stage1-windows.md) records the actual native controller checks and remaining Windows worker gap.

### Final review and scoped Claude repair

One fresh independent reviewer found a P1 in native Claude launch permissions: retained guidance paths were allowed by prose but absent from the actual harness Read grants. A real Claude component reproduced that prompt after a successful parent replacement. The repair adds generation-checked, task-scoped Read/Edit settings at the existing launch owner, preserving the selected mode and original settings. It received seven new checks and one repair pass; no second review was run.

The final 63-case integration discovery passed with platform skips: WSL 55 passed/eight skipped; Windows 42 passed/21 skipped. Fresh preparation reproduced all 562 candidate files. The inherited ordinary spawn-dispatch suite also passed again after the template repair, exit 0 without gate skips. [Stage 1 verification](stage1-verification.md) records durations, review scope and the exact evidence boundary. [Stage 1 state](stage1-state.json) identifies the final bytes separately from the reviewed and earlier runtime candidates.

### Final repaired native case

The final Codex trial `2oqaz0tn` completed through FirstMate in Herdr on WSL: one component, supported parent replacement, identical-request replay without duplication, correct retained report, gather by the replacement generation and normal root scout delivery. The actual result notice reached the new root inbox and was handled. Both task exits and ordinary teardowns returned 0. The original fixture and worktrees remained clean, retained-result integrity passed, and lab/sentinel shutdown left no scoped processes; the copied authentication file was removed. [Native evidence](stage1-native-trial.md) records the exact identities and reports.

The repaired Claude retry `wpgnlat8` failed before model work when its copied Windows cache could not authenticate the request, despite cached logged-in status. Its earlier Windows-cache attempt had executed actual tools and parent replacement before the now-repaired guidance prompt. Repaired Claude completion, actual native Windows workers and normal watcher stale-supervision behavior remain open. The named lab had no ordinary watcher, so owner-state polling and parent replacement do not close that last question.

## Stage 1 acceptance continuation — September 14, 2026

The user confirmed the refreshed native Windows Claude login. A bounded real native diagnostic succeeded; a subsequent isolated FirstMate/Herdr Claude Work trial completed source inspection, retained result, replay, gather and ordinary root delivery. Both task exits and ordinary teardowns succeeded, with the cleanup owner explicitly reaping leaked worktree processes, followed by successful private lab/sentinel shutdown and empty scoped process inventory. Its actual watcher also exposed a launching-request race, and Claude's background shell remained active after FirstMate classified the component unknown. Those failures are retained beside the successful Work result in [acceptance continuation](stage1-acceptance-continuation.md). No refresh token or credential file was copied into that Work trial.

The old copied Codex cache produced an already-used-refresh-token failure before model work. The authentication design now follows the owning host's supported store and avoids resetting rotating caches from old seeds. That failed fixture does not negate the earlier successful Codex tuple or imply that the user is logged out. Official guidance and exact distinctions are in the continuation record.

Native Windows probes staged official Herdr0.9.0/protocol22 and Treehouse2.0.1 binaries in ignored storage. Private endpoint and worktree operations passed; FirstMate's actual idle-shell and session-marker owners refused native observations. An attached native child stopped on workspace close; a detached child survived both workspace and lab closure, then the probe stopped that exact child through a retained Windows handle. [Native Windows evidence](stage1-windows-native.md) preserves source/release/binary identities and the required owner changes. No native Windows model worker was launched.

The 563-file continuation candidate adds positive Linux launch-transaction custody and native Windows admission/retention guards. Its full 77-case integration suite passed with platform skips: WSL67 passed/ten skipped, Windows49 passed/28 skipped. Fresh preparation reproduced every candidate byte and the eleven deployables match the manifest. Ordinary inherited spawn-dispatch and teardown endpoint-safety suites passed without gate skips. These fixture/owner results remain separate from the subsequent actual watcher observations and final review in [continuation verification](stage1-continuation-verification.md).

One fresh final independent review found the routine root signal defect also reproduced live: authoritative task-group waiting failed the no-verb working predicate, causing an unnecessary watcher wake. The single repair pass accepts group waiting only in that signal owner, preserving actionable-status precedence, secondmate routing and the general working proof. Four new regressions reproduce the prior rejection and pass repaired. Full final discovery ran 81 cases: WSL71 passed/ten skipped; Windows49 passed/32 skipped. No second independent review was run.

Final Claude trial `ed3tuvcz` on the repaired 563-file candidate passed actual ordinary watcher supervision: 20 waiting classifications over 345.56 seconds, matching same-watcher/root-waiting/child-working samples and an advancing beacon. The routine progress signal was absorbed; the only wake was the legitimate group-ready result. Complete native reads preceded gather, the retained and ordinary reports were correct, source/worktrees stayed clean, and all ordinary cleanup operations succeeded with no scoped processes remaining. The cleanup owner reaped residual worktree shells; this is not a claim that endpoint closure alone retired them. No drain/rearm or credential-file copy was used. Parent replacement was not repeated in this final trial, and background-tool/native Windows/full-parity acceptance remain open. [Final verification](stage1-continuation-verification.md), [exact runtime evidence](stage1-acceptance-continuation.md).


### Linux-first development and actual current-package Work

The user changed the development priority to Ubuntu/WSL, Linux first. Native
Windows owner work is deferred; its earlier evidence and admission refusals
remain. A new Linux runner validates the source pin, stages native LF/symlink
checkouts and exact owned bytes on ext4, reproduces the FirstMate distribution,
and isolates both fixture suites from host configuration and authentication.

The owned package remains dev.3 at Orchflows ca72258493480ddcfe73b3f01d0475ad532e4726.
The new FirstMate patch selects the per-launch native Claude foreground profile.
All 84 package tests passed; all 72 Linux integration tests passed with ten
explicit Windows skips. The runner also refused a Windows-mounted staging
directory and a Windows PE executable. These checks are fixture evidence.

Separately, actual Claude trial pzzebeug ran the new 563-path candidate and
current package through FirstMate/Herdr on Ubuntu. Both native workers had the
FirstMate-supplied foreground profile. One component, same-child replay, correct
retained output and ordinary root report passed. The same ordinary watcher
recorded 20 waiting classifications over 383.632 seconds without an active-work
wake. Full native report/result reads preceded gather. Normal task/lab/sentinel
cleanup returned zero and left no scoped processes; the owner reaped residual
worktree shells. The logs preserve post-result watcher-down/pending-wake
warnings; a complete supervisor drain/rearm loop was not tested. No private
credential file or copied refresh token was used.

See [Linux verification](linux-first-verification.md) and [exact state](linux-first-state.json).
Parent replacement, Codex watcher acceptance, native background tools, Review,
writers and wider feature parity remain open. No separate agent review was
performed for this increment. Active installations and pinned research files
were not changed; design-loop was not used.


## Dev.4 Review and Linux recovery — September 14, 2026

The user explicitly requested Orchflows dynamic workflow for this development.
The upstream skill at ca72258493480ddcfe73b3f01d0475ad532e4726 was applied:
three fresh makers with separate file ownership, joined checks, one fresh
independent Review and one repair/check pass. Design-loop was not used.
This development process is separate from the fork's still-gated dynamic runtime.

The owned dev.4 package retains all 1,081 upstream paths in 1,088 files.
FirstMate now admits one Linux Review/explicit-audit attachment alongside the
legacy Work/none profile. Review binds the frozen clean input, package,
primitive, metadata and result, uses a fresh fleet component with Review
guidance, and leaves repairs and root delivery outside that component.
The controller/client do not dispatch native child workers.

Final Ubuntu/ext4 checks passed 99 package, 90 integration and 13 driver tests,
with ten explicit native Windows skips. Preparation reproduced the 564-path
candidate from thirteen inventoried deployables. The independent review found
the overlong private socket path/missing failure diagnostics and a repeated
gather timestamp that could hide early acknowledgement. The repair adds short
paths and capacity admission, scrubbed operation failure logs, and a durable
first acknowledgement timestamp that survives current-generation re-gather.

The first actual attempt failed before worker launch because of socket length;
ordinary cleanup passed. The long Review retry completed one component, exact
replay, full native reads before its single gather, correct reports and root
delivery. Its original receipt failed only on a wrong observer status label.
That receipt is preserved. The repaired parser's separate assessment passed
23 positive waiting/working samples over 395.338 seconds; the actual watcher
trace independently contains 20 waiting classifications over 382.435 seconds.
The same repair/check pass added a regression against actual owner output.

The final repaired candidate passed real Claude Work parent replacement
a-7ysafo1o and explicit Review a-w469d47l. Both passed full reads before gather,
same-child replay, retained identity, clean inputs/worktrees, ordinary root
delivery and all task/lab/sentinel cleanup, leaving no scoped processes.
The replacement root gathered under its new generation and read/handled the
actual result inbox notice. These final cases used a zero required steady
watcher span; they do not repeat the long uninterrupted watcher measurement.
Selected live process observations confirmed FirstMate's foreground profile.
No authentication file or refresh token was copied, and active profiles were
unchanged.

[Review verification](review-verification.md) and [exact state](review-state.json)
preserve candidate, package, driver, runtime and receipt identities separately,
including original failed receipts and the observer-only reassessment.
Native Windows remains deferred. Codex Review/watcher acceptance, native
background tools, full supervisor drain/rearm, writers, multi-component joins,
nested composition and optional-library parity remain open.


## User clarification and next-session handoff — September 14, 2026

After dev.4, the user clarified that the goal is a plug-and-play upgrade through
which FirstMate uses Orchflows' Work/Review primitives, dynamic workflow and
custom/meta-workflows. Existing FirstMate systems should provide subagents,
workspaces, communication, supervision, recovery and delivery; Claude/Codex
handling stays with FirstMate. The user rejected the emphasis on building these
mechanisms and treating harness integration as the main work.

This is a product-direction clarification, not new runtime evidence. The next
implementation priority is to map and simplify the experimental adapter against
existing FirstMate owners and wire normal skill/workflow availability, with
targeted compatibility checks. D26 and the current [handoff](../HANDOFF.md)
record it. The [previous handoff](../HANDOFF-through-dev4-2026-09-14.md) is preserved
byte-for-byte as historical context; its next-work queue is superseded.
This handoff update changed documentation only and did not repeat or relabel
dev.4 tests or trials.

## September 14 continuation: normal launch and retained custom workflows

**Observed source:** the [owner mapping](firstmate-owner-mapping.md) traces the
actual pinned FirstMate owners and audits every baseline added helper/record.
It distinguishes necessary parent/request/result provenance from authoritative
FirstMate task state and identifies policy work still needed for full dynamic
composition.

**Implemented:** dev.5 adds project enablement, complete retained custom
libraries, ordinary scout spawn attachment and immutable client context through
existing spawn/relaunch. A capability declaration preserves legacy dev.4
invocations. No separate dispatch, recovery, supervisor or Herdr control path
was added. Custom skills currently compose one admitted read-only primitive.

**Executed checks and actual workers:** [normal launch verification](normal-launch-verification.md)
and [exact state](normal-launch-state.json) contain the joined/repaired test
counts, one independent review, one repair pass, exact candidate identities,
private worker trial receipts and cleanup outcomes. Earlier receipts and the
dated assessment are unchanged.

**Still unverified/unimplemented:** full dynamic/multi-component and writer
composition, broad custom/meta and optional-example parity, current actual
Codex normal-launch behavior, and the lifecycle gaps carried in the handoff.
Package readiness remains package-only.


## September 14 continuation: bounded dynamic composition

**Observed source and implemented glue:** [dynamic contract](dynamic-composition.md)
extends the completed owner mapping. Existing FirstMate spawn/Treehouse owners
allocate and position components; the request/result owner preserves multiple
assignments, clean writer commits and archival Git refs. The root uses ordinary
Git joins and requests one exact-candidate Review. Policy changes live at AGENTS
and fm-dod; root delivery and no-mistakes custody remain distinct. Custom skills
compose the same retained primitives, with no workflow-specific runtime.

**Executed evidence:** [dynamic verification](dynamic-verification.md) and
[exact state](dynamic-state.json) contain the reviewed/repaired checks, the one
independent development Review, its three concrete findings and the single
repair/check pass. Real dynamic/custom trials and failures are recorded under
the actual candidate and driver identity. A successful fixture or copied skill
is not live parity.

**Remaining scope:** ordinary scout report delivery is not ship code delivery.
Ship/local-only delivery, nesting, Build/SelfImprove, current actual Codex
composition and the remaining lifecycle/release gaps stay open. No active
installation, rotating cache or pinned source was changed; design-loop was not
used. Historical verification and the original dated assessment remain intact.

**Final dev.6 execution:** 124 package, 142 Linux integration and 19 driver checks
passed (ten explicit native Windows skips). Final actual Claude trial a-x6osytu8
passed all seventeen acceptance checks without intervention: two writer results,
ordinary replacement while one Work remained running, retained custom requirements,
exact joined Review, final tests after gather and normal completion/cleanup. Both
writer refs survived teardown and the scoped process inventory was empty. Earlier
failed and manually assisted trials remain recorded separately.

## September 14 continuation: ordinary local-only root delivery

**Dependency and source:** the user requested waiting for the in-flight PR.
PR #3 merged as d465c1a4d90e7144137a08073a79e5fd9c2cf451 before this increment
began. FirstMate remains pinned to b182d0f908b78d08c7ccb8dce3775bdca8c5d657;
dev.7 retains all 1,081 upstream Orchflows paths. The original dev.6 handoff is
preserved byte-for-byte as [historical context](../HANDOFF-through-dev6-2026-09-14.md).

**Implemented owner glue:** explicit dynamic ship/local-only selection adds an
immutable root delivery binding and capability negotiation. Components retain
their parent-return contract; the root follows the existing brief, ready branch,
merge-local and teardown owners. Default ships remain ordinary. Unsupported
selected delivery profiles refuse. No new dispatch, workspace, recovery, merger
or no-mistakes run parser was introduced. [Local delivery](local-delivery.md)
defines the exact admission and cleanup contract.

**Executed development checks:** one fresh independent Review found that a
worktree branch switch could hide an unlanded promised branch during cleanup.
The single repair/check pass validates that retained ref and repository and
preserves existing detach/slot-return retry behavior. Actual ordinary spawn
then exposed a check that ran before worker-side branch creation. The same
repair pass now allows only pristine detached input during initial launch,
with strict later client/relaunch/delivery checks. No second development Review
ran. The final candidate passed 128 package, 154 Linux integration and 23 driver
tests: 305 passed checks, with ten explicit native Windows skips.

**Actual runtime evidence:** two authentication preflights refused insufficient
token lifetime without workers. Attempt a-rn6116ra passed authentication but
ordinary spawn rejected the branch before worker creation; that source gap was
corrected. Its original receipt remains unchanged.

After the user refreshed Ubuntu authentication, a-lf4thn46 ran on Sonnet 5/high
as explicitly requested. Two writers, root replacement while one maker ran,
retained custom-skill rereading, exact joined Review and post-Review checks
produced the correct ready branch. Its original driver receipt failed because
the observer misparsed a normal trailing 2>&1 redirect on the first gather.
Full native reads preceded both that call and durable acknowledgement. A narrow
observer correction passed all 25 pre-landing assertions on the preserved trace.

The exact ready commit then landed through the existing merge-local owner.
After restoring structured endpoint inspection through the same private lab
owner, ordinary cleanup succeeded. All six delivered-code tests pass; both
writer refs survive and no scoped processes remain. These administrative
follow-ups ran no additional models. The final evidence adds ordinary landing
as the 26th assertion and records cleanup/code/ref checks separately. This is
a documented corrected assessment and resumed delivery, not an uninterrupted
final-driver pass. Original failed and follow-up receipts retain separate hashes.

[Verification](local-delivery-verification.md) and [exact state](local-delivery-state.json)
keep reviewed, cleanup-repaired and final candidate identities distinct.
Current Codex composition, direct-PR/no-mistakes, nested/meta authoring and the
remaining lifecycle/release gaps remain open. Pinned references, active
installations and rotating credential caches remain unchanged; design-loop
was not used.
