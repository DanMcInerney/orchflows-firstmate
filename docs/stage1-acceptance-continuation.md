# Stage 1 acceptance continuation

This record continues the [native trials](stage1-native-trial.md) without changing that historical evidence. It targets repaired Claude completion and actual normal FirstMate watcher behavior. The experimental scope remains one read-only Work component; these checks do not certify native Windows workers or broader feature parity.

The final repaired Claude attempt, `ed3tuvcz`, completed the Work/read-before-gather/report/cleanup flow and kept the original normal watcher active across 345.56 seconds of positively observed component activity. Earlier failures and fixture limitations remain recorded below with their own frozen inputs.

## Claude prerequisite check

The first read-only Windows filesystem probe on September 14, 2026 found the already authorized Claude credential source as a regular 914-byte file, last written September 13 at 14:58:18 UTC. That timestamp preceded the recorded `wpgnlat8` failure. It was an observation of that file at that moment, not evidence that the user was logged out.

The user confirmed being logged in. A subsequent bounded native Windows diagnostic saw a newer source timestamp, September 14 at 11:39:51 UTC. The installed Claude Code 2.1.270 completed an actual one-turn model request and returned `AUTH_OK`, exit 0, in 3.08 seconds. This diagnostic used one private exact cache copy in an access-controlled temporary directory, empty settings sources, safe mode, no tools, no MCP servers, disabled skills and no session persistence. The copy was removed after the process exited; a scoped Windows process check found no remaining process. It proves authentication for that native diagnostic, not FirstMate/Herdr completion or Windows worker acceptance.

That successful authentication removed the basis for asking the user to log in again. Subsequent Work acceptance uses a different, explicitly authorized test-authentication design: only the current Claude access token is held in memory and passed through `CLAUDE_CODE_OAUTH_TOKEN` in the private Herdr process environment. No refresh token or credential file is copied. Its safe expiry metadata must leave at least 1,200 seconds at trial start; the runner stops before expiry rather than refreshing. The ordinary watcher receives no token in its environment or diagnostic trace. Claude documents this environment variable as session access-token authentication whose value remains in use unless `/login` is invoked. The trial never invokes login. [Official Claude environment-variable contract](https://code.claude.com/docs/en/env-vars).

## Fixed ordinary watcher acceptance

Each trial uses the exact frozen candidate identified in its own section; [stage1-state.json](stage1-state.json) identifies the current prepared candidate. Both complete source inventories are copied into private Linux storage and compared with their recorded aggregate hashes before execution. The existing verified WSL binary tuple and source-owned named Herdr lab procedure remain as documented in [runtime preparation](stage1-runtime.md). The first model attempt used a native Codex cache copy; subsequent Claude attempts use only the session access token described above.

The initial attempts through `lvshcu9v` used these frozen identities; later repairs retain them as historical trial inputs:

| Input | Identity |
| --- | --- |
| FirstMate base | `b182d0f908b78d08c7ccb8dce3775bdca8c5d657` |
| Integration manifest | `78d8c553eeafd51bfb14c33189d003ef96d172aacd5bd5d0e2c58e86339a80eb` |
| Prepared FirstMate, 562 files | `5072cf224d4b45677fef3d0d9b6efdacdac755e694c57ecd5d0c9c71d4a24af2` |
| Package dev.2, 1,070 files | `a3cd1cddf0098ed0462ebf62fd8802dfc7cb92ddd29c9a8007fb1e2f97706c8e` |

Tree digests use the state document's sorted POSIX relative path, NUL, file SHA-256 and LF aggregate. No file contents were changed during native execution.

The actual `fm-watch-arm.sh` owns the ordinary watcher as a tracked child in the private FirstMate home. No away-mode marker, fabricated backend response, substitute component, user watcher, or user default Herdr session participates. A diagnostic Bash trace records selected actual watcher function/classification lines, while the ordinary arm, singleton lock, beacon, backend reads and durable wake owners remain unchanged.

Acceptance was fixed before launch:

- Keep the default 15-second poll, 240-second stale escalation interval and 3,600-second busy-turn bound.
- Give the real component a 330-second initial shell sleep, then require its source findings and retained report through the normal component completion contract.
- Observe the actual watcher classify the root as waiting for an active component across at least 240 seconds, with a live watcher and advancing beacon.
- Require no stale or group-attention wake for the root during that interval of proved child activity; retain any unexpected wake rather than silently rearming it away.
- Require the retained result, identical request replay, current-generation gather, correct ordinary root report and ordinary cleanup, with scoped process inventory empty and copied credentials removed afterward.

The component's ordinary supervision remains active. Crossing the 240-second stale threshold does not test the separate 3,600-second busy-turn bound. The trial does not repeat parent replacement, already established by the previous repaired Codex case.

## Execution

Disposable scripts, selected traces and receipts live under ignored `.scratch/stage1-runtime/`; harness profiles and authentication files are excluded from retained evidence.

The initial `t81r5ag1` preflight stopped before any credentials or runtime launch because the disposable runner sorted filesystem Path objects instead of the state document's POSIX strings. The file inventories matched; recomputing with the documented sort produced the expected package hash. Only the runner was corrected. The receipt shows no remaining scoped processes, no running session and no credential copies.

Attempt `gihzfr9y` then reproduced all 562 candidate files and 1,070 package files, matching their state aggregates. The real ordinary watcher started with a fresh beacon and confirmed defaults `POLL=15`, `STALE_ESCALATE_SECS=240`, `BUSY_TURN_MAX_SECS=3600`. FirstMate launched Codex root `native-codex-gihzfr9y`, generation `s1789386202.486930.14007`, at `fm-lab-acceptance-codex-486327-1768:w1:p2`.

The copied native Linux Codex cache passed cached login status but failed before model work because its refresh token had already been used; the connector also returned HTTP 401. No Work request or child was admitted. The actual watcher classified the endpoint as unknown and durably queued `stale: fm-lab-acceptance-codex-486327-1768:w1:p2`, then exited normally through the arm owner. This is actual normal-watcher attention evidence for an unavailable root, not a pass for waiting-component suppression across 240 seconds. The frozen acceptance-runner SHA-256 is `8f194116f3cfdac3b610d891086c9fae855e173de65258347775289346839722`.

The runner was interrupted to avoid idle retries and ran its ordinary cleanup: FirstMate endpoint exit 0, report-less scout teardown correctly refused, named-lab teardown 0 and private sentinel stop 0. The scoped process inventory was empty, only a stopped private default session remained, and the copied Codex credential file was removed. Durable incomplete task and wake records were preserved.

## Authentication design correction

The old copy/run/delete authentication fixture was insufficient for rotating OAuth credentials. Official Codex guidance requires keeping the refreshed cache for later runs in one machine or serialized workflow stream; resetting every attempt from the original seed discards the replacement token. Token rotation is a source-backed explanation for the observed already-used failure, but these receipts do not identify which process rotated it. No credentials were written back or symlinked to an active profile, and no further Codex cache experiment was attempted. [Official Codex account-authentication guidance](https://learn.chatgpt.com/docs/auth/ci-cd-auth).

Normal pinned FirstMate explicitly forwards the existing Claude configuration directory so workers use the same selected native credential/configuration store. Its launch-environment contract also describes ordinary use of the host user's provider store, with explicit custom-store variables when required. It does not prescribe cloning OAuth refresh tokens into disposable homes. [Pinned Claude launch owner](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-spawn.sh#L4070-L4078), [pinned launch-environment contract](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/configuration.md#L363-L406).

## Claude Work and watcher attempt

Attempt `lvshcu9v` uses the same exact candidate/package and frozen acceptance runner `0d0c9faafc30eb05866631e7521959ed922488aa23d145df982d6368b7502aa6`. The access token had 28,242 seconds of remaining lifetime at startup. The real Claude root authenticated, read the retained Work skill, submitted the request and confirmed the identical replay. No credential file or refresh token was copied.

The ordinary watcher exposed a launch-admission race. Request `inspect-fixture-v1` was reserved at `1789386629.1585424`, but at `1789386630.145` the watcher surfaced `group-attention: accepted component launch requires reconciliation`. Child generation `s1789386639.498673.23633` was minted roughly nine seconds after that wake. The later sample at `1789386640.6296692` saw a still-`launching` request and a child busy in `fm-spawn`; by `1789386657.7726557` the same child was `launched`, replay was confirmed and current owner state was waiting for an active component. The earlier wake did not prove an actual launch failure or that a child endpoint existed at the wake timestamp. Launch custody needs explicit owner evidence before the controller may absorb this transition safely.

The watcher wake and ordinary drain presentation were preserved. During preparation to acknowledge and rearm, a new observation changed the test: Claude had put the long sleep in a native background shell and ended its turn. Its pane still showed one shell running, but the existing FirstMate pane/run-step classifier returned unknown for the component and attention for its root. No rearm or fabricated working proof was supplied. This is a separate observation from the early launch race; it does not satisfy the planned continuous 240-second positive-activity interval.

A later fixture can disable background tasks and set a sufficiently long Bash default timeout in its private harness environment, both documented Claude settings. That tests the existing foreground activity contract without claiming native background-shell supervision is supported. [Official Claude environment variables](https://code.claude.com/docs/en/env-vars).

The real Work flow completed in 526.34 seconds. The component's native background-shell completion notification resumed its model, which published the retained result through FirstMate. The root gathered that result, produced a correct ordinary scout report and appended `done`. Independent retained-byte validation matched the result and report digests. Exactly one component was present; the original fixture and both worktrees were clean.

| Evidence | Recorded value |
| --- | --- |
| Root | `native-claude-lvshcu9v` |
| Root generation | `s1789386572.494074.20211` |
| Root endpoint | `fm-lab-acceptance-claud-493492-24995:w1:p2` |
| Child | `tg-341e9bd00eb8237ed97e` |
| Child generation | `s1789386639.498673.23633` |
| Child endpoint | `fm-lab-acceptance-claud-493492-24995:w1:p3` |
| Request body hash | `b725d73910e33372629cc1df39c857eb43a63049aab3346e355ebfead2544b25` |
| Result digest | `d4fa1b047144f4860d8af8bfa5978611dafbacf8dd40955b355cd7ec6ca50771` |
| Retained report digest | `52cd923dfa42257a02a9a4dafa18b442233317cab21b553a40a2fb049d42c7e7` |
| Ordinary root report digest | `6d30bc0e46c0fa2dc56ae6a07895e7f19cb7e798b1b29c05d758bc400fb73dc2` |
| Final request | `complete`, `gathered=true`, gathered by the current root generation |

This demonstrates the repaired native Claude path through required source/guidance reads, component report publication, retained result, gather and ordinary root delivery. It does not establish every acceptance condition: the watcher surfaced the launch race above; the long interval used a background shell; no parent replacement occurred; and the root gathered before reading the full retained report/result. A narrowly scoped observer of only this private root session confirmed successful full native Read results at `11:56:56.606Z` and `11:56:57.164Z`, after the owner's gather acknowledgement at `11:56:54.344Z`. The required read-before-acknowledgement order was not met. Only safe tool-event identities, paths, success flags and ordering were retained; no native transcript content was copied. This diagnostic does not implement product-wide native transcript correlation. The root's own statement that it found no defects describes its limited source assignment and does not override these observer findings.

Both FirstMate endpoint exits and both ordinary task teardowns returned 0. The teardown owner reported reaping and then force-killing leaked processes from each owned worktree; this was its actual cleanup behavior, not a clean endpoint-exit-only shutdown. Named-lab teardown and identity-proven private sentinel stop returned 0, followed by an empty scoped process inventory and only the stopped private default session. No private Claude or Codex credential file existed. The launch attention wake was preserved and was not silently acknowledged or rearmed away.

## Joined repair acceptance plan

After the separate launch-custody and native Windows admission/cleanup repairs passed the coordinator's WSL integration discovery, attempt `hrilwgto` began against a fresh prepared distribution: 563 files, aggregate `5f3b429e3b314f47427cc1e62a78300ec04eedfc0055a2a596a46d4a7b814fa8`. Its manifest is `df304e456ad49611dc3233056d4b8c47280971d89e8eb027a45303f300029b25`; package bytes remain unchanged.

The private Claude environment sets `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` and `BASH_DEFAULT_TIMEOUT_MS=420000`, with an explicit foreground 330-second component delay. The root must perform complete native Read calls for the retained report and result before one standalone literal client gather command. The bounded observer checks successful complete reads against both the actual gather invocation and the owner's acknowledgement time, correlating only the private root worktree. Watcher defaults and ordinary owners are unchanged.

The real launch transition passed: at `1789387655.023`, the ordinary watcher recorded waiting for FirstMate component launch under live parent lock custody and kept running, while the sampled child had no metadata yet. The same child, `tg-7aff0ec0d70ef2333a68`, subsequently became a launched, positively busy Claude component and the root became waiting for that active component. This observation addresses the earlier launch race without treating an absent endpoint as alive.

A distinct ordinary-signal path then surfaced the root's routine `working: submitted ... replay confirmed ... polling status` update. At `1789387705.256`, arm output reported `signal: .../native-claude-hrilwgto.status`, while durable queue rows used type `check`, key `task-group-native-claude-hrilwgto`, and the existing instruction to inspect changed group state instead of treating the status as outer delivery. Child state remained positively working and root state remained waiting. This was not a stale or group-attention alarm, but the first watcher cycle ended before the continuous 240-second assertion was satisfied.

The observer presented this wake through the ordinary drain owner. An auxiliary helper looked for its acknowledgement instruction on stdout although it was emitted on stderr, so it stopped before any acknowledgement or rearm. That is a separate disposable-observer error. Once diagnosed, the remaining fixed-delay interval was too short for a new 240-second cycle. No rearm was performed and no acceptance threshold was lowered. The complete watcher acceptance remains unmet for this attempt.

The Work/read-order/delivery case completed in 618.59 seconds with exactly one component, an unchanged fixture and clean root/component worktrees. Runner identity was `88dc9c9eaacf7c65b8a8a39efa3f0f26818307d13838b7c02817087487dcd2e0`. Root generation `s1789387566.543174.16929` and child generation `s1789387651.564679.21493` belonged to named lab `fm-lab-acceptance-claud-538873-28018`, panes `w1:p2` and `w1:p3`. The request body hash was `a65262f3a146f9970528c698ed9deb6d48d0cbf4e26b22343326dcf4f319cd47`; the retained canonical result digest was `35b43be0d68d929b987c90e60eae5cafb685d6ec7a213881f2cfd157cde2dec3`.

The scoped native-event observer now proved the required read order. Full successful report and result reads occurred at `12:14:43.495Z` and `12:14:44.039Z`; the first standalone gather invocation followed at `12:14:58.888Z`, and owner acknowledgement at `12:15:01.640Z`. Both checks—full reads before first gather invocation and before owner acknowledgement—passed. The report byte digest was `30729744fffe8ddc15024862165942f4f151b22a38be652e0b66a5575fa8ee83`; the entire result-file byte digest was `ac6196a22dddcfee9120b1e044afd929ddd2e16109c0dbd3b487f4f151653b62`, distinct from its canonical result digest. Observer source identity was `7485427239dc32027abcc8dd265425d5b9c96ef89a962f7bea0df0c2b19aa7b1`.

Both ordinary endpoint exits, both task teardowns, named-lab teardown and the identity-proven private sentinel stop returned 0. The teardown owner reaped and force-killed residual worktree shell processes `545036` and `566209`. The final scoped process inventory was empty, only the stopped private default session remained, and no private authentication file existed. These results release this frozen candidate while preserving its early routine-status watcher exit as an unmet acceptance condition.

## Signal repair acceptance

After the separate signal-absorption repair passed the coordinator's 81-case integration discovery on WSL and Windows, attempt `ed3tuvcz` began with the same foreground delay, routine status updates, complete native reads, ordinary owners and 240-second continuous watcher assertion. The completed trial used no watcher drain or rearm.

This attempt used `.scratch/stage1-signal-repaired`: 563 files, aggregate `b2a77515706e18b5eade021ec774f57cc0f11cd632023723900d155f77fb07a1`, manifest `b56d9fc44eaf67cd3e728c5ae580af3472434244bf1d2b02eb6ba7c9298e6cc0`. Package bytes and the native read-order observer remained unchanged. Acceptance-runner identity was `e5323b0cbf9d814a68ea29b33d55d0d886d8c16a3700c25a423aae830cd1d84f`. The component assignment body was identical to `hrilwgto`; the model's wording of its routine status line varied, with no status instructions removed from the fixture.

The actual ordinary watcher, PID `618931`, absorbed the routine root status signal at `1789388759.769845`. It subsequently recorded 20 consecutive waiting-for-active-component classifications from `1789388761.475899` through `1789389107.032330`, a span of **345.556 seconds**. All 19 contemporaneous owner samples in that interval showed the same live watcher lock, the root waiting and its Claude component positively working. The actual trace retained the unchanged defaults `15/240/3600`; the child pane showed its one foreground `sleep 330`. There was one watcher start, no watcher drain, wake acknowledgement, rearm or parent replacement, and no wake interrupted that active interval.

The first and only actual watcher wake followed retained completion at `1789389124.644817`: `check: task-group native-claude-ed3tuvcz: group-ready: retained component result awaits gather acknowledgement`. Its durable queue row agrees, and the arm exit record reports `exit_code=0`, `signal=none`, `reason=actionable-check`, beacon age 2 seconds and no successor. This is the expected result attention after waiting, not a stale or group-attention alarm. The read-only watcher-evidence summarizer has SHA-256 `85824ada0dd934703c4d3190c43c4f9244c2ff1957e1a56260bb359f042568df`. Applied unchanged to the earlier `hrilwgto` trace, it reports no qualifying continuous active-watch interval and a failed assertion, preserving that comparison.

The trace also contains early `group-attention`/`record unavailable` variable assignments before request acceptance, at `1789388678`, `1789388694` and `1789388711`. These are the helper's initial defaults, not surfaced attention: the source's ordinary-task path returns 1 before the watcher's attention branch. The observation annotates those pre-request assignments separately from its completed active-wait evidence and actual wake calls. The selected trace does not itself record helper return codes; this interpretation combines the recorded timing with the frozen helper/caller source. No corresponding attention wake or durable queue entry occurred.

The real Work flow completed in 637.02 seconds. Both findings matched the unchanged source fixture: `total_units([]) == 0` from `stock.py:3–4`, and `normalize_code(' ab-7 ') == 'AB-7'` from `labels.py:3–4`. Retained-byte integrity matched; exactly one component existed; the original fixture and both worktrees were clean. The root report records identical request replay with the same child/generation; the durable request confirms its single reservation. The narrow native-event observer records Read/gather ordering, not the two submit transcripts.

| Evidence | Recorded value |
| --- | --- |
| Root | `native-claude-ed3tuvcz` |
| Root generation | `s1789388671.619399.27774` |
| Root endpoint | `fm-lab-acceptance-claud-618791-21225:w1:p2` |
| Child | `tg-dda4652f1c0a7b85dcb2` |
| Child generation | `s1789388730.622363.13016` |
| Child endpoint | `fm-lab-acceptance-claud-618791-21225:w1:p3` |
| Request body hash | `a65262f3a146f9970528c698ed9deb6d48d0cbf4e26b22343326dcf4f319cd47` |
| Canonical result digest | `3bbd46777c58cf1129276348dcf7ec8499fe5d43f500bcc35ccd1a83989ffb01` |
| Retained report digest | `e5a114fe980ba241faa89513b3e4ef6a50f0fe4622880be24d11368b7a49852d` |
| Entire result-file byte digest | `65f5fba891474ec1ded992f1375172c7180f8acb76468ea5f00587fb5ecccdc2` |
| Ordinary root report digest | `3f108d1c191cefde173d0284aa9bc07bc3de125b326791732b7bd94089ac5682` |
| Final request | `complete`, `gathered=true`, acknowledged by the same current root generation |

The same scoped native-event observer proved full successful report and result reads at `12:33:35.753Z` and `12:33:36.372Z`. The first standalone gather invocation followed at `12:33:45.228Z`; the owner's acknowledgement occurred at `12:33:47.287Z`, followed by native tool-result success at `12:33:47.503Z`. Both read-before-gather checks passed. This remains private-trial evidence: product metadata still does not claim a verified native transcript session.

Both FirstMate endpoint exits and both ordinary task teardowns returned 0. The teardown owner reaped and force-killed residual worktree shells `620011` and `623333`; named-lab teardown and the identity-proven private sentinel stop returned 0. The scoped process inventory was empty afterward, only the stopped private default session remained, and no private authentication file existed. Teardown emitted supervision-down and queued-wake warnings because the completed actionable watcher cycle was deliberately not rearmed or acknowledged. Those warnings and the legitimate result wake were retained; they do not imply endpoint-exit-only cleanup or continued supervision after the result wake.

The coordinator's single independent review identified the routine-signal issue. Its isolated repair was followed by the reproducing regressions, both platform integration suites and this actual trial. No second independent review or further model trial was performed. Native Windows worker lifecycle, native background-shell activity tracking, broader Orchflows actions and general native transcript correlation remain outside this acceptance result.

## Local receipt index

These files are local evidence under ignored storage, not distributed authentication profiles or full native transcripts. The dated native-trial record is unchanged.

| Attempt | Local receipt | Outcome |
| --- | --- | --- |
| `t81r5ag1` | [preflight receipt](../.scratch/stage1-runtime/native-trial-fm-n1.t81r5ag1/receipt.json) | Disposable inventory-sort error, before runtime/authentication |
| `gihzfr9y` | [Codex receipt](../.scratch/stage1-runtime/native-trial-fm-n1.gihzfr9y/receipt.json) | Actual copied-cache refresh failure; ordinary stale wake; copied-cache design retired |
| `auth-win-3hzo4xn7` | [safe authentication receipt](../.scratch/stage1-runtime/auth-win-3hzo4xn7/safe-receipt.json) | Native Windows authentication-only request succeeded |
| `lvshcu9v` | [Claude receipt](../.scratch/stage1-runtime/native-trial-fm-n1.lvshcu9v/receipt.json) | Work completed; launch race, background activity gap and incorrect read order preserved |
| `hrilwgto` | [joined repair receipt](../.scratch/stage1-runtime/native-trial-fm-n1.hrilwgto/receipt.json) | Launch custody and read order passed; routine signal ended watcher early |
| `ed3tuvcz` | [final repaired receipt](../.scratch/stage1-runtime/native-trial-fm-n1.ed3tuvcz/receipt.json) | Work/read-order/report/cleanup and continuous normal watcher acceptance passed |

The final [watcher observation](../.scratch/stage1-runtime/native-trial-fm-n1.ed3tuvcz/claude/watch-acceptance-observation.json), [selected actual watcher trace](../.scratch/stage1-runtime/native-trial-fm-n1.ed3tuvcz/claude/watch-execution.trace), [native read-order observation](../.scratch/stage1-runtime/native-trial-fm-n1.ed3tuvcz/claude/read-order-observation.json) and [ordinary root report](../.scratch/stage1-runtime/native-trial-fm-n1.ed3tuvcz/claude/root-report.md) retain the detailed evidence behind the final result.
