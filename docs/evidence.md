# Evidence and completed work

This document preserves what the originating session established. The [original assessment](assessment-2026-09-13.md) remains the dated narrative record; this file can accumulate later evidence.

**Source baseline**

| Project | Repository | Examined revision | Scope |
| --- | --- | --- | --- |
| FirstMate | https://github.com/kunchenguid/firstmate | b182d0f908b78d08c7ccb8dce3775bdca8c5d657 | Shallow clone of then-current main; source and documentation inspection only |
| Orchflows | https://github.com/DanMcInerney/orchflows | 86aabd91071fa07a05cf970db2e73909184a1955 | User's clean checkout, manifest version 0.7.0; source inspection and existing packaging tests |

The original search results contained older descriptions. Conclusions were checked against the pinned local source, not merely search snippets. Account inspection identified the relevant FirstMate/no-mistakes/treehouse ecosystem; no broad claim about every repository was made.

[Source manifest](source-manifest.json) contains SHA-256 values for the local source bytes available during handoff preparation. Git checkouts may normalize line endings, so use the manifest's Git blob IDs for cross-platform byte identity; working-copy hashes describe the inspected copies. Upstream code is not vendored into this documentation repository.

**Source entrypoints**

| Topic | FirstMate evidence | Orchflows comparison |
| --- | --- | --- |
| Responsibilities and architecture | [VISION.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/VISION.md), [docs/architecture.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/architecture.md) | [docs/architecture.md](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/architecture.md) |
| Supervisor policy, native-child exemption and enforcement gaps | [docs/subagent-guard.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/subagent-guard.md) | [orch-work](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/skills/orch-work/SKILL.md), [orch-review](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/skills/orch-review/SKILL.md) |
| Review ownership and delivery modes | [AGENTS.md, selected delivery path](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/AGENTS.md#selected-delivery-path-and-merge-authority) | [dynamic workflow](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/skills/orch-dynamic-workflow/SKILL.md) |
| Brief composition, workspaces and status | [bin/fm-brief.sh](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-brief.sh), [bin/fm-dod-lib.sh](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-dod-lib.sh) | [hosts: isolation](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/hosts.md#isolation) |
| Actual launch templates | [bin/fm-spawn.sh](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-spawn.sh#L1514-L1564) | [host registration and controls](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/hosts.md) |
| Harness-specific evidence | [Claude adapter](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.agents/skills/harness-adapters/references/harness/claude.md), [Codex adapter](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.agents/skills/harness-adapters/references/harness/codex.md) | [host contracts](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/hosts.md) |
| Dispatch and environment | [docs/configuration.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/configuration.md) | [home and package resolution](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/home.md) |
| Existing extension API | [docs/extension-bindings.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/extension-bindings.md) | [package layout](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/architecture.md#a-library) |
| Updates and secondmates | [updatefirstmate skill](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.agents/skills/updatefirstmate/SKILL.md), [inheritance owner](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-config-inherit-lib.sh), [provisioning contract](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.agents/skills/secondmate-provisioning/SKILL.md) | [setup CLI](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/scripts/orchflows.py), [host settings](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/scripts/host_config.py) |
| Desktop limitation | [docs/codex-app-backend.md](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/docs/codex-app-backend.md) | Orchflows does not provide a FirstMate backend transport |
| Native history and recovery evidence | FirstMate durable state is distinct from native child state | [docs/history.md](https://github.com/DanMcInerney/orchflows/blob/86aabd91071fa07a05cf970db2e73909184a1955/docs/history.md); a transcript is evidence, not a live process registry |

**Checks actually executed in the originating investigation**

From the pinned Orchflows checkout, on Windows PowerShell with Python 3.14.6:

```text
python -B -m unittest discover -s tests -p test_home_setup.py
Ran 29 tests in 9.946s
OK

python -B -m unittest discover -s tests -p test_home_cli.py
Ran 2 tests in 4.292s
OK
```

The test code was inspected before execution. It redirects setup and host settings into disposable directories. The tests exercise existing setup, preservation, recovery and installed-CLI behavior. No user's active host plugin configuration was installed or refreshed. Raw test logs were not saved as independent artifacts during that session; the transcript reported the outputs above.

A local reference check also verified that all 17 source-file references in the final original assessment resolved to files in the pinned checkouts and that numeric line anchors were in range. It was not an HTTP-link or heading-anchor validation.

**Independent investigation and review**

A native child investigated FirstMate contracts while the coordinator inspected Orchflows and joined the findings. A fresh child reviewed the complete original assessment without making repairs. It found one substantive wording issue: the report implied primary delegation enforcement across all harnesses, whereas the source only establishes verified Claude wiring and documents other gaps. The coordinator corrected the finding and the related acceptance check. No second review was run.

A legacy Claude adapter reference mentions `--setting-sources project,local`; the examined current `fm-spawn.sh` launch template does not contain that flag. The report therefore does not claim that current FirstMate universally excludes user plugins.

FirstMate records a Codex CLI tool inventory without subagents; the originating Codex Desktop session itself exposed native child tools. This is conflicting deployment evidence, not proof that either source describes every Codex worker. The required FirstMate worker launch remains untested.

**What was not done**

No integrated FirstMate task, native worker capability probe inside a FirstMate-launched process, live supervision/recovery test, package registration test in a crewmate, remote secondmate install, update/rollback experiment across both systems, implementation, upstream PR, or maintainer outreach. No complete license/distribution review or performance/cost comparison. The original work was feasibility research.

**Rehydrate the evidence without relying on previous machine paths**

Clone the two public repositories into disposable directories; these commands download source without running project installers or hooks:

```sh
git clone --no-checkout https://github.com/kunchenguid/firstmate.git firstmate
git -C firstmate checkout --detach b182d0f908b78d08c7ccb8dce3775bdca8c5d657

git clone --no-checkout https://github.com/DanMcInerney/orchflows.git orchflows
git -C orchflows checkout --detach 86aabd91071fa07a05cf970db2e73909184a1955
```

Use separate checkout locations or recorded refs for contemporary upstream research. Verify each `git rev-parse HEAD` before reproducing claims or checks. The original local directories and temporary clone are not dependencies of this handoff.

**Handoff preservation**

The original report was copied unchanged into this repository. Its recorded SHA-256 is `b2e10533790e2886cf3d94479afe48edff58a1a317e38eca6aa160cafa64528c`. Its phrase “this investigation” refers to the originating session described above. New questions and candidate approaches in this repository are proposed follow-up work, not additional completed research.
