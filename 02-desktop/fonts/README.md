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
- **Rasterization:** Enables antialiasing, `hintslight` hinting, `rgb` subpixel
  order, and `lcddefault` LCD filtering for crisp text on standard RGB panels.
- **User font directory:** Includes `$XDG_DATA_HOME/fonts` (`~/.local/share/fonts`).

## Font packages

Font binary files are never tracked in git. Install the required families from
[`01-system/cachyos/packages/fonts.txt`](../../01-system/cachyos/packages/fonts.txt)
and refresh the font cache:

```sh
fc-cache -fv
```
