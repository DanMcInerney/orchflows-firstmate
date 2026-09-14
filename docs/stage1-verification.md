# Stage 1 implementation and verification

This records the previous increment through its repaired 562-file FirstMate candidate. The [continuation verification](stage1-continuation-verification.md) records the subsequent 563-file candidate, launch/cleanup changes and newer runtime outcomes. The current [state](stage1-state.json) preserves the earlier candidate under `previous_repaired_firstmate` and its checks under `previous_increment_verification`; the runtime gaps below describe the earlier checkpoint.

Stage 1 adds an experimental read-only Work component owned by FirstMate. The full target remains near Orchflows feature parity through FirstMate/Herdr with Claude and Codex workers. This increment does not certify that broader target, native Windows operation, or a plug-and-play release.

The exact bounded behavior and acceptance criteria are in the [Stage 1 contract](stage1-contract.md). The [foundation verification](foundation-verification.md) describes the earlier dev.1 package and remains a historical record. Current package identity is `0.1.0-dev.2`; the current implementation must not be compared against the foundation digest as if unchanged.

## Source identity correction

The current [state record](stage1-state.json) preserves the actual package digest and separates comparison with the pinned local checkout from comparison with raw Git blobs. All 1,064 upstream files are retained; 1,022 example files are byte-identical to that local checkout. Forty-nine example text files have checkout CRLF line endings where their raw Git blobs use LF. Earlier claims of byte identity to upstream meant the inspected checkout, not every raw blob. The historical foundation identity remains unchanged; no example content was edited by Stage 1.

## Implemented ownership

The package's new client negotiates the actual FirstMate controller, verifies the current root generation and exact retained package, and exposes submit/status/gather. Only `orch-work` conditionally admits the Stage 1 subset. The other four core workflows retain their execution gate. No normal Orchflows installation or native child tool is a fallback.

The FirstMate distribution contains an explicit native Windows runtime boundary, an admission/result controller, immutable complete package snapshots, request reservation before launch, a bridge using existing parent control/metadata locks, and seven patches to existing launch/lifecycle owners. The ordinary spawn owner publishes group metadata and regenerated root/component instructions. Repeated requests reuse one child; uncertain launch never authorizes automatic replacement. Completion retains the report and its digest before notification; gathering verifies bytes and records acknowledgement. Component completion cannot become ordinary scout delivery, promotion or premature teardown.

## Executed checks

| Check | Executed result | Limit |
| --- | --- | --- |
| Package core suite, Windows Python 3.14.6 | 84 tests: 83 passed, one POSIX-mode skip | Packaging, history and client fixtures; no live worker |
| Package core suite, WSL Python 3.12.3 | All 84 passed | Same suite with POSIX case enabled |
| Controller/bridge/lifecycle fixtures, WSL | All 41 passed before distribution tests were added | Real Git and selected FirstMate lock/lifecycle owners; launch/backend observations are test doubles |
| Initial complete integration fixture suite | WSL: all 46 passed against the freshly prepared candidate. Windows: 29 passed, 17 POSIX fixtures skipped | Historical controller, five distribution checks and the applicable shell fixtures |
| Distribution inventory tests, Windows | All five passed | Reject altered bytes, unlisted files, duplicate/traversal inventory and unverified patch sequence |
| Fresh preparation from clean pinned source | Succeeded; all 559 prepared files byte-identical to the isolated implementation candidate | Local clone, patch and overlay only; does not install a live home |
| Plugin and five core skill validators | All passed | Manifest/frontmatter structure only |
| Inherited `fm-brief` behavior suite | Passed through FirstMate's runner | Ordinary brief generation remains intact |

The first inherited launch/regression invocation lacked native Node on PATH. The allowlist fixture and Claude relaunch fixture refused; the latter explicitly reported the missing Node trust prerequisite. These failures are retained as setup evidence. With the staged native Node/runtime dependencies on PATH, the full inherited `fm-spawn-dispatch-profile` and `fm-control-relaunch` suites both passed through the same runner (156.323 and 105.681 seconds respectively; no gate skips).

The first long watcher triage run failed its held-worker timing expectation. The unchanged exact failing case then passed in isolated comparison: pinned baseline exit 0 in 117.58 seconds; candidate exit 0 in 103.61 seconds. No regression was reproduced and no assertion was weakened. Timing is a leading explanation (a fixed 10-second exit wait versus observed 11–12-second polling gaps), but the original cause is unproven. The full suite remains recorded as failed; the targeted comparison passed.

## Joined repair checks

The cleanup regression was reproduced against the pre-fix candidate, then repaired using the existing backlog `--report` contract with the validated retained component report. Three tests exercise actual tasks-axi pending-close staging, interrupted-close replay, duplicate replay and artifact preservation; the 13 lifecycle fixtures also passed. The backlog schema was not widened.

The native Windows runtime boundary was joined into the distribution; [Windows evidence](stage1-windows.md) explains its exact scope. Before the final review repair, discovery ran 56 cases on each platform: WSL passed 49 with seven Windows skips in 46.250 seconds; Windows passed 36 with 20 POSIX/dependency skips in 108.874 seconds. The Windows invocation explicitly selected Git Bash and native Python. A fresh prepared checkout reproduced all 561 files byte for byte, and Bash syntax checks passed. The state record preserves this independently reviewed candidate separately from the earlier Codex trial and the final repaired candidate.

## Independent review and final repair

One fresh reviewer assessed the joined implementation without making changes. It found one P1: the role overlay declared retained package paths readable, but the actual Claude launch did not grant those native Read permissions. A real Claude component independently reproduced the outside-working-directory prompt. The reviewer also passed the 56-case WSL discovery with seven Windows skips and all seven native Windows boundary tests. These were checks of the 561-file candidate, not the subsequent repair.

The repair adds a generation-checked launch callback that merges scoped Read/Edit rules into the existing Claude settings. It grants reads of the retained package and the task's declared metadata, instructions and output locations. Edits are limited to its task temporary directory and status, plus the root's own report. Root-only lifecycle instruction reads are explicit. It preserves the selected permission mode and existing feedback/attribution settings; it adds no directory-wide working scope or blanket shell grant. Absolute Read/Edit patterns and Windows drive normalization follow the [official Claude permission contract](https://code.claude.com/docs/en/permissions).

Seven new tests cover root/component scope, stale generation and relaunch, missing launch metadata, the actual CLI, literal glob characters and Unicode, Bash settings argument expansion, and native Windows drive paths. Complete discovery after repair ran **63 cases**: **WSL 55 passed, eight platform skips (40.854 seconds); Windows 42 passed, 21 platform skips (113.201 seconds)**. Fresh preparation reproduced all **562** candidate files exactly. Bash syntax passed. Because the actual launch template changed, the full inherited `fm-spawn-dispatch-profile` suite was repeated on this repaired candidate: exit 0, no gate skips, 183.660 seconds. One repair pass followed the review; no second review was run.

## Runtime evidence boundary

The [runtime preparation](stage1-runtime.md) records the exact Linux tools and a successful private Herdr lifecycle smoke test. Real worker trials are subsequent evidence. Early attempts exposed slow package inventory across the WSL mount, a required trust entry for the exact disposable Codex Git fixture, and an incomplete staged Codex distribution missing its code-mode companion. None launched a successful component or establishes adapter failure by itself.

Windows authentication is available according to the user. Read-only probes also found native Windows Git Bash and Python, but default `bash` selects WSL, native Python interprets MSYS paths differently, and Git Bash's process interface does not support the POSIX ancestry query used by the current bridge. The joined runtime module addresses those controller-boundary gaps in native tests. Live Windows FirstMate/Herdr workers remain unverified.

The first completed Codex run exposed a real cleanup integration defect: the component's backlog close used a note rejected by FirstMate's durable pending-close schema. FirstMate retained its task records and reported failure. Root teardown and named-lab shutdown succeeded, but that earlier attempt was not full component teardown success. The report-reference repair passed its real pending-close regression and the final live Codex cleanup below.

The final repaired Codex case, `2oqaz0tn`, completed in 249.62 seconds. FirstMate replaced the root after component admission, preserving the same root endpoint/worktree and one child. The replacement replayed the identical request, gathered the retained correct source findings under its current generation, handled the actual result inbox notice and completed ordinary scout delivery. Independent retained-result integrity checks passed; the original fixture and both worktrees stayed clean. Both task exits and ordinary teardowns returned 0, followed by successful named-lab and private sentinel shutdown, an empty scoped process inventory and removal of the copied authentication file. Exact generations and digests are in [native trials](stage1-native-trial.md).

Claude had previously executed real tools and survived parent replacement before encountering the retained-guidance permission prompt. After the scoped launch repair, its fresh trial `wpgnlat8` failed before model work with an expired copied Windows login cache. Cached authentication status had reported logged in, but the model request failed. The repaired Claude completion path remains unverified; no user-wide authentication conclusion follows. That failed attempt was stopped through FirstMate and the lab owner, with no remaining scoped processes and copied credentials removed.

## Remaining acceptance

The [native trial record](stage1-native-trial.md) contains the actual attempts and their identities. Codex has completed the source-inspection, parent replacement, replay, gather, normal delivery and cleanup case on the recorded WSL tuple. Claude must still complete that same repaired path. Actual native Windows workers remain unverified. Normal stale-supervision behavior also remains open: the named lab had no ordinary watcher, and its 60-second component delay and owner-state observations cannot establish stale-alarm behavior across the configured interval.

Review, writers, nesting, several components, group-wide cancellation, native transcript correlation, optional libraries, remote operation, upgrades and production installation remain later implementation and acceptance stages. Preserving their source is not feature execution parity.

## Final provenance and documentation checks

The final package's 1,070 files, prepared FirstMate candidate's 562 files and all ten deployed patch/overlay files match the state and manifest hashes. Both pinned research clones remain clean. The original assessment and source manifest have no diff; the assessment SHA-256 still matches its preserved value. Documentation validation checked 22 documents, 161 local links/headings and 128 pinned source-file/line references across 55 files with no issues. Those checks establish target existence and numeric ranges, not citation semantics or remote page availability. `git diff --check` passed. Raw receipts and disposable checkouts remain in ignored storage.
