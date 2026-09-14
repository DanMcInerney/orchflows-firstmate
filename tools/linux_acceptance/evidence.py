"""Scoped assertions for retained results and the private Claude read observer."""
from datetime import datetime
import json
from pathlib import Path
import shlex


def read_order(namespace, home, run):
    root = run["root"]
    cwd = run["metadata"].get(root, {}).get("worktree")
    request = run.get("request") or {}
    child = request.get("child")
    if not cwd or not child:
        return {"read_both_before_first_gather": False, "reason": "missing root or child identity"}
    retained = home / "data" / root / "task-group/results" / child
    targets = {str(retained / "report.md"): "report", str(retained / "result.json"): "result"}
    expected = {kind: Path(path).read_text() for path, kind in targets.items()}
    events = []
    for path in (namespace / "claude/projects").rglob("*.jsonl"):
        if path.is_symlink() or not path.resolve().is_relative_to(namespace):
            continue
        pending = {}
        # Examine native transcripts in memory; retain only scoped event facts.
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if record.get("cwd") != cwd or record.get("isSidechain") is True:
                    continue
                content = record.get("message", {}).get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use":
                        inputs, event = block.get("input", {}), None
                        if block.get("name") == "Read" and inputs.get("file_path") in targets:
                            event = {"kind": "read", "file": targets[inputs["file_path"]],
                                     "unlimited": inputs.get("offset") in (None, 1) and inputs.get("limit") is None}
                        elif block.get("name") == "Bash":
                            command = inputs.get("command", "")
                            try:
                                argv = shlex.split(command)
                            except ValueError:
                                argv = []
                            if (argv and Path(argv[0]).name in ("python", "python3") and
                                any(arg.endswith("/scripts/firstmate.py") for arg in argv) and
                                any(operation in argv for operation in ("submit", "gather")) and root in argv and
                                not any(term in command for term in ("\n", ";", "&&", "||", chr(96)))):
                                event = {"kind": "gather" if "gather" in argv else "submit"}
                        if event is not None:
                            event["invoked_at"] = record.get("timestamp")
                            pending[block.get("id")] = event
                            events.append(event)
                    elif block.get("type") == "tool_result" and block.get("tool_use_id") in pending:
                        event = pending[block["tool_use_id"]]
                        event.update(success=block.get("is_error") is not True, result_at=record.get("timestamp"))
                        if event["kind"] == "submit" and event.get("success"):
                            payload = block.get("content", "")
                            if isinstance(payload, list):
                                payload = "\n".join(part.get("text", "") for part in payload if isinstance(part, dict))
                            if isinstance(payload, str):
                                decoder = json.JSONDecoder()
                                for position, char in enumerate(payload):
                                    if char != "{":
                                        continue
                                    try:
                                        value, _ = decoder.raw_decode(payload[position:])
                                    except ValueError:
                                        continue
                                    if isinstance(value, dict) and isinstance(value.get("request"), dict):
                                        event["returned_child"] = value["request"].get("child")
                                        event["returned_request_id"] = value["request"].get("body", {}).get("request_id")
                                        break
                        if event["kind"] == "read":
                            payload = block.get("content", "")
                            if isinstance(payload, list):
                                payload = "\n".join(part.get("text", "") for part in payload if isinstance(part, dict))
                            if not isinstance(payload, str):
                                payload = ""
                            body = expected[event["file"]]
                            event["full_content_observed"] = bool(body) and all(
                                text.strip() in payload for text in body.splitlines() if text.strip())
    def timestamp(value):
        try:
            return datetime.fromisoformat(value).timestamp()
        except (ValueError, TypeError):
            return float("inf")
    submissions = [event for event in events if event["kind"] == "submit" and event.get("success")]
    gathers = [event for event in events if event["kind"] == "gather"]
    first = min((timestamp(event["invoked_at"]) for event in gathers), default=float("-inf"))
    acknowledged = request.get("gathered_at")
    ack = acknowledged if isinstance(acknowledged, (float, int)) else float("-inf")
    def before(cutoff):
        return all(any(event["kind"] == "read" and event["file"] == kind and
                       event.get("success") and event["unlimited"] and event.get("full_content_observed") and
                       timestamp(event.get("result_at")) < cutoff for event in events)
                   for kind in ("report", "result"))
    return {"scope": "private native Read/Bash observation; first literal gather and durable first owner acknowledgement",
            "read_both_before_first_gather": before(first),
            "read_both_before_owner_acknowledgement": before(ack),
            "recognized_gather_count": len(gathers),
            "successful_submissions": len(submissions),
            "same_child_replay": len(submissions) >= 2 and all(
                event.get("returned_child") == child and
                event.get("returned_request_id") == request.get("body", {}).get("request_id")
                for event in submissions),
            "events": events}


def assess(run, *, restart, minimum_waiting_span):
    request = run.get("request") or {}
    samples = run.get("watch_samples", [])
    waiting = [sample for sample in samples
               if sample.get("root_current_exit") == 0 and sample.get("child_current_exit") == 0
               and sample.get("root_current", "").startswith("state: waiting · source: task-group · ")
               and sample.get("child_current", "").startswith(("state: working · source: pane · ",
                                                               "state: working · source: run-step · "))
               and sample.get("arm_exit") is None and sample.get("beacon_age_seconds", float("inf")) < 60]
    span = waiting[-1]["at"] - waiting[0]["at"] if len(waiting) >= 2 else 0
    locks = {sample["watcher_lock"] for sample in waiting}
    status = run.get("root_status", "").splitlines()
    result = {
        "root_spawn_succeeded": run.get("spawn_exit") == 0,
        "ordinary_root_done": bool(status) and status[-1].startswith("done:"),
        "one_component": run.get("component_count") == 1,
        "same_child_replay": run.get("read_order", {}).get("same_child_replay") is True,
        "retained_result_integrity": run.get("retained_integrity_matches") is True,
        "component_gathered": request.get("state") == "complete" and request.get("gathered") is True,
        "source_findings_in_root_report": run.get("source_findings_present") is True,
        "fixture_unchanged": run.get("input_status") == "" and run.get("input_commit_unchanged") is True,
        "worktrees_unchanged": bool(run.get("worktree_status")) and
                              all(value == "" for value in run.get("worktree_status", {}).values()),
        "full_reads_before_gather": run.get("read_order", {}).get("read_both_before_first_gather") is True
                                  and run.get("read_order", {}).get("read_both_before_owner_acknowledgement") is True,
        "watcher_waiting_span": minimum_waiting_span == 0 or (span >= minimum_waiting_span and len(locks) == 1 and None not in locks),
        "no_watcher_exit_while_pending": restart or not run.get("watcher_ended_while_pending", False),
    }
    if restart:
        replacement = run.get("replacement", {})
        current = run.get("metadata", {}).get(run["root"], {}).get("spawn_gen")
        result["replacement_preserved_child"] = replacement.get("exit") == 0 and (
            replacement.get("before_generation") != current) and replacement.get("child") == request.get("child")
        result["gathered_by_replacement"] = request.get("gathered_parent_gen") == current and current is not None
    return {"passed": all(result.values()), "checks": result,
            "minimum_waiting_span_seconds": minimum_waiting_span, "restart_requested": restart,
            "waiting_samples": len(waiting), "waiting_span_seconds": round(span, 3)}
