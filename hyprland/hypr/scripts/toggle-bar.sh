#!/bin/bash
# noctalia bar-toggle only hides the icons and keeps the layer surface's blur
# decoration rendering over its full reserved geometry, leaving a visible
# frosted strip where the bar used to be. bar-hide releases the reserved
# space, but the blur artifact still shows unless blur is also switched off
# for that surface while it's hidden.

STATE_FILE="/tmp/noctalia-bar-hidden"

if [ -f "$STATE_FILE" ]; then
    noctalia msg bar-show
    hyprctl keyword layerrule "blur on, match:namespace noctalia-bar-default"
    hyprctl keyword layerrule "xray on, match:namespace noctalia-bar-default"
    rm -f "$STATE_FILE"
else
    noctalia msg bar-hide
    hyprctl keyword layerrule "blur off, match:namespace noctalia-bar-default"
    touch "$STATE_FILE"
fi
