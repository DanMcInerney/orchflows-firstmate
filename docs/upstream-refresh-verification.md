# Upstream source refresh — September 14, 2026

The owned package is now **0.1.0-dev.3**, based on the latest public Orchflows revision observed for this increment: `ca72258493480ddcfe73b3f01d0475ad532e4726` (upstream version 0.7.0). The user authorized the refresh and said not to use design-loop. Its new upstream files are retained as inactive migration source; no design-loop workflow was invoked, enabled, registered or installed as a library.

## Change and provenance

The upstream delta from `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a` is one commit: 17 new files under `example-workflows/design-loop/` and a root README change. All 17 additions were imported byte-for-byte from Git blobs. The fork's inactive upstream README quotation was refreshed, its provenance updated, and its three manifests advanced from dev.2 to dev.3. Those are the only five changed existing package files.

All 1,081 current upstream paths are retained, plus six fork additions: **1,087 package files**, including 1,039 example files. All 1,022 historical example files remain unchanged. The earlier checkout line-ending differences remain recorded; importing the new files directly from Git did not normalize old files. A complete Git-tree/blob comparison confirmed the same nineteen deliberate upstream-content differences as Stage 1, with checkout-only line-ending differences accounted for separately.

The five core skills, runtime scripts, tests and entire FirstMate distribution are unchanged. `.sources/orchflows/` and `.sources/firstmate/` remain clean at their historical pins. The new upstream reference was acquired in a separate ignored checkout. No active installation, host settings or live fleet was changed.

| State | Exact identity |
| --- | --- |
| Current package | 1,087 files; aggregate `15e5b6ff0280903b2be4805143f9cd3f610080a688a249942f944baeff6d87d5` |
| Historical dev.2 package | 1,070 files; aggregate `a3cd1cddf0098ed0462ebf62fd8802dfc7cb92ddd29c9a8007fb1e2f97706c8e` |
| Unchanged prepared FirstMate | 563 files; aggregate `b2a77515706e18b5eade021ec774f57cc0f11cd632023723900d155f77fb07a1` |
| Unchanged integration manifest | `b56d9fc44eaf67cd3e728c5ae580af3472434244bf1d2b02eb6ba7c9298e6cc0` |

The aggregate rule is sorted POSIX relative path + NUL + lowercase file SHA-256 + LF, encoded as UTF-8 and SHA-256 hashed; exclude `.git` and bytecode. [Current state](upstream-refresh-state.json) records imported-file hashes, changed-file before/after hashes, exact source identity and platform check receipts. [Stage 1 state](stage1-state.json) remains the historical live-trial record.

## Executed checks

The existing package suite ran against the changed package with disposable fixtures:

| Runtime | Result | Test duration |
| --- | --- | --- |
| Windows, Python 3.14.6 | 84 cases: 83 passed, one existing POSIX-mode skip | 18.313 seconds |
| WSL Ubuntu, Python 3.12.3 | All 84 cases passed | 13.057 seconds |

Commands from the repository root:

```powershell
python -B -m unittest discover -s packages/orchflows-firstmate/tests
wsl -d Ubuntu -- python3 -B -m unittest discover -s packages/orchflows-firstmate/tests
```

The existing distribution preparation tool produced a fresh FirstMate candidate from the clean pinned source. Its entire 563-file aggregate and eleven-deployable manifest matched the previously tested distribution:

```sh
python integrations/firstmate/prepare.py --source .sources/firstmate --destination .scratch/upstream-refresh-2026-09-14/firstmate-candidate
```

A separate check used the actual dev.3 package on each platform. Public setup, repeated setup, doctor and resolve operated in a temporary package home. Both core names resolved to dev.3, the user-owned marker file survived repeated setup, host configuration was skipped, and readiness remained explicitly package-only with execution readiness false. Default setup installed no optional libraries; both catalogs contained only the fork core.

The freshly prepared FirstMate controller then attached the complete real package to a disposable local Git fixture before any worker launch. Repeating the attachment returned the same record; every retained file matched the source package; verifying a deliberately changed retained README raised the expected snapshot-changed error. This check passed in 239.135 seconds on Windows and 231.304 seconds on WSL, including setup, repeated inventory reads and temporary-home cleanup. Its original fixture incorrectly expected a seeded personal directory; source inspection showed setup creates an empty libraries directory, so that fixture assertion was corrected without changing product code.

Controller attachment digests are recorded separately for each platform in the state file; they are the existing owner's ordered inventory digests, distinct from the portable package aggregate above. These checks do not demonstrate moving a live attachment between operating systems. No harness, Herdr endpoint or component was launched.

Raw package logs, source/import receipts and the bounded setup/attachment check are under ignored `.scratch/upstream-refresh-2026-09-14/`. No new permanent test suite or independent agent review was added for this source-only increment. Earlier reviews do not cover its changed files. Final source/manifest checks and `git diff --check` passed.

## Runtime boundary and continuation

This refresh does not extend live compatibility. Earlier Claude/Codex Work, watcher and parent-replacement results remain tied to their exact dev.2 inputs. One experimental read-only Work component remains the only admitted execution scope; other core workflows and optional libraries remain gated. Native Windows custody, remaining harness/restart acceptance and background-tool supervision remain the next implementation work in [open questions](open-questions.md).
