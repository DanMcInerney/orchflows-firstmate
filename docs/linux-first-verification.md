# Linux-first implementation and verification

September 14, 2026. The user directed all development through Ubuntu in WSL and Linux working first. Native Windows development is deferred. Historical Windows probes and the existing refusal guards remain; no active installation was changed.

## Implemented

The repository now has a repeatable [Linux check runner](../tools/linux-dev.py).
It stages the exact owned sources on ext4, validates the research pin, prepares
a candidate using the distribution tool, isolates test homes and PATH, and
records all test outcomes and skips. Source checkouts made by Windows Git are
validated with per-command line-ending normalization and cloned into an LF
Linux reference. Their configuration, tracked files and pins are not rewritten.
The prepared candidate retains its actual upstream in-tree skills symlink.

The second FirstMate patch sets the native Claude foreground profile at the
existing spawn/relaunch owner, only for attached Linux tasks. It disables native
background tasks and sets a 420,000 ms default Bash timeout. Existing mode,
model, effort and file grants are preserved. This selects the foreground
behavior already exercised by the earlier WSL watcher trial; it does not
implement background-tool activity or detached-process custody.
The variables are documented in [Claude's environment reference](https://code.claude.com/docs/en/env-vars).

## Executed fixture checks

All commands ran in Ubuntu 24.04.4 on WSL2, Linux 6.6.87.2, using native Linux
binaries and ext4 candidate/test homes.

~~~sh
python3 -B tools/linux-dev.py check --bin-dir .scratch/stage1-runtime/bin
~~~

- Current package: 84 tests passed, no skips (6.986 seconds).
- Current FirstMate integration: 82 tests, 72 passed, ten explicitly native Windows skips, no unexpected skips (34.006 seconds).
- Actual launch-command expansion verified both native environment values for attached Claude, preserved permissions/argument boundaries, and preserved existing environment values for unattached Claude and Codex.
- The runner refused staging on the Windows 9p mount and rejected a Windows PE executable before execution.
- The prepared candidate has 563 inventoried paths including one actual in-tree symlink. The distribution has twelve deployable patch/overlay files. Exact hashes and test counts are in [Linux state](linux-first-state.json).
- The unchanged package is dev.3 with 1,087 files at the latest recorded Orchflows source identity.

During runner development, checks exposed CRLF research-checkout differences,
the native upstream skills symlink, and a fixture's expected research-reference
location. These were corrected in the runner; source-integrity validation and
the tests were retained. The successful receipt and logs are saved under ignored
scratch storage. No test failures were relabeled as platform skips.

## Live acceptance

The actual current-candidate trial **pzzebeug** passed in **709.618 seconds**
using Claude Code 2.1.269, Herdr 0.7.4 and Treehouse 2.0.1. Both real Claude
processes received the two foreground environment values from FirstMate's
launch command; the test environment supplied neither value. The observation
was scoped to the exact worker processes and recorded only those non-secret
profile fields.

Exactly one component was launched. Replaying the same request returned the
same child. The ordinary watcher recorded **20 waiting classifications spanning
383.632 seconds**, corroborated by 21 current-owner samples using the same live
watcher. Its actual defaults were 15-second polling, a 240-second stale
threshold and a 3,600-second busy maximum. It absorbed routine root progress,
with no wake during that active interval. Its single final wake was a component
turn-ended signal after the retained result had been published.

The native transcript observer confirmed full reads of both retained report
and result before the first gather invocation and before the owner's gather
acknowledgement. Retained digests matched, the root scout report contained
the correct two source findings, and the original fixture plus both worktrees
remained clean.

Both ordinary task exits and teardowns returned zero, as did private lab and
sentinel shutdown. The cleanup owner reaped residual worktree shells and its
final scoped process inventory was empty. The teardown logs retain
watcher-down/pending-wake warnings after the expected watcher close; this
trial did not drain/rearm a supervisor after the result. Endpoint closure
alone is not credited with process retirement. No authentication file or
refresh token was copied, no login was invoked, and no private credential file
existed after cleanup.

Exact candidate/package/result identities and sanitized receipt references are
in [Linux state](linux-first-state.json). This is actual acceptance of the
current foreground one-Work path. It does not establish native background-tool
supervision, parent replacement or a complete supervisor wake/drain/rearm cycle.

The code was checked locally without a separate agent review. Linux parent
replacement, Codex watcher acceptance, background tools, Review, writers and
the remaining feature inventory stay separate acceptance work. This increment
does not claim seamless full-parity fleet integration.
