#!/usr/bin/env python3
"""Client for FirstMate-owned Work, Review and bounded Linux dynamic workflows."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess


PROTOCOL = {"protocol": "firstmate-task-group", "version": 1,
            "experimental": True, "scope": "local-readonly-work"}
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CONTEXT_ENV = "ORCHFLOWS_FIRSTMATE_CONTEXT"
CONTEXT_LIMIT = 16 * 1024
AUTHORITY_FIELDS = ("firstmate_root", "home", "root", "generation", "primitive")
CONTEXT_FIELDS = {"schema", *AUTHORITY_FIELDS, "package_path"}
IDENTIFIER = r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}"
DYNAMIC_FIELDS = {"request_id", "assignment", "primitive", "writable"}


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


def context_path(value: str, *, directory: bool = False) -> Path:
    if not isinstance(value, str) or not value or "\0" in value:
        raise ValueError("Context paths must be nonempty strings without NUL")
    path = Path(value)
    if not path.is_absolute():
        raise ValueError("Context authority paths must be absolute")
    # Do not resolve away a symlink or a parent traversal supplied as authority.
    if path.resolve(strict=True) != path or any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("Context paths must be canonical and contain no symlinks")
    if directory and not path.is_dir():
        raise ValueError("Context authority paths must identify existing directories")
    return path


def read_context(path: Path) -> dict:
    try:
        path = context_path(str(path.expanduser().absolute()))
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        with os.fdopen(os.open(path, flags), "rb") as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > CONTEXT_LIMIT:
                raise ValueError("Context must be a regular JSON file of at most 16 KiB")
            raw = stream.read(CONTEXT_LIMIT + 1)
        if len(raw) > CONTEXT_LIMIT:
            raise ValueError("Context exceeds 16 KiB")
        context = parse_object(raw.decode("utf-8"))
        if set(context) != CONTEXT_FIELDS:
            raise ValueError("Context must contain exactly schema, firstmate_root, home, root, "
                             "generation, primitive and package_path")
        if type(context["schema"]) is not int or context["schema"] != 1:
            raise ValueError("Unsupported FirstMate launch context schema")
        for key in ("firstmate_root", "home", "package_path"):
            context[key] = context_path(context[key], directory=True)
        if context["package_path"] != PACKAGE_ROOT:
            raise ValueError("Run the client from the exact context package snapshot")
        return context
    except (OSError, ValueError, UnicodeError, RuntimeError) as exc:
        raise ClientError(f"Invalid FirstMate launch context: {exc}", "preflight") from exc


def resolve_authority(args: argparse.Namespace) -> argparse.Namespace:
    # Keep imported run(args) callers and repeated calls from changing their inputs.
    args = argparse.Namespace(**vars(args))
    context = getattr(args, "context", None)
    if context is None:
        context = os.environ.get(CONTEXT_ENV)
    if context is not None:
        if any(getattr(args, key, None) is not None for key in AUTHORITY_FIELDS):
            raise ClientError("Launch context cannot be mixed with manual authority flags", "preflight")
        if not str(context):
            raise ClientError("FirstMate launch context path must not be empty", "preflight")
        selected = read_context(Path(context))
        for key in AUTHORITY_FIELDS:
            setattr(args, key, selected[key])
    else:
        if any(getattr(args, key, None) is None for key in AUTHORITY_FIELDS[:-1]):
            raise ClientError("FirstMate launch context or complete explicit authority is required", "preflight")
        args.primitive = getattr(args, "primitive", None) or "Work"
    return args


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
                      handshake: bool = True, workflow: str | None = None) -> None:
    expected = dict(PROTOCOL)
    if not handshake:
        if workflow == "dynamic":
            expected["scope"] = "local-dynamic"
        elif primitive == "Review":
            expected["scope"] = "local-readonly-review"
    # bool is an int subclass; version true must not negotiate protocol version 1.
    if any(response.get(key) != value or type(response.get(key)) is not type(value)
           for key, value in expected.items()):
        raise ClientError("Unsupported FirstMate task-group protocol or scope", operation,
                          uncertain=operation in {"submit", "gather"})
    if handshake and (primitive == "Review" or workflow == "dynamic"):
        required_capabilities = (("primitives", "Review"), ("review_policies", "explicit-audit"))
        if workflow == "dynamic":
            required_capabilities = (("primitives", "Work"), ("primitives", "Review"),
                                     ("workflows", "dynamic"), ("review_policies", "workflow-review"))
        for key, required in required_capabilities:
            capabilities = response.get(key)
            if (not isinstance(capabilities, list)
                    or any(not isinstance(value, str) for value in capabilities)
                    or len(set(capabilities)) != len(capabilities)
                    or required not in capabilities):
                raise ClientError("FirstMate must explicitly advertise " +
                                  ("dynamic, Work, Review and workflow-review support"
                                   if workflow == "dynamic" else "Review and explicit-audit support"),
                                  operation)


def validate_view(response: dict, args: argparse.Namespace, operation: str) -> None:
    primitive = getattr(args, "primitive", "Work")
    attachment = response.get("attachment")
    workflow = attachment.get("workflow") if isinstance(attachment, dict) else None
    validate_protocol(response, operation, primitive=primitive, handshake=False, workflow=workflow)
    if (response.get("attached") is not True or response.get("root") != args.root
            or response.get("generation") != args.generation or not isinstance(attachment, dict)):
        raise ClientError("FirstMate did not confirm this attached root and generation", operation,
                          uncertain=operation in {"submit", "gather"})
    expected = {"schema": 1, "root": args.root, "epoch": 1, "primitive": primitive,
                "readonly": True, "max_components": 1}
    if workflow == "dynamic":
        expected.update(workflow="dynamic", primitive="Work", review_policy="workflow-review",
                        readonly=False, max_components=32)
    elif primitive == "Review":
        expected["review_policy"] = "explicit-audit"
    if (workflow not in (None, "dynamic")
            or (workflow == "dynamic" and (primitive != "Work" or sys.platform != "linux"))
            or any(attachment.get(key) != value or type(attachment.get(key)) is not type(value)
            for key, value in expected.items())
            or type(response.get("epoch")) is not int or response["epoch"] != 1
            or (workflow is None and primitive == "Work"
                and attachment.get("review_policy", "none") != "none")):
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


def validate_request(path: Path, primitive: str = "Work") -> dict:
    """Validate syntax before controller calls; the attachment selects the shape."""
    try:
        request = parse_object(path.read_text(encoding="utf-8"))
        fields = set(request)
        if fields != {"request_id", "assignment"} and not (
                primitive == "Work" and fields == DYNAMIC_FIELDS):
            raise ValueError("Request must contain request_id and assignment, with primitive and "
                             "writable only for a dynamic attachment")
        for key in ("request_id", "assignment"):
            if not isinstance(request[key], str) or not request[key].strip():
                raise ValueError("request_id and assignment must be nonempty strings")
        if re.fullmatch(IDENTIFIER, request["request_id"]) is None:
            raise ValueError("request_id must be a valid FirstMate identifier")
        if "\0" in request["assignment"] or len(request["assignment"].encode("utf-8")) > 32768:
            raise ValueError("assignment must be at most 32768 UTF-8 bytes without NUL")
        if fields == DYNAMIC_FIELDS:
            if request["primitive"] not in ("Work", "Review") or type(request["writable"]) is not bool:
                raise ValueError("dynamic requests require primitive Work or Review and boolean writable")
            if request["primitive"] == "Review" and request["writable"]:
                raise ValueError("Review must be read-only")
        return request
    except (OSError, ValueError, UnicodeError) as exc:
        raise ClientError(f"Invalid {primitive} request: {exc}", "preflight") from exc


def validate_selection(response: dict, request_id: str, operation: str, *,
                       body: dict | None = None) -> None:
    request = response.get("request")
    observed = request.get("body") if isinstance(request, dict) else None
    if (not isinstance(observed, dict) or observed.get("request_id") != request_id
            or (body is not None and observed != body)):
        raise ClientError("FirstMate did not confirm the selected request", operation,
                          uncertain=operation in {"submit", "gather"})


def run(args: argparse.Namespace) -> dict:
    args = resolve_authority(args)
    package_identity()
    primitive = getattr(args, "primitive", "Work")
    if primitive not in ("Work", "Review"):
        raise ClientError("Primitive must be Work or Review", "preflight")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        raise ClientError("Timeout must be a finite positive number", "preflight")
    if any(not isinstance(value, str)
           or re.fullmatch(IDENTIFIER, value) is None
           for value in (args.root, args.generation)):
        raise ClientError("Root and current generation must be valid FirstMate identifiers", "preflight")
    request_id = getattr(args, "request_id", None)
    if request_id is not None and (
            not isinstance(request_id, str) or re.fullmatch(IDENTIFIER, request_id) is None):
        raise ClientError("Request ID must be a valid FirstMate identifier", "preflight")
    request = validate_request(args.request, primitive) if args.operation == "submit" else None
    protocol = call_controller(args, "protocol")
    validate_protocol(protocol, "protocol", primitive=primitive)
    identity = (args.root, "--generation", args.generation)
    selection = ("--request-id", request_id) if request_id is not None else ()
    current = call_controller(args, "status", *identity, *selection)
    validate_view(current, args, "status")
    workflow = current["attachment"].get("workflow")
    if request_id is not None:
        validate_selection(current, request_id, "status")
    if workflow == "dynamic":
        validate_protocol(protocol, "protocol", primitive=primitive, workflow=workflow)
    if request is not None:
        expected_fields = DYNAMIC_FIELDS if workflow == "dynamic" else {"request_id", "assignment"}
        if set(request) != expected_fields:
            raise ClientError("Request fields must match the admitted " +
                              ("dynamic" if workflow == "dynamic" else "single-primitive") +
                              " attachment", "preflight")
    if args.operation == "status":
        return current
    if args.operation == "gather" and workflow == "dynamic" and request_id is None:
        raise ClientError("Dynamic gather requires --request-id", "preflight")
    extra = ("--request", str(args.request)) if args.operation == "submit" else selection
    outcome = call_controller(args, args.operation, *identity, *extra)
    validate_view(outcome, args, args.operation)
    if request_id is not None:
        validate_selection(outcome, request_id, args.operation)
    elif workflow == "dynamic" and request is not None:
        validate_selection(outcome, request["request_id"], args.operation, body=request)
    if outcome["attachment"] != current["attachment"]:
        raise ClientError("FirstMate attachment changed during the operation", args.operation,
                          uncertain=True)
    return outcome


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", type=Path,
                        help="FirstMate launch context JSON (default: ORCHFLOWS_FIRSTMATE_CONTEXT)")
    parser.add_argument("--firstmate-root", type=lambda value: Path(value).expanduser().resolve(),
                        help="Explicit experimental FirstMate code root containing bin/fm-task-group.py")
    parser.add_argument("--home", type=lambda value: Path(value).expanduser().resolve(),
                        help="Owning FirstMate home; not the Orchflows package home")
    parser.add_argument("--root", help="Attached normal root scout task ID")
    parser.add_argument("--generation", help="This launch's root spawn_gen from FirstMate")
    parser.add_argument("--primitive", choices=("Work", "Review"),
                        help="Explicit attachment primitive (default without launch context: Work)")
    parser.add_argument("--timeout", type=float, default=420, help="Seconds per controller call (default: 420)")
    commands = parser.add_subparsers(dest="operation", required=True)
    status = commands.add_parser("status", help="Inspect the group or one selected request")
    status.add_argument("--request-id", help="Observe this retained logical request")
    submit = commands.add_parser("submit", help="Submit an assignment admitted by the attachment")
    submit.add_argument("--request", required=True, type=lambda value: Path(value).expanduser().resolve())
    gather = commands.add_parser("gather", help="Gather and acknowledge a retained result")
    gather.add_argument("--request-id", help="Logical request to acknowledge (required for dynamic)")
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
