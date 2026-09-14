# Standalone foundation verification

This record concerns Stage 0 of [fundamental-design.md](fundamental-design.md): independently owned source and installation identity, preserved feature source, and an explicit unimplemented execution boundary. It is not a FirstMate/Herdr integration test or a full feature-parity result.

## Baseline and candidate

- Upstream Orchflows: `0fc6cb7ac7da7b275a83cc90807fba15b8ceb15a`, manifest 0.7.0, complete 1,064-file Git archive.
- FirstMate reference: `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`; no FirstMate source modifications in this increment.
- Owned candidate: `packages/orchflows-firstmate/`. It contains the full archive, with deliberate namespace/setup/instruction changes; no nested Git repository.
- Before editing, the existing research workspace's tracked and relevant untracked files were copied and hashed under ignored `.scratch/standalone-foundation/research-baseline/`. The source archive and baseline manifest are in that same ignored verification directory. No prior research files were discarded.
- Exact candidate identity and divergence inventory are recorded in [foundation-state.json](foundation-state.json). Original research clones and the dated assessment remain unchanged.

The package is independently owned code intended for this repository, unlike ignored `.sources/` research copies. Git history remains in the full research clone; provenance in the owned package identifies the source revision. The original examples, their assets and notices remain migration fixtures, not independently certified FirstMate plugins.

## Implemented scope

The foundation separates package/home/catalog identity from normal Orchflows, retains setup/resolve/history mechanics, makes host concurrency edits explicit, and distinguishes package preparation from executable workflow readiness. The five core skills direct the caller to an execution gate while the task-group adapter is unimplemented. There is no native-child fallback or pretend successful FirstMate adapter.

Administrative package commands may run outside a fleet to prepare or inspect a home. That does not create a direct workflow execution mode. The gate is an instruction contract; it is not an operating-system sandbox or proof that a future worker loaded the right instructions. Existing native history parsing remains usable as an evidence tool.

## Checks and evidence

Required foundation checks were fixed in the design before completion. The same core suite is run against baseline and candidate; namespace/default-behavior adaptations and additional isolation tests must be identified separately. Temporary homes, host settings and synthetic transcripts are disposable. No test reads private conversation data or installs into the user's live package home.

| Check | Result | Evidence scope |
| --- | --- | --- |
| Baseline Windows core suite | 61 tests; 60 passed, one POSIX-mode skip | Setup, host configuration, native history; `baseline-tests.log` |
| Baseline WSL Ubuntu core suite | All 61 passed | Same inherited suite under Linux Python; `baseline-tests-linux.log` |
| Candidate Windows core and isolation suite | 69 tests; 68 passed, one POSIX-mode skip (11.702s) | Python 3.14.6; foundation behavior only; no fleet sessions |
| Candidate WSL Ubuntu core and isolation suite | All 69 passed (8.608s) | Python 3.12.3; same suite, including POSIX-mode behavior |
| Plugin manifest / skill validation | Plugin validator and all five core skill validators passed | Structural checks, not runtime activation |
| Exact source retention and difference inventory | 1,067 candidate files: 19 upstream files changed, three added, none removed; all 1,022 example files and license/notice files byte-identical | Complete Git archive comparison; hashes and paths in foundation-state.json |
| Bounded execution-gate trial | Fresh caller reported the missing integration and stopped; no plan.md or child/fleet action | Observed refusal on a small reading-list task; cannot establish a positive integration path |
| Independent review | No material findings after a second pass for shared causes; eight new isolation/readiness tests independently passed | Joined implementation/design/evidence; source and candidate identities independently verified; no repairs required |

Logs and disposable fixtures are under ignored `.scratch/standalone-foundation/`. Baseline test commands were `python -B -m unittest discover -s tests` in the pinned source and the same command with `python3` in WSL Ubuntu. The one Windows skip is the inherited POSIX file-mode check, which passed under Linux.

The package maker executed the same commands for the candidate. Its `candidate-package-tests.md` is a summary of executed tool output, not a raw transcript. The inherited 61 tests remain, with namespace/default-concurrency assertions adapted in `tests/test_home_setup.py` and `tests/test_home_cli.py`; eight new tests in `tests/test_firstmate_foundation.py` cover home/environment isolation, protected normal homes/catalogs/cores, no default host-setting access, strict core aliasing and collision rejection, and honest readiness. `host_config.py` and `native_logs.py` are byte-identical to upstream.

### Observed execution-gate trial

A fresh native caller was assigned the exact fork dynamic-workflow skill and an unrelated disposable project containing a 112-byte `notes.txt`. The requested output was `plan.md`, a short reading-list organization plan. No FirstMate task attachment or Herdr session was supplied. The caller read the skill and linked architecture, reported the unimplemented task-group adapter, and stopped. It reported no file changes, external-service calls, installations or delegation. The coordinator separately checked the unchanged input hash and absence of `plan.md`.

The exercised workflow SHA-256 was `47b8ca84704b23f0f41e2fb2d864fc236829e6bc0cb9f7b94708ccd4c90357fa`; architecture SHA-256 was `0de2464b400071091bb12d553b6dee80ce7c92d6b8fc3a5914adbe39fd416317`. The fixture input SHA-256 was `6c9c92dd5e65a932aeeb6bf2d6df5e06b5df62662ce7b697a62d1a90f00bd5ff`. The other four skills passed structural checks but were not separately exercised by native callers. This one negative trial establishes observed instruction-following in this session, not a host-enforced sandbox or future worker readiness.

### Independent review and final state

One fresh reviewer examined the joined package/design/evidence without changing files or delegating repairs. It reported no material findings after a second pass for shared causes. It independently ran all eight new isolation/readiness tests and checked the candidate aggregate, full archive retention, unchanged examples/notices, design/parity hashes, clean research clones and preserved original assessment. It did not repeat the full Windows/WSL suites or the negative agent trial; those remain maker/coordinator observations. No repair pass was necessary and no second review was run.

The reviewed package aggregate is `ccd246a9035ffe024e70379ff729331e0d0bed45357327cf19c49f6627d7fc5a`. The reviewed design and parity SHA-256 values are `9afb4c6f2658c4d99273d0f0c7651decf2eeb361a8cda8b2f8c9fc4375fd31e2` and `5ada35ab870b7dfc3cea992689bda846c94f4e7256596b3583b9e013477f79d7`. The package and those two documents were not edited after review. Only final verification/evidence/handoff records were completed.

The coordinator checked 16 root Markdown files, 120 local targets/headings and 111 commit-pinned source file/numeric-range references without errors. This checks reachability and numeric validity, not semantic citation strength or external HTTP/heading targets. `git diff --check` passed; the original dated assessment and original source manifest have no Git diff. No owned package file is excluded by the parent repository's ignore rules.

## Runtime boundary

Read-only inventory found no `herdr` executable on the inspected Windows or WSL Ubuntu PATH. WSL also did not discover `jq`, `treehouse` or `claude`; its `codex` entry is a mounted Windows npm shim. Windows has a jq executable. This inventory does not prove the runtime is absent from every possible remote or configured host, and it does not certify authentication or worker launch.

No Herdr session was created, stopped or inspected through its CLI. No FirstMate home was bootstrapped and no user host configuration was changed. Stage 1 requires an established supported disposable environment and the actual FirstMate task-group seam. Herdr lifecycle tests must use FirstMate's named-lab helper and its default-session tripwire, as specified by the pinned FirstMate contract.

## Next implementation boundary

Implement the FirstMate-owned component request/result path and a single real read-only Work result in a Herdr lab. Only after that useful complete path succeeds should the port expand to independent Review, writer integration, delivery, nested composition, retained bundles and example-library trials. Passing this foundation is a basis for that next increment, not a plug-and-play release claim.
