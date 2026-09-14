#!/usr/bin/env python3
"""Client for FirstMate's experimental local read-only Work or Review task group."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess


PROTOCOL = {"protocol": "firstmate-task-group", "version": 1,
            "experimental": True, "scope": "local-readonly-work"}
PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class ClientError(Exception):
    def __init__(self, message: str, operation: str, *, uncertain: bool = False):
        self.payload = {"error": message, "operation": operation,
                        "status": "uncertain" if uncertain else "rejected",
                        "retry_automatically": False}
        super().__init__(message)


class ControllerError(Exception):
    def __init__(self, payload: dict, returncode: int):
        self.payload = payload
        self.returncode = returncode if 0 < returncode < 126 else 2


def unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def parse_object(raw: str) -> dict:
    result = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(result, dict):
        raise ValueError("Expected one JSON object")
    return result


def package_identity() -> None:
    versions = set()
    try:
        for relative in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
            manifest = parse_object((PACKAGE_ROOT / relative).read_text(encoding="utf-8"))
            if manifest.get("name") != "orchflows-firstmate":
                raise ValueError("Package must identify as orchflows-firstmate")
            version = manifest.get("version")
            if not isinstance(version, str) or not version:
                raise ValueError("Package manifest needs a version")
            versions.add(version)
        if len(versions) != 1:
            raise ValueError("Package manifest versions disagree")
    except (OSError, ValueError) as exc:
        raise ClientError(f"Invalid fork package: {exc}", "preflight") from exc


def call_controller(args: argparse.Namespace, operation: str, *extra: str) -> dict:
    controller = args.firstmate_root / "bin/fm-task-group.py"
    if not controller.is_file():
        raise ClientError(f"FirstMate task-group controller is missing: {controller}", operation)
    command = [sys.executable, "-B", str(controller), "--home", str(args.home), operation, *extra]
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                timeout=args.timeout, env=environment, check=False)
    except subprocess.TimeoutExpired as exc:
        mutating = operation in {"submit", "gather"}
        message = ("Controller timed out; its outcome is unknown. Inspect FirstMate status "
                   "before any further action. A submission may still have launched a child."
                   if mutating else "Controller observation timed out; no mutation was requested.")
        raise ClientError(message, operation, uncertain=mutating) from exc
    except (OSError, UnicodeError) as exc:
        raise ClientError(f"Controller communication failed: {exc}", operation,
                          uncertain=operation in {"submit", "gather"}) from exc
    try:
        payload = parse_object(result.stdout or result.stderr)
    except ValueError as exc:
        raise ClientError(f"Controller returned malformed JSON (exit {result.returncode}): {exc}",
                          operation, uncertain=operation in {"submit", "gather"}) from exc
    if result.returncode:
        raise ControllerError(payload, result.returncode)
    if "error" in payload:
        raise ControllerError(payload, 2)
    return payload


def validate_protocol(response: dict, operation: str, *, primitive: str = "Work",
                      handshake: bool = True) -> None:
    expected = dict(PROTOCOL)
    if not handshake and primitive == "Review":
        expected["scope"] = "local-readonly-review"
    # bool is an int subclass; version true must not negotiate protocol version 1.
    if any(response.get(key) != value or type(response.get(key)) is not type(value)
           for key, value in expected.items()):
        raise ClientError("Unsupported FirstMate task-group protocol or scope", operation,
                          uncertain=operation in {"submit", "gather"})
    if handshake and primitive == "Review":
        for key, required in (("primitives", "Review"), ("review_policies", "explicit-audit")):
            capabilities = response.get(key)
            if (not isinstance(capabilities, list)
                    or any(not isinstance(value, str) for value in capabilities)
                    or len(set(capabilities)) != len(capabilities)
                    or required not in capabilities):
                raise ClientError("FirstMate must explicitly advertise Review and explicit-audit support",
                                  operation)


def validate_view(response: dict, args: argparse.Namespace, operation: str) -> None:
    primitive = getattr(args, "primitive", "Work")
    validate_protocol(response, operation, primitive=primitive, handshake=False)
    attachment = response.get("attachment")
    if (response.get("attached") is not True or response.get("root") != args.root
            or response.get("generation") != args.generation or not isinstance(attachment, dict)):
        raise ClientError("FirstMate did not confirm this attached root and generation", operation,
                          uncertain=operation in {"submit", "gather"})
    expected = {"schema": 1, "root": args.root, "epoch": 1, "primitive": primitive,
                "readonly": True, "max_components": 1}
    if primitive == "Review":
        expected["review_policy"] = "explicit-audit"
    if (any(attachment.get(key) != value or type(attachment.get(key)) is not type(value)
            for key, value in expected.items())
            or type(response.get("epoch")) is not int or response["epoch"] != 1
            or (primitive == "Work" and attachment.get("review_policy", "none") != "none")):
        raise ClientError("Unsupported FirstMate task-group attachment or review policy", operation,
                          uncertain=operation in {"submit", "gather"})
    package_path = attachment.get("package_path")
    digest = attachment.get("package_digest")
    try:
        matching_path = (isinstance(package_path, str) and Path(package_path).is_absolute()
                         and Path(package_path).resolve() == PACKAGE_ROOT)
    except (OSError, ValueError, RuntimeError):
        matching_path = False
    if (not matching_path or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None):
        raise ClientError("Run the client from the exact FirstMate-attached fork snapshot", operation,
                          uncertain=operation in {"submit", "gather"})


def validate_request(path: Path, primitive: str = "Work") -> None:
    try:
        request = parse_object(path.read_text(encoding="utf-8"))
        if set(request) != {"request_id", "assignment"}:
            raise ValueError("Request must contain exactly request_id and assignment")
        if any(not isinstance(request[key], str) or not request[key].strip() for key in request):
            raise ValueError("request_id and assignment must be nonempty strings")
    except (OSError, ValueError) as exc:
        raise ClientError(f"Invalid {primitive} request: {exc}", "preflight") from exc


def run(args: argparse.Namespace) -> dict:
    package_identity()
    primitive = getattr(args, "primitive", "Work")
    if primitive not in ("Work", "Review"):
        raise ClientError("Primitive must be Work or Review", "preflight")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        raise ClientError("Timeout must be a finite positive number", "preflight")
    if any(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value) is None
           for value in (args.root, args.generation)):
        raise ClientError("Root and current generation must be valid FirstMate identifiers", "preflight")
    if args.operation == "submit":
        validate_request(args.request, primitive)
    validate_protocol(call_controller(args, "protocol"), "protocol", primitive=primitive)
    identity = (args.root, "--generation", args.generation)
    current = call_controller(args, "status", *identity)
    validate_view(current, args, "status")
    if args.operation == "status":
        return current
    extra = ("--request", str(args.request)) if args.operation == "submit" else ()
    outcome = call_controller(args, args.operation, *identity, *extra)
    validate_view(outcome, args, args.operation)
    return outcome


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firstmate-root", required=True, type=lambda value: Path(value).expanduser().resolve(),
                        help="Explicit experimental FirstMate code root containing bin/fm-task-group.py")
    parser.add_argument("--home", required=True, type=lambda value: Path(value).expanduser().resolve(),
                        help="Owning FirstMate home; not the Orchflows package home")
    parser.add_argument("--root", required=True, help="Attached normal root scout task ID")
    parser.add_argument("--generation", required=True, help="Current root spawn_gen from FirstMate")
    parser.add_argument("--primitive", choices=("Work", "Review"), default="Work",
                        help="Attachment primitive to validate (default: Work)")
    parser.add_argument("--timeout", type=float, default=420, help="Seconds per controller call (default: 420)")
    commands = parser.add_subparsers(dest="operation", required=True)
    commands.add_parser("status", help="Validate protocol, root generation and exact package attachment")
    submit = commands.add_parser("submit", help="Submit the group's one read-only assignment")
    submit.add_argument("--request", required=True, type=lambda value: Path(value).expanduser().resolve())
    commands.add_parser("gather", help="Gather and acknowledge the retained result through FirstMate")
    args = parser.parse_args(argv)
    try:
        payload, code = run(args), 0
    except ClientError as exc:
        payload, code = exc.payload, 2
    except ControllerError as exc:
        payload, code = exc.payload, exc.returncode
    print(json.dumps(payload))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
