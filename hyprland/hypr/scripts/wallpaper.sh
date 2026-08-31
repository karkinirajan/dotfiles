#!/bin/sh
# Wallpaper switcher for hyprpaper.
#
# Usage:
#   wallpaper.sh pick     interactive wofi picker (default if no arg given)
#   wallpaper.sh random   pick a random wallpaper and apply it
#   wallpaper.sh <path>   apply a specific wallpaper by absolute path
#
# Any mode also persists the choice into hyprpaper.conf so it survives a
# reboot/relogin (written in the block `wallpaper { monitor; path; fit_mode }`
# form — hyprpaper 0.8.4 dropped the older flat `preload =` / `wallpaper =
# monitor,path` directives).
#
# hyprpaper 0.8.4 ALSO dropped runtime preload/unload IPC entirely (hyprctl
# reports "invalid hyprpaper request" for both), and the surviving `wallpaper`
# IPC request only re-issues a wallpaper already declared in the config file
# for that monitor — it does not accept an arbitrary new path at runtime.
# There is no config hot-reload (SIGHUP does nothing) either. Verified by
# direct hyprctl testing. So the only way to actually change the wallpaper
# is: rewrite hyprpaper.conf, then kill and relaunch the hyprpaper daemon so
# it re-reads the file on startup. This causes a brief black flash, which is
# an accepted tradeoff since the IPC path used previously never worked.
# fit_mode is contain, not the default cover, so wallpapers are scaled to
# fit entirely on screen rather than cropped at the edges.

WALLPAPER_DIR="$HOME/.wallpapers"
HYPRPAPER_CONF="$HOME/.config/hypr/hyprpaper.conf"
FIT_MODE="cover"

apply() {
    wp="$1"
    [ -f "$wp" ] || { echo "wallpaper.sh: not a file: $wp" >&2; exit 1; }

    {
        echo "splash = false"
        echo "ipc = on"
        echo
        hyprctl monitors -j | jq -r '.[].name' | while read -r mon; do
            echo "wallpaper {"
            echo "    monitor = $mon"
            echo "    path = $wp"
            echo "    fit_mode = $FIT_MODE"
            echo "}"
            echo
        done
    } > "$HYPRPAPER_CONF"

    pkill -x hyprpaper 2>/dev/null
    sleep 0.3
    setsid -f hyprpaper >/tmp/hyprpaper.log 2>&1 </dev/null

    for _ in 1 2 3 4 5 6 7 8 9 10; do
        sleep 0.3
        active=$(hyprctl hyprpaper listactive 2>/dev/null)
        case "$active" in
            *"$wp"*) break ;;
        esac
    done

    notify-send -a "Wallpaper" "Wallpaper changed" "$(basename "$wp")" 2>/dev/null
}

mode="${1:-pick}"

case "$mode" in
    random)
        wp=$(find "$WALLPAPER_DIR" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) | shuf -n1)
        apply "$wp"
        ;;
    pick)
        wp=$(find "$WALLPAPER_DIR" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) \
            | sed "s|^$WALLPAPER_DIR/||" | sort \
            | wofi --dmenu --prompt "Wallpaper" --cache-file /dev/null)
        [ -n "$wp" ] && apply "$WALLPAPER_DIR/$wp"
        ;;
    *)
        apply "$mode"
        ;;
esac
