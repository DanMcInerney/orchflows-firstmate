# Architecture

## FirstMate execution gate

**The client supports one experimental read-only Work or independent Review component per attachment.** The [client contract](firstmate-client.md) requires an actual matching FirstMate controller, a current normal root scout generation and the exact retained fork snapshot. Every dispatch validates these inputs. Review requires a Linux attachment admitted with primitive Review and review policy explicit-audit; it cannot be requested through a Work attachment. Broader Work, composed workflows, Dynamic, Build and SelfImprove remain blocked; stop before their work, delegation, repairs or trials. Reading documentation and using package setup, resolve, doctor and read-only transcript tools remain available. A FirstMate environment variable, a discoverable host plugin, an available native Agent/spawn tool or package `status: ready` does not satisfy this gate. There is no native fallback and no direct Claude/Codex mode.

The target is FirstMate running in Herdr, with Claude Code and Codex CLI as worker harnesses. The root crewmate composes the requested workflow. Work and Review each request one FirstMate-owned component through protocol version 1, with scopes `local-readonly-work` and `local-readonly-review` respectively; it inherits the root's harness/model/effort. Only FirstMate controls Herdr endpoints, scheduling, workspaces, recovery and cancellation. The package calls its task-group controller, never Herdr or other fleet lifecycle commands directly. FirstMate owns root delivery and merge authority; a component result is not root completion.

The experimental attachment binds durable root identity, a complete package snapshot and a clean local input commit. The request contains only `request_id` and `assignment`; FirstMate owns the reservation and retained result. Standalone Review is an explicitly authorized audit of that clean input commit; it does not review a writer's later dirty state or add a delivery gate. Broader dispatch still needs workspace/output controls, model/effort overrides, composition-level review policy, composition, cancellation and reconciliation of old writers before replacement work. The client must refuse unsupported requirements explicitly. Its package tests do not establish an operational worker runtime.

A selected Orchflows independent review remains an explicit deliverable. Dynamic workflow keeps one final independent review and one repair pass; it cannot silently remove that review or add an unauthorized extra gate to FirstMate delivery. FirstMate must authorize the selected composition and stage before it can run.

## Two primitives

- [orch-work](../skills/orch-work/SKILL.md): a fresh FirstMate component task will make a result under chosen guidance.
- [orch-review](../skills/orch-review/SKILL.md): a fresh FirstMate component task whose worker did not make the candidate will review without fixing.

All workflow delegation goes through these primitives and the required FirstMate seam. Orchflows adds composition and guidance, with no separate scheduler or endpoint manager. Loading a `SKILL.md` does not launch a task. The contracts below define the intended migration; execution remains subject to the gate above.

Choose planning, delegation and isolation from unknowns, dependencies and edit conflicts. Run independent work concurrently.

## Where things live

Give each instruction and mechanism one owner; reference shared facts. READMEs address humans; other live documentation addresses agents.

| Concept | Owner / location |
| --- | --- |
| Request and defaults: question, dates, sources, bounds, model, effort, output location | Caller prompt; [model and effort](#model-and-effort) covers saved preferences |
| Coordination: composition, control flow, agent count | Composing workflow's `SKILL.md` |
| Quality criteria, including source-specific preferences | `guidance/<domain>.md` |
| Shared contracts and operational knowledge | Library `references/`; skill-local `references/` for one consumer |
| Package dependencies and guidance requirements | `references/library-context.md`, reused by entrypoints |
| Resolved paths and request context | Outermost entrypoint; pass through composed calls |
| Deterministic mechanics | Owning skill's `scripts/`, with sibling `tests/`; core CLI in `scripts/` |
| Package identity | Root `plugin.json` |
| Native skill discovery | Host manifests and catalogs per [hosts.md](hosts.md) |
| Host registration, execution and isolation facts | [hosts.md](hosts.md) |
| Setup, updates and home paths | [home.md](home.md) |
| Transcript access and interpretation | [history.md](history.md) |
| Run outputs and evidence | Caller workspace, never a package |

## Model and effort

Model and effort are optional choices for work, review or a named assignment. Resolve each setting separately: current caller instructions override saved workflow preferences; within either source, the named assignment overrides the operation default. Leave unspecified controls unset for FirstMate worker routing to resolve. Keep the caller's choices and their scope with request context through composed workflows.

Record saved preferences beside the relevant assignments only when the user asks the generated workflow to use them. The authoring session's settings do not become workflow defaults. Plain language is sufficient; no model file or role registry is required. Behavioral corrections remain in guidance.

Apply these choices to every assignment, including repairs. Direct coordinator work or reuse of an existing worker is valid only when it honors that assignment's settings; otherwise use a fresh worker. The primitives apply choices through [FirstMate worker launch controls](hosts.md#model-and-effort); report an unsupported setting as a gap instead of substituting another value.

## Guidance selection

Guidance records domain preferences in `## Make` and `## Review`; omit empty sections. Apply Make when producing and Review when assessing. Workflows name required domains; select `orchflows` for authoring workflows, guidance or libraries. A domain being extended is source material for its author.

Resolve once at the outer entrypoint, including a leaf invoked alone:

1. Select independent domain names, such as `writing`, `visual-design`, `short-video.marketing`.
2. For each name, visit dotted prefixes from general to specific. At each prefix, read core then selected libraries in caller-supplied order. Example: `short-video` across packages, then `short-video.marketing` across packages.
3. Keep each resolved file once, in first-use order. More specific guidance wins within its domain; independent domains compose.
4. Missing implicit parents are allowed; library-only domains are valid. An explicit selection must exist in core or a selected library; report a gap and block dependent work otherwise. Use general guidance for unfamiliar sites or genres.
5. Resolve package dependencies from the task's pinned complete package set using supplied roots or the [home CLI](home.md#resolve). Native unqualified skill discovery must not substitute the normal Orchflows core. Pass absolute paths and request context unchanged to composed skills and primitives; extend only for new dependencies.

Selected libraries may supply removable model corrections under existing domain names. Normal specificity applies; model names are not domain specializations.

## Three roots

| Root | Contents / editing owner |
| --- | --- |
| Core checkout | Built-in `skills/orch-*/`, guidance, docs, CLI, tests, example libraries; orchflows developers |
| Home `~/.orchflows-firstmate` | User-owned libraries and runtime; setup-managed core per [home.md](home.md) |
| Project workspace | Task outputs |

Reserve `orch-` for built-ins. Author custom workflows in the task-assigned checkout or an explicitly authorized output location. Publishing into `~/.orchflows-firstmate/libraries/personal/skills/<workflow>/` is a separate authorized delivery step; a worker must not implicitly write a user home. Edit source, never managed core or host caches.

Setup's `CORE_ENTRIES` in `scripts/orchflows.py` owns the shipped file list. Tests and example libraries stay in the checkout; core Markdown links must resolve within the shipped core. To update core: edit the checkout, run `python -m unittest discover -s tests`, then [load it for development](hosts.md#register-and-refresh) or [run setup](home.md#setup) to update a home.

## A library

```text
<library>/
├── plugin.json                     name, version, skills: "./skills/"
├── .claude-plugin/plugin.json      Claude manifest
├── .codex-plugin/plugin.json       Codex manifest
├── README.md                       composition, agent count, install, dependencies
├── references/                     shared context and contracts
├── guidance/<domain>.md            domain or dotted specialization
├── skills/<skill>/SKILL.md          frontmatter name + description; instructions
├── skills/<skill>/references/       knowledge used by this skill only
├── skills/<skill>/scripts/          mechanics; sibling tests/
└── trials/                         request.md, expected-behavior.md
```

Skill identity is `<library>:<skill>`. Keep links within the package; reach other packages by native skill name or resolved paths. Never embed machine-specific paths. Declare runtime dependencies in the README; setup installs none for libraries.

## Invariants

- Skills name scripts, inputs and results; scripts own their internals.
- Declare agent counts; extra reviews, loops or repairs require a caller request.
- Report missing work as a gap, never as no-results evidence.
- Establish behavior with a real bounded trial. Valid frontmatter proves no behavior; unexercised failure paths remain untested.
