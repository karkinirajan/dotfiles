#!/bin/bash
# Screenshot capture + annotate, bound to Print/Ctrl+Print/Alt+Print.
#
# Capture: grim + slurp. hyprshot was tried first but removed — it showed a
# flaky first-launch failure on this machine (silent exit, no window, no
# error) that was never fully root-caused, so grim/slurp (older, more
# battle-tested) is used directly instead of as a fallback.
#
# Annotate: swash, the only screenshot editor on this system (satty, swappy
# and flameshot were removed). swash cannot capture by itself, so grim/slurp
# stay as the capture backend.
#
# The raw capture is saved and copied to the clipboard before swash opens,
# so closing swash without saving still leaves a usable screenshot.

MODE="$1"
DIR="$HOME/Pictures/Screenshots"
FILE="$DIR/screenshot-$(date +%Y%m%d-%H%M%S).png"

mkdir -p "$DIR"

case "$MODE" in
  region)
    geom=$(slurp) || exit 0
    grim -g "$geom" "$FILE"
    ;;
  window)
    geom=$(hyprctl activewindow -j | jq -r '"\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"')
    grim -g "$geom" "$FILE"
    ;;
  screen)
    mon=$(hyprctl monitors -j | jq -r '.[] | select(.focused==true) | .name')
    grim -o "$mon" "$FILE"
    ;;
  *)
    echo "Usage: screenshot.sh {region|window|screen}" >&2
    exit 1
    ;;
esac

# Bail out quietly if the capture was cancelled or failed — grim leaves an
# empty or missing file in that case.
if [ ! -s "$FILE" ]; then
  rm -f "$FILE"
  exit 0
fi

wl-copy --type image/png < "$FILE"

exec swash "$FILE"
