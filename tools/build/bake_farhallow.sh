#!/bin/sh
# Bake voxel Farhallow's buildings (BuildingKit.load_or_build) so the village loads them instead of building them.
# Run after changing the building kit, its layouts or the plan, and before an export. Needs a real renderer (not
# --headless): on a desktop just run it; in the cloud it runs under xvfb-run.
cd "$(dirname "$0")/../../godot" || exit 1
if [ -z "$DISPLAY" ] && command -v xvfb-run >/dev/null; then X="xvfb-run -a -s '-screen 0 1280x720x24'"; else X=""; fi
eval $X godot --path . --rendering-driver opengl3 res://scenes/farhallow_voxel.tscn -- bake 2>&1 | grep -E "BAKE|ready in|ERROR"
