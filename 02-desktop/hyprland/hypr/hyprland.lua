-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃            CachyOS Hyprland Configuration (Lua)             ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
-- Hyprland 0.57 reads only this file; 0.55-0.56 prefer it over hyprland.conf
-- when both exist. The modules live beside the old .conf files in config/
-- (see ../lua-migration.md). `require` paths are relative to this file.

require("config.look")
require("config.autostart")
require("config.keybinds")
require("config.rules")
require("config.plugins")
