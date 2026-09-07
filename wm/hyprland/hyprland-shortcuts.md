# Hyprland Keyboard Shortcuts Cheat Sheet

Generated from your actual config at `~/.config/hypr/config/keybinds.conf`.
`SUPER` = the Windows/Cmd key (set as `$mainMod` in `~/.config/hypr/hyprland.conf`).

## Apps & Core

| Shortcut | Action |
|---|---|
| `SUPER + Return` | Open terminal (kitty) |
| `SUPER + E` | Open file manager (kitty + yazi) |
| `SUPER + Space` | Open app launcher (Noctalia) — moves the cursor off the bar first, so a hover-triggered panel can't steal focus and close it instantly |
| `SUPER + Q` | Close current window (graceful) |
| `SUPER + SHIFT + M` | Log out / end session |
| `SUPER + L` | Lock screen |
| `SUPER + O` | Reload/restart Noctalia shell |
| `SUPER + B` | Toggle the top bar visibility (also drops its blur decoration, so no ghost strip is left behind) |
| `SUPER + C` | Clipboard history (Noctalia) |
| `SUPER + P` | Color picker (copies hex) |
| `SUPER + W` | Open the WallRizz wallpaper/theme picker |
| `SUPER + SHIFT + W` | Switch to a random wallpaper via WallRizz |

## Plugins (hyprpm)

| Shortcut | Action |
|---|---|
| `SUPER + H` | Toggle the Hyprspace workspace overview (GNOME/macOS Mission Control-style) |

Also installed and loaded, but with no dedicated keybind by design:
- **hy3** — i3/sway-style manual tiling layout, available as an alternative to the active `dwindle` layout. Not switched on by default (would change how every window tiles); set `general:layout = hy3` in `variables.conf` to try it.
- **split-monitor-workspaces** — per-monitor independent workspace numbering. Loaded but not wired into the workspace keybinds below, since that would mean rewriting all of them.
- **dynamic-cursors** — cursor tilts with movement, shake-to-find (mouse-driven, no keybind needed).
- **hyprfocus** — flash animation on keyboard-driven focus changes (automatic, no keybind).
- **borders-plus-plus** — extra static outer border accent (visual only, no keybind).

## Screenshots

| Shortcut | Action |
|---|---|
| `Print` | Screenshot a selected area |
| `Ctrl + Print` | Screenshot the active window |
| `Alt + Print` | Screenshot the whole screen |

## Window State

| Shortcut | Action |
|---|---|
| `SUPER + V` | Toggle floating ↔ tiling |
| `SUPER + F` | Toggle fullscreen |
| `SUPER + D` | Toggle pseudo-tiling |
| `SUPER + Y` | Pin window (shows on all workspaces) |
| `SUPER + J` | Toggle split direction (dwindle layout) |
| `SUPER + K` | Toggle window grouping (tab group) |
| `SUPER + Tab` | Cycle to next window in the group |

## Moving Focus / Windows

| Shortcut | Action |
|---|---|
| `SUPER + ←/→/↑/↓` | Move focus in that direction |
| `SUPER + SHIFT + ←/→/↑/↓` | Move the active window in that direction |
| `SUPER + Left-click` + drag | Move window with mouse |

## Resizing Windows

| Shortcut | Action |
|---|---|
| `SUPER + R`, then `←/→/↑/↓` or `h/j/k/l`, `Esc` to exit | Resize mode — tap repeatedly to grow/shrink 15px per press, no need to hold the mod key while in this mode |
| `SUPER + Ctrl + Shift + ←/→/↑/↓` (or `h/j/k/l`) | One-shot resize, 15px per press, no mode needed |
| `SUPER + Right-click` + drag | Freeform resize with mouse |

> Resize mode (`SUPER + R`) is the fastest way to fine-tune a window: hit it once, then just tap arrow keys/hjkl repeatedly, then `Esc` when done — you don't need to re-press `SUPER` each time.

## Gaps

| Shortcut | Action |
|---|---|
| `SUPER + G` | Remove gaps between windows |
| `SUPER + SHIFT + G` | Restore default CachyOS gaps |

## Workspaces

| Shortcut | Action |
|---|---|
| `SUPER + [1-9, 0]` | Switch to workspace 1–10 |
| `SUPER + Ctrl + [1-9, 0]` | Move active window to workspace N **and follow it** |
| `SUPER + Shift + [1-9, 0]` | Move active window to workspace N **silently** (you stay put) |
| `SUPER + Ctrl + ←/→` | Move window to next/previous workspace and follow |
| `SUPER + . ` (period) | Scroll to next workspace |
| `SUPER + ,` (comma) | Scroll to previous workspace |
| `SUPER + scroll wheel` | Scroll through workspaces |
| `SUPER + /` (slash) | Jump to previous (last-used) workspace |

## Special Workspace (Scratchpad)

| Shortcut | Action |
|---|---|
| `SUPER + -` (minus) | Move active window to the special workspace |
| `SUPER + =` (equals) | Toggle the special workspace visible |
| `SUPER + F1` | Toggle the "scratchpad" special workspace |
| `SUPER + Alt + Shift + F1` | Move active window to scratchpad silently |
| `SUPER + SHIFT + -` (minus) | Minimize active window (stays hidden until restored) |
| `SUPER + SHIFT + =` (equals) | Restore minimized window(s) into normal tiling |

## Media Keys (hardware keys, no SUPER needed)

| Key | Action |
|---|---|
| Volume Up/Down | Adjust volume ±5%, and it keeps going past 100% up to 150% |
| SHIFT + Volume Up | Jump straight to the boosted maximum (150%) |
| SHIFT + Volume Down | Drop back to a plain 100%, no boost |
| Mute | Toggle mute |
| Play/Pause, Next, Prev | Media playback control |
| Brightness Up/Down | Adjust screen brightness ±5% |

---

### Quick tips
- Full reference: `~/.config/hypr/config/keybinds.conf` (every bind has a `bindd` description — run `hyprctl binds` in a terminal to list them all live, including descriptions).
- If a shortcut ever doesn't fire, check `bindd = $mainMod ..., description, dispatcher, args` syntax — the 3rd field is the human description, 4th is the actual dispatcher. Also check for a duplicate bind on the same key (`hyprctl binds -j` shows exactly what's actually registered) — a later `bindd` on the same key silently wins over an earlier one.
- `workspace_back_and_forth = 1` is on, so pressing the same workspace number twice toggles back to the previous one.
- Noctalia (bar, launcher, clipboard, control center) replaced Waybar/wofi/mako entirely — none of the shortcuts above launch those anymore, even though some dispatcher names still say things like "wofi" in older comments.
