This is one Orchflows Work assignment: author the complete library yourself in this worktree. Do not delegate to subagents or other agents; one agent owns this result.

## Read first, then apply the Make sections

The installed Orchflows core is CORE_PATH (read-only; never edit it). Read these files completely before writing anything:

- CORE_PATH/docs/architecture.md (a library's layout, model and effort, guidance selection, invariants)
- CORE_PATH/docs/firstmate.md (how each Work and Review becomes a FirstMate agent; delivery modes; the backlog note)
- CORE_PATH/skills/orch-work/SKILL.md, CORE_PATH/skills/orch-review/SKILL.md, CORE_PATH/skills/orch-dynamic-workflow/SKILL.md (the primitives your workflow composes; match their length and style)
- CORE_PATH/skills/orch-build-workflow/SKILL.md (what a saved workflow must contain)
- CORE_PATH/docs/hosts.md (manual-only workflows)
- CORE_PATH/guidance/orchflows.md and CORE_PATH/guidance/writing.md: apply their Make sections to everything you write.
- CORE_PATH/guidance/code.md: the parent domain your guidance extension specializes.

## Deliverable

Create libraries/mixed-build/ in this worktree with exactly this layout:

- plugin.json, .claude-plugin/plugin.json, .codex-plugin/plugin.json: name mixed-build, version 1.0.0, skills "./skills/", a one-sentence description. The three manifests must agree on name and version.
- README.md: what the workflow does, the phase table with each agent's harness, model and effort, the declared agent count (six agents plus at most three repairs), how the captain runs it (by name only), and dependencies (none beyond the Orchflows FirstMate core).
- references/library-context.md: the guidance domains the workflow requires (code, code.cli, writing) and that it depends on the Orchflows FirstMate core.
- guidance/code.cli.md: a specialization of the core code domain for command-line tools, with a Make section and a Review section. State only the differences from code.md: for example explicit exit codes, stdin and file input handling, machine-readable output, a --help that documents every option, and errors on stderr. Keep it under 120 words.
- skills/feature/SKILL.md: frontmatter with name feature, a description that begins with "Manual:" and says the workflow runs only when the captain names it, and disable-model-invocation: true. The body is the composition, about 200 words or fewer, written for the FirstMate primary session that loads it. It composes the core primitives by name (orch-work, orch-review) and never restates their contracts. It declares three phases in order, each with its Work assignment, its Review assignment, one repair pass, the guidance domains, and the saved model and effort preference beside each assignment:
  - spec: Work is a read-only scout, codex gpt-5.6-luna at xhigh, that writes a design and an acceptance checklist into its report. Review is a scout, claude claude-sonnet-5 at xhigh, applying the writing and code Review sections to the spec.
  - implement: Work is a ship in the project's delivery mode, claude claude-sonnet-5 at xhigh, implementing the spec with tests. Review is a scout, codex gpt-5.6-luna at xhigh, applying the code and code.cli Review sections to the branch.
  - docs-qa: Work is a ship, codex gpt-5.6-luna at xhigh, that writes the README and usage docs and runs the acceptance checklist. Review is a scout, claude claude-sonnet-5 at xhigh, that checks the delivered artifact against the spec's acceptance checklist and applies the writing Review section.
  The skill must say: the current request overrides these saved preferences field by field; each phase lands through the project's delivery mode before the next phase starts; the captain records the phase and task IDs in the backlog item note; the spec report is the input to the implement phase and the acceptance checklist is the input to the final Review.
- trials/request.md: a representative request (a small command-line tool), and trials/expected-behavior.md: the agents, order and outputs a correct run produces.

## Checks before you finish

- Every relative link in the library resolves inside libraries/mixed-build/.
- All three manifests parse as JSON and agree.
- python3 -B CORE_PATH/scripts/orchflows.py resolve mixed-build --home "$PWD" --skill feature prints the skill path (run it from your worktree root; it reads libraries/ only).
- The skill body is 200 words or fewer excluding frontmatter; report the count.
- Nothing outside libraries/mixed-build/ changes.

Commit everything on your branch with a clear message, then follow this brief's local-only definition of done exactly. Do not edit .local/, do not run setup, do not touch other projects.