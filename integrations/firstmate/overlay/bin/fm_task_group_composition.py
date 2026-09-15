"""Static dynamic call authorization; FirstMate retains every runtime owner."""
from fm_task_group_store import GroupError, identifier

CAPABILITY = "scoped-composition-v1"


def validate_composition(value):
    if not isinstance(value, dict) or set(value) != {"calls"}:
        raise GroupError("composition must contain only an authorized calls list")
    calls = value["calls"]
    if not isinstance(calls, list) or not 1 <= len(calls) <= 32:
        raise GroupError("composition requires one to 32 authorized dynamic calls")
    seen = set()
    for call in calls:
        if not isinstance(call, dict) or set(call) != {"id", "caller"}:
            raise GroupError("each composition call requires only id and caller")
        identifier(call["id"], "workflow call")
        identifier(call["caller"], "workflow caller")
        if call["id"] in seen:
            raise GroupError("composition call IDs must be unique")
        seen.add(call["id"])
    if not any(call["caller"] == "root" for call in calls):
        raise GroupError("composition requires an authorized root call")
    return value


def calls(attachment):
    value = attachment.get("composition")
    if value is None:
        return [{"id": "dynamic", "caller": "root"}]
    return validate_composition(value)["calls"]


def caller_calls(attachment, caller_request=None):
    if caller_request == "root":
        return []  # The reserved root label never grants a same-named Work authority.
    label = caller_request or "root"
    return [call for call in calls(attachment) if call["caller"] == label]


def request_call(body, attachment, caller_request=None):
    selected = body.get("workflow_call", "dynamic")
    identifier(selected, "workflow call")
    if not any(call["id"] == selected for call in caller_calls(attachment, caller_request)):
        raise GroupError("workflow call is not authorized for this caller by the selected composition")
    return selected


def pending_calls(attachment, records, caller_request=None):
    return [call for call in caller_calls(attachment, caller_request)
            if not any(record.get("workflow_call", "dynamic") == call["id"]
                       and record["primitive"] == "Review" and record.get("gathered")
                       for record in records)]


def admit_call(body, attachment, records, caller_request=None):
    named_callers = {call["caller"] for call in calls(attachment) if call["caller"] != "root"}
    if body["request_id"] in named_callers and (
            caller_request is not None or body["primitive"] != "Work" or body["writable"] is not True):
        raise GroupError("named workflow callers require root-owned writable Work")
    selected = request_call(body, attachment, caller_request)
    permitted = caller_calls(attachment, caller_request)
    index = next(i for i, call in enumerate(permitted) if call["id"] == selected)
    before = permitted[:index]
    later = {call["id"] for call in permitted[index + 1:]}
    if any(record.get("workflow_call", "dynamic") in later for record in records):
        raise GroupError("cannot reopen an earlier dynamic call after a later phase starts")
    for call in before:
        previous = [record for record in records if record.get("workflow_call", "dynamic") == call["id"]]
        if (not any(record["primitive"] == "Review" and record.get("gathered") for record in previous)
                or any(not record.get("gathered") for record in previous)):
            raise GroupError("finish and gather the earlier authorized dynamic call before the next phase")
    scoped = [record for record in records if record.get("workflow_call", "dynamic") == selected]
    reviews = [record for record in scoped if record["primitive"] == "Review"]
    if body["primitive"] == "Review":
        if reviews:
            raise GroupError("dynamic workflow permits only one fresh independent Review per authorized call")
        if any(not record.get("gathered") for record in scoped):
            raise GroupError("gather all accepted Work results before Review")
    elif reviews and not reviews[0].get("gathered"):
        raise GroupError("gather Review before the single repair/check phase")
    return selected, ("review" if body["primitive"] == "Review" else "repair" if reviews else "work")
