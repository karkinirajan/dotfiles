#!/usr/bin/env bash
# Run one Hyprland dispatch in whichever form the active config accepts.
#
# `hyprctl dispatch 'hl.dsp...'` only works when Hyprland loaded a Lua config
# (hyprland.lua). With the tracked hyprland.conf (hyprlang, Hyprland 0.56.x) it
# answers "Invalid dispatcher", and the legacy names (dpms, movecursor,
# movetoworkspacesilent) are the ones that work. This helper tries the Lua form
# first and then the legacy form, so the same script runs before and after the
# Lua migration (see ../../lua-migration.md).
#
# Usage: hypr-dispatch.sh '<lua form>' '<legacy form>'
set -uo pipefail

if (($# != 2)); then
    echo "usage: ${0##*/} '<lua form>' '<legacy form>'" >&2
    exit 2
fi

lua_form=$1
legacy_form=$2

reply=$(hyprctl dispatch "$lua_form" 2>&1) || true
if [[ "$reply" == ok* ]]; then
    exit 0
fi

reply=$(hyprctl dispatch "$legacy_form" 2>&1) || true
if [[ "$reply" == ok* ]]; then
    exit 0
fi

echo "${0##*/}: neither form was accepted (last reply: ${reply:-none})" >&2
exit 1
