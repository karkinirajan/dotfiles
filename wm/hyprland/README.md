# Hyprland + Noctalia

CachyOS/Arch Wayland desktop: Hyprland compositor with Noctalia as the shell
(bar, launcher, clipboard history, control center) — replaces Waybar/wofi/mako.

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
│   └── hyprland.conf              → /etc/sddm.conf.d/hyprland.conf
│                                  # Only needed if starting from a Plasma-default
│                                  #   login manager — see KDE-REMOVAL.md. Presets
│                                  #   the Hyprland (uwsm-managed) session and a
│                                  #   Wayland-native greeter; does NOT enable
│                                  #   passwordless autologin (no `User=` set).
├── hypr/                          → ~/.config/hypr/
│   ├── hyprland.conf              # entry point, sources everything below
│   ├── hyprlock.conf, hypridle.conf, hyprpaper.conf
│   ├── config/
│   │   ├── autostart.conf         # exec-once list (Noctalia via the watchdog
│   │   │                          #   script below, hyprpaper, fcitx5, kwallet,
│   │   │                          #   polkit, theme-border-watch, hyprpm reload...)
│   │   ├── keybinds.conf          # all bindd/bindr/bindm binds
│   │   ├── colors.conf            # palette variables — kept as Catppuccin-shaped
│   │   │                          #   names ($mauve, $text, $surface0, ...) but
│   │   │                          #   the *values* are live-synced from Noctalia's
│   │   │                          #   active theme by sync-theme-border.sh, so
│   │   │                          #   whatever hex is here reflects the palette
│   │   │                          #   selected in Noctalia at snapshot time, not
│   │   │                          #   necessarily Catppuccin or Jade specifically.
│   │   ├── variables.conf         # gaps, borders (col.active_border synced to
│   │   │                          #   Noctalia's primary/secondary accent, 45deg
│   │   │                          #   gradient; border_size=1, thin by design)
│   │   ├── windowrules.conf       # window/layer rules incl. blur/xray for Noctalia + wofi
│   │   ├── plugins.conf           # `plugin:...` config for hyprpm-managed plugins
│   │   │                          #   (Hyprspace, borders-plus-plus, hyprfocus,
│   │   │                          #   dynamic-cursors) — see "Plugins" below. The
│   │   │                          #   plugins themselves are NOT installed by
│   │   │                          #   copying this repo; hyprpm manages those
│   │   │                          #   separately (see Install).
│   │   ├── defaults.conf          # $terminal/$applauncher/etc variable defaults
│   │   ├── animations.conf, decorations.conf, input.conf,
│   │   │   monitor.conf, environment.conf
│   └── scripts/
│       ├── minimize.sh, restore.sh, wallpaper.sh
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
    │       Bar layout/widgets (incl. paired usage% + absolute-value sysmon
    │       widgets for CPU/GPU/memory), theme source=custom, keybinds config,
    │       etc. Noctalia rewrites this file on every run and the bundled
    │       Settings GUI can too (it's live state, not a static config) —
    │       treat this copy as a snapshot/reference, not something to symlink
    │       live.
    └── dbus-override/fr.emersion.mako.service   → ~/.local/share/dbus-1/services/
            User-level override so D-Bus service *activation* launches
            Noctalia instead of mako when something requests
            org.freedesktop.Notifications. Needed because mako ships its own
            dbus-1/services file that respawns it regardless of whether its
            systemd unit or Hyprland exec-once are disabled.
```

## Install

```sh
cp hyprland-shortcuts.md ~/
cp -r hyprland/hypr/* ~/.config/hypr/
chmod +x ~/.config/hypr/scripts/*.sh
mkdir -p ~/.config/noctalia/palettes
cp hyprland/noctalia/palettes/* ~/.config/noctalia/palettes/
mkdir -p ~/.local/state/noctalia ~/.local/share/dbus-1/services
cp hyprland/noctalia/state/settings.toml ~/.local/state/noctalia/settings.toml
cp hyprland/noctalia/dbus-override/fr.emersion.mako.service ~/.local/share/dbus-1/services/
systemctl --user disable --now mako.service noctalia.service 2>/dev/null
sudo pacman -S --needed hyprsunset  # night light backend, see below

# Plugins — see "Plugins" below for what each one is and why the fork/commit
hyprpm update
hyprpm add https://github.com/ImanolBarba/Hyprspace migrate-v2
hyprpm add https://github.com/hyprwm/hyprland-plugins
hyprpm add https://github.com/kociap/hy3
hyprpm add https://github.com/VirtCode/hypr-dynamic-cursors
hyprpm add https://github.com/Duckonaut/split-monitor-workspaces
hyprpm enable Hyprspace borders-plus-plus hyprfocus hy3 dynamic-cursors split-monitor-workspaces
```

## Plugins

Managed by `hyprpm`, not by copying this repo — `hypr/config/plugins.conf` only
holds their `plugin:...` config keywords, which Hyprland silently ignores until
the matching plugin is actually built and enabled.

| Plugin | What it does | Keybind |
|---|---|---|
| [Hyprspace](https://github.com/KZDKM/Hyprspace) | Workspace overview (GNOME/macOS Mission Control-style) | `Super+H` |
| [hy3](https://github.com/outfoxxed/hy3) | i3/sway-style manual tiling layout, alternative to `dwindle` | none — opt-in, see below |
| [split-monitor-workspaces](https://github.com/Duckonaut/split-monitor-workspaces) | Per-monitor independent workspace numbering | none — loaded but inert, see below |
| [borders-plus-plus](https://github.com/hyprwm/hyprland-plugins) | Extra static outer border accent | n/a (visual only) |
| [hyprfocus](https://github.com/hyprwm/hyprland-plugins) | Flash animation on keyboard-driven focus changes | n/a (automatic) |
| [dynamic-cursors](https://github.com/VirtCode/hypr-dynamic-cursors) | Cursor tilts with movement, shake-to-find | n/a (mouse-driven) |

**Two upstream repos are broken on Hyprland 0.56.x and had to be installed
from a fork/PR instead** — both are open, unfixed issues as of this writing:
- Hyprspace: `KZDKM/Hyprspace` issue #239 (moved header path,
  `AnimationManager.hpp`) → installed from `ImanolBarba/Hyprspace` branch
  `migrate-v2` (PR #238) instead.
- hy3: `outfoxxed/hy3` issue #334 (same class of bug, different header) →
  installed from `kociap/hy3` instead (linked as the fix in that issue's
  comments).

`hyprexpo` and `hyprgrass` were evaluated and dropped: every hyprexpo
fork/branch found hits the same broken-header problem with no fix anywhere
(Hyprspace already covers overview functionality, so not missed), and
hyprgrass (touch gestures) has nothing to do on a machine with no
touchscreen.

**hy3 and split-monitor-workspaces are installed and loaded but deliberately
not wired up**, since activating either changes fundamental interaction
behavior:
- hy3 is a full alternative layout engine — `general:layout` is still
  `dwindle` in `variables.conf`. Set it to `hy3` to try it.
- split-monitor-workspaces needs every workspace keybind in `keybinds.conf`
  (`Super`+`1-9,0`, `Shift`+those, `Ctrl`+those — ~30 binds) rewritten from
  `workspace`/`movetoworkspace(silent)` to this plugin's own
  `split-workspace`/`split-movetoworkspace(silent)` dispatchers to do
  anything at all. Not done here since that's a decision, not a default.

**hyprbars was tried and removed** — title bars on every window clashed with
the borderless/minimal aesthetic the rest of this setup is built around.
Disabled via `hyprpm disable hyprbars` rather than fully uninstalled, since
it ships in the same repo as borders-plus-plus/hyprfocus (which are kept).

**A stale-binary gotcha worth knowing**: if Hyprland's package gets
reinstalled/updated without restarting the compositor, the running process's
`/proc/self/exe` points at a deleted file, and `hyprctl plugin load` fails
for *every* plugin with `cannot make canonical path: No such file or
directory [/proc/self/exe]` — nothing to do with the plugins themselves.
Restart Hyprland (or reboot) to fix it.

## Notes

- Noctalia (`noctalia-qs` + `noctalia` packages) replaces Waybar, wofi, and
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
  `[nightlight] enabled = false` is set permanently in settings.toml so
  Noctalia's own schedule can never interfere.
- **Window border color tracks Noctalia's theme automatically.**
  `scripts/theme-border-watch.sh` is autostarted and watches
  `settings.toml`'s `[theme]` block; any change re-runs
  `scripts/sync-theme-border.sh`, which pulls the active palette's
  primary/secondary accent and rewrites `colors.conf` + `variables.conf`.
  Change the palette in Noctalia (or switch `custom_palette` between
  `CatppuccinMocha`/`ShadesOfJade`) and window borders follow within a
  second, no manual re-sync needed.
