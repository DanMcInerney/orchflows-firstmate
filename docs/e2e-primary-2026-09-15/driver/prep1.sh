#!/usr/bin/env bash
# Prepare the model-driven primary trial: new private Herdr lab session, disposable local-only project, registry entry.
set -u
source /tmp/orchflows-e2e/driver/env.sh
export GIT_AUTHOR_NAME="Orchflows Trial" GIT_AUTHOR_EMAIL="trial@orchflows.invalid" GIT_COMMITTER_NAME="Orchflows Trial" GIT_COMMITTER_EMAIL="trial@orchflows.invalid"
cd "$FM_HOME"
echo "--- old session file: $(cat $E/lab/session)"
NAME=$(bash "$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh" name e2eprimary) || { echo "name failed"; exit 1; }
echo "--- new lab name: $NAME"
if bash "$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh" provision "$NAME"; then
  echo "$NAME" > "$E/lab/session"; echo "provisioned"
else
  echo "PROVISION FAILED"; exit 1
fi
export HERDR_SESSION=$NAME
echo "--- lab status:"; HERDR_SESSION=$NAME herdr status --json --session "$NAME" | jq -c '{server: .server.running, socket: .server.socket_path}'
echo "--- sessions:"; herdr session list --json | jq -c '.sessions[] | {name, default, running}'
P=$FM_HOME/projects/tally
if [ -e "$P" ]; then echo "tally exists already"; else
  mkdir -p "$P" && cd "$P" && git init -q -b main \
  && printf '__pycache__/\n*.pyc\n.orch/\n' > .gitignore \
  && printf '# tally\n\nA word-frequency command-line tool. Not built yet.\n' > README.md \
  && git add -A && git commit -q -m "Seed tally" && echo "--- tally seeded: $(git log --oneline -1)"; git remote -v; git status --short
fi
cd "$FM_HOME"
grep -q "^- tally " data/projects.md || echo "- tally [local-only] - e2e primary trial: word-frequency CLI (added 2026-09-15)" >> data/projects.md
echo "--- projects.md:"; cat data/projects.md
echo "--- backlog head:"; head -5 data/backlog.md
