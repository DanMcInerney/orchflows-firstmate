# Architecture

## Two primitives

- [orch-work](../skills/orch-work/SKILL.md): a fresh FirstMate agent makes a result under chosen guidance.
- [orch-review](../skills/orch-review/SKILL.md): a fresh FirstMate scout who did not make it reviews without fixing.

All delegation goes through these primitives. FirstMate owns dispatch, execution profiles, brief, spawn, worktree, watcher, steering, relaunch, recovery, cancellation and delivery. Orchflows adds no runtime, scheduler or workflow language. Loading a `SKILL.md` applies its instructions in the caller's context, which is the FirstMate primary session; it does not launch an agent. Composing workflows add only their own decisions and supply each agent's assignment and context. [FirstMate](firstmate.md) records how each primitive maps onto FirstMate's owners and checkpoints.

The coordinator never edits a project, so the smallest workflow is one Work and one Review. Choose planning, delegation and isolation from unknowns, dependencies and edit conflicts. Run independent work concurrently.

## Where things live

Give each instruction and mechanism one owner; reference shared facts. READMEs address humans; other live documentation addresses agents.

| Concept | Owner / location |
| --- | --- |
| Request: question, dates, sources, bounds, output location | Captain's request |
| Harness, model, effort and quota | FirstMate's ordinary dispatch; [model and effort](#model-and-effort) defines the workflow boundary |
| Coordination: composition, control flow, agent count | Composing workflow's `SKILL.md` |
| Workflow state in flight: phase and task IDs | FirstMate backlog item note |
| Quality criteria, including source-specific preferences | `guidance/<domain>.md` |
| Shared contracts and operational knowledge | Library `references/`; skill-local `references/` for one consumer |
| Package dependencies and guidance requirements | `references/library-context.md`, reused by entrypoints |
| Resolved paths and request context | Outermost entrypoint; passed through composed calls and into every brief |
| Deterministic mechanics | Owning skill's `scripts/`, with sibling `tests/`; core CLI in `scripts/` |
| Package identity | Root `plugin.json` |
| Agent execution, isolation, steering, recovery, delivery | FirstMate; [firstmate.md](firstmate.md) |
| Host registration and invocation policy | [hosts.md](hosts.md) |
| Setup, updates and home paths | [home.md](home.md) |
| Task records and their interpretation | [history.md](history.md) |
| Run outputs and evidence | Worker worktree, scout report or delivered branch, never a package |

## Invocation

[orch-dynamic-workflow](../skills/orch-dynamic-workflow/SKILL.md) is the automatic fallback when the request names no workflow; the `captain.md` block makes it FirstMate's default. Every other core skill and every saved workflow in `~/.orchflows-firstmate/libraries/` is manual-only: the captain runs one when the request names it, by its slash command or by reading its `SKILL.md` from the resolved path. A skill that a running workflow links is read as a file and needs no invocation. When creating or copying a workflow, write and verify the [host invocation settings](hosts.md#invocation-policy) for every skill, including helpers.

## Model and effort

FirstMate owns harness, model and effort for every Work, Review and repair. Follow its installed intake, dispatch and recovery procedures; FirstMate resolves the concrete launch settings before each spawn. Its handling of the current request, local configuration, quota and adapter capabilities applies unchanged. Describe each assignment's purpose, inputs, uncertainty and checks so FirstMate can judge the work.

Dynamic and saved workflows define no harness, model, effort or vendor-selection preferences, including in composed steps and repairs. Ignore those settings in older saved workflows and remove them when updating the workflow. Do not save the authoring session's execution settings. Execution preferences belong in the captain's current request or FirstMate's own configuration, handled by FirstMate. Behavioral corrections remain in guidance.

## Guidance selection

Guidance records domain preferences in `## Make` and `## Review`; omit empty sections. Apply Make when producing and Review when assessing. Workflows name required domains; select `orchflows` for authoring workflows, guidance or libraries. A domain being extended is source material for its author.

Resolve once at the outer entrypoint, including a leaf invoked alone:

1. Select independent domain names, such as `writing`, `visual-design`, `short-video.marketing`.
2. For each name, visit dotted prefixes from general to specific. At each prefix, read core then selected libraries in caller-supplied order. Example: `short-video` across packages, then `short-video.marketing` across packages.
3. Keep each resolved file once, in first-use order. More specific guidance wins within its domain; independent domains compose.
4. Missing implicit parents are allowed; library-only domains are valid. An explicit selection must exist in core or a selected library; report a gap and block dependent work otherwise. Use general guidance for unfamiliar sites or genres.
5. Resolve package dependencies through supplied roots or the home's [`libraries/<name>/`](home.md#libraries). Pass absolute paths and request context unchanged into every brief and composed skill; workers read guidance as files and need no plugin. Extend only for new dependencies.

Selected libraries may supply removable model corrections under existing domain names. Normal specificity applies; model names are not domain specializations.

## Three roots

| Root | Contents / editing owner |
| --- | --- |
| Core checkout | Built-in `skills/orch-*/`, guidance, docs, CLI, tests; installed as the plugin and named as `<core>` in `captain.md` |
| Home `~/.orchflows-firstmate` | Your saved libraries and their catalogs per [home.md](home.md); a local-only FirstMate project |
| Project workspace | Task outputs, in FirstMate worktrees |

Reserve `orch-` for built-ins. Create custom workflows in `~/.orchflows-firstmate/libraries/personal/skills/<workflow>/` unless the caller names another library or repository. The author is a Work agent shipping into the home, which is a registered FirstMate project per [home.md](home.md#authoring). Edit the checkout or your library, never a host cache.

Core Markdown links must resolve within the checkout. To update core: edit the checkout, run `python -m unittest discover -s tests`, then [refresh the registration](hosts.md#register-and-refresh).

## A library

```text
<library>/
├── plugin.json                     name, version, skills: "./skills/"
├── .claude-plugin/plugin.json      Claude manifest
├── .codex-plugin/plugin.json       Codex manifest
├── README.md                       composition, agent count, install, dependencies
├── references/                     shared context and contracts
├── guidance/<domain>.md            domain or dotted specialization
├── skills/<skill>/SKILL.md          frontmatter, invocation policy; instructions
├── skills/<skill>/agents/openai.yaml Codex invocation policy and UI metadata
├── skills/<skill>/references/       knowledge used by this skill only
├── skills/<skill>/scripts/          mechanics; sibling tests/
└── trials/                         request.md, expected-behavior.md
```

Skill identity is `<library>:<skill>`. Keep links within the package; reach other packages by resolved paths. Never embed machine-specific paths. Declare runtime dependencies in the README; setup installs none.

## Invariants

- Skills name scripts, inputs and results; scripts own their internals.
- Declare agent counts; extra reviews, loops or repairs require a caller request.
- FirstMate makes no change and holds no workflow state in chat; the backlog note does.
- Report missing work as a gap, never as no-results evidence.
- Establish behavior with a real bounded trial through FirstMate. Valid frontmatter proves no behavior; unexercised failure paths remain untested.
