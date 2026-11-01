#!/usr/bin/env bash
# Screenshot capture + annotate pipeline: grim + slurp + satty (with swash fallback).
# Bound to Print / SUPER+Print / SUPER+Shift+S (region), Ctrl+Print (window),
# and Alt+Print (screen).
#
# Stability design:
# 1. Single-instance lock (flock) prevents overlapping slurp overlays if Print
#    is pressed repeatedly.
# 2. Region mode feeds visible window geometries on the active workspace(s) into
#    slurp stdin: drag to select any custom rectangle, or single-click a window
#    to snap to its exact bounds.
# 3. Window mode clamps active-window geometry to output bounds so partially
#    off-screen floating windows never cause grim to fail.
# 4. Raw capture is written to ~/Pictures/Screenshots/ and copied to the
#    Wayland clipboard BEFORE Satty opens, so pressing Esc in Satty still
#    leaves the raw screenshot saved and on the clipboard. Pressing Enter or
#    Ctrl+C in Satty overwrites both with the annotated version.

set -euo pipefail

MODE="${1:-region}"
DIR="$HOME/Pictures/Screenshots"
FILE="$DIR/screenshot-$(date +%Y%m%d-%H%M%S).png"
LOCK="${XDG_RUNTIME_DIR:-/tmp}/hypr-screenshot.lock"

# Prevent stacked slurp overlays when Print is pressed while a capture is in flight.
exec 9>"$LOCK"
flock -n 9 || exit 0

mkdir -p "$DIR"

# Pull active accent hex from colors.conf (kept in sync with Noctalia by sync-theme-border.sh).
ACCENT="$(sed -n 's/^\$mauve[[:space:]]*=[[:space:]]*rgba(\([0-9A-Fa-f]\{6\}\).*/\1/p' \
  "$HOME/.config/hypr/config/colors.conf" 2>/dev/null | head -n1)"
ACCENT="${ACCENT:-bd93f9}"

active_window_boxes() {
  local ws_ids
  ws_ids="$(hyprctl monitors -j 2>/dev/null | jq -r '[.[].activeWorkspace.id] | @json' 2>/dev/null || echo '[]')"
  hyprctl clients -j 2>/dev/null | jq -r --argjson ws "$ws_ids" '
    .[]
    | select(.mapped == true and .hidden == false and (.workspace.id as $id | $ws | index($id)))
    | select(.size[0] > 0 and .size[1] > 0)
    | "\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"
  ' 2>/dev/null || true
}

case "$MODE" in
  region)
    geom="$(active_window_boxes | slurp -d -w 2 -F "JetBrains Mono" \
      -b "#00000055" -c "#${ACCENT}ff" -s "#${ACCENT}14" -B "#${ACCENT}44")" || exit 0
    [ -n "$geom" ] || exit 0
    grim -g "$geom" "$FILE"
    ;;
  window)
    geom="$(hyprctl -j activewindow 2>/dev/null | jq -r '
      select(.address != null and .size[0] > 0 and .size[1] > 0)
      | "\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"
    ' 2>/dev/null || true)"
    if [ -n "$geom" ]; then
      # Clamp geometry to total monitor layout bounds so off-screen overhangs never fail in grim.
      clamped="$(hyprctl -j monitors 2>/dev/null | jq -r --arg g "$geom" '
        ($g | capture("^(?<x>-?[0-9]+),(?<y>-?[0-9]+) (?<w>[0-9]+)x(?<h>[0-9]+)$")) as $r
        | ($r.x | tonumber) as $wx | ($r.y | tonumber) as $wy
        | ($r.w | tonumber) as $ww | ($r.h | tonumber) as $wh
        | ([.[].x] | min) as $minx | ([.[].y] | min) as $miny
        | ([.[] | .x + (.width / .scale | floor)] | max) as $maxx
        | ([.[] | .y + (.height / .scale | floor)] | max) as $maxy
        | ([ $wx, $minx ] | max) as $x1
        | ([ $wy, $miny ] | max) as $y1
        | ([ $wx + $ww, $maxx ] | min) as $x2
        | ([ $wy + $wh, $maxy ] | min) as $y2
        | select($x2 > $x1 and $y2 > $y1)
        | "\($x1),\($y1) \($x2 - $x1)x\($y2 - $y1)"
      ' 2>/dev/null || echo "$geom")"
      grim -g "${clamped:-$geom}" "$FILE"
    else
      mon="$(hyprctl monitors -j | jq -r '.[] | select(.focused == true) | .name')"
      grim -o "$mon" "$FILE"
    fi
    ;;
  screen)
    mon="$(hyprctl monitors -j | jq -r '.[] | select(.focused == true) | .name')"
    grim -o "$mon" "$FILE"
    ;;
  *)
    echo "Usage: screenshot.sh {region|window|screen}" >&2
    exit 1
    ;;
esac

# Bail out quietly if the capture was cancelled or failed: grim leaves an
# empty or missing file in that case.
if [ ! -s "$FILE" ]; then
  rm -f "$FILE"
  exit 0
fi

# Release the capture lock before launching the annotator UI so another
# screenshot can be taken while an annotation window stays open.
flock -u 9

wl-copy --type image/png < "$FILE"

if command -v satty >/dev/null 2>&1; then
  exec satty --filename "$FILE" --output-filename "$FILE"
elif command -v swappy >/dev/null 2>&1; then
  exec swappy -f "$FILE" -o "$FILE"
elif command -v swash >/dev/null 2>&1; then
  exec swash "$FILE"
else
  notify-send -a "Screenshot" -i "$FILE" "Screenshot saved" "$FILE (copied to clipboard)"
fi
