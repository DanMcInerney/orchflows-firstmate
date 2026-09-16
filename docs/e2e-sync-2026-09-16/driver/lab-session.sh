#!/usr/bin/env bash
# Start the default Herdr server headless (the lab helper's tripwire needs it), then provision the private lab session.
set -u
export PATH=/mnt/c/Users/danhm/tools/orchflows-firstmate/.scratch/stage1-runtime/bin:$PATH
export GIT_AUTHOR_NAME="Orchflows Trial" GIT_AUTHOR_EMAIL="trial@orchflows.invalid" GIT_COMMITTER_NAME="Orchflows Trial" GIT_COMMITTER_EMAIL="trial@orchflows.invalid"
E=$HOME/orchflows-e2e
export FM_HOME=$E/home FM_ROOT_OVERRIDE=$E/firstmate FM_HERDR_LAB_STATE_DIR=$E/lab FM_BACKEND=herdr TMPDIR=$E/tmp
cd "$FM_HOME"
echo "=== default server"
if [ "$(herdr status --json 2>/dev/null | jq -r '.server.running')" != true ]; then
  setsid -f herdr server > "$E/lab/default-server.log" 2>&1
  for i in $(seq 1 30); do sleep 1; [ "$(herdr status --json 2>/dev/null | jq -r '.server.running')" = true ] && break; done
fi
herdr status --json | jq -c '{running: .server.running, version: .server.version, protocol: .server.protocol}'
herdr session list --json | jq -c '.sessions[] | {name, default, running}'
echo "=== lab session"
NAME=$(bash "$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh" name e2esync) || { echo "name failed"; exit 1; }
echo "lab name: $NAME"
setsid -f bash -c 'source "$2/driver/env.sh"; cd "$FM_HOME"; bash "$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh" provision "$1"; echo "provision rc=$?"; sleep 2147483647' _ "$NAME" "$E" > "$E/lab/provision.log" 2>&1
r=false
for i in $(seq 1 90); do sleep 1; r=$(HERDR_SESSION=$NAME herdr status --json --session "$NAME" 2>/dev/null | jq -r '.server.running // false'); [ "$r" = true ] && break; done
echo "running after ${i}s: $r"; cat "$E/lab/provision.log"
if [ "$r" = true ]; then echo "$NAME" > "$E/lab/session"; fi
echo "--- sessions:"; herdr session list --json | jq -c '.sessions[] | {name, default, running}'
