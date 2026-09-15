#!/usr/bin/env bash
# say.sh "<text>": type text into the captain pane and press Enter.
set -u
source /tmp/orchflows-e2e/driver/env.sh
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"; PANE=$(cat "$E/lab/captain-pane")
bash "$H" run "$LAB" pane send-text "$PANE" "$1" >/dev/null && sleep 1.5 && bash "$H" run "$LAB" pane send-keys "$PANE" Enter >/dev/null && echo "sent"
sleep 4; bash "$H" run "$LAB" pane read "$PANE" --lines 15 2>/dev/null | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -12
