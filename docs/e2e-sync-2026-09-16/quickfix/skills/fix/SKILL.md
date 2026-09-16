---
name: fix
description: Small bounded change to an existing project — Work with tests on a branch, one independent cross-vendor Review, one repair pass, then the project's delivery mode. Run only when named.
disable-model-invocation: true
---

For one small, bounded change to an existing project: a fix, a small feature, a flag. Two Orchflows agents total, dispatched in sequence; nothing runs concurrently. The repair pass reuses the Work agent rather than spawning a third.

## 1. Work

Dispatch one `orch-work` agent (`<core>/skills/orch-work/SKILL.md`) as a ship in the target project's own delivery mode: implement the captain's bounded change with tests, committed on a branch.

- **Input:** the captain's request (the exact change and its acceptance criteria) and the target project's existing conventions.
- **Check:** the branch builds, the new tests exercise the change and pass, no files outside the bounded change are touched.
- **Guidance domain:** `code`, resolved per `<core>/docs/architecture.md#guidance-selection` — apply its Make sections. The target project's own conventions also apply.
- **Saved preference:** harness `claude`, model `claude-sonnet-5`, effort `xhigh`, overridable by the current request per the precedence in `<core>/docs/architecture.md#model-and-effort` (core = the installed `orchflows-firstmate` package).

## 2. Review

Dispatch one `orch-review` scout (`<core>/skills/orch-review/SKILL.md`), using a harness from a different vendor than Work's so the reviewer never shares the maker's vendor, to audit the Work branch detached and read-only.

- **Input:** the exact branch name and reviewed commit, and the captain's original bounded request as the intended outcome.
- **Check:** findings with evidence against two sources — the captain's request (does the change do what was asked) and the behavior already on the base branch (does anything outside the requested change regress) — no fix and no delegation; verdict is ready, ready with the listed repairs, or not ready.
- **Guidance domain:** `code`, resolved the same way — apply its Review sections. The target project's own conventions also apply.
- **Saved preference:** harness `codex`, model `gpt-5.6-luna`, effort `xhigh`, same override precedence as Work.

## 3. Repair

If Review's verdict lists any repairs, steer the same Work agent from step 1 with the report: the numbered repairs to make, any finding deliberately left unaddressed and why, and no other changes. No second Review. If Review's verdict is clean, skip straight to delivery.

## 4. Deliver

The target project's own delivery mode lands the (possibly repaired) branch. This workflow adds no further gate.

---

Manual-only: this workflow runs only when the captain names it, by its slash command or by reading this file from its resolved library path.
