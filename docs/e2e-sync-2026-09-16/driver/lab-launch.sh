#!/usr/bin/env bash
# Run the FirstMate primary (Claude Code) in the existing lab pane w1:p1, accept the folder-trust dialog, show the digest.
set -u
export GIT_AUTHOR_NAME="Orchflows Trial" GIT_AUTHOR_EMAIL="trial@orchflows.invalid" GIT_COMMITTER_NAME="Orchflows Trial" GIT_COMMITTER_EMAIL="trial@orchflows.invalid"
E=$HOME/orchflows-e2e
source "$E/driver/env.sh"
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"
echo w1 > "$E/lab/captain-ws"; echo w1:p1 > "$E/lab/captain-pane"
PANE=w1:p1
CMD='bash -c '"'"'source '"$E"'/driver/env.sh; cd '"$E"'/firstmate; exec claude --plugin-dir "$CORE" --setting-sources project,local --dangerously-skip-permissions'"'"
echo "--- pane run: $CMD"
bash "$H" run "$LAB" pane run "$PANE" "$CMD" 2>&1 | head -3
sleep 12
echo "--- pane after 12s:"; bash "$H" run "$LAB" pane read "$PANE" --lines 30 2>&1 | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -25
echo "--- answer trust: Down, Enter"
bash "$H" run "$LAB" pane send-keys "$PANE" Down >/dev/null; sleep 1; bash "$H" run "$LAB" pane send-keys "$PANE" Enter >/dev/null
sleep 75
echo "--- pane after 75s:"; bash "$H" run "$LAB" pane read "$PANE" --lines 90 2>&1 | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -70
