-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃                       Keybinds (Lua)                        ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
-- Lua port of keybinds.conf, one bind per original `bindd` line with the same
-- description, so `hyprctl binds` and hyprland-shortcuts.md still line up.

local d   = require("config.defaults")
local dsp = hl.dsp
local M   = d.mainMod

local function bind(keys, action, desc, opts)
    opts = opts or {}
    opts.description = desc
    return hl.bind(keys, action, opts)
end
local function exec(cmd) return dsp.exec_cmd(cmd) end

bind(M .. " + RETURN", exec(d.terminal), "Opens your preferred terminal emulator (" .. d.terminal .. ")")
bind(M .. " + E", exec(d.filemanager), "Opens your preferred filemanager (" .. d.filemanager .. ")")
bind(M .. " + Q", dsp.window.close(), "Closes (not kill) current window")
bind(M .. " + SHIFT + M", exec('loginctl terminate-session "$XDG_SESSION_ID"'), "Ends the current graphical session cleanly")
bind(M .. " + V", dsp.window.float({ action = "toggle" }), "Switches current window between floating and tiling mode")
bind(M .. " + SPACE", exec(d.applauncher), "Runs your application launcher")
bind(M .. " + H", function()
    if hl.plugin.overview and hl.plugin.overview.toggle then
        hl.plugin.overview.toggle()
    end
end, "Toggles the Hyprspace workspace overview")
bind(M .. " + F", dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" }), "Toggles current window fullscreen mode")
bind(M .. " + Y", dsp.window.pin({ action = "toggle" }), "Pin current window (shows on all workspaces)")
bind(M .. " + J", dsp.layout("togglesplit"), "Toggles current window split mode")
bind(M .. " + D", dsp.window.pseudo({ action = "toggle" }), "Toggles pseudo-tiling for the active window")
bind(M .. " + W", exec("noctalia msg panel-toggle wallpaper"), "Opens Noctalia's wallpaper picker panel")
bind(M .. " + SHIFT + W", exec("noctalia msg wallpaper-random"), "Switches to a random wallpaper via Noctalia")
bind("Print", exec(d.shot_region), "Creates a screenshot of an area")
bind("CTRL + Print", exec(d.shot_window), "Creates a screenshot of the active window")
bind("ALT + Print", exec(d.shot_screen), "Creates a screenshot of the active display")

-- ======= Grouping Windows =======
bind(M .. " + K", dsp.group.toggle(), "Toggles  current window group mode (ungroup all related)")
bind(M .. " + Tab", dsp.group.next(), "Switches to the next window in the group")

-- ======= Toggle Gaps =======
-- `hyprctl keyword` is gone in 0.57; set the options directly.
bind(M .. " + SHIFT + G", function()
    hl.config({ general = { gaps_out = { top = 4, right = 0, bottom = 0, left = 0 }, gaps_in = 4 } })
end, "Restore default gaps")
bind(M .. " + G", function()
    hl.config({ general = { gaps_out = 0, gaps_in = 0 } })
end, "Remove gaps between windows")

-- ======= Volume Control =======
-- Volume can go above 100%: scripts/volume.sh drives wpctl (Noctalia clamps at
-- 100%) and caps at its own CEILING_PCT.
local held = { locked = true, repeating = true }
hl.bind("XF86AudioRaiseVolume", exec(d.scripts .. "volume.sh up"), held)
hl.bind("XF86AudioLowerVolume", exec(d.scripts .. "volume.sh down"), held)
hl.bind("XF86AudioMute", exec(d.scripts .. "volume.sh mute"), held)
bind("SHIFT + XF86AudioRaiseVolume", exec(d.scripts .. "volume.sh max"), "Volume straight to the boosted maximum (150%)")
bind("SHIFT + XF86AudioLowerVolume", exec(d.scripts .. "volume.sh full"), "Volume back to a plain 100% (no boost)")

-- ======= Playback Control =======
bind("XF86AudioPlay", exec("playerctl play-pause"), "Toggles play/pause")
bind("XF86AudioNext", exec("playerctl next"), "Next track")
bind("XF86AudioPrev", exec("playerctl previous"), "Previous track")

-- ======= Screen Brightness =======
hl.bind("XF86MonBrightnessUp", exec("brightnessctl s +5%"), held)
hl.bind("XF86MonBrightnessDown", exec("brightnessctl s 5%-"), held)

bind(M .. " + L", exec("hyprlock"), "Lock the screen")
bind(M .. " + O", exec("pkill -x noctalia"), "Reload/restarts Noctalia (respawned by noctalia-watchdog.sh)")
bind(M .. " + B", exec(d.scripts .. "toggle-bar.sh"), "Toggle the top bar (Noctalia) visibility")
bind(M .. " + C", exec("noctalia msg panel-toggle clipboard"), "Opens clipboard history")
bind(M .. " + P", exec("hyprpicker -a"), "Pick a color under the cursor (copies hex)")

-- ======= Window Actions =======
local dirs = { left = "left", right = "right", up = "up", down = "down" }
local dirWords = { left = "to the left", right = "to the right", up = "upwards", down = "downwards" }
for key, dir in pairs(dirs) do
    bind(M .. " + SHIFT + " .. key, dsp.window.move({ direction = dir }), "Move active window " .. dirWords[key])
    bind(M .. " + " .. key, dsp.focus({ direction = dir }), "Move focus " .. dirWords[key])
end

-- Keyboard window resize mode (submap)
local resize = {
    { "right", 15, 0, "Resize to the right" }, { "left", -15, 0, "Resize to the left" },
    { "up", 0, -15, "Resize upwards" },        { "down", 0, 15, "Resize downwards" },
    { "l", 15, 0, "Resize to the right" },     { "h", -15, 0, "Resize to the left" },
    { "k", 0, -15, "Resize upwards" },         { "j", 0, 15, "Resize downwards" },
}
bind(M .. " + R", dsp.submap("resize"), "Activates window resizing mode")
hl.define_submap("resize", function()
    for _, r in ipairs(resize) do
        bind(r[1], dsp.window.resize({ x = r[2], y = r[3], relative = true }), r[4] .. " (resizing mode)")
    end
    bind("escape", dsp.submap("reset"), "Ends window resizing mode")
end)

-- Quick resize; SUPER is added because CTRL + SHIFT selects words in editors
for _, r in ipairs(resize) do
    bind(M .. " + CTRL + SHIFT + " .. r[1], dsp.window.resize({ x = r[2], y = r[3], relative = true }), r[4])
end

-- Resize and drag with SUPER + RMB / LMB
hl.bind(M .. " + mouse:273", dsp.window.resize(), { mouse = true })
hl.bind(M .. " + mouse:272", dsp.window.drag(), { mouse = true })

-- Workspaces are capped at 6 by design: no binds exist for 7 and above.
for i = 1, 6 do
    bind(M .. " + CTRL + " .. i, dsp.window.move({ workspace = i }), "Move window and switch to workspace " .. i)
    bind(M .. " + SHIFT + " .. i, dsp.window.move({ workspace = i, follow = false }), "Move window silently to workspace " .. i)
    bind(M .. " + " .. i, dsp.focus({ workspace = i }), "Switch to workspace " .. i)
end
bind(M .. " + CTRL + left", dsp.window.move({ workspace = "-1" }), "Move window and switch to the previous workspace")
bind(M .. " + CTRL + right", dsp.window.move({ workspace = "+1" }), "Move window and switch to the next workspace")

-- ======= Workspace Actions =======
bind(M .. " + PERIOD", dsp.focus({ workspace = "e+1" }), "Scroll through workspaces incrementally")
bind(M .. " + COMMA", dsp.focus({ workspace = "e-1" }), "Scroll through workspaces decrementally")
bind(M .. " + mouse_down", dsp.focus({ workspace = "e+1" }), "Scroll through workspaces incrementally")
bind(M .. " + mouse_up", dsp.focus({ workspace = "e-1" }), "Scroll through workspaces decrementally")
bind(M .. " + slash", dsp.focus({ workspace = "previous" }), "Switch to the previous workspace")

-- Special workspaces (scratchpads)
bind(M .. " + minus", dsp.window.move({ workspace = "special" }), "Move active window to Special workspace")
bind(M .. " + equal", dsp.workspace.toggle_special("special"), "Toggles the Special workspace")
-- Minimize / restore keep the window in normal tiling (see the scripts)
bind(M .. " + SHIFT + minus", exec(d.scripts .. "minimize.sh"), "Minimize active window (stays hidden until restored)")
bind(M .. " + SHIFT + equal", exec(d.scripts .. "restore.sh"), "Restore minimized window(s) into normal tiling")
bind(M .. " + F1", dsp.workspace.toggle_special("scratchpad"), "Call special workspace scratchpad")
bind(M .. " + ALT + SHIFT + F1", dsp.window.move({ workspace = "special:scratchpad", follow = false }), "Move active window to special workspace scratchpad")
