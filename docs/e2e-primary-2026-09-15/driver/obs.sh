#!/usr/bin/env bash
# obs.sh [pane-lines]: captain pane tail, backlog, task states, status logs, inboxes, tabs.
set -u
source /tmp/orchflows-e2e/driver/env.sh
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"; PANE=$(cat "$E/lab/captain-pane"); N=${1:-60}
echo "===== $(date -u +%H:%M:%SZ) captain pane (last $N lines)"; bash "$H" run "$LAB" pane read "$PANE" --lines "$N" 2>/dev/null | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -"$N"
echo "===== backlog"; sed -n '1,40p' "$FM_HOME/data/backlog.md"
for m in "$FM_HOME"/state/*.meta; do [ -f "$m" ] || continue; id=$(basename "$m" .meta); echo "===== task $id: $(grep -E '^(kind|mode|harness|model|effort)=' "$m" | tr '\n' ' ')"; echo "state: $(bash "$FM_ROOT_OVERRIDE/bin/fm-crew-state.sh" "$id" 2>/dev/null | head -1)"; echo "status: "; cat "$FM_HOME/state/$id.status" 2>/dev/null; [ -d "$FM_HOME/state/$id.inbox" ] && echo "inbox: $(ls "$FM_HOME/state/$id.inbox" | tr '\n' ' ')"; done
echo "===== tabs"; bash "$H" run "$LAB" tab list 2>/dev/null | jq -c '(.result.tabs // .result // [])[] | {id: (.tab_id // .id), label, workspace: (.workspace_id // .workspace)}' 2>/dev/null | head -20
