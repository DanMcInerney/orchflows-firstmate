#!/usr/bin/env bash
# dispatch.sh <id> <project-name> <scout|ship> <intent-file> <spec-file> <harness> <model> <effort> "<title>" ["<backlog note>"]
# Captain-side mechanics only: backlog item, brief, fill, spawn. Decisions are the caller's.
set -euo pipefail
. /tmp/orchflows-e2e/driver/env.sh
id=$1 project=$2 kind=$3 intent=$4 spec=$5 harness=$6 model=$7 effort=$8 title=$9 note=${10:-}
cd "$FM_HOME"
if ! tasks-axi show "$id" --file data/backlog.md >/dev/null 2>&1; then
  tasks-axi add "$id" "$title" --kind "$kind" --repo "$project" --file data/backlog.md --json | jq -c '{ok,action}'
fi
[ -z "$note" ] || tasks-axi update "$id" --file data/backlog.md --body "$note" --json | jq -c '{ok,action}'
if [ "$kind" = scout ]; then
  fm fm-brief.sh "$id" "$project" --scout 2>&1 | tail -1
else
  fm fm-brief.sh "$id" "$project" --mode local-only 2>&1 | tail -1
fi
python3 - "$FM_HOME/data/$id/brief.md" "$intent" "$spec" "$CORE" <<'EOF'
import sys, pathlib
brief, intent, spec = [pathlib.Path(p) for p in sys.argv[1:4]]
core = sys.argv[4]
text = brief.read_text()
assert "{TASK}" in text and "{FIRSTMATE_SPEC}" in text, "placeholders missing"
text = text.replace("{TASK}", intent.read_text().strip()).replace(
    "{FIRSTMATE_SPEC}", spec.read_text().strip().replace("CORE_PATH", core))
brief.write_text(text)
print("brief filled:", len(text), "chars")
EOF
if [ "$kind" = scout ]; then
  fm fm-spawn.sh "$id" "$FM_HOME/projects/$project" --scout --backend herdr --harness "$harness" --model "$model" --effort "$effort" 2>&1 | grep -v "^WARNING\|^●" | tail -3
else
  fm fm-spawn.sh "$id" "$FM_HOME/projects/$project" --mode local-only --yolo off --backend herdr --harness "$harness" --model "$model" --effort "$effort" 2>&1 | grep -v "^WARNING\|^●" | tail -3
fi
grep -E "^(kind|mode|harness|model|effort|worktree|herdr_pane_id|spawn_gen)=" "state/$id.meta" | tr '\n' ' '; echo
