# Hyprland + Noctalia

CachyOS/Arch Wayland desktop: Hyprland compositor with Noctalia as the shell
(bar, launcher, clipboard history, control center) — replaces Waybar/wofi/mako.

```
hyprland/
├── hypr/                          → ~/.config/hypr/
│   ├── hyprland.conf              # entry point, sources everything below
│   ├── hyprlock.conf, hypridle.conf, hyprpaper.conf
│   ├── config/
│   │   ├── autostart.conf         # exec-once list (Noctalia, hyprpaper, fcitx5, kwallet, polkit, theme-border-watch...)
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
│   │   ├── defaults.conf          # $terminal/$applauncher/etc variable defaults
│   │   ├── animations.conf, decorations.conf, input.conf,
│   │   │   monitor.conf, environment.conf
│   └── scripts/
│       ├── minimize.sh, restore.sh, wallpaper.sh
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
cp -r hyprland/hypr/* ~/.config/hypr/
chmod +x ~/.config/hypr/scripts/*.sh
mkdir -p ~/.config/noctalia/palettes
cp hyprland/noctalia/palettes/* ~/.config/noctalia/palettes/
mkdir -p ~/.local/state/noctalia ~/.local/share/dbus-1/services
cp hyprland/noctalia/state/settings.toml ~/.local/state/noctalia/settings.toml
cp hyprland/noctalia/dbus-override/fr.emersion.mako.service ~/.local/share/dbus-1/services/
systemctl --user disable --now mako.service 2>/dev/null
sudo pacman -S --needed hyprsunset  # night light backend, see below
```

## Notes

- Noctalia (`noctalia-qs` + `noctalia` packages) replaces Waybar, wofi, and
  mako entirely — see `hypr/config/autostart.conf` (`noctalia -d`) and
  `hypr/config/keybinds.conf` (`noctalia msg ...` IPC calls for launcher,
  clipboard, bar toggle).
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
