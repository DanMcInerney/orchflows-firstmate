#!/usr/bin/env bash
# Rebuild the FirstMate trial lab in WSL under a persistent path: clone, home, projects, Orchflows core, Herdr lab session.
set -u
export PATH=/mnt/c/Users/danhm/tools/orchflows-firstmate/.scratch/stage1-runtime/bin:$PATH
export GIT_AUTHOR_NAME="Orchflows Trial" GIT_AUTHOR_EMAIL="trial@orchflows.invalid" GIT_COMMITTER_NAME="Orchflows Trial" GIT_COMMITTER_EMAIL="trial@orchflows.invalid"
WT=/mnt/c/Users/danhm/tools/orchflows-firstmate/.claude/worktrees/orchflows-public-release-e7c1a6
SRC_FM=/mnt/c/Users/danhm/tools/orchflows-firstmate/.sources/firstmate
E=$HOME/orchflows-e2e
cd "$HOME"

echo "=== 1. directories under $E"
mkdir -p "$E"/{home/{data,state,config,projects},lab,tmp,driver}

echo "=== 2. FirstMate clone at b182d0f"
if [ ! -d "$E/firstmate/.git" ]; then
  git clone -q "$SRC_FM" "$E/firstmate" || { echo "CLONE FAILED"; exit 1; }
fi
git -C "$E/firstmate" checkout -q b182d0f908b78d08c7ccb8dce3775bdca8c5d657 2>/dev/null || true
git -C "$E/firstmate" checkout -q -B main 2>/dev/null || true
git -C "$E/firstmate" remote set-url origin https://github.com/kunchenguid/firstmate.git
echo "firstmate: $(git -C "$E/firstmate" log --oneline -1) branch=$(git -C "$E/firstmate" branch --show-current)"

echo "=== 3. driver scripts (repointed from /tmp to $E)"
cp "$WT"/docs/e2e-2026-09-15/driver/*.sh "$E/driver/"
cp "$WT"/docs/e2e-primary-2026-09-15/driver/*.sh "$E/driver/"
sed -i "s#/tmp/orchflows-e2e#$E#g" "$E"/driver/*.sh
chmod +x "$E"/driver/*.sh
grep -n '^export E=' "$E/driver/env.sh"

echo "=== 4. home files"
export FM_HOME=$E/home FM_ROOT_OVERRIDE=$E/firstmate FM_HERDR_LAB_STATE_DIR=$E/lab FM_BACKEND=herdr TMPDIR=$E/tmp
printf '# Backlog\n\n## In flight\n## Queued\n## Done\n' > "$FM_HOME/data/backlog.md"
printf 'herdr\n' > "$FM_HOME/config/backend"
cat > "$FM_HOME/config/crew-dispatch.json" <<'EOF'
{
  "rules": [
    {"when": "Orchflows Work: a maker with a clear, bounded assignment",
     "use": {"harness": "claude", "model": "claude-sonnet-5", "effort": "xhigh"},
     "why": "A cheaper model; the assignment and guidance carry the judgment"},
    {"when": "Orchflows Review or investigation: a fresh reviewer, or a scout resolving ambiguity before work",
     "use": {"harness": "codex", "model": "gpt-5.6-luna", "effort": "xhigh"},
     "why": "A different vendor reviews what the maker built"}
  ],
  "default": {"harness": "claude", "model": "claude-sonnet-5", "effort": "xhigh"}
}
EOF

echo "=== 5. orchflows-home project + Orchflows core install"
OH=$FM_HOME/projects/orchflows-home
python3 -B "$WT/packages/orchflows-firstmate/scripts/orchflows.py" setup --home "$OH" --source "$WT/packages/orchflows-firstmate" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("setup:", d["status"], d["core"]["version"], d["core"]["status"], d["git"], d["issues"])'
CORE=$OH/.local/packages/orchflows-firstmate
grep -q '^\.orch/' "$OH/.gitignore" || printf '.orch/\n' >> "$OH/.gitignore"
git -C "$OH" symbolic-ref HEAD refs/heads/main
git -C "$OH" add -A && git -C "$OH" commit -q -m "Seed orchflows-home" 2>/dev/null
git -C "$OH" remote remove origin 2>/dev/null
echo "orchflows-home: $(git -C "$OH" log --oneline -1) remotes=[$(git -C "$OH" remote | tr '\n' ' ')]"
ls "$CORE/skills"

echo "=== 6. target project: roman (local-only, no origin)"
P=$FM_HOME/projects/roman
if [ ! -d "$P/.git" ]; then
  mkdir -p "$P" && git -C "$P" init -q -b main \
  && printf '__pycache__/\n*.pyc\n.orch/\n' > "$P/.gitignore" \
  && printf '# roman\n\nA Roman numeral command-line tool. Not built yet.\n' > "$P/README.md" \
  && git -C "$P" add -A && git -C "$P" commit -q -m "Seed roman"
fi
echo "roman: $(git -C "$P" log --oneline -1) remotes=[$(git -C "$P" remote | tr '\n' ' ')]"

echo "=== 7. projects.md and captain.md"
cat > "$FM_HOME/data/projects.md" <<EOF
- orchflows-home [local-only] - Orchflows FirstMate package home; saved workflows ship into libraries/ (added 2026-09-16)
- roman [local-only] - trial target: Roman numeral CLI (added 2026-09-16)
EOF
cat > "$FM_HOME/data/captain.md" <<EOF
# Captain preferences

## Orchflows
- Run every ship and scout through orch-dynamic-workflow unless I name another workflow or say "plain". Run any other workflow only when I name it: invoke it by its slash command or read its SKILL.md by path.
- Resolve each agent's model and effort per $CORE/docs/architecture.md#model-and-effort: my request, then the saved workflow, then the Orchflows rules in crew-dispatch.json, then your effort fallback.
- Record each workflow's phase and task IDs in the backlog item note and resume from it after a restart.
- Read $CORE/docs/firstmate.md before the first Orchflows dispatch of a session.
EOF
cat "$FM_HOME/data/captain.md"

echo "=== 8. herdr lab session"
cd "$FM_HOME"
NAME=$(bash "$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh" name e2esync) || { echo "name failed"; exit 1; }
echo "lab name: $NAME"
setsid -f bash -c 'source "$2/driver/env.sh"; cd "$FM_HOME"; bash "$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh" provision "$1"; echo "provision rc=$?"; sleep 2147483647' _ "$NAME" "$E" > "$E/lab/provision.log" 2>&1
r=false
for i in $(seq 1 60); do sleep 1; r=$(HERDR_SESSION=$NAME herdr status --json --session "$NAME" 2>/dev/null | jq -r '.server.running // false'); [ "$r" = true ] && break; done
echo "running after ${i}s: $r"; cat "$E/lab/provision.log"
if [ "$r" = true ]; then echo "$NAME" > "$E/lab/session"; fi
echo "--- sessions:"; herdr session list --json | jq -c '.sessions[] | {name, running}'
echo "=== done"
