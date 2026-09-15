#!/usr/bin/env python3
"""Summarize structured JSON-lines logs."""

import argparse
import json
import sys
from datetime import datetime, timezone

VALID_LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")
REQUIRED_FIELDS = ("ts", "level", "service", "msg")
STDIN_SOURCE = "<stdin>"

HELP_TEXT = """usage: kvlog [options] [FILE ...]

kvlog summarizes structured JSON-lines logs read from files or stdin.

Options:
  -h, --help          Show this help message and exit.
  --json              Emit one compact JSON object instead of the human summary (default: human summary).
  --top N             Show at most N most frequent ERROR messages, ordered by count descending then message ascending (default: 5).
  --since ISO8601     Include records with timestamps at or after this instant (inclusive; default: none).
  --until ISO8601     Include records with timestamps at or before this instant (inclusive; default: none).

With no FILE, read stdin; FILE may be repeated and - selects stdin.
"""


class InputError(Exception):
    """Raised for malformed records or unreadable input; maps to exit 1."""


def parse_timestamp(value):
    if not isinstance(value, str) or not value:
        raise ValueError(f"invalid timestamp {value!r}")
    text = value
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        raise ValueError(f"invalid timestamp {value!r}") from None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        try:
            parsed = parsed.astimezone(timezone.utc)
        except OverflowError:
            raise ValueError(f"invalid timestamp {value!r}") from None
    return parsed


def _reject_non_standard_constant(token):
    raise ValueError(f"non-standard JSON constant {token!r}")


def parse_record(text, source, line_number):
    try:
        obj = json.loads(text, parse_constant=_reject_non_standard_constant)
    except (json.JSONDecodeError, ValueError):
        raise InputError(f"{source}:{line_number}: invalid JSON") from None
    if not isinstance(obj, dict):
        raise InputError(f"{source}:{line_number}: expected a JSON object")
    for key in REQUIRED_FIELDS:
        if key not in obj:
            raise InputError(
                f"{source}:{line_number}: missing required key '{key}'"
            )
        if not isinstance(obj[key], str):
            raise InputError(
                f"{source}:{line_number}: field '{key}' must be a string"
            )
    level = obj["level"]
    if level not in VALID_LEVELS:
        raise InputError(
            f"{source}:{line_number}: unsupported level '{level}'"
        )
    try:
        ts = parse_timestamp(obj["ts"])
    except ValueError:
        raise InputError(
            f"{source}:{line_number}: invalid timestamp '{obj['ts']}'"
        ) from None
    return {"ts": ts, "level": level, "service": obj["service"], "msg": obj["msg"]}


def iter_records(stream, source):
    line_number = 0
    for raw_line in stream:
        line_number += 1
        try:
            text = raw_line.decode("utf-8")
        except UnicodeDecodeError:
            raise InputError(
                f"{source}:{line_number}: input is not valid UTF-8"
            ) from None
        if not text.strip():
            continue
        yield parse_record(text, source, line_number)


def _read_all(files):
    for filename in files:
        close = False
        if filename == "-":
            source = STDIN_SOURCE
            stream = sys.stdin.buffer
        else:
            source = filename
            try:
                stream = open(filename, "rb")
            except OSError as exc:
                reason = exc.strerror or str(exc)
                raise InputError(f"{source}: cannot read input: {reason}") from None
            close = True
        try:
            yield from iter_records(stream, source)
        except OSError as exc:
            reason = exc.strerror or str(exc)
            raise InputError(f"{source}: cannot read input: {reason}") from None
        finally:
            if close:
                stream.close()


def _format_timestamp(value):
    utc_value = value.astimezone(timezone.utc).replace(microsecond=0, tzinfo=None)
    return f"{utc_value.isoformat()}Z"


def summarize(records, since=None, until=None, top=5):
    total = 0
    level_counts = {level: 0 for level in VALID_LEVELS}
    service_counts = {}
    error_counts = {}
    start = None
    end = None

    for record in records:
        ts = record["ts"]
        if since is not None and ts < since:
            continue
        if until is not None and ts > until:
            continue
        total += 1
        level_counts[record["level"]] += 1
        service = record["service"]
        service_counts[service] = service_counts.get(service, 0) + 1
        if record["level"] == "ERROR":
            msg = record["msg"]
            error_counts[msg] = error_counts.get(msg, 0) + 1
        if start is None or ts < start:
            start = ts
        if end is None or ts > end:
            end = ts

    ranked_errors = sorted(error_counts.items(), key=lambda item: (-item[1], item[0]))
    top_errors = [
        {"message": message, "count": count}
        for message, count in ranked_errors[:top]
    ]

    return {
        "total_lines": total,
        "by_level": {level: level_counts[level] for level in VALID_LEVELS},
        "by_service": dict(sorted(service_counts.items())),
        "top_errors": top_errors,
        "time_range": {
            "start": _format_timestamp(start) if start is not None else None,
            "end": _format_timestamp(end) if end is not None else None,
        },
    }


def render_text(summary, top):
    lines = [f"Total lines: {summary['total_lines']}", "Counts by level:"]
    for level in VALID_LEVELS:
        lines.append(f"  {level}: {summary['by_level'][level]}")

    lines.append("Counts by service:")
    if summary["by_service"]:
        for service, count in summary["by_service"].items():
            lines.append(f"  {json.dumps(service)}: {count}")
    else:
        lines.append("  (none)")

    lines.append(f"Top {top} ERROR messages:")
    if summary["top_errors"]:
        for entry in summary["top_errors"]:
            lines.append(f"  {entry['count']}: {json.dumps(entry['message'])}")
    else:
        lines.append("  (none)")

    start = summary["time_range"]["start"]
    end = summary["time_range"]["end"]
    if start is None or end is None:
        lines.append("Time range: none")
    else:
        lines.append(f"Time range: {start} .. {end}")

    return "\n".join(lines) + "\n"


def render_json(summary):
    return json.dumps(summary, separators=(",", ":"))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="kvlog",
        usage="kvlog [options] [FILE ...]",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--since", default=None)
    parser.add_argument("--until", default=None)
    parser.add_argument("files", nargs="*")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.help:
        sys.stdout.write(HELP_TEXT)
        return 0

    if args.top <= 0:
        parser.error("--top must be a positive integer")

    since = None
    until = None
    if args.since is not None:
        try:
            since = parse_timestamp(args.since)
        except ValueError:
            parser.error("invalid --since timestamp")
    if args.until is not None:
        try:
            until = parse_timestamp(args.until)
        except ValueError:
            parser.error("invalid --until timestamp")
    if since is not None and until is not None and since > until:
        parser.error("--since must be less than or equal to --until")

    files = args.files or ["-"]
    if files.count("-") > 1:
        parser.error("'-' may only be given once")

    try:
        summary = summarize(_read_all(files), since=since, until=until, top=args.top)
    except InputError as exc:
        print(f"kvlog: {exc}", file=sys.stderr)
        return 1

    if args.json:
        sys.stdout.write(render_json(summary) + "\n")
    else:
        sys.stdout.write(render_text(summary, args.top))

    return 0


if __name__ == "__main__":
    sys.exit(main())
