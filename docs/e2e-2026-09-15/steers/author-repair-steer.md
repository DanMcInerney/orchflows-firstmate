Repair pass for fm/orch-author-1. An independent review (report: /tmp/orchflows-e2e/home/data/orch-author-review-1/report.md) returned the verdict "ready with repairs". Make exactly these repairs on your existing branch, keeping the skill body at 200 words or fewer:

1. In skills/feature/SKILL.md add code.cli to the spec phase's Work guidance and to its Review guidance. Mirror that wherever README.md or trials/expected-behavior.md list the spec phase's guidance.
2. Reword the inputs sentence so the acceptance checklist is input to both docs-qa Work and docs-qa Review, not only the Review.
3. Fold the exact trigger phrases into the frontmatter description so it ends with: Only run when the captain says "run mixed-build" or "run the feature workflow".
4. Make the root plugin.json identical to .codex-plugin/plugin.json, carrying the interface block, to match the core package's convention.

Do not act on the review's finding 1 (no trial record): the captain runs the trial through FirstMate after this branch lands and will attach its record to the library afterwards. Re-run the resolve check and the word count, commit the repairs on your branch, and then append a fresh "done: ready in branch fm/orch-author-1" line to your status file.