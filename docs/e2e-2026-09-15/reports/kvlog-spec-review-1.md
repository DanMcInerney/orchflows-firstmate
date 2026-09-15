# kvlog spec review

**Scope:** Read-only spec-phase review of `/tmp/orchflows-e2e/home/data/kvlog-spec-1/report.md` (the kvlog design scout report) against the captain's request, `guidance/writing.md` (Review), `guidance/code.md` (Review), and `libraries/mixed-build/guidance/code.cli.md` (Review). No files were edited and no work was delegated, per the brief. The worktree at `/home/danhm/.treehouse/kvlog-0f3c59/2/kvlog` was inspected only to confirm the spec's own evidence claim.

## What I did

1. Read the spec report in full (272 lines).
2. Read the three named guidance files in full.
3. Confirmed the worktree state the spec cites as evidence: `git status --short --branch` → `## HEAD (no branch)`, `git log -1 --oneline` → `682a53c Seed kvlog`, `ls -la` → only `.claude/`, `.git`, `.gitignore`, `README.md`. This matches the spec's "Evidence and bound" section (its commit hash `682a53e` differs by one trailing character from the actual `682a53c`; likely a typo, noted below).
4. Hand-verified the spec's worked fixture (`sample.jsonl`, four records) against every expected output in acceptance checklist items 1–6, confirming the level counts, service counts, top-error ordering, and UTC time-range normalization are internally consistent.
5. Tested the one technical claim that needed independent verification: whether `datetime.fromisoformat` accepts a trailing `Z`.
   ```
   $ python3 --version
   Python 3.12.3
   $ python3 -c "from datetime import datetime; print(datetime.fromisoformat('2025-01-01T00:00:00Z'))"
   2025-01-01 00:00:00+00:00
   ```
   This environment only has Python 3.12 available, so I could not reproduce the pre-3.11 failure directly, but it is documented CPython behavior (`fromisoformat` gained general ISO 8601 / `Z`-suffix parsing in the 3.11 changelog) — see finding 4 below.

## Findings, ordered by impact

### 1. Exit-1 diagnostic wording is pinned for only 2 of the several failure classes it covers
Report §2 states exit 1 covers "malformed input, missing or mistyped required fields, invalid record timestamps/levels, file-open/read failures, or UTF-8 decoding errors," all using "one source-and-physical-line diagnostic (for example, `kvlog: app.jsonl:4: invalid JSON`)." The acceptance checklist (§6, items 8–9) pins exact stderr text for exactly two cases: invalid JSON (`kvlog: <stdin>:3: invalid JSON`) and a missing key (`kvlog: <stdin>:1: missing required key 'msg'`). No wording is given anywhere for: a non-object JSON value, a non-string or wrong-type field, an unsupported `level` value, an invalid `ts` value, a file that fails to open, or a UTF-8 decode error. File-open failures in particular have no natural "physical line number" — the captain's own request ties exit 1 specifically to "the offending line number on stderr," and the spec never says what a maker should print for a source that fails before any line is read.

This means a reviewer executing the checklist mechanically (task's own bar: "a later reviewer can execute mechanically against the delivered tool") cannot check most of exit 1's stated causes — only the two that happen to have pinned text. A maker has to invent wording, format, and (for file-open failures) whether a line number appears at all, for the remaining ~5 cases.

**Repair:** either give one canonical message template per failure class (e.g. `kvlog: <source>:<line>: invalid level '<value>'`, `kvlog: <source>: <os error text>` with no line segment for open failures) or explicitly say wording for the untested classes is a maker's choice with any nonempty message accepted, so a reviewer knows not to expect exact-match text there.

### 2. The `<stdin>` source label is never established as part of the contract, only used in acceptance tests
§2 describes the diagnostic format with a file example only: `kvlog: app.jsonl:4: invalid JSON`. The literal string `<stdin>` first appears in §6 items 8 and 9, with no prior statement in §2–§4 that stdin's source label (as opposed to a bare `-`, `stdin`, or `(stdin)`) must be exactly `<stdin>`. A maker who implements from the design sections (§2–4) — which is where the module layout in §3 tells them to look — and only skims the acceptance checklist for one example each of exit 1/2 could reasonably choose a different label and still believe they matched the documented contract, then fail checklist items 8–9.

**Repair:** state the exact stdin source label once in §2, next to the existing `app.jsonl:4` example.

### 3. Exit-2 usage-error wording is pinned for only one of several documented causes
§2 lists exit-2 causes as "invalid option values, invalid filter timestamps, reversed bounds, a repeated `-`, or unrecognized options," but §6 item 10 pins exact text only for `--top 0` (`kvlog: error: --top must be a positive integer`). There is no pinned (or even example) wording for an invalid `--since`/`--until` value or for `since > until`. Given check item requirement 3 — "is every item a concrete command with an exact expected result" — this is the same gap as finding 1, on the usage-error side.

**Repair:** add one acceptance item (or at minimum one example string per class) for invalid-filter-syntax and reversed-bounds text, matching the treatment already given to `--top`.

### 4. No minimum Python version is stated, and the spec's own `Z`-handling requirement is a known cross-version pitfall
§2: "`ts`, `--since`, and `--until` accept ISO 8601 date-times supported by `datetime.fromisoformat`, with a terminal `Z` accepted." `datetime.fromisoformat` did not accept a trailing `Z` before Python 3.11 (it raises `ValueError`); general ISO 8601 `Z`/offset parsing was added in the 3.11 changelog. I confirmed `Z` works on the only Python available here (3.12.3, shown in "What I did" above) but could not test 3.9/3.10 — no older interpreter was installed in this environment to reproduce the failure directly.

The captain's request only says "Python 3," and the spec (§ "Module layout," README checklist item 11) only says "Requires Python 3; no third-party dependencies," never pinning 3.11+ or instructing the maker to normalize `Z` manually (e.g. `value[:-1] + '+00:00'` before calling `fromisoformat`). A maker who develops and tests only on a recent local interpreter (very plausible — this very review environment only has 3.12) would ship code that raises on any Python 3.9/3.10 deployment target, silently failing every timestamp in the input the moment `-Z` appears, which is the format used in almost every acceptance-checklist fixture.

**Repair:** either state a minimum Python version of 3.11, or explicitly instruct `parse_timestamp` to strip/normalize a trailing `Z` itself rather than relying on `fromisoformat`'s native handling, so the tool works on any Python 3 the captain's request implies.

### 5. Acceptance item 13 pins the literal unit-test count, which is a structural detail, not observable behavior
§6 item 13 requires `python3 -m unittest` output to contain exactly `Ran 15 tests in ...` followed by `OK`. §5's own preface says tests should "assert observable behavior, not private implementation details," and `guidance/code.md` (Review) says to treat file/test structure as a design preference and to test "observable behavior rather than implementation structure." Pinning the exact count of top-level test methods contradicts both: a maker who splits one listed test into two (e.g., separating "missing key" from "wrong type" in test 3) for clarity, or adds one extra defensive case, produces `Ran 16 tests` and fails an acceptance item that has nothing to do with correctness.

**Repair:** relax item 13 to check for `OK` (and no failures/errors) without pinning the count, or explicitly say "at least 15."

### 6. Acceptance item 5 is not a self-contained expected result
§6 item 5 ("`--top` greater than distinct errors") says output "matches item 3's JSON except `top_errors` contains both ... in that order," rather than giving the full expected line the way every other JSON-output item does. This is derivable (I derived it while checking the fixture: `{"total_lines":4,"by_level":{"DEBUG":0,"INFO":1,"WARN":0,"ERROR":3},"by_service":{"auth":3,"web":1},"top_errors":[{"message":"timeout","count":2},{"message":"denied","count":1}],"time_range":{"start":"2025-01-01T05:00:00Z","end":"2025-01-03T00:00:00Z"}}`) but requires the reviewer to hand-construct the comparison string rather than diff against one given in the spec, unlike every other item in the checklist.

**Repair:** print the full expected JSON line inline, matching the style of items 3 and 12.

### 7. `by_service` omits zero-count services; `by_level` always shows all four — the asymmetry is demonstrated once, never stated as a rule
§2 states "All four level keys always appear, including zero counts" but says nothing equivalent (positive or negative) for `by_service`. The only evidence that services are *omitted* rather than zero-padded is acceptance item 4, where a filtered-out `web` record causes the `web` line to disappear entirely from both the human and JSON output rather than showing `"web": 0`. §3's description of `summarize()` ("apply inclusive filters and compute total, all level counts, service counts...") confirms services are computed post-filter like everything else, but doesn't say why the two collections behave differently at zero. A maker who patterns `by_service` after the explicitly-stated `by_level` "always all four... including zero" rule could reasonably (and wrongly) build a zero-padded service map from every service name seen across all input, and would only discover the mismatch by diffing against the acceptance checklist.

**Repair:** add one sentence to §2 stating `by_service` only includes services present in matching records (no zero-padding), contrasting it explicitly with the fixed `by_level` enum.

### 8. Minor: no acceptance test proves "stop at first malformed record" across multiple sources
§2's "one source-and-physical-line diagnostic" and §1's streaming design imply fail-fast (stop at the first bad line, across sources, without buffering the rest), and this reading is also consistent with the captain's own phrasing ("the offending line number," singular). But no design sentence states it outright, and no checklist item exercises it with two malformed lines, or a valid first file followed by a bad second file. Given the design intent is inferable from existing text and matches the captain's own wording, this is a documentation/coverage nice-to-have, not a genuine ambiguity — lowest priority of the eight findings.

### Typo (non-blocking)
§ "Evidence and bound": `git log -1 --oneline` is quoted as `682a53e Seed kvlog`; the actual commit hash in this worktree is `682a53c` (confirmed above). One-character transcription slip, doesn't affect any conclusion in the report.

## Requirement coverage check (captain's request)

Every explicit captain requirement is present in the spec and I found no dropped or contradicted requirement:

- Files and stdin: §2 ("No file arguments means read stdin... named files are read in argument order and may be combined with `-`").
- The five summary parts (total lines, by-level, by-service, top-N ERROR messages with counts, time range): all five appear in both the JSON shape (§2) and human layout (§2), and in `summarize()`'s ownership (§3).
- `--json`, `--top N`, `--since`, `--until`, `--help`: all in the options table (§2).
- Exit 0/1/2, with the offending line number on stderr for exit 1: §2, though see findings 1–3 on how completely the *wording* of those diagnostics is specified.
- Unit tests under `python3 -m unittest`: §3 (`tests/__init__.py`, `tests/test_kvlog.py`), §5 (15 named tests), §6 item 13.
- README with install and usage: §3, §6 item 11 (pins exact README lines) and item 12 (proves the installed script actually runs).
- No third-party dependencies: §1 ("use only the standard library"), §3 ("no external imports"), README line in item 11.

Ambiguities the captain's own request leaves open — option semantics, JSON field names/types, tie-breaking for top errors, inclusive/exclusive bounds, timezone handling, empty-input behavior — are all explicitly and consistently resolved in §2 and §4 (inclusive bounds stated twice consistently; naive timestamps assumed UTC; ties broken count-desc then message-asc; empty input defined down to the exact zero/none shape). I did not find a case where the spec's resolution contradicts the captain's text.

## Verdict

**Ready with the listed repairs.** The design is sound, internally consistent (I independently re-derived every number in the worked fixture and it matches), appropriately minimal (no packaging, no schema system, no unrequested machinery — consistent with `code.md`'s file-size/ownership guidance and `code.cli.md`'s exit-code/stdio/help requirements), and resolves essentially every ambiguity the captain's request leaves open. The gaps are concentrated in one place: the acceptance checklist doesn't yet pin exact text for most non-happy-path diagnostics (findings 1–3), doesn't state the stdin source label as part of the contract rather than only as a test fixture (finding 2), is missing a cross-version correctness note that could break the tool on Python 3.9/3.10 (finding 4), and has two checklist items (5, 13) that are harder to execute mechanically than the rest. None of these require a captain decision — they're spec-completeness repairs a maker or spec author can resolve unilaterally — but a maker proceeding on the design sections alone, without reverse-engineering missing rules from the checklist, would plausibly build something that fails several checklist items despite matching every explicit sentence in §2–§4.
