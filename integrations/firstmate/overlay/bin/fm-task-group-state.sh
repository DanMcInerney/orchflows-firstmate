#!/usr/bin/env bash
# Experimental Stage 1 task-group lifecycle projection. The Python controller
# owns durable requests/results; this owner adds actual endpoint observations.
# An unbound task takes no Python/backend call and keeps its ordinary behavior.

_FM_TASK_GROUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$_FM_TASK_GROUP_DIR/fm-task-group-runtime.sh"

fm_task_group_generation() { # <meta>
  [ -f "$1" ] && [ ! -L "$1" ] || return 1
  awk -F= '$1 == "spawn_gen" { count++; value=substr($0,11) }
    END { if (count != 1 || value !~ /^[A-Za-z0-9][A-Za-z0-9_.-]*$/) exit 1; print value }' "$1"
}


# 0 = validated binding; 1 = ordinary task; 2 = binding cannot be read safely.
# A broken/missing controller never turns a visibly bound task into an ordinary one.
fm_task_group_read() { # <home> <task> [state]
  local home=$1 task=$2 state=${3:-$1/state} raw fields
  FM_TASK_GROUP_COMPONENT=false
  FM_TASK_GROUP_PENDING=false
  FM_TASK_GROUP_CLEANUP_ALLOWED=false
  FM_TASK_GROUP_ROOT=
  FM_TASK_GROUP_CHILD=
  FM_TASK_GROUP_CHILD_GEN=
  FM_TASK_GROUP_RESULT_READY=false
  FM_TASK_GROUP_LAUNCH_ACTIVE=false
  FM_TASK_GROUP_DETAIL='task-group record unavailable; reconcile before continuing'
  fm_task_group_present "$home" "$task" "$state" || return 1
  raw=$(fm_task_group_python "$_FM_TASK_GROUP_DIR/fm-task-group.py" --home "$home" waiting "$task" 2>/dev/null) || return 2
  fields=$(printf '%s' "$raw" | "${FM_TASK_GROUP_PYTHON:-python3}" -c '
import json,re,sys
d=json.load(sys.stdin)
for k in ("attached","component","pending","cleanup_allowed"):
    if type(d.get(k)) is not bool: raise ValueError(k)
if not d["attached"]: raise ValueError("binding disappeared")
if d["pending"] and d["cleanup_allowed"]: raise ValueError("pending cleanup")
for k in ("root","child_task_id","child_generation"):
    v=d.get(k) or ""
    if not isinstance(v,str) or (v and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}",v)): raise ValueError(k)
launch=d.get("launch_active",False)
if type(launch) is not bool: raise ValueError("launch_active")
ready=d.get("result_ready",False)
if type(ready) is not bool: raise ValueError("result_ready")
if launch and (d["component"] or not d["pending"] or ready or d.get("request_state")!="launching"): raise ValueError("inconsistent launch activity")
for v in (d["component"],d["pending"],d["cleanup_allowed"],d.get("child_task_id") or "-",d.get("child_generation") or "-",ready,d.get("root") or "-",launch):
    print(str(v).lower() if type(v) is bool else v)
' 2>/dev/null) || return 2
  {
    IFS= read -r FM_TASK_GROUP_COMPONENT
    IFS= read -r FM_TASK_GROUP_PENDING
    IFS= read -r FM_TASK_GROUP_CLEANUP_ALLOWED
    IFS= read -r FM_TASK_GROUP_CHILD
    IFS= read -r FM_TASK_GROUP_CHILD_GEN
    IFS= read -r FM_TASK_GROUP_RESULT_READY
    IFS= read -r FM_TASK_GROUP_ROOT
    IFS= read -r FM_TASK_GROUP_LAUNCH_ACTIVE
  } <<EOF
$fields
EOF
  [ "$FM_TASK_GROUP_CHILD" != - ] || FM_TASK_GROUP_CHILD=
  [ "$FM_TASK_GROUP_CHILD_GEN" != - ] || FM_TASK_GROUP_CHILD_GEN=
  [ "$FM_TASK_GROUP_ROOT" != - ] || FM_TASK_GROUP_ROOT=
  return 0
}

# Used under the caller's existing control/meta locks. Pending includes an
# uncertain launch and a published result not yet acknowledged by the root.
fm_task_group_guard() { # <home> <task> <state> <promote|teardown>
  local home=$1 task=$2 state=$3 operation=$4 rc
  if fm_task_group_read "$home" "$task" "$state"; then rc=0; else rc=$?; fi
  [ "$rc" -ne 1 ] || return 0
  if [ "$rc" -ne 0 ]; then
    printf 'REFUSED: task-group state for %s is unavailable; %s requires reconciliation.\n' "$task" "$operation" >&2
    return 1
  fi
  if [ "$operation" = promote ]; then
    printf 'REFUSED: Stage 1 task-group task %s cannot be promoted.\n' "$task" >&2
    return 1
  fi
  if [ "$FM_TASK_GROUP_CLEANUP_ALLOWED" != true ]; then
    printf 'REFUSED: task-group task %s has ungathered or uncertain work; gather its retained result before teardown.\n' "$task" >&2
    return 1
  fi
}

# Components always return to their parent. Root events regain ordinary scout
# delivery semantics once the request is gathered; an unreadable binding remains
# explicitly scoped so a malformed record cannot make a component an outer task.
fm_task_group_event_scoped() { # <home> <task> <state>
  local rc
  if fm_task_group_read "$1" "$2" "$3"; then rc=0; else rc=$?; fi
  [ "$rc" -ne 1 ] || return 1
  [ "$rc" -eq 0 ] || return 0
  [ "$FM_TASK_GROUP_COMPONENT" = true ] || [ "$FM_TASK_GROUP_PENDING" = true ]
}

# 0 = group state projected into CLASS/DETAIL; 1 = ordinary current-state path.
# This never reports ordinary done. The root alone owns its scout delivery.
fm_task_group_current() { # <home> <task> [state]
  local home=$1 task=$2 state=${3:-$1/state} rc child_meta child_line child_state live gen root_gen
  FM_TASK_GROUP_CLASS=group-attention
  if fm_task_group_read "$home" "$task" "$state"; then rc=0; else rc=$?; fi
  [ "$rc" -ne 1 ] || return 1
  [ "$rc" -eq 0 ] || return 0
  if [ "$FM_TASK_GROUP_COMPONENT" = true ]; then
    if [ "$FM_TASK_GROUP_RESULT_READY" = true ]; then
      FM_TASK_GROUP_CLASS=component-ready
      FM_TASK_GROUP_DETAIL='retained component result; outer delivery belongs to its root'
      return 0
    fi
    return 1
  fi
  [ "$FM_TASK_GROUP_PENDING" = true ] || return 1
  root_gen=$(fm_task_group_generation "$state/$task.meta") || return 0
  fm_backend_validate_task_endpoint "$state/$task.meta" "$task" >/dev/null 2>&1 || return 0
  [ "$FM_BACKEND_VALIDATED_BACKEND" = herdr ] || return 0
  live=$(fm_backend_agent_state "$FM_BACKEND_VALIDATED_BACKEND" "$FM_BACKEND_VALIDATED_TARGET" 2>/dev/null) || live=unknown
  if [ "$live" != alive ]; then
    FM_TASK_GROUP_DETAIL="root endpoint is $live; reconcile its accepted component before replacement"
    return 0
  fi
  if [ "$FM_TASK_GROUP_RESULT_READY" = true ]; then
    [ "$(fm_task_group_generation "$state/$task.meta")" = "$root_gen" ] || return 0
    FM_TASK_GROUP_CLASS=group-ready
    FM_TASK_GROUP_DETAIL='retained component result awaits gather acknowledgement'
    return 0
  fi
  if [ "$FM_TASK_GROUP_LAUNCH_ACTIVE" = true ]; then
    [ "$(fm_task_group_generation "$state/$task.meta")" = "$root_gen" ] || return 0
    FM_TASK_GROUP_CLASS=waiting
    FM_TASK_GROUP_DETAIL="waiting for FirstMate component launch $FM_TASK_GROUP_CHILD (live parent lock custody)"
    return 0
  fi
  FM_TASK_GROUP_DETAIL='accepted component launch requires reconciliation'
  [ -n "$FM_TASK_GROUP_CHILD" ] && [ "$FM_TASK_GROUP_CHILD" != "$task" ] || return 0
  child_meta="$state/$FM_TASK_GROUP_CHILD.meta"
  [ -f "$child_meta" ] && [ ! -L "$child_meta" ] || return 0
  # Endpoint validators reject ambiguous/foreign identities. Child generation is
  # checked before AND after observation, since relaunch can race these reads.
  gen=$(fm_task_group_generation "$child_meta") || return 0
  [ -n "$FM_TASK_GROUP_CHILD_GEN" ] && [ "$gen" = "$FM_TASK_GROUP_CHILD_GEN" ] || return 0
  fm_backend_validate_task_endpoint "$child_meta" "$FM_TASK_GROUP_CHILD" >/dev/null 2>&1 || return 0
  [ "$FM_BACKEND_VALIDATED_BACKEND" = herdr ] || return 0
  live=$(fm_backend_agent_state "$FM_BACKEND_VALIDATED_BACKEND" "$FM_BACKEND_VALIDATED_TARGET" 2>/dev/null) || live=unknown
  if [ "$live" != alive ]; then
    FM_TASK_GROUP_DETAIL="component $FM_TASK_GROUP_CHILD endpoint is $live; reconcile before replacement"
    return 0
  fi
  child_line=$(FM_HOME="$home" FM_STATE_OVERRIDE="$state" FM_CREW_STATE_META_OVERRIDE= FM_CREW_STATE_STATUS_OVERRIDE= \
    "${FM_CREW_STATE_BIN:-$_FM_TASK_GROUP_DIR/fm-crew-state.sh}" "$FM_TASK_GROUP_CHILD" 2>/dev/null) || child_line=
  gen=$(fm_task_group_generation "$child_meta") || return 0
  [ "$gen" = "$FM_TASK_GROUP_CHILD_GEN" ] || return 0
  [ "$(fm_task_group_generation "$state/$task.meta")" = "$root_gen" ] || return 0
  child_state=${child_line#state: }; child_state=${child_state%% *}
  if [ "$child_state" = working ]; then
    # A status-only working line is old prose, not positive activity evidence.
    case "$child_line" in
      *'source: pane'*|*'source: run-step'*)
        FM_TASK_GROUP_CLASS=waiting
        FM_TASK_GROUP_DETAIL="waiting for active component $FM_TASK_GROUP_CHILD"
        return 0 ;;
    esac
  fi
  FM_TASK_GROUP_DETAIL="component $FM_TASK_GROUP_CHILD needs attention (${child_state:-unknown}); no retained result"
}

# Notification means durable inbox admission, not proof that the root gathered.
# No group lock is taken here. Callers publish the result before invoking this.
fm_task_group_notify() { # <home> <root> <root-generation> <request> <result-digest>
  local home=$1 root=$2 generation=$3 request=$4 digest=$5 lock meta target backend record body value
  for value in "$root" "$generation" "$request"; do
    case "$value" in ''|.*|*[!A-Za-z0-9._-]*) return 2 ;; esac
  done
  [ "${#digest}" -eq 64 ] || return 2
  case "$digest" in *[!a-f0-9]*) return 2 ;; esac
  FM_HOME=$home
  STATE="$home/state"
  meta="$STATE/$root.meta"
  lock=$(fm_meta_lock_path "$meta") || return 1
  fm_task_inbox_lock_acquire "$lock" || return 1
  if ! fm_backend_validate_task_endpoint "$meta" "$root" >/dev/null 2>&1 \
    || [ "$(fm_task_group_generation "$meta")" != "$generation" ]; then
    fm_lock_release "$lock"
    return 1
  fi
  target=$FM_BACKEND_VALIDATED_TARGET
  backend=$FM_BACKEND_VALIDATED_BACKEND
  if [ "$backend" != herdr ]; then fm_lock_release "$lock"; return 1; fi
  body="FirstMate component result retained: request=$request digest=$digest. Gather and acknowledge this exact result through the task-group interface before completing your scout report."
  if ! record=$(fm_task_inbox_write_idempotent "$STATE" "$root" "$body"); then
    fm_lock_release "$lock"
    return 1
  fi
  fm_lock_release "$lock" || return 1
  # A handled record has already reached the root. Otherwise the ordinary
  # watcher inbox ladder retries a lost doorbell without duplicating the record.
  case "$record" in */handled/*) ;; *) fm_task_inbox_ring "$backend" "$target" "$record" "fm-$root" >/dev/null 2>&1 || true ;; esac
  printf '%s\n' "$record"
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  case "${1:-}" in
    notify)
      [ "$#" -eq 6 ] || exit 2
      FM_HOME=$2
      STATE="$FM_HOME/state"
      # shellcheck source=bin/fm-wake-lib.sh
      . "$_FM_TASK_GROUP_DIR/fm-wake-lib.sh"
      # shellcheck source=bin/fm-backend.sh
      . "$_FM_TASK_GROUP_DIR/fm-backend.sh"
      # shellcheck source=bin/fm-task-inbox-lib.sh
      . "$_FM_TASK_GROUP_DIR/fm-task-inbox-lib.sh"
      shift
      fm_task_group_notify "$@"
      ;;
    *) printf 'usage: fm-task-group-state.sh notify HOME ROOT GENERATION REQUEST DIGEST\n' >&2; exit 2 ;;
  esac
fi
