# Trial record: mixed-build:feature on kvlog

Run September 15, 2026 through stock FirstMate `b182d0f` with Herdr, by the captain that authored this library. Request: [request.md](request.md)-shaped, a Python 3 JSON-lines log summary CLI named kvlog with files and stdin, level and service counts, top-N errors, a time range, `--json`, `--top`, `--since`, `--until`, `--help`, exit codes 0/1/2, unit tests and a README. Target project: `kvlog`, delivery mode local-only.

## Agents, in dispatch order

| Phase | Role | Task | Harness, model, effort | Outcome |
| --- | --- | --- | --- | --- |
| spec | Work (scout) | `kvlog-spec-1` | codex gpt-5.6-luna xhigh | design, 15-test plan, 13-item acceptance list; revised to 17 items after review |
| spec | Review (scout) | `kvlog-spec-review-1` | claude claude-sonnet-5 xhigh | ready with 8 repairs (diagnostic wording, `<stdin>` label, Python floor, checklist executability) |
| implement | Work (ship) | `kvlog-impl-1` | claude claude-sonnet-5 xhigh | `kvlog.py` + 15 tests; repaired to 20 tests after review |
| implement | Review (scout) | `kvlog-impl-review-1` | codex gpt-5.6-luna xhigh | not ready: NaN accepted, read-time OSError uncaught, year-0001 overflow (all real, all repaired); README stub deferred to docs-qa by design |
| docs-qa | Work (ship) | `kvlog-docs-3` | codex gpt-5.6-luna xhigh | README, `examples/app.jsonl`, `scripts/acceptance.sh`, `ACCEPTANCE.md` 17/17 |
| docs-qa | Review (scout) | `kvlog-docs-review-1` | claude claude-sonnet-5 xhigh | ready with 1 writing repair; 17/17 acceptance, 20/20 tests, README outputs exact, 3 novel inputs correct |

Six agents plus three repair passes, each repair a single steer to the phase's maker through FirstMate's inbox, none a second Review. Every reviewer was a different vendor from its maker, as the saved preferences declare. Delivered `main`: `682a53c` → `d0d0673` (implement) → `c08cb11` (docs-qa).

## Deviations from expected-behavior.md

- The docs-qa Work was dispatched three times. The first two were discarded before doing work: one because the captain's landing helper did not stop on a refused merge, one because the project had a bare origin that FirstMate's local-only merge never updates, so the new worktree started from a stale base. Removing the origin (a local-only project has no remote) fixed it. This is a project-shape rule for callers, not a workflow defect.
- Codex workers needed the captain twice on first run (repository trust, hooks trust) and the docs-qa Codex worker reported `blocked:` twice because its exec wrapper could not parse commands containing backticks; both were unblocked by one steer each (run the checklist from a script file; write file contents with the native edit tool).
- The Codex docs-qa worker committed a ticket file from an unrelated globally installed skill under `.orch/`; the final Review noted it and the repair steer removed it.
- The spec Review found the first checklist pinned an exact unit-test count; the revised spec requires at least 15.

## Unexercised

Delivery modes other than local-only; a FirstMate primary driven by a model rather than by the authoring captain; Python versions below 3.12 for the 3.9 floor claim.
