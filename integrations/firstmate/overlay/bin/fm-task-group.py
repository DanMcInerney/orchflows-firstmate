#!/usr/bin/env python3
"""FirstMate Stage 1 task-group commands; requires an explicit owning home."""
import argparse
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True

from fm_task_group import TaskGroups
from fm_task_group_launch import launch_check, launch_meta, launch_overlay, launch_position
from fm_task_group_policy import claude_permissions
from fm_task_group_delivery import delivery_check
from fm_task_group_store import GroupError, identifier, read_json, safe_path


def bridge_call(owner, arguments, verify=False):
    bridge = safe_path(owner.code_root / "bin" / "fm-task-group-spawn.sh")
    environment = owner.runtime.environment(home=owner.home, code_root=owner.code_root)
    path_indexes = (3,) if arguments and arguments[0] == "--submit" else ()
    result = owner.runtime.run(bridge, arguments, path_indexes=path_indexes, env=environment,
                               capture_output=True, timeout=360, check=False)
    if verify:
        if result.returncode:
            raise GroupError("internal operation requires FirstMate parent lifecycle lock custody")
    else:
        sys.stdout.buffer.write(result.stdout)
        sys.stderr.buffer.write(result.stderr)
    return result.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", default=os.environ.get("FM_HOME"))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("protocol")
    attach = commands.add_parser("attach")
    attach.add_argument("task")
    attach.add_argument("--package", required=True)
    attach.add_argument("--project", required=True)
    attach.add_argument("--primitive", choices=("Work", "Review"), default="Work")
    attach.add_argument("--review-policy", choices=("none", "explicit-audit", "workflow-review"), default="none")
    attach.add_argument("--workflow", choices=("dynamic",))
    enable = commands.add_parser("enable", help="Enable one read-only primitive and libraries for a project's future scouts")
    enable.add_argument("--package", required=True)
    enable.add_argument("--project", required=True)
    enable.add_argument("--primitive", choices=("Work", "Review"), default="Work")
    enable.add_argument("--review-policy", choices=("none", "explicit-audit", "workflow-review"), default="none")
    enable.add_argument("--library", action="append", default=[])
    enable.add_argument("--workflow", choices=("dynamic",))
    disable = commands.add_parser("disable", help="Disable a default; keep existing task attachments")
    disable.add_argument("--project", required=True)
    for verb in ("submit", "status", "gather", "complete", "internal-submit", "internal-gather"):
        child = commands.add_parser(verb)
        child.add_argument("task")
        child.add_argument("--generation", required=True)
        if verb in ("submit", "internal-submit"):
            child.add_argument("--request", required=True)
        if verb in ("status", "gather", "internal-gather"):
            child.add_argument("--request-id")
        if verb == "complete":
            child.add_argument("--report", required=True)
    for verb in ("launch-check", "launch-overlay", "launch-meta", "waiting", "launch-claude-permissions", "auto-attach", "launch-context", "launch-position", "delivery-check"):
        child = commands.add_parser(verb)
        child.add_argument("task")
        if verb in ("launch-claude-permissions", "launch-context"):
            child.add_argument("--generation", required=True)
        if verb == "delivery-check":
            child.add_argument("--landing", action="store_true")
            child.add_argument("--teardown", action="store_true")
            child.add_argument("--reassigned", action="store_true")
        if verb == "auto-attach":
            child.add_argument("--workflow", choices=("default", "dynamic", "none"), default="default")
        if verb == "launch-position":
            child.add_argument("--worktree", required=True)
        if verb in ("launch-check", "auto-attach"):
            child.add_argument("--mode", default="")
            for argument in ("kind", "backend", "harness", "project"):
                child.add_argument("--" + argument, required=True)
            if verb == "launch-check":
                child.add_argument("--worktree")
    args = parser.parse_args(argv)
    try:
        if args.command == "protocol":
            print(json.dumps({"protocol": "firstmate-task-group", "version": 1,
                              "experimental": True, "scope": "local-readonly-work",
                              "runtime_verified": False,
                              "primitives": ["Work", "Review"],
                              "review_policies": ["explicit-audit", "workflow-review"],
                              "workflows": ["dynamic"],
                              "root_deliveries": ["ship-local-only"],
                              "commands": ["attach", "submit", "status", "gather", "complete",
                                           "waiting", "launch-check", "launch-meta", "launch-overlay"]}))
            return 0
        owner = TaskGroups(args.home)
        if args.command in ("submit", "gather", "internal-submit", "internal-gather"):
            identifier(args.task, "root ID")
            identifier(args.generation, "generation")
            if args.command.endswith("submit"):
                owner.request_body(read_json(args.request))
            if args.command.startswith("internal-"):
                bridge_call(owner, ["--verify-lock", args.task, args.generation], verify=True)
            else:
                arguments = ["--" + args.command, args.task, args.generation]
                if args.command == "submit":
                    arguments.append(str(safe_path(args.request)))
                elif args.request_id is not None:
                    arguments.append(identifier(args.request_id, "request ID"))
                return bridge_call(owner, arguments)
        if args.command in ("enable", "disable", "auto-attach", "launch-context", "launch-position"):
            import fm_orchflows
            if args.command == "enable":
                result = fm_orchflows.enable(owner, args.package, args.project, args.primitive,
                                            args.review_policy, args.library, workflow=args.workflow)
            elif args.command == "disable":
                result = fm_orchflows.disable(owner, args.project)
            elif args.command == "auto-attach":
                fm_orchflows.auto_attach(owner, args.task, args.kind, args.backend, args.harness, args.project, workflow=args.workflow, mode=args.mode)
                return 0
            elif args.command == "launch-position":
                launch_position(owner, args.task, args.worktree)
                return 0
            else:
                print(fm_orchflows.launch_context(owner, args.task, args.generation))
                return 0
        elif args.command == "attach":
            if args.workflow == "dynamic" and args.review_policy == "none":
                args.review_policy = "workflow-review"
            result = owner.attach(args.task, args.package, args.project, args.primitive, args.review_policy, workflow=args.workflow)
        elif args.command == "internal-submit":
            result = owner.submit(args.task, args.generation, read_json(args.request))
        elif args.command in ("status", "internal-gather"):
            result = owner.status(args.task, args.generation, gather=args.command == "internal-gather", request_id=args.request_id)
        elif args.command == "complete":
            result = owner.complete(args.task, args.generation, args.report)
        elif args.command == "waiting":
            result = owner.waiting(args.task)
        elif args.command == "launch-claude-permissions":
            result = claude_permissions(owner, args.task, args.generation)
        elif args.command == "delivery-check":
            delivery_check(owner, args.task, landing=args.landing,
                           teardown=args.teardown, reassigned=args.reassigned)
            return 0
        elif args.command == "launch-check":
            launch_check(owner, args.task, args.kind, args.backend, args.harness, args.project, args.worktree, mode=args.mode)
            return 0
        elif args.command == "launch-meta":
            print(launch_meta(owner, args.task), end="")
            return 0
        else:
            print(launch_overlay(owner, args.task), end="")
            return 0
        print(json.dumps(result, sort_keys=True))
        return 0
    except (GroupError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error), "execution_ready": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
