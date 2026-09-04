#!/bin/bash
# Screenshot capture + annotate, bound to Print/Ctrl+Print/Alt+Print.
#
# Primary: hyprshot (purpose-built for Hyprland) + satty (annotation).
# grimblast (the original binding target) isn't installed on this system
# anymore, so all three Print-key bindings were silently no-ops until this
# was written.
#
# hyprshot's own `-- command` hook only appends the saved file path as a
# single trailing argument to a single-word command (see its source: it
# runs `"$COMMAND" "$output"` with $COMMAND quoted as one token), so it
# can't invoke something like `satty --filename -` directly. Capturing to
# a temp file first (instead of piping straight into satty) also lets the
# raw capture get copied to the clipboard immediately, before satty even
# opens — matching the old grimblast behavior of an instant copy on
# capture, with annotation still available as an extra step afterward.
#
# Fallback: grim + slurp (capture) + swappy (annotation). hyprshot/satty
# have shown a one-off flaky-first-launch failure on this machine (silent
# exit, no window, no error) that self-resolves after the first attempt —
# cause not fully pinned down (portal/GTK-cache warmup suspected), but
# rather than chase it further, capture and annotation both fall back to
# the older, more battle-tested grim/slurp/swappy combo automatically if
# the primary path fails.

MODE="$1"
DIR="$HOME/Pictures/Screenshots"
FILE="$DIR/screenshot-$(date +%Y%m%d-%H%M%S).png"
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

# ── grim+slurp fallback capture, per mode ───────────────────────────────
_grim_capture() {
  case "$MODE" in
    region)
      slurp | grim -g - "$TMP"
      ;;
    window)
      local geom
      geom=$(hyprctl activewindow -j | jq -r '"\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"')
      grim -g "$geom" "$TMP"
      ;;
    screen)
      local mon
      mon=$(hyprctl monitors -j | jq -r '.[] | select(.focused==true) | .name')
      grim -o "$mon" "$TMP"
      ;;
  esac
}

# ── primary: hyprshot ────────────────────────────────────────────────────
hyprshot "${HYPRSHOT_ARGS[@]}" --raw --silent > "$TMP"
if [ ! -s "$TMP" ]; then
  # region mode with Esc cancelled is also an empty file — but hyprshot
  # exits 0 either way, so we can't tell "cancelled" from "hyprshot itself
  # failed" here. Try the grim fallback; if the user genuinely cancelled a
  # region select, slurp below will also come back empty and we bail out
  # quietly rather than looping forever.
  _grim_capture
fi

[ -s "$TMP" ] || exit 0

wl-copy --type image/png < "$TMP"

# ── annotate: satty, falling back to swappy on failure ─────────────────
if ! satty --filename "$TMP" -o "$FILE" --copy-command wl-copy --early-exit copy; then
  swappy -f "$TMP" -o "$FILE"
fi
