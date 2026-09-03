#!/usr/bin/env bash
# Moves every window currently parked on the "minimized" special
# workspace back onto the real workspace it was minimized from
# (falling back to the currently active workspace if we never
# recorded one), so it re-tiles instead of staying an overlay.
set -euo pipefail

state_file="$HOME/.cache/hypr/minimized.tsv"
touch "$state_file"

current_ws=$(hyprctl activeworkspace -j | jq -r '.id')

addrs=$(hyprctl clients -j | jq -r '.[] | select(.workspace.name == "special:minimized") | .address')

for addr in $addrs; do
    origin=$(awk -F'\t' -v a="$addr" '$1 == a { print $2; exit }' "$state_file")
    target="${origin:-$current_ws}"
    hyprctl dispatch movetoworkspace "${target},address:${addr}" >/dev/null
    grep -v "^${addr}	" "$state_file" > "${state_file}.tmp" || true
    mv "${state_file}.tmp" "$state_file"
done
