"""Test fixture and terminal transport. Never dispatches or repairs a worker."""
import json
import hashlib
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import time
import uuid

from scenarios import requests
from io_utils import atomic_text


class Lab:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.config = json.loads((self.root / "lab.json").read_text())
        self.fm = Path(self.config["firstmate"])
        self.core = Path(self.config["core"])
        self.home = self.root / "home"
        self.env = os.environ | self.config["env"]
        self.session = self.config.get("session", "")
        self.pane = self.config.get("pane", "")

    def save(self):
        atomic_text(self.root / "lab.json", json.dumps(self.config, indent=2) + "\n")

    def log(self, kind, **fields):
        with (self.root / "events.jsonl").open("a") as f:
            f.write(json.dumps({"time": time.time(), "kind": kind, **fields}) + "\n")

    def call(self, args, *, check=True, timeout=30, cwd=None):
        p = subprocess.run([str(a) for a in args], cwd=cwd or self.fm,
                           env=self.env, capture_output=True, text=True,
                           errors="replace", timeout=timeout)
        self.log("command", argv=[str(a) for a in args], returncode=p.returncode,
                 stdout=p.stdout, stderr=p.stderr)
        if check and p.returncode:
            raise RuntimeError(f"{args}: {p.stderr or p.stdout}")
        return p

    def herdr(self, *args, **kwargs):
        return self.call(["bash", self.fm / "bin/fm-herdr-lab.sh", "run",
                          self.session, *args], **kwargs)

    def read(self, lines=80):
        return self.herdr("pane", "read", self.pane, "--lines", str(lines)).stdout

    def send(self, text):
        # A captain message only. Native hooks own all subsequent supervision.
        self.herdr("pane", "send-text", self.pane, " ".join(text.splitlines()))
        time.sleep(1)
        self.herdr("pane", "send-keys", self.pane, "Enter")
        self.log("captain-message", text=text)

    def background(self, args, name):
        with (self.root / f"{name}.log").open("ab") as f:
            p = subprocess.Popen(args, cwd=self.fm, env=self.env,
                                 stdout=f, stderr=f, stdin=subprocess.DEVNULL,
                                 start_new_session=True)
        self.log("background", name=name, pid=p.pid, argv=[str(a) for a in args])
        return p.pid

    def start(self):
        if self.session:
            raise RuntimeError("Lab already started; inspect it instead of overwriting it")
        sessions = json.loads(self.call(["herdr", "session", "list", "--json"]).stdout)
        default = [s for s in sessions["sessions"] if s["default"]]
        if len(default) != 1:
            raise RuntimeError("Expected exactly one default Herdr session")
        self.config["default_was_running"] = default[0]["running"]
        if not default[0]["running"]:
            self.background(["herdr", "server"], "default-server")
            time.sleep(2)
        helper = self.fm / "bin/fm-herdr-lab.sh"
        self.session = self.call(["bash", helper, "name", "orchflows-e2e"]).stdout.strip()
        self.config["session"] = self.session
        self.env["HERDR_SESSION"] = self.session
        self.config["env"]["HERDR_SESSION"] = self.session
        self.save()
        self.background(["bash", str(helper), "provision", self.session], "provision")
        for _ in range(30):
            p = self.herdr("workspace", "list", check=False)
            if p.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Lab provisioning timed out; see provision.log")
        self.call(["bash", helper, "viewer", "start", self.session])
        self.launch()

    def launch(self):
        if self.pane:
            raise RuntimeError("Primary pane already exists; inspect it before any recovery")
        # Fresh topology comes from Herdr, never from assumed w1:p1 handles.
        result = json.loads(self.herdr("workspace", "create", "--label", "E2E captain",
                                       "--cwd", str(self.fm)).stdout)
        self.pane = result["result"]["root_pane"]["pane_id"]
        self.config["pane"] = self.pane
        self.save()
        command = ["env", *[f"{k}={v}" for k, v in self.config["env"].items()],
                   "claude", "--plugin-dir", str(self.core),
                   "--setting-sources", "project,local", "--permission-mode", "auto",
                   "--session-id", self.config["primary_session"]]
        self.herdr("pane", "run", self.pane, "cd " + shlex.quote(str(self.fm)) +
                   " && exec " + shlex.join(command))

    def fresh_primary(self):
        """A new captain conversation between completed cases, never worker recovery."""
        if list((self.home / "state").glob("*.meta")):
            raise RuntimeError("Cannot replace a primary with live native tasks")
        old = self.config["primary_session"]
        self.send("/exit")
        for _ in range(30):
            live = []
            for proc in Path("/proc").glob("[0-9]*"):
                try:
                    argv = (proc / "cmdline").read_bytes().split(b"\0")
                    if old.encode() in argv and b"--session-id" in argv:
                        live.append(proc.name)
                except OSError:
                    continue
            if not live:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Old primary did not exit; no replacement launched")
        self.config.setdefault("primary_sessions", []).append(old)
        self.config["primary_session"] = str(uuid.uuid4())
        self.config["pane"] = ""
        self.pane = ""
        self.save()
        self.launch()
        self.log("fresh-primary", previous_session=old, session=self.config["primary_session"])
        # Wait for native startup, not a model response; leave dialogs to the operator.
        for _ in range(30):
            screen = self.read(30)
            if "auto mode on" in screen and "Quick safety check" not in screen:
                return
            time.sleep(1)
        raise RuntimeError("New primary is not ready; inspect the retained pane")


def provision(root, firstmate, core, tool_path, dispatch_from=None):
    root, firstmate, core = (Path(p).resolve() for p in (root, firstmate, core))
    if (root / "lab.json").exists() or (root / "home").exists():
        raise RuntimeError("Refusing to overwrite an existing test home")
    if subprocess.check_output(["git", "-C", str(firstmate), "diff", "HEAD"]).strip():
        raise RuntimeError("FirstMate must have no tracked modifications")
    root.mkdir(parents=True, exist_ok=True)
    os.chmod(root, 0o700)
    for part in ("home/data", "home/state", "home/config", "home/projects", "tmp", "lab", "requests"):
        (root / part).mkdir(parents=True)
    env = {"FM_HOME": str(root / "home"), "FM_ROOT_OVERRIDE": str(firstmate),
           "FM_HERDR_LAB_STATE_DIR": str(root / "lab"), "FM_BACKEND": "herdr",
           "TMPDIR": str(root / "tmp"), "PATH": tool_path,
           "ORCHFLOWS_FIRSTMATE_HOME": str(root / "home/projects/orchflows-home"),
           "CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION": "false",
           "GIT_AUTHOR_NAME": "Orchflows E2E", "GIT_AUTHOR_EMAIL": "e2e@orchflows.invalid",
           "GIT_COMMITTER_NAME": "Orchflows E2E", "GIT_COMMITTER_EMAIL": "e2e@orchflows.invalid"}
    config = {"firstmate": str(firstmate), "core": str(core), "env": env,
              "primary_session": str(uuid.uuid4()), "created": time.time(),
              "firstmate_revision": subprocess.check_output(
                  ["git", "-C", str(firstmate), "rev-parse", "HEAD"], text=True).strip()}
    (root / "lab.json").write_text(json.dumps(config, indent=2) + "\n")
    lab = Lab(root)
    isolate_claude(lab)
    (lab.home / "config/backend").write_text("herdr\n")
    (lab.home / "config/claude-permission-mode").write_text("auto\n")
    # Never author routing policy here. An optional existing native config is
    # copied verbatim; FirstMate owns its schema, validation and interpretation.
    if dispatch_from:
        source = Path(dispatch_from).resolve(strict=True)
        shutil.copyfile(source, lab.home / "config/crew-dispatch.json")
        lab.config["dispatch_source"] = str(source)
        lab.save()
    (lab.home / "data/backlog.md").write_text("# Backlog\n\n## In flight\n\n## Queued\n\n## Done\n")
    names = ("orchflows-home", "cashbook-dynamic", "cashbook-trial", "cashbook-saved")
    for name in names:
        project = lab.home / "projects" / name
        if name == "orchflows-home":
            lab.call(["python3", core / "scripts/orchflows.py", "setup", "--home", project])
            lab.call(["git", "symbolic-ref", "HEAD", "refs/heads/main"], cwd=project)
        else:
            project.mkdir()
            lab.call(["git", "init", "-b", "main"], cwd=project)
            (project / "README.md").write_text(f"# {name}\n\nDisposable E2E project, not yet implemented.\n")
            (project / ".gitignore").write_text("__pycache__/\n*.pyc\n.orch/\n")
        lab.call(["git", "add", "."], cwd=project)
        lab.call(["git", "commit", "-m", "Seed isolated E2E fixture"], cwd=project)
    date = time.strftime("%Y-%m-%d", time.gmtime())
    (lab.home / "data/projects.md").write_text("".join(
        f"- {n} [local-only +yolo] - disposable Orchflows E2E fixture (added {date})\n" for n in names))
    (lab.home / "data/captain.md").write_text(f'''# Test captain preferences

## Orchflows
- Run every ship and scout through orch-dynamic-workflow unless I name another workflow or say "plain". Run any other workflow only when I name it: invoke it by its slash command or read its SKILL.md by path.
- Use your normal dispatch and recovery for every workflow. Follow {core}/docs/architecture.md#model-and-effort for the boundary with saved workflows.
- Record each workflow's phase and task IDs in the backlog item note and resume from it after a restart.
- Read {core}/docs/firstmate.md before the first Orchflows dispatch of a session.

## Bounded test authority
All four registered projects are disposable local-only E2E fixtures. Merge green,
in-scope reviewed changes there through normal FirstMate local delivery and clean
up landed agents. Do not change FirstMate code or the core package. The current
request authorizes using the installed tools for these tests.
''')
    for name, request in requests(core, lab.home).items():
        (root / "requests" / f"{name}.md").write_text(request + "\n")
    provenance(lab)
    return lab


def isolate_claude(lab):
    """Reuse login only; keep unrelated personal plugins/instructions out of tests."""
    config = lab.root / "claude-config"
    config.mkdir(exist_ok=True, mode=0o700)
    source = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    credential = source / ".credentials.json"
    if credential.exists() and not (config / ".credentials.json").exists():
        (config / ".credentials.json").symlink_to(credential)
    # Copy onboarding state, not projects, plugins, tools, preferences or model pins.
    original = source / ".claude.json" if os.environ.get("CLAUDE_CONFIG_DIR") else Path.home() / ".claude.json"
    if original.exists():
        data = json.loads(original.read_text())
        allowed = ("hasCompletedOnboarding", "lastOnboardingVersion",
                   "bypassPermissionsModeAccepted", "oauthAccount")
        (config / ".claude.json").write_text(json.dumps({k: data[k] for k in allowed if k in data}))
        os.chmod(config / ".claude.json", 0o600)
    lab.config["env"]["CLAUDE_CONFIG_DIR"] = str(config)
    user_home = lab.root / "user-home"
    user_home.mkdir(exist_ok=True, mode=0o700)
    if not (user_home / ".claude").exists():
        (user_home / ".claude").symlink_to(config, target_is_directory=True)
    lab.config["env"]["HOME"] = str(user_home)
    # Keep Herdr on the same guarded session socket after isolating HOME.
    lab.config["env"]["XDG_CONFIG_HOME"] = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    # Native tools can reuse existing authentication without importing home skills.
    lab.config["env"]["CODEX_HOME"] = os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))
    lab.config["env"]["GH_CONFIG_DIR"] = os.environ.get("GH_CONFIG_DIR", str(Path(lab.config["env"]["XDG_CONFIG_HOME"]) / "gh"))
    lab.env.update(lab.config["env"])
    lab.env["CLAUDE_CONFIG_DIR"] = str(config)
    lab.save()


def provenance(lab):
    files = {str(p.relative_to(lab.core)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in lab.core.rglob("*") if p.is_file() and
             p.suffix in {".md", ".py", ".json", ".yaml"} and "__pycache__" not in p.parts}
    versions = {}
    for tool in ("claude", "codex", "herdr", "treehouse", "tasks-axi", "python3", "git"):
        try:
            p = lab.call([tool, "--version"], check=False)
            versions[tool] = {"exit": p.returncode, "output": (p.stdout + p.stderr).strip()}
        except (OSError, subprocess.TimeoutExpired) as exc:
            versions[tool] = {"unavailable": str(exc)}
    (lab.root / "provenance.json").write_text(json.dumps({
        "recorded_at": time.time(), "firstmate_revision": lab.config["firstmate_revision"],
        "core_files_sha256": files, "versions": versions}, indent=2) + "\n")
