# 03.3 · Kitty

Secondary GPU-accelerated terminal emulator configuration (Alacritty is the
primary terminal bound to `Super+Return`; Kitty remains installed and configured
in parity).

```text
03-terminal/kitty/
├── README.md                 ← you are here
├── kitty.conf                → ~/.config/kitty/kitty.conf (linked)
├── catppuccin-mocha.conf     → ~/.config/kitty/catppuccin-mocha.conf (linked)
├── gruvbox-dark-hard.conf    → ~/.config/kitty/gruvbox-dark-hard.conf (linked)
└── psql-mode.conf            → ~/.config/kitty/psql-mode.conf (linked)
```

## Why per-file links?

`manifest.conf` links the four static files individually rather than linking
`~/.config/kitty/` as a directory. The live `~/.config/kitty/` directory also
holds `current-theme.conf`, which is rewritten at runtime by
`~/.config/hypr/scripts/nightlight-theme-sync.sh` (Catppuccin Mocha when
night-light is off, Gruvbox Dark Hard when night-light is on) and ignored via
`.gitignore`.
