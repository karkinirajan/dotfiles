-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃               Hyprpm-managed plugins (Lua)                  ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
-- Lua port of plugins.conf. hyprpm loads the plugins (autostart.lua); each
-- block only applies once its plugin is loaded, so it is guarded.

-- Hyprspace workspace overview (ImanolBarba fork). It does not build against
-- Hyprland 0.57.0 yet, so on 0.57 this block is skipped until it does.
if hl.plugin.overview then
    hl.config({ plugin = { overview = {
        panelColor                  = "rgba(00110bee)",
        panelBorderColor            = "rgba(00a86bee)",
        workspaceActiveBackground   = "rgba(00a86b33)",
        workspaceInactiveBackground = "rgba(1c372a99)",
        workspaceActiveBorder       = "rgba(00a86bff)",
        workspaceInactiveBorder     = "rgba(3E665088)",
        workspaceBorderSize         = 2,
        panelHeight                 = 200,
        panelBorderWidth            = 2,
        centerAligned               = true,
        workspaceMargin             = 12,
        -- mirror the real gaps so thumbnails preview the actual layout
        overrideGaps                = true,
        gapsIn                      = 4,
        gapsOut                     = 1,
    } } })
end

-- dynamic-cursors: tilt in the direction of movement, shake to find
if hl.plugin.dynamic_cursors then
    hl.config({ plugin = { dynamic_cursors = {
        enabled = true,
        mode    = "tilt",
        shake   = {
            enabled   = true,
            effects   = true,
            threshold = 5.5,
            base      = 3.5,
            speed     = 4,
            limit     = 6,
            timeout   = 1500,
        },
    } } })
end
