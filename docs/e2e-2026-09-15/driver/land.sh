#!/usr/bin/env bash
# land.sh <ship-id> [<scout-id>...]: FirstMate merges the ship branch locally, then tears down every listed task.
# Stops if the merge did not land, so a refused merge never leads to a teardown attempt or a mis-based next phase.
set -uo pipefail
. /tmp/orchflows-e2e/driver/env.sh
ship=$1; shift
proj=$(grep -m1 '^project=' "$FM_HOME/state/$ship.meta" | cut -d= -f2)
echo "=== merge-local $ship"; fm fm-merge-local.sh "$ship" 2>&1 | grep -v "^WARNING\|^●" | tail -6
if ! git -C "$proj" merge-base --is-ancestor "fm/$ship" main 2>/dev/null; then
  echo "MERGE DID NOT LAND; stopping before teardown"; exit 1
fi
echo "=== main after merge"; git -C "$proj" log --oneline -3
for id in "$ship" "$@"; do
  echo "=== teardown $id"; fm fm-teardown.sh "$id" 2>&1 | grep -v "^WARNING\|^●" | tail -4
done
echo "=== backlog"; tasks-axi list --file "$FM_HOME/data/backlog.md" 2>&1 | sed -n '2,12p'
