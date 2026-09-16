#!/usr/bin/env bash
# Tear down the trial lab: exit the primary, stop the viewer by its recorded pid, tear the lab session down, stop the default server.
set -u
export PATH=/mnt/c/Users/danhm/tools/orchflows-firstmate/.scratch/stage1-runtime/bin:$PATH
E=$HOME/orchflows-e2e
source "$E/driver/env.sh"
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"; PANE=$(cat "$E/lab/captain-pane")
cd "$FM_HOME"
echo "=== state before"; ls "$FM_HOME/state"
echo "=== exit the primary"
bash "$H" run "$LAB" pane send-keys "$PANE" Escape >/dev/null; sleep 1
bash "$H" run "$LAB" pane send-text "$PANE" "/exit" >/dev/null; sleep 1; bash "$H" run "$LAB" pane send-keys "$PANE" Enter >/dev/null; sleep 6
bash "$H" run "$LAB" pane read "$PANE" --lines 6 2>/dev/null | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -4
echo "=== stop viewer"
bash "$H" viewer stop "$LAB" 2>&1 | tail -2
pid=$(grep -o 'pid [0-9]*' "$E/lab/viewer.log" 2>/dev/null | head -1 | cut -d' ' -f2)
if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then kill "$pid"; sleep 2; kill -0 "$pid" 2>/dev/null && kill -9 "$pid"; echo "viewer pid $pid signalled"; fi
pkill -f fm-herdr-lab-viewer.py 2>/dev/null && echo "viewer helper killed"
sleep 2
echo "=== teardown"
bash "$H" teardown "$LAB" 2>&1 | tail -5
echo "=== sessions after"; herdr session list --json | jq -c '.sessions[] | {name, default, running}'
echo "=== stop default server (started by this trial)"
herdr server stop 2>&1 | tail -1
sleep 2; herdr status --json 2>/dev/null | jq -c '{running: .server.running}'
echo "=== state after"; ls "$FM_HOME/state"
