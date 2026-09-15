# Tally candidate review

Reviewed commit: `7bbb08c97c6122583080da1e15535eb861261baf` (`fm/tally-build`). I checked the candidate read-only, ran its tests and CLI, exercised the README examples with sample inputs, and inspected the implementation and dependency imports.

## Finding

**Invalid UTF-8 input escapes the documented file-error handling.** [`tally.py:42-43`](/home/danhm/.treehouse/tally-ccf83a/2/tally/tally.py:42) opens inputs as UTF-8 and decodes during `read()`, but [`tally.py:104-108`](/home/danhm/.treehouse/tally-ccf83a/2/tally/tally.py:104) catches only `OSError`. A file containing invalid UTF-8 raises `UnicodeDecodeError`, so the CLI emits a Python traceback instead of the concise file error promised by [`README.md:100`](/home/danhm/.treehouse/tally-ccf83a/2/tally/README.md:100).

Reproduction:

```sh
python3 -c "import subprocess; p=subprocess.run(['python3','tally.py','/dev/stdin'],input=b'bad:\xff',capture_output=True); print('exit=',p.returncode); print('stdout=',p.stdout.decode(errors='replace')); print('stderr=',p.stderr.decode(errors='replace'))"
```

Observed: exit code `1`, empty stdout, and stderr ending in `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff ...` with a traceback. Handle decode failures as file-read errors and document the accepted encoding; keep the file-error exit code distinct from usage errors.

## Checks that passed

- `python3 -m unittest` from the repository root discovered and passed all 22 tests (`Ran 22 tests ... OK`). CLI tests use subprocesses and separate temporary directories; see [`tests/test_tally.py:16-23`](/home/danhm/.treehouse/tally-ccf83a/2/tally/tests/test_tally.py:16) and the per-test fixtures from lines 60 onward.
- File, stdin, and multiple-file examples produced the expected counts. For example, `python3 tally.py <(printf 'apple banana\n') <(printf 'apple apple\n')` printed `apple<TAB>3` then `banana<TAB>1`; `printf 'one two two three three three\n' | python3 tally.py` ranked `three`, `two`, `one` with counts 3, 2, 1.
- The README’s top-3 case-insensitive example printed `dog<TAB>3` then `cat<TAB>2`. The JSON example parsed as a JSON array in the test suite, and a direct `--json` run produced the documented array of `{ "word", "count" }` objects.
- `python3 -m tally --help` printed usage and exited 0. `python3 tally.py --top 0` printed an argparse usage error and exited 2; the unit tests also cover an unknown option, negative and non-integer `--top` values.
- A 12-unique-word stdin sample produced 10 output lines by default. `printf 'z a z a m\n' | python3 tally.py` ranked the tied `a` and `z` alphabetically. The README describes the same descending-count/alphabetical-tie behavior implemented in [`tally.py:27-33`](/home/danhm/.treehouse/tally-ccf83a/2/tally/tally.py:27).
- Missing-file and directory inputs returned exit 1, no stdout, and a concise `tally: cannot read ...` stderr message. The README documents exit 1 for file-read failures and exit 2 for usage errors.
- The implementation and tests import only Python standard-library modules ([`tally.py:13-17`](/home/danhm/.treehouse/tally-ccf83a/2/tally/tally.py:13), [`tests/test_tally.py:1-6`](/home/danhm/.treehouse/tally-ccf83a/2/tally/tests/test_tally.py:1)); no third-party dependency manifest or imports are present.

## Verdict

**Ready with the listed repair:** handle invalid UTF-8 as a documented file-read error rather than exposing a traceback.
