-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃              Colors Configuration: Shades of Jade            ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
-- Lua twin of colors.conf (Hyprland 0.57+ reads only Lua). Palette source:
-- https://github.com/HANCORE-linux/omarchy-shadesofjade-theme
-- Same Catppuccin-shaped role names as colors.conf, recolored to Shades of
-- Jade. scripts/sync-theme-border.sh rewrites the mauve, lavender and blue_dim
-- lines of both files, so keep each on its own line in this form.

local c = {}

c.rosewater = "rgba(FFF7F2ff)"
c.flamingo  = "rgba(FFF7F2ff)"
c.pink      = "rgba(E25F4Bff)"
c.mauve     = "rgba(e95678ff)"
c.red       = "rgba(ff3370ff)"
c.maroon    = "rgba(ff3370ff)"
c.peach     = "rgba(FF6600ff)"
c.yellow    = "rgba(D1FFb0ff)"
c.green     = "rgba(00a86bff)"
c.teal      = "rgba(80d4b5ff)"
c.sky       = "rgba(80d4b5ff)"
c.sapphire  = "rgba(00a86bff)"
c.blue      = "rgba(00a86bff)"
c.lavender  = "rgba(fab795ff)"

c.text      = "rgba(e6f6f0ff)"
c.subtext1  = "rgba(c4d4ceff)"
c.subtext0  = "rgba(a1b1abff)"
c.overlay2  = "rgba(7e8f89ff)"
c.overlay1  = "rgba(61716bff)"
c.overlay0  = "rgba(4a5a54ff)"
c.surface2  = "rgba(466d58ff)"
c.surface1  = "rgba(2b4c3bff)"
c.surface0  = "rgba(1c372aff)"
c.base      = "rgba(00110bff)"
c.mantle    = "rgba(000806ff)"
c.crust     = "rgba(000000ff)"

-- Dimmed accent for floating-window borders (same accent, low alpha)
c.blue_dim  = "rgba(e9567826)"

-- Primary accent used everywhere: active workspace, active border, power button
c.ctp_accent = c.mauve

-- Window border gradients: the accent pair at full (ee) and dimmed (aa) alpha.
local function alpha(rgba, a)
    return (rgba:gsub("%x%x%)$", a .. ")"))
end
c.active_border   = { colors = { alpha(c.mauve, "ee"), alpha(c.lavender, "ee") }, angle = 45 }
c.inactive_border = { colors = { alpha(c.mauve, "aa"), alpha(c.lavender, "aa") }, angle = 45 }

return c
