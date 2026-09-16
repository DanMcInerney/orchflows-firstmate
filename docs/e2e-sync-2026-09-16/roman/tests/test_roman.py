"""Unit tests for roman.py. Run with `python3 -m unittest` from the repository root."""

import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import roman

ROMAN_SCRIPT = Path(__file__).resolve().parent.parent / "roman.py"


class IntToRomanTests(unittest.TestCase):
    def test_known_values(self):
        cases = {
            1: "I",
            4: "IV",
            9: "IX",
            14: "XIV",
            40: "XL",
            90: "XC",
            400: "CD",
            900: "CM",
            1994: "MCMXCIV",
            2026: "MMXXVI",
            3999: "MMMCMXCIX",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(roman.int_to_roman(value), expected)

    def test_rejects_zero(self):
        with self.assertRaises(ValueError):
            roman.int_to_roman(0)

    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            roman.int_to_roman(-5)

    def test_rejects_above_range(self):
        with self.assertRaises(ValueError):
            roman.int_to_roman(4000)

    def test_accepts_range_bounds(self):
        self.assertEqual(roman.int_to_roman(1), "I")
        self.assertEqual(roman.int_to_roman(3999), "MMMCMXCIX")


class RomanToIntTests(unittest.TestCase):
    def test_known_values(self):
        cases = {
            "I": 1,
            "IV": 4,
            "IX": 9,
            "XIV": 14,
            "XL": 40,
            "XC": 90,
            "CD": 400,
            "CM": 900,
            "MCMXCIV": 1994,
            "MMXXVI": 2026,
            "MMMCMXCIX": 3999,
        }
        for numeral, expected in cases.items():
            with self.subTest(numeral=numeral):
                self.assertEqual(roman.roman_to_int(numeral), expected)

    def test_rejects_lowercase_and_mixed_case(self):
        for numeral in ("mcmxciv", "McMxCiV", "iv"):
            with self.subTest(numeral=numeral):
                with self.assertRaises(ValueError):
                    roman.roman_to_int(numeral)

    def test_rejects_non_canonical_forms(self):
        for numeral in ("IIII", "VX", "IC", "MMMM", "XCIC", "VV"):
            with self.subTest(numeral=numeral):
                with self.assertRaises(ValueError):
                    roman.roman_to_int(numeral)

    def test_rejects_empty_and_garbage(self):
        for text in ("", "ABCD", "12IV"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    roman.roman_to_int(text)


class RoundTripTests(unittest.TestCase):
    def test_round_trip_full_range(self):
        for value in range(roman.MIN_VALUE, roman.MAX_VALUE + 1):
            with self.subTest(value=value):
                numeral = roman.int_to_roman(value)
                self.assertEqual(roman.roman_to_int(numeral), value)


class MainFunctionTests(unittest.TestCase):
    def _run_main(self, argv, stdin_text=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        original_stdin = sys.stdin
        if stdin_text is not None:
            sys.stdin = io.StringIO(stdin_text)
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = roman.main(argv)
        finally:
            sys.stdin = original_stdin
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_int_to_roman_argument(self):
        code, out, err = self._run_main(["1994"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "MCMXCIV\n")
        self.assertEqual(err, "")

    def test_roman_to_int_argument(self):
        code, out, err = self._run_main(["MCMXCIV"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "1994\n")
        self.assertEqual(err, "")

    def test_multiple_arguments_in_order(self):
        code, out, err = self._run_main(["9", "MCMXCIV", "XIV"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "IX\n1994\n14\n")

    def test_reads_stdin_when_no_arguments(self):
        code, out, err = self._run_main([], stdin_text="9\n1994\nMCMXCIV\n")
        self.assertEqual(code, 0)
        self.assertEqual(out, "IX\nMCMXCIV\n1994\n")

    def test_invalid_values_exit_1_with_stderr_message(self):
        for value in ("0", "4000", "-5", "IIII", "VX", "IC", "MMMM"):
            with self.subTest(value=value):
                code, out, err = self._run_main([value])
                self.assertEqual(code, 1)
                self.assertEqual(out, "")
                self.assertIn(value, err)

    def test_mixed_valid_and_invalid_values(self):
        code, out, err = self._run_main(["1994", "IIII", "14"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "MCMXCIV\nXIV\n")
        self.assertNotEqual(err, "")

    def test_unknown_option_exits_2(self):
        with self.assertRaises(SystemExit) as ctx:
            self._run_main(["--bogus"])
        self.assertEqual(ctx.exception.code, 2)

    def test_lower_flag_prints_lowercase_numeral(self):
        code, out, err = self._run_main(["--lower", "1994"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "mcmxciv\n")
        self.assertEqual(err, "")

    def test_lower_flag_accepts_lowercase_numeral_input(self):
        code, out, err = self._run_main(["--lower", "mcmxciv"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "1994\n")
        self.assertEqual(err, "")

    def test_lowercase_numeral_rejected_without_lower_flag(self):
        code, out, err = self._run_main(["mcmxciv"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("mcmxciv", err)

    def test_json_flag_valid_value(self):
        code, out, err = self._run_main(["--json", "1994"])
        self.assertEqual(code, 0)
        self.assertEqual(
            out, '{"input": "1994", "output": "MCMXCIV", "ok": true}\n'
        )
        self.assertEqual(err, "")

    def test_json_flag_invalid_value(self):
        code, out, err = self._run_main(["--json", "IIII"])
        self.assertEqual(code, 1)
        self.assertEqual(
            out,
            '{"input": "IIII", "output": "\'IIII\' is not a canonical '
            'Roman numeral", "ok": false}\n',
        )
        self.assertEqual(err, "")

    def test_json_flag_mixed_values_in_order(self):
        code, out, err = self._run_main(["--json", "1994", "IIII", "14"])
        self.assertEqual(code, 1)
        self.assertEqual(
            out,
            '{"input": "1994", "output": "MCMXCIV", "ok": true}\n'
            '{"input": "IIII", "output": "\'IIII\' is not a canonical '
            'Roman numeral", "ok": false}\n'
            '{"input": "14", "output": "XIV", "ok": true}\n',
        )
        self.assertEqual(err, "")

    def test_json_flag_reads_stdin(self):
        code, out, err = self._run_main(
            ["--json"], stdin_text="9\nIIII\n1994\n"
        )
        self.assertEqual(code, 1)
        self.assertEqual(
            out,
            '{"input": "9", "output": "IX", "ok": true}\n'
            '{"input": "IIII", "output": "\'IIII\' is not a canonical '
            'Roman numeral", "ok": false}\n'
            '{"input": "1994", "output": "MCMXCIV", "ok": true}\n',
        )
        self.assertEqual(err, "")

    def test_json_flag_composes_with_lower(self):
        code, out, err = self._run_main(["--json", "--lower", "1994", "IIII"])
        self.assertEqual(code, 1)
        self.assertEqual(
            out,
            '{"input": "1994", "output": "mcmxciv", "ok": true}\n'
            '{"input": "IIII", "output": "\'IIII\' is not a canonical '
            'Roman numeral", "ok": false}\n',
        )
        self.assertEqual(err, "")

    def test_json_flag_output_is_parseable_json_lines(self):
        code, out, err = self._run_main(["--json", "1994", "IIII"])
        lines = out.splitlines()
        self.assertEqual(len(lines), 2)
        first, second = (json.loads(line) for line in lines)
        self.assertEqual(first, {"input": "1994", "output": "MCMXCIV", "ok": True})
        self.assertEqual(set(first.keys()), {"input", "output", "ok"})
        self.assertFalse(second["ok"])


class CommandLineTests(unittest.TestCase):
    """End-to-end checks that invoke the script as a real subprocess."""

    def _run(self, args, stdin_text=None):
        return subprocess.run(
            [sys.executable, str(ROMAN_SCRIPT), *args],
            input=stdin_text,
            capture_output=True,
            text=True,
        )

    def test_int_to_roman(self):
        result = self._run(["1994"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "MCMXCIV\n")

    def test_roman_to_int(self):
        result = self._run(["MCMXCIV"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "1994\n")

    def test_stdin_one_value_per_line(self):
        result = self._run([], stdin_text="9\n1994\n")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "IX\nMCMXCIV\n")

    def test_invalid_value_exit_1(self):
        result = self._run(["IIII"])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("IIII", result.stderr)

    def test_lowercase_numeral_rejected(self):
        result = self._run(["mcmxciv"])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("mcmxciv", result.stderr)
        self.assertIn("not a canonical Roman numeral", result.stderr)

    def test_lower_flag_prints_lowercase_numeral(self):
        result = self._run(["--lower", "1994"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "mcmxciv\n")

    def test_lower_flag_accepts_lowercase_numeral_input(self):
        result = self._run(["--lower", "mcmxciv"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "1994\n")

    def test_help_exits_0(self):
        result = self._run(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())

    def test_unknown_option_exits_2(self):
        result = self._run(["--bogus"])
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_json_flag_mixed_values(self):
        result = self._run(["--json", "1994", "IIII"])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout,
            '{"input": "1994", "output": "MCMXCIV", "ok": true}\n'
            '{"input": "IIII", "output": "\'IIII\' is not a canonical '
            'Roman numeral", "ok": false}\n',
        )
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
