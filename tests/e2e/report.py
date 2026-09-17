"""A compact shareable index; raw native transcripts stay in the private lab."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

from evidence import records, task_sessions


def write_report(lab, output):
    output = Path(output).resolve()
    if output == lab.root or lab.root in output.parents:
        raise ValueError("Choose a report directory outside the private lab")
    output.mkdir(parents=True, exist_ok=True)
    routing_path = lab.root / "evidence/routing.json"
    routing = json.loads(routing_path.read_text()) if routing_path.exists() else {}
    events = list(records(lab.root / "events.jsonl"))
    cases = []
    deliveries = []
    for case in ("dynamic", "author", "saved", "regression"):
        source = lab.root / "checks" / case / "result.json"
        if not source.exists():
            cases.append((case, "NOT VERIFIED", "NOT VERIFIED", "NOT VERIFIED", 0, []))
            continue
        result = json.loads(source.read_text())
        for project, artifact in result["artifacts"].items():
            deliveries.append((case, project, artifact["sha"], len(artifact["checks"])))
        checks = result["workflow_checks"] + [check for artifact in result["artifacts"].values()
                                              for check in artifact["checks"]]
        failures = [check["name"] for check in checks if not check["passed"]]
        artifacts_pass = all(a["passed"] for a in result["artifacts"].values())
        workflow_pass = all(c["passed"] for c in result["workflow_checks"] if "resolver" not in c["name"])
        resolver_pass = all(c["passed"] for c in result["workflow_checks"] if "resolver" in c["name"])
        cases.append((case, "PASS" if artifacts_pass else "FAIL", "PASS" if workflow_pass else "FAIL",
                      "PASS" if resolver_pass else "FAIL", len(checks), failures))
        target = output / case
        target.mkdir(exist_ok=True)
        shutil.copyfile(source, target / "result.json")
    if routing_path.exists():
        shutil.copyfile(routing_path, output / "routing.json")
    if (lab.root / "provenance.json").exists():
        shutil.copyfile(lab.root / "provenance.json", output / "provenance.json")
    lines = ["# FirstMate live E2E run", "",
             "Generated " + datetime.now(timezone.utc).isoformat(), "",
             f"FirstMate: `{lab.config['firstmate_revision']}`. Core: `{lab.core}`.",
             f"Private lab and full evidence: `{lab.root}`.", "",
             "| Case | Artifacts | Workflow assertions | Resolver calls | Assertions |", "| --- | --- | --- | --- | ---: |"]
    for case, artifacts, workflow, resolver, count, failures in cases:
        lines.append(f"| {case} | {artifacts} | {workflow} | {resolver} | {count} |")
    lines += ["", "The strict suite passes only when all three result columns pass.",
              "Workflow assertions exclude the separately displayed resolver checks.",
              "", "## Delivered commits", "", "| Case | Project | Commit | Artifact checks |",
              "| --- | --- | --- | ---: |"]
    for case, project, sha, count in deliveries:
        lines.append(f"| [{case}]({case}/result.json) | {project} | `{sha}` | {count} |")
    lines += ["", "## Dispatch and observed models", "",
              "`default` is a native dispatch choice, not a model name. Actual model IDs below come from native response records.",
              "", "| Task | Kind | Harness | Recorded model | Recorded effort | Native model | Native effort |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for task in sorted(routing.get("tasks", []), key=lambda item: item["task_id"]):
        meta = task["metadata"]
        sessions = task_sessions(routing, task["task_id"], meta)
        actual_models = sorted({m for s in sessions for m in s.get("response_models", [])})
        actual_efforts = sorted({e for s in sessions for e in s.get("native_efforts", [])})
        lines.append("| " + " | ".join([task["task_id"], *[
            meta.get(key, "unknown") for key in ("kind", "harness", "model", "effort")],
            ", ".join(actual_models) or "unknown", ", ".join(actual_efforts) or "unknown"]) + " |")
    models = sorted({model for session in routing.get("claude_sessions", {}).values()
                     for model in session.get("response_models", [])})
    lines += ["", "Observed Claude response model IDs: " + ", ".join(f"`{m}`" for m in models) + ".",
              "", "See `routing.json` for session IDs, working directories and native usage fields;",
              "`evidence/processes/history.jsonl` in the lab records observed launch flags.",
              "Missing effort is unknown. No monetary cost is estimated.", "", "## Failures and limits", ""]
    for case, artifacts, workflow, resolver, _, failures in cases:
        if artifacts != "PASS" or workflow != "PASS" or resolver != "PASS":
            lines.append(f"- {case}: " + ("; ".join(failures) or "not verified"))
    interventions = [e for e in events if e.get("kind") in ("operator-key", "case-timeout", "capture-error", "test-driver-restart")]
    lines += [f"- {len(interventions)} recorded dialog, timeout, capture-error or test-driver restart events; inspect `events.jsonl` for context.",
              "- Local-only projects, Claude primary, native default routing without injected profile rules. This does not test quota-array ranking, Typesafe routing, remote delivery or a Codex primary.",
              "- Ten-second observation interval; short-lived processes can be missed. Native transcripts and status history are retained separately.",
              "- Artifact exports and command-by-command expected checks live under `delivered/` and `checks/` in the private lab.",
              "- Full logs contain private local paths and native transcript content. Review before sharing."]
    (output / "report.md").write_text("\n".join(lines) + "\n")
    return output / "report.md"
