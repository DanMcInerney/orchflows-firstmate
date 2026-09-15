# Hosts

The FirstMate primary session is the only host that loads these skills. Workers need no registration: their briefs carry absolute guidance and reference paths, which they read as files.

CLI commands checked 2026-09-12: Codex 0.144.0, Claude Code 2.1.233. Host behavior is version-dependent.

## Register and refresh

Setup writes catalogs into the home; register the home with the harness that runs the primary, install the core and each library, then start a new FirstMate session. Keep one enabled core installation. If edits are missing, check the installed cache and restart.

| | Codex | Claude Code |
| --- | --- | --- |
| Register home | `codex plugin marketplace add <home>` | `claude plugin marketplace add <home>` |
| Install | `codex plugin add <lib>@orchflows-firstmate-home` | `claude plugin install <lib>@orchflows-firstmate-home --scope user` |
| After editing a library | bump manifest versions; `codex plugin add <lib>@orchflows-firstmate-home` | bump manifest versions; `claude plugin marketplace update orchflows-firstmate-home`; `claude plugin update <lib>@orchflows-firstmate-home` |
| Invoke | `$<lib>:<skill>` or `/skills` | `/<lib>:<skill>` |
| Core development | register the checkout's `orchflows-firstmate-local` catalog; install `orchflows-firstmate@orchflows-firstmate-local` | same, or `claude --plugin-dir <checkout>` |

`<core>` in `captain.md` is the installed package path, `<home>/.local/packages/orchflows-firstmate`. A primary on Pi, omp, Grok or Cursor has no manifest here; give `captain.md` the absolute path of `<core>/skills/orch-dynamic-workflow/SKILL.md` and FirstMate reads skills by path.

Registration references: [Codex plugins](https://developers.openai.com/plugins/build/plugins), [Claude plugins](https://code.claude.com/docs/en/plugins).

## Loading

Resolve links from the containing file, scripts from the loaded skill's directory, and inputs and outputs from the assignment workspace. Copying only skill folders breaks package-relative links such as `../../guidance/`. Orchflows built-ins use the current context. [Codex skills](https://developers.openai.com/codex/skills), [Claude skills](https://code.claude.com/docs/en/skills).

## Manual-only workflows

A custom workflow runs only when the captain names it. On Claude Code, put `disable-model-invocation: true` in its `SKILL.md` frontmatter so the model cannot select it on its own; the captain invokes it by name or reads it by path. Codex has no verified equivalent; begin the description with `Manual:` and state the exact trigger so it never matches an ordinary request. Built-in `orch-*` workflows stay model-invocable, and [orch-dynamic-workflow](../skills/orch-dynamic-workflow/SKILL.md) is the catch-all.

## Model and effort

FirstMate applies the [resolved choices](architecture.md#model-and-effort) as `--harness`, `--model` and `--effort` spawn flags and validates them per harness; an effort a harness cannot take is recorded in task metadata and omitted from the launch. Writing a model name in a brief does not select it. This package changes no host settings; FirstMate owns concurrency and quota.

## Isolation

Every agent has its own FirstMate worktree. A reviewer checks the named candidate out detached in its scratch worktree. Joins happen in a Work agent's worktree, never in the primary session. Non-repository work uses the scout report or the delivered branch.
