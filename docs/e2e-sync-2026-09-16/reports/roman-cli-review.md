# Roman CLI candidate review

Reviewed commit: `c7fa4fd3a99045846a53d47f64c15ef94c7191e9` (`fm/roman-cli`). I checked out the requested commit detached and reviewed the CLI, tests, README, and added project agent files. The review was read-only.

## Verdict

**Ready with the listed repair.** The only material mismatch is that lowercase Roman numerals are accepted even though the brief requires them to be rejected.

## Repair

1. **Reject lowercase numerals at the CLI and add a regression test.** In `roman.py:42-46`, `roman_to_int` uppercases the input before validation. `tests/test_roman.py:72-73` explicitly expects lowercase to succeed. Reproduction: `python3 roman.py mcmxciv` exits 0 and prints `1994`; the brief requires exit 1 and a clear stderr message. Validate the original spelling and add a subprocess test asserting the CLI exit code and stderr for lowercase input.

## Evidence

- `git checkout --detach fm/roman-cli` followed by `git rev-parse HEAD` reported the reviewed SHA above; the worktree remained clean.
- `python3 roman.py 1994` printed `MCMXCIV`; `python3 roman.py MCMXCIV` printed `1994`; `python3 roman.py 9 1994 MCMXCIV` printed `IX`, `1994`, `1994` in order. All exited 0.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest` ran 23 tests and passed. `RoundTripTests.test_round_trip_full_range` checks every integer from 1 through 3999. The suite also invokes the script as a subprocess and checks output, exit codes, help, usage errors, and stderr for invalid input.
- Stdin probes with blank lines and surrounding whitespace skipped empty lines and converted `9` to `IX`. Input `9  \n1994\t` without a final newline produced `IX\nMCMXCIV\n` and exited 0.
- CLI probes for `0`, `4000`, `-5`, `IIII`, `VX`, `IC`, `MMMM`, and an empty argument exited 1 with explanatory stderr. `-5` is correctly treated as an invalid value, not an argparse usage error. A mixed `1994 IIII 14` invocation converted both valid values, reported `IIII` on stderr, and exited 1.
- `python3 roman.py --help` exited 0; `python3 roman.py --bogus` exited 2 with argparse's usage error. The README's integer, numeral, multiple-value, stdin, help, and invalid-value examples match observed behavior, apart from its omission of the lowercase case required by the brief.
- Python imports in the tool and tests are from the standard library; no third-party dependency was added.
- The extra `AGENTS.md` records the project entry point and the Python 3.12.3 `unittest` discovery requirement; `CLAUDE.md` is a two-line pointer to it. These additions are small and tied to maintaining the requested test command.

## Review coverage

The brief's checklist was exercised against the candidate and README. A second pass found no other material issue or shared cause beyond the lowercase normalization. There were no dead-end sources. The review was run on Python 3.12.3; other Python versions and operating systems were outside this bounded check.
