#!/usr/bin/env bash
# Stop the default Herdr server this trial started (it was not running before), and report the final session state.
export PATH=/mnt/c/Users/danhm/tools/orchflows-firstmate/.scratch/stage1-runtime/bin:$PATH
unset HERDR_SESSION
cd "$HOME"
echo "--- sessions"; herdr session list --json | jq -c '.sessions[] | {name, default, running}'
if [ "$(herdr status --json 2>/dev/null | jq -r '.server.running')" = true ]; then
  herdr server stop 2>&1 | tail -1; sleep 2
fi
echo "--- default running now: $(herdr status --json 2>/dev/null | jq -r '.server.running')"
echo "--- lab state dir"; ls "$HOME/orchflows-e2e/lab"
echo "--- leftover herdr/claude/codex processes"; pgrep -af 'herdr|fm-herdr-lab-viewer|claude|codex' | grep -v pgrep | head
