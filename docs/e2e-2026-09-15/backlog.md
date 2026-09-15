# Backlog

## In flight
## Queued
- [ ] kvlog-feature - kvlog: build via mixed-build:feature (Orchflows saved workflow) (repo: kvlog) (kind: ship) (since 2026-09-15)
  orchflows: mixed-build:feature phase=docs-qa work=kvlog-docs-3 (fm/kvlog-docs-3 @ca74410) review=kvlog-docs-review-1 (done: ready with 1 writing repair; 17/17, 20/20) repair=steer kvlog-docs-3 guidance=writing,code.cli
## Done
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
- [x] kvlog-spec-1 - kvlog spec phase Work (design + acceptance checklist) data/kvlog-spec-1/report.md (repo: kvlog) (kind: scout) (reported 2026-09-15)
  orchflows: mixed-build:feature phase=spec role=Work; reports design and acceptance checklist
- [x] orch-author-review-1 - Review the authored mixed-build library (Orchflows Review) data/orch-author-review-1/report.md (repo: orchflows-home) (kind: scout) (reported 2026-09-15)
  orchflows: build-workflow phase=review reviews work=orch-author-1 branch fm/orch-author-1; findings only
- [x] orch-author-1 - Author the mixed-build workflow library through Orchflows build-workflow (repo: orchflows-home) (kind: ship) (done 2026-09-15)
  orchflows: build-workflow phase=deliver work=orch-author-1 (fm/orch-author-1 @5d13f33) review=orch-author-review-1 (done) repair=steer (done, 5d13f33) guidance=orchflows,writing,code | trial record deferred to Half B
  local main
