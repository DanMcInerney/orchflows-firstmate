"""Read-only evidence capture. Missing evidence is never treated as a pass."""
import hashlib
from datetime import datetime
import json
import os
from pathlib import Path
import re
import time

from io_utils import atomic_text


def records(path):
    if not path.exists():
        return
    for line in path.read_text(errors="replace").splitlines():
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue  # A native transcript can end in an in-flight partial write.


def primary_records(lab):
    sessions = set(lab.config.get("primary_sessions", [])) | {lab.config["primary_session"]}
    rows = []
    for path in (lab.root / "evidence/transcripts/claude").glob("*.jsonl"):
        if path.stem in sessions:
            rows.extend(records(path))
    yield from sorted(rows, key=lambda row: row.get("timestamp", ""))


def completed(lab, case):
    marker = f"E2E_CASE_DONE {case}"
    start = max((row["time"] for row in records(lab.root / "events.jsonl")
                 if row.get("kind") == "case-start" and row.get("case") == case), default=0)

    def current(row):
        if not start:
            return True
        try:
            return datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")).timestamp() >= start
        except (KeyError, ValueError):
            return False

    # Only assistant text counts, never an echoed prompt or a tool result.
    return any(marker == line.strip()
               for row in primary_records(lab) if row.get("type") == "assistant" and current(row)
               for block in row.get("message", {}).get("content", [])
               if isinstance(block, dict) and block.get("type") == "text"
               for line in block.get("text", "").splitlines())


def metadata(text):
    return dict((key, value.strip().strip("'\"")) for key, value in
                re.findall(r"^([A-Za-z_][A-Za-z_0-9]*)=(.*)$", text, re.M))


def task_sessions(routing, task_id, meta, fallback_time=0):
    """Join fresh native launches by worktree and generation, not a reused path alone."""
    spawn = re.match(r"s(\d+)", meta.get("spawn_gen", ""))
    lower = int(spawn[1]) - 5 if spawn else fallback_time - 15
    later = []
    for other in routing.get("tasks", []):
        item = other["metadata"]
        match = re.match(r"s(\d+)", item.get("spawn_gen", ""))
        if other["task_id"] != task_id and item.get("worktree") == meta.get("worktree") and match:
            if int(match[1]) > lower + 5:
                later.append(int(match[1]))
    upper = min(later, default=float("inf"))
    return [session for session in routing.get("claude_sessions", {}).values()
            if session.get("cwd") == meta.get("worktree") and session.get("first_time") and
            lower <= datetime.fromisoformat(session["first_time"].replace("Z", "+00:00")).timestamp() < upper]


class Collector:
    def __init__(self, lab):
        self.lab = lab
        self.out = lab.root / "evidence"
        self.out.mkdir(exist_ok=True)
        self.hashes = {}
        index = self.out / "files.jsonl"
        for row in records(index):
            self.hashes[row["path"]] = row["sha256"]
        # Whitelist capture, plus redact known secrets if a tool prints one.
        self.secrets = [v for k, v in os.environ.items() if len(v) >= 12 and
                        re.search(r"TOKEN|SECRET|PASSWORD|API_KEY", k, re.I)]

    def clean(self, text):
        for secret in self.secrets:
            text = text.replace(secret, "[REDACTED]")
        return re.sub(r"(?:sk-ant-|sk-proj-|ghp_|github_pat_)[A-Za-z0-9_-]{12,}",
                      "[REDACTED]", text)

    def save(self, relative, text, version=True):
        text = self.clean(text)
        digest = hashlib.sha256(text.encode()).hexdigest()
        if self.hashes.get(relative) == digest:
            return
        self.hashes[relative] = digest
        target = self.out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_text(target, text)
        if version:
            obj = self.out / "objects" / digest
            obj.parent.mkdir(exist_ok=True)
            if not obj.exists():
                atomic_text(obj, text)
        with (self.out / "files.jsonl").open("a") as f:
            f.write(json.dumps({"time": time.time(), "path": relative,
                                "sha256": digest, "bytes": len(text.encode()),
                                "versioned": version}) + "\n")

    def home(self):
        # No .env, credential stores, auth/config dumps, unrelated fleet or projects.
        for folder in ("data", "state"):
            for path in (self.lab.home / folder).rglob("*"):
                if path.is_symlink() or not path.is_file():
                    continue
                rel = path.relative_to(self.lab.home)
                if folder == "state" and not (path.suffix in {
                    ".meta", ".status", ".msg", ".json", ".log", ".jsonl"} or
                    "wake-queue" in path.name or "launch" in path.name):
                    continue
                try:
                    self.save("home/" + str(rel), path.read_text(errors="replace"))
                except FileNotFoundError:
                    pass  # Native teardown can remove an already enumerated file.

    def processes(self):
        observed = []
        marker = f"FM_HOME={self.lab.home}".encode()
        for proc in Path("/proc").glob("[0-9]*"):
            try:
                if marker not in (proc / "environ").read_bytes().split(b"\0"):
                    continue
                argv = (proc / "cmdline").read_bytes().decode(errors="replace").split("\0")
                if not argv or not any(x in Path(argv[0]).name for x in ("claude", "codex", "node")):
                    continue
                flags = {}
                for i, arg in enumerate(argv[:-1]):
                    if arg in ("--model", "--effort", "--session-id", "--resume"):
                        flags[arg] = argv[i + 1]
                    elif arg == "-c" and "reasoning_effort" in argv[i + 1]:
                        flags["reasoning_effort"] = argv[i + 1]
                observed.append({"pid": int(proc.name), "executable": argv[0],
                                 "resolved_executable": str((proc / "exe").resolve()),
                                 "cwd": str((proc / "cwd").resolve()), "flags": flags})
            except (OSError, PermissionError):
                continue
        self.save("processes/latest.json", json.dumps(observed, indent=2))
        with (self.out / "processes/history.jsonl").open("a") as f:
            f.write(json.dumps({"time": time.time(), "processes": observed}) + "\n")

    def transcripts(self):
        # Full native JSONL is kept privately, scoped to this lab by path/session.
        # Discovery never guesses the newest global conversation is ours.
        config = json.loads((self.lab.root / "lab.json").read_text())
        claude = Path(config["env"].get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
        codex = Path(config["env"].get("CODEX_HOME", Path.home() / ".codex"))
        for kind, directory in (("claude", claude / "projects"),
                                ("codex", codex / "sessions")):
            for path in directory.rglob("*.jsonl"):
                if path.stat().st_mtime < self.lab.config["created"]:
                    continue
                with path.open(errors="replace") as f:
                    head = f.read(131072)
                if not self.belongs_to_lab(head):
                    continue
                self.save(f"transcripts/{kind}/{path.name}", path.read_text(errors="replace"), version=False)
                if kind == "claude":
                    for result in (path.parent / path.stem / "tool-results").glob("*"):
                        if result.is_file() and result.suffix in {".txt", ".json"}:
                            self.save(f"transcripts/tool-results/{path.stem}/{result.name}",
                                      result.read_text(errors="replace"), version=False)

    def belongs_to_lab(self, head):
        primary = set(self.lab.config.get("primary_sessions", [])) | {self.lab.config["primary_session"]}
        for line in head.splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("sessionId", row.get("session_id")) in primary:
                return True
            cwd = row.get("cwd")
            if row.get("type") == "session_meta":
                cwd = row.get("payload", {}).get("cwd", cwd)
            if cwd:
                candidate = Path(cwd)
                if candidate == self.lab.root or self.lab.root in candidate.parents:
                    return True
        return False

    def routing(self):
        tasks = []
        for path in (self.out / "home/state").glob("*.meta"):
            task = metadata(path.read_text())
            tasks.append({"task_id": path.stem, "metadata": task})
        models, codex = {}, {}
        calls = []
        for path in (self.out / "transcripts/claude").glob("*.jsonl"):
            used, efforts, turn_efforts, usage, cwd, first_time, version = set(), set(), set(), {}, None, None, None
            message_usage = {}
            for row in records(path):
                cwd = row.get("cwd", cwd)
                first_time = first_time or row.get("timestamp")
                version = row.get("version", version)
                message = row.get("message") or {}
                if row.get("type") == "assistant":
                    if row.get("effort"):
                        efforts.add(row["effort"])
                    if row.get("perTurnEffort"):
                        turn_efforts.add(row["perTurnEffort"])
                    if message.get("model"):
                        used.add(message["model"])
                    # Native usage is preserved in the raw log; no cost is invented.
                    for block in message.get("content", []):
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            calls.append({"session": path.stem, "time": row.get("timestamp"),
                                          "name": block.get("name"), "input": block.get("input")})
                    usage = message.get("usage", usage)
                    if message.get("id") and message.get("usage"):
                        totals = message_usage.setdefault(message["id"], {})
                        for key in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
                            totals[key] = max(totals.get(key, 0), message["usage"].get(key, 0))
            models[path.stem] = {"response_models": sorted(used), "cwd": cwd,
                                "first_time": first_time, "cli_version": version,
                                "native_efforts": sorted(efforts), "native_per_turn_efforts": sorted(turn_efforts),
                                "usage_totals_deduplicated_by_message_id": {
                                    key: sum(u.get(key, 0) for u in message_usage.values())
                                    for key in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")},
                                "last_message_usage": usage}
        for path in (self.out / "transcripts/codex").glob("*.jsonl"):
            contexts = []
            for row in records(path):
                payload = row.get("payload") or {}
                if row.get("type") == "turn_context":
                    contexts.append({key: payload.get(key) for key in
                                     ("cwd", "model", "effort", "reasoning_effort")})
                if row.get("type") == "response_item" and payload.get("type") in {
                        "function_call", "custom_tool_call"}:
                    calls.append({"session": path.stem, "time": row.get("timestamp"),
                                  "name": payload.get("name"), "input": payload.get("arguments", payload.get("input"))})
            codex[path.stem] = {"native_turn_contexts": contexts}
        self.save("routing.json", json.dumps({"tasks": tasks, "claude_sessions": models, "codex_sessions": codex,
                  "note": "Metadata is a dispatch record; process flags and native response models are separate evidence. Missing effort is unknown, not low. Typed routing may be off without configuration/credentials."}, indent=2))
        calls.sort(key=lambda call: (call.get("time") or "", call["session"]))
        self.save("tool-calls.jsonl", "".join(json.dumps(c) + "\n" for c in calls), version=False)

    def collect(self):
        self.lab = type(self.lab)(self.lab.root)
        self.home()
        self.processes()
        self.transcripts()
        if self.lab.pane:
            try:
                self.save("panes/primary.txt", self.lab.read(4000))
            except (OSError, RuntimeError) as exc:
                self.lab.log("capture-error", error=str(exc))
        self.routing()
