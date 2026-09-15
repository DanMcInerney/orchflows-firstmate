#!/usr/bin/env python3
"""FirstMate-owned workflow discovery and committed-library publication."""
import argparse
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True

from fm_task_group import TaskGroups
from fm_task_group_store import GroupError
import fm_orchflows_home


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", default=os.environ.get("FM_HOME"))
    parser.add_argument("--workflow-home", help="Explicit editable workflow home")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("setup", help="Initialize or update the FirstMate workflow home")
    prepare.add_argument("--package")
    commands.add_parser("catalog", help="List available library:skill identities")
    for verb in ("resolve", "brief"):
        child = commands.add_parser(verb)
        child.add_argument("identity")
    publish = commands.add_parser("publish", help="Save a delivered library and refresh future task bundles")
    publish.add_argument("--project", required=True)
    publish.add_argument("--library", required=True, help="Library directory relative to the project")
    publish.add_argument("--commit", required=True, help="Exact delivered commit on local default")
    publish.add_argument("--package", help="Core package source for first-time setup or upgrade")
    args = parser.parse_args(argv)
    try:
        owner = TaskGroups(args.home)
        if args.command == "setup":
            result = fm_orchflows_home.setup(owner, args.package, args.workflow_home)
        elif args.command == "catalog":
            result = fm_orchflows_home.catalog(owner, args.workflow_home)
        elif args.command == "resolve":
            result = fm_orchflows_home.resolve(owner, args.identity, args.workflow_home)
        elif args.command == "brief":
            print(fm_orchflows_home.brief(owner, args.identity, args.workflow_home), end="")
            return 0
        else:
            result = fm_orchflows_home.publish(owner, args.project, args.library, args.commit,
                                               args.package, args.workflow_home)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (GroupError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error), "execution_ready": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
