---
title: "21 Media, Office and Personal"
part: "01"
chapter: "21"
topic: media-office
versions: []
last_verified: 2026-10-29
status: current
sources:
  - https://github.com/mpv-player/mpv/releases
  - https://endoflife.date/libreoffice
---

# 21 Media, Office and Personal

## Purpose

Media players, graphics, office and file-handling tools, with the package source that works on CachyOS today.

## 21.1 Media players

```bash
sudo pacman -S --needed vlc mpv
```

VLC 3.0.24 (2026-09-22) is current stable; 4.0 is still in development. mpv 0.41.0 is the latest release (Arch extra 0.41.0-6).

`~/.config/mpv/mpv.conf`:

```ini
hwdec=auto
profile=high-quality
```

Two lines changed from the old file. `vo=gpu-next` is the default VO since mpv 0.41.0, so it is redundant (harmless to keep). `profile=gpu-hq` is a deprecated alias of `profile=high-quality`. `hwdec=auto` is still valid, but 0.41 prefers Vulkan hwdec and non-copy variants, so it may pick a different decoder than before; not tested on the RX 6700 XT. Label: `machine-only`.

## 21.2 Image editing

```bash
sudo pacman -S --needed gimp inkscape
```

GIMP 3.2.6 and Inkscape 1.4.4 are the current stable releases. Inkscape has a reported Wayland crash when moving a docked tab on some GTK versions.

## 21.3 Office suite

```bash
sudo pacman -S --needed libreoffice-fresh
sudo pacman -S --needed onlyoffice-bin   # CachyOS repo only (10.0.0)
```

LibreOffice Fresh is 26.8.1 (supported to 2027-06-13); `libreoffice-still` is 26.2.6 (EOL 2026-11-30). `onlyoffice-bin` is not in Arch repositories: it comes from the `cachyos` repo or the AUR (maintainer dbermond), so the pacman line works on CachyOS only.

## 21.4 Music

```bash
paru -S spotify                 # AUR 1.3.4.258, community build; Spotify does not actively support Linux
sudo pacman -S --needed strawberry       # local music (FLAC, MP3, gapless), 1.2.31
```

`spotify-launcher` (extra, 0.6.6) downloads the official client and is the pacman-only alternative.

## 21.5 File manager enhancements

```bash
sudo pacman -S --needed dolphin kdegraphics-thumbnailers ffmpegthumbs
```

All three are 26.08.2. Thumbnail packages add image and video previews. Dolphin outside Plasma needs a menu file for its "Open with" list; see chapter 17.3.

## 21.6 Archive manager

```bash
sudo pacman -S --needed ark 7zip unrar
```

## Sources

- [mpv releases](https://github.com/mpv-player/mpv/releases), [LibreOffice lifecycle](https://endoflife.date/libreoffice)
- Ledger: cluster C10, topics `mpv`, `VLC`, `GIMP`, `LibreOffice`, `OnlyOffice`, `Spotify` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
