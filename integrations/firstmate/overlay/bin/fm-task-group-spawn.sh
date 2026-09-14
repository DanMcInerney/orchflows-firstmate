#!/usr/bin/env bash
# FirstMate-owned Stage 1 launch bridge. Called by fm-task-group.py while its
# request lock is held. Preserve the existing parent control/meta lock owners;
# fm-spawn retains child task-set/spawn/project/meta publication and rollback.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mode=launch
case "${1:-}" in
  --submit) [ "$#" -eq 4 ] || exit 2; mode=submit; root=$2 generation=$3 request=$4 ;;
  --gather) { [ "$#" -eq 3 ] || [ "$#" -eq 4 ]; } || exit 2; mode=gather; root=$2 generation=$3 request_id=${4:-} ;;
  --capture-lock) [ "$#" -eq 3 ] || exit 2; mode=capture; root=$2 generation=$3 ;;
  --observe-lock) [ "$#" -eq 3 ] || exit 2; mode=observe; root=$2 generation=$3 ;;
  --verify-position) [ "$#" -eq 6 ] || exit 2; mode=position; root=$2 generation=$3 child=$4 project=$5 worktree=$6 ;;
  --verify-lock) [ "$#" -eq 3 ] || exit 2; mode=verify; root=$2 generation=$3 ;;
  *)
    [ "$#" -eq 7 ] || { echo 'task-group launch expects ROOT GEN CHILD PROJECT HARNESS MODEL EFFORT' >&2; exit 2; }
    root=$1 generation=$2 child=$3 project=$4 harness=$5 model=$6 effort=$7
    [[ "$child" =~ ^tg-[a-f0-9]{20}$ ]] || exit 2
    ;;
esac
[[ "$root" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]] || exit 2
[ -n "${FM_HOME:-}" ] && [ -d "$FM_HOME/state" ] || { echo 'task-group requires an explicit FirstMate home' >&2; exit 2; }
for override in FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE; do
  [ -z "${!override:-}" ] || { echo "task-group does not support $override" >&2; exit 2; }
done
. "$SCRIPT_DIR/fm-backend.sh"
. "$SCRIPT_DIR/fm-wake-lib.sh"
. "$SCRIPT_DIR/fm-task-group-runtime.sh"
. "$SCRIPT_DIR/fm-gate-refuse-lib.sh"
fm_refuse_if_gate_agent
control_lock="$FM_HOME/state/.control-$root.lock"
meta="$FM_HOME/state/$root.meta"
meta_lock=$(fm_meta_lock_path "$meta")
control_held=0 meta_held=0
cleanup() {
  [ "$meta_held" = 0 ] || fm_lock_release "$meta_lock" || true
  [ "$control_held" = 0 ] || fm_lock_release "$control_lock" || true
}
trap cleanup EXIT
inherited_custody() {
  local owner=${FM_TASK_GROUP_LOCK_OWNER:-} ancestor=$PPID count=0
  [[ "$owner" =~ ^[0-9]+$ ]] || return 1
  [ "${FM_TASK_GROUP_LOCK_ROOT:-}" = "$root" ] && [ "${FM_TASK_GROUP_LOCK_HOME:-}" = "$FM_HOME" ] || return 1
  [ "$(cat "$control_lock/pid" 2>/dev/null)" = "$owner" ] || return 1
  [ "$(cat "$meta_lock/pid" 2>/dev/null)" = "$owner" ] || return 1
  fm_pid_alive "$owner" || return 1
  case "$_FM_UNAME" in
    MINGW*|MSYS*)
      fm_task_group_python "$SCRIPT_DIR/fm_task_group_runtime.py" ancestor "$owner"
      return $? ;;
  esac
  while [ "$count" -lt 64 ] && [ "$ancestor" -gt 1 ]; do
    [ "$ancestor" != "$owner" ] || return 0
    ancestor=$(ps -o ppid= -p "$ancestor" 2>/dev/null | tr -d '[:space:]') || return 1
    [[ "$ancestor" =~ ^[0-9]+$ ]] || return 1
    count=$((count + 1))
  done
  return 1
}
# Observation must never acquire lifecycle locks: doing so would replace the
# very evidence being checked. Capture runs only under proven inherited custody.
if [ "$mode" = observe ]; then
  . "$SCRIPT_DIR/fm-task-group-custody.sh"
  fm_task_group_custody_observe "$root" "$generation" "$control_lock" "$meta_lock" "$meta"
  exit $?
elif [ "$mode" = verify ] || [ "$mode" = capture ] || [ "$mode" = position ]; then
  inherited_custody || { echo 'task-group internal operation has no parent lock custody' >&2; exit 1; }
elif ! inherited_custody; then
  fm_lock_try_acquire "$control_lock" || { echo 'parent lifecycle operation in progress' >&2; exit 1; }
  control_held=1
  fm_lock_try_acquire "$meta_lock" || { echo 'parent metadata operation in progress' >&2; exit 1; }
  meta_held=1
  fm_current_pid FM_TASK_GROUP_LOCK_OWNER
  export FM_TASK_GROUP_LOCK_OWNER
  export FM_TASK_GROUP_LOCK_ROOT="$root" FM_TASK_GROUP_LOCK_HOME="$FM_HOME"
fi
[ -f "$meta" ] && [ ! -L "$meta" ] || exit 1
[ "$(fm_meta_get "$meta" spawn_gen)" = "$generation" ] || { echo 'stale parent generation' >&2; exit 1; }
[ "$(fm_meta_get "$meta" backend)" = herdr ] && [ "$(fm_meta_get "$meta" kind)" = scout ] || exit 1
[ "$(fm_meta_get "$meta" task_group_role)" = root ] || exit 1
case "$mode" in
  position)
    # The existing spawn owns both locks and the exact Treehouse slot claim.
    # A worker or unrelated callback cannot reposition another task's worktree.
    . "$SCRIPT_DIR/fm-task-group-custody.sh"
    [[ "$child" =~ ^tg-[a-f0-9]{20}$ ]] || exit 1
    [ "$(fm_meta_get "$meta" project)" = "$project" ] || exit 1
    spawn_lock="$FM_HOME/state/.spawn-$child.lock"
    spawn_owner=$(cat "$spawn_lock/pid" 2>/dev/null) || exit 1
    fm_pid_alive "$spawn_owner" || exit 1
    fm_task_group_custody_ancestor "$PPID" "$spawn_owner" || exit 1
    project_lock=$(fm_treehouse_project_lock_path "$project") || exit 1
    [ "$(cat "$project_lock/pid" 2>/dev/null)" = "$spawn_owner" ] || exit 1
    fm_treehouse_pool_slot "$project" "$worktree" || exit 1
    fm_treehouse_slot_owner_state "$worktree" "$child"
    [ "$FM_TREEHOUSE_SLOT_OWNER" = mine ] && [ "$FM_TREEHOUSE_SLOT_OWNER_HOME" = "$FM_HOME" ] || exit 1
    exit 0 ;;
  verify) exit 0 ;;
  capture)
    . "$SCRIPT_DIR/fm-task-group-custody.sh"
    fm_task_group_custody_capture "$FM_TASK_GROUP_LOCK_OWNER" "$PPID" "$control_lock" "$meta_lock"
    exit $? ;;
  submit)
    fm_task_group_python "$SCRIPT_DIR/fm-task-group.py" --home "$FM_HOME" internal-submit "$root" --generation "$generation" --request "$request"
    exit $? ;;
  gather)
    gather_args=()
    [ -z "$request_id" ] || gather_args+=(--request-id "$request_id")
    fm_task_group_python "$SCRIPT_DIR/fm-task-group.py" --home "$FM_HOME" internal-gather "$root" --generation "$generation" "${gather_args[@]}"
    exit $? ;;
esac
[ "$(fm_meta_get "$meta" project)" = "$project" ] || exit 1
[ "$(fm_meta_get "$meta" harness)" = "$harness" ] || exit 1
case "$harness" in claude|codex) ;; *) exit 1 ;; esac
[ "$(fm_meta_get "$meta" model)" = "$model" ] && [ "$(fm_meta_get "$meta" effort)" = "$effort" ] || exit 1
args=("$child" "$project" --scout --backend herdr --harness "$harness")
[ "$model" = default ] || args+=(--model "$model")
[ "$effort" = default ] || args+=(--effort "$effort")
# Exact session identity comes from the current parent record. Endpoint
# placement and all Herdr calls remain the backend adapter's responsibility.
session=$(fm_meta_get "$meta" herdr_session)
[ -n "$session" ] || exit 1
. "$SCRIPT_DIR/fm-tasks-axi-lib.sh"
. "$SCRIPT_DIR/fm-backlog-transition-lib.sh"
if fm_backlog_transition_applies "$FM_HOME/config" "$FM_HOME/data" scout; then
  "$SCRIPT_DIR/fm-tasks-axi.sh" add "$child" "Orchflows component for $root" --kind scout
else
  transition_status=$?
  [ "$transition_status" -eq 1 ] || { echo 'task-group backlog admission could not be resolved' >&2; exit "$transition_status"; }
fi
FM_BACKEND=herdr HERDR_SESSION="$session" "$SCRIPT_DIR/fm-spawn.sh" "${args[@]}"
