---
title: Font rendering
part: "02"
chapter: "02"
topic: fonts
last_verified: 2026-10-29
status: current
sources:
  - https://www.freedesktop.org/software/fontconfig/fontconfig-user.html
---

# 02.2 · Font Rendering (`fontconfig`)

Fontconfig rendering rules for the Wayland desktop session.

```
02-desktop/fonts/
├── README.md
└── fontconfig/
    └── fonts.conf    → ~/.config/fontconfig/fonts.conf (linked via manifest.conf)
```

## What `fonts.conf` configures

- **Synthetic styles:** Generates artificial oblique (`matrix` shear) and bold
  (`embolden`) variants when a family lacks dedicated italic or bold faces.
- **Rasterization:** Enables antialiasing, `hintslight` hinting and `rgb` subpixel
  order for crisp text on standard RGB panels. Only `rgba = rgb` differs from the
  fontconfig defaults (slight hinting, no subpixel, antialiasing and the
  `lcddefault` filter come from the distro's linked config); the two synthetic
  stanzas are the stock `90-synthetic.conf` rules, which fontconfig 2.18 already
  links by default.
- **User font directory:** Includes `$XDG_DATA_HOME/fonts` (`~/.local/share/fonts`).

## Font packages

Font binary files are never tracked in git. Install the required families from
[`01-system/cachyos/packages/fonts.txt`](../../01-system/cachyos/packages/fonts.txt)
and refresh the font cache:

```sh
fc-cache -fv
```
