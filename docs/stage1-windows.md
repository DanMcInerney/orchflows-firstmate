# Native Windows runtime boundary

The experimental controller now has an explicit native Windows runtime boundary. This fixes shell selection, path conversion and parent-lock ancestry at the controller seam. It does not establish live native Windows FirstMate/Herdr workers. Subsequent [native Windows probes](stage1-windows-native.md) passed real Herdr and Treehouse primitives but reproduced owner refusals and a surviving detached child after lab teardown. The [Linux native trial](stage1-native-trial.md) is separate evidence.

Read-only probes found that Windows PATH resolves `bash` to the WSL launcher, while native Git Bash is also installed. Native Python interprets `/c/...` differently from MSYS, and Git Bash rejects the POSIX `ps -o ppid=` query previously used for inherited lock custody. The original FirstMate lock owner also requires real symlinks; Git Bash's default `ln -s` behavior in this environment did not publish one.

## Selected boundary

`fm_task_group_runtime.py` owns typed filesystem conversion, shell execution and Windows ancestry checks. `fm-task-group-runtime.sh` converts only Python entrypoint paths and disables heuristic argv conversion for that invocation. Existing FirstMate metadata is retained verbatim; conversion applies to filesystem operations and explicit command arguments. POSIX attachments without runtime fields remain usable.

On Windows, the owning FirstMate process must select the actual Git Bash interpreter in `usr/bin`, alongside its matching `cygpath.exe` and `ps.exe`, and the native Python interpreter running the controller:

```powershell
$env:FM_TASK_GROUP_BASH = Join-Path $env:ProgramFiles 'Git/usr/bin/bash.exe'
$env:FM_TASK_GROUP_PYTHON = (& python -c 'import sys; print(sys.executable)')
```

The controller refuses missing configuration, the WSL launcher and mismatched interpreter selection. It records the selected executable paths and digests, Python version and symlink policy in the Windows attachment. Subsequent operations require that same runtime. These settings belong to the owning process or disposable lab; this implementation does not change a global shell or harness profile.

Child processes use `MSYS=winsymlinks:nativestrict`; the host must permit native symlinks or existing lock acquisition refuses. Parent lock custody checks the actual FirstMate lock records and a live native ancestor mapped from the MSYS PID. A matching marker or unrelated live process is insufficient.

Generated worker commands carry the explicit runtime and native client arguments. Request-file paths passed to the package client must be native paths; the root overlay explains conversion with `cygpath -m`. The package client itself requires no Windows-specific implementation changes.

## Executed evidence

The isolated prototype passed seven tests in 46.089 seconds using real Git Bash, native Python, Git worktrees, the existing FirstMate parent locks and the existing inbox writer. Cases included spaces, apostrophes and Unicode paths; actual package-client submission; failed launch with durable uncertainty and no duplicate dispatch; retained completion/gather; and rejection of missing runtime, WSL, stale generation, forged custody and an unrelated live lock owner. Only worker launch and the backend notification endpoint were substituted.

The existing 24 controller tests also passed on native Windows with the explicit runtime selected, in 58.009 seconds. These are controller tests, not model-worker trials. The joined distribution's final suite is recorded in [verification](stage1-verification.md).

Subsequent native Windows probes passed private Herdr endpoint operations and real Treehouse worktree allocation, then reproduced failures in FirstMate's idle-shell and session-marker owners. A detached native child survived workspace and lab teardown. See the [exact native observations and implementation sequence](stage1-windows-native.md). Real Claude/Codex workers, live notification, parent restart and complete process custody still require native owner changes and their own acceptance. Windows authentication availability and successful controller tests cannot establish those capabilities. The user explicitly requested a Windows-capable integration; these remaining checks are rollout work, not a permanent exclusion of Windows.
