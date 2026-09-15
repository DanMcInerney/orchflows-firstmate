"""Admission and immutable primitive identity for FirstMate task groups."""
import re
import sys

from fm_task_group_store import GroupError
from fm_task_group_delivery import root_delivery, validate_root_metadata

MAX_COMPONENTS = 32


def is_dynamic(attachment):
    return attachment.get("workflow") == "dynamic"


def admit(primitive, review_policy, workflow=None):
    if workflow == "dynamic":
        if (primitive, review_policy) != ("Work", "workflow-review"):
            raise GroupError("dynamic workflow requires Work/workflow-review admission")
        if not sys.platform.startswith("linux"):
            raise GroupError("dynamic workflow currently requires Linux")
    elif workflow is not None or (primitive, review_policy) not in (("Work", "none"), ("Review", "explicit-audit")):
        raise GroupError("supported admission pairs are Work/none and Review/explicit-audit")
    if primitive == "Review" and not sys.platform.startswith("linux"):
        raise GroupError("read-only Review currently requires Linux")
    return primitive


def attachment_primitive(attachment):
    root_delivery(attachment)
    if "composition" in attachment:
        from fm_task_group_composition import validate_composition
        validate_composition(attachment["composition"])
        if not is_dynamic(attachment):
            raise GroupError("composition requires dynamic attachment")
    primitive = admit(attachment.get("primitive"), attachment.get("review_policy", "none"), attachment.get("workflow"))
    readonly, maximum = (False, MAX_COMPONENTS) if is_dynamic(attachment) else (True, 1)
    if attachment.get("readonly") is not readonly or type(attachment.get("max_components")) is not int or attachment["max_components"] != maximum:
        raise GroupError("task-group attachment requires bounded dynamic components" if is_dynamic(attachment)
                         else "task-group attachment requires one read-only component")
    return primitive


def component_primitive(record, attachment):
    if not is_dynamic(attachment):
        return attachment_primitive(attachment)
    primitive = record.get("primitive")
    if primitive not in ("Work", "Review"):
        raise GroupError("saved component primitive or review policy differs from request")
    return primitive


def component_fields(record, attachment):
    if is_dynamic(attachment):
        body = record.get("body", record)
        primitive, writable = body.get("primitive"), body.get("writable")
        if primitive not in ("Work", "Review") or type(writable) is not bool or (primitive == "Review" and writable):
            raise GroupError("dynamic requests require Work or read-only Review and a writable boolean")
        return {"primitive": primitive, "review_policy": "workflow-review",
                "writable": writable, "readonly": not writable}
    return review_fields(attachment)


def review_fields(attachment):
    if attachment_primitive(attachment) == "Review":
        return {"primitive": "Review", "review_policy": "explicit-audit"}
    return {}


def validate_record(record, attachment, *, result=False, request=None):
    primitive = attachment_primitive(attachment)
    if is_dynamic(attachment):
        source = request if result else record
        if source is None:
            raise GroupError("dynamic retained result requires accepted request identity")
        expected = component_fields(source, attachment)
        if any(record.get(key) != value for key, value in expected.items()):
            raise GroupError("saved component primitive or review policy differs from request")
        if record.get("package_digest") != attachment["package_digest"] or not re.fullmatch(r"[0-9a-f]{40,64}", record.get("input_commit", "")):
            raise GroupError("saved component input or package identity is invalid")
        if result:
            for key in ("root", "child", "epoch", "body_hash", "input_commit", "package_digest", "accepted_parent_gen"):
                if record.get(key) != request.get(key):
                    raise GroupError("retained component identity differs from accepted request")
            if record.get("request_id") != request["body"]["request_id"]:
                raise GroupError("retained result request identity differs from accepted request")
            validate_metadata(record.get("component_meta", {}), attachment, request)
            parent = request.get("parent", request["root"])
            if (record.get("parent", record["root"]) != parent
                    or record.get("workflow_call", "dynamic") != request.get("workflow_call", "dynamic")):
                raise GroupError("retained composition identity differs from accepted request")
            parent_meta = record.get("parent_at_completion", {})
            if parent == request["root"]:
                validate_metadata(parent_meta, attachment)
            else:
                from fm_task_group_composition import calls
                selected = next(call for call in calls(attachment)
                                if call["id"] == request["workflow_call"])
                expected_parent = {"endpoint_task_id": parent, "task_group_role": "component",
                                   "task_group_parent": request["root"],
                                   "task_group_request": selected["caller"],
                                   "task_group_primitive": "Work", "task_group_workflow": "dynamic",
                                   "task_group_writable": "true", "kind": "scout", "backend": "herdr"}
                if any(parent_meta.get(key) != value for key, value in expected_parent.items()):
                    raise GroupError("retained descendant parent metadata differs from authorized caller")
            if expected["writable"]:
                if not re.fullmatch(r"[0-9a-f]{40,64}", record.get("output_commit", "")):
                    raise GroupError("retained writer result lacks an output commit")
                if not isinstance(record.get("output_ref"), str) or not record["output_ref"].startswith("refs/firstmate/orchflows/"):
                    raise GroupError("retained writer result lacks its output ref")
            elif "output_commit" in record or "output_ref" in record:
                raise GroupError("read-only result cannot authorize writer output")
        return
    # Work request records predate primitive fields. Review never does.
    expected = {"primitive": primitive, "review_policy": attachment.get("review_policy", "none")}
    defaults = {} if primitive == "Review" else {"primitive": "Work", "review_policy": "none"}
    if any(record.get(key, defaults.get(key)) != value for key, value in expected.items()):
        raise GroupError("saved component primitive or review policy differs from attachment")
    if primitive == "Review":
        if any(record.get(key) != attachment[key] for key in ("input_commit", "package_digest")):
            raise GroupError("saved Review input or package identity differs from attachment")
        if result:
            for key in ("component_meta", "parent_at_completion"):
                value = record.get(key)
                if not isinstance(value, dict):
                    raise GroupError("retained Review result lacks launch metadata")
                validate_metadata(value, attachment)
    if result and (record.get("primitive") != primitive or record.get("readonly") is not True):
        raise GroupError("retained result primitive or read-only identity differs from attachment")


def validate_metadata(value, attachment, record=None):
    if record is None and isinstance(value, dict):
        validate_root_metadata(value, attachment)
    primitive = component_primitive(record, attachment) if record is not None else attachment_primitive(attachment)
    permitted = (primitive,) if primitive == "Review" or is_dynamic(attachment) else (None, "Work")
    if not isinstance(value, dict) or value.get("task_group_primitive") not in permitted:
        raise GroupError("task metadata primitive differs from immutable attachment")
    if is_dynamic(attachment):
        if value.get("task_group_workflow") != "dynamic":
            raise GroupError("task metadata workflow differs from immutable attachment")
        if record is not None and value.get("task_group_writable") != str(record["writable"]).lower():
            raise GroupError("component metadata writable permission differs from accepted request")


def scope(attachment):
    if is_dynamic(attachment):
        return "local-dynamic-ship-local-only" if root_delivery(attachment) else "local-dynamic"
    return "local-readonly-review" if attachment_primitive(attachment) == "Review" else "local-readonly-work"
