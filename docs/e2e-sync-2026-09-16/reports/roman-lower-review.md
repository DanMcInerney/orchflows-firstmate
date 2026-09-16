# Review report: `--lower`

Reviewed commit: `f032c56e0189d7d3694fe2a76b20a45375f1ad28` (`fm/roman-lower`).

## What I checked

Detached this worktree with `git checkout --detach fm/roman-lower` and confirmed the SHA with `git rev-parse HEAD`. Ran `python3 roman.py --help`, behavior probes for arguments and standard input, compared the no-flag lowercase error against `main:roman.py`, inspected `git diff main...HEAD`, and ran `python3 -m unittest` and `git diff --check main...HEAD`.

## Findings

1. **Lowercase output and input work with the flag.** `roman.py:59-66` lowercases integer-to-numeral results when `lower=True` and uppercases numeral input before canonical validation. The CLI passes the flag to each conversion (`roman.py:113-121`). `python3 roman.py --lower 9 1994 MCMXCIV` returned exit 0 and stdout `ix\nmcmxciv\n1994\n`. `python3 roman.py --lower xiv`, `--lower xIv`, and `--lower XIV` each returned `14\n`. Piping `9\nXIV\nxiv\nxIv\n` into `python3 roman.py --lower` returned `ix\n14\n14\n14\n`.

2. **Canonical validation still rejects non-canonical input.** `python3 roman.py --lower iiii` returned exit 1, no stdout, and `roman.py: error: 'IIII' is not a canonical Roman numeral`. Case normalization does not make `IIII` valid.

3. **Default lowercase rejection matches `main`.** Candidate `python3 roman.py xiv` returned exit 1, no stdout, and `roman.py: error: 'xiv' is not a canonical Roman numeral`. Executing `main:roman.py` with the same argument produced the identical exit code and stderr. Lowercase standard input without the flag produced the same error. With `lower=False`, the candidate passes the original stripped input to `roman_to_int` and returns the original uppercase numeral output unchanged (`roman.py:61-66`).

4. **Case handling is sensible; mixed case is not called out explicitly.** Uppercase input remains accepted with `--lower`, consistent with prior behavior. Mixed-case input such as `xIv` is also accepted after normalization. The README and help document lowercase input acceptance, but do not explicitly say mixed-case input is accepted. This is an undocumented extra behavior, not a blocker for the requested lowercase support.

5. **Tests and documentation cover the requested behavior.** Tests cover lowercase output, lowercase input, and rejection without the flag (`tests/test_roman.py:153-169`, `tests/test_roman.py:211-219`). The README documents the flag (`README.md:56`), and `python3 roman.py --help` describes printing lowercase numerals and accepting lowercase input. `python3 -m unittest` passed: **29 tests, OK**.

6. **Change scope is bounded.** `git diff --name-status main...HEAD` lists only `README.md`, `roman.py`, and `tests/test_roman.py`. `git diff --check main...HEAD` passed, and `git status --short` was empty.

## Recommendation

No required repairs. Mixed-case input acceptance is reasonable; documenting it would make the added behavior explicit but is optional for this request.

**Verdict: ready.**
