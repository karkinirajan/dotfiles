---
title: Part 02 Desktop
part: "02"
topic: desktop
last_verified: 2026-10-29
status: current
---

# 02 · Desktop

The graphical session, from the compositor down to font rendering.

| Chapter | Path | Purpose |
|---------|------|---------|
| Hyprland + Noctalia | [`hyprland/`](hyprland/README.md) | Compositor config, shell settings, palettes, scripts, keybinds |
| Lua config migration | [`hyprland/lua-migration.md`](hyprland/lua-migration.md) | Plan and mapping for moving from hyprlang to Hyprland's Lua config (required from Hyprland 0.57) |
| Plasma removal | [`hyprland/KDE-REMOVAL.md`](hyprland/KDE-REMOVAL.md) | How the second desktop environment was removed (archived log) |
| Fonts | [`fonts/`](fonts/README.md) | Rendering rules only; font files come from packages |
| Login keyring | [`keyring/`](keyring/README.md) | Unlock gnome-keyring at login; one secrets daemon |

Read the Hyprland chapter first. Its README explains which parts the manifest
links, which are seeded, and which need manual steps.
