---
title: "18 Communication and Collaboration"
part: "01"
chapter: "18"
topic: communication
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 18 Communication and Collaboration


## 18.1 Communication Apps

```bash
sudo pacman -S discord telegram-desktop thunderbird
paru -S slack-desktop zoom
```

**Wayland screen sharing portals (Hyprland):**

```bash
sudo pacman -S xdg-desktop-portal xdg-desktop-portal-hyprland xdg-desktop-portal-gtk
```

## 18.2 Email — Thunderbird

```bash
sudo pacman -S thunderbird
```

Built-in calendar, contacts, and RSS reader. Supports Gmail, Outlook, and any IMAP/SMTP.

## 18.3 Phone Integration — KDE Connect

```bash
sudo pacman -S kdeconnect
sudo ufw allow 1714:1764/udp
sudo ufw allow 1714:1764/tcp
```

Syncs clipboard, notifications, files, and SMS between phone and desktop.
