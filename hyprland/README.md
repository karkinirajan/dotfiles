# Hyprland + Noctalia

CachyOS/Arch Wayland desktop: Hyprland compositor with Noctalia as the shell
(bar, launcher, clipboard history, control center) — replaces Waybar/wofi/mako.

```
hyprland/
├── hypr/                          → ~/.config/hypr/
│   ├── hyprland.conf              # entry point, sources everything below
│   ├── hyprlock.conf, hypridle.conf, hyprpaper.conf
│   ├── config/
│   │   ├── autostart.conf         # exec-once list (Noctalia, hyprpaper, fcitx5, kwallet, polkit...)
│   │   ├── keybinds.conf          # all bindd/bindr/bindm binds
│   │   ├── colors.conf            # Catppuccin Mocha palette variables
│   │   ├── variables.conf         # gaps, borders (col.active_border = mauve)
│   │   ├── windowrules.conf       # window/layer rules incl. blur/xray for Noctalia + wofi
│   │   ├── defaults.conf          # $terminal/$applauncher/etc variable defaults
│   │   ├── animations.conf, decorations.conf, input.conf,
│   │   │   monitor.conf, environment.conf
│   └── scripts/                   # minimize.sh, restore.sh, wallpaper.sh
│
└── noctalia/
    ├── palettes/CatppuccinMocha.json   → ~/.config/noctalia/palettes/
    │       Custom palette matching the same Catppuccin Mocha values used
    │       by hypr/config/colors.conf, so the shell and compositor match.
    ├── state/settings.toml             → ~/.local/state/noctalia/settings.toml
    │       Bar layout/widgets, theme source=custom, keybinds config, etc.
    │       Noctalia rewrites this file on every run (it's the live state,
    │       not a static config) — treat this copy as a snapshot/reference,
    │       not something to symlink live.
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
mkdir -p ~/.config/noctalia/palettes
cp hyprland/noctalia/palettes/* ~/.config/noctalia/palettes/
mkdir -p ~/.local/state/noctalia ~/.local/share/dbus-1/services
cp hyprland/noctalia/state/settings.toml ~/.local/state/noctalia/settings.toml
cp hyprland/noctalia/dbus-override/fr.emersion.mako.service ~/.local/share/dbus-1/services/
systemctl --user disable --now mako.service 2>/dev/null
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
