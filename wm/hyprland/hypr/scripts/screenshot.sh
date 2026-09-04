#!/bin/bash
# Screenshot capture + annotate, bound to Print/Ctrl+Print/Alt+Print.
#
# grimblast (the previous binding target) isn't installed on this system
# anymore, so all three Print-key bindings were silently no-ops. Switched to
# hyprshot (purpose-built for Hyprland, actively maintained) + satty
# (annotation) instead — both already installed but unused.
#
# hyprshot's own `-- command` hook only appends the saved file path as a
# single trailing argument to a single-word command (see its source: it
# runs `"$COMMAND" "$output"` with $COMMAND quoted as one token), so it
# can't invoke something like `satty --filename -` directly. Capturing to
# a temp file first (instead of piping straight into satty) also lets the
# raw capture get copied to the clipboard immediately, before satty even
# opens — matching the old grimblast behavior of an instant copy on
# capture, with annotation still available as an extra step afterward.

MODE="$1"
DIR="$HOME/Pictures/Screenshots"
FILE="$DIR/satty-$(date +%Y%m%d-%H%M%S).png"
TMP="$(mktemp --suffix=.png)"
trap 'rm -f "$TMP"' EXIT

mkdir -p "$DIR"

case "$MODE" in
  region) HYPRSHOT_ARGS=(-m region) ;;
  window) HYPRSHOT_ARGS=(-m window -m active) ;;
  screen) HYPRSHOT_ARGS=(-m output -m active) ;;
  *)
    echo "Usage: screenshot.sh {region|window|screen}" >&2
    exit 1
    ;;
esac

hyprshot "${HYPRSHOT_ARGS[@]}" --raw --silent > "$TMP"

# Bail out quietly if the capture was cancelled (e.g. Esc during region
# select) — hyprshot still exits 0 in that case but writes an empty file.
[ -s "$TMP" ] || exit 0

wl-copy --type image/png < "$TMP"
satty --filename "$TMP" -o "$FILE" --copy-command wl-copy --early-exit copy
