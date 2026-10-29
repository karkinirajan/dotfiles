-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃                     Defaults Configuration                  ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
-- Lua twin of defaults.conf. Alacritty is the default terminal; kitty stays
-- installed and configured (swap terminal back to return to it). TERMINAL in
-- environment.lua must stay in step with this.

local scripts = os.getenv("HOME") .. "/.config/hypr/scripts/"

return {
    mainMod     = "SUPER",
    terminal    = "alacritty",
    filemanager = "alacritty -e yazi",
    applauncher = scripts .. "launcher-open.sh",
    scripts     = scripts,

    -- grim + slurp capture, swash annotation (see scripts/screenshot.sh)
    shot_region = scripts .. "screenshot.sh region",
    shot_window = scripts .. "screenshot.sh window",
    shot_screen = scripts .. "screenshot.sh screen",
}
