#!/usr/bin/env bash
# Collect trial evidence into the repository worktree under docs/e2e-sync-2026-09-16/.
set -u
export PATH=/mnt/c/Users/danhm/tools/orchflows-firstmate/.scratch/stage1-runtime/bin:$PATH
E=$HOME/orchflows-e2e; FM_HOME=$E/home; FM_ROOT_OVERRIDE=$E/firstmate
WT=/mnt/c/Users/danhm/tools/orchflows-firstmate/.claude/worktrees/orchflows-public-release-e7c1a6
D=$WT/docs/e2e-sync-2026-09-16
mkdir -p "$D"/{briefs,reports,quickfix,roman/tests,state,driver}
LAB=$(cat "$E/lab/session"); H="$FM_ROOT_OVERRIDE/bin/fm-herdr-lab.sh"; PANE=$(cat "$E/lab/captain-pane")

echo "=== briefs and reports"
for t in roman-cli roman-cli-review quickfix-lib roman-lower roman-lower-review quickfix-lib-review roman-json roman-json-review; do
  [ -f "$FM_HOME/data/$t/brief.md" ] && cp "$FM_HOME/data/$t/brief.md" "$D/briefs/$t.md"
  [ -f "$FM_HOME/data/$t/report.md" ] && cp "$FM_HOME/data/$t/report.md" "$D/reports/$t.md"
done
[ -f "$FM_HOME/data/quickfix-lib/trial-record.md" ] && cp "$FM_HOME/data/quickfix-lib/trial-record.md" "$D/trial-record.md"
ls "$D/briefs" "$D/reports"

echo "=== home files"
cp "$FM_HOME/data/backlog.md" "$D/backlog.md"
cp "$FM_HOME/data/captain.md" "$D/captain.md"
cp "$FM_HOME/data/projects.md" "$D/projects.md"
cp "$FM_HOME/config/crew-dispatch.json" "$D/crew-dispatch.json"
echo "$LAB" > "$D/state/lab-session.txt"
ls "$FM_HOME/state" > "$D/state/state-listing.txt"

echo "=== quickfix library (from orchflows-home main)"
OH=$FM_HOME/projects/orchflows-home
(cd "$OH" && git archive main libraries/quickfix | tar -x -C "$D/quickfix" --strip-components=2)
git -C "$OH" log --format='%h %ad %an %s' --date=iso > "$D/quickfix/git-log.txt"
find "$D/quickfix" -type f | sed "s#$D/##"

echo "=== roman (from main)"
R=$FM_HOME/projects/roman
cp "$R/roman.py" "$R/README.md" "$R/.gitignore" "$D/roman/"; [ -f "$R/AGENTS.md" ] && cp "$R/AGENTS.md" "$D/roman/"
cp "$R"/tests/*.py "$D/roman/tests/" 2>/dev/null
git -C "$R" log --format='%h %ad %an %s' --date=iso > "$D/roman/git-log.txt"
(cd "$R" && python3 -m unittest 2>&1 | tail -2)

echo "=== captain pane scrollback"
bash "$H" run "$LAB" pane read "$PANE" --lines 6000 2>/dev/null | sed 's/[[:space:]]*$//' > "$D/captain-pane.txt"
wc -l "$D/captain-pane.txt"

echo "=== captain transcript"
sed "s#-tmp-orchflows-e2e-firstmate#-home-danhm-orchflows-e2e-firstmate#" "$WT/docs/e2e-primary-2026-09-15/driver/transcript-full.py" | tr -d '\r' > "$E/driver/transcript-full.py"
python3 "$E/driver/transcript-full.py" > "$D/captain-transcript.md" 2> "$E/lab/transcript.err" || cat "$E/lab/transcript.err"
head -5 "$D/captain-transcript.md"; wc -l "$D/captain-transcript.md"

echo "=== drivers used"
cp "$E"/driver/*.sh "$E/driver/transcript-full.py" "$D/driver/" 2>/dev/null
ls "$D/driver"
echo "=== done"
