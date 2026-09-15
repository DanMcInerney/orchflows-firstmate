"""tally: count word frequencies in text files or standard input.

Word definition: a word is a maximal run of ASCII letters and digits,
optionally joined by internal apostrophes (so "don't" and "O'Brien" are
each a single word, while surrounding quotes are not part of the word
and hyphens split words: "well-known" -> "well", "known"). All other
characters are treated as separators.

Ordering: results are ranked by count descending; words with equal
counts are ordered alphabetically ascending so output is deterministic.

Input is expected to be UTF-8 encoded, whether from files or standard
input; a decode failure is reported the same way as a missing or
unreadable file (see main()).
"""

import argparse
import json
import re
import sys
from collections import Counter

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)*")


def tokenize(text):
    """Split text into words per the module's word definition."""
    return _WORD_RE.findall(text)


def top_n(counts, n):
    """Return the n most frequent (word, count) pairs.

    Ties are broken alphabetically by word so the result is deterministic.
    """
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:n]


class InputError(Exception):
    """Raised when an input source cannot be read or is not valid UTF-8."""


def _read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise InputError(f"cannot read '{path}': {exc.strerror}") from exc
    except UnicodeDecodeError as exc:
        raise InputError(f"cannot read '{path}': not valid UTF-8 ({exc.reason})") from exc


def _read_stdin():
    try:
        return sys.stdin.buffer.read().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InputError(f"cannot read <stdin>: not valid UTF-8 ({exc.reason})") from exc


def read_input(paths):
    """Return the concatenated text of the given files, or stdin if empty.

    Input is expected to be UTF-8 encoded; a decode failure is raised as
    an InputError alongside missing/unreadable files.
    """
    if not paths:
        return _read_stdin()
    return "\n".join(_read_file(path) for path in paths)


def format_text(ranked):
    """Render ranked (word, count) pairs as "word<TAB>count" lines."""
    lines = [f"{word}\t{count}" for word, count in ranked]
    return "\n".join(lines) + ("\n" if lines else "")


def format_json(ranked):
    """Render ranked (word, count) pairs as a JSON array of objects."""
    return json.dumps([{"word": word, "count": count} for word, count in ranked], indent=2)


def positive_int(value):
    """argparse type for --top: must parse as a positive integer."""
    try:
        result = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid int value: {value!r}")
    if result <= 0:
        raise argparse.ArgumentTypeError(f"--top must be a positive integer, got {value!r}")
    return result


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tally",
        description="Count word frequencies in text files or standard input.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Input file(s) to read. Reads standard input when omitted.",
    )
    parser.add_argument(
        "--top",
        type=positive_int,
        default=10,
        metavar="N",
        help="Show the N most frequent words (default: 10).",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Treat words case-insensitively.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of plain text.",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = read_input(args.files)
    except InputError as exc:
        print(f"tally: {exc}", file=sys.stderr)
        return 1

    words = tokenize(text)
    if args.ignore_case:
        words = [word.lower() for word in words]

    ranked = top_n(Counter(words), args.top)

    if args.json:
        print(format_json(ranked))
    else:
        print(format_text(ranked), end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
