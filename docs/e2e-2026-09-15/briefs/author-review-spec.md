This is one Orchflows Review: an independent read-only audit by a fresh agent who did not make the candidate. Do not make or delegate repairs, do not edit any file, do not delegate to subagents. Your deliverable is findings with evidence in your report.

## Candidate

Branch fm/orch-author-1 of this repository. In your scratch worktree run: git fetch --quiet && git checkout --detach fm/orch-author-1 (the branch exists locally in this repository; use git branch -a to find it if fetch reports nothing). Review the tree at that commit, specifically libraries/mixed-build/. Record the commit SHA you reviewed at the top of your report.

## Intended outcome

A reusable Orchflows workflow library named mixed-build with one manual-only workflow, feature, that builds a small software feature in three phases (spec, implement, docs-qa). Each phase is one Work, one independent Review by a fresh agent from the other vendor, and one repair pass. The saved preferences alternate claude claude-sonnet-5 at xhigh and codex gpt-5.6-luna at xhigh so every reviewer differs in vendor from its maker. The library also supplies a code.cli guidance extension. A FirstMate primary session will load skills/feature/SKILL.md and dispatch the agents through the core orch-work and orch-review skills.

## Read first, then apply the Review sections

The installed Orchflows core is CORE_PATH (read-only). Read:

- CORE_PATH/docs/architecture.md (library layout, model and effort, guidance selection, invariants)
- CORE_PATH/docs/firstmate.md and CORE_PATH/docs/hosts.md (delivery modes, the backlog note, manual-only workflows)
- CORE_PATH/skills/orch-work/SKILL.md, orch-review/SKILL.md, orch-dynamic-workflow/SKILL.md, orch-build-workflow/SKILL.md
- CORE_PATH/guidance/orchflows.md, CORE_PATH/guidance/writing.md and CORE_PATH/guidance/code.md: apply their Review sections.

## Checks to perform

1. Would a FirstMate primary that has only the core skills and this SKILL.md know exactly which six agents to dispatch, in what order, with which harness, model, effort, guidance domains and inputs? Quote any ambiguity.
2. Does the skill restate the primitives or FirstMate's runtime instead of composing them by name? Flag duplicated instructions.
3. Frontmatter: name feature, description begins with "Manual:", disable-model-invocation: true. Body word count (excluding frontmatter) at most 200.
4. The three manifests agree on name and version; all relative links resolve inside the library; guidance/code.cli.md has Make and Review sections and states only differences from code.md.
5. The README declares the agent count and how the captain runs the workflow.
6. Run: python3 -B CORE_PATH/scripts/orchflows.py resolve mixed-build --home "$PWD" --skill feature from your worktree root and report the result.
7. Anything else that would make the workflow fail or mislead when actually run.

Write the report at the path this brief names for a scout report. Order findings by impact, each with file and line references, and end with a verdict: ready, ready with the listed repairs, or not ready. Then follow the scout definition of done.