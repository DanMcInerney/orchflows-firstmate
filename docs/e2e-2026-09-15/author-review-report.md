# Review: mixed-build workflow library (feature workflow)

**Reviewed commit:** `79b2d6c017c7f058c5f334abb1ba961cf931130b` on branch `fm/orch-author-1` (detached checkout, worktree `/home/danhm/.treehouse/orchflows-home-1fccc7/2/orchflows-home`). This is the only commit adding `libraries/mixed-build/` on top of the seed commit `75c1b5e`.

I am the fresh, independent reviewer named in the brief: I did not make this candidate, I made no edits, and I ran no repairs or subagents. Everything below is read-only inspection plus the one requested `resolve` invocation.

## What I did

1. Read the core reference docs named in the brief: `docs/architecture.md`, `docs/firstmate.md`, `docs/hosts.md`, `skills/orch-work/SKILL.md`, `skills/orch-review/SKILL.md`, `skills/orch-dynamic-workflow/SKILL.md`, `skills/orch-build-workflow/SKILL.md`, and `guidance/orchflows.md`, `guidance/writing.md`, `guidance/code.md` (applying their Review sections).
2. Fetched and detached-checked-out `fm/orch-author-1`.
3. Read every file under `libraries/mixed-build/`: `plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `README.md`, `references/library-context.md`, `guidance/code.cli.md`, `skills/feature/SKILL.md`, `trials/request.md`, `trials/expected-behavior.md`.
4. Verified frontmatter, manifest agreement, and all relative links by inspection and a small script (word count) and `find`.
5. Ran `python3 -B .../scripts/orchflows.py resolve mixed-build --home "$PWD" --skill feature`, plus two extra `--resource` resolutions (`guidance/code.cli.md`, `references/library-context.md`) and a `doctor` run, from the worktree root.
6. Compared the library against the core's own manifest shape (`orchflows-firstmate/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`).
7. Passed the `captain-hold-lifecycle` completion gate: `FM_HOME=/tmp/orchflows-e2e/home bin/fm-captain-hold.sh complete orch-author-review-1 --none` → `complete: orch-author-review-1 captain-call inventory reviewed` (exit 0). None of the findings below are captain-only decisions; they are ordinary repair-shaped findings, so `--none` was correct per the lifecycle skill's line 48 ("Resolved findings, recommendations that need no captain choice... do not create held tasks").

## Findings, ordered by impact

### 1. (High) No evidence the mandatory trial was ever run through FirstMate — the library's own behavioral claims are unverified

`orch-build-workflow/SKILL.md` (core) states verification for any new workflow: *"run the workflow through FirstMate on a bounded request in a disposable project... Return trial findings to the maker before final review; give the final reviewer the candidate and trial record."* `docs/architecture.md` §Invariants adds: *"Establish behavior with a real bounded trial through FirstMate. Valid frontmatter proves no behavior; unexercised failure paths remain untested."*

The commit `79b2d6c` only adds the trial **materials** — `trials/request.md` (the bounded ask: build a `wordcount` CLI) and `trials/expected-behavior.md` (a prediction of what a "correct run" should dispatch). There is no trial **record** anywhere in the repo (no second commit, no `.orch/` run state, no report) showing `feature` was actually dispatched through FirstMate and that the real six-agent sequence matched the prediction. I was handed only the candidate tree, not a trial record, which the build-workflow skill says the final reviewer should receive.

`guidance/orchflows.md`'s Review section, which I was told to apply, says directly: *"Judge behavioral claims against observed use."* `trials/expected-behavior.md` is entirely unobserved — it is a spec of intended behavior, not evidence one occurred.

**Recommendation:** before treating this library as final, run `feature` once through FirstMate on the `wordcount` request in a disposable project, and attach the resulting record (agent IDs, actual guidance/model/effort used, any deviations from `expected-behavior.md`) alongside the trial materials, per the build-workflow's own verification step.

### 2. (Medium-High) `spec` Work's declared guidance omits `code.cli`, which its own trial expectation assumes it needs

`skills/feature/SKILL.md:9`:
> `**spec** — Work: read-only scout, codex gpt-5.6-luna, xhigh; writes a design and acceptance checklist into its report. Guidance: writing, code.`

Guidance for `spec` Work is `writing, code` only — `code.cli` is not selected for this phase. Compare with `trials/expected-behavior.md:5`, written by the same author, describing what a correct `spec` Work should produce:
> *"...investigates the project's CLI conventions and produces a report containing a design for `wordcount` (flags, input handling, output format) and an acceptance checklist (e.g., ... "`--json` emits valid JSON", "`--help` documents every flag", "exit code 0 on success, nonzero on a missing file")."*

Those acceptance-checklist items (exit codes, `--json`/machine-readable output, `--help` coverage) are precisely the domain `guidance/code.cli.md` covers ("Use explicit, documented exit codes... Offer a machine-readable output mode... Ship a `--help` that documents every option..."). The phase meant to originate the CLI-specific acceptance checklist is not given the one guidance file that states those CLI conventions, while `implement` and `docs-qa` (lines 11, 13) both are. This is an internal inconsistency between the SKILL.md's own guidance selection and the same library's trial expectations, and risks a spec checklist that is thinner on CLI conventions than the library assumes.

**Recommendation:** add `code.cli` to `spec`'s Work guidance list (and its Review guidance, if the design should be checked against CLI convention too), or, if the omission is deliberate, explain in `expected-behavior.md`/`SKILL.md` why CLI-convention criteria are expected from a phase that isn't given `code.cli` guidance.

### 3. (Medium) The acceptance checklist's handoff into `docs-qa` Work is not named as an input, even though that phase is described as running it

`skills/feature/SKILL.md:13`:
> `**docs-qa** — Work: ship, codex gpt-5.6-luna, xhigh; writes the README and usage docs, runs the acceptance checklist.`

`skills/feature/SKILL.md:15` (the line that states inputs):
> `The spec report is input to implement; its acceptance checklist is input to the docs-qa Review.`

The checklist is explicitly named as an input only for **docs-qa Review**, never for **docs-qa Work** — yet line 13 says docs-qa Work itself "runs the acceptance checklist." A FirstMate primary composing docs-qa Work's brief strictly from this text could omit the checklist from that brief (since it isn't listed as one of docs-qa Work's inputs) and only remember to carry it into the Review brief. This is exactly the kind of ambiguity Check 1 in the brief asks to be quoted.

**Recommendation:** reword line 15 to state the checklist is input to both docs-qa Work and docs-qa Review, e.g. *"the spec report is input to implement; its acceptance checklist is input to both docs-qa Work and docs-qa Review."*

### 4. (Low-Medium) The manual-only trigger doesn't fully satisfy `hosts.md`'s Codex convention

`docs/hosts.md:29`: *"Codex has no verified equivalent [to `disable-model-invocation`]; begin the description with `Manual:` and **state the exact trigger** so it never matches an ordinary request."*

`skills/feature/SKILL.md:3` frontmatter description:
> `"Manual: builds a small software feature through spec, implement and docs-qa phases with cross-vendor Review. Runs only when the captain names this workflow."`

This begins with `Manual:` (satisfies Check 3 literally) but "Runs only when the captain names this workflow" is a general condition, not an exact trigger phrase — contrast with `README.md:22`, which does give one: *"say 'run mixed-build' or 'run the feature workflow.'"* Since Codex has no frontmatter flag to fall back on and depends entirely on this description text to avoid auto-matching, the vaguer wording is weaker protection on that host than intended.

**Recommendation:** fold the README's exact trigger phrases into the frontmatter description, e.g. `"Manual: ... Only run when the captain says 'run mixed-build' or 'run the feature workflow.'"`

### 5. (Low) Root `plugin.json` doesn't mirror the core's own root-manifest convention

The core's own `plugin.json` (root) is identical to its `.codex-plugin/plugin.json` (both carry the full `interface` block), while `.claude-plugin/plugin.json` is the reduced version. `libraries/mixed-build/plugin.json` (root) is instead identical to its `.claude-plugin/plugin.json` (both reduced, no `interface` block), while `.codex-plugin/plugin.json` alone carries `interface`. Functionally harmless — `resolve` succeeds regardless (see Check 6 below) — but it's an inconsistent convention versus the one example this codebase ships (the core package itself), and worth normalizing if root `plugin.json` is meant to be host-neutral duplicate of one specific manifest.

### 6. (Low, informational) Body word count is 198/200 — passes, with almost no margin

Measured via `body.split()` after stripping YAML frontmatter: **198 words**, under the 200-word cap in Check 3, but only two words of margin. Any future edit to `skills/feature/SKILL.md`'s body should re-measure.

## Checks confirmed passing (no findings)

- **Frontmatter (Check 3):** `name: feature` ✓, description begins `"Manual:` ✓, `disable-model-invocation: true` ✓, body 198/200 words ✓ (see Finding 6 for margin note).
- **Manifest agreement (Check 4):** `plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` all agree on `name: "mixed-build"` and `version: "1.0.0"`.
- **Relative links resolve (Check 4):** every link I found resolves inside the library: `skills/feature/SKILL.md:7` → `../../references/library-context.md` → `libraries/mixed-build/references/library-context.md` (exists); `references/library-context.md` → `../guidance/code.cli.md` and `../skills/feature/SKILL.md` (both exist); `README.md` → `skills/feature/SKILL.md` and `references/library-context.md` (both exist); `trials/expected-behavior.md` → `request.md` (exists).
- **`guidance/code.cli.md` shape (Check 4):** has both `## Make` and `## Review` sections, and states only differences from `code.md` ("Specializes the core `code` domain for command-line tools. States only the differences; the parent's baseline still applies.") — matches `guidance/orchflows.md`'s Review requirement that "Specializations state differences from their parents."
- **README declarations (Check 5):** states the agent count explicitly — *"six agents (three Work, three Review), plus at most three repairs"* — and how the captain runs it — *"say 'run mixed-build' or 'run the feature workflow.'"*
- **`resolve` (Check 6):** run from the worktree root:
  ```
  $ python3 -B /tmp/orchflows-e2e/home/projects/orchflows-home/.local/packages/orchflows-firstmate/scripts/orchflows.py resolve mixed-build --home "$PWD" --skill feature
  {"name":"mixed-build","version":"1.0.0","package_root":".../libraries/mixed-build","skill_path":".../libraries/mixed-build/skills/feature/SKILL.md","runtime_python":".../.local/runtime/bin/python"}
  ```
  Exit 0. I additionally resolved `--resource guidance/code.cli.md` and `--resource references/library-context.md`; both succeeded (exit 0). `doctor --home "$PWD"` reports `mixed-build` correctly discovered under `libraries`; its "incomplete" status and catalog-staleness warnings are because this scratch worktree's `.local/packages/orchflows-firstmate` core isn't installed/setup here — an environment condition of the worktree, not a defect in `mixed-build` itself.
- **Vendor alternation (captain's intent):** spec Work=codex/claude-Review, implement Work=claude/codex-Review, docs-qa Work=codex/claude-Review — every reviewer is a different vendor from its phase's maker, and every model/effort pair matches "claude claude-sonnet-5 xhigh" / "codex gpt-5.6-luna xhigh" exactly as the brief specified. Preferences are saved beside each assignment in both `SKILL.md` and mirrored in `README.md`'s table, and `SKILL.md:15` correctly states the current request overrides them field by field, matching `docs/architecture.md`'s resolution order.
- **No restated primitives (Check 2):** `SKILL.md` never restates FirstMate spawn mechanics, delivery-mode detail, or the backlog-note format (`orchflows: <workflow> phase=... work=... review=... repair=... guidance=...` from `firstmate.md:59`) — it just names "backlog item note," "project's delivery mode," "orch-work," "orch-review," and "one repair pass," composing by name rather than duplicating. One minor stylistic gap: `orch-work`/`orch-review` are named as plain code spans, not markdown links (unlike `orch-build-workflow/SKILL.md`'s `[orch-dynamic-workflow](...)` style) — harmless since both are core skills the primary already has loaded, but inconsistent with the one other example in this codebase.

## Verdict

**Ready with the listed repairs.** The artifact is structurally sound — correct frontmatter, agreeing manifests, resolving links, a properly-scoped `code.cli` specialization, a clear README, correct and fully-saved model/effort/vendor-alternation preferences, and a clean `resolve` — and would very likely dispatch correctly as written. But before calling this final: (1) run the mandatory trial through FirstMate and attach its record — Finding 1 — since none of this review's static checks substitute for `guidance/orchflows.md`'s "judge behavioral claims against observed use"; (2) add `code.cli` to `spec`'s guidance or explain its absence — Finding 2; (3) clarify that the acceptance checklist is also input to docs-qa Work, not just docs-qa Review — Finding 3. Findings 4–6 are minor polish, worth fixing but not blocking.
