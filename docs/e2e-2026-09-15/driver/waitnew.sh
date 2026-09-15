#!/usr/bin/env bash
# waitnew.sh <task-id> <lines-already-present> [max-seconds]: wait for a terminal status line beyond the given count.
. /tmp/orchflows-e2e/driver/env.sh
id=$1; skip=$2; max=${3:-2400}; start=$(date +%s)
while :; do
  status=$FM_HOME/state/$id.status
  new=$( [ -f "$status" ] && tail -n +$((skip+1)) "$status" || echo "" )
  last=$(printf '%s\n' "$new" | grep -v '^$' | tail -1)
  state=$(bash "$FM_ROOT_OVERRIDE/bin/fm-crew-state.sh" "$id" 2>/dev/null || echo "state: unknown")
  now=$(date +%s); el=$((now-start))
  echo "[$el s] $state | new: $last"
  case "$last" in done:*|failed:*|blocked:*|needs-decision:*) exit 0;; esac
  [ $el -lt $max ] || { echo "TIMEOUT"; exit 3; }
  sleep 30
done
