# 03.4 · Alacritty

Primary GPU-accelerated terminal emulator (`$terminal = alacritty` in Hyprland).

```
03-terminal/alacritty/
├── README.md         ← you are here
├── alacritty.toml    → ~/.config/alacritty/alacritty.toml (linked via manifest.conf)
└── SHORTCUTS.md      # keybinding reference (matched to kitty.conf)
```

## Theme integration

`alacritty.toml` imports `~/.config/alacritty/themes/noctalia.toml` and defines
no `[colors]` table of its own. Noctalia's built-in `alacritty` template
regenerates `themes/noctalia.toml` whenever the active desktop palette changes,
and Alacritty (`live_config_reload = true`) applies the new colours immediately
without touching the tracked `alacritty.toml`.

See [`SHORTCUTS.md`](SHORTCUTS.md) for the complete keyboard shortcut table.
