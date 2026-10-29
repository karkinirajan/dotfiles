-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃                      Autostart (Lua)                        ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
-- Lua port of autostart.conf: session infrastructure only, no user apps.
-- `dbus-update-activation-environment` is not ported: Hyprland exports the
-- environment itself and uwsm does it under systemd. Why each line exists
-- (and why noctalia-watchdog.sh must not be a systemd unit) is written up in
-- autostart.conf.

local d = require("config.defaults")

hl.on("hyprland.start", function()
    hl.exec_cmd("hyprpm reload -n")
    hl.exec_cmd(d.scripts .. "noctalia-watchdog.sh")
    hl.exec_cmd("wl-paste --watch cliphist store")
    hl.exec_cmd("hypridle")
    hl.exec_cmd(d.scripts .. "sync-theme-border.sh")
    hl.exec_cmd(d.scripts .. "theme-border-watch.sh")
end)
