# Stage 1 native trial evidence

This is the executed WSL native-worker trial record, distinct from package checks and the server-only smoke in [stage1-runtime.md](stage1-runtime.md). The scoped target is one normal FirstMate root scout using the attached Orchflows Work client to submit one FirstMate-owned component, gather its retained result, and incorporate it in the ordinary root report. These observations do not establish native Windows support or production readiness.

The final repaired candidate passed the native Codex Work, identical replay, parent replacement, current-generation gather, normal scout report and ordinary teardown case. Claude authenticated and reached a real component/replacement on an earlier candidate, exposing a path-scope defect; the repaired Claude case was then blocked by an expired copied authentication cache before tools ran. Actual watcher behavior across its stale interval remains unverified.

## Fixed inputs and isolation

The candidate derives from FirstMate commit `b182d0f908b78d08c7ccb8dce3775bdca8c5d657` with the Stage 1 controller, overlays, and existing-owner patches described by `integrations/firstmate/manifest.json`. The trial's manifest SHA-256 is `077541f8d7b0e45bd1cffd11338b849302c01ebc154ce773fcefabc2d72284d5`. The attached standalone package identifies as `0.1.0-dev.2`; each successful attachment below retains its own complete immutable package snapshot. The full 1,070-file source inventory is copied byte-for-byte into private Linux storage before attachment, avoiding repeated Windows-mount metadata traffic. The owner attachment digest observed in these attempts is `0107a84d7073defd9d858140770e9072f02db38dcda91b3e307c8e6bdec159d4`.

The fixture is a new local Git repository without an origin. Its deterministic commit is `594d8ccf264e78965e75450be4aa0de5d45fa683`:

| File | Source fact | SHA-256 |
| --- | --- | --- |
| `stock.py` | Lines 3–4 define `total_units(counts)` as `sum(counts)`, so an empty list returns `0`. | `952f3ca5263d22e9268c6bd6df405c2cb43dfddb7b34b4fdeb0f719673d5968e` |
| `labels.py` | Lines 3–4 define `normalize_code(value)` as `value.strip().upper()`, so `' ab-7 '` returns `'AB-7'`. | `583010ccec3aaacf6ab984aa055fea724cc768de58d1f02c8bbdfed8e4936df8` |

Each run has a new private `/tmp/fm-n1.<random>/` namespace, mode 0700, with explicit HOME, CODEX_HOME, CLAUDE_CONFIG_DIR, XDG_CONFIG_HOME, XDG_STATE_HOME and Linux-only PATH. Only the two explicitly authorized authentication files are copied into the private stores, mode 0600; Codex uses the native Linux cache and the Claude source is identified per attempt below. No credential contents or hashes are emitted or retained in repository evidence. The original profiles, user default Herdr namespace, and host settings are untouched. The copied files are removed after owned workers and sessions stop; FirstMate endpoint-exit refusals remain recorded separately from successful named-lab teardown and identity-proven private sentinel stop.

The original pinned `fm-herdr-lab.sh` owns generated `fm-lab-*` sessions. Its default-session tripwire is satisfied by a private default sentinel with the source-proven XDG socket/config isolation documented in [stage1-runtime.md](stage1-runtime.md). Its PID/start identity, executable, working directory, and arguments are compared before explicit stop. Ordinary task teardown is allowed to refuse incomplete work; no forced discard is used to manufacture a completed lifecycle.

The runtime tuple is Ubuntu 24.04.4 under WSL2, Herdr 0.7.4/protocol 16, treehouse 2.0.1, jq 1.8.1, tasks-axi 0.2.5, Node 24.15.0, Codex 0.152.0, and Claude Code 2.1.269. Both harnesses use the same source assignment and their native Linux executable. The root is launched through `fm-spawn --scout --backend herdr --harness <harness>` after `fm-task-group.py attach`. Its model receives the retained Work skill/client contract, the exact two-field request, an identical replay requirement, and the normal scout completion policy. The component is instructed to wait before inspection (25 seconds in the first Work case; 60 seconds in replacement cases), write only its recorded tasktmp report, and complete through FirstMate's component owner.

## Preparation failures observed

| Attempt | Actual observation | Consequence and cleanup |
| --- | --- | --- |
| `fm-n1.eo0ah7d2` | Attachment exceeded the runner's 90-second limit while copying/inventorying the 39 MB package from the Windows mount. No root worker launched. | Exact native Linux package staging and a 300-second preparation limit were added to the disposable runner. Named helper teardown and private sentinel stop exited 0; final isolated session inventory showed only stopped default; credential copies removed. |
| `fm-n1.cuctkvwi` | Attachment succeeded; Codex root spawn exited 0 but the native CLI stopped at its initial repository trust prompt. Codex identified the original fixture Git root behind the treehouse worktree. | FirstMate source pre-registers Claude trust but has no equivalent Codex trust helper. The retry writes a trust entry for only the known-clean private fixture root, as explicit fixture setup. FirstMate exit succeeded; ordinary teardown correctly refused the missing report. Lab/sentinel stopped and credential copies removed. |
| `fm-n1.wykz8z30` | Codex passed trust and the actual worker model started (`gpt-5.6-sol`, default). Both command-tool attempts failed before starting a shell because `codex-code-mode-host` was absent beside the staged Codex binary. No Work request was dispatched. | The main CLI archive contains only the main executable; its separate matching companion asset was staged. FirstMate exit succeeded, missing-report teardown refused, lab/sentinel stopped, and credential copies were removed. |

The private Codex trust prerequisite uses documented `projects.<path>.trust_level = "trusted"`; this is fixture configuration, not a claim that the product automatically handles first use. [Official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

The companion comes from the [same official Codex 0.152.0 release](https://github.com/openai/codex/releases/tag/rust-v0.152.0): `codex-code-mode-host-x86_64-unknown-linux-musl.tar.gz`, archive SHA-256 `449cefe35b9f347e3fdbf121e816339b37825eb0bfee7de8298a0a61b6687cba`, extracted static-pie ELF SHA-256 `e1b6c563a63fd1388690294400ac2744a066ee0291179cb9b715db86ae022ac6`. Its archive digest matched the official GitHub release asset metadata before extraction.

The ignored runner is `.scratch/stage1-runtime/native-trial.py`; each attempt writes a bounded receipt and task metadata/report artifacts beneath `.scratch/stage1-runtime/native-trial-<namespace>/`. Harness profiles, conversation history and authentication material stay outside that evidence directory. Result observations from the corrected native attempts follow below.

## Native Codex Work result

Attempt `fm-n1.77u7j2e7` executed the requested root-to-component Work flow. The real root used the retained package client to submit the exact request, repeated the identical request, read the complete retained component report and identity, gathered it, then wrote its ordinary scout report and appended `done`. Its report correctly explains both source facts above with line references. Metadata identifies a native Codex scout root and one native Codex component under one explicit Herdr session; neither task used a substitute orchestrator.

| Evidence | Recorded value |
| --- | --- |
| Root | `native-codex-77u7j2e7` |
| Root generation | `s1789359273.368954.14166` |
| Root endpoint | `fm-lab-native-codex-362874-24674:w1:p2` |
| Request | `inspect-fixture-v1` |
| Request body digest | `5f6d03d3a020e39aff979f39cef3b8d4754e9361a76436d1035d679749d19628` |
| First submit and identical replay child | `tg-a01231c4e463e7080769` |
| Child generation | `s1789359326.395643.24168` |
| Child endpoint | `fm-lab-native-codex-362874-24674:w1:p3` |
| Final owner state | `complete`, `gathered: true`, exactly one component metadata record |
| Retained result digest | `e3007002007f1782871a93992086137e8d8f19429492147545a4c708e40a887a` |
| Retained report digest | `2407eb4146ebcdc0fbb3b6f442f05ee53da0717cc573bf978d98cf63a2466b96` |

The original fixture remained clean at its fixed commit. Completion checked the component worktree's clean commit through the owner; the normal root report also records an empty `git status --short`. The result explicitly leaves `native_session_id` null: native model/tool activity was observed through the bounded FirstMate endpoint view, but no native transcript identity was verified or copied.

An observer error briefly advanced the Claude launch when Codex emitted a turn-ended notification while still processing. Claude remained parked at onboarding without model work. The final cleanup capture, `postcheck.json`, retained reports and owner state establish the Codex outcome; the earlier receipt sample stating `ended_before_work_request` and `source_facts_present: false` was not a final observation. That shortcut was removed before subsequent single-harness attempts. This attempt is not presented as a strictly sequential two-harness comparison.

Cleanup exposed an actual integration defect. FirstMate exit returned 0 for both Codex tasks, and root teardown returned 0. Component teardown returned 1 because the existing backlog-close owner rejected the component's pending-close arguments. The owner preserved all durable component records. No force/discard option was used. Both named labs and the identity-proven private sentinel then stopped successfully; a separate scoped process check found no remaining processes in this namespace, and the credential copies were removed. The ignored receipt preserves the exact pending-close diagnostic. The isolated lifecycle repair and its later native regression are separate from this initial result.

## Native Claude startup boundaries

In `fm-n1.77u7j2e7`, Claude Code 2.1.269 initially stopped at its theme/onboarding picker. The verified binary's startup guard checks `hasCompletedOnboarding`; the private fixture therefore received only `hasCompletedOnboarding: true` and `theme: "dark"`, preserving FirstMate's trust entries. No user profile was copied. FirstMate relaunch refused after its exit protocol could not confirm the onboarding process had stopped within 30 seconds. The original instructions were restored, and the named lab later stopped through its owner. No direct endpoint bypass was used.

Fresh attempt `fm-n1.2xu3b1uq` set those private preferences before launch. FirstMate spawn returned 0 and Claude reached the normal task prompt in auto permission mode. Its first model request immediately displayed `Login expired · Please run /login`, followed by `Not logged in`. The verified binary maps this message to an OAuth session that expired and could not be refreshed. No Work request was accepted. The prior `claude auth status` exit 0 and `loggedIn: true` were cached-status evidence only, not successful model authentication.

This attempt used the existing native Linux credential cache and does not establish the state of the user's Windows authentication. FirstMate exit returned 0; ordinary teardown refused the absent scout report. Named-lab teardown and private sentinel stop returned 0, the scoped process check was empty, and copied credentials were removed. A later Windows-cache-copy trial is a separate credential-source experiment; it does not reuse or mutate the Windows profile.

## Joined candidate: native Claude replacement and path-scope failure

Attempt `fm-n1.bv6q_bdf` used a fresh prepared candidate with the backlog-close repair and Windows runtime boundary. Its integration manifest SHA-256 is `84bdd5ffb900f315561ec5bb437c7d7597430b955264b531b71427cfaab0cb2f`. The observed source inventory contains 561 files excluding Git administration, digest `4582d5f710096e6bd2a7b93f31a67c261f00ee5dc49227f0a65b7d0032fd0bbd`. The 1,070-file package inventory digest is `22aa3ab770812157cadee44e65380aae09dbf3ec8e0e38346c316e141c1ca0b7` after the provenance wording update. These inventory digests hash the UTF-8 JSON list of sorted relative-path/SHA-256 pairs; the owner attachment uses its own canonical inventory digest.

This attempt explicitly copied the authorized Windows Claude credential file into the private Linux profile. The real Claude worker authenticated and executed tool commands, resolving the prior Linux-cache authentication gap. A real component was admitted, and FirstMate successfully replaced the parent while retaining that component:

| Evidence | Recorded value |
| --- | --- |
| Root | `native-claude-bv6q_bdf` |
| Accepted parent generation | `s1789360513.422177.4405` |
| Replacement parent generation | `s1789360581.426267.23354` |
| FirstMate relaunch | Exit 0; same explicit root endpoint |
| Retained child | `tg-7dc5da8056705979e33b` |
| Child generation | `s1789360563.424105.25613` |
| Final component count | 1 |
| Final Work state | `launched`, not complete or gathered |

The component stopped at Claude's first outside-directory Read prompt while opening the retained package's `guidance/code.md`. Auto permission mode alone did not declare that path readable. The verified binary opens this prompt only for an `ask` permission result whose reason is `workingDir`. No broad UI allowance, private permission bypass, alternate worker, or fabricated report was supplied. This is a product launch-wiring gap; it is not a successful completed Claude Work case. The child had not yet reached its requested observation delay.

The supported repair direction is a per-launch `permissions.allow` rule for the exact retained package and task metadata paths using absolute `Read(//path/...)` syntax, plus narrowly authorized tasktmp output rules where needed. `--add-dir` also extends editing access, so it is broader than a read grant. Existing feedback/attribution settings and FirstMate ownership must remain intact on both initial spawn and relaunch. [Official permission rules and directory semantics](https://code.claude.com/docs/en/permissions).

Both native Claude endpoint exits returned 0. Both ordinary task teardowns correctly refused the ungathered work and preserved durable records. The named lab and identity-proven sentinel stopped with exit 0; the scoped process scan was empty and credential copies were removed. The original fixture and both worktrees remained clean. The planned Codex case did not start, preserving strict sequence before the next repaired candidate.

## Repaired candidate and renewed Claude authentication failure

The next prepared candidate has integration manifest SHA-256 `78d8c553eeafd51bfb14c33189d003ef96d172aacd5bd5d0e2c58e86339a80eb` and 562 source files. Its JSON path/hash-pair inventory digest is `d72ebcad9cc1a8ca6c0e6e6999bdd27eb2de14f3d4a1175b5840a9c4be4a428a`. The package's bytes and owner attachment digest remain unchanged from the joined candidate above. The source repair adds task-scoped Claude read/output rules to the existing per-launch settings after current metadata publication, preserving auto mode and the existing attribution/feedback settings. Product tests for that repair are coordinator evidence, distinct from the native outcomes here.

In attempt `fm-n1.wpgnlat8`, a new copy of the same authorized Windows Claude credential file passed cached `auth status` but returned `Login expired · Please run /login` on the first actual model request. No tools or Work request ran. This does not erase the observed successful authentication/model tools in `fm-n1.bv6q_bdf`, and it does not establish user-wide logout. It establishes that this fresh copied cache could not authenticate/refresh for this attempt. No additional login, secret inspection, or broader profile copy was attempted.

FirstMate exit returned 0; ordinary teardown correctly refused the absent report. Named-lab teardown and identity-proven sentinel stop returned 0, no scoped processes remained, and credential copies were removed. The repaired Claude Work flow, including the new read grants through completion/gather, remains unverified by a successful native run. Codex was then tested separately against the same frozen repaired candidate; its trial copied only the Codex authentication file.

## Repaired native Codex replacement case: passed

Attempt `fm-n1.2oqaz0tn` used that exact repaired candidate and unchanged package. Its frozen disposable runner source SHA-256 is `73f32da8377daf003847355346cff8ee577f4f21da7208f30ec33cdbd0114594`. The model received the same two source questions, with an initial 60-second component delay. Native Codex 0.152.0 executed the real parent and child; the observed root model was `gpt-5.6-sol` with default FirstMate model/effort controls. Only the native Linux Codex authentication file was copied for this single-harness case.

| Evidence | Recorded value |
| --- | --- |
| Root | `native-codex-2oqaz0tn` |
| Accepted parent generation | `s1789361675.471074.32539` |
| Replacement/completing parent generation | `s1789361750.478280.8920` |
| Root endpoint | `fm-lab-native-codex-470947-28313:w1:p2` |
| FirstMate parent relaunch | Exit 0 while the accepted request remained `launched` |
| Request | `inspect-fixture-v1` |
| Request body digest | `b37773a934dab473d6a54739cb11ae925745a592534282ce2afc2ecaac78d415` |
| Original and replay child | `tg-e6ecb6703ffc6aaf0fe2` |
| Child generation/endpoint | `s1789361734.475220.7559`; `fm-lab-native-codex-470947-28313:w1:p3` |
| Final component count | 1 |
| Final owner state | `complete`, `gathered: true`, gathered by replacement generation `s1789361750.478280.8920` |
| Retained result digest | `7d1bd2b26db33bdc1b6044ab35428d45bb07e3653f548ac69b203be0c6da9b91` |
| Retained component report digest | `31c5780b78efd53bd59ee2702c3fb020372a416db6f3236c12625ce1dbbd9db2` |
| Normal root report SHA-256 | `790d8af903705692ea1a86fe4154514ad72c275f8e7851236a38484177a2b78d` |
| Work interval, including parent replacement | 249.62 seconds |

The replacement root read its current metadata, reused the existing request file and retained package client, and submitted the identical request. The response retained the original child identity and generation. After completion it read the full retained component report and result identity, gathered using its current generation, then wrote the ordinary root report and `done` status. Independent inspection of both reports confirms the correct `0` and `'AB-7'` conclusions with source lines 3–4. Independent checksum verification matched the retained report and result against the owner's digests. The original fixture and both allocated worktrees had empty final Git status at the fixed input commit.

Notification was actually observed: FirstMate delivered its retained-result notice to the replacement root's inbox; the root read `001.msg` and moved it to `handled`. A bounded direct read of the handled 298-byte message showed the exact result digest above before ordinary teardown removed that inbox. Its `schema=fm-task-inbox.v1` and timestamp `2026-09-14T04:57:17Z` were observed. This is delivery/handling evidence, separate from watcher behavior. The parents polled the retained client while the request was pending; no normal watcher was configured, and the normal stale interval was not deliberately crossed and observed. The watcher-down guard notices do not establish a pending-join classification or stale-alarm acceptance result.

Ordinary cleanup passed: both FirstMate endpoint exits returned 0, both task teardowns returned 0, and the repaired component backlog close recorded a done row linking to the parent-retained report. The root backlog row also closed with its ordinary report, and no task metadata remained. The existing teardown owner reaped its identified leaked worktree processes; the operator did not use a `--force` task discard or substitute endpoint kill. The named-lab helper and identity-proven private sentinel stop returned 0, the final isolated session list contained only stopped default, the scoped process scan was empty, and the copied Codex authentication file was removed.

The ignored evidence directory contains the frozen runner, receipt, complete normal root report, complete retained component report and result JSON, attachment/request/endpoint metadata, and `backlog-after-teardown.md`. The result continues to leave `native_session_id` null: no native transcript identity or conversation history was claimed or copied. Repaired Claude completion/gather and normal watcher stale supervision remain open acceptance items; the Codex replacement result does not close them.
