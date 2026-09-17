"""Artifact and native execution evidence assertions; no workflow decisions."""
import io
import hashlib
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess
import tarfile

from evidence import Collector, completed, metadata, primary_records, records, task_sessions
from oracle import ArtifactOracle, generated
from io_utils import atomic_text


def export_main(lab, project, case):
    source = lab.home / "projects" / project
    previous = lab.root / "checks" / case / "result.json"
    old = json.loads(previous.read_text()) if previous.exists() else {}
    sha = old.get("artifacts", {}).get(project, {}).get("sha")
    if not sha:
        sha = lab.call(["git", "rev-parse", "main"], cwd=source).stdout.strip()
    target = lab.root / "delivered" / case / project / sha
    if not target.exists():
        target.mkdir(parents=True)
        archive = subprocess.check_output(["git", "-C", str(source), "archive", sha])
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(target, filter="data")
    lab.log("artifact-export", case=case, project=project, sha=sha, path=str(target))
    return target, sha


def case_window(lab, case):
    events = list(records(lab.root / "events.jsonl"))
    starts = [r for r in events if r.get("kind") == "case-start"]
    selected = [r for r in starts if r.get("case") == case]
    if not selected:
        return float("inf"), float("inf")
    start = selected[-1]["time"]
    end = min((r["time"] for r in starts if r["time"] > start), default=float("inf"))
    return start, end


def tool_calls(lab, start=0, end=float("inf")):
    for row in primary_records(lab):
        if row.get("type") != "assistant":
            continue
        stamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")).timestamp()
        if not start <= stamp < end:
            continue
        for block in row.get("message", {}).get("content", []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                yield {"time": row.get("timestamp"), **block}


def reviewed_revisions(text):
    """Accept Git abbreviations, but never mistake a report's base SHA for its review."""
    return set(re.findall(
        r"\b(?:reviewed\s+(?:commit|revision)|(?:commit|revision)\s+reviewed)\b"
        r"[^\n\w]*([0-9a-f]{7,40})\b", text, re.I))


def workflow_checks(lab, case, artifacts):
    checks = []

    def check(name, okay, detail=""):
        checks.append({"name": name, "passed": bool(okay), "detail": detail})

    check("primary reported complete", completed(lab, case))
    start, end = case_window(lab, case)
    calls = list(tool_calls(lab, start, end))
    command_text = "\n".join(c.get("input", {}).get("command", "") for c in calls)
    loaded = "\n".join(json.dumps(c.get("input")) for c in calls)
    if case in ("dynamic", "regression"):
        check("dynamic workflow loaded", "orch-dynamic-workflow" in loaded)
    elif case == "author":
        check("authoring skill loaded", "orch-build-workflow" in loaded)
    else:
        check("saved workflow loaded by path", "cashflow/skills/change/SKILL.md" in loaded)
        fresh = [r for r in records(lab.root / "events.jsonl") if r.get("kind") == "fresh-primary" and
                 r["time"] <= start and r.get("session") != r.get("previous_session")]
        check("saved reuse starts in a fresh primary conversation", bool(fresh))
    check("native dispatch resolver used", "fm-dispatch-resolve.sh" in command_text)
    check("native local delivery used", "fm-merge-local.sh" in command_text)
    hidden_delegation = []
    for path in (lab.root / "evidence/transcripts/claude").glob("*.jsonl"):
        for row in records(path):
            if row.get("type") != "assistant" or not row.get("timestamp"):
                continue
            stamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")).timestamp()
            if not start <= stamp < end:
                continue
            for block in row.get("message", {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_use" and (
                        block.get("name") in {"Agent", "Task", "spawn_agent"} or
                        str(block.get("name", "")).endswith("__spawn_agent")):
                    hidden_delegation.append({"session": path.stem, "tool": block["name"]})
    check("no native subagents outside FirstMate", not hidden_delegation, json.dumps(hidden_delegation))
    direct_edits = [c for c in calls if c.get("name") in {"Write", "Edit"} and
                    (str(lab.home / "projects") in str(c.get("input", {}).get("file_path", "")) or
                     "/.treehouse/" in str(c.get("input", {}).get("file_path", "")))]
    check("primary does not edit projects with file tools", not direct_edits, json.dumps(direct_edits))
    # Assert actual launched distinct tasks, not only role words in a prompt.
    tasks = []
    routing_path = lab.root / "evidence/routing.json"
    routing = json.loads(routing_path.read_text()) if routing_path.exists() else {}
    first_seen = {}
    first_done = {}
    for row in records(lab.root / "evidence/files.jsonl"):
        if row["path"].startswith("home/state/") and row["path"].endswith(".meta"):
            first_seen.setdefault(Path(row["path"]).stem, row["time"])
        elif row["path"].startswith("home/state/") and row["path"].endswith(".status"):
            obj = lab.root / "evidence/objects" / row["sha256"]
            if obj.exists() and re.search(r"^done:", obj.read_text(), re.M):
                first_done.setdefault(Path(row["path"]).stem, row["time"])
    for path in (lab.root / "evidence/home/state").glob("*.meta"):
        if start <= first_seen.get(path.stem, 0) < end:
            tasks.append((path.stem, metadata(path.read_text())))
    for project, artifact in artifacts.items():
        selected = [(task, meta) for task, meta in tasks if project in json.dumps(meta)]
        ships = [(task, meta) for task, meta in selected if meta.get("kind") == "ship"]
        scouts = [(task, meta) for task, meta in selected if meta.get("kind") == "scout"]
        check(project + " has native maker", ships, json.dumps([t for t, _ in selected]))
        check(project + " has independent scout", scouts and
              not ({t for t, _ in ships} & {t for t, _ in scouts}))
        reports = [(lab.root / "evidence/home/data" / task / "report.md") for task, _ in scouts]
        check(project + " scout evidence preserved", reports and all(p.is_file() and
              len(p.read_text().strip()) > 100 for p in reports))
        if ships:
            maker_time = min(first_seen[t] for t, _ in ships)
            reviewers = [t for t, _ in scouts if first_seen[t] >= maker_time]
            for task in reviewers:
                report = lab.root / "evidence/home/data" / task / "report.md"
                text = report.read_text() if report.exists() else ""
                candidates = reviewed_revisions(text)
                ancestors = [sha for sha in candidates if lab.call(
                    ["git", "merge-base", "--is-ancestor", sha, artifact["sha"]],
                    cwd=lab.home / "projects" / project, check=False).returncode == 0]
                check(task + " reviewed revision belongs to delivered history", ancestors,
                      json.dumps(sorted(candidates)))
        for task, meta in selected:
            brief = lab.root / "evidence/home/data" / task / "brief.md"
            check(task + " brief retained", brief.is_file())
            resolver_calls = [c for c in calls if "fm-dispatch-resolve.sh" in c.get("input", {}).get("command", "") and
                              re.search(rf"(?<![\w-]){re.escape(task)}(?![\w-])", c["input"]["command"])]
            check(task + " native resolver call associated with its brief", bool(resolver_calls))
            check(task + " harness recorded", bool(meta.get("harness")))
            check(task + " model and effort dispatch recorded", bool(meta.get("model")) and bool(meta.get("effort")))
            if meta.get("harness") == "claude":
                matched = task_sessions(routing, task, meta, first_seen[task])
                check(task + " actual model captured", matched and any(s.get("response_models") for s in matched))
                check(task + " native effort captured", matched and any(s.get("native_efforts") for s in matched))
            check(task + " native cleanup complete", not (lab.home / "state" / f"{task}.meta").exists())
            check(task + " completed natively", any(
                re.search(r"^done:", p.read_text(), re.M) for p in
                (lab.root / "evidence/home/state").glob(task + ".status")))
        if case in ("author", "saved") and project != "orchflows-home":
            check(project + " planning and review are separate", len(scouts) >= 2)
            check(project + " plan delivered", (Path(artifact["path"]) / "docs/change-plan.md").is_file())
            if ships and len(scouts) >= 2:
                maker_time = min(first_seen[t] for t, _ in ships)
                planners = [t for t, _ in scouts if first_seen[t] < maker_time]
                reviewers = [t for t, _ in scouts if first_seen[t] > maker_time]
                check(project + " plan precedes implementation and review follows", planners and reviewers)
                # Equal timestamps can occur when both changes were captured in one poll.
                check(project + " completed plan before maker", any(
                    first_done.get(t, float("inf")) <= maker_time for t in planners))
                check(project + " completed maker before review", any(
                    first_done.get(m, float("inf")) <= first_seen[r]
                    for m, _ in ships for r in reviewers))
    if case == "saved":
        author_result = lab.root / "checks/author/result.json"
        saved_sha = lab.call(["git", "rev-parse", "main"],
                             cwd=lab.home / "projects/orchflows-home").stdout.strip()
        author_sha = None
        if author_result.exists():
            author_sha = json.loads(author_result.read_text())["artifacts"]["orchflows-home"]["sha"]
        check("saved library reused without rewriting", saved_sha == author_sha)
        check("saved library home remains clean", not lab.call(
            ["git", "status", "--porcelain"], cwd=lab.home / "projects/orchflows-home").stdout.strip())
    # Tracked FirstMate source remains stock even if bootstrap writes private state.
    check("FirstMate tracked code unchanged", not lab.call(
        ["git", "diff", "HEAD", "--"], cwd=lab.fm).stdout.strip())
    check("FirstMate revision unchanged", lab.call(
        ["git", "rev-parse", "HEAD"], cwd=lab.fm).stdout.strip() == lab.config["firstmate_revision"])
    provenance = lab.root / "provenance.json"
    unchanged = False
    if provenance.exists():
        hashes = json.loads(provenance.read_text()).get("core_files_sha256", {})
        unchanged = bool(hashes) and all((lab.core / relative).is_file() and
                    hashlib.sha256((lab.core / relative).read_bytes()).hexdigest() == digest
                    for relative, digest in hashes.items())
    check("core package unchanged during live work", unchanged)
    return checks


def library_checks(path):
    checks = []

    def check(name, okay, detail=""):
        checks.append({"name": name, "passed": bool(okay), "detail": detail})

    library = path / "libraries/cashflow"
    versions = []
    for relative in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        p = library / relative
        try:
            data = json.loads(p.read_text())
            okay = isinstance(data, dict) and data.get("name") == "cashflow" and isinstance(data.get("version"), str) and bool(data["version"])
            if okay:
                versions.append(data["version"])
            check(relative + " no model or effort fields", not re.search(
                r'"(?:model|effort|harness|vendor)"\s*:', json.dumps(data)))
        except (OSError, ValueError):
            okay = False
        check("manifest " + relative, okay)
    check("host manifest versions agree", len(versions) == 3 and len(set(versions)) == 1)
    skills = list((library / "skills").glob("*/SKILL.md"))
    check("saved change workflow exists", (library / "skills/change/SKILL.md") in skills)
    for skill in skills:
        text = skill.read_text()
        check(skill.parent.name + " Claude manual-only", "disable-model-invocation: true" in text)
        policy = skill.parent / "agents/openai.yaml"
        check(skill.parent.name + " Codex manual-only", policy.is_file() and
              "allow_implicit_invocation: false" in policy.read_text())
        check(skill.parent.name + " portable instructions", not re.search(r"/home/|/var/tmp/|/mnt/[a-z]/|[A-Z]:\\", text))
        check(skill.parent.name + " no saved execution pins", not re.search(
            r"--(?:model|effort|harness)\b|gpt-\d|claude-(?:sonnet|opus|haiku)-\d|"
            r"(?mi:^\s*(?:model|effort|harness)\s*:)" , text))
    for directory in (library / "references", library / "guidance"):
        for instruction in directory.rglob("*.md"):
            text = instruction.read_text()
            check(str(instruction.relative_to(library)) + " portable instructions",
                  not re.search(r"/home/|/var/tmp/|/mnt/[a-z]/|[A-Z]:\\", text))
            check(str(instruction.relative_to(library)) + " no execution pins", not re.search(
                r"--(?:model|effort|harness)\b|gpt-\d|claude-(?:sonnet|opus|haiku)-\d|"
                r"(?mi:^\s*(?:model|effort|harness)\s*:)", text))
    trial_files = list((library / "trials").rglob("*.md"))
    check("observed trial recorded", len(trial_files) >= 2 and
          any("cashbook-trial" in p.read_text() for p in trial_files))
    check("dependency declaration", (library / "README.md").is_file() and
          "orchflows-firstmate" in (library / "README.md").read_text())
    return checks


def verify_case(lab, case):
    Collector(lab).collect()
    output = lab.root / "checks" / case
    output.mkdir(parents=True, exist_ok=True)
    projects = {"dynamic": ["cashbook-dynamic"], "author": ["cashbook-trial", "orchflows-home"],
                "saved": ["cashbook-saved"], "regression": ["cashbook-dynamic"]}[case]
    artifacts, checks = {}, []
    for project in projects:
        path, sha = export_main(lab, project, case)
        if project == "orchflows-home":
            result = {"checks": library_checks(path)}
            doctor = lab.call(["python3", "-B", lab.core / "scripts/orchflows.py", "doctor", "--home", path], check=False)
            try:
                healthy = doctor.returncode == 0 and json.loads(doctor.stdout).get("status") == "ready"
            except ValueError:
                healthy = False
            result["checks"].append({"name": "delivered home passes package doctor", "passed": healthy,
                                     "detail": doctor.stdout + doctor.stderr})
            result["passed"] = all(c["passed"] for c in result["checks"])
        else:
            result = ArtifactOracle(path, output / project, total=case == "regression").run()
            if case == "regression":
                result["checks"].extend(backward_compatibility(lab, path, output / "compatibility"))
                result["passed"] = all(c["passed"] for c in result["checks"])
        artifacts[project] = {"sha": sha, "path": str(path), **result}
    checks.extend(workflow_checks(lab, case, artifacts))
    result = {"passed": all(a["passed"] for a in artifacts.values()) and all(c["passed"] for c in checks),
              "artifacts": artifacts, "workflow_checks": checks}
    atomic_text(output / "result.json", json.dumps(result, indent=2) + "\n")
    lab.log("case-verified", case=case, passed=result["passed"], result=str(output / "result.json"))
    return result


def backward_compatibility(lab, current, output):
    baseline = lab.root / "checks/dynamic/result.json"
    if not baseline.exists():
        return [{"name": "original delivered baseline available", "passed": False, "detail": str(baseline)}]
    old_path = Path(json.loads(baseline.read_text())["artifacts"]["cashbook-dynamic"]["path"])
    old = ArtifactOracle(old_path, output / "before")
    new = ArtifactOracle(current, output / "after")
    inputs = ["account,amount\n", "account,amount\nz,0.1\nz,0.2\na,-0.00\n"]
    inputs += [generated(seed)[0] for seed in (0, 7, 15)]
    checks = []
    for i, data in enumerate(inputs):
        before = old.command(f"baseline {i}", ["moneylog.py", "-"], data.encode())
        after = new.command(f"regression {i}", ["moneylog.py", "-"], data.encode())
        checks.append({"name": f"default output byte-compatible with original commit ({i})",
                       "passed": before["returncode"] == after["returncode"] == 0 and
                                 before["stdout"] == after["stdout"] and before["stderr"] == after["stderr"],
                       "detail": json.dumps({"before": before, "after": after})})
    return checks
