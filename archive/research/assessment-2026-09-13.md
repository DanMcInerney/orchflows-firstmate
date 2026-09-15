# FirstMate + Orchflows integration assessment

Investigated September 13, 2026. FirstMate source: [b182d0f](https://github.com/kunchenguid/firstmate/tree/b182d0f908b78d08c7ccb8dce3775bdca8c5d657). Orchflows source: [86aabd9, version 0.7.0](https://github.com/DanMcInerney/orchflows/tree/86aabd91071fa07a05cf970db2e73909184a1955). The Orchflows checkout was clean before this report.

**Verdict: a simple optional integration is feasible, but installing the existing Orchflows plugin does not establish seamless FirstMate compatibility.** The strongest first version places a selected Orchflows workflow inside a normal FirstMate crewmate. Making Orchflows itself direct the entire FirstMate fleet is substantially more work.

This is a source-based engineering assessment. I inspected Kun Chen's public repository account and FirstMate's current source, compared it with this Orchflows checkout, and ran existing Orchflows installation tests. I did not launch an integrated FirstMate fleet, install plugins into the user's active harness, or establish a runtime compatibility matrix.

**Why they fit**

Kun Chen's ecosystem separates fleet operation (FirstMate), validation (no-mistakes), and worktree management (treehouse). FirstMate's own vision assigns it the command role and keeps validation elsewhere. Orchflows similarly adds instructions and guidance above the native agent host, without an execution runtime. There is a useful layering opportunity: FirstMate handles durable outer tasks; Orchflows supplies reusable ways to carry out an assignment. This is an architectural interpretation of their documented boundaries. [FirstMate vision](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/VISION.md), [Orchflows architecture](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/architecture.md).

| Responsibility in the proposed integration | Owner |
| --- | --- |
| Intake, top-level task dispatch, fleet supervision and recovery | FirstMate |
| Task workspace, delivery mode and merge authority | FirstMate and its selected delivery path |
| Workflow selection within the assigned task, domain guidance, bounded work composition | Orchflows inside the crewmate |
| Native child execution and child model controls | The crewmate's actual agent host |
| Final task status, escalation and delivery handoff | The crewmate |

The supervisor should dispatch a crewmate through FirstMate's ordinary mechanism. That crewmate loads the requested Orchflows workflow and remains accountable for its children.

**Three possible products**

| Scope | Assessment |
| --- | --- |
| Manually select an Orchflows workflow for one compatible crewmate | A plausible small proof of concept: install the complete package, supply a specific brief, and resolve review/workspace rules. Runtime verification is still required. |
| Install once, automatically apply approved workflows to matching FirstMate tasks, and update safely | The recommended product. Needs a small bridge package plus explicit FirstMate configuration, launch and policy support. |
| Make every Orchflows worker/reviewer a durable, independently visible FirstMate fleet member | A larger execution adapter and a change to Orchflows' native-child contract. Needs lifecycle, state and result mapping beyond installation. |

**The major complexities**

1. **The supervisor has a different delegation contract.** FirstMate requires primary and secondmate supervisors to dispatch through its fleet. Its native-delegation guard is wired and verified for Claude; enforcement on other harnesses has documented gaps. Task worktrees are explicitly outside the guard's scope. Consequently the crewmate is the intended integration location. Preserve the supervisor policy and verify enforcement for the selected harness. [Delegation boundary and harness wiring](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/subagent-guard.md#harness-wiring).

2. **Review ownership is a real policy incompatibility.** FirstMate assigns review and subsequent delivery rigor to the selected path: no-mistakes owns its pipeline, and faster paths do not gain independent reviewers by default. Separately requested reviews are allowed. Orchflows' dynamic workflow always includes independent review and one repair pass. Simply making that workflow the default would change FirstMate's policy. The bridge should use an appropriate work-only composition before no-mistakes, or require an explicit policy selecting the separate review deliverable. Keeping both full review systems by default would add cost and gates. [FirstMate delivery policy](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/AGENTS.md#selected-delivery-path-and-merge-authority), [Orchflows dynamic workflow](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/skills/orch-dynamic-workflow/SKILL.md).

3. **A supported FirstMate harness is not automatically a supported Orchflows host.** Orchflows documents Codex and Claude Code with native children. FirstMate supports a much wider selection and can choose the worker harness separately from its supervisor. The bridge must check the worker's real tools, plugin visibility, requested model/effort and delegation depth. FirstMate's recorded Codex tool inventory differs from the native delegation available in this investigation; it cannot prove what another launched worker will expose. Begin with a verified Claude Code worker configuration, then certify the exact Codex launch. The primary may use another supported FirstMate harness. [Orchflows host contracts](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/hosts.md), [FirstMate worker launch templates](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-spawn.sh#L1514-L1564).

4. **Workspace and identity instructions need a bridge.** FirstMate's generated briefs constrain writes to the task worktree, with specified output exceptions. Some Orchflows tasks require additional isolated worktrees, and workflow authoring defaults to a user library outside the task. A first version should keep child operations in the task workspace and avoid concurrent conflicting edits. Broader isolation needs explicit allowed locations, branch ownership and cleanup. When the target repository is FirstMate itself, its injected role contract also forbids delegating the assigned task; that wording needs a narrow child-delegation exception if this use case is supported. [Brief rules](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-brief.sh#L358-L395), [Ship workspace rules](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-brief.sh#L442-L479), [Self-development role contract](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-dod-lib.sh#L31-L38).

5. **Inner workflow completion is not final delivery.** The crewmate must aggregate child results, acknowledge FirstMate inbox messages, propagate steering to children, and route decisions through its supervisor. The no-mistakes path has two distinct completion signals: implementation `done` prompts FirstMate to instruct the worker to run validation; CI-ready `done` follows the pipeline. Subsequent fixes belong to that pipeline. A generic translation of every child completion into `done` would be wrong. The parent should remain active while children work and collect or stop them before handoff. Recovery of an interrupted crewmate's inner workflow needs durable checkpoints or an explicit restart policy; outer task durability does not establish native-child recovery. [Delivery contract](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-dod-lib.sh#L211-L248), [Supervision architecture](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/architecture.md).

6. **Installation and updates cross different discovery boundaries.** Orchflows installs a complete managed core and generates host marketplaces; it does not register those marketplaces or activate plugins by itself. Its package-relative links mean copying only skill folders is insufficient. FirstMate's present extension mechanism is specifically for process-event adapters and explicitly excludes instruction injection and worker-launch hooks, so it is not an existing workflow integration API. A bridge needs normal host plugin registration and a small, separate FirstMate workflow configuration seam. [Orchflows setup](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/home.md), [FirstMate extension scope](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/extension-bindings.md#scope-and-design).

7. **Resources and configuration must propagate deliberately.** Orchflows setup defaults to changing both hosts' user concurrency settings to 15. A FirstMate integration should initially use the existing `--skip-host-config` option and set deliberate child limits; multiplying fleet workers by inner concurrency can exhaust quotas. Resolve outer dispatch choices and inner assignment choices separately, preserve explicit model/effort requests, and prevent an automatic harness fallback from silently dropping the workflow. Custom `ORCHFLOWS_HOME` and host configuration locations must actually reach the launched process; listing environment variables is not equivalent to provisioning them in a long-lived terminal daemon or on a remote host. [Setup implementation](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/scripts/orchflows.py#L220-L269), [FirstMate environment contract](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/configuration.md#worker-launch-environment-configlaunch-env-allowlist).

**What I would adjust on Orchflows**

- Ship an optional `firstmate` library containing the bridge workflow and FirstMate-specific guidance. Keep the core Work and Review primitives unchanged for the worker-level integration.
- Give the bridge explicit inputs: task identity, workspace, delivery contract, selected workflow and libraries, guidance, child limits, model/effort choices, artifact destination and status route.
- Provide separate compositions for work handed to the existing delivery gate and explicitly authorized independent review. Preserve the dynamic workflow's existing contract.
- Add a small integration installer/checker that verifies complete packages, worker-visible host registration and required capabilities. Extend readiness beyond the current filesystem/package `doctor` checks.
- Wrap existing setup and host refresh with version recording, preservation of user libraries, explicit compatibility checks and a recoverable update path. Apply updates to new tasks and avoid changing resources underneath an active workflow. Setup's package-swap recovery alone does not provide a transaction across FirstMate configuration, plugin caches and remote machines.

**What I would adjust on FirstMate**

- Add an opt-in worker-workflow selection contract and inject its resolved instructions through the existing brief/launch owner. Keep it separate from harness/model dispatch unless that schema is deliberately extended.
- Include the workflow and resolved version in durable task metadata so relaunches can reconstruct the same assignment.
- Document whether the selected workflow includes an authorized separate review, and make the generated brief agree with that policy.
- Preflight package visibility and native delegation for the actual selected worker profile. Route only to a compatible, authorized profile.
- Define subordinate workspace access and the worker-to-supervisor status boundary. Resolve the FirstMate self-development role wording before enabling that use case.
- Include any new configuration in secondmate inheritance, with independent package installation and path resolution on each remote host.

A manual, narrowly scoped trial can likely use existing briefs and host registration without changing FirstMate source, provided the review deliverable and boundaries are explicit. Reliable automatic application and upgrades deserve the small supported seam above.

For Codex Desktop specifically, FirstMate currently documents no selectable Desktop backend: its shell scripts lack a supported transport to create and manage the same visible Desktop tasks throughout their lifecycle. Installing Orchflows does not supply that transport. This is separate from integrating with a FirstMate-launched Codex CLI worker. [Desktop backend boundary](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/codex-app-backend.md#current-blocker).

**Suggested first release and acceptance checks**

Start with one local FirstMate home, one verified Claude Code worker profile, the complete Orchflows core plus the bridge, and a deliberately requested knowledge/review task or work-only coding composition. Keep the outer FirstMate dispatch and delivery lifecycle.

Before calling it plug-and-play, demonstrate:

1. Install twice; preserve existing configuration and user libraries.
2. Launch through FirstMate; resolve the selected workflow and create/collect a real native child.
3. Verify the selected primary harness's delegation enforcement, preserve its fleet-only policy, and keep all child edits inside their authorized workspace.
4. Exercise an authorized independent review, and separately prove no-mistakes delivery does not receive an accidental extra gate.
5. Interrupt and relaunch a worker; recover or explicitly restart the inner work without premature completion.
6. Upgrade and recover from an interrupted upgrade; preserve an existing task's recorded workflow version.
7. Report a missing capability or unsupported model/effort clearly; never claim the workflow ran after falling back to ordinary execution.

**Verification completed:** 29 existing `test_home_setup.py` tests and 2 existing `test_home_cli.py` tests passed on Python 3.14.6 using disposable homes and host settings. This supports reuse of Orchflows' packaging, preservation, update recovery and installed CLI mechanics. It is not an end-to-end FirstMate integration test.

The practical recommendation is an optional worker workflow package with a small FirstMate attachment point. The bulk of the work is reconciling authority, delivery policy and lifecycle expectations; copying and registering the package is the easier portion.
