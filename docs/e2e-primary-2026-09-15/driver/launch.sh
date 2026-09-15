#!/usr/bin/env bash
# launch.sh: create a captain workspace in the lab session and start the FirstMate primary (claude) in its pane.
set -u
source /tmp/orchflows-e2e/driver/env.sh
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"
echo "--- workspace create"; out=$(bash "$H" run "$LAB" workspace create --cwd "$FM_ROOT_OVERRIDE" --label captain --focus 2>&1); echo "$out"
WS=$(printf '%s' "$out" | jq -r '.result.workspace_id // .result.workspace.id // .result.id // empty' 2>/dev/null)
echo "WS=$WS"; echo "$WS" > "$E/lab/captain-ws"
echo "--- panes in workspace"; panes=$(bash "$H" run "$LAB" pane list --workspace "$WS" 2>&1); echo "$panes"
PANE=$(printf '%s' "$panes" | jq -r '(.result.panes // .result // [])[0] | (.pane_id // .id // empty)' 2>/dev/null)
echo "PANE=$PANE"; echo "$PANE" > "$E/lab/captain-pane"
CMD='bash -c '"'"'source /tmp/orchflows-e2e/driver/env.sh; cd /tmp/orchflows-e2e/firstmate; exec claude --plugin-dir "$CORE" --setting-sources project,local --dangerously-skip-permissions'"'"
echo "--- pane run: $CMD"; bash "$H" run "$LAB" pane run "$PANE" "$CMD" 2>&1 | head -5
sleep 8
echo "--- pane after 8s:"; bash "$H" run "$LAB" pane read "$PANE" --lines 40 2>&1 | tail -40
