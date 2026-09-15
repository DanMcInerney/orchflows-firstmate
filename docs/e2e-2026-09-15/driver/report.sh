#!/usr/bin/env bash
# report.sh <id>: status log, crew state, and either the scout report or the ship branch summary.
set -uo pipefail
. /tmp/orchflows-e2e/driver/env.sh
id=$1
echo "=== status log ($FM_HOME/state/$id.status)"; cat "$FM_HOME/state/$id.status" 2>/dev/null
echo "=== crew state"; fm fm-crew-state.sh "$id" 2>/dev/null
kind=$(grep -m1 '^kind=' "$FM_HOME/state/$id.meta" | cut -d= -f2)
wt=$(grep -m1 '^worktree=' "$FM_HOME/state/$id.meta" | cut -d= -f2)
proj=$(grep -m1 '^project=' "$FM_HOME/state/$id.meta" | cut -d= -f2)
if [ "$kind" = scout ]; then
  echo "=== report ($FM_HOME/data/$id/report.md)"; cat "$FM_HOME/data/$id/report.md" 2>/dev/null || echo "(no report yet)"
else
  echo "=== branch fm/$id in $proj"
  git -C "$proj" log --oneline "main..fm/$id" 2>/dev/null || echo "(branch not visible from project)"
  echo "=== worktree status"; git -C "$wt" status --short 2>/dev/null | head; git -C "$wt" log --oneline -5 2>/dev/null
  echo "=== diff stat vs main"; git -C "$proj" diff --stat "main...fm/$id" 2>/dev/null | tail -20
fi
