-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃       Monitor, environment, input, look and feel (Lua)      ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
-- Lua port of monitor.conf, environment.conf, input.conf, variables.conf,
-- decorations.conf and animations.conf. Comments explaining each choice stay
-- in the .conf files, which Hyprland 0.56.x still reads when no hyprland.lua
-- is linked.

local colors = require("config.colors")

-- MSI MAG 275QF: its EDID marks 60 Hz as preferred, so pin the native mode.
hl.monitor({ output = "DP-2", mode = "2560x1440@180", position = "auto", scale = 1 })

-- The third argument exports the variable to D-Bus too (the old `envd`).
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")
hl.env("HYPRCURSOR_THEME", "Bibata-Modern-Ice", true)
hl.env("HYPRCURSOR_SIZE", "24", true)
hl.env("XCURSOR_THEME", "Bibata-Modern-Ice", true)
hl.env("XCURSOR_SIZE", "24", true)
hl.env("QT_CURSOR_SIZE", "24", true)
hl.env("COLORTERM", "truecolor", true)
hl.env("GTK_THEME", "catppuccin-mocha-blue-standard+default", true)
hl.env("TERMINAL", "alacritty", true)

hl.config({
    input = {
        follow_mouse = 2,
        float_switch_override_focus = 2,
    },

    general = {
        gaps_in = 4,
        -- top, right, bottom, left: only the gap under the top bar survives
        gaps_out = { top = 4, right = 0, bottom = 0, left = 0 },
        border_size = 2,
        col = {
            active_border   = colors.active_border,
            inactive_border = colors.inactive_border,
        },
        layout = "dwindle",
        snap = { enabled = true },
    },

    group = {
        col = {
            border_active          = colors.blue,
            border_inactive        = colors.surface1,
            border_locked_active   = colors.sapphire,
            border_locked_inactive = colors.surface2,
        },
        groupbar = {
            font_family = "DejaVu Sans",
            text_color  = colors.crust,
            col = {
                active          = colors.blue,
                inactive        = colors.surface1,
                locked_active   = colors.sapphire,
                locked_inactive = colors.surface2,
            },
        },
    },

    misc = {
        font_family           = "DejaVu Sans",
        splash_font_family    = "DejaVu Sans",
        disable_hyprland_logo = true,
        col = { splash = colors.blue },
        background_color      = colors.base,
        enable_swallow        = true,
        swallow_regex         = "^(nautilus|nemo|thunar|btrfs-assistant.)$",
        focus_on_activate     = true,
        vrr                   = 2,
    },

    -- cm_auto_hdr = 0: with the default (1) every fullscreen client that signals
    -- HDR/wide-gamut (Brave video) forces an HDR modeset on DP-2, which blanks
    -- the screen while the DisplayPort link retrains.
    render = { direct_scanout = true, cm_auto_hdr = 0 },

    dwindle = { special_scale_factor = 0.8, preserve_split = true },
    master  = { new_status = "master", special_scale_factor = 0.8 },

    decoration = {
        active_opacity   = 1,
        inactive_opacity = 1,
        rounding         = 2,
        blur   = { size = 15, passes = 2, xray = true },
        shadow = { enabled = false },
    },

    binds = {
        allow_workspace_cycles            = true,
        workspace_back_and_forth          = 1,
        workspace_center_on               = 1,
        movefocus_cycles_fullscreen       = true,
        window_direction_monitor_fallback = true,
    },

    animations = { enabled = true },

    -- Full compositor logging, kept across upgrades so session exits are captured
    debug = { disable_logs = false },
})

-- Gestures: 4-finger horizontal switches workspaces; 3-finger down closes,
-- up toggles fullscreen, left toggles float/tile.
hl.gesture({ fingers = 4, direction = "horizontal", action = "workspace" })
hl.gesture({ fingers = 3, direction = "down",       action = "close" })
hl.gesture({ fingers = 3, direction = "up",         action = "fullscreen" })
hl.gesture({ fingers = 3, direction = "left",       action = "float" })

hl.curve("overshot", { type = "bezier", points = { { 0.13, 0.99 }, { 0.29, 1.1 } } })
hl.animation({ leaf = "windowsIn",     enabled = true, speed = 4, bezier = "overshot", style = "slide" })
hl.animation({ leaf = "windowsOut",    enabled = true, speed = 5, bezier = "default",  style = "popin 80%" })
hl.animation({ leaf = "border",        enabled = true, speed = 5, bezier = "default" })
hl.animation({ leaf = "workspacesIn",  enabled = true, speed = 6, bezier = "overshot", style = "slide" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 6, bezier = "overshot", style = "slidefade 80%" })
