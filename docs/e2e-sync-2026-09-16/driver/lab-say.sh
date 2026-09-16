#!/usr/bin/env bash
# lab-say.sh <request-file> [wait-seconds]: Escape the composer suggestion, type the file's text into the captain pane, Enter, then show the pane.
set -u
E=$HOME/orchflows-e2e
source "$E/driver/env.sh"
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"; PANE=$(cat "$E/lab/captain-pane")
FILE=$1; WAIT=${2:-20}
TEXT=$(tr -d '\r' < "$FILE" | tr '\n' ' ' | sed 's/[[:space:]]*$//')
bash "$H" run "$LAB" pane send-keys "$PANE" Escape >/dev/null; sleep 1
bash "$H" run "$LAB" pane send-text "$PANE" "$TEXT" >/dev/null && sleep 2 && bash "$H" run "$LAB" pane send-keys "$PANE" Enter >/dev/null && echo "sent $(date -u +%H:%M:%SZ): ${TEXT:0:80}..."
sleep "$WAIT"
echo "===== captain pane"; bash "$H" run "$LAB" pane read "$PANE" --lines 40 2>/dev/null | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -30
