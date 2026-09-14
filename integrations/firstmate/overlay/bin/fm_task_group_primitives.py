"""Admission and immutable primitive identity for bounded read-only groups."""
import sys

from fm_task_group_store import GroupError


def admit(primitive, review_policy):
    if (primitive, review_policy) not in (("Work", "none"), ("Review", "explicit-audit")):
        raise GroupError("supported admission pairs are Work/none and Review/explicit-audit")
    if primitive == "Review" and not sys.platform.startswith("linux"):
        raise GroupError("read-only Review currently requires Linux")
    return primitive


def attachment_primitive(attachment):
    primitive = admit(attachment.get("primitive"), attachment.get("review_policy", "none"))
    if attachment.get("readonly") is not True or type(attachment.get("max_components")) is not int or attachment.get("max_components") != 1:
        raise GroupError("task-group attachment requires one read-only component")
    return primitive


def review_fields(attachment):
    if attachment_primitive(attachment) == "Review":
        return {"primitive": "Review", "review_policy": "explicit-audit"}
    return {}


def validate_record(record, attachment, *, result=False):
    primitive = attachment_primitive(attachment)
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


def validate_metadata(value, attachment):
    primitive = attachment_primitive(attachment)
    permitted = ("Review",) if primitive == "Review" else (None, "Work")
    if value.get("task_group_primitive") not in permitted:
        raise GroupError("task metadata primitive differs from immutable attachment")


def scope(attachment):
    return "local-readonly-review" if attachment_primitive(attachment) == "Review" else "local-readonly-work"
