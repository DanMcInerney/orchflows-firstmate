# kvlog

kvlog summarizes structured JSON-lines logs, counting records by level and service, ranking frequent `ERROR` messages, and reporting the covered timestamp range. It reads one or more UTF-8 files or standard input, applies inclusive time filters, and emits either a human-readable summary or compact JSON.

## Requirements and installation

Requires Python 3.9+; no third-party dependencies.

From the repository root, install the executable in `~/.local/bin`:

```sh
mkdir -p "$HOME/.local/bin"
install -m 755 kvlog.py "$HOME/.local/bin/kvlog"
```

Make sure `~/.local/bin` is on your `PATH` to run it as `kvlog`. You can also run it from this checkout with `python3 kvlog.py`.

## Usage

Each input line must be a JSON object with string fields `ts`, `level`, `service`, and `msg`. Timestamps are ISO 8601; timestamps without an offset are treated as UTC, and output times are normalized to UTC. Other fields are accepted and ignored. Blank lines are skipped.

The sample log is [`examples/app.jsonl`](examples/app.jsonl). From the repository root, run:

```sh
python3 kvlog.py examples/app.jsonl
```

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

Pipe input to get compact JSON:

```sh
cat examples/app.jsonl | python3 kvlog.py --json
```

```json
{"total_lines":4,"by_level":{"DEBUG":0,"INFO":1,"WARN":0,"ERROR":3},"by_service":{"auth":3,"web":1},"top_errors":[{"message":"timeout","count":2},{"message":"denied","count":1}],"time_range":{"start":"2025-01-01T05:00:00Z","end":"2025-01-03T00:00:00Z"}}
```

Apply inclusive time bounds and show at most three error messages:

```sh
python3 kvlog.py --top 3 --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z examples/app.jsonl
```

```text
Total lines: 3
Counts by level:
  DEBUG: 0
  INFO: 0
  WARN: 0
  ERROR: 3
Counts by service:
  "auth": 3
Top 3 ERROR messages:
  2: "timeout"
  1: "denied"
Time range: 2025-01-02T00:00:00Z .. 2025-01-03T00:00:00Z
```

<details>
<summary>Running the same examples with a bare <code>app.jsonl</code> filename</summary>

If you want to use the short filename shown in these commands, copy the script and sample
into a temporary directory. Run this setup and the commands in the same shell session from
the repository root:

```sh
demo_dir="$(mktemp -d)"
cp kvlog.py "$demo_dir/kvlog.py"
cp examples/app.jsonl "$demo_dir/app.jsonl"
(
cd "$demo_dir"
python3 kvlog.py app.jsonl
)
```

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

```sh
(
cd "$demo_dir"
cat app.jsonl | python3 kvlog.py --json
)
```

```json
{"total_lines":4,"by_level":{"DEBUG":0,"INFO":1,"WARN":0,"ERROR":3},"by_service":{"auth":3,"web":1},"top_errors":[{"message":"timeout","count":2},{"message":"denied","count":1}],"time_range":{"start":"2025-01-01T05:00:00Z","end":"2025-01-03T00:00:00Z"}}
```

```sh
(
cd "$demo_dir"
python3 kvlog.py --top 3 --since 2025-01-02T00:00:00Z --until 2025-01-03T00:00:00Z app.jsonl
)
```

```text
Total lines: 3
Counts by level:
  DEBUG: 0
  INFO: 0
  WARN: 0
  ERROR: 3
Counts by service:
  "auth": 3
Top 3 ERROR messages:
  2: "timeout"
  1: "denied"
Time range: 2025-01-02T00:00:00Z .. 2025-01-03T00:00:00Z
```

</details>

## Options

| Option | Default | Effect |
| --- | --- | --- |
| `-h`, `--help` | Not applicable | Print help, including all options, and exit successfully. |
| `--json` | Human summary | Emit one compact JSON object and a newline instead of the human-readable summary. |
| `--top N` | `5` | Include at most N distinct `ERROR` messages, ordered by count descending and then message ascending. N must be a positive integer. |
| `--since ISO8601` | None | Include records at or after this timestamp. The bound is inclusive. |
| `--until ISO8601` | None | Include records at or before this timestamp. The bound is inclusive. |
| `FILE ...` | Standard input | Read one or more UTF-8 JSON-lines files in argument order. |
| `-` | Not used | Read standard input at this position among files; it may appear at most once. |

With no FILE, kvlog reads stdin; pass - to read stdin alongside files.

Records are fully validated before filtering, so malformed input is reported even when its timestamp falls outside the selected range. `total_lines` and every count include only valid, nonblank records that remain after filtering. A valid input with no matching records succeeds with zero counts, empty service and error collections, and a `null` start and end time in JSON.

## JSON output

JSON fields: total_lines, by_level, by_service, top_errors, and time_range.

- `total_lines` is the number of matching records.
- `by_level` always contains `DEBUG`, `INFO`, `WARN`, and `ERROR` counts.
- `by_service` maps each service in the matching records to its count; keys are sorted lexically.
- `top_errors` is an array of objects with `message` and `count` fields, sorted by frequency and then message.
- `time_range` contains `start` and `end` timestamps in UTC ISO 8601 form with `Z`; both are `null` when no records match.

Use the field names rather than relying on JSON object key order.

## Exit codes

Exit codes: 0 success, 1 malformed/input failure, 2 usage error.

Malformed JSON, invalid or missing required fields, invalid record timestamps, unreadable files, and invalid UTF-8 input return 1. Invalid options, a non-positive `--top`, invalid filter timestamps, reversed time bounds, and repeated `-` inputs return 2. Errors go to standard error; standard output contains only help or a completed summary.

## Tests

Run the unit suite from the repository root:

```sh
python3 -m unittest
```
