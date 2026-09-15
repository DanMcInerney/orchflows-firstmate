# kvlog docs-QA review

**Reviewed commit:** `ca744106b92dfcb7db7d0519b48d19256c6e23e3` ("Complete kvlog docs QA ticket"), branch `fm/kvlog-docs-3`, detached HEAD in the scratch worktree.
**Base:** this commit's only changes over `main` (`d0d0673`) are `README.md`, `ACCEPTANCE.md`, `examples/app.jsonl`, `scripts/acceptance.sh`, and a `.orch/tickets/...` run ticket. `kvlog.py` and `tests/test_kvlog.py` are byte-identical to `main` (`git diff main...HEAD -- kvlog.py tests/test_kvlog.py` is empty) — this is a docs/evidence-only delivery, not a code change.
**Method:** independent, read-only re-execution of every check named in the brief, in this worktree, against the frozen spec at `/tmp/orchflows-e2e/home/data/kvlog-spec-1/report.md`. No files were edited.

## Findings, ordered by impact

### 1. (Medium — writing) README's Usage section buries the actual usage pattern behind an unexplained scratch-directory dance

`README.md:22-37`:

```
The sample log is [`examples/app.jsonl`](examples/app.jsonl). To run the commands below exactly
as written with the file name `app.jsonl`, start at the repository root and run this setup once
in a shell session:

    demo_dir="$(mktemp -d)"
    cp kvlog.py "$demo_dir/kvlog.py"
    cp examples/app.jsonl "$demo_dir/app.jsonl"

Run the following commands in that same shell session. Each command runs from the scratch
directory containing the copied script and sample:

    ( cd "$demo_dir"; python3 kvlog.py app.jsonl )
```

A reader who just wants to try the tool has to: read a paragraph explaining why a scratch directory is needed, run a `mktemp`/`cp` block, remember that `$demo_dir` must survive across the rest of the session, and then read a second block that `cd`s into it inside a subshell — all to reproduce output that `python3 kvlog.py examples/app.jsonl`, run once from the repo root, produces identically. I confirmed this directly: running the plain form from the repo root against `examples/app.jsonl` gives byte-identical output to the three demo blocks (see §3 below). The indirection exists only so the README can contain the literal line `python3 kvlog.py app.jsonl` (to satisfy ACCEPTANCE.md item 14's `grep -Fx` checks against the frozen spec), not because it reflects real usage. That's a legitimate constraint, but it's surfaced to the reader as if it were necessary tool behavior, which buries the actually-simple usage pattern and forces rereading to figure out what's essential vs. incidental. Per `guidance/writing.md`'s Review section ("wording that... buries the point or requires needless rereading"), this is worth fixing.

**Suggested repair:** state the simple form first (`python3 kvlog.py examples/app.jsonl`, from the repo root) as the primary example, and if the literal `app.jsonl` line must stay for the acceptance grep, move the scratch-dir mechanics into a small aside or footnote rather than the main walkthrough path.

### 2. (Low — consistency, not a spec violation) `--top` with a non-integer value produces argparse's generic message instead of the tool's own error voice

Not in the acceptance checklist or the spec's canonical-message table, so not a compliance defect, but worth noting for consistency:

```
$ python3 kvlog.py --top abc examples/app.jsonl
usage: kvlog [options] [FILE ...]
kvlog: error: argument --top: invalid int value: 'abc'
```

versus the spec-mandated message for the zero/negative case, `kvlog: error: --top must be a positive integer` (`kvlog.py:230-231`). Both correctly exit 2 with nothing on stdout, so behavior is correct — only the wording is inconsistent between "not a positive integer" (custom message) and "not parseable as int at all" (argparse default). Cosmetic; no action required unless the team wants one uniform message for all bad `--top` values.

### 3. (Low — test coverage gap) The repeated-`-` usage error is exercised but not asserted precisely

`tests/test_kvlog.py:337-355` (`test_cli_invalid_top_and_invalid_bounds_return_two`) includes `(["-", "-"], None)` as a case — the `None` expected-message means the test only checks exit code 2 and empty stdout, not the actual stderr text. I confirmed the real behavior independently (see novel-input #3 below): `kvlog: error: '-' may only be given once`. The behavior is correct; the test just doesn't pin the message the way its siblings do. Also note: this path isn't in ACCEPTANCE.md's 17-item checklist at all, because the frozen spec's section 6 checklist doesn't include it — that's a spec-checklist gap, not a delivery defect.

### 4. (Informational) Python-3.9 floor claim not independently executed

README.md:7 and the spec both assert a Python 3.9+ floor, and `kvlog.py:36-37` manually strips a trailing `Z` before calling `datetime.fromisoformat` specifically because native `Z` support only landed in 3.11 — consistent with the claim. This worktree only has Python 3.12.3 available (`/usr/bin/python3.9` etc. do not exist), so I could not execute the suite under 3.9 to confirm; I'm relying on code inspection, not execution, for this one claim.

## 2. Acceptance checklist reproduction (spec §6 vs. ACCEPTANCE.md)

Ran the committed runner, `scripts/acceptance.sh`, which replays all 17 frozen spec items with byte-exact `cmp` comparisons:

```
1 PASS
2 PASS
3 PASS
4 PASS
5 PASS
6 PASS
7 PASS
8 PASS
9 PASS
10 PASS
11 PASS
12 PASS
13 PASS
14 PASS
15 PASS
16 PASS
17 PASS
```
Exit code: 0. Every row matches ACCEPTANCE.md's table exactly — I found no row I could not reproduce.

## 3. README command reproduction

Ran the exact three demo commands from README.md (via the documented `demo_dir` setup) and the two grep-checked snippets separately:

- `python3 kvlog.py app.jsonl` → output matched README.md:39-53 exactly.
- `cat app.jsonl | python3 kvlog.py --json` → output matched README.md:64-66 exactly.
- `python3 kvlog.py --top 3 --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z app.jsonl` → output matched README.md:77-90 exactly.
- All nine `grep -Fx` literal-line checks from ACCEPTANCE.md item 14 pass (verified inside `scripts/acceptance.sh`'s item 14, and independently).
- Install snippet (README.md:11-14): validated via ACCEPTANCE.md item 15's equivalent (`install -m 755 kvlog.py "$tmp/bin/kvlog"` then run it) rather than against the real `$HOME/.local/bin`, to avoid writing outside the worktree. Passed, exit 0, exact JSON.

No discrepancies between README-shown output and actual output.

## 4. `python3 -m unittest` — verbatim result

```
$ python3 -m unittest
....................
----------------------------------------------------------------------
Ran 20 tests in 0.224s

OK
```

Exit code 0. Matches ACCEPTANCE.md's claim ("20 tests in 0.214s... OK") and the spec's requirement of ≥15 tests with no failures.

## 5. Three novel inputs not covered by the acceptance checklist

1. **Malformed line in the middle of a file** (valid line 1, broken JSON line 2, valid line 3):
   ```
   $ python3 kvlog.py mid_malformed.jsonl
   kvlog: <path>/mid_malformed.jsonl:2: invalid JSON
   exit=1
   ```
   Correct: reports the true physical line number (2), not line 1 or a count of valid records.

2. **Lowercase level** (`"level":"error"`):
   ```
   $ printf '...' | python3 kvlog.py
   kvlog: <stdin>:1: unsupported level 'error'
   exit=1
   ```
   Correct per spec §2: level must be exactly one of the four uppercase strings; lowercase is rejected with the right message and line.

3. **Repeated `-` for stdin** (`python3 kvlog.py - -`):
   ```
   usage: kvlog [options] [FILE ...]
   kvlog: error: '-' may only be given once
   exit=2
   ```
   Correct per spec §2 ("a repeated `-`" is a usage error). This path is exercised by the unit suite but not by ACCEPTANCE.md's 17-item checklist (see Finding 3) — a spec-checklist gap, not a code defect.

Bonus check beyond the requested three: `--since` exactly equal to `--until` (equal, not reversed) succeeds (exit 0) and includes both boundary records, confirming the "only `since > until` errors" rule is implemented correctly, not "since >= until".

## Verdict

**Ready with the listed repair.** Every acceptance-checklist row reproduces exactly, every README command's shown output matches actual output, the unit suite passes (20/20, matching the recorded count), and all three novel inputs plus the bonus boundary check behave correctly per the frozen spec. Source and tests are unchanged from `main`, so no regression risk was introduced by this docs-only delivery.

The one repair worth making before calling this done is Finding 1 (README's Usage section burying the real usage pattern behind an unexplained scratch-directory dance) — a writing-quality fix, not a functional one. Findings 2-4 are optional polish/coverage notes, not blockers.
