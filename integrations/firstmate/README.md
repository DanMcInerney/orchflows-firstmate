# Experimental FirstMate task-group integration

This distribution admits one local read-only Work component or one explicitly authorized Linux Review component to FirstMate at `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`. It is the FirstMate-owned execution half of `packages/orchflows-firstmate/`; the package itself never launches a harness. See the [Stage 1 contract](../../docs/stage1-contract.md) for admission, immutable input, uncertainty and delivery boundaries.

The distribution patches seven existing owners and adds controller, storage, launch and lifecycle files. `manifest.json` lists the complete deployable patch/overlay inventory. Preparation validates the complete inventory, clones a clean pinned checkout, applies the patch, and adds the overlay. It neither installs dependencies nor changes a live FirstMate home.

For current development, use the [Ubuntu/WSL check runner](../../docs/linux-development.md). It verifies the pinned research input, creates an LF checkout on the Linux filesystem, calls this distribution's preparation tool and runs both owned suites with isolated homes. Native Windows development is deferred.

For manual preparation from a clean Linux reference, choose a nonexistent disposable candidate path:

```sh
python3 integrations/firstmate/prepare.py \
  --source "$LINUX_FIRSTMATE_SOURCE" --destination "$LINUX_CANDIDATE"
```

The prepared directory is a modified detached FirstMate checkout. Its upstream instructions remain FirstMate source contracts; preparing it does not make this research task a fleet supervisor. Keep real runtime trials in a private FirstMate home and named Herdr lab with the original helper's default-session tripwire. The [runtime record](../../docs/stage1-runtime.md) describes the isolated tested prerequisites.

The administrator creates an ordinary scout brief and clean no-origin Git fixture, then attaches the complete package before the root's first FirstMate launch:

```sh
python3 "$CANDIDATE/bin/fm-task-group.py" --home "$FM_HOME" attach "$ROOT_TASK" \
  --package "$PACKAGE" --project "$PROJECT"
```

Launch the root through the candidate's ordinary `fm-spawn.sh` with explicit Herdr session and Claude or Codex harness. The regenerated root overlay supplies the exact retained package/client paths and current generation. Workers use that attachment's `scripts/firstmate.py` to submit, inspect and gather. The component receives its distinct completion command. Do not invoke internal controller commands directly or substitute direct Herdr/harness launching.

For attached Claude tasks, the same spawn owner translates the declared package/task paths into per-launch Read/Edit permissions after publishing the current generation. It preserves the selected permission mode and existing settings. This avoids requiring a manual outside-directory grant for retained guidance while keeping output grants scoped to the task. The [verification record](../../docs/stage1-verification.md#independent-review-and-final-repair) describes the review finding, repair tests and remaining live Claude acceptance.

The following are isolated fixture checks, not a live compatibility trial. On a POSIX runtime with Bash, Git and Python, set the prepared candidate explicitly:

```sh
FM_STAGE1_FIRSTMATE_ROOT="$CANDIDATE" \
  python3 -B -m unittest discover -s integrations/firstmate/tests
python3 -B -m unittest discover -s packages/orchflows-firstmate/tests
```

The inherited FirstMate regression runner is `bin/fm-test-run.sh`; use its fixture and dependency requirements. The [native Windows controller boundary](../../docs/stage1-windows.md) supplies explicit Git Bash/Python selection, typed path conversion and process ancestry checks for its isolated fixtures. Select that runtime as documented before native controller tests. Actual Windows Stage 1 spawn/relaunch and teardown now refuse before task mutation because native process custody is not implemented; neither these settings nor `--force` enables unsupported workers.

On Linux, current launch supervision checks the original parent lock claims, process identities and ancestry before treating a launching request as waiting. Unknown or abandoned custody remains attention. Attached POSIX teardown also refuses missing process-cleanup evidence and preserves worktree/task records. The [continuation verification](../../docs/stage1-continuation-verification.md) records the 81-case combined suite and separates fixtures from actual runtime acceptance.

The Review extension requires explicit primitive Review and policy explicit-audit at attachment; see the [Review contract](../../docs/review-contract.md). Writers, multiple components, nesting, promotion and remote homes remain rejected. All upstream Orchflows example files remain available for migration; their presence does not certify runtime parity. No global install or published release is performed by this distribution.


For attached Linux Claude workers, the spawn/relaunch owner now supplies
CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1 and BASH_DEFAULT_TIMEOUT_MS=420000
on that worker command. This selects the foreground profile exercised by the
Stage 1 Linux watcher acceptance; it does not claim native background-shell
supervision. The selected permission mode, model, effort and native file
grants remain intact. Ordinary unattached tasks and Codex launches are unchanged.
See [Linux verification](../../docs/linux-first-verification.md).
