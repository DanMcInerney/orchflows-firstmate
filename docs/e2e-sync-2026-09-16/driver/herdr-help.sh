#!/usr/bin/env bash
export PATH=/mnt/c/Users/danhm/tools/orchflows-firstmate/.scratch/stage1-runtime/bin:$PATH
cd "$HOME"
echo "=== herdr --help"; herdr --help 2>&1 | head -40
echo; echo "=== herdr server --help"; herdr server --help 2>&1 | head -30
echo; echo "=== herdr session --help"; herdr session --help 2>&1 | head -30
echo; echo "=== herdr status"; herdr status --json 2>&1 | head -5
