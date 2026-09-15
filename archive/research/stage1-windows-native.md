# Native Windows acceptance and required owner changes

These September 14, 2026 observations extend the [controller boundary tests](stage1-windows.md). They are actual native Windows process and worktree probes. They do not establish a Claude or Codex worker launched through FirstMate on Windows. The [continuation record](stage1-acceptance-continuation.md) separately covers authentication and ordinary watcher acceptance.

## Exact prerequisites

The FirstMate baseline remains `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`; the tested owner functions came from the prepared 562-file Stage 1 candidate recorded in [state](stage1-state.json). Its original integration manifest was `78d8c553eeafd51bfb14c33189d003ef96d172aacd5bd5d0e2c58e86339a80eb`. Subsequent guards must be identified separately from these probes.

Herdr's stable Windows distribution was staged in ignored storage from **v0.9.0**, tag object `cca4af8dfad160bc5fb5ae133b70882b5fe28f61`, source commit `b99002ac99b09e00b4ca692436cb15a6b0d676f1`. The executable reported `herdr 0.9.0`; both native client and server reported protocol **22**, compatible. This is a separate tuple from the Linux v0.7.4/protocol 16 trials. The [official release](https://github.com/herdrdev/herdr/releases/tag/v0.9.0) was published September 7, 2026.

Treehouse v2.0.1 also has official Windows amd64/arm64 archives, even though FirstMate's pinned installer only selects Linux/macOS assets. The actual Windows binary reported `v2.0.1`. Missing Windows branches in that installer must not be described as missing upstream Windows binaries. [Treehouse release](https://github.com/kunchenguid/treehouse/releases/tag/v2.0.1), [pinned FirstMate installer](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-install-treehouse.sh).

| Asset | Archive SHA-256 | Extracted executable SHA-256 |
| --- | --- | --- |
| `herdr-windows-x86_64.zip` | `b4508c445de1c1a68c760a01735da2aba2fa214b2aafd4b07f732e49b2a64b11` | `9b3bf49f94c2d09b1d62e11171b132865768dafc36b1327fb946c0cef9ca0d00` |
| `treehouse-v2.0.1-windows-amd64.zip` | `d4c7bebc876b6dc1f9cf2f2b934803234d4f2f6e1c1c314505db85e64f5100bc` | `b3446e4c0e16951888b3debaf6c530e182374d1051600408e40e3f7f107e1c8f` |

Downloads matched the size and SHA-256 supplied by official GitHub release metadata before extraction. No global installer, PATH setting or active user installation was changed. Source inspection and raw release metadata are retained under ignored `.scratch/stage1-windows-native/`.

## Isolation and measured primitives

Each probe created a new private directory with its own HOME, USERPROFILE, APPDATA, LOCALAPPDATA, XDG config/state and temporary directories. No authentication was supplied. Herdr's configuration explicitly selected native Git Bash as the pane shell. Its Windows default is PowerShell; setting the task-group controller's Bash path alone does not select the terminal shell. [Herdr shell owner](https://github.com/herdrdev/herdr/blob/b99002ac99b09e00b4ca692436cb15a6b0d676f1/src/pane.rs).

Herdr's XDG overrides determine the private session directory. On Windows, the reported socket path is a native filesystem marker; its exact string is used to name the IPC pipe. A private default sentinel satisfied the original FirstMate lab helper's tripwire, and all named lab provisioning, pane operations and teardown used that unchanged helper. Sentinel shutdown targeted its retained native process handle. Background processes were hidden. [Configuration roots](https://github.com/herdrdev/herdr/blob/b99002ac99b09e00b4ca692436cb15a6b0d676f1/src/config/io.rs), [session identity](https://github.com/herdrdev/herdr/blob/b99002ac99b09e00b4ca692436cb15a6b0d676f1/src/session.rs), [Windows IPC](https://github.com/herdrdev/herdr/blob/b99002ac99b09e00b4ca692436cb15a6b0d676f1/src/ipc.rs).

| Probe | Actual result |
| --- | --- |
| Private default and generated named lab | Provision/status/teardown succeeded; final session inventory contained only the stopped private default |
| Native Bash pane | Workspace creation, text/key delivery and capture returned the expected marker |
| Native process observation | `process-info` returned a native PID and `bash.exe` with native cwd/argv |
| Real native Treehouse | Leased a real Git worktree under the private home, verified clean Git status and returned it successfully |
| FirstMate idle-shell owner | Refused the actual idle Bash pane (`idle=1`) |
| FirstMate session-socket owner | Refused the actual native session marker path (`socket=1`) |

The first probe `fm-win-v0xuutff` accidentally called a nonexistent idle-shell function and returned 127. That is a probe error, not a product result. The corrected probe `fm-win-dgx6f7ob` invoked the actual `fm_backend_herdr_pane_idle_shell_pid` and `fm_backend_herdr_presentation_session_socket_path`; both returned 1. Their current source requires extensionless POSIX shells/process-table evidence and an absolute Unix socket path. [FirstMate backend](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/backends/herdr.sh).

## Attached and detached cleanup differ

The corrected attached-child case started a real native Python process inside the pane and retained Windows process handles for the shell and child before closing the workspace. Both handles reported exited after workspace closure and remained exited after lab teardown. No auxiliary termination was needed.

The detached-child case `fm-win-t46d9yna` launched a native Python child with a new detached process group, ignored console interrupt/break signals and waited for 120 seconds. It wrote its own PID inside the private fixture. The probe retained an actual process handle before any close operation; later checks therefore identified the same process incarnation rather than relying on PID reuse assumptions.

**The shell exited, but the detached child survived both workspace closure and named-lab teardown, even though the close operations returned success.** The probe then terminated and waited for that one child through its retained handle. Its cleanup receipt confirms exit. No unrelated process was targeted. This is a demonstrated endpoint/process-lifetime gap, not a claim that every Windows close leaks.

Herdr's Windows shutdown enumerates the current descendant tree. Its signal function opens query-only process handles, calls `TerminateProcess` without checking success, and does not account for every escaped child. The Windows API requires termination rights and a wait to establish exit. These are source findings consistent with the detached result; they do not establish which mechanism alone caused that particular survival. [Herdr Windows process owner](https://github.com/herdrdev/herdr/blob/b99002ac99b09e00b4ca692436cb15a6b0d676f1/src/platform/windows.rs), [Microsoft termination contract](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess).

FirstMate's existing teardown also treats a missing `lsof` as a successful fallback for Herdr after printing a warning. That does not prove Windows worktree or task-temporary processes stopped. Endpoint absence cannot replace that proof. [FirstMate teardown owner](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-teardown.sh).

## Fundamental Windows implementation sequence

The first admission/retention step is now implemented in the [563-file continuation candidate](stage1-continuation-verification.md): actual native Windows Stage 1 spawn/relaunch and teardown refuse before task mutation, including forced teardown. Missing `lsof` also prevents attached POSIX task cleanup from discarding records. The remaining native endpoint, process and environment owners below are still required; controller fixture success cannot bypass the guard.

1. **Admission and retention:** refuse actual native Windows task-group launch before allocating an endpoint until the required lifecycle owner exists; preserve task data when process cleanup cannot be established. Native controller fixtures remain useful evidence for their narrower boundary.
2. **Endpoint and lock identity:** share one native transport-identity implementation between launcher validation and presentation serialization. Preserve the exact server pipe identity; use a private native lock namespace with ownership/ACL checks.
3. **Process ownership:** give FirstMate one native process interface for PID plus creation time, executable/argv, ancestry, cwd, observation completeness and pane binding. Existing classification, recovery and stop owners consume it. An MSYS PID is not interchangeable with a native Windows PID.
4. **Verified descendant retirement:** associate work with an owned native process container or equivalent generation-bound mechanism. Include detached children, wait for the exact processes to exit, and preserve unknown work. A successful pane-close response alone is insufficient.
5. **Environment and live workers:** preserve Herdr's pane runtime attribution marker and the required native environment through filtered launches. Exercise actual interactive Treehouse allocation, Claude/Codex Work, replacement, replay, gathering and cleanup on the same tuple.

Herdr's Windows foreground-process-group field represents its selected native process, not a POSIX group. Adding `.exe` aliases to shell names would not supply the missing custody proof. Native event streaming can remain a later optimization because FirstMate already falls back to polling when its POSIX event reader is unavailable. These changes belong in FirstMate/Herdr's existing owners; Orchflows still supplies composition and guidance.

Raw receipts preserve command results, versions, process observations, runner hashes and cleanup outcomes. Frozen receipt directories remain historical evidence; the disposable probe script may evolve for later cases. No real Windows model worker was launched in these probes.
