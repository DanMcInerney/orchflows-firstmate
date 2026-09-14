# Worker harnesses

Only FirstMate running in Herdr is in scope. Claude Code and Codex CLI are worker harnesses selected and launched by FirstMate. Neither direct host-native execution nor Codex Desktop is a mode of this package. **The [execution gate](architecture.md#firstmate-execution-gate) admits one experimental read-only Work or explicitly authorized Review after actual controller and attachment checks. Review is currently Linux-only and requires explicit-audit policy.** Other workflows remain gated.

## Register and refresh

Setup generates `orchflows-firstmate-home` catalogs in the dedicated package home; the source checkout has `orchflows-firstmate-local` catalogs. They describe the package namespace, not a functioning FirstMate installation. Host registration alone cannot provide the missing adapter. Do not enable these development skills as a general host workflow fallback.

The experimental FirstMate controller attaches a complete fork snapshot before a root's first launch; invoke the [client](firstmate-client.md) from that exact retained snapshot. This is not a host installer or an operational readiness check. Broader installation must still provision dependencies and discovery for each worker environment and verify launch/relaunch behavior. Normal Orchflows registrations are outside this package's ownership.

## Loading

Resolve links from the containing file, scripts from the loaded skill's directory and task inputs/outputs from the assigned workspace. Copying only skill folders breaks package-relative dependencies. The task must identify this fork's exact package and library roots. The CLI's `orchflows` alias does not redirect native host skill discovery; existing `orchflows:*` library calls require adaptation before certification.

## Model and effort

Preserve the [assignment preference rules](architecture.md#model-and-effort). Stage 1 inherits the root's harness, model and effort, and accepts no override fields. Requests needing different settings must refuse. Broader model/effort routing remains a migration requirement. A prompt containing a model name is not a model selection. Direct work or worker reuse is valid only when its effective settings satisfy the assignment.

The package does not alter global concurrency by default. Explicit `setup --concurrency N` retains the upstream host-setting utility for an operator, with the same shared `.orchflows.lock` and backup format to coordinate those shared files. This setting does not establish FirstMate task-group capacity; FirstMate must account for all component tasks.

## Isolation

FirstMate must allocate component workspaces and govern branch ownership, result integration and cleanup. Workers cannot allocate or control Herdr endpoints. Work and Review must use their task-assigned write/read scope; review must name the exact candidate. Old writer termination and result retention must be established before reuse or teardown. Native isolation instructions below are retained as migration evidence and are inactive in this fork.

## Upstream migration baseline (inactive)

The quoted upstream host documentation records the native implementation being replaced. Its commands, native dispatch controls and support statements do not define supported behavior for this fork.

> # Hosts
>
> CLI commands checked 2026-09-12: Codex 0.144.0, Claude Code 2.1.233. Host behavior is version-dependent.
>
> ## Register and refresh
>
> Setup writes catalogs; register the home, install each library, then start a new session. Keep one enabled core installation. If edits are missing, check the installed cache and restart. Following an unregistered `SKILL.md` by absolute path does not register it.
>
> | | Codex | Claude Code |
> | --- | --- | --- |
> | Register home | `codex plugin marketplace add <home>` | `claude plugin marketplace add <home>` |
> | Install | `codex plugin add <lib>@orchflows-home` | `claude plugin install <lib>@orchflows-home --scope user` |
> | After editing a library | bump manifest versions; `codex plugin add <lib>@orchflows-home` | bump manifest versions; `claude plugin marketplace update orchflows-home`; `claude plugin update <lib>@orchflows-home` |
> | Invoke | `$<lib>:<skill>` or `/skills` | `/<lib>:<skill>` |
> | Core development | register the checkout's `orchflows-local` catalog; install `orchflows@orchflows-local` | same, or `claude --plugin-dir <checkout>` |
> | Concurrency key written by setup | `[agents] max_threads` in `$CODEX_HOME/config.toml` or `~/.codex/config.toml`: open spawned threads, primary excluded | `env.CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` in `$CLAUDE_CONFIG_DIR/settings.json` or `~/.claude/settings.json`: parallel read-only tools and subagents |
> | Custom agent definitions | `.codex/agents/*.toml`, `~/.codex/agents/` | `.claude/agents/*.md`, `~/.claude/agents/` |
>
> Concurrency takes effect in new sessions; higher-precedence settings may override it. Current Codex documentation names `max_concurrent_threads_per_session`; setup's `max_threads` remains a supported alias. [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents#global-settings), [Claude concurrency](https://code.claude.com/docs/en/env-vars).
>
> Registration references: [Codex plugins](https://developers.openai.com/plugins/build/plugins), [Claude plugins](https://code.claude.com/docs/en/plugins).
>
> ## Loading
>
> Resolve links from the containing file, scripts from the loaded skill's directory, and inputs/outputs from the assignment workspace. Copying only skill folders breaks package-relative links such as `../../guidance/`. `${CLAUDE_SKILL_DIR}` is Claude-only; `context: fork` launches a child context without filesystem isolation. Orchflows built-ins use the current context. [Codex skills](https://developers.openai.com/codex/skills), [Claude skills](https://code.claude.com/docs/en/skills).
>
> ## Model and effort
>
> Apply the [resolved assignment choices](architecture.md#model-and-effort) through the controls exposed by the current host. Unset controls use native defaults, which may differ from the coordinator's settings. Writing a model name in a child's prompt does not select it.
>
> | Host | Native controls |
> | --- | --- |
> | Codex | Use the spawn tool's model and reasoning-effort fields when exposed, such as `model` and `reasoning_effort`. If full-history forks disallow overrides, use a fresh or partial context fork. |
> | Claude Code | The Agent tool supports a model override. Effort is configured in an agent definition's `effort` field; use a definition that supplies the requested setting when the invocation has no effort field. Unset effort inherits the session's setting. |
>
> Check native configuration when it can override a launch choice. Codex custom agent files can override explicit spawn values; absent explicit values, subagent defaults precede parent settings. Selecting a different model without effort can select that model's default effort. Claude precedence can also depend on environment overrides and host version. Use only supported model/effort combinations and report an unhonored request before dependent work. Do not create standing host configuration as an implicit fallback.
>
> Reuse a worker only if the host can honor the repair assignment's settings. If the continuation tool cannot change them, launch a fresh worker with the joined result and repair context. [Codex agent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents), [Claude agent configuration](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields).
>
> ## Isolation
>
> When a child needs isolation, use a worktree at the intended revision. Claude supports `isolation: worktree`; confirm the starting commit, since the default may use the remote default branch. If Codex's child tool has no workspace argument, create a worktree and direct every child operation there:
>
> ```sh
> git worktree add -b codex/task-candidate ../task-candidate <commit>
> git worktree add --detach ../task-review <candidate-commit>
> ```
>
> Transfer needed uncommitted files explicitly. Continue existing children through native messaging. Integrate through the host or Git, check the combined result, then clean up. Non-repository work uses host workspace/artifact access. [Codex worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees), [Claude worktrees](https://code.claude.com/docs/en/worktrees).
