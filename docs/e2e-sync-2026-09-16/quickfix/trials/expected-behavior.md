# Expected behavior

Observable behavior of one `quickfix:fix` run against [`request.md`](request.md), for FirstMate to check against the actual trial.

## Invocation

- The workflow fires only because the captain named `quickfix:fix`; it does not fire on request wording alone.

## Work (step 1)

- Exactly one Orchflows Work agent spawns as a ship in the `roman` project's own delivery mode, on a new branch.
- Absent a request override, it spawns with harness `claude`, model `claude-sonnet-5`, effort `xhigh`.
- The branch adds a `--lower` flag: with the flag, output numerals print lowercase; lowercase input parses only when the flag is given (lowercase input without the flag is rejected or otherwise unchanged from prior behavior).
- The branch adds tests exercising: lowercase output with `--lower`, lowercase input accepted with `--lower`, and lowercase input still rejected without `--lower`.
- The branch adds one README line documenting the flag.
- No files outside this bounded change are touched.
- The change is committed before the Work agent reports done.

## Review (step 2)

- Exactly one Orchflows Review scout spawns after the Work branch is committed, from a vendor different from Work's harness.
- Absent a request override, it spawns with harness `codex`, model `gpt-5.6-luna`, effort `xhigh`.
- It checks out the exact Work branch and commit detached, in its own worktree.
- It edits no files and dispatches no sub-agents.
- Its report names the reviewed commit, gives findings with evidence, and ends with a verdict: ready, ready with the listed repairs, or not ready.

## Repair (step 3)

- If the verdict lists repairs: exactly one steer message reaches the same Work agent from step 1, naming the numbered repairs, any finding deliberately left unaddressed and why, and no other scope; no fresh Work agent and no second Review are dispatched; the Work agent appends a fresh `done:` line after applying them.
- If the verdict is clean: no repair message is sent, and step 4 begins directly.

## Deliver (step 4)

- The `roman` project's own delivery mode lands the final branch; `quickfix:fix` adds no additional review, gate, or loop beyond the one Review and the one conditional repair pass.

## Trial limits

- This is one bounded run under author preparation (the request above, written for this trial); it does not exercise every failure path (for example, a Work agent that cannot honor the Review harness, or a `not ready` verdict requiring more than one repair pass).
- The first trial, run 2026-09-16 against this request, returned a clean Review verdict (no repairs listed), so the repair-by-steer path (step 3) remains unexercised; a future trial or the captain's own use should eventually exercise a run that does list repairs.
