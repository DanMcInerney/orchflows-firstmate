import builtins
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kvlog

KVLOG_PATH = Path(__file__).resolve().parent.parent / "kvlog.py"


def _record(ts, level, service, msg):
    return {"ts": kvlog.parse_timestamp(ts), "level": level, "service": service, "msg": msg}


def run_cli(args, input_text=""):
    return subprocess.run(
        [sys.executable, str(KVLOG_PATH), *args],
        input=input_text,
        capture_output=True,
        text=True,
    )


class ReadingTests(unittest.TestCase):
    def test_read_skips_blank_lines_and_ignores_extra_fields(self):
        data = (
            b"\n"
            b'{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"web","msg":"ok","extra":"ignored"}\n'
            b"   \n"
            b'{"ts":"2025-01-01T00:00:01Z","level":"DEBUG","service":"web","msg":"tick"}\n'
        )
        records = list(kvlog.iter_records(io.BytesIO(data), "test"))
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["service"], "web")
        self.assertEqual(records[0]["msg"], "ok")
        self.assertNotIn("extra", records[0])

    def test_read_reports_malformed_json_with_source_line(self):
        data = (
            b'{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"web","msg":"ok"}\n'
            b'{"ts":\n'
        )
        with self.assertRaises(kvlog.InputError) as ctx:
            list(kvlog.iter_records(io.BytesIO(data), "sample.jsonl"))
        self.assertEqual(str(ctx.exception), "sample.jsonl:2: invalid JSON")

    def test_read_rejects_missing_keys_and_invalid_field_types(self):
        cases = [
            (
                '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"web"}',
                "missing required key 'msg'",
            ),
            (
                '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":1,"msg":"ok"}',
                "field 'service' must be a string",
            ),
            (
                '{"ts":"2025-01-01T00:00:00Z","level":"WEIRD","service":"web","msg":"ok"}',
                "unsupported level 'WEIRD'",
            ),
            (
                '{"ts":"not-a-timestamp","level":"INFO","service":"web","msg":"ok"}',
                "invalid timestamp 'not-a-timestamp'",
            ),
            ('["not", "an", "object"]', "expected a JSON object"),
        ]
        for text, expected_message in cases:
            with self.subTest(text=text):
                with self.assertRaises(kvlog.InputError) as ctx:
                    kvlog.parse_record(text, "source", 7)
                self.assertEqual(str(ctx.exception), f"source:7: {expected_message}")

    def test_read_rejects_non_standard_json_constants(self):
        cases = [
            '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"web","msg":"ok","extra":NaN}',
            '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"web","msg":"ok","extra":Infinity}',
            '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"web","msg":"ok","extra":-Infinity}',
        ]
        for text in cases:
            with self.subTest(text=text):
                with self.assertRaises(kvlog.InputError) as ctx:
                    kvlog.parse_record(text, "source", 4)
                self.assertEqual(str(ctx.exception), "source:4: invalid JSON")

    def test_read_rejects_timestamp_that_overflows_utc_conversion(self):
        with self.assertRaises(kvlog.InputError) as ctx:
            kvlog.parse_record(
                '{"ts":"0001-01-01T00:00:00+01:00","level":"INFO","service":"api","msg":"ok"}',
                "source",
                3,
            )
        self.assertEqual(
            str(ctx.exception), "source:3: invalid timestamp '0001-01-01T00:00:00+01:00'"
        )


class TimestampTests(unittest.TestCase):
    def test_parse_timestamp_normalizes_offsets_and_assumes_utc_when_naive(self):
        self.assertEqual(
            kvlog.parse_timestamp("2025-01-01T00:00:00Z"),
            datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            kvlog.parse_timestamp("2025-01-01T00:00:00-05:00"),
            datetime(2025, 1, 1, 5, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            kvlog.parse_timestamp("2025-01-01T00:00:00"),
            datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        )
        with self.assertRaises(ValueError):
            kvlog.parse_timestamp("not-a-date")

    def test_parse_timestamp_rejects_utc_conversion_overflow(self):
        with self.assertRaises(ValueError):
            kvlog.parse_timestamp("0001-01-01T00:00:00+01:00")


class SummarizeTests(unittest.TestCase):
    def test_summarize_applies_inclusive_since_until_filters(self):
        records = [
            _record("2025-01-01T00:00:00Z", "INFO", "web", "a"),
            _record("2025-01-02T00:00:00Z", "ERROR", "auth", "b"),
            _record("2025-01-03T00:00:00Z", "ERROR", "auth", "c"),
        ]
        since = kvlog.parse_timestamp("2025-01-02T00:00:00Z")
        until = kvlog.parse_timestamp("2025-01-03T00:00:00Z")
        summary = kvlog.summarize(records, since=since, until=until)
        self.assertEqual(summary["total_lines"], 2)
        self.assertEqual(summary["by_service"], {"auth": 2})

    def test_summarize_returns_empty_shape_when_filters_exclude_every_record(self):
        records = [_record("2025-01-01T00:00:00Z", "INFO", "web", "a")]
        since = kvlog.parse_timestamp("2030-01-01T00:00:00Z")
        summary = kvlog.summarize(records, since=since)
        self.assertEqual(summary["total_lines"], 0)
        self.assertEqual(
            summary["by_level"], {"DEBUG": 0, "INFO": 0, "WARN": 0, "ERROR": 0}
        )
        self.assertEqual(summary["by_service"], {})
        self.assertEqual(summary["top_errors"], [])
        self.assertEqual(summary["time_range"], {"start": None, "end": None})

    def test_summarize_counts_services_and_levels_after_filtering(self):
        records = [
            _record("2025-01-01T00:00:00Z", "INFO", "web", "a"),
            _record("2025-01-01T00:00:01Z", "DEBUG", "web", "b"),
            _record("2025-01-01T00:00:02Z", "ERROR", "auth", "c"),
            _record("2025-01-01T00:00:03Z", "WARN", "auth", "d"),
        ]
        summary = kvlog.summarize(records)
        self.assertEqual(summary["total_lines"], 4)
        self.assertEqual(
            summary["by_level"], {"DEBUG": 1, "INFO": 1, "WARN": 1, "ERROR": 1}
        )
        self.assertEqual(summary["by_service"], {"auth": 2, "web": 2})

    def test_summarize_sorts_error_frequency_then_message_and_caps_top(self):
        records = [
            _record("2025-01-01T00:00:00Z", "ERROR", "svc", "timeout"),
            _record("2025-01-01T00:00:01Z", "ERROR", "svc", "timeout"),
            _record("2025-01-01T00:00:02Z", "ERROR", "svc", "denied"),
            _record("2025-01-01T00:00:03Z", "ERROR", "svc", "aborted"),
            _record("2025-01-01T00:00:04Z", "ERROR", "svc", "aborted"),
        ]
        summary = kvlog.summarize(records, top=2)
        self.assertEqual(
            summary["top_errors"],
            [{"message": "aborted", "count": 2}, {"message": "timeout", "count": 2}],
        )

    def test_summarize_formats_extreme_year_with_four_digit_padding(self):
        record = _record("0001-01-01T00:00:00Z", "INFO", "api", "ok")
        summary = kvlog.summarize([record])
        self.assertEqual(summary["time_range"]["start"], "0001-01-01T00:00:00Z")
        self.assertEqual(summary["time_range"]["end"], "0001-01-01T00:00:00Z")


class RenderTests(unittest.TestCase):
    def test_render_text_has_stable_human_format_for_data_and_empty_summary(self):
        summary = {
            "total_lines": 1,
            "by_level": {"DEBUG": 0, "INFO": 1, "WARN": 0, "ERROR": 0},
            "by_service": {"web": 1},
            "top_errors": [],
            "time_range": {
                "start": "2025-01-01T00:00:00Z",
                "end": "2025-01-01T00:00:00Z",
            },
        }
        expected = (
            "Total lines: 1\n"
            "Counts by level:\n"
            "  DEBUG: 0\n"
            "  INFO: 1\n"
            "  WARN: 0\n"
            "  ERROR: 0\n"
            "Counts by service:\n"
            '  "web": 1\n'
            "Top 5 ERROR messages:\n"
            "  (none)\n"
            "Time range: 2025-01-01T00:00:00Z .. 2025-01-01T00:00:00Z\n"
        )
        self.assertEqual(kvlog.render_text(summary, top=5), expected)

        empty_summary = {
            "total_lines": 0,
            "by_level": {"DEBUG": 0, "INFO": 0, "WARN": 0, "ERROR": 0},
            "by_service": {},
            "top_errors": [],
            "time_range": {"start": None, "end": None},
        }
        expected_empty = (
            "Total lines: 0\n"
            "Counts by level:\n"
            "  DEBUG: 0\n"
            "  INFO: 0\n"
            "  WARN: 0\n"
            "  ERROR: 0\n"
            "Counts by service:\n"
            "  (none)\n"
            "Top 5 ERROR messages:\n"
            "  (none)\n"
            "Time range: none\n"
        )
        self.assertEqual(kvlog.render_text(empty_summary, top=5), expected_empty)

    def test_render_json_has_documented_shape_and_normalized_time_range(self):
        summary = {
            "total_lines": 2,
            "by_level": {"DEBUG": 0, "INFO": 1, "WARN": 0, "ERROR": 1},
            "by_service": {"auth": 1, "web": 1},
            "top_errors": [{"message": "timeout", "count": 1}],
            "time_range": {
                "start": "2025-01-01T00:00:00Z",
                "end": "2025-01-02T00:00:00Z",
            },
        }
        text = kvlog.render_json(summary)
        self.assertEqual(
            text,
            '{"total_lines":2,"by_level":{"DEBUG":0,"INFO":1,"WARN":0,"ERROR":1},'
            '"by_service":{"auth":1,"web":1},"top_errors":[{"message":"timeout","count":1}],'
            '"time_range":{"start":"2025-01-01T00:00:00Z","end":"2025-01-02T00:00:00Z"}}',
        )
        self.assertEqual(
            list(json.loads(text).keys()),
            ["total_lines", "by_level", "by_service", "top_errors", "time_range"],
        )


class CliTests(unittest.TestCase):
    def test_cli_reads_stdin_and_multiple_files(self):
        line = '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"web","msg":"ok"}\n'
        result = run_cli([], input_text=line)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total lines: 1", result.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            path_a = os.path.join(tmp, "a.jsonl")
            path_b = os.path.join(tmp, "b.jsonl")
            with open(path_a, "w") as handle:
                handle.write(
                    '{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"web","msg":"ok"}\n'
                )
            with open(path_b, "w") as handle:
                handle.write(
                    '{"ts":"2025-01-02T00:00:00Z","level":"ERROR","service":"auth","msg":"boom"}\n'
                )
            result = run_cli(
                [path_a, "-", path_b],
                input_text='{"ts":"2025-01-01T12:00:00Z","level":"WARN","service":"web","msg":"slow"}\n',
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            self.assertIn("Total lines: 3", result.stdout)

    def test_cli_read_error_during_iteration_reports_cannot_read_input(self):
        class FailingStream:
            def __iter__(self):
                return self

            def __next__(self):
                raise OSError("simulated read failure")

            def close(self):
                pass

        real_open = builtins.open

        def fake_open(path, mode="r", *args, **kwargs):
            if path == "simulated.jsonl":
                return FailingStream()
            return real_open(path, mode, *args, **kwargs)

        stdout = io.StringIO()
        stderr = io.StringIO()
        builtins.open = fake_open
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                returncode = kvlog.main(["simulated.jsonl"])
        finally:
            builtins.open = real_open

        self.assertEqual(returncode, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(
            stderr.getvalue().strip(),
            "kvlog: simulated.jsonl: cannot read input: simulated read failure",
        )

    def test_cli_malformed_input_returns_one_without_stdout(self):
        result = run_cli([], input_text='{"ts":\n')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr.strip(), "kvlog: <stdin>:1: invalid JSON")

    def test_cli_missing_required_key_reports_line_and_returns_one(self):
        result = run_cli(
            [], input_text='{"ts":"2025-01-01T00:00:00Z","level":"INFO","service":"api"}\n'
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(
            result.stderr.strip(), "kvlog: <stdin>:1: missing required key 'msg'"
        )

    def test_cli_invalid_top_and_invalid_bounds_return_two(self):
        cases = [
            (["--top", "0"], "kvlog: error: --top must be a positive integer"),
            (["--since", "not-a-date"], "kvlog: error: invalid --since timestamp"),
            (["--until", "not-a-date"], "kvlog: error: invalid --until timestamp"),
            (
                ["--since", "2025-01-04T00:00:00Z", "--until", "2025-01-03T00:00:00Z"],
                "kvlog: error: --since must be less than or equal to --until",
            ),
            (["-", "-"], "kvlog: error: '-' may only be given once"),
        ]
        for args, expected_last_line in cases:
            with self.subTest(args=args):
                result = run_cli(args, input_text="")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                if expected_last_line is not None:
                    self.assertEqual(
                        result.stderr.strip().splitlines()[-1], expected_last_line
                    )

    def test_cli_help_documents_options_defaults_and_effects(self):
        result = run_cli(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("usage: kvlog [options] [FILE ...]", result.stdout)
        self.assertIn("-h, --help", result.stdout)
        self.assertIn("--json", result.stdout)
        self.assertIn("(default: human summary)", result.stdout)
        self.assertIn("--top N", result.stdout)
        self.assertIn("(default: 5)", result.stdout)
        self.assertIn("--since ISO8601", result.stdout)
        self.assertIn("--until ISO8601", result.stdout)
        self.assertIn("(inclusive; default: none)", result.stdout)
        self.assertIn(
            "With no FILE, read stdin; FILE may be repeated and - selects stdin.",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
