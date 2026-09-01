#!/bin/bash
# Watches Noctalia's live settings.toml for theme changes (source, palette
# selection, mode) and re-syncs Hyprland's window border color whenever it
# changes, so the two stay in lockstep without manual intervention.
#
# Watches the containing DIRECTORY, not the file directly: Noctalia (like
# most config writers, and like `sed -i`) saves via write-temp + atomic
# rename-over, which replaces the file's inode. A watch on the file path
# itself silently dies the first time that happens; a directory watch
# filtered to the filename survives every rename.

SETTINGS="$HOME/.local/state/noctalia/settings.toml"
SETTINGS_DIR="$(dirname "$SETTINGS")"
SETTINGS_NAME="$(basename "$SETTINGS")"
SYNC="$HOME/.config/hypr/scripts/sync-theme-border.sh"

get_theme_block() {
    awk '/^\[theme\]/{f=1;next} /^\[/{f=0} f' "$SETTINGS" 2>/dev/null
}

last_theme="$(get_theme_block)"

inotifywait -q -m -e close_write,moved_to,create "$SETTINGS_DIR" |
while read -r _dir _events name; do
    [ "$name" = "$SETTINGS_NAME" ] || continue
    current_theme="$(get_theme_block)"
    if [ "$current_theme" != "$last_theme" ]; then
        last_theme="$current_theme"
        "$SYNC"
    fi
done
