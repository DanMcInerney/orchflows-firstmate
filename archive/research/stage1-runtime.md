# Stage 1 disposable runtime preparation

This is the historical staging and smoke-test record. Later actual worker attempts and the corrected authentication approach are in [acceptance continuation](stage1-acceptance-continuation.md). Do not seed repeated disposable runs from an old OAuth refresh cache; retain each exact runtime tuple and distinguish the staging checks below from later Work acceptance.

Observed September 13–14, 2026. **A native Linux runtime is now available and an isolated Herdr lifecycle smoke test passed.** This does not establish Stage 1 component execution: this preparation launched no Claude/Codex assignment, created no FirstMate component, and returned no component result.

FirstMate remains the unchanged research source at `b182d0f908b78d08c7ccb8dce3775bdca8c5d657`. Its source checkout was clean after this preparation. No global package installation, host plugin registration, user harness settings edit, live user Herdr session, or credential copy occurred in this preparation. Later integration trials need their own evidence record.

## Host and platform evidence

The initial native-only WSL path inventory found Bash, Git, Python, curl, wget and gh. It did not find Herdr, jq, Treehouse, Node, npm, Claude, Codex, Cargo, rustc or a C compiler. Excluding mounted Windows path entries matters: the pre-existing Windows npm Codex shim was not evidence of a Linux worker installation.

The actual Linux host reported:

| Property | Observed value |
| --- | --- |
| Distribution | Ubuntu 24.04.4 LTS |
| Kernel | `6.6.87.2-microsoft-standard-WSL2` |
| Architecture | `x86_64`, 64-bit |
| Bash | 5.2.21 |
| Git | 2.43.0 |
| Python | 3.12.3 |
| glibc | 2.39 |

Pinned Herdr v0.7.4 resolves through annotated tag object `54208dc16efe15ea92d7f131439d43cbd84b489e` to commit `50aaa2ec046ee26ff407c20f49de496f522512a8`. Its GitHub release API reports publication at `2026-07-15T16:36:20Z` and four binary assets: Linux and macOS, each x86_64 and aarch64. Its version-matched installation documentation calls native Windows preview beta and directs Windows to preview releases. Linux binary installation is therefore a documented path for this pin; no source build is required. [Pinned installation documentation](https://github.com/herdrdev/herdr/blob/50aaa2ec046ee26ff407c20f49de496f522512a8/docs/next/website/src/content/docs/install.mdx), [release metadata](https://api.github.com/repos/herdrdev/herdr/releases/tags/v0.7.4).

Current upstream differs: v0.9.0 was published at `2026-09-07T19:21:31Z`, and its release includes `herdr-windows-x86_64.zip` alongside Linux/macOS assets. The current website advertises all three platforms. This is evidence of a newer available Windows distribution, not a certification of pinned FirstMate on Windows or a reason to silently upgrade the lab. v0.9.0 was not installed or tested. [Current release metadata](https://api.github.com/repos/herdrdev/herdr/releases/tags/v0.9.0), [current website](https://herdr.dev/).

## Staged tuple and provenance

Binaries and npm dependencies live only under ignored `.scratch/stage1-runtime/`. Its `bin/` directory can be prepended to the PATH of a disposable WSL subprocess. These files are local preparation artifacts, not shipped dependencies or a new installer.

| Tool | Exact staged version | Actual check |
| --- | --- | --- |
| Herdr | 0.7.4, protocol 16 | Native ELF; `--version`; isolated client/server status and lifecycle |
| jq | 1.8.1 | Native ELF; `--version`; runtime JSON assertions |
| Treehouse | 2.0.1 | Native ELF; `--version` |
| Codex CLI | 0.152.0 | Native Linux-musl ELF; `--version`; authentication status |
| Claude Code | 2.1.269 | Native Linux-x64 ELF; `--version`; authentication status |
| Node | 24.15.0 | Native Linux binary; `--version`; matches the observed Windows Node version |
| npm | 11.12.1 | Bundled with that Node archive; `--version` and local install |
| tasks-axi | 0.2.5 | Node CLI; `--version`; FirstMate compatibility probe |

Herdr and Treehouse versions and archive hashes match FirstMate's [Herdr installer](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-install-herdr.sh) and [Treehouse installer](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-install-treehouse.sh). Downloads used explicit official release URLs, size/time bounds and digest verification. Herdr's installer itself was not run: its unqualified post-install `status` call was replaced in this preparation by explicit isolated-session checks.

| Download | SHA-256 verified before use |
| --- | --- |
| [Herdr v0.7.4 Linux x86_64](https://github.com/herdrdev/herdr/releases/download/v0.7.4/herdr-linux-x86_64) | `bc0fc02d4ba500f9cac2353a43e67fe036785ecca6eb55378e050fac3c103059` |
| [jq 1.8.1 Linux amd64](https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-linux-amd64) | `020468de7539ce70ef1bceaf7cde2e8c4f2ca6c3afb84642aabc5c97d9fc2a0d` |
| [Treehouse v2.0.1 Linux amd64 archive](https://github.com/kunchenguid/treehouse/releases/download/v2.0.1/treehouse-v2.0.1-linux-amd64.tar.gz) | `1d5a32751ab921670103fd201ddb2b91b47338cb13976f45642b827cf8976af2` |
| [Codex 0.152.0 Linux-musl archive](https://github.com/openai/codex/releases/download/rust-v0.152.0/codex-x86_64-unknown-linux-musl.tar.gz) | `05f942d3d3c5b5acd9edad56ce2797b6fe72dbb1462b24e5c9bf7dcec9a28a11` |
| [Claude Code 2.1.269 Linux-x64](https://downloads.claude.ai/claude-code-releases/2.1.269/linux-x64/claude) | `25e44883f54419569a3d739f38cbbdaebe83b09895da0f343e1b003710a4775b` |
| [Node v24.15.0 Linux-x64 archive](https://nodejs.org/dist/v24.15.0/node-v24.15.0-linux-x64.tar.xz) | `472655581fb851559730c48763e0c9d3bc25975c59d518003fc0849d3e4ba0f6` |

The extracted Treehouse binary hash is `07a54f318c4b17f200cf34a679ad63c66bc05166461de9c33fa83ed39301338d`; extracted Codex is `f541420d35d3ad757fe71c0a34a3de0ec80fd513e10e5c52596b39d8be6e445c`; Node is `d1de76d8edf2fededf6f8b30d244e2c0529ac607923a018283b77e9c74bd932c`.

Claude's release manifest detached signature passed against published fingerprint `31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE`, in an isolated public-key keyring. GPG reported a good signature; its fresh-key trust warning and mounted-filesystem keyring permission warning were retained. No private key or user keyring was involved. The signature and binary checksum procedure follows [Anthropic's installation documentation](https://code.claude.com/docs/en/setup#binary-integrity-and-code-signing).

The pinned FirstMate tree has no `fm-install-dependencies.sh` and no tasks-axi binary checksum installer. [Its compatibility owner](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/bin/fm-tasks-axi-lib.sh) requires version 0.2.4 or newer, `update --archive-body`, and multi-ID `mv`. The [stock Bash CI lane](https://github.com/kunchenguid/firstmate/blob/b182d0f908b78d08c7ccb8dce3775bdca8c5d657/.github/workflows/ci.yml) pins npm package 0.2.5; other lanes install a floating version. This preparation chose exact 0.2.5 and ran `fm_tasks_axi_compatible_probe` successfully. Its local lock records `axi-sdk-js` 0.1.11 and `@toon-format/toon` 2.3.1, with npm integrity values. Lock SHA-256: `44835dcc7b2cd9a9cad310972427bdb645bede94ac0f95f8913fca7b9ac368fb`.

## Runtime isolation and actual smoke result

Herdr's storage isolation is source-backed, not an invented environment marker. At the exact Herdr commit:

- [`src/config/io.rs`](https://github.com/herdrdev/herdr/blob/50aaa2ec046ee26ff407c20f49de496f522512a8/src/config/io.rs) makes `XDG_CONFIG_HOME` and `XDG_STATE_HOME` own configuration and state roots.
- [`src/session.rs`](https://github.com/herdrdev/herdr/blob/50aaa2ec046ee26ff407c20f49de496f522512a8/src/session.rs) derives default/named session directories, API/client sockets and enumeration from that config root. Explicit `--session` takes precedence over an inherited API socket override.
- The [configuration contract](https://github.com/herdrdev/herdr/blob/50aaa2ec046ee26ff407c20f49de496f522512a8/docs/next/website/src/content/docs/configuration.mdx) supplies `terminal.default_shell`, `shell_mode` and `new_cwd`; the [model](https://github.com/herdrdev/herdr/blob/50aaa2ec046ee26ff407c20f49de496f522512a8/src/config/model.rs) supplies update checks and agent-resume controls.

The successful smoke created a fresh private `mktemp -d /tmp/fm-s1.XXXXXX` namespace. Each invocation used `env -i` with a new HOME, config/state/temp directories within that namespace, the staged binaries plus Linux system tools, and `/bin/bash`. It inherited no Windows paths, harness profile, credential variable, or Herdr endpoint. Local config selected a non-login Bash shell, home cwd, disabled update/manifest checks, and disabled agent resume. The short path is necessary for Unix socket length limits.

The unmodified FirstMate lab helper requires exactly one running default session as a tripwire. A **disposable sentinel in that new namespace** supplied it. This sentinel was not the user's default runtime. Preflight confirmed its exact namespace socket and that it was initially stopped. The named lab then used only the helper's generated `fm-lab-*` name and guarded provision/run/teardown operations. Both running sessions' sockets were asserted beneath the private config root.

Successful run `fm-s1.SmiH0c`, named session `fm-lab-s1-366-7408`:

| Check | Executed result |
| --- | --- |
| Initial private session enumeration | One default record, `running=false`, exact private socket |
| Disposable sentinel status | Herdr 0.7.4, protocol 16, running |
| Unchanged lab helper provision | Passed |
| Named client/server status | Both 0.7.4/protocol 16; `compatible=true`, `restart_needed=false` |
| Session enumeration during run | Exactly the private sentinel and named lab; both running, both sockets scoped |
| `workspace list` | Valid structured response, empty list; no worker pane launched |
| Lab helper teardown | Passed; no stderr; named session absent afterward |
| Sentinel stop | Allowed only after PID, process-start, executable, cwd and full command identity matched |
| Final private enumeration | Only default remains, `running=false`; no running session |

The smoke script SHA-256 is `abafeca3959d10b976be360ca941481381a80252478e9eb16e892cde4d54bc73`; unchanged lab-helper SHA-256 is `3e46927b3222bab2762b82b320f9597e5d13b628fae211c639650b9995a563c2`. Local commands, source excerpts, public release metadata, scripts and sanitized smoke receipts are retained under ignored `.scratch/stage1-runtime/`; the successful receipts are in `attempts/fm-s1.SmiH0c/`. They are disposable local evidence, not portable installed state.

Failed preparation probes are retained separately. Using the long mounted repository path as a socket root failed with `local socket name length exceeds capacity of sun_path of sockaddr_un`, motivating the short Linux temp namespace. The first lifecycle attempt successfully provisioned the lab but passed unsupported `--json` to `workspace list`; cleanup then refused a sentinel stop because a background shell wrapper PID did not match the binary. The next inventory found that transient namespace and processes absent; this was not counted as graceful cleanup. The rerun used direct `exec` for the sentinel and the supported CLI form, then passed verified teardown. An initial npm invocation also refused using the same `/dev/null` file as both user and global config; distinct empty private config files resolved it.

## Harness authentication and remaining Stage 1 work

Official documentation provides Linux CLI installation for [Codex](https://learn.chatgpt.com/docs/codex/cli) and Linux/WSL installation for [Claude](https://code.claude.com/docs/en/setup). Both staged binaries were actually identified as Linux ELF and executed. This establishes native executable availability; current documentation alone is not a live FirstMate compatibility result.

The empty disposable profiles correctly reported not authenticated. A subsequent authorized read-only check used the existing **Linux** login user's HOME, a clean environment, and explicit status commands, without a Windows credential home, interactive login or profile mutation:

- `codex login status`: exit 0, `Logged in using ChatGPT`.
- `codex -c 'cli_auth_credentials_store="file"' login status`: same successful file-store status.
- `claude auth status`: exit 0, `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty`.

Metadata-only checks found regular, non-symlink files at the Linux user's `~/.codex/auth.json` and `~/.claude/.credentials.json`, both owner mode 0600. No credential contents were printed, read into research, or copied by this preparation. These status results establish an available cached login; they do not prove a future model request will succeed or establish quotas.

For a subsequent authorized trial, minimum credentials can be copied only into private Linux temporary profiles, after the trial owner takes custody: `CODEX_HOME/auth.json` and `CLAUDE_CONFIG_DIR/.credentials.json`, directories 0700 and files 0600, with a separate disposable HOME. Codex file storage and the auth-cache copy route are [documented](https://learn.chatgpt.com/docs/auth#credential-storage); Claude documents [Linux credential storage and the config-directory override](https://code.claude.com/docs/en/authentication#credential-management). Use copies rather than symlinks so refreshes and trust/config writes cannot rewrite the source files. Copy no settings, instruction files, plugins or conversation history; never include auth in retained traces; remove disposable credentials after every owned worker has stopped. This is a plan for the integration owner, not an executed credential seed.

FirstMate's Claude trust pre-registration needs Node and writes the selected config store. A disposable store is therefore required even though a Linux login already exists. Model/effort routing, prompt admission, actual harness launch, process-state detection, component result retention, parent waiting/restart, and cleanup with real workers remain the Stage 1 acceptance work. The smoke also does not certify the complete universal FirstMate bootstrap toolchain: no-mistakes, gh-axi, chrome-devtools-axi and quota-axi were not provisioned here. No running runtime was left for another owner to adopt.
