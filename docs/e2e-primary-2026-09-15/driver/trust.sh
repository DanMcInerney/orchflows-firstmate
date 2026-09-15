#!/usr/bin/env bash
set -u
source /tmp/orchflows-e2e/driver/env.sh
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"
echo "--- viewer start (detached):"; setsid -f bash -c "source /tmp/orchflows-e2e/driver/env.sh; bash \$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh viewer start '$LAB'; echo rc=\$?; sleep 2147483647" > "$E/lab/viewer.log" 2>&1
sleep 8; cat "$E/lab/viewer.log"
echo "--- pane geometry:"; bash "$H" run "$LAB" pane get "w1:p1" 2>/dev/null | jq -c '.result | {rows: .scroll.viewport_rows, agent_status}'
echo "--- answer trust: Down, Enter"; bash "$H" run "$LAB" pane send-keys "w1:p1" Down >/dev/null; sleep 1; bash "$H" run "$LAB" pane send-keys "w1:p1" Enter >/dev/null
sleep 90
echo "--- pane after 90s:"; bash "$H" run "$LAB" pane read "w1:p1" --lines 80 2>&1 | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -60
