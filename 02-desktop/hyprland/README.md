# Hyprland + Noctalia

CachyOS/Arch Wayland desktop: Hyprland compositor with Noctalia as the shell
(bar, launcher, clipboard history, control center) — replaces Waybar/wofi/mako.

The manifest installs `hyprland-shortcuts.md` at `~/hyprland-shortcuts.md`.
Hyprland scripts use the Lua dispatcher API in Hyprland 0.55 and newer; check
the installed version before copying them to older releases.

```
hyprland/
├── hyprland-shortcuts.md          → ~/hyprland-shortcuts.md
│                                  # Full keybind cheat sheet, regenerated from the
│                                  #   actual keybinds.conf below whenever it drifts —
│                                  #   don't hand-edit it out of sync with that file.
├── KDE-REMOVAL.md                 # How the full KDE/Plasma desktop environment
│                                  #   was removed from this originally dual-DE
│                                  #   CachyOS install — landmines hit (a hard
│                                  #   Dolphin dependency, an active login manager),
│                                  #   the SDDM switchover, and why a blind orphan
│                                  #   sweep at the end would have broken things
│                                  #   this setup actually depends on. Read before
│                                  #   ever running `pacman -Rns $(pacman -Qtdq)`
│                                  #   on this machine.
├── sddm/
│   ├── hyprland.conf              → /etc/sddm.conf.d/hyprland.conf (optional preset)
│   │                              # Only needed if using SDDM instead of the
│   │                              #   active greetd + noctalia-greeter login
│   │                              #   manager — see KDE-REMOVAL.md. Presets
│   │                              #   one UWSM-managed Hyprland session and an
│   │                              #   X11 greeter; does NOT enable autologin.
│   ├── sddm.conf                  # Reference SDDM base configuration
│   └── sessions/
│       └── hyprland-uwsm.desktop  → /usr/local/share/wayland-sessions/
│                                  # Limits SDDM to the UWSM-managed Hyprland session.
├── uwsm/
│   └── env                        → ~/.config/uwsm/env (linked via manifest.conf)
│                                  # Session environment: BROWSER=brave, cursor
│                                  #   theme (Bibata-Modern-Ice), Qt/Electron
│                                  #   Wayland hints, PATH, and NVM initialization.
├── hypr/                          → ~/.config/hypr/
│   ├── hyprland.conf              # entry point, sources everything below
│   ├── hyprlock.conf, hypridle.conf
│   ├── config/
│   │   ├── autostart.conf         # exec-once list — session infrastructure ONLY:
│   │   │                          #   hyprpm reload, Noctalia via the watchdog
│   │   │                          #   script below, cliphist, dbus/systemd env
│   │   │                          #   import, hypridle, theme-border-watch. No
│   │   │                          #   applications: the session comes up on an
│   │   │                          #   empty workspace by design. Retired lines
│   │   │                          #   (hyprpaper, fcitx5, mako, nm-applet, wob)
│   │   │                          #   are kept commented with the reason.
│   │   ├── keybinds.conf          # all bindd/bindr/bindm binds
│   │   ├── colors.conf            # palette variables — kept as Catppuccin-shaped
│   │   │                          #   names ($mauve, $text, $surface0, ...) but
│   │   │                          #   the *values* are live-synced from Noctalia's
│   │   │                          #   active theme by sync-theme-border.sh, so
│   │   │                          #   whatever hex is here reflects the palette
│   │   │                          #   selected in Noctalia at snapshot time, not
│   │   │                          #   necessarily Catppuccin or Jade specifically.
│   │   ├── variables.conf         # gaps + borders. border_size=2. Both
│   │   │                          #   col.active_border (alpha ee) and
│   │   │                          #   col.inactive_border (alpha aa — visible,
│   │   │                          #   one step down, NOT invisible) are synced
│   │   │                          #   to Noctalia's accent as a 45deg gradient.
│   │   │                          #   gaps_out is 4,0,0,0 (top only): windows
│   │   │                          #   sit flush to the screen on three sides,
│   │   │                          #   gaps_in=4 separates them from each other,
│   │   │                          #   and the top gap clears the bar.
│   │   ├── windowrules.conf       # window/layer rules incl. blur/xray for Noctalia + wofi
│   │   ├── plugins.conf           # `plugin:...` config for hyprpm-managed plugins
│   │   │                          #   (Hyprspace and dynamic-cursors) — see
│   │   │                          #   "Plugins" below. The
│   │   │                          #   plugins themselves are NOT installed by
│   │   │                          #   copying this repo; hyprpm manages those
│   │   │                          #   separately (see Install).
│   │   ├── defaults.conf          # terminal/filemanager/applauncher variable defaults
│   │   ├── animations.conf, decorations.conf, input.conf,
│   │   │   monitor.conf, environment.conf
│   └── scripts/
│       ├── minimize.sh, restore.sh, screenshot.sh
│       ├── volume.sh                  # PipeWire/wpctl volume control with 150% boost ceiling
│       ├── nightlight-temperature.sh  # Scroll wheel handler (2500–6500 K in 250 K steps)
│       ├── noctalia-watchdog.sh       # Runs `noctalia` in a restart-on-crash loop.
│       │                              #   Deliberately NOT a systemd --user service:
│       │                              #   apps launched from Noctalia's own launcher
│       │                              #   inherit its cgroup, and Chromium's sandbox
│       │                              #   cannot tolerate living inside a systemd
│       │                              #   service scope — every Chrome/Brave launch
│       │                              #   from the launcher crashed instantly with
│       │                              #   SIGSEGV when Noctalia ran as
│       │                              #   noctalia.service (confirmed via
│       │                              #   coredumpctl). This plain restart loop
│       │                              #   gives the same crash-resilience without
│       │                              #   that problem.
│       ├── launcher-open.sh           # Super+Space target. Opening the launcher
│       │                              #   while the cursor rests over a bar widget
│       │                              #   (e.g. media) triggers that widget's
│       │                              #   hover-preview panel, which force-closes
│       │                              #   the launcher within ~1s since Noctalia's
│       │                              #   panels are mutually exclusive — confirmed
│       │                              #   reproducible. This moves the cursor to
│       │                              #   screen center first so nothing can steal
│       │                              #   the panel slot.
│       ├── toggle-bar.sh              # Super+B: hides the bar *and* drops its
│       │                              #   blur decoration (bar-hide alone still
│       │                              #   left a frosted-glass strip behind).
│       ├── nightlight-toggle.sh       # Bar nightlight icon action. Noctalia's own
│       │                              #   gamma engine has a confirmed upstream bug
│       │                              #   (force can't be toggled back off), so this
│       │                              #   drives `hyprsunset` directly instead —
│       │                              #   process running/not-running is the only
│       │                              #   state, nothing to get stuck. Also rewrites
│       │                              #   the bar icon's glyph (moon-off/moon-stars)
│       │                              #   and hot-reloads Noctalia to reflect it.
│       ├── sync-theme-border.sh       # Reads Noctalia's active theme (custom
│       │                              #   palette JSON, community palette, or
│       │                              #   builtin) and writes its primary/secondary
│       │                              #   accent into colors.conf + variables.conf,
│       │                              #   so window borders always match the bar's
│       │                              #   item border color.
│       ├── nightlight-theme-sync.sh    # Flips 03-terminal/editor colour schemes to
│       │                              #   match the night light state.
│       ├── noctalia-restore.sh         # Puts settings.toml back from the repo,
│       │                              #   or from any commit/tag. Stops Noctalia
│       │                              #   first (a restore under a running
│       │                              #   instance is overwritten from memory),
│       │                              #   validates the TOML and refuses a config
│       │                              #   whose panel_anchor_bar names no bar,
│       │                              #   writes atomically, and restarts via
│       │                              #   hyprctl so the cgroup stays right.
│       │                              #   `--list` shows the restore points.
│       └── theme-border-watch.sh      # inotify-watches settings.toml's [theme]
│                                      #   block and re-runs sync-theme-border.sh
│                                      #   whenever it changes — autostarted, keeps
│                                      #   window borders and bar colors in lockstep
│                                      #   with no manual step.
│
└── noctalia/
    ├── palettes/
    │   ├── CatppuccinMocha.json   → ~/.config/noctalia/palettes/
    │   └── ShadesOfJade.json      → ~/.config/noctalia/palettes/
    │           Two custom palettes. Which one is active is whatever
    │           [theme].custom_palette says in state/settings.toml below —
    │           check that file rather than assuming from this list.
    ├── state/settings.toml             → ~/.local/state/noctalia/settings.toml
    │       Bar layout and widgets, theme source, plugin enable list, keybinds.
    │       SEEDED, never symlinked: Noctalia rewrites this file itself, both on
    │       upgrade (schema migrations) and on every change made through its
    │       settings GUI, so a symlink here would be destroyed by a
    │       replace-style write and the repo would silently stop tracking it.
    │       `./install.sh status` compares repo against live and
    │       `./install.sh pull` brings live changes in as a reviewable diff —
    │       run pull after tuning the bar, or the change only ever exists on
│       this machine. The Obsidian status widget is configured for the
│       `~/Documents/kneeraazon` vault (URI name `kneeraazon`), alongside the
│       AI usage bar widget.
│       See "Bar styling can be reset by an upgrade" below.
    └── dbus-override/fr.emersion.mako.service   → ~/.local/share/dbus-1/services/ (linked)
            User-level override so D-Bus service *activation* launches
            Noctalia instead of mako when something requests
            org.freedesktop.Notifications. Needed because mako ships its own
            dbus-1/services file that respawns it regardless of whether its
            systemd unit or Hyprland exec-once are disabled.
```

## Install

```bash
# 1. Packages (compositor, shell, helpers, fonts) — see 01-system/cachyos/packages/
mapfile -t repo_packages < <(awk 'NF && $1 !~ /^#/ && $2 != "(AUR)" {print $1}' \
  ../../01-system/cachyos/packages/desktop.txt ../../01-system/cachyos/packages/fonts.txt)
mapfile -t aur_packages < <(awk 'NF && $1 !~ /^#/ && $2 == "(AUR)" {print $1}' \
  ../../01-system/cachyos/packages/desktop.txt ../../01-system/cachyos/packages/fonts.txt)
sudo pacman -S --needed "${repo_packages[@]}"
aur_helper="$(command -v paru || command -v yay || true)"
if ((${#aur_packages[@]})) && [[ -z "$aur_helper" ]]; then
  echo "Install paru or yay before installing AUR packages" >&2
  exit 1
fi
if ((${#aur_packages[@]})); then
  "$aur_helper" -S --needed "${aur_packages[@]}"
fi

# 2. Config — the repo root installer links hypr/, scripts/, uwsm/env, the
#    Noctalia palettes, the D-Bus mako override, and fontconfig, and seeds
#    Noctalia's settings.toml.
cd ../.. && ./install.sh && ./install.sh status

# 3. Ensure competing user notification/shell units stay disabled:
systemctl --user disable --now mako.service noctalia.service 2>/dev/null || true

# 4. Display manager: greetd + noctalia-greeter is the active login manager on
#    this workstation. If using SDDM instead, install its optional session preset:
# sudo install -Dm644 02-desktop/hyprland/sddm/hyprland.conf /etc/sddm.conf.d/hyprland.conf
# sudo install -Dm644 02-desktop/hyprland/sddm/sessions/hyprland-uwsm.desktop \
#   /usr/local/share/wayland-sessions/hyprland-uwsm.desktop

# 5. Plugins — see "Plugins" below for what each one is and why the fork/commit
hyprpm update
hyprpm add https://github.com/ImanolBarba/Hyprspace 0799be7464fac7ea959b7c6c7809dadd6c21c5aa
hyprpm add https://github.com/VirtCode/hypr-dynamic-cursors
hyprpm enable Hyprspace dynamic-cursors
```

## Plugins

Managed by `hyprpm`, not by copying this repo — `hypr/config/plugins.conf` only
holds their `plugin:...` config keywords, which Hyprland silently ignores until
the matching plugin is actually built and enabled.

| Plugin | What it does | Keybind |
|---|---|---|
| [Hyprspace](https://github.com/KZDKM/Hyprspace) | Workspace overview (GNOME/macOS Mission Control-style) | `Super+H` |
| [dynamic-cursors](https://github.com/VirtCode/hypr-dynamic-cursors) | Cursor tilts with movement, shake-to-find | n/a (mouse-driven) |
| [hy3](https://github.com/outfoxxed/hy3) | Optional i3/sway-style manual tiling layout, alternative to `dwindle` | none — not installed |
| [split-monitor-workspaces](https://github.com/Duckonaut/split-monitor-workspaces) | Optional per-monitor workspace numbering | none — not installed |

Hyprspace upstream does not build on Hyprland 0.56.x because of a moved
header. The baseline uses the tested `ImanolBarba/Hyprspace` migration fork,
pinned to commit `0799be7464fac7ea959b7c6c7809dadd6c21c5aa`. The `hy3` plugin
is optional and not installed by the baseline.

`hyprexpo` and `hyprgrass` were evaluated and dropped: every hyprexpo
fork/branch found hits the same broken-header problem with no fix anywhere
(Hyprspace already covers overview functionality, so not missed), and
hyprgrass (touch gestures) has nothing to do on a machine with no
touchscreen.

**hy3 and split-monitor-workspaces are optional and not part of the baseline
plugin set**, since activating either changes fundamental interaction
behavior:
- hy3 would be a full alternative layout engine — `general:layout` is still
  `dwindle` in `variables.conf`. Set it to `hy3` to try it.
- split-monitor-workspaces would need every workspace keybind in `keybinds.conf`
  (`Super`+`1-6`, `Shift`+those, `Ctrl`+those — 18 binds) rewritten from
  `workspace`/`movetoworkspace(silent)` to this plugin's own
  `split-workspace`/`split-movetoworkspace(silent)` dispatchers to do
  anything at all. Not done here since that's a decision, not a default.

**The hyprland-plugins repository was removed** — hyprbars title bars clashed
with the minimal aesthetic; borders-plus-plus and hyprfocus are not part of
the baseline plugin set.

**A stale-binary gotcha worth knowing**: if Hyprland's package gets
reinstalled/updated without restarting the compositor, the running process's
`/proc/self/exe` points at a deleted file, and `hyprctl plugin load` fails
for *every* plugin with `cannot make canonical path: No such file or
directory [/proc/self/exe]` — nothing to do with the plugins themselves.
Restart Hyprland (or reboot) to fix it.

## Notes

- Noctalia (`noctalia` package) replaces Waybar, wofi, and
  mako entirely — see `hypr/config/autostart.conf`
  (`scripts/noctalia-watchdog.sh`, not a systemd service — see that script's
  own comments for why) and `hypr/config/keybinds.conf` (`noctalia msg ...`
  IPC calls for launcher, clipboard, bar toggle).
- `hyprland.conf` sources absolute `~/.config/hypr/...` paths, so it works
  regardless of clone location as long as the files land under
  `~/.config/hypr/`.
- Old Waybar/wofi/Quickshell-custom-bar configs are intentionally not
  included here — retired in favor of Noctalia.
- **Night light does not use Noctalia's own gamma engine.** That module has
  a confirmed upstream bug in this build (`nightlight-force-toggle`,
  `nightlight-disable`, and even a direct config edit + reload all fail to
  turn it back off once forced on — verified via the running Noctalia's own
  Control Center, not just IPC). The bar's nightlight widget is a
  `custom_button` wired to `scripts/nightlight-toggle.sh`, which drives
  `hyprsunset` (Hyprland's own dedicated blue-light tool, `pacman -S
  hyprsunset`) as a plain process instead — on = launch it, off = kill it.
  `[nightlight] enabled = false` is set in settings.toml so Noctalia's own
  gamma engine cannot fight it. Click the bar button to toggle; scroll up to
  warm the display and down to cool it in 250 K steps (2500–6500 K). The
  selected temperature persists across toggles, and the widget posts the
  current setting as a short notification.
- **Recovering a reset config is one command:**
  `~/.config/hypr/scripts/noctalia-restore.sh` (add a commit or tag to go
  further back, `--list` to see the options). Do not just `cp` the file into
  place — Noctalia holds the config in memory and writes it back out, so a
  restore under a running instance is undone within seconds.
- **Bar styling can be reset by a Noctalia upgrade, silently.** The 5.0.1
  upgrade (`config_version` 14) rewrote `settings.toml` and put the whole
  `[bar.kneeraazon]` block back to stock: the border hex values, `border_width`,
  `font_family`, `font_weight`, `icon_color`, `widget_spacing`, `scale` and the
  margins all reverted, while the widget list survived — so the bar still looked
  broadly right and the regression went unnoticed. `./install.sh status` now
  reports this as DRIFT on the seeded settings.toml; the fix is to compare
  against the last known-good copy in git (`git log -p --
  02-desktop/hyprland/noctalia/state/settings.toml`) rather than re-tuning by eye.
- **Bar fonts come from packages, not this repo.** `[bar.kneeraazon].font_family`
  and `[widget.clock].font_family` use `JetBrains Mono`, `[shell].font_family`
  and `[widget."tmelik/system-monitor:summary"].font_family` use `DejaVu Sans`,
  and terminal/editor configs use `JetBrains Maple Mono` and `FiraCode Nerd Font`.
  If any of those is missing, Noctalia silently falls back to a default sans and
  the bar's metrics shift — `01-system/cachyos/packages/fonts.txt` lists which
  package supplies each.
- **Window border color tracks Noctalia's theme automatically.**
  `scripts/theme-border-watch.sh` is autostarted and watches
  `settings.toml`'s `[theme]` block; any change re-runs
  `scripts/sync-theme-border.sh`, which pulls the active palette's
  primary/secondary accent and rewrites `colors.conf` + `variables.conf`.
  Change the palette in Noctalia (or switch `custom_palette` between
  `CatppuccinMocha`/`ShadesOfJade`) and window borders follow within a
  second, no manual re-sync needed.
