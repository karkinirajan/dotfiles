---
title: "21 Media, Office and Personal"
part: "01"
chapter: "21"
topic: media-office
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 21 Media, Office and Personal


## 21.1 Media Players

```bash
sudo pacman -S vlc mpv
```

`~/.config/mpv/mpv.conf`:

```ini
hwdec=auto
vo=gpu-next
profile=gpu-hq
```

## 21.2 Image Editing

```bash
sudo pacman -S gimp inkscape
```

## 21.3 Office Suite

```bash
sudo pacman -S libreoffice-fresh onlyoffice-bin
```

## 21.4 Music

```bash
paru -S spotify                 # Streaming
sudo pacman -S strawberry       # Local music (FLAC, MP3, gapless playback)
```

## 21.5 File Manager Enhancements

```bash
sudo pacman -S dolphin kdegraphics-thumbnailers ffmpegthumbs
# Thumbnail packages add image/video previews in Dolphin
```

## 21.6 Archive Manager

```bash
sudo pacman -S ark 7zip unrar
```
