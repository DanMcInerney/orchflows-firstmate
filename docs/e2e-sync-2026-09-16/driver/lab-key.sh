#!/usr/bin/env bash
# lab-key.sh <key> <wait-seconds> [lines]: send a key to the captain pane, wait, print the pane tail.
set -u
E=$HOME/orchflows-e2e
source "$E/driver/env.sh"
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"; PANE=$(cat "$E/lab/captain-pane")
KEY=${1:-Enter}; WAIT=${2:-30}; N=${3:-80}
bash "$H" run "$LAB" pane send-keys "$PANE" "$KEY" >/dev/null
sleep "$WAIT"
echo "===== $(date -u +%H:%M:%SZ) captain pane (last $N lines)"
bash "$H" run "$LAB" pane read "$PANE" --lines "$N" 2>/dev/null | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -"$N"
