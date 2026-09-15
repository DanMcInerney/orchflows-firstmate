import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import tally  # noqa: E402  (path must be adjusted before this import)

TALLY_PATH = REPO_ROOT / "tally.py"


def run_cli(args, stdin_text=None):
    """Run the tally CLI as a subprocess and return the completed process."""
    return subprocess.run(
        [sys.executable, str(TALLY_PATH), *args],
        input=stdin_text,
        capture_output=True,
        text=True,
    )


class TestTokenize(unittest.TestCase):
    def test_splits_on_whitespace_and_punctuation(self):
        self.assertEqual(tally.tokenize("the cat, the hat!"), ["the", "cat", "the", "hat"])

    def test_keeps_internal_apostrophes(self):
        self.assertEqual(tally.tokenize("don't stop O'Brien's car"), ["don't", "stop", "O'Brien's", "car"])

    def test_strips_surrounding_quotes(self):
        self.assertEqual(tally.tokenize("'hello' \"world\""), ["hello", "world"])

    def test_splits_on_hyphens(self):
        self.assertEqual(tally.tokenize("well-known fact"), ["well", "known", "fact"])

    def test_empty_text_has_no_words(self):
        self.assertEqual(tally.tokenize(""), [])


class TestTopN(unittest.TestCase):
    def test_orders_by_count_descending(self):
        counts = {"a": 1, "b": 3, "c": 2}
        self.assertEqual(tally.top_n(counts, 10), [("b", 3), ("c", 2), ("a", 1)])

    def test_ties_broken_alphabetically(self):
        counts = {"zebra": 2, "apple": 2, "mango": 2}
        self.assertEqual(
            tally.top_n(counts, 10),
            [("apple", 2), ("mango", 2), ("zebra", 2)],
        )

    def test_limits_to_n(self):
        counts = {"a": 3, "b": 2, "c": 1}
        self.assertEqual(tally.top_n(counts, 2), [("a", 3), ("b", 2)])


class TestCliCounting(unittest.TestCase):
    def test_counts_single_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.txt"
            path.write_text("the quick fox the lazy fox the dog\n")

            result = run_cli([str(path)])

            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                result.stdout,
                "the\t3\nfox\t2\ndog\t1\nlazy\t1\nquick\t1\n",
            )

    def test_reads_stdin_when_no_files_given(self):
        result = run_cli([], stdin_text="one two two three three three\n")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "three\t3\ntwo\t2\none\t1\n")

    def test_combines_multiple_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            path_a = Path(tmp) / "a.txt"
            path_b = Path(tmp) / "b.txt"
            path_a.write_text("apple banana\n")
            path_b.write_text("apple apple\n")

            result = run_cli([str(path_a), str(path_b)])

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "apple\t3\nbanana\t1\n")

    def test_top_limits_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.txt"
            path.write_text("a b c d e\n")

            result = run_cli(["--top", "2", str(path)])

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "a\t1\nb\t1\n")

    def test_ignore_case_merges_words(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.txt"
            path.write_text("Cat cat CAT dog\n")

            result = run_cli(["--ignore-case", str(path)])

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "cat\t3\ndog\t1\n")

    def test_without_ignore_case_keeps_case_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.txt"
            path.write_text("Cat cat CAT dog\n")

            result = run_cli([str(path)])

            self.assertEqual(result.returncode, 0)
            lines = result.stdout.strip().split("\n")
            self.assertIn("Cat\t1", lines)
            self.assertIn("cat\t1", lines)
            self.assertIn("CAT\t1", lines)
            self.assertIn("dog\t1", lines)


class TestCliJson(unittest.TestCase):
    def test_json_output_parses_and_matches_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.txt"
            path.write_text("x x y\n")

            result = run_cli(["--json", str(path)])

            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertEqual(data, [{"word": "x", "count": 2}, {"word": "y", "count": 1}])

    def test_json_output_empty_input_is_empty_array(self):
        result = run_cli(["--json"], stdin_text="")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), [])


class TestCliUsage(unittest.TestCase):
    def test_help_exits_zero(self):
        result = run_cli(["--help"])

        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())

    def test_unknown_option_exits_two(self):
        result = run_cli(["--not-a-real-option"])

        self.assertEqual(result.returncode, 2)
        self.assertNotEqual(result.stderr, "")

    def test_top_zero_exits_two(self):
        result = run_cli(["--top", "0"], stdin_text="a b c\n")

        self.assertEqual(result.returncode, 2)

    def test_top_negative_exits_two(self):
        result = run_cli(["--top", "-1"], stdin_text="a b c\n")

        self.assertEqual(result.returncode, 2)

    def test_top_non_integer_exits_two(self):
        result = run_cli(["--top", "abc"], stdin_text="a b c\n")

        self.assertEqual(result.returncode, 2)


class TestCliFileErrors(unittest.TestCase):
    def test_missing_file_reports_error_and_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist.txt"

            result = run_cli([str(missing)])

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn(str(missing), result.stderr)

    def test_invalid_utf8_file_reports_error_and_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.txt"
            path.write_bytes(b"not \xffvalid utf-8\n")

            result = run_cli([str(path)])

            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn(str(path), result.stderr)
            self.assertIn("UTF-8", result.stderr)

    def test_invalid_utf8_stdin_reports_error_and_exits_one(self):
        result = subprocess.run(
            [sys.executable, str(TALLY_PATH)],
            input=b"bad \xff bytes\n",
            capture_output=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"UTF-8", result.stderr)


if __name__ == "__main__":
    unittest.main()
