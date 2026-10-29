---
title: Hyprland Lua config migration
part: "02"
chapter: "01"
topic: hyprland-lua-migration
versions: [hyprland]
last_verified: 2026-10-29
status: current
sources:
  - https://hypr.land/news/26_lua/
  - https://wiki.hypr.land/
  - https://github.com/hyprwm/Hyprland/releases/tag/v0.57.0
---

# Hyprland Lua config migration

## Purpose

Hyprland 0.57.0 (Arch `extra`, 2026-10-28) removed the hyprlang parser: only `~/.config/hypr/hyprland.lua` loads. The machine runs <!-- v:hyprland -->0.57.0<!-- /v --> on the Lua port since 2026-10-29; the hyprlang tree (`hyprland.conf` plus `config/*.conf`) is kept only for 0.56.x. This page records the mapping. **The port:** [`hypr/hyprland.lua`](hypr/hyprland.lua) requires the modules `config/look.lua`, `config/autostart.lua`, `config/keybinds.lua`, `config/rules.lua`, `config/plugins.lua`, `config/colors.lua` and `config/defaults.lua`, and `manifest.conf` links it to `~/.config/hypr/hyprland.lua`. The `.conf` tree stays for 0.56.x. Checked on 2026-10-29: `Hyprland --verify-config` prints `config ok` on 0.56.2 and on the 0.57.0 binary from Arch `extra` (signature verified), and a nested 0.57.0 compositor loaded it with no `configerrors` and the same 94 key, modifier, submap and flag combinations as the live 0.56.2 session. In the live 0.57.0 login after the upgrade: `configerrors` empty, 94 binds, gaps and border gradient as configured, the autostart processes running, the bar rule toggle answering `ok`. Hyprspace fails to build on 0.57.0, and while its repo is present `hyprpm update` stops before rebuilding dynamic-cursors; remove the Hyprspace repo (`hyprpm remove Hyprspace`) to get dynamic-cursors back. Still to try by hand: hypridle DPMS, minimize and restore, the launcher position.

## Prerequisites

- Hyprland 0.55 or newer for Lua support. On 0.56.2 a `hyprland.lua` wins over `hyprland.conf` when both exist, so you can test the port without removing the `.conf` tree.
- A TTY or SSH session to recover from, in case the Lua config fails to load.
- Time line from the project: Lua optional in 0.55, hyprlang deprecated for "1 to 2 releases", removed in 0.57. `hypridle.conf`, `hyprlock.conf` and `hyprsunset` keep hyprlang for now.

## Steps

1. Stay on 0.56.2. Add `IgnorePkg = hyprland hyprpm` to `/etc/pacman.conf`. Label: `machine-only`.
2. Write `~/.config/hypr/hyprland.lua` and split it with `require("config.keybinds")`, relative to the file or absolute, wildcards allowed. Keep the file in the repo under `02-desktop/hyprland/hypr/` and link it in `manifest.conf` only after step 4 passes.
3. Reload and check: `hyprctl reload`, `hyprctl configerrors`, `hyprctl binds`. `hyprctl eval '<lua>'` runs a snippet and `hyprctl repl` opens an interactive session.
4. Test every behavior that touches a dispatcher: hypridle DPMS, minimize and restore, launcher open, the gaps toggles, the bar toggle, the overview plugin.
5. Rebuild plugins for the version you run (`hyprpm update`, then enable). `dynamic-cursors` at its newest commit configures through Lua (`hl.config { plugin = { dynamic_cursors = ... } }` inside `if hl.plugin.dynamic_cursors then`); Hyprspace configures through `hl.config({ plugin = { overview = {...} } })` and toggles with `hl.plugin.overview.toggle()`. Hyprspace does not compile on 0.57.0 (see the README).
6. Only then remove the `IgnorePkg` line and update to 0.57.

The port was written by hand from the v0.57.0 Lua bindings source (`src/config/lua/bindings/`), not with the third-party `hyprconf2lua` converter.

## Mapping from the tracked hyprlang files

Verified against the wiki sources and the v0.57.0 Lua bindings.

| hyprlang (today) | Lua |
|---|---|
| `source = ~/.config/hypr/config/x.conf` | `require("config.x")` |
| `general { gaps_in = 4 }` | `hl.config({ general = { gaps_in = 4 } })` or `hl.config({ ["general.gaps_in"] = 4 })`; Int options accept booleans |
| `monitor = DP-2, 2560x1440@180, auto, 1` | `hl.monitor({ output = "DP-2", mode = "2560x1440@180", position = "auto", scale = 1 })` |
| `envd = XCURSOR_SIZE,24` (the `d` exports to D-Bus) | `hl.env("XCURSOR_SIZE", "24", true)` (the third argument replaces the `d`) |
| `exec-once = cmd` | `hl.on("hyprland.start", function() hl.exec_cmd("cmd") end)` |
| `bindd = SUPER, Q, Close window, killactive` | `hl.bind("SUPER + Q", hl.dsp.window.close(), { description = "Close window" })` |
| `bindel = , XF86AudioRaiseVolume, exec, ...` | flags `repeating` and `locked` |
| `bindr` (on release) | flag `release` |
| `bindm = $mainMod, mouse:273, resizewindow` | flag `mouse` with `hl.dsp.window.resize()`; moving uses `hl.dsp.window.drag()` |
| `windowrule = float on, match:class ^(x)$` | `hl.window_rule({ match = { class = "^(x)$" }, float = true })` |
| `layerrule = blur on, match:namespace n` | `hl.layer_rule({ match = { namespace = "n" }, blur = true })` |
| a smart-gaps `workspace = w[t1], ...` rule | `hl.workspace_rule({ workspace = "w[t1]", gaps_in = ... })` |
| `bezier = overshot, 0.13, 0.99, 0.29, 1.1` | `hl.curve("overshot", { type = "bezier", points = { {0.13, 0.99}, {0.29, 1.1} } })` |
| `animation = windowsIn, 1, 4, overshot, slide` | `hl.animation({ leaf = "windowsIn", enabled = true, speed = 4, bezier = "overshot", style = "slide" })` |
| `plugin:overview:...` keywords | `hl.config({ plugin = { overview = { ... } } })` |

Bind flags available: `locked release click drag long_press repeating non_consuming auto_consuming mouse transparent ignore_mods description dont_inhibit submap_universal device allow_input_capture`. A dispatcher function called from a Lua function must be wrapped in `hl.dispatch(...)`. Named rules return handles with `set_enabled()`. All 45 option names the tracked tree uses exist unchanged in 0.57.0.

## Scripts and binds to change in the port

| Where | Today | After |
|---|---|---|
| `hypridle.conf`, `minimize.sh`, `restore.sh`, `launcher-open.sh` | via `scripts/hypr-dispatch.sh` (Lua form, then legacy form) | unchanged; the Lua form is accepted first |
| `keybinds.conf:15` | `hyprctl dispatch overview:toggle` | done: a Lua function bind calling `hl.plugin.overview.toggle()` when the plugin is loaded |
| `keybinds.conf:34-35` | `hyprctl --batch "keyword general:gaps_out ..."` | done: Lua function binds calling `hl.config(...)`; `hyprctl keyword` is not registered in 0.57 |
| `scripts/toggle-bar.sh` | `hyprctl keyword layerrule ...` | done: `rules.lua` keeps the bar rules in the global `noctalia_bar_rules`, and the script runs `hyprctl eval '... r:set_enabled(false) ...'` (answered `ok` on nested 0.57.0), falling back to `keyword` on hyprlang |
| `scripts/noctalia-restore.sh:94` | `hyprctl dispatch exec "$WATCHDOG"` | done: goes through `hypr-dispatch.sh` with `hl.dsp.exec_cmd(...)` first |
| `scripts/sync-theme-border.sh` | rewrites `colors.conf` and `variables.conf`, then `hyprctl reload` | done: also rewrites the `mauve`, `lavender` and `blue_dim` lines of `colors.lua`, from which the border gradients are derived |
| `config/windowrules.conf:27,29` | `move 25%- 25%-` | done: `move = "(monitor_w*0.25) (monitor_h*0.25)"`, accepted by `--verify-config` on 0.57.0 |
| `config/autostart.conf` | `dbus-update-activation-environment` exec-once | drop it: Hyprland does this itself and uwsm does it under systemd |
| `hyprland-shortcuts.md` | "Quick tips" describe `bindd` field order and `hyprctl binds -j` | rewrite after the port |

Layer rules for logout_dialog, waybar, wallpaper and wofi are dead (those programs are retired); Noctalia ships one upstream layer rule that covers all of its namespaces.

## Verify

`hyprctl version` reports the version you run, `hyprctl configerrors` prints nothing, and `ls ~/.config/hypr/hyprland.lua` exists. On 0.57 with only a `.conf` present, Hyprland generates a default `hyprland.lua` instead of loading the old files. Dispatch check: `hyprctl dispatch 'hl.dsp.cursor.move({ x = 100, y = 100 })'` prints `ok` under Lua and `Invalid dispatcher` under the legacy config.

## Sources

- [Hyprland news: moving to Lua](https://hypr.land/news/26_lua/) and the 0.57.0 release post
- [Hyprland wiki](https://wiki.hypr.land/) (versioned; lowercase paths)
- Ledger: cluster C2, topics `hyprland`, `hyprpm`, `hypr-ecosystem-packages` in [`LEDGER.csv`](../../docs/modernization/LEDGER.csv)
