# Ubuntu / WSL development

The dev.7 [local-only root extension](local-delivery.md) builds on this contract.
[Current verification](local-delivery-verification.md) records its scope and
executed evidence; earlier increment restrictions below are historical context.

The dev.6 continuation extends this seam to bounded Linux dynamic composition;
see [dynamic contract](dynamic-composition.md) and [current verification](dynamic-verification.md).
Earlier one-component restrictions below describe the dev.5 baseline.

The user selected **Ubuntu in WSL, Linux first** on September 14, 2026. Use native Linux tools for edits, source preparation, checks and actual FirstMate/Herdr worker trials. Native Windows development and acceptance are deferred; the existing Windows refusal guards remain.

The shared repository remains the source of edits. Run commands from its root inside Ubuntu. The check runner stages exact owned package/integration bytes under a private directory on the Linux filesystem, so Git worktrees, process inspection, locks and temporary homes use Linux semantics.

~~~sh
python3 -B tools/linux-dev.py doctor --bin-dir "$LINUX_RUNTIME_BIN"
python3 -B tools/linux-dev.py check --bin-dir "$LINUX_RUNTIME_BIN"
~~~

Omit --bin-dir when the required dependencies are installed in Ubuntu's normal Linux paths. It is repeatable for separate dependency directories. In this workspace the previously staged native Linux binaries are available under .scratch/stage1-runtime/bin; this ignored directory is local runtime preparation, not part of the distribution.

The fixture dependencies are native Linux python3, bash, git, lsof, jq, node, tasks-axi and timeout. The runner checks native executable headers, excludes the inherited Windows PATH and rejects a staging directory on the Windows mount. It does not launch Herdr or a model. Herdr and the two harnesses are additional prerequisites for a separately scoped live trial.

The check command performs the following sequence:

1. Copy and hash the owned package and FirstMate integration into a new Linux directory.
2. Check the research FirstMate HEAD against the distribution pin and reject source changes. Windows checkout line endings are normalized only for this check, with a per-command Git option. The research checkout's files and configuration remain unchanged.
3. Clone its pinned Git objects into a fresh Linux reference with LF files, then invoke integrations/firstmate/prepare.py. Preparation still verifies the complete deployment manifest.
4. Run both owned unittest suites in separate processes with a private HOME, temporary directory, XDG directories and empty harness config directories. No authentication or active profile is inherited.
5. Record test counts, all skip reasons, command exits, source identities and logs. A missing Linux dependency or unexpected skipped test fails the check. Only explicitly native Windows tests may skip.
6. Verify the staged source bytes remained unchanged. Retain the candidate, logs and receipt.json at the printed Linux path for inspection.

The default work root is /tmp/orchflows-firstmate-dev. Use --work-root to retain candidates elsewhere on a native Linux filesystem. Every run creates a new directory and does not overwrite an earlier candidate. Temporary workspaces may be removed by the OS; preserve useful sanitized receipts under ignored repository scratch storage and summarize actual evidence in the living documents. Do not put machine paths, authentication caches or raw session transcripts into tracked documentation.

## Current acceptance boundary

The repository admits one read-only Work component or one explicitly authorized
Linux Review component; see the [Review contract](review-contract.md). Earlier actual Claude and Codex Work trials ran in WSL; their exact package/candidate identities remain in the historical evidence. Passing this new check runner proves the current package/controller/owner fixtures, not a current live fleet release.

Attached Linux Claude workers now receive the foreground shell profile from
FirstMate's spawn/relaunch owner: native background tasks disabled and a
420,000 ms default Bash timeout. This makes the bounded Stage 1 launch match its
foreground acceptance profile. It is not background-process custody or a promise
that arbitrary detached commands can be supervised. See
[Linux verification](linux-first-verification.md).

Current work follows the [normal launch contract](normal-launch.md) and
[verification](normal-launch-verification.md). The owner audit and automatic
project enablement/client context are implemented. Full dynamic composition,
writer joins and custom/meta-workflow parity remain next; current Codex and
broader lifecycle gaps are tracked separately. Do not restore the superseded
harness-first roadmap.

FirstMate remains the only owner of component dispatch, Herdr endpoints, lifecycle and outer delivery. The Linux development runner is a test driver, not a fleet scheduler. It never registers plugins, starts workers or changes active installations. Design-loop is not used to perform this work.


[The Linux acceptance driver](linux-acceptance.md) supplies reproducible actual
Claude Work/Review and optional parent-replacement trials. Its receipts remain
separate from this fixture runner and from historical live identities.
