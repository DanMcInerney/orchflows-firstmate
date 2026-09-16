# Backlog

## In flight
## Queued
## Done
- [x] roman-json - quickfix:fix on roman: add --json flag (repo: roman) (kind: ship) (done 2026-09-16)
  Resolution recorded by fm-captain-hold.
  Decision digest: 40ba035685c54ab7826f33358feec2490f59e5452ed77a8fc07167c8d0bae641
  Resolution mode: released

  Captain decision:
  Yes, land the --json branch into roman main. Your reading of the keys is right.

  mode=local-only yolo=off (registry posture). orchflows: quickfix:fix (home library @2a5ca6d) phase=deliver work=roman-json (fm/roman-json @746e01d) review=roman-json-review (ready, no repairs; report data/roman-json-review/report.md) repair=skipped (clean verdict) guidance=code. Reading: exactly keys input/output/ok; invalid -> ok false, output = message; JSON mode no stderr for invalid. next=captain landing approval
  local main
- [x] roman-json-review - quickfix:fix review of roman-json data/roman-json-review/report.md (repo: roman) (kind: scout) (reported 2026-09-16)
  orchflows: quickfix:fix phase=review role=reviewer candidate=fm/roman-json @746e01d
- [x] quickfix-lib - Build Orchflows library quickfix with manual-only fix workflow (repo: orchflows-home) (kind: ship) (done 2026-09-16)
  Resolution recorded by fm-captain-hold.
  Decision digest: eb9e50a97d9d855b9391cfad9d6a39e2dde93870320184b669ac2c98d0d53ecf
  Resolution mode: released

  Captain decision:
  Yes, land it into the Orchflows home main. Do not register anything: when I name quickfix:fix, read it from the home library path as my captain preferences say.

  mode=local-only yolo=off. orchflows: orch-build-workflow via orch-dynamic-workflow phase=deliver work=quickfix-lib (fm/quickfix-lib @2a5ca6d) trial=quickfix:fix work=roman-lower (landed roman main f032c56) review=roman-lower-review (ready) record=data/quickfix-lib/trial-record.md final-review=quickfix-lib-review (ready, no repairs; report data/quickfix-lib-review/report.md) repair=none needed guidance=orchflows,writing next=captain landing approval, then host registration
  local main
- [x] quickfix-lib-review - Final review of quickfix library data/quickfix-lib-review/report.md (repo: orchflows-home) (kind: scout) (reported 2026-09-16)
  orchflows: orch-build-workflow phase=review role=final reviewer candidate=fm/quickfix-lib @2a5ca6d
- [x] roman-lower - Trial quickfix:fix on roman: add --lower flag (repo: roman) (kind: ship) (done 2026-09-16)
  Resolution recorded by fm-captain-hold.
  Decision digest: 6b7da478ef527c670aba187e7c3ca580d8066f1b25fcaa06dc734e9a49d302b1
  Resolution mode: released

  Captain decision:
  Yes, land the --lower trial branch into roman main. Mixed-case input with --lower is fine as it is.

  mode=local-only yolo=off. orchflows: quickfix:fix (trial of fm/quickfix-lib @8811905) phase=work work=roman-lower guidance=none (workflow names none)
  local main
- [x] roman-lower-review - Trial quickfix:fix review of roman-lower data/roman-lower-review/report.md (repo: roman) (kind: scout) (reported 2026-09-16)
  orchflows: quickfix:fix (trial) phase=review role=reviewer candidate=fm/roman-lower @f032c56
- [x] roman-cli - Build roman: integer <-> Roman numeral CLI (repo: roman) (kind: ship) (done 2026-09-16)
  Resolution recorded by fm-captain-hold.
  Decision digest: 9d61dc2659e5d95ff1fa95b12a5d400cf457a4a6685e5acc266415211e151f22
  Resolution mode: released

  Captain decision:
  Yes, land it into local main. Lowercase should stay rejected.

  mode=local-only yolo=off (registry posture). orchflows: orch-dynamic-workflow phase=deliver work=roman-cli (fm/roman-cli @0f83743) review=roman-cli-review (ready with repairs; report data/roman-cli-review/report.md) repair=steer (reject lowercase numerals; verified) guidance=code,writing
  local main
- [x] roman-cli-review - Review roman-cli branch (orch-dynamic-workflow review) data/roman-cli-review/report.md (repo: roman) (kind: scout) (reported 2026-09-16)
  orchflows: orch-dynamic-workflow phase=review role=reviewer candidate=fm/roman-cli @c7fa4fd
