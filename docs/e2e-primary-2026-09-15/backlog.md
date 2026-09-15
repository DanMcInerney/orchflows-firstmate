# Backlog

## In flight
## Queued
## Done
- [x] tally-build - Build tally word-frequency CLI (repo: tally) (kind: ship) (done 2026-09-15)
  Resolution recorded by fm-captain-hold.
  Decision digest: ec519f46cc6aabd187430685f3a07488ebc0f900abef77a685c9b8ea30bd5895
  Resolution mode: released

  Captain decision:
  Yes, merge it into main.

  Captain request: Python 3 CLI counting word frequencies in files or stdin; --top N (default 10), --ignore-case, --json, --help; exit 0 success, 2 usage errors; unittest tests; README with usage examples; no third-party deps.
  Delivery: local-only, yolo off (registry posture).
  orchflows: orch-dynamic-workflow phase=deliver work=tally-build (fm/tally-build @3dfd86f) review=tally-review (ready with one repair: invalid UTF-8 traceback; report data/tally-review/report.md) repair=steer (applied @3dfd86f, 24 tests pass) guidance=code
  local main
- [x] tally-review - Review tally build branch data/tally-review/report.md (repo: tally) (kind: scout) (reported 2026-09-15)
  orchflows: orch-dynamic-workflow phase=review role=reviewer for tally-build (fm/tally-build @7bbb08c) guidance=code
- [x] kvlog-feature - kvlog: build via mixed-build:feature (Orchflows saved workflow) (repo: kvlog) (kind: ship) (done 2026-09-15)
  orchflows: mixed-build:feature phase=docs-qa work=kvlog-docs-3 (fm/kvlog-docs-3 @ca74410) review=kvlog-docs-review-1 (done: ready with 1 writing repair; 17/17, 20/20) repair=steer kvlog-docs-3 guidance=writing,code.cli
- [x] kvlog-docs-review-1 - kvlog docs-qa phase Review (final QA of the delivered artifact) data/kvlog-docs-review-1/report.md (repo: kvlog) (kind: scout) (reported 2026-09-15)
  orchflows: mixed-build:feature phase=docs-qa role=Review of fm/kvlog-docs-3 against the spec acceptance checklist; findings only
- [x] kvlog-docs-3 - kvlog docs-qa phase Work (README, examples, ACCEPTANCE.md) (repo: kvlog) (kind: ship) (done 2026-09-15)
  orchflows: mixed-build:feature phase=docs-qa role=Work on merged main; inputs spec report + impl review
  local main
- [x] kvlog-docs-2 - kvlog docs-qa phase Work (README, examples, ACCEPTANCE.md) (repo: kvlog) (kind: ship) (done 2026-09-15)
  orchflows: mixed-build:feature phase=docs-qa role=Work on merged main; inputs spec report + impl review
  local main
- [x] kvlog-impl-1 - kvlog implement phase Work (kvlog.py + tests per spec) (repo: kvlog) (kind: ship) (done 2026-09-15)
  orchflows: mixed-build:feature phase=implement role=Work; input spec data/kvlog-spec-1/report.md
  local main
- [x] kvlog-docs-1 - kvlog docs-qa phase Work (README, examples, ACCEPTANCE.md) (repo: kvlog) (kind: ship) (done 2026-09-15)
  orchflows: mixed-build:feature phase=docs-qa role=Work; inputs spec report + impl review
  local main
- [x] kvlog-impl-review-1 - kvlog implement phase Review (audit fm/kvlog-impl-1) data/kvlog-impl-review-1/report.md (repo: kvlog) (kind: scout) (reported 2026-09-15)
  orchflows: mixed-build:feature phase=implement role=Review of fm/kvlog-impl-1; findings only
- [x] kvlog-spec-review-1 - kvlog spec phase Review (independent audit of the spec) data/kvlog-spec-review-1/report.md (repo: kvlog) (kind: scout) (reported 2026-09-15)
  orchflows: mixed-build:feature phase=spec role=Review of kvlog-spec-1 report; findings only
