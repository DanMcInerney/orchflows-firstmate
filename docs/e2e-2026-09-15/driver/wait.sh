#!/usr/bin/env bash
# wait.sh <task-id> [max-seconds]: poll until a terminal status event; print state.
. /tmp/orchflows-e2e/driver/env.sh
id=$1; max=${2:-2400}; start=$(date +%s)
while :; do
  status=$FM_HOME/state/$id.status
  last=$( [ -f "$status" ] && tail -1 "$status" || echo "" )
  state=$(bash "$FM_ROOT_OVERRIDE/bin/fm-crew-state.sh" "$id" 2>/dev/null || echo "state: unknown")
  now=$(date +%s); el=$((now-start))
  echo "[$el s] $state | last: $last"
  case "$last" in done:*|failed:*|blocked:*|needs-decision:*) exit 0;; esac
  [ $el -lt $max ] || { echo "TIMEOUT"; exit 3; }
  sleep 30
done
