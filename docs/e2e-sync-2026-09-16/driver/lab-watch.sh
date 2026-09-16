#!/usr/bin/env bash
# lab-watch.sh <seconds> [interval] [grep]: poll task states and the captain pane; "grep" first dumps scrollback lines about skills.
set -u
E=$HOME/orchflows-e2e
source "$E/driver/env.sh"
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"; PANE=$(cat "$E/lab/captain-pane")
MAX=${1:-240}; INT=${2:-60}; MODE=${3:-}
if [ "$MODE" = grep ]; then
  echo "===== scrollback lines about skills"
  bash "$H" run "$LAB" pane read "$PANE" --lines 800 2>/dev/null | sed 's/[[:space:]]*$//' | grep -n -E 'Skill[(]|orch-|firstmate[.]md|SKILL[.]md|disable-model|Read[(]' | head -50
fi
start=$(date +%s)
while :; do
  now=$(date +%s); el=$((now-start))
  echo "===== +${el}s $(date -u +%H:%M:%SZ)"
  for m in "$FM_HOME"/state/*.meta; do
    [ -f "$m" ] || continue; id=$(basename "$m" .meta)
    printf '  task %s: %s | %s | last: %s\n' "$id" "$(grep -E '^(kind|harness|model|effort)=' "$m" | cut -d= -f2 | tr '\n' ' ')" "$(bash "$FM_ROOT_OVERRIDE/bin/fm-crew-state.sh" "$id" 2>/dev/null | head -1)" "$(tail -1 "$FM_HOME/state/$id.status" 2>/dev/null)"
  done
  echo "  backlog:"; sed -n '/## In flight/,/## Done/p' "$FM_HOME/data/backlog.md" | grep -E '^- |^  orchflows' | head -8 | sed 's/^/    /'
  [ $el -ge $MAX ] && break
  sleep "$INT"
done
echo "===== captain pane tail"
bash "$H" run "$LAB" pane read "$PANE" --lines 60 2>/dev/null | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -45
