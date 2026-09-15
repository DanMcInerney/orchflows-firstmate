#!/usr/bin/env bash
set -u
source /tmp/orchflows-e2e/driver/env.sh
export GIT_AUTHOR_NAME="Orchflows Trial" GIT_AUTHOR_EMAIL="trial@orchflows.invalid" GIT_COMMITTER_NAME="Orchflows Trial" GIT_COMMITTER_EMAIL="trial@orchflows.invalid"
NAME=$(cat "$E/lab/session"); echo "lab: $NAME"
echo "--- sessions before:"; herdr session list --json | jq -c '.sessions[] | {name, running}'
setsid -f bash -c "source /tmp/orchflows-e2e/driver/env.sh; cd \$FM_HOME; bash \$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh provision '$NAME'; echo \"provision rc=\$?\"; sleep 2147483647" > "$E/lab/provision.log" 2>&1
for i in $(seq 1 30); do sleep 1; r=$(HERDR_SESSION=$NAME herdr status --json --session "$NAME" 2>/dev/null | jq -r '.server.running // false'); [ "$r" = true ] && break; done
echo "--- running after ${i}s: $r"; cat "$E/lab/provision.log"
echo "--- sessions after:"; herdr session list --json | jq -c '.sessions[] | {name, running}'
