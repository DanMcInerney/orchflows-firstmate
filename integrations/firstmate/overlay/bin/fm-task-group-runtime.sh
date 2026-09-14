#!/usr/bin/env bash
# Task-group Python entrypoint only. Ordinary FirstMate tool argument conversion
# stays unchanged; native Windows Python receives explicit script and path data.
fm_task_group_python() { # <script> [arguments...]
  local script=$1 python=${FM_TASK_GROUP_PYTHON:-python3}
  shift
  case "${_FM_UNAME:-$(uname -s)}" in
    MINGW*|MSYS*)
      script=$(/usr/bin/cygpath -m "$script") || return 1
      MSYS2_ARG_CONV_EXCL='*' "$python" "$script" "$@"
      ;;
    *) "$python" "$script" "$@" ;;
  esac
}

fm_task_group_present() { # <home> <task> <state>
  local home=$1 task=$2 state=$3 path
  case "$task" in ''|*[!A-Za-z0-9._-]*) return 1 ;; esac
  for path in "$home/data/$task/task-group" "$home/data/$task/task-group-component.json"; do
    [ ! -e "$path" ] && [ ! -L "$path" ] || return 0
  done
  grep -qE '^(task_group_role=|result_disposition=parent$)' "$state/$task.meta" 2>/dev/null
}

# Controller/bridge fixtures do not prove native worker process custody. Consult
# the actual shell platform, not _FM_UNAME or an opt-in environment flag. Both
# fresh and replacement launches refuse; --force cannot authorize lost custody.
fm_task_group_native_worker_guard() { # <home> <task> <state> <spawn|teardown>
  local home=$1 task=$2 state=$3 operation=$4 platform
  fm_task_group_present "$home" "$task" "$state" || return 0
  platform=$(uname -s) || {
    printf 'REFUSED: cannot identify the worker host for task %s; preserving its records.\n' "$task" >&2
    return 1
  }
  case "$platform" in MINGW*|MSYS*|CYGWIN*) ;; *) return 0 ;; esac
  printf 'REFUSED: native Windows Stage 1 task-group %s for %s requires FirstMate/Herdr process custody, which is not implemented. Controller/bridge fixture support does not enable real workers. Preserve this task and use a validated Linux/WSL worker home or implement and verify native custody before retrying.\n' "$operation" "$task" >&2
  return 1
}
