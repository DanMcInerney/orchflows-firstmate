#!/usr/bin/env python3
"""Prepare or run a private Linux FirstMate/Herdr readonly component acceptance."""
import argparse
import json
from pathlib import Path
import sys
import time

from linux_acceptance.runtime import preflight
from linux_acceptance.trial import Trial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("doctor", "fixture", "run"))
    parser.add_argument("--candidate", type=Path, required=True, help="Candidate reproduced by integrations/firstmate/prepare.py")
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--bin-dir", type=Path, action="append", default=[], help="Explicit native Linux dependency directory; repeatable")
    parser.add_argument("--work-root", type=Path, default=Path("/tmp/of-accept"))
    parser.add_argument("--primitive", choices=("Work", "Review"), default="Work")
    parser.add_argument("--model", default="claude-sonnet-5", help="Explicit Claude model inherited by every component")
    parser.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max"), default="high")
    parser.add_argument("--dynamic", action="store_true", help="Two writer Work results, joined candidate, one Review and checks")
    parser.add_argument("--authoring", action="store_true", help="Author and trial a non-delegating leaf library through dynamic local-only delivery")
    parser.add_argument("--authoring-repair", action="store_true", help="Author a leaf library, review it, then commit a bounded repair and fresh repair-trial evidence")
    parser.add_argument("--local-only", action="store_true", help="Deliver the dynamic result through an ordinary ship/local-only root")
    parser.add_argument("--enabled", action="store_true", help="Enable the project once; ordinary spawn attaches it")
    parser.add_argument("--custom-workflow", action="store_true", help="Invoke a retained custom one-primitive workflow (requires --enabled)")
    parser.add_argument("--restart", action="store_true", help="Replace the root through FirstMate while its component is pending")
    parser.add_argument("--replace-after", type=int, default=15, help="Seconds after observing the launched component")
    parser.add_argument("--component-delay", type=int, help="Foreground sleep; defaults to 60 with --restart, otherwise 330")
    parser.add_argument("--minimum-waiting-span", type=int, help="Required observed waiting span; defaults to 0 with --restart, otherwise 240")
    parser.add_argument("--timeout", type=int, default=900, help="Maximum component observation seconds, excluding setup/cleanup")
    parser.add_argument("--claude-access-token-file", type=Path, help="Explicit user-owned Claude cache: read only accessToken/expiresAt")
    parser.add_argument("--access-token-expires-at", type=float, help="Unix expiration of CLAUDE_CODE_OAUTH_TOKEN when known")
    args = parser.parse_args()
    if args.authoring_repair:
        args.authoring = True
    if args.authoring:
        if args.custom_workflow:
            parser.error("--authoring supplies its own authored leaf; omit --custom-workflow")
        args.dynamic = args.local_only = True
    if args.local_only and not args.dynamic:
        parser.error("--local-only requires --dynamic")
    if args.dynamic:
        args.enabled = True
        if args.primitive != "Work":
            parser.error("--dynamic selects Work plus Review; omit --primitive Review")
    if args.custom_workflow and not args.enabled:
        parser.error("--custom-workflow requires --enabled")
    if args.component_delay is None:
        args.component_delay = 60 if args.restart else 330
    if args.minimum_waiting_span is None:
        args.minimum_waiting_span = 0 if args.restart else 240
    if not 0 <= args.component_delay <= 360:
        parser.error("--component-delay must be between 0 and 360 seconds")
    if not 0 <= args.minimum_waiting_span <= args.component_delay:
        parser.error("--minimum-waiting-span must be between 0 and --component-delay")
    if not 120 <= args.timeout <= 3600 or args.timeout < args.component_delay + 120:
        parser.error("--timeout must be 120..3600 and at least --component-delay + 120")
    if not 0 <= args.replace_after < args.component_delay and args.restart:
        parser.error("--replace-after must be nonnegative and below --component-delay for --restart")
    try:
        probe, search_path = preflight(args)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Linux acceptance preflight failed: {error}\n")
    if args.command == "doctor":
        print(json.dumps(probe, indent=2, sort_keys=True))
        return 0
    if args.authoring_repair:
        from linux_acceptance.authoring_repair import AuthoringRepairTrial
        trial = AuthoringRepairTrial(args, probe, search_path)
    elif args.authoring:
        from linux_acceptance.authoring import AuthoringTrial
        trial = AuthoringTrial(args, probe, search_path)
    elif args.dynamic:
        from linux_acceptance.dynamic import DynamicTrial
        trial = DynamicTrial(args, probe, search_path)
    else:
        trial = Trial(args, probe, search_path)
    print(f"Private acceptance workspace: {trial.namespace}", flush=True)
    okay = False
    try:
        trial.stage()
        # Fixture preparation deliberately never reads authentication or starts a
        # server, model, watcher, endpoint, or component.
        if args.command == "run":
            trial.authenticate()
        project = trial.fixture()
        if args.command == "fixture":
            trial.prepare_root(project, "fm-lab-fixture")
            trial.receipt["status"] = "fixture-prepared-no-live-run"
            okay = True
        else:
            trial.select_session()
            trial.start_sentinel()
            okay = trial.run_component(project)
            trial.receipt["status"] = "passed" if okay else "failed"
    except (Exception, KeyboardInterrupt) as error:
        trial.receipt["status"] = "failed"
        # No raw subprocess exception or transcript can enter stdout.
        trial.receipt["error_type"] = type(error).__name__
        trial.receipt["error"] = trial.clean(str(error))
        print(f"Acceptance stopped: {type(error).__name__}; inspect the private receipt.", file=sys.stderr)
    finally:
        trial.cleanup()
        okay = okay and trial.receipt["cleanup_passed"]
        if not okay:
            trial.receipt["status"] = "failed"
        trial.receipt["finished_at"] = time.time()
        trial.save()
        print(f"Receipt: {trial.out / 'receipt.json'}", flush=True)
    return 0 if okay else 1


if __name__ == "__main__":
    raise SystemExit(main())
