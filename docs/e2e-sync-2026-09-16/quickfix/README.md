# quickfix

One saved Orchflows workflow: [`fix`](skills/fix/SKILL.md), for a small, bounded change to an existing project.

## Composition

Two agents, dispatched in sequence; nothing runs concurrently:

1. **Work** — an `orch-work` ship implements the change with tests, on a branch, in the target project's own delivery mode. Saved preference: `claude` / `claude-sonnet-5` / `xhigh`.
2. **Review** — an `orch-review` scout, from a vendor different than Work's, audits that branch detached and read-only. Saved preference: `codex` / `gpt-5.6-luna` / `xhigh`.
3. **Repair** — if Review lists repairs, the same Work agent is steered with them. No second Review.
4. **Deliver** — the target project's own delivery mode lands the branch.

The current request's model and effort choices, if any, still override the saved preferences per the precedence in `<core>/docs/architecture.md#model-and-effort` (core = the installed `orchflows-firstmate` package). This workflow is manual-only: it runs only when the captain names it.

## Install

Requires the `orchflows-firstmate` core installed and registered per that package's `docs/hosts.md`. Add this library to a FirstMate home, then run its setup and register/refresh the library with the primary's harness:

```sh
python <core>/scripts/orchflows.py setup --home <home> --source <core>
python <core>/scripts/orchflows.py doctor --home <home>
```

Then register or refresh `quickfix` with the primary's harness (Claude Code or Codex) per `docs/hosts.md#register-and-refresh`.

## Invoke

- Claude Code: `/quickfix:fix`
- Codex: `$quickfix:fix` or the skill picker

Or read `skills/fix/SKILL.md` from its resolved library path.

## Dependencies

The `orchflows-firstmate` core, for its `orch-work` and `orch-review` primitives and the FirstMate brief/spawn owners they dispatch through. No other library.

## Trial

[`trials/request.md`](trials/request.md) and [`trials/expected-behavior.md`](trials/expected-behavior.md) record the bounded trial run against the `roman` project (add a `--lower` flag) used to exercise this workflow before delivery.
