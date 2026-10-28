#!/usr/bin/env bash
# Adjust the hyprsunset color temperature from the Noctalia bar.
# Lower Kelvin values are warmer; the chosen value persists across toggles.
set -euo pipefail

STATE_DIR="$HOME/.local/state/hyprsunset"
TEMP_FILE="$STATE_DIR/temperature-k"
ON_FILE="/tmp/noctalia-nightlight-on"
STEP=250
MIN=2500
MAX=6500

case "${1:-}" in
  warmer) delta=-$STEP ;;
  cooler) delta=$STEP ;;
  *) echo "Usage: ${0##*/} warmer|cooler" >&2; exit 2 ;;
esac

mkdir -p "$STATE_DIR"
current=5500
if [[ -r "$TEMP_FILE" ]] && read -r candidate < "$TEMP_FILE" && [[ "$candidate" =~ ^[0-9]+$ ]]; then
  current=$candidate
fi
next=$((current + delta))
(( next < MIN )) && next=$MIN
(( next > MAX )) && next=$MAX
printf '%s\n' "$next" > "$TEMP_FILE"

if [[ -e "$ON_FILE" ]] && pgrep -x hyprsunset >/dev/null; then
  pkill -x hyprsunset || true
  sleep 0.2
  nohup hyprsunset -t "$next" >/tmp/hyprsunset.log 2>&1 </dev/null &
fi

if command -v notify-send >/dev/null 2>&1; then
  notify-send -a "Night Light" "${next} K" "$([[ $delta -lt 0 ]] && echo Warmer || echo Cooler)" -t 1200
fi
