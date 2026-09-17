# Live FirstMate end-to-end tests

These opt-in tests run a real primary and real workers in Ubuntu (including
WSL). They consume model quota. The Python driver only prepares disposable
projects, sends captain requests, records evidence and checks delivered results.
FirstMate alone selects profiles, launches workers, supervises, reviews, repairs
and delivers. Nothing here is installed with the plugin or changes FirstMate.

The four cases, in order:

1. **Dynamic:** an unnamed request builds an exact-cent CSV aggregation CLI.
2. **Author:** `orch-build-workflow` creates a portable saved workflow with
   separate planning, implementation and independent review. FirstMate trials
   that workflow on a disposable project before reviewing the library.
3. **Saved:** a fresh primary conversation loads the delivered workflow by
   name/path and applies its composition to another fresh project. It has the
   durable FirstMate records, but no authoring conversation.
4. **Regression:** a follow-up dynamic request adds a flag while preserving the
   original interface. Both old behavior and the new output are checked.

All projects are local-only, have no origin, and authorize native guarded merges
only within these disposable fixtures. No remote repositories or PRs are made.
Scenarios describe the public interface; the independent oracle is not put in
worker projects or included in their prompts.

## Run in WSL Ubuntu

Use Python 3.12 or newer, a clean, current FirstMate checkout and its normal installed prerequisites.
The recorded September 17 run used upstream
`3eb5b6334a80e06083e3837f0032a5cec39b8e52`. Verify the upstream revision at the time
of a new run; this suite never updates or resets an existing install.

Choose a fresh Linux filesystem directory outside any ancestor with personal
`CLAUDE.md` instructions. `/var/tmp` works across WSL restarts; `/tmp` may not.
Do not reuse an old home. From Ubuntu, with paths adapted to your machine:

```bash
REPO=/mnt/c/Users/danhm/tools/orchflows-firstmate
LAB=/var/tmp/orchflows-e2e-$(date +%Y%m%d-%H%M%S)
git clone --depth 1 https://github.com/kunchenguid/firstmate.git "$LAB/firstmate"
python3 "$REPO/tests/e2e/run.py" --root "$LAB" init \
  --firstmate "$LAB/firstmate" \
  --core "$REPO/packages/orchflows-firstmate" \
  --tool-path "$PATH"
python3 "$REPO/tests/e2e/run.py" --root "$LAB" start
python3 "$REPO/tests/e2e/run.py" --root "$LAB" status
```

The supplied PATH must resolve Linux `claude`, `herdr`, `treehouse`, `tasks-axi`,
`jq`, Git, Python and FirstMate's other normal prerequisites. A Windows `codex`
launcher on WSL's inherited PATH is not a Linux harness.

The primary launches **from the FirstMate checkout**, with the core plugin
loaded for that session. Claude runs in auto permission mode through its normal
CLI option and FirstMate's supported home setting. Login is reused through a
credential symlink; personal instructions/plugins and model preferences are not
copied. Neither credentials nor the isolated Claude configuration are collected.
Herdr lifecycle actions use FirstMate's guarded named-lab helper. Its required
default-session tripwire stays intact; the driver never stops an existing server.

Inspect and resolve any first-use workspace trust dialog before sending work.
The driver does not automatically accept permission, trust, login or external
import prompts. `key` is an explicit operator tool for a dialog already inspected;
each intervention is logged. An unexpected import prompt means the environment
is contaminated: fix the fixture location instead of importing another workflow
installation.

```bash
python3 "$REPO/tests/e2e/run.py" --root "$LAB" suite --background
tail -f "$LAB/suite.log"
python3 "$REPO/tests/e2e/run.py" --root "$LAB" status
```

`suite` gives each case a one-hour deadline by default (`--timeout SECONDS`).
It never fabricates a completion marker, answers a worker, retries a failed
workflow, or silently repairs an artifact. Timeout/failure exits nonzero and
retains the lab and all unlanded work. Use native FirstMate recovery through the
primary if a run needs help; record that intervention and report it as a limit.
`suite --resume` reverifies already completed cases and continues with cases that
were never sent. It refuses to resend an unfinished request. A process lock
prevents two suites from owning one lab. `verify` reuses each case's exported
commit, even after the regression case has advanced the project's main branch.
`--keep-going` records assertion failures and exercises the remaining cases; the
aggregate still exits nonzero if anything failed. It never resends a timed-out
request. Functional artifact results and strict native-dispatch trace assertions
remain separate in each result file, so an omitted native step cannot be hidden
by a correct output artifact.

`send CASE`, `collect`, `observe`, and `verify CASE` support investigation.
Only one suite should own the lab at a time. A standalone `observe` loop stops
when a file named `stop-observer` exists in the lab. Do not delete a live lab;
finish or cancel through FirstMate first and use its guarded lab teardown.
`close` invokes that teardown only after all started requests reported completion,
native task metadata is gone, and the fixture projects are clean. Artifacts and
logs remain on disk. The default Herdr server is left alone.

## Assertions and evidence

Each case exports the **delivered main commit** before running the oracle.
Checks cover exact cents (including values beyond floating-point and default
Decimal precision), ordering, Unicode, quoted CSV, stdin/files, zero, atomic
error handling, physical line diagnostics, invalid UTF-8, usage errors, seeded
generated ledgers, the delivered unit suite and runnable README examples.
The regression case reruns the original contract, compares unflagged output
byte for byte with the original delivered commit, and checks `--total` and its
documented sample output too.

Workflow assertions use case-scoped native records: loaded skill, dispatch
resolver use for each worker brief, distinct maker/reviewer identities, actual scout reports,
completion statuses, planning output, delivery and unchanged FirstMate code.
Saved-library checks cover manifests, manual invocation, portable instructions,
absence of execution pins, dependencies and an observed trial record.
The fresh primary starts only after native task cleanup; the previous primary
exits through its normal `/exit` command. No worker is interrupted or relaunched
by the test driver. Completion requires an exact standalone assistant marker **and** these checks;
an echoed prompt or a success claim by itself is insufficient.

Evidence is private under the lab (mode 0700):

- `events.jsonl`: requests, interventions, command results and case boundaries.
- `evidence/home/`: briefs, reports, metadata, status, inboxes and backlog.
- `evidence/files.jsonl` and `objects/`: timestamped content versions, including
  records that native cleanup subsequently removes.
- `evidence/transcripts/`: full lab-scoped native transcripts; `tool-calls.jsonl`
  extracts tool names, inputs, times and session IDs for inspection.
- `evidence/processes/`: observed launch flags and working directories.
- `evidence/routing.json`: native dispatch metadata and actual Claude response
  model IDs. A recorded model/effort, an observed flag and a provider-reported
  model are different evidence. Absent effort stays unknown; no cost is invented.
- `delivered/`, `checks/`, `results.json`: exact artifact commits, every oracle
  command/input/output, individual assertions and aggregate outcomes.

For a compact index outside the private lab:

```bash
python3 "$REPO/tests/e2e/run.py" --root "$LAB" report \
  --output "$REPO/artifacts/e2e-report"
```

Capture is restricted to the test home and matching native sessions. It excludes
credential stores and `.env`, and redacts known environment secrets and common
token formats. Full transcripts are still private diagnostic material; inspect
before sharing them. Recording is a ten-second sample, not proof that every
short-lived process was seen. Native transcripts and versioned task records
provide the complementary evidence.

No dispatch rules are authored or injected by default. To test your existing
FirstMate policy, pass `init --dispatch-from /path/to/config/crew-dispatch.json`;
the file is copied verbatim and FirstMate owns validation and selection.
Without an existing rule file or Typesafe
credentials, typed dispatch may be off; the primary still uses FirstMate's normal
dispatch/effort procedure. A passing test does not require different vendors or
models, and does not establish quota-array routing, remote delivery, a Codex
primary, or an unexercised repair branch.

## Fast checks (no model calls)

```bash
python -B -m unittest discover -s tests/e2e
python -B -m unittest discover -s packages/orchflows-firstmate/tests
```

The oracle's own tests include incorrect results, duplicate/unsorted keys,
partial output on failure, wrong diagnostics, and false completion markers.
