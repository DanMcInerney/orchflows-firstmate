#!/usr/bin/env bash
# Read-only verification of the trial outputs: roman main, the quickfix library in the home, catalogs, task records.
set -u
export PATH=/mnt/c/Users/danhm/tools/orchflows-firstmate/.scratch/stage1-runtime/bin:$PATH
E=$HOME/orchflows-e2e; FM_HOME=$E/home
R=$FM_HOME/projects/roman; OH=$FM_HOME/projects/orchflows-home
CORE=$OH/.local/packages/orchflows-firstmate
echo "=== roman main"; git -C "$R" log --oneline main | head -8; git -C "$R" status --short | head -5; git -C "$R" remote -v
echo "--- tests"; (cd "$R" && python3 -m unittest 2>&1 | tail -3)
echo "--- commands"; (cd "$R" && python3 roman.py 1994 MCMXCIV; echo "rc=$?"; python3 roman.py mcmxciv; echo "rc=$?"; python3 roman.py --lower 1994; echo "rc=$?"; python3 roman.py --lower mcmxciv; echo "rc=$?"; python3 roman.py --json 4 IV xx 2>/dev/null; echo "rc=$?"; python3 roman.py --bogus 2>&1 | tail -1; echo "rc=$?")
echo; echo "=== orchflows-home main"; git -C "$OH" log --oneline main | head -8; git -C "$OH" status --short | head -5
echo "--- libraries"; ls "$OH/libraries" 2>&1; find "$OH/libraries" -type f 2>/dev/null | sed "s#$OH/##" | head -30
echo "--- quickfix fix SKILL.md"; cat "$OH/libraries/quickfix/skills/fix/SKILL.md" 2>/dev/null
echo "--- quickfix openai.yaml"; cat "$OH/libraries/quickfix/skills/fix/agents/openai.yaml" 2>/dev/null
echo "--- catalogs"; grep -o '"name": *"[^"]*"' "$OH/.claude-plugin/marketplace.json" | tr '\n' ' '; echo
echo "--- doctor"; python3 -B "$CORE/scripts/orchflows.py" doctor --home "$OH" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["status"], [l["name"] for l in d["checks"]["libraries"]], d["issues"])'
echo "--- resolve"; python3 -B "$CORE/scripts/orchflows.py" resolve quickfix --home "$OH" --skill fix 2>&1 | head -2
echo; echo "=== backlog"; cat "$FM_HOME/data/backlog.md"
echo; echo "=== task metadata"; for m in "$FM_HOME"/state/*.meta; do [ -f "$m" ] && { echo "$(basename "$m" .meta): $(grep -E '^(kind|mode|harness|model|effort)=' "$m" | tr '\n' ' ')"; }; done
echo "=== reports"; ls "$FM_HOME"/data/*/report.md 2>/dev/null
echo "=== steers"; ls "$FM_HOME"/state/*.inbox/handled 2>/dev/null | head
