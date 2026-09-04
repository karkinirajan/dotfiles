#!/bin/bash
# Screenshot capture + annotate, bound to Print/Ctrl+Print/Alt+Print.
#
# Capture: grim + slurp. hyprshot was tried first but removed — it showed a
# flaky first-launch failure on this machine (silent exit, no window, no
# error) that was never fully root-caused, so grim/slurp (older, more
# battle-tested) is used directly instead of as a fallback.
#
# Annotate: satty, falling back to swappy if satty fails to launch.
#
# grimblast (the original binding target, predating both of the above) also
# isn't installed on this system anymore — all three Print-key bindings were
# silently no-ops until this was written.

MODE="$1"
DIR="$HOME/Pictures/Screenshots"
FILE="$DIR/screenshot-$(date +%Y%m%d-%H%M%S).png"
TMP="$(mktemp --suffix=.png)"
trap 'rm -f "$TMP"' EXIT

mkdir -p "$DIR"

case "$MODE" in
  region)
    slurp | grim -g - "$TMP"
    ;;
  window)
    geom=$(hyprctl activewindow -j | jq -r '"\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"')
    grim -g "$geom" "$TMP"
    ;;
  screen)
    mon=$(hyprctl monitors -j | jq -r '.[] | select(.focused==true) | .name')
    grim -o "$mon" "$TMP"
    ;;
  *)
    echo "Usage: screenshot.sh {region|window|screen}" >&2
    exit 1
    ;;
esac

# Bail out quietly if the capture was cancelled (e.g. Esc during region
# select) — slurp/grim leave an empty or missing file in that case.
[ -s "$TMP" ] || exit 0

wl-copy --type image/png < "$TMP"

# Annotate: satty, falling back to swappy on failure.
if ! satty --filename "$TMP" -o "$FILE" --copy-command wl-copy --early-exit copy; then
  swappy -f "$TMP" -o "$FILE"
fi
