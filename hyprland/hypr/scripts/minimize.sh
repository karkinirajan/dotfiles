#!/usr/bin/env bash
# Sends the active window to the "minimized" special workspace and
# remembers which real workspace it came from, so restore.sh can
# put it back into normal tiling instead of leaving it stuck as a
# floating overlay on the special workspace.
set -euo pipefail

state_file="$HOME/.cache/hypr/minimized.tsv"
mkdir -p "$(dirname "$state_file")"
touch "$state_file"

win=$(hyprctl activewindow -j)
addr=$(jq -r '.address' <<<"$win")
ws=$(jq -r '.workspace.id' <<<"$win")

[[ -z "$addr" || "$addr" == "null" ]] && exit 0

# Drop any stale entry for this window, then record where it came from.
grep -v "^${addr}	" "$state_file" > "${state_file}.tmp" || true
mv "${state_file}.tmp" "$state_file"
printf '%s\t%s\n' "$addr" "$ws" >> "$state_file"

hyprctl dispatch movetoworkspacesilent special:minimized
