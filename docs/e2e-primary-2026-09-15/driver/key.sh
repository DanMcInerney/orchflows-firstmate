#!/usr/bin/env bash
# key.sh <key> [pane-id]: send a key to the captain pane (or a named pane).
set -u
source /tmp/orchflows-e2e/driver/env.sh
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"; PANE=${2:-$(cat "$E/lab/captain-pane")}
bash "$H" run "$LAB" pane send-keys "$PANE" "$1" && sleep 3 && bash "$H" run "$LAB" pane read "$PANE" --lines 20 2>/dev/null | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -15
