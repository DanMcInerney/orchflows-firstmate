#!/usr/bin/env bash
# Replays the frozen acceptance checklist from the kvlog spec report.
# No top-level errexit: every item runs even after a failure.

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root" || exit 2

# Fixture setup from the spec report.
tmp="$(mktemp -d)"
trap 'python3 -c "import shutil,sys; shutil.rmtree(sys.argv[1])" "$tmp"' EXIT
export tmp

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

failures=0
empty="$tmp/empty"
: > "$empty"

check_item() {
    item_number="$1"
    expected_exit="$2"
    expected_stdout="$3"
    expected_stderr="$4"
    item_script="$(cat)"
    actual_stdout="$tmp/item-$item_number.stdout"
    actual_stderr="$tmp/item-$item_number.stderr"

    bash -c "$item_script" > "$actual_stdout" 2> "$actual_stderr"
    actual_exit="$?"
    if [ "$item_number" -eq 17 ]; then
        grep -E '^Ran (1[5-9]|[2-9][0-9]|[1-9][0-9]{2,}) tests in .+s$' "$tmp/tests.err" > "$expected_stdout"
        grep -Fx 'OK' "$tmp/tests.err" >> "$expected_stdout"
    fi
    if [ "$actual_exit" -eq "$expected_exit" ] &&
        cmp -s "$actual_stdout" "$expected_stdout" &&
        cmp -s "$actual_stderr" "$expected_stderr"; then
        printf '%s PASS\n' "$item_number"
    else
        failures=1
        printf '%s FAIL\nstdout:\n' "$item_number"
        if [ -s "$actual_stdout" ]; then cat "$actual_stdout"; else printf '<empty>\n'; fi
        printf 'stderr:\n'
        if [ -s "$actual_stderr" ]; then cat "$actual_stderr"; else printf '<empty>\n'; fi
        printf 'exit code: %s\n' "$actual_exit"
    fi
}

cat > "$tmp/expected-default" <<'EXPECTED'
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
EXPECTED
cat > "$tmp/expected-json-top1" <<'EXPECTED'
{"total_lines":4,"by_level":{"DEBUG":0,"INFO":1,"WARN":0,"ERROR":3},"by_service":{"auth":3,"web":1},"top_errors":[{"message":"timeout","count":2}],"time_range":{"start":"2025-01-01T05:00:00Z","end":"2025-01-03T00:00:00Z"}}
EXPECTED
cat > "$tmp/expected-filtered" <<'EXPECTED'
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
EXPECTED
cat > "$tmp/expected-json-top20" <<'EXPECTED'
{"total_lines":4,"by_level":{"DEBUG":0,"INFO":1,"WARN":0,"ERROR":3},"by_service":{"auth":3,"web":1},"top_errors":[{"message":"timeout","count":2},{"message":"denied","count":1}],"time_range":{"start":"2025-01-01T05:00:00Z","end":"2025-01-03T00:00:00Z"}}
EXPECTED
cat > "$tmp/expected-empty" <<'EXPECTED'
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
EXPECTED
cat > "$tmp/expected-help" <<'EXPECTED'
usage: kvlog [options] [FILE ...]
  -h, --help          Show this help message and exit.
  --json              Emit one compact JSON object instead of the human summary (default: human summary).
  --top N             Show at most N most frequent ERROR messages, ordered by count descending then message ascending (default: 5).
  --since ISO8601     Include records with timestamps at or after this instant (inclusive; default: none).
  --until ISO8601     Include records with timestamps at or before this instant (inclusive; default: none).
With no FILE, read stdin; FILE may be repeated and - selects stdin.
EXPECTED
cat > "$tmp/expected-invalid-json" <<'EXPECTED'
exit=1
stdout=<empty>
kvlog: <stdin>:3: invalid JSON
EXPECTED
cat > "$tmp/expected-missing-msg" <<'EXPECTED'
kvlog: <stdin>:1: missing required key 'msg'
EXPECTED
cat > "$tmp/expected-top-error" <<'EXPECTED'
exit=2
stdout=<empty>
kvlog: error: --top must be a positive integer
EXPECTED
cat > "$tmp/expected-since-error" <<'EXPECTED'
exit=2
stdout=<empty>
kvlog: error: invalid --since timestamp
EXPECTED
cat > "$tmp/expected-until-error" <<'EXPECTED'
exit=2
stdout=<empty>
kvlog: error: invalid --until timestamp
EXPECTED
cat > "$tmp/expected-bounds-error" <<'EXPECTED'
exit=2
stdout=<empty>
kvlog: error: --since must be less than or equal to --until
EXPECTED
cat > "$tmp/expected-readme" <<'EXPECTED'
Requires Python 3.9+; no third-party dependencies.
install -m 755 kvlog.py "$HOME/.local/bin/kvlog"
python3 kvlog.py app.jsonl
cat app.jsonl | python3 kvlog.py --json
python3 kvlog.py --top 3 --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z app.jsonl
With no FILE, kvlog reads stdin; pass - to read stdin alongside files.
JSON fields: total_lines, by_level, by_service, top_errors, and time_range.
Exit codes: 0 success, 1 malformed/input failure, 2 usage error.
python3 -m unittest
EXPECTED
cat > "$tmp/expected-install-json" <<'EXPECTED'
{"total_lines":1,"by_level":{"DEBUG":0,"INFO":0,"WARN":1,"ERROR":0},"by_service":{"api":1},"top_errors":[],"time_range":{"start":"2025-01-01T00:00:00Z","end":"2025-01-01T00:00:00Z"}}
EXPECTED
: > "$tmp/expected-unit-tests"

# 1. Default summary and stdin.
check_item 1 0 "$tmp/expected-default" "$empty" <<'ITEM'
cat "$tmp/sample.jsonl" | python3 kvlog.py
ITEM

# 2. Multiple file inputs.
check_item 2 0 "$tmp/expected-default" "$empty" <<'ITEM'
python3 kvlog.py "$tmp/part1.jsonl" "$tmp/part2.jsonl"
ITEM

# 3. --json and --top 1.
check_item 3 0 "$tmp/expected-json-top1" "$empty" <<'ITEM'
cat "$tmp/sample.jsonl" | python3 kvlog.py --json --top 1
ITEM

# 4. --since and --until, inclusive.
check_item 4 0 "$tmp/expected-filtered" "$empty" <<'ITEM'
python3 kvlog.py --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z "$tmp/sample.jsonl"
ITEM

# 5. --top greater than distinct errors.
check_item 5 0 "$tmp/expected-json-top20" "$empty" <<'ITEM'
python3 kvlog.py --top 20 --json "$tmp/sample.jsonl"
ITEM

# 6. Filters excluding everything.
cat "$tmp/expected-empty" "$tmp/expected-empty" > "$tmp/expected-empty-twice"
check_item 6 0 "$tmp/expected-empty-twice" "$empty" <<'ITEM'
python3 kvlog.py --since 2030-01-01T00:00:00Z "$tmp/sample.jsonl"
python3 kvlog.py --until 2020-01-01T00:00:00Z "$tmp/sample.jsonl"
ITEM

# 7. --help and required option/default/effect lines.
check_item 7 0 "$tmp/expected-help" "$empty" <<'ITEM'
python3 kvlog.py --help > "$tmp/help" 2> "$tmp/err"
test ! -s "$tmp/err"
grep -F 'usage: kvlog [options] [FILE ...]' "$tmp/help"
grep -F -- '-h, --help' "$tmp/help"
grep -F -- '--json' "$tmp/help" | grep -F '(default: human summary)'
grep -F -- '--top N' "$tmp/help" | grep -F '(default: 5)'
grep -F -- '--since ISO8601' "$tmp/help" | grep -F '(inclusive; default: none)'
grep -F -- '--until ISO8601' "$tmp/help" | grep -F '(inclusive; default: none)'
grep -F 'With no FILE, read stdin; FILE may be repeated and - selects stdin.' "$tmp/help"
ITEM

# 8. Malformed JSON, physical line number, and exit 1.
check_item 8 0 "$tmp/expected-invalid-json" "$empty" <<'ITEM'
set +e
printf '%s\n\n%s\n' '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"api","msg":"ok"}' '{"ts":' | python3 kvlog.py > "$tmp/out" 2> "$tmp/err"
rc=$?
set -e
test "$rc" -eq 1 && test ! -s "$tmp/out"
printf 'exit=%s\nstdout=<empty>\n' "$rc"
cat "$tmp/err"
ITEM

# 9. Missing required key and exit 1.
check_item 9 1 "$empty" "$tmp/expected-missing-msg" <<'ITEM'
printf '%s\n' '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"api"}' | python3 kvlog.py
ITEM

# 10. --top 0 usage error and exit 2.
check_item 10 0 "$tmp/expected-top-error" "$empty" <<'ITEM'
set +e
python3 kvlog.py --top 0 "$tmp/sample.jsonl" > "$tmp/out" 2> "$tmp/err"
rc=$?
set -e
test "$rc" -eq 2 && test ! -s "$tmp/out"
printf 'exit=%s\nstdout=<empty>\n' "$rc"
tail -n 1 "$tmp/err"
ITEM

# 11. Invalid --since value and exit 2.
check_item 11 0 "$tmp/expected-since-error" "$empty" <<'ITEM'
set +e
python3 kvlog.py --since not-a-date "$tmp/sample.jsonl" > "$tmp/out" 2> "$tmp/err"
rc=$?
set -e
test "$rc" -eq 2 && test ! -s "$tmp/out"
printf 'exit=%s\nstdout=<empty>\n' "$rc"
tail -n 1 "$tmp/err"
ITEM

# 12. Invalid --until value and exit 2.
check_item 12 0 "$tmp/expected-until-error" "$empty" <<'ITEM'
set +e
python3 kvlog.py --until not-a-date "$tmp/sample.jsonl" > "$tmp/out" 2> "$tmp/err"
rc=$?
set -e
test "$rc" -eq 2 && test ! -s "$tmp/out"
printf 'exit=%s\nstdout=<empty>\n' "$rc"
tail -n 1 "$tmp/err"
ITEM

# 13. Reversed time bounds and exit 2.
check_item 13 0 "$tmp/expected-bounds-error" "$empty" <<'ITEM'
set +e
python3 kvlog.py --since 2025-01-04T00:00:00Z --until 2025-01-03T00:00:00Z "$tmp/sample.jsonl" > "$tmp/out" 2> "$tmp/err"
rc=$?
set -e
test "$rc" -eq 2 && test ! -s "$tmp/out"
printf 'exit=%s\nstdout=<empty>\n' "$rc"
tail -n 1 "$tmp/err"
ITEM

# 14. README installation, usage, test instructions, and documented shape.
check_item 14 0 "$tmp/expected-readme" "$empty" <<'ITEM'
grep -Fx 'Requires Python 3.9+; no third-party dependencies.' README.md
grep -Fx 'install -m 755 kvlog.py "$HOME/.local/bin/kvlog"' README.md
grep -Fx 'python3 kvlog.py app.jsonl' README.md
grep -Fx 'cat app.jsonl | python3 kvlog.py --json' README.md
grep -Fx 'python3 kvlog.py --top 3 --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z app.jsonl' README.md
grep -Fx 'With no FILE, kvlog reads stdin; pass - to read stdin alongside files.' README.md
grep -Fx 'JSON fields: total_lines, by_level, by_service, top_errors, and time_range.' README.md
grep -Fx 'Exit codes: 0 success, 1 malformed/input failure, 2 usage error.' README.md
grep -Fx 'python3 -m unittest' README.md
ITEM

# 15. Install and run the executable without dependencies.
check_item 15 0 "$tmp/expected-install-json" "$empty" <<'ITEM'
mkdir -p "$tmp/bin" && install -m 755 kvlog.py "$tmp/bin/kvlog" && printf '%s\n' '{"ts":"2025-01-01T00:00:00Z","level":"WARN","service":"api","msg":"slow"}' | "$tmp/bin/kvlog" --json
ITEM

# 16. Stop at the first malformed record across input sources.
printf 'exit=1\nstdout=<empty>\nkvlog: %s/second.jsonl:1: invalid JSON\n' "$tmp" > "$tmp/expected-first-error"
check_item 16 0 "$tmp/expected-first-error" "$empty" <<'ITEM'
set +e
python3 kvlog.py "$tmp/first.jsonl" "$tmp/second.jsonl" "$tmp/third.jsonl" > "$tmp/out" 2> "$tmp/err"
rc=$?
set -e
test "$rc" -eq 1 && test ! -s "$tmp/out"
printf 'exit=%s\nstdout=<empty>\n' "$rc"
cat "$tmp/err"
ITEM

# 17. Complete unit suite.
check_item 17 0 "$tmp/expected-unit-tests" "$empty" <<'ITEM'
set +e
python3 -m unittest > "$tmp/tests.out" 2> "$tmp/tests.err"
rc=$?
set -e
test "$rc" -eq 0 && test ! -s "$tmp/tests.out"
grep -E '^Ran (1[5-9]|[2-9][0-9]|[1-9][0-9]{2,}) tests in .+s$' "$tmp/tests.err"
grep -Fx 'OK' "$tmp/tests.err"
! grep -E '^(FAILED|ERROR:)' "$tmp/tests.err"
ITEM

if [ "$failures" -ne 0 ]; then
    exit 1
fi
