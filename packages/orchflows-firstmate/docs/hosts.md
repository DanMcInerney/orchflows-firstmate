# Hosts

The FirstMate primary session is the only host that loads these skills. Workers need no registration: their briefs carry absolute guidance and reference paths, which they read as files.

Registration commands checked 2026-09-12: Codex 0.144.0, Claude Code 2.1.233. The trials of 2026-09-15 ran a Claude Code 2.1.269 primary with Claude Code and Codex 0.154 workers. Host behavior is version-dependent.

## Register and refresh

Install the core from the checkout into the harness that runs the primary. Register the home only when you want a saved library by slash command; the captain reads a named workflow from the home's `libraries/` path either way. Start a new FirstMate session after installing. Keep one enabled core installation. Bump the package version in every host manifest before refreshing; Claude Code can reuse its cached copy at an unchanged version. If edits are missing, check the installed cache and restart.

| | Codex | Claude Code |
| --- | --- | --- |
| Install the core | `codex plugin marketplace add <checkout>`; `codex plugin add orchflows-firstmate@orchflows-firstmate-local` | `claude plugin marketplace add <checkout>`; `claude plugin install orchflows-firstmate@orchflows-firstmate-local --scope user`, or `claude --plugin-dir <checkout>` for one session |
| Register the home | `codex plugin marketplace add <home>` | `claude plugin marketplace add <home>` |
| Install a library | `codex plugin add <lib>@orchflows-firstmate-home` | `claude plugin install <lib>@orchflows-firstmate-home --scope user` |
| After editing a library | bump manifest versions; `codex plugin add <lib>@orchflows-firstmate-home` | bump manifest versions; `claude plugin marketplace update orchflows-firstmate-home`; `claude plugin update <lib>@orchflows-firstmate-home` |
| Invoke | `$<lib>:<skill>` or `/skills` | `/<lib>:<skill>` |

`<core>` in `captain.md` is the checkout path. A primary on Pi, omp, Grok or Cursor has no manifest here; give `captain.md` the absolute path of `<core>/skills/orch-dynamic-workflow/SKILL.md` and FirstMate reads skills by path.

Registration references: [Codex plugins](https://developers.openai.com/plugins/build/plugins), [Claude plugins](https://code.claude.com/docs/en/plugins).

## Loading

Resolve links from the containing file, scripts from the loaded skill's directory, and inputs and outputs from the assignment workspace. Copying only skill folders breaks package-relative links such as `../../guidance/`. Orchflows built-ins use the current context. [Codex skills](https://developers.openai.com/codex/skills), [Claude skills](https://code.claude.com/docs/en/skills).

## Invocation policy

Apply the [invocation policy](architecture.md#invocation) per skill; a library manifest does not set it. `orch-dynamic-workflow` opts into automatic selection with `disable-model-invocation: false` in its frontmatter and `policy.allow_implicit_invocation: true` in `skills/<skill>/agents/openai.yaml`. Every other skill carries the manual-only settings below.

| Host | Manual-only setting | Explicit invocation |
| --- | --- | --- |
| Codex | `policy.allow_implicit_invocation: false` in `skills/<skill>/agents/openai.yaml` | `$<library>:<skill>` or the skill picker |
| Claude Code | `disable-model-invocation: true` in `SKILL.md` frontmatter | `/<library>:<skill>` |

Include `interface.display_name` and `interface.short_description` in the Codex metadata. Opting a skill into automatic selection requires changing both settings; refresh the installed plugin afterwards. Claude Code also blocks model calls to a manual-only skill, so the captain reads a named workflow's `SKILL.md` by path when the request does not invoke it, and a primary on Pi, omp, Grok or Cursor reads every skill by path. A Codex primary has not yet exercised this policy. [Codex invocation policy](https://learn.chatgpt.com/docs/build-skills#optional-metadata), [Claude invocation control](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill).

## Model and effort

FirstMate owns [execution settings](architecture.md#model-and-effort), capability discovery and launch controls. Follow its installed `harness-adapters` guidance for dispatch and recovery. This package changes no host settings; FirstMate owns concurrency and quota.

## Isolation

Every agent has its own FirstMate worktree. A reviewer checks the named candidate out detached in its scratch worktree. Joins happen in a Work agent's worktree, never in the primary session. Non-repository work uses the scout report or the delivered branch.
