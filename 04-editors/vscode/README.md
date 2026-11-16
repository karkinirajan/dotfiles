# 04.1 · Visual Studio Code

> **Status, 2026-11-16:** VS Code was uninstalled from the primary workstation in the November 2026 trim (2026-11-11 and 2026-11-12), and its two seed entries left `manifest.conf`. The settings, keybindings and extension list below stay as reference for a reinstall. See [`workstation-changes.md`](../../01-system/cachyos/workstation-changes.md).

User settings, keybindings, and extension manifest for `visual-studio-code-bin`.

```text
04-editors/vscode/
├── README.md                  ← you are here
├── vscode-settings.json       → ~/.config/Code/User/settings.json (seeded)
├── vscode-keybindings.json    → ~/.config/Code/User/keybindings.json (seeded)
├── vscode-extensions.json     # curated extension IDs
└── extensions.sh              # bulk-install helper for vscode-extensions.json
```

## Why `seed` instead of `link`?

VS Code rewrites `settings.json` and `keybindings.json` whenever a setting is
toggled in its GUI (and `nightlight-theme-sync.sh` toggles
`workbench.colorTheme`). Seeding them via `manifest.conf` keeps the repo copy
safe from unreviewed runtime churn:

```sh
./install.sh status    # check if live VS Code settings drifted from repo
./install.sh pull      # copy live ~/.config/Code/User/*.json back into repo
./install.sh restore   # overwrite live files with the repo version
```

## Installing extensions

```sh
./04-editors/vscode/extensions.sh
```
