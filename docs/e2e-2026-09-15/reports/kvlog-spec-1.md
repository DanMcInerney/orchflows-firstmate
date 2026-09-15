# kvlog design scout report

**Recommendation:** build a flat, standard-library-only Python 3 CLI in one `kvlog.py` module, with one `unittest` module and a README that documents local installation and use. This is a design report only; I changed no project files. Lavish was not used, as directed by the brief. I found no unresolved captain choice: this report makes concrete decisions for unspecified defaults and edge behavior.

## Evidence and bound

The inspected worktree is `/home/danhm/.treehouse/kvlog-0f3c59/1/kvlog`. `git status --short --branch` returned `## HEAD (no branch)`, and `git log -1 --oneline` returned `682a53c Seed kvlog`. `ls -la` showed only `.git`, `.gitignore`, and `README.md`; the targeted `rg --files -g 'README*' -g 'AGENTS.md' -g '*.py' -g 'pyproject.toml' -g 'setup.cfg' -g 'tox.ini' -g 'Makefile'` returned only `README.md`. `README.md:1-3` contains only the title and the sentence “Structured log summary CLI. Built through Orchflows on FirstMate.” There is no implementation, test suite, or packaging configuration to validate. The captain's request is therefore the primary evidence for product behavior; all detailed choices below are recommendations, not claims about existing behavior.

I read the requested Make guidance in Firstmate's `guidance/writing.md`, `guidance/code.md`, and `libraries/mixed-build/guidance/code.cli.md`, and followed the read-only `orch-investigate` lane. The bound is design and acceptance planning for one maker's first implementation; code behavior, runtime compatibility, and actual test output remain unverified until the artifact is built.

## 1. Scope and non-goals

Implement a Python 3.9+ command-line program that reads JSON Lines from UTF-8 files or stdin, validates each nonblank record, applies inclusive time filters, and summarizes matching records. Keep parsing, filtering, aggregation, and rendering in one small module; use only the standard library. Add tests runnable by `python3 -m unittest` and replace the README stub with installation and usage instructions.

Do not add a service, database, third-party dependency, JSON schema system, arbitrary level registry, visualization, or packaging/build backend. Stream records while aggregating counters and the time extrema; memory should scale with distinct service names and ERROR messages, not total input lines.

## 2. Command-line contract

Invocation is `kvlog [options] [FILE ...]`; during development use `python3 kvlog.py ...`. No file arguments means read stdin. A positional `-` also means stdin and may appear at most once; named files are read in argument order and may be combined with `-`. Each file is UTF-8 JSON Lines. Physical line numbering starts at 1 for each input source. The diagnostic source label for stdin is exactly `<stdin>`.

| Option | Default | Effect |
|---|---|---|
| `-h`, `--help` | — | Print usage, every option, defaults, and effects to stdout; exit 0. |
| `--json` | Human output | Emit the compact JSON object below instead of the human summary. |
| `--top N` | `5` | Show at most N distinct ERROR messages, ordered by count descending then message ascending. N must be a positive integer; zero or negative is a usage error. |
| `--since ISO8601` | None | Include records with timestamps at or after this instant (inclusive). |
| `--until ISO8601` | None | Include records with timestamps at or before this instant (inclusive). |
| `FILE ...` | stdin | Read one or more files; `-` selects stdin. With no FILE, read stdin. |

A record must be a JSON object with string-valued `ts`, `level`, `service`, and `msg`. `level` must be exactly `DEBUG`, `INFO`, `WARN`, or `ERROR`. Extra keys are accepted and ignored. A blank or whitespace-only physical line is ignored and does not count as a record. `total_lines` means the number of valid, nonblank records remaining after time filtering.

The minimum supported version is Python 3.9. `parse_timestamp` must normalize a trailing `Z` itself by replacing it with `+00:00` before calling `datetime.fromisoformat`; do not rely on interpreter-specific native `Z` parsing. `ts`, `--since`, and `--until` accept ISO 8601 date-times supported by `datetime.fromisoformat` after that normalization. A timestamp without an offset is interpreted as UTC. Offset-aware times are converted to UTC before comparison and output. Filters are inclusive. If both bounds are present and `since > until`, return a usage error. A valid input that filters to zero records succeeds with an empty summary.

The JSON output is one compact UTF-8 JSON object on stdout, followed by a newline. Object keys appear in this documented order; consumers should use keys rather than rely on object order. Service keys are sorted lexically. `by_service` includes only services present in matching records; it is not zero-padded, unlike `by_level`, which always has the fixed four level keys including zero counts. The error list is sorted by count descending and then message ascending. The time range is over matching records and uses normalized UTC ISO 8601 strings; both ends are `null` for an empty result.

```json
{
  "total_lines": 3,
  "by_level": {"DEBUG": 0, "INFO": 1, "WARN": 0, "ERROR": 2},
  "by_service": {"auth": 2, "web": 1},
  "top_errors": [
    {"message": "timeout", "count": 2},
    {"message": "denied", "count": 1}
  ],
  "time_range": {
    "start": "2025-01-01T05:00:00Z",
    "end": "2025-01-03T00:00:00Z"
  }
}
```

Human output has this stable layout. Quote service names and messages as JSON strings so embedded whitespace and newlines stay unambiguous. Use `(none)` for an empty service list, error list, or time range; keep all four level rows even when their count is zero.

```text
Total lines: 3
Counts by level:
  DEBUG: 0
  INFO: 1
  WARN: 0
  ERROR: 2
Counts by service:
  "auth": 2
  "web": 1
Top 5 ERROR messages:
  2: "timeout"
  1: "denied"
Time range: 2025-01-01T05:00:00Z .. 2025-01-03T00:00:00Z
```

Exit 0 for a completed summary, including empty input/results, and for `--help`. Exit 1 for malformed input, missing or mistyped required fields, invalid record timestamps/levels, file-open/read failures, or UTF-8 decoding errors. Use these canonical stderr templates (with `{source}`, `{line}`, `{key}`, `{value}`, and `{reason}` replaced by the indicated source, physical line, field/value, or OS error text): invalid JSON `kvlog: {source}:{line}: invalid JSON`; non-object JSON `kvlog: {source}:{line}: expected a JSON object`; missing key `kvlog: {source}:{line}: missing required key '{key}'`; wrong field type `kvlog: {source}:{line}: field '{key}' must be a string`; unsupported level `kvlog: {source}:{line}: unsupported level '{value}'`; invalid `ts` `kvlog: {source}:{line}: invalid timestamp '{value}'`; file open/read failure `kvlog: {source}: cannot read input: {reason}` (no line segment); UTF-8 decode error `kvlog: {source}:{line}: input is not valid UTF-8`. Stop parsing at the first malformed record across all sources and do not print a partial summary. Exit 2 for command-line usage errors, including invalid option values, invalid filter timestamps, reversed bounds, a repeated `-`, or unrecognized options. For invalid `--since`, print exactly `kvlog: error: invalid --since timestamp`; for invalid `--until`, print exactly `kvlog: error: invalid --until timestamp`; for `since > until`, print exactly `kvlog: error: --since must be less than or equal to --until`. All diagnostics go to stderr; stdout contains only the complete summary or help text.

## 3. Module layout

Create only these files for the first slice:

- `kvlog.py`: executable script with `#!/usr/bin/env python3`; no external imports. Keep CLI and domain behavior here to make the first delivery buildable in one sitting.
- `tests/__init__.py`: make unittest discovery reliable across supported Python 3 versions.
- `tests/test_kvlog.py`: isolated standard-library tests with temporary streams/files and subprocess checks for the CLI contract.
- `README.md`: replace the stub with requirements, installation, usage, options/defaults, output fields, exit codes, and test command.

Public functions and ownership in `kvlog.py`:

- `parse_timestamp(value)`: validate an ISO date-time, assume UTC when no offset is present, return a UTC-aware `datetime`.
- `parse_record(text, source, line_number)`: decode one nonblank JSON line, validate object shape and required field types/values, normalize `ts`, and raise one input exception carrying source and line on failure.
- `iter_records(stream, source)`: enumerate physical lines, skip blanks, and yield validated records.
- `summarize(records, since=None, until=None, top=5)`: apply inclusive filters and compute total, all level counts, service counts, top ERROR messages, and time extrema in the documented shape.
- `render_text(summary, top)`: render the stable human format above.
- `render_json(summary)`: serialize the documented compact JSON shape deterministically.
- `build_parser()` and `main(argv=None)`: define help/arguments, validate usage-level values, open each requested input, route stdin, write exactly one summary only after successful parsing, map failures to exit codes, and keep diagnostics on stderr.

Do not mix JSON parsing with aggregation or presentation. Keep errors from record parsing source-aware so the CLI can report the offending line without emitting a partial result.

## 4. Edge cases the implementation must handle

- Empty or whitespace-only lines are skipped; line numbering still counts them. A malformed nonblank line reports its physical line number and exits 1.
- Valid JSON that is not an object, missing any required key, a non-string required value, an unsupported level, or an invalid `ts` is malformed input. Extra object keys do not affect parsing.
- Parse offset-aware timestamps and compare instants correctly across offsets. Normalize output range endpoints to UTC with `Z`; interpret timestamps lacking an offset as UTC so comparisons remain deterministic.
- Empty stdin/files and filters that exclude all records return 0, zero totals and level counts, empty service/error collections, and a null/null time range.
- `--top` larger than the distinct ERROR message count returns every available message; ties use ascending message order. Repeated ERROR messages are counted together.
- `--since` and `--until` boundaries are inclusive. Each filter may independently exclude every record without turning that into an error. Invalid filter syntax or `since > until` is a usage error (2).
- Parse and validate all nonblank records even when their timestamps would later fall outside the selected window; malformed input must not be silently hidden by filtering.
- If any source fails, print no summary, even if earlier sources were read successfully. Report line numbers per source and preserve input argument order.

## 5. Test plan

Add these tests to `tests/test_kvlog.py`; each test should own its fixtures and assert observable behavior, not private implementation details.

1. `test_read_skips_blank_lines_and_ignores_extra_fields` — blank lines do not count; extra JSON keys are harmless.
2. `test_read_reports_malformed_json_with_source_line` — malformed JSON after a blank line carries the right source and physical line.
3. `test_read_rejects_missing_keys_and_invalid_field_types` — missing keys, wrong field types, unknown levels, and invalid record timestamps are rejected.
4. `test_parse_timestamp_normalizes_offsets_and_assumes_utc_when_naive` — offsets and `Z` normalize to UTC; no offset means UTC.
5. `test_summarize_applies_inclusive_since_until_filters` — both endpoints are included and out-of-window records are excluded.
6. `test_summarize_returns_empty_shape_when_filters_exclude_every_record` — empty result has zeroes, empty collections, and null time endpoints.
7. `test_summarize_counts_services_and_levels_after_filtering` — totals and group counts describe only matched records, with every level key present.
8. `test_summarize_sorts_error_frequency_then_message_and_caps_top` — duplicate messages aggregate, ties sort deterministically, and N caps the list.
9. `test_render_text_has_stable_human_format_for_data_and_empty_summary` — headings, quoting, counts, ranges, and empty markers match the contract.
10. `test_render_json_has_documented_shape_and_normalized_time_range` — exact key names, types, ordering, and null/range forms match the contract.
11. `test_cli_reads_stdin_and_multiple_files` — no path reads stdin; multiple files combine in argument order; `-` can select stdin once.
12. `test_cli_malformed_input_returns_one_without_stdout` — exit 1, source/line diagnostic on stderr, and no partial summary.
13. `test_cli_missing_required_key_reports_line_and_returns_one` — missing-key diagnostic includes line and exits 1.
14. `test_cli_invalid_top_and_invalid_bounds_return_two` — zero/negative N, invalid filter timestamps, reversed bounds, and duplicate `-` are usage errors.
15. `test_cli_help_documents_options_defaults_and_effects` — help exits 0 and documents every option, default, stdin behavior, and filter semantics.

## 6. Acceptance checklist

Run from the repository root after implementation. The first block creates reusable temporary fixtures; later commands in this checklist use `$tmp`. These checks are intentionally shell-visible so a reviewer can verify exact stdout, stderr, and status.

**Fixture setup**

```sh
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/sample.jsonl" <<'JSON'
{"ts":"2025-01-03T00:00:00Z","level":"ERROR","service":"auth","msg":"timeout","request_id":"a"}
{"ts":"2025-01-01T00:00:00-05:00","level":"INFO","service":"web","msg":"ok"}
{"ts":"2025-01-02T00:00:00Z","level":"ERROR","service":"auth","msg":"denied"}
{"ts":"2025-01-02T00:00:00Z","level":"ERROR","service":"auth","msg":"timeout"}
JSON
sed -n '1,2p' "$tmp/sample.jsonl" > "$tmp/part1.jsonl"
sed -n '3,4p' "$tmp/sample.jsonl" > "$tmp/part2.jsonl"
sed -n '2p' "$tmp/sample.jsonl" > "$tmp/first.jsonl"
printf '%s\n' '{"ts":' > "$tmp/second.jsonl"
printf '%s\n' '{"broken":' > "$tmp/third.jsonl"
```

1. **Default summary and stdin:** run `cat "$tmp/sample.jsonl" | python3 kvlog.py`. Exit 0; stdout is exactly the following, stderr is empty:

   ```text
   Total lines: 4
   Counts by level:
     DEBUG: 0
     INFO: 1
     WARN: 0
     ERROR: 3
   Counts by service:
     "auth": 3
     "web": 1
   Top 5 ERROR messages:
     2: "timeout"
     1: "denied"
   Time range: 2025-01-01T05:00:00Z .. 2025-01-03T00:00:00Z
   ```

2. **Multiple file inputs:** run `python3 kvlog.py "$tmp/part1.jsonl" "$tmp/part2.jsonl"`. Exit 0 with exactly the same stdout as item 1 and empty stderr.

3. **`--json` and `--top 1`:** run `cat "$tmp/sample.jsonl" | python3 kvlog.py --json --top 1`. Exit 0; stdout is exactly one line below and stderr is empty:

   ```json
   {"total_lines":4,"by_level":{"DEBUG":0,"INFO":1,"WARN":0,"ERROR":3},"by_service":{"auth":3,"web":1},"top_errors":[{"message":"timeout","count":2}],"time_range":{"start":"2025-01-01T05:00:00Z","end":"2025-01-03T00:00:00Z"}}
   ```

4. **`--since` and `--until`, inclusive:** run `python3 kvlog.py --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z "$tmp/sample.jsonl"`. Exit 0; stdout is exactly:

   ```text
   Total lines: 3
   Counts by level:
     DEBUG: 0
     INFO: 0
     WARN: 0
     ERROR: 3
   Counts by service:
     "auth": 3
   Top 5 ERROR messages:
     2: "timeout"
     1: "denied"
   Time range: 2025-01-02T00:00:00Z .. 2025-01-03T00:00:00Z
   ```

   stderr is empty. This proves both flags and inclusion of records exactly on each bound.

5. **`--top` greater than distinct errors:** run `python3 kvlog.py --top 20 --json "$tmp/sample.jsonl"`. Exit 0; stdout is exactly the following line and stderr is empty:

   ```json
   {"total_lines":4,"by_level":{"DEBUG":0,"INFO":1,"WARN":0,"ERROR":3},"by_service":{"auth":3,"web":1},"top_errors":[{"message":"timeout","count":2},{"message":"denied","count":1}],"time_range":{"start":"2025-01-01T05:00:00Z","end":"2025-01-03T00:00:00Z"}}
   ```

6. **Filters excluding everything:** run each command below. Both exit 0 and print the following exact human output, with empty stderr:

   ```sh
   python3 kvlog.py --since 2030-01-01T00:00:00Z "$tmp/sample.jsonl"
   python3 kvlog.py --until 2020-01-01T00:00:00Z "$tmp/sample.jsonl"
   ```

   ```text
   Total lines: 0
   Counts by level:
     DEBUG: 0
     INFO: 0
     WARN: 0
     ERROR: 0
   Counts by service:
     (none)
   Top 5 ERROR messages:
     (none)
   Time range: none
   ```

7. **`--help`:** run this check. It exits 0, help goes to stdout, stderr is empty, and each `grep` prints its exact matching help line; all option defaults and effects are therefore checked.

   ```sh
   python3 kvlog.py --help > "$tmp/help" 2> "$tmp/err"
   test ! -s "$tmp/err"
   grep -F 'usage: kvlog [options] [FILE ...]' "$tmp/help"
   grep -F -- '-h, --help' "$tmp/help"
   grep -F -- '--json' "$tmp/help" | grep -F '(default: human summary)'
   grep -F -- '--top N' "$tmp/help" | grep -F '(default: 5)'
   grep -F -- '--since ISO8601' "$tmp/help" | grep -F '(inclusive; default: none)'
   grep -F -- '--until ISO8601' "$tmp/help" | grep -F '(inclusive; default: none)'
   grep -F 'With no FILE, read stdin; FILE may be repeated and - selects stdin.' "$tmp/help"
   ```

8. **Malformed JSON / line number / exit 1:** run the following. It must print `exit=1`, then `stdout=<empty>`, then exactly `kvlog: <stdin>:3: invalid JSON` on stderr:

   ```sh
   set +e
   printf '%s\n\n%s\n' '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"api","msg":"ok"}' '{"ts":' | python3 kvlog.py > "$tmp/out" 2> "$tmp/err"
   rc=$?
   set -e
   test "$rc" -eq 1 && test ! -s "$tmp/out"
   printf 'exit=%s\nstdout=<empty>\n' "$rc"
   cat "$tmp/err"
   ```

9. **Missing required key / exit 1:** run `printf '%s\n' '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"api"}' | python3 kvlog.py`. Exit 1, stdout empty, and stderr exactly `kvlog: <stdin>:1: missing required key 'msg'`.

10. **Usage error / exit 2:** run this check. It exits 2, stdout is empty, and the last stderr line is exactly `kvlog: error: --top must be a positive integer` (argparse's usage line precedes it).

   ```sh
   set +e
   python3 kvlog.py --top 0 "$tmp/sample.jsonl" > "$tmp/out" 2> "$tmp/err"
   rc=$?
   set -e
   test "$rc" -eq 2 && test ! -s "$tmp/out"
   printf 'exit=%s\nstdout=<empty>\n' "$rc"
   tail -n 1 "$tmp/err"
   ```

11. **Invalid `--since` value / exit 2:** run this check. It prints `exit=2`, then `stdout=<empty>`, then exactly `kvlog: error: invalid --since timestamp` as the last stderr line.

   ```sh
   set +e
   python3 kvlog.py --since not-a-date "$tmp/sample.jsonl" > "$tmp/out" 2> "$tmp/err"
   rc=$?
   set -e
   test "$rc" -eq 2 && test ! -s "$tmp/out"
   printf 'exit=%s\nstdout=<empty>\n' "$rc"
   tail -n 1 "$tmp/err"
   ```

12. **Invalid `--until` value / exit 2:** run this check. It prints `exit=2`, then `stdout=<empty>`, then exactly `kvlog: error: invalid --until timestamp` as the last stderr line.

   ```sh
   set +e
   python3 kvlog.py --until not-a-date "$tmp/sample.jsonl" > "$tmp/out" 2> "$tmp/err"
   rc=$?
   set -e
   test "$rc" -eq 2 && test ! -s "$tmp/out"
   printf 'exit=%s\nstdout=<empty>\n' "$rc"
   tail -n 1 "$tmp/err"
   ```

13. **Reversed time bounds / exit 2:** run this check. It prints `exit=2`, then `stdout=<empty>`, then exactly `kvlog: error: --since must be less than or equal to --until` as the last stderr line.

   ```sh
   set +e
   python3 kvlog.py --since 2025-01-04T00:00:00Z --until 2025-01-03T00:00:00Z "$tmp/sample.jsonl" > "$tmp/out" 2> "$tmp/err"
   rc=$?
   set -e
   test "$rc" -eq 2 && test ! -s "$tmp/out"
   printf 'exit=%s\nstdout=<empty>\n' "$rc"
   tail -n 1 "$tmp/err"
   ```

14. **README install, usage, and test instructions:** run these checks. Each prints the exact matching README line and exits 0.

   ```sh
   grep -Fx 'Requires Python 3.9+; no third-party dependencies.' README.md
   grep -Fx 'install -m 755 kvlog.py "$HOME/.local/bin/kvlog"' README.md
   grep -Fx 'python3 kvlog.py app.jsonl' README.md
   grep -Fx 'cat app.jsonl | python3 kvlog.py --json' README.md
   grep -Fx 'python3 kvlog.py --top 3 --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z app.jsonl' README.md
   grep -Fx 'With no FILE, kvlog reads stdin; pass - to read stdin alongside files.' README.md
   grep -Fx 'JSON fields: total_lines, by_level, by_service, top_errors, and time_range.' README.md
   grep -Fx 'Exit codes: 0 success, 1 malformed/input failure, 2 usage error.' README.md
   grep -Fx 'python3 -m unittest' README.md
   ```

15. **README installation works without dependencies:** run `mkdir -p "$tmp/bin" && install -m 755 kvlog.py "$tmp/bin/kvlog" && printf '%s\n' '{"ts":"2025-01-01T00:00:00Z","level":"WARN","service":"api","msg":"slow"}' | "$tmp/bin/kvlog" --json`. Exit 0; stdout is exactly `{"total_lines":1,"by_level":{"DEBUG":0,"INFO":0,"WARN":1,"ERROR":0},"by_service":{"api":1},"top_errors":[],"time_range":{"start":"2025-01-01T00:00:00Z","end":"2025-01-01T00:00:00Z"}}`; stderr is empty.

16. **Stop at the first malformed record across input sources:** run this check with a valid first file followed by malformed second and third files. It prints `exit=1`, then `stdout=<empty>`, and exactly one stderr line: `kvlog: $tmp/second.jsonl:1: invalid JSON`. No diagnostic for the third file is printed.

   ```sh
   set +e
   python3 kvlog.py "$tmp/first.jsonl" "$tmp/second.jsonl" "$tmp/third.jsonl" > "$tmp/out" 2> "$tmp/err"
   rc=$?
   set -e
   test "$rc" -eq 1 && test ! -s "$tmp/out"
   printf 'exit=%s\nstdout=<empty>\n' "$rc"
   cat "$tmp/err"
   ```

17. **Unit suite:** run `python3 -m unittest` from the repository root. Exit 0, stdout empty, stderr contains `Ran N tests in ...` for N >= 15 followed by `OK`, and contains no failure or error report.

   ```sh
   set +e
   python3 -m unittest > "$tmp/tests.out" 2> "$tmp/tests.err"
   rc=$?
   set -e
   test "$rc" -eq 0 && test ! -s "$tmp/tests.out"
   grep -E '^Ran (1[5-9]|[2-9][0-9]|[1-9][0-9]{2,}) tests in .+s$' "$tmp/tests.err"
   grep -Fx 'OK' "$tmp/tests.err"
   ! grep -E '^(FAILED|ERROR:)' "$tmp/tests.err"
   ```

## Recommendation

Proceed with the one-module design above. It gives the maker a clear ownership boundary, preserves the standard-library-only constraint, and makes sorting, timezone handling, filtering, error reporting, and empty-result behavior deterministic for both tests and reviewers.
