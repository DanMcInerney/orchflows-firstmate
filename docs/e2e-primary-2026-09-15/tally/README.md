# tally

A command-line tool that counts word frequencies in one or more text
files (or standard input) and prints the most frequent words with
their counts. Standard library only — no third-party dependencies.

## Running it

```sh
python3 tally.py [OPTIONS] [FILE ...]
# or
python3 -m tally [OPTIONS] [FILE ...]
```

Both forms must be run from the repository root (or with the repo
root on `PYTHONPATH`).

With no `FILE` arguments, tally reads from standard input.

Input (files and standard input) is expected to be **UTF-8 encoded**.

## Word definition and ordering

A **word** is a maximal run of ASCII letters and digits, optionally
joined by internal apostrophes:

- `don't` and `O'Brien's` are each counted as a single word.
- Surrounding punctuation/quotes are stripped: `'hello'` → `hello`.
- Hyphens split words: `well-known` → `well`, `known`.
- All other characters (whitespace, punctuation, non-ASCII letters)
  are treated as separators.

Results are sorted by count **descending**. Words with equal counts
are broken **alphabetically ascending** (case-sensitive, using the
casing the words are counted with — i.e. lowercased first when
`--ignore-case` is given), so output is deterministic run to run.

## Options

| Option          | Description                                                        |
|-----------------|---------------------------------------------------------------------|
| `--top N`       | Show the `N` most frequent words. Default: `10`. `N` must be a positive integer; `0`, negative, or non-integer values are a usage error. |
| `--ignore-case` | Fold words to lowercase before counting, so `Cat`, `cat`, and `CAT` count as one word. |
| `--json`        | Print machine-readable JSON instead of plain text.                 |
| `--help`        | Print usage and exit `0`.                                          |

## Output format

Plain text (default): one `word<TAB>count` line per ranked word, e.g.

```
the	3
fox	2
```

JSON (`--json`): an array of objects, e.g.

```json
[
  {"word": "the", "count": 3},
  {"word": "fox", "count": 2}
]
```

## Examples

Count words in a file, top 10 by default:

```sh
python3 tally.py notes.txt
```

Top 3 words, case-insensitive:

```sh
python3 tally.py --top 3 --ignore-case notes.txt
```

Read from standard input:

```sh
cat notes.txt | python3 tally.py
```

Combine multiple files (counts are merged across all of them):

```sh
python3 tally.py chapter1.txt chapter2.txt
```

Machine-readable output:

```sh
python3 tally.py --json notes.txt
```

## Exit codes

| Code | Meaning                                                              |
|------|-----------------------------------------------------------------------|
| `0`  | Success (including `--help`).                                        |
| `1`  | An input source could not be read: a file is missing/unreadable, or a file or standard input is not valid UTF-8. tally prints `tally: cannot read '<path>': <reason>` (or `tally: cannot read <stdin>: ...` for standard input) to stderr and produces no stdout output. |
| `2`  | Usage error: an unknown/malformed option, or an invalid `--top` value (non-integer, zero, or negative). argparse prints a usage message to stderr. |

## Running the tests

From the repository root, with no extra arguments:

```sh
python3 -m unittest
```

Tests live in `tests/test_tally.py`. Unit tests exercise the
tokenizer and ranking functions directly; CLI tests run `tally.py` as
a subprocess against temporary files/stdin to verify observable
behavior (counting, `--top`, `--ignore-case`, `--json`, multiple
files, and exit codes). Each test uses its own temporary files, so
tests are independent and safe to run in any order.
