#!/bin/bash
# Opening the launcher while the mouse cursor rests over a top-bar widget
# (e.g. the media widget) triggers that widget's hover-preview panel
# (Control Center), which force-closes the launcher within ~1s since
# Noctalia's panels are mutually exclusive — confirmed reproducible: with
# the cursor over the bar the launcher self-closes every time; with the
# cursor away from the bar it stays open reliably.
#
# Move the cursor away from the bar first so no hover-trigger can compete
# for the panel slot, regardless of where the mouse happened to be.

MONITOR_INFO=$(hyprctl monitors -j | python3 -c "
import json,sys
m = json.load(sys.stdin)[0]
print(m['width'], m['height'])
")
read -r W H <<< "$MONITOR_INFO"
hyprctl dispatch movecursor $((W / 2)) $((H / 2))

noctalia msg panel-toggle launcher
