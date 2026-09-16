# roman

A command-line tool that converts between integers and Roman numerals.
Standard library only — no third-party dependencies.

## Usage

```
python3 roman.py [VALUE ...]
```

Each `VALUE` is either an integer from 1 to 3999 or a canonical,
uppercase Roman numeral (lowercase, such as `mcmxciv`, is rejected).
Integers convert to numerals and numerals convert to integers. Give
no arguments to read one value per line from standard input.

### Examples

Convert an integer to a numeral:

```
$ python3 roman.py 1994
MCMXCIV
```

Convert a numeral to an integer:

```
$ python3 roman.py MCMXCIV
1994
```

Convert several values at once, one result per line, in order:

```
$ python3 roman.py 9 1994 MCMXCIV
IX
1994
1994
```

Read values from standard input when no arguments are given:

```
$ printf '9\n1994\n' | python3 roman.py
IX
MCMXCIV
```

Show help:

```
$ python3 roman.py --help
```

Pass `--lower` to print numerals in lowercase and accept lowercase numeral input (still rejected without the flag).

Pass `--json` to print one JSON object per value instead, with keys
`input`, `output`, and `ok`. Invalid values no longer stop processing
or print to standard error; instead they appear in the JSON with
`ok` set to `false` and `output` set to the error message:

```
$ python3 roman.py --json 1994 IIII
{"input": "1994", "output": "MCMXCIV", "ok": true}
{"input": "IIII", "output": "'IIII' is not a canonical Roman numeral", "ok": false}
```

The exit code rules below still apply, so this example exits 1.

## Errors

Values outside 1-3999, and numerals that are not in canonical form
(such as `IIII`, `VX`, `IC`, or `MMMM`), print a message to standard
error and cause a nonzero exit:

```
$ python3 roman.py IIII
roman.py: error: 'IIII' is not a canonical Roman numeral
```

### Exit codes

| Code | Meaning                                  |
| ---- | ----------------------------------------- |
| 0    | All values converted successfully.         |
| 1    | One or more values were invalid.           |
| 2    | A usage error, such as an unknown option.  |

## Tests

```
python3 -m unittest
```

Run from the repository root. Tests are in `tests/test_roman.py`.
