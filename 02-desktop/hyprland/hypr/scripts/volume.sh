#!/bin/bash
# Volume control that can go ABOVE 100%.
#
# Noctalia caps the volume at 100% and offers no way to raise it:
#   * `noctalia msg volume-set 110` leaves the sink at 1.00 (verified)
#   * `noctalia msg volume-osd 110` fails outright with
#     "invalid volume value (use percent like 65 or 65%, or normalized ...)"
#   * its Settings window has no Audio section at all, and a search for
#     "amplif" returns "No settings found"
#
# PipeWire has no such limit — `wpctl set-volume @DEFAULT_AUDIO_SINK@ 110%`
# sets 1.10 without complaint — so this drives wpctl directly and uses its
# own `--limit` flag as the ceiling.
#
# The keybinds this replaces went through pactl and clamped to 100% by hand
# (`awk '{if($1>100) system("pactl set-sink-volume ... 100%")}'`), which is
# where the cap was actually coming from on the keyboard path.
#
# Usage: volume.sh up | down | max | full | mute | set <percent>

set -uo pipefail

# Ceiling for boosted volume, as a percentage. Past roughly 150% most
# speakers distort rather than get louder, so that is the default. Raise it
# here if you want more headroom — it is the only place the limit is set.
CEILING_PCT=150
STEP_PCT=5
SINK="@DEFAULT_AUDIO_SINK@"

# wpctl --limit takes a normalized float (1.5 = 150%), not a percentage.
CEILING_NORM="$(awk -v p="$CEILING_PCT" 'BEGIN{printf "%.2f", p/100}')"

current_pct() {
    # "Volume: 1.10" or "Volume: 1.10 [MUTED]" -> 110
    wpctl get-volume "$SINK" | awk '{printf "%d", $2*100 + 0.5}'
}

# Show feedback. Noctalia's OSD refuses anything over 100, so the bar pins at
# full there and the true figure goes out as a notification instead — tagged
# synchronous so repeated steps replace the previous popup rather than stack.
show_feedback() {
    local vol="$1" osd="$1"
    [ "$vol" -gt 100 ] && osd=100
    noctalia msg volume-osd "$osd" >/dev/null 2>&1
    if [ "$vol" -gt 100 ]; then
        notify-send -a Volume -u low \
            -h string:x-canonical-private-synchronous:volume \
            "Volume ${vol}%" "Boosted above 100%" >/dev/null 2>&1
    fi
}

set_pct() {
    local vol="$1"
    [ "$vol" -lt 0 ] && vol=0
    [ "$vol" -gt "$CEILING_PCT" ] && vol="$CEILING_PCT"
    wpctl set-volume --limit "$CEILING_NORM" "$SINK" "${vol}%"
    show_feedback "$(current_pct)"
}

case "${1:-}" in
    up)   set_pct "$(( $(current_pct) + STEP_PCT ))" ;;
    down) set_pct "$(( $(current_pct) - STEP_PCT ))" ;;
    max)  set_pct "$CEILING_PCT" ;;      # the boosted maximum
    full) set_pct 100 ;;                 # plain 100%, no boost
    mute)
        wpctl set-mute "$SINK" toggle
        noctalia msg volume-osd "$(current_pct)" >/dev/null 2>&1
        ;;
    set)  set_pct "${2:?usage: volume.sh set <percent>}" ;;
    get)  echo "$(current_pct)%" ;;
    *)
        echo "usage: $(basename "$0") up|down|max|full|mute|set <percent>|get" >&2
        exit 2
        ;;
esac
