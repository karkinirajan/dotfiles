-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃           Window, workspace and layer rules (Lua)           ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
-- Lua port of windowrules.conf. The layer rules for logout_dialog, waybar,
-- wallpaper and wofi are not ported: those programs are retired.

local colors = require("config.colors")

local function rule(match, effects)
    effects.match = match
    return hl.window_rule(effects)
end

-- Float necessary windows
for _, m in ipairs({
    { class = "^(org.pulseaudio.pavucontrol)" },
    { class = "^()$", title = "^(Picture in picture)$" },
    { class = "^()$", title = "^(Save File)$" },
    { class = "^()$", title = "^(Open File)$" },
    { class = "^(LibreWolf)$", title = "^(Picture-in-Picture)$" },
    { class = "^(blueman-manager)$" },
    { class = "^(xdg-desktop-portal-gtk|xdg-desktop-portal-kde|xdg-desktop-portal-hyprland)(.*)$" },
    { class = "^(polkit-gnome-authentication-agent-1|hyprpolkitagent|org.kde.polkit-kde-authentication-agent-1)(.*)$" },
    { class = "^(CachyOSHello)$" },
    { class = "^(zenity)$" },
    { class = "^()$", title = "^(Steam - Self Updater)$" },
}) do
    rule(m, { float = true })
end

-- Opacity
rule({ class = "^(thunar|nemo)$" }, { opacity = "0.92" })
rule({ class = "^(discord|armcord|webcord)$" }, { opacity = "0.96" })
rule({ title = "^(QQ|Telegram)$" }, { opacity = "0.95" })
rule({ title = "^(NetEase Cloud Music Gtk4)$" }, { opacity = "0.95" })

-- Floating media and helper windows: 960x540, a quarter in from the top left.
-- The hyprlang form was `move 25%- 25%-`; Lua takes monitor expressions.
local quarter = "(monitor_w*0.25) (monitor_h*0.25)"
rule({ title = "^(Picture-in-Picture)$" }, { float = true, size = "960 540", move = quarter })
rule({ title = "^(imv|mpv|danmufloat|termfloat|nemo|ncmpcpp)$" }, { float = true, size = "960 540", move = quarter })
rule({ title = "^(danmufloat)$" }, { pin = true })
rule({ title = "^(danmufloat|termfloat)$" }, { rounding = 5 })
rule({ class = "^(kitty|Alacritty)$" }, { animation = "slide right" })
rule({ class = "^(org.mozilla.firefox)$" }, { no_blur = true })

-- Floating windows on workspaces 1 to 10
rule({ float = true, workspace = "w[fv1-10]" }, { border_size = 2, border_color = colors.blue_dim, rounding = 8 })
-- Tiled windows on workspaces 1 to 10
rule({ float = false, workspace = "f[1-10]" }, { border_size = 2, rounding = 2 })

-- Smart gaps: keep the top-bar gap when a workspace holds a single window
hl.workspace_rule({ workspace = "w[t1]", gaps_out = { top = 4, right = 0, bottom = 0, left = 0 }, gaps_in = 4 })
hl.workspace_rule({ workspace = "f[1]",  gaps_out = { top = 4, right = 0, bottom = 0, left = 0 }, gaps_in = 4 })

-- Noctalia bar/panels are translucent, so blur shows through (frosted glass).
-- The bar rules are named and kept in a global so scripts/toggle-bar.sh can
-- switch them off while the bar is hidden (`hyprctl eval`).
noctalia_bar_rules = {}
for _, ns in ipairs({ "noctalia-bar-kneeraazon", "noctalia-bar-default" }) do
    table.insert(noctalia_bar_rules, hl.layer_rule({ name = "blur-" .. ns, match = { namespace = ns }, blur = true, xray = true }))
end
hl.layer_rule({ match = { namespace = "noctalia-attached-panel" }, blur = true, xray = true })
