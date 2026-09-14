#!/usr/bin/env bash
# Read-only proof for an accepted but not-yet-confirmed component launch.
# This is transaction custody, never endpoint liveness or a retry permission.
# Called only through the parent bridge; it does not acquire or release locks.
fm_task_group_custody_ancestor() { # <controller-pid> <lock-owner-pid>
  local pid=$1 owner=$2 count=0
  [[ "$pid" =~ ^[1-9][0-9]*$ ]] && [[ "$owner" =~ ^[1-9][0-9]*$ ]] || return 1
  # The controller must be a descendant, not a caller-provided copy of owner.
  [ "$pid" != "$owner" ] || return 1
  while [ "$count" -lt 64 ] && [ "$pid" -gt 1 ]; do
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d '[:space:]') || return 1
    [[ "$pid" =~ ^[1-9][0-9]*$ ]] || return 1
    [ "$pid" != "$owner" ] || return 0
    count=$((count + 1))
  done
  return 1
}

fm_task_group_custody_capture() { # <owner> <controller> <control-lock> <meta-lock>
  local owner=$1 controller=$2 control=$3 metalock=$4 control_dir meta_dir owner_identity controller_identity
  [ "$_FM_UNAME" = Linux ] && [ -z "${FM_PROC_ROOT_OVERRIDE:-}" ] || return 1
  fm_task_group_custody_ancestor "$controller" "$owner" || return 1
  fm_pid_alive "$owner" && fm_pid_alive "$controller" || return 1
  control_dir=$(readlink "$control") && meta_dir=$(readlink "$metalock") || return 1
  [ "$(cat "$control/pid" 2>/dev/null)" = "$owner" ] || return 1
  [ "$(cat "$metalock/pid" 2>/dev/null)" = "$owner" ] || return 1
  owner_identity=$(fm_pid_identity "$owner") || return 1
  controller_identity=$(fm_pid_identity "$controller") || return 1
  "${FM_TASK_GROUP_PYTHON:-python3}" -c '
import hashlib,json,sys
owner,controller,control_dir,meta_dir,owner_identity,controller_identity=sys.argv[1:]
print(json.dumps(dict(schema=1,owner=owner,controller=controller,control_dir=control_dir,meta_dir=meta_dir,
                     owner_identity=hashlib.sha256(owner_identity.encode()).hexdigest(),
                     controller_identity=hashlib.sha256(controller_identity.encode()).hexdigest()),sort_keys=True))
' "$owner" "$controller" "$control_dir" "$meta_dir" "$owner_identity" "$controller_identity"
}

fm_task_group_custody_observe() { # <root> <generation> <control-lock> <meta-lock> <metadata>
  local root=$1 generation=$2 control=$3 metalock=$4 meta=$5 parsed owner controller control_dir meta_dir expected actual
  [ "$_FM_UNAME" = Linux ] || return 1
  parsed=$("${FM_TASK_GROUP_PYTHON:-python3}" -c '
import json,re,sys
raw=sys.stdin.buffer.read(32769)
if len(raw)>32768: raise ValueError("bounded custody required")
d=json.loads(raw)
if set(d)!={"schema","owner","controller","control_dir","meta_dir","owner_identity","controller_identity"} or d["schema"]!=1: raise ValueError("custody schema")
for k in ("owner","controller"):
    if not isinstance(d[k],str) or not re.fullmatch(r"[1-9][0-9]*",d[k]): raise ValueError(k)
for k in ("control_dir","meta_dir"):
    if not isinstance(d[k],str) or not d[k].startswith("/") or any(c in d[k] for c in "\x00\r\n"): raise ValueError(k)
for k in ("owner_identity","controller_identity"):
    if not isinstance(d[k],str) or not re.fullmatch(r"[0-9a-f]{64}",d[k]): raise ValueError(k)
for k in ("owner","controller","control_dir","meta_dir"): print(d[k])
print(json.dumps(d,sort_keys=True))
' 2>/dev/null) || return 1
  {
    IFS= read -r owner
    IFS= read -r controller
    IFS= read -r control_dir
    IFS= read -r meta_dir
    IFS= read -r expected
  } <<EOF
$parsed
EOF
  [ "$(fm_meta_get "$meta" spawn_gen)" = "$generation" ] || return 1
  [ "$(readlink "$control" 2>/dev/null)" = "$control_dir" ] || return 1
  [ "$(readlink "$metalock" 2>/dev/null)" = "$meta_dir" ] || return 1
  actual=$(fm_task_group_custody_capture "$owner" "$controller" "$control" "$metalock") || return 1
  [ "$actual" = "$expected" ] || return 1
  [ "$(fm_meta_get "$meta" spawn_gen)" = "$generation" ] || return 1
  # Recheck the exact published claims after process inspection. A later holder
  # of the same lifecycle locks cannot inherit this launch's waiting state.
  [ "$(readlink "$control" 2>/dev/null)" = "$control_dir" ] || return 1
  [ "$(readlink "$metalock" 2>/dev/null)" = "$meta_dir" ] || return 1
}
