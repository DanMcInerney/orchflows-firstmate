# Candidate review: `--json`

**Reviewed commit:** `746e01d2c92db48a015173271f7d2b681b449405` (`fm/roman-json`)

## Verdict: ready

I reviewed the candidate read-only in the requested detached worktree. The diff contains only `roman.py`, `tests/test_roman.py`, and `README.md`. The requested JSON behavior, existing conversion behavior, tests, help text, and README example are all present and verified. I found no repair that blocks acceptance.

## Findings and evidence

- `roman.py:111-119` registers `--json` and describes the three output keys and invalid-value handling. `python3 roman.py --help` exits 0 and includes the JSON description.
- `roman.py:127-143` continues after a `ValueError`, records the failure for the final exit code, writes one `json.dumps` object per value to stdout in JSON mode, and keeps plain-mode success and error output on their existing streams. The JSON object has exactly the keys `input`, `output`, and `ok`; parsed output uses string values and a boolean `ok`.
- Manual CLI checks confirmed valid, invalid, and mixed argument cases, plus mixed standard input. Invalid records stayed in stdout with no stderr; mixed and invalid runs returned 1, and valid output returned 0. `--json --lower` converted lowercase Roman input and emitted lowercase numeral output consistently. `--json --bogus 9` returned 2, with argparse's usage error on stderr and no stdout.
- I loaded `main:roman.py` and compared results for valid input, mixed valid/invalid input, `--lower`, and standard input. Candidate stdout, stderr, and exit codes were identical in each conversion case. For unknown options, exit code 2 and argparse stderr remain; its generated usage synopsis now lists the newly supported `--json` option.
- `tests/test_roman.py:172-235` covers valid, invalid, mixed, standard-input, lowercase-composition, and JSON parsing/key checks. `tests/test_roman.py:296-306` also exercises mixed JSON output through a subprocess and checks exit 1 and empty stderr. The in-process harness restores stdin in a `finally` block (`tests/test_roman.py:100-111`), and subprocess cases isolate their process state.
- `README.md:58-69` documents the flag, error object, and exit status. Running `python3 roman.py --json 1994 IIII` produced the example's two exact JSON lines and returned 1.
- `python3 -m unittest` passed: **36 tests, OK**. `git diff --check main...HEAD` passed. `git status --short` was empty; the candidate diff lists only the three files above.

## Repairs

None.

## Scope limits

This review covered the named candidate commit and the local Python environment. It did not test other Python versions or packaging/deployment environments.
