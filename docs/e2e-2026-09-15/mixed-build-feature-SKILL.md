---
name: feature
description: "Manual: builds a small software feature through spec, implement and docs-qa phases with cross-vendor Review. Only run when the captain says 'run mixed-build' or 'run the feature workflow'."
disable-model-invocation: true
---

Three phases run in order: spec, implement, docs-qa. Each is one `orch-work` assignment, one independent `orch-review` assignment, then one repair pass. Guidance domains: `code`, `code.cli`, `writing`, per [library-context](../../references/library-context.md). Every reviewer is a different vendor from its phase's maker.

**spec** — Work: read-only scout, codex gpt-5.6-luna, xhigh; writes a design and acceptance checklist into its report. Guidance: writing, code, code.cli. Review: scout, claude claude-sonnet-5, xhigh; applies the writing, code and code.cli Review sections to the spec.

**implement** — Work: ship, project delivery mode, claude claude-sonnet-5, xhigh; implements the spec with tests. Guidance: code, code.cli. Review: scout, codex gpt-5.6-luna, xhigh; applies the code and code.cli Review sections to the branch.

**docs-qa** — Work: ship, codex gpt-5.6-luna, xhigh; writes the README and usage docs, runs the acceptance checklist. Guidance: writing, code.cli. Review: scout, claude claude-sonnet-5, xhigh; checks the delivered artifact against the spec's acceptance checklist, applies the writing Review section.

The current request overrides these preferences field-by-field. Each phase lands through the project's delivery mode before the next starts. The captain records phase and task IDs in the backlog item note. The spec report is input to implement; its acceptance checklist is input to docs-qa Work and Review.
