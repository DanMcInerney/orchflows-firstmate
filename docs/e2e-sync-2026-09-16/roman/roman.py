#!/usr/bin/env python3
"""Convert between integers and Roman numerals from the command line."""

import argparse
import json
import re
import sys

MIN_VALUE = 1
MAX_VALUE = 3999

_INT_TO_ROMAN_TABLE = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]

_ROMAN_DIGIT_VALUES = {
    "I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000,
}

_CANONICAL_ROMAN_RE = re.compile(
    r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
)

_INTEGER_RE = re.compile(r"-?\d+")


def int_to_roman(value: int) -> str:
    """Convert an integer in [MIN_VALUE, MAX_VALUE] to a canonical Roman numeral."""
    if not MIN_VALUE <= value <= MAX_VALUE:
        raise ValueError(
            f"{value} is out of range: must be between {MIN_VALUE} and {MAX_VALUE}"
        )
    digits = []
    remaining = value
    for amount, numeral in _INT_TO_ROMAN_TABLE:
        count, remaining = divmod(remaining, amount)
        digits.append(numeral * count)
    return "".join(digits)


def roman_to_int(text: str) -> int:
    """Convert a canonical, uppercase Roman numeral to an integer."""
    if not text or not _CANONICAL_ROMAN_RE.match(text):
        raise ValueError(f"{text!r} is not a canonical Roman numeral")
    total = 0
    index = 0
    while index < len(text):
        current = _ROMAN_DIGIT_VALUES[text[index]]
        if index + 1 < len(text) and _ROMAN_DIGIT_VALUES[text[index + 1]] > current:
            total += _ROMAN_DIGIT_VALUES[text[index + 1]] - current
            index += 2
        else:
            total += current
            index += 1
    return total


def convert(value: str, lower: bool = False) -> str:
    """Convert one value to its counterpart representation, as a string."""
    stripped = value.strip()
    if _INTEGER_RE.fullmatch(stripped):
        numeral = int_to_roman(int(stripped))
        return numeral.lower() if lower else numeral
    numeral_text = stripped.upper() if lower else stripped
    return str(roman_to_int(numeral_text))


def read_values(argument_values):
    """Return the values to convert: CLI arguments, or one per line from stdin."""
    if argument_values:
        return list(argument_values)
    return [line.strip() for line in sys.stdin if line.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="roman.py",
        description="Convert between integers (1-3999) and Roman numerals.",
        epilog=(
            "examples:\n"
            "  roman.py 1994\n"
            "      MCMXCIV\n"
            "  roman.py MCMXCIV\n"
            "      1994\n"
            "  roman.py 9 1994 MCMXCIV\n"
            "      IX\n"
            "      MCMXCIV\n"
            "      1994\n"
            "  printf '9\\n1994\\n' | roman.py\n"
            "      IX\n"
            "      MCMXCIV\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "values",
        metavar="VALUE",
        nargs="*",
        help=(
            "an integer from 1 to 3999, or a canonical Roman numeral; "
            "reads one value per line from standard input when omitted"
        ),
    )
    parser.add_argument(
        "--lower",
        action="store_true",
        help="print numerals in lowercase, and accept lowercase numeral input",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help=(
            "print one JSON object per value, with keys input, output, and ok, "
            "instead of stopping on invalid values"
        ),
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    values = read_values(args.values)

    had_error = False
    for value in values:
        try:
            output = convert(value, lower=args.lower)
            ok = True
        except ValueError as exc:
            output = str(exc)
            ok = False
            had_error = True

        if args.json:
            print(json.dumps({"input": value.strip(), "output": output, "ok": ok}))
        elif ok:
            print(output)
        else:
            print(f"roman.py: error: {output}", file=sys.stderr)
    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
