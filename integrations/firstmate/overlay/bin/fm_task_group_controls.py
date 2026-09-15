"""Optional assignment controls resolved through FirstMate's profile owner."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from fm_task_group_store import GroupError, canonical, digest, identifier, read_json

CONTROL_FIELDS = {"model", "effort", "operation_defaults", "assignment_name"}
CAPABILITY = "model-effort-v1"
EFFORTS = {"default", "low", "medium", "high", "xhigh", "max", "ultra"}
MODEL = r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}"


def validate_axes(value):
    if not isinstance(value, dict) or not set(value) <= {"model", "effort"}:
        raise GroupError("assignment preferences contain only model and effort")
    if "model" in value and (not isinstance(value["model"], str) or
                             re.fullmatch(MODEL, value["model"]) is None):
        raise GroupError("model must be a concrete harness model token or default")
    if "effort" in value and (not isinstance(value["effort"], str) or value["effort"] not in EFFORTS):
        raise GroupError("effort must be default, low, medium, high, xhigh, max or ultra")
    return value


def validate_request_controls(body):
    validate_axes({key: body[key] for key in ("model", "effort") if key in body})
    if "operation_defaults" in body:
        validate_axes(body["operation_defaults"])
    if "assignment_name" in body:
        identifier(body["assignment_name"], "assignment name")
    return body


def validate_preferences(value):
    if not isinstance(value, dict) or not set(value) <= {"assignments", "operations"}:
        raise GroupError("workflow preferences contain assignments and operations maps")
    for kind in ("assignments", "operations"):
        entries = value.get(kind, {})
        if not isinstance(entries, dict) or len(entries) > (32 if kind == "assignments" else 2):
            raise GroupError("workflow preferences exceed their bounded assignment/operation maps")
        for name, axes in entries.items():
            if kind == "assignments":
                identifier(name, "assignment name")
            elif name not in ("Work", "Review"):
                raise GroupError("operation preferences must select Work or Review")
            validate_axes(axes)
    return value


def supports_controls(package):
    path = Path(package) / "scripts" / "firstmate-client.json"
    if not path.exists():
        return False
    value = read_json(path)
    return value.get("schema") == 1 and value.get("assignment_controls") == [CAPABILITY]


def resolve_axes(body, preferences, primitive):
    """Each axis has independent caller-named/operation then saved precedence."""
    validate_request_controls(body)
    preferences = validate_preferences(preferences)
    name = body.get("assignment_name", body["request_id"])
    choices = [
        ("caller-named", body),
        ("caller-operation", body.get("operation_defaults", {})),
        ("saved-named", preferences.get("assignments", {}).get(name, {})),
        ("saved-operation", preferences.get("operations", {}).get(primitive, {})),
        ("firstmate-default", {"model": "default", "effort": "default"}),
    ]
    selected, sources = {}, {}
    for axis in ("model", "effort"):
        for source, values in choices:
            if axis in values:
                selected[axis], sources[axis] = values[axis], source
                break
    return selected, sources


def validate_owner_profile(owner, harness, model, effort):
    # FirstMate owns model interpretation, harness choice and the actual flags.
    # The same flag functions are called by fm-spawn.sh at its launch boundary.
    command = owner.code_root / "bin" / "fm-harness.sh"
    if not command.is_file():
        raise GroupError("FirstMate assignment profile owner is unavailable")
    result = owner.runtime.run(
        command, ["workflow-profile", harness, model, effort],
        env=owner.runtime.environment(home=owner.home, code_root=owner.code_root),
        capture_output=True, timeout=10, check=False)
    lines = result.stdout.decode("utf-8").splitlines() if isinstance(result.stdout, bytes) else result.stdout.splitlines()
    if result.returncode or lines != [harness, model, effort]:
        message = result.stderr.decode("utf-8", errors="replace") if isinstance(result.stderr, bytes) else result.stderr
        raise GroupError("FirstMate refused assignment profile: " + (message.strip() or "profile flags unavailable")[:1024])


def resolve_profile(owner, parent, attachment, body):
    modern = supports_controls(attachment["package_path"])
    if not modern:
        if CONTROL_FIELDS & set(body) or attachment.get("workflow_preferences"):
            raise GroupError("attached client must negotiate model-effort-v1 assignment controls")
        return {axis: parent.get(axis, "default") for axis in ("harness", "model", "effort")}
    primitive = body.get("primitive", attachment.get("primitive", "Work"))
    axes, sources = resolve_axes(body, attachment.get("workflow_preferences", {}), primitive)
    # The existing FirstMate intake selected this caller's harness. A model
    # token never changes the harness, provider, credentials or endpoint owner.
    profile = {"harness": parent["harness"], **axes, "sources": sources}
    validate_owner_profile(owner, profile["harness"], profile["model"], profile["effort"])
    return {key: profile[key] for key in ("harness", "model", "effort")} | {
        "profile": profile,
        "profile_hash": digest(canonical([digest(canonical(body)), profile])),
    }


def validate_profile(record, attachment=None):
    profile = record.get("profile")
    if profile is None:
        if "profile_hash" in record or (attachment is not None and supports_controls(attachment["package_path"])):
            raise GroupError("accepted assignment profile is missing")
        return
    if (not isinstance(profile, dict) or set(profile) != {"harness", "model", "effort", "sources"}
            or profile.get("harness") not in ("claude", "codex")
            or any(record.get(key) != profile.get(key) for key in ("harness", "model", "effort"))
            or record.get("profile_hash") != digest(canonical([record["body_hash"], profile]))):
        raise GroupError("accepted assignment profile identity changed")
    validate_axes({key: profile[key] for key in ("model", "effort")})
    if (not isinstance(profile["sources"], dict) or set(profile["sources"]) != {"model", "effort"}
            or any(value not in {"caller-named", "caller-operation", "saved-named", "saved-operation", "firstmate-default"}
                   for value in profile["sources"].values())):
        raise GroupError("accepted assignment profile source is invalid")


def check_launch(owner, task, harness, model, effort, parent=None, generation=None):
    binding = owner.binding(task)
    if not binding:
        if parent is not None:
            raise GroupError("component launch requires its accepted binding")
        return
    binding, record, attachment = owner.component_context(task)
    validate_profile(record, attachment if "package_path" in attachment else None)
    if record["state"] != "launching":
        raise GroupError("component profile launch requires its accepted launching request")
    if parent is not None:
        if binding["parent"] != parent or binding["accepted_parent_gen"] != generation:
            raise GroupError("component launch differs from its accepted parent")
        (getattr(owner, "caller_meta", owner.root_meta))(parent, generation)
    if [record.get(key, "default") for key in ("harness", "model", "effort")] != [harness, model, effort]:
        raise GroupError("component launch profile differs from its accepted request")
    if record.get("profile") is not None:
        validate_owner_profile(owner, harness, model, effort)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", required=True)
    parser.add_argument("--code-root", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    launch = commands.add_parser("launch")
    bridge = commands.add_parser("bridge")
    bridge.add_argument("parent")
    bridge.add_argument("generation")
    for command in (launch, bridge):
        for key in ("task", "harness", "model", "effort"):
            command.add_argument(key)
    args = parser.parse_args()
    try:
        from fm_task_group import TaskGroups
        owner = TaskGroups(args.home, args.code_root)
        check_launch(owner, args.task, args.harness, args.model, args.effort,
                     getattr(args, "parent", None), getattr(args, "generation", None))
        return 0
    except (GroupError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
