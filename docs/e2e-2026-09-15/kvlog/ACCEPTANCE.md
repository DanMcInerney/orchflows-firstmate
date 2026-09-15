# Acceptance results

Executed all 17 items from section 6 of the frozen spec report with the committed runner, `scripts/acceptance.sh`. The runner continued through every item and would print actual stdout, stderr, and exit code on failure. All 17 items passed. I also ran the three README sample commands against `examples/app.jsonl`; their output matched the documented blocks exactly.

| Item | Command | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| 1 | <code>cat "$tmp/sample.jsonl" &#124; python3 kvlog.py</code> | Exit 0; exact default summary; stderr empty. | Exit 0; default summary matched exactly; stderr empty. | PASS |
| 2 | `python3 kvlog.py "$tmp/part1.jsonl" "$tmp/part2.jsonl"` | Exit 0; same exact summary as item 1; stderr empty. | Exit 0; summary matched item 1 exactly; stderr empty. | PASS |
| 3 | <code>cat "$tmp/sample.jsonl" &#124; python3 kvlog.py --json --top 1</code> | Exit 0; exact compact JSON with only the most frequent error; stderr empty. | Exit 0; compact JSON matched exactly; stderr empty. | PASS |
| 4 | `python3 kvlog.py --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z "$tmp/sample.jsonl"` | Exit 0; exact summary including both inclusive boundaries; stderr empty. | Exit 0; filtered summary matched exactly; both boundary records included; stderr empty. | PASS |
| 5 | `python3 kvlog.py --top 20 --json "$tmp/sample.jsonl"` | Exit 0; exact compact JSON with every distinct error; stderr empty. | Exit 0; both distinct errors returned in the expected order; stderr empty. | PASS |
| 6 | `python3 kvlog.py --since 2030-01-01T00:00:00Z "$tmp/sample.jsonl"`<br>`python3 kvlog.py --until 2020-01-01T00:00:00Z "$tmp/sample.jsonl"` | Both exit 0 and print the exact empty summary; stderr empty. | Both commands exited 0 and printed the exact empty summary; stderr empty. | PASS |
| 7 | `python3 kvlog.py --help` plus the seven grep checks from the spec | Exit 0; all required help lines match; stderr empty. | Exit 0; all seven exact help lines printed; stderr empty. | PASS |
| 8 | <code>printf '%s\n\n%s\n' '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"api","msg":"ok"}' '{"ts":' &#124; python3 kvlog.py</code> | Exit 1; stdout empty; stderr exactly reports invalid JSON at stdin line 3. | Exit 1; stdout empty; stderr was `kvlog: <stdin>:3: invalid JSON`. | PASS |
| 9 | <code>printf '%s\n' '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"api"}' &#124; python3 kvlog.py</code> | Exit 1; stdout empty; exact missing-key diagnostic. | Exit 1; stdout empty; stderr was `kvlog: <stdin>:1: missing required key 'msg'`. | PASS |
| 10 | `python3 kvlog.py --top 0 "$tmp/sample.jsonl"` | Exit 2; stdout empty; final diagnostic says top must be positive. | Exit 2; stdout empty; final diagnostic was `kvlog: error: --top must be a positive integer`. | PASS |
| 11 | `python3 kvlog.py --since not-a-date "$tmp/sample.jsonl"` | Exit 2; stdout empty; final diagnostic identifies invalid since timestamp. | Exit 2; stdout empty; final diagnostic was `kvlog: error: invalid --since timestamp`. | PASS |
| 12 | `python3 kvlog.py --until not-a-date "$tmp/sample.jsonl"` | Exit 2; stdout empty; final diagnostic identifies invalid until timestamp. | Exit 2; stdout empty; final diagnostic was `kvlog: error: invalid --until timestamp`. | PASS |
| 13 | `python3 kvlog.py --since 2025-01-04T00:00:00Z --until 2025-01-03T00:00:00Z "$tmp/sample.jsonl"` | Exit 2; stdout empty; final diagnostic identifies reversed bounds. | Exit 2; stdout empty; final diagnostic was `kvlog: error: --since must be less than or equal to --until`. | PASS |
| 14 | The nine exact `grep -Fx ... README.md` checks in section 6 of the spec | Every required README line prints exactly; all commands exit 0. | All nine requested lines printed exactly; every grep exited 0. | PASS |
| 15 | <code>mkdir -p "$tmp/bin" && install -m 755 kvlog.py "$tmp/bin/kvlog" && printf '%s\n' '{"ts":"2025-01-01T00:00:00Z","level":"WARN","service":"api","msg":"slow"}' &#124; "$tmp/bin/kvlog" --json</code> | Exit 0; exact one-record JSON; stderr empty. | Exit 0; installed executable emitted the exact expected JSON; stderr empty. | PASS |
| 16 | `python3 kvlog.py "$tmp/first.jsonl" "$tmp/second.jsonl" "$tmp/third.jsonl"` | Exit 1; stdout empty; only the second input's line-1 error is reported. | Exit 1; stdout empty; only `second.jsonl:1: invalid JSON` was reported; third input was not read. | PASS |
| 17 | `python3 -m unittest` and the test-report grep checks from section 6 | Exit 0; at least 15 tests; Ran line followed by OK; no failures. | Exit 0; 20 tests ran in 0.250s; `OK`; no failures. | PASS |

The nine README checks in item 14 were:
- `grep -Fx 'Requires Python 3.9+; no third-party dependencies.' README.md`
- `grep -Fx 'install -m 755 kvlog.py "$HOME/.local/bin/kvlog"' README.md`
- `grep -Fx 'python3 kvlog.py app.jsonl' README.md`
- `grep -Fx 'cat app.jsonl | python3 kvlog.py --json' README.md`
- `grep -Fx 'python3 kvlog.py --top 3 --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z app.jsonl' README.md`
- `grep -Fx 'With no FILE, kvlog reads stdin; pass - to read stdin alongside files.' README.md`
- `grep -Fx 'JSON fields: total_lines, by_level, by_service, top_errors, and time_range.' README.md`
- `grep -Fx 'Exit codes: 0 success, 1 malformed/input failure, 2 usage error.' README.md`
- `grep -Fx 'python3 -m unittest' README.md`
