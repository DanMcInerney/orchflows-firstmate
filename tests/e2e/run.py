#!/usr/bin/env python3
"""Explicit opt-in live FirstMate E2E tests; run in Ubuntu/WSL."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

from lab import Lab, provision
from io_utils import atomic_text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--firstmate", required=True, type=Path)
    init.add_argument("--core", required=True, type=Path)
    init.add_argument("--tool-path", default=os.environ["PATH"])
    init.add_argument("--dispatch-from", type=Path, help="Copy an existing native crew-dispatch.json verbatim")
    commands.add_parser("start")
    commands.add_parser("launch", help="Recover provisioning before a primary pane exists")
    status = commands.add_parser("status")
    status.add_argument("--lines", type=int, default=40)
    send = commands.add_parser("send")
    send.add_argument("case", choices=("dynamic", "author", "saved", "regression"))
    key = commands.add_parser("key")
    key.add_argument("keys", nargs="+")
    commands.add_parser("collect")
    report = commands.add_parser("report")
    report.add_argument("--output", type=Path, required=True)
    commands.add_parser("close", help="Guarded lab teardown after all work is landed")
    observe = commands.add_parser("observe")
    observe.add_argument("--interval", type=float, default=10)
    verify = commands.add_parser("verify")
    verify.add_argument("case", choices=("dynamic", "author", "saved", "regression", "all"))
    verify.add_argument("--verbose", action="store_true")
    suite = commands.add_parser("suite")
    suite.add_argument("--timeout", type=int, default=3600, help="Seconds per case")
    suite.add_argument("--background", action="store_true")
    suite.add_argument("--resume", action="store_true", help="Reverify completed cases and continue; never resend unfinished work")
    suite.add_argument("--keep-going", action="store_true", help="Record assertion failures and exercise remaining completed-case dependencies")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Live tests must run in Linux; use WSL Ubuntu on Windows")
    if args.command == "init":
        lab = provision(args.root, args.firstmate, args.core, args.tool_path, args.dispatch_from)
        print(lab.root)
        return
    lab = Lab(args.root)
    if args.command == "start":
        lab.start()
    elif args.command == "launch":
        lab.launch()
    elif args.command == "status":
        print(lab.read(args.lines))
        from evidence import primary_records
        messages = [b.get("text", "") for r in primary_records(lab) if r.get("type") == "assistant"
                    for b in r.get("message", {}).get("content", [])
                    if isinstance(b, dict) and b.get("type") == "text"]
        if messages:
            print("Latest captured assistant message:\n" + messages[-1][:2000])
    elif args.command == "send":
        lab.log("case-start", case=args.case)
        lab.send((lab.root / "requests" / f"{args.case}.md").read_text())
    elif args.command == "key":
        lab.log("operator-key", keys=args.keys)
        lab.herdr("pane", "send-keys", lab.pane, *args.keys)
    elif args.command == "report":
        from report import write_report
        print(write_report(lab, args.output))
    elif args.command == "close":
        from evidence import Collector, completed, records
        Collector(lab).collect()
        if list((lab.home / "state").glob("*.meta")):
            raise RuntimeError("Live native tasks remain; finish them through FirstMate first")
        cases = {r["case"] for r in records(lab.root / "events.jsonl") if r.get("kind") == "case-start"}
        if any(not completed(lab, case) for case in cases):
            raise RuntimeError("An unfinished request remains; retain the lab for native recovery")
        for project in (lab.home / "projects").iterdir():
            if (project / ".git").exists() and lab.call(
                    ["git", "status", "--porcelain"], cwd=project).stdout.strip():
                raise RuntimeError(f"Uncommitted project changes remain: {project}")
        lab.call(["bash", lab.fm / "bin/fm-herdr-lab.sh", "teardown", lab.session])
        lab.log("lab-closed", session=lab.session)
    elif args.command in ("collect", "observe"):
        from evidence import Collector
        collector = Collector(lab)
        while True:
            collector.collect()
            if args.command == "collect" or (lab.root / "stop-observer").exists():
                break
            time.sleep(args.interval)
    elif args.command == "verify":
        from assertions import verify_case
        names = ("dynamic", "author", "saved", "regression") if args.case == "all" else (args.case,)
        results = {name: verify_case(lab, name) for name in names}
        aggregate_path = lab.root / "results.json"
        aggregate = json.loads(aggregate_path.read_text()) if aggregate_path.exists() else {}
        aggregate.update(results)
        atomic_text(aggregate_path, json.dumps(aggregate, indent=2) + "\n")
        summary = {name: {"passed": result["passed"], "failures": [
            check["name"] for check in result["workflow_checks"] + [
                c for a in result["artifacts"].values() for c in a["checks"]] if not check["passed"]]}
                   for name, result in results.items()}
        print(json.dumps(results if args.verbose else summary, indent=2))
        if not all(r["passed"] for r in results.values()):
            raise SystemExit(1)
    elif args.command == "suite":
        if args.background:
            pid = lab.background([sys.executable, str(Path(__file__).resolve()), "--root", str(lab.root),
                                  "suite", "--timeout", str(args.timeout),
                                  *(["--resume"] if args.resume else []),
                                  *(["--keep-going"] if args.keep_going else [])], "suite")
            print(f"Suite pid {pid}; progress: {lab.root / 'suite.log'}")
            return
        import fcntl
        from evidence import Collector, completed, records
        from assertions import verify_case
        lock = (lab.root / "suite.lock").open("a")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Another suite owns this lab") from None
        started = {r["case"] for r in records(lab.root / "events.jsonl") if r.get("kind") == "case-start"}
        if started and not args.resume:
            raise RuntimeError("Cases already started; use --resume or a fresh lab")
        collector = Collector(lab)
        results = {}
        for name in ("dynamic", "author", "saved", "regression"):
            collector.collect()
            if name in started:
                if not completed(lab, name):
                    raise RuntimeError(f"{name} is unfinished; use FirstMate to finish it, then --resume")
                results[name] = verify_case(lab, name)
                atomic_text(lab.root / "results.json", json.dumps(results, indent=2) + "\n")
                print(json.dumps({"case": name, "passed": results[name]["passed"],
                                  "result": str(lab.root / "checks" / name / "result.json")}), flush=True)
                if not results[name]["passed"] and not args.keep_going:
                    raise SystemExit(1)
                continue
            if name == "saved":
                lab.fresh_primary()
            lab.log("case-start", case=name)
            lab.send((lab.root / "requests" / f"{name}.md").read_text())
            deadline = time.monotonic() + args.timeout
            while time.monotonic() < deadline:
                collector.collect()
                if completed(lab, name):
                    break
                time.sleep(10)
            else:
                lab.log("case-timeout", case=name)
                raise RuntimeError(f"{name} timed out; lab retained at {lab.root}")
            results[name] = verify_case(lab, name)
            atomic_text(lab.root / "results.json", json.dumps(results, indent=2) + "\n")
            print(json.dumps({"case": name, "passed": results[name]["passed"],
                              "result": str(lab.root / "checks" / name / "result.json")}), flush=True)
            if not results[name]["passed"] and not args.keep_going:
                raise SystemExit(1)
        print(json.dumps({"suite_passed": all(r["passed"] for r in results.values())}), flush=True)
        if not all(r["passed"] for r in results.values()):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
