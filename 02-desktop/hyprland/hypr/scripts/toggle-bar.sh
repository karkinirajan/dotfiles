#!/bin/bash
# noctalia bar-toggle only hides the icons and keeps the layer surface's blur
# decoration rendering over its full reserved geometry, leaving a visible
# frosted strip where the bar used to be. bar-hide releases the reserved
# space, but the blur artifact still shows unless blur is also switched off
# for that surface while it's hidden.

STATE_FILE="/tmp/noctalia-bar-hidden"

# Lua config (Hyprland 0.57+): rules.lua keeps the bar's blur rules in the
# global noctalia_bar_rules. hyprlang (0.56.x): add rules with `keyword`.
bar_blur() {
    local enabled=true
    [ "$1" = off ] && enabled=false
    if [ "$(hyprctl eval "for _, r in ipairs(noctalia_bar_rules or {}) do r:set_enabled($enabled) end" 2>&1)" = ok ]; then
        return
    fi
    for ns in noctalia-bar-kneeraazon noctalia-bar-default; do
        hyprctl keyword layerrule "blur $1, match:namespace $ns"
        [ "$1" = on ] && hyprctl keyword layerrule "xray on, match:namespace $ns"
    done
}

if [ -f "$STATE_FILE" ]; then
    noctalia msg bar-show
    bar_blur on
    rm -f "$STATE_FILE"
else
    noctalia msg bar-hide
    bar_blur off
    touch "$STATE_FILE"
fi
