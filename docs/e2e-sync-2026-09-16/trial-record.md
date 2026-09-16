# Trial record: quickfix:fix on roman (--lower)

Candidate workflow: `libraries/quickfix/skills/fix/SKILL.md` read by FirstMate from branch `fm/quickfix-lib` at 8811905 (not yet registered; read by path from git).
Request: the text in `libraries/quickfix/trials/request.md`, given by the captain on 2026-09-16.
Coordinator: FirstMate primary on Claude Code 2.1.269. Target: `roman`, delivery mode local-only, merge approval by the captain.

## Observed run

1. Work: task `roman-lower`, spawned as a ship with `--harness claude --model claude-sonnet-5 --effort xhigh` (the saved preference; the request named none), base local main 0f83743. Committed f032c56 touching only README.md, roman.py, tests/test_roman.py; reported ready in branch.
2. Review: task `roman-lower-review`, a scout spawned with `--harness codex --model gpt-5.6-luna --effort xhigh`, after the Work commit. It checked out `fm/roman-lower` detached, recorded f032c56, edited nothing, delegated nothing. Report: `data/roman-lower-review/report.md`, verdict **ready**, no required repairs; one optional note that mixed-case input (e.g. `xIv`) is accepted with `--lower` and undocumented. 29 tests pass.
3. Repair: skipped, as the workflow says for a clean verdict. No steer sent, no second review.
4. Deliver: the captain approved and FirstMate fast-forwarded roman local main to f032c56 on 2026-09-16; the captain accepted mixed-case input with --lower as is. FirstMate spot-checked: tests pass, `--lower 1994` -> mcmxciv, `--lower mcmxciv` -> 1994, `mcmxciv` without the flag -> exit 1.

Agent count: 2, sequential, as declared. Behavior matched `trials/expected-behavior.md` for invocation, Work, Review, the clean-verdict branch of Repair, and Deliver up to the approval gate.

## Coordinator observations

- The workflow names no guidance domain for either assignment. FirstMate therefore passed no guidance files; the core `code` guidance (Make and Review sections) was applicable and unused.
- `orch-work` and `orch-review` are named but not linked; a coordinator reading the skill by path must already know where the primitives live.
- The workflow does not say what the Review brief's checks come from; FirstMate derived them from the request and the prior behavior on main.

## Trial limits

- Author preparation: the request was written for this trial; FirstMate wrote both briefs, including the numbered checks, using `docs/firstmate.md` brief wording.
- Intervention: none during the run.
- Unexercised: the repair-by-steer path (verdict was clean), a `not ready` verdict, a Work agent whose profile cannot honor a repair, a no-mistakes or direct-PR project, manual-only invocation through an installed plugin (the library was read by path from an unmerged branch).
