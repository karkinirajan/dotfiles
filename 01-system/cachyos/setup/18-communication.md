---
title: "18 Communication and Collaboration"
part: "01"
chapter: "18"
topic: communication
versions: []
last_verified: 2026-10-29
status: current
sources:
  - https://wiki.archlinux.org/title/XDG_Desktop_Portal
  - https://userbase.kde.org/KDE_Connect
---

# 18 Communication and Collaboration

## Purpose

Chat, email, video calls and phone integration on Hyprland, including the portals Wayland screen sharing needs.

## 18.1 Communication apps

```bash
sudo pacman -S --needed discord telegram-desktop thunderbird
paru -S slack-desktop zoom
```

| App | Source | Version seen 2026-10-28 |
|---|---|---|
| Discord | Arch extra | 1.0.167 |
| Telegram Desktop | Arch extra | 7.3.3 |
| Thunderbird | Arch extra | 158.0.1 (upstream 159.0, 2026-10-27) |
| Slack | AUR `slack-desktop` (repacks the official `.deb`; Slack for Linux is still labelled Beta) | 4.52.182 |
| Zoom | AUR `zoom` | 7.2.1 (7.2.5 announced for 2026-10-30) |

**Wayland screen sharing (Hyprland):**

```bash
sudo pacman -S --needed xdg-desktop-portal xdg-desktop-portal-hyprland xdg-desktop-portal-gtk
```

The portal packages are current (1.22.1, 1.4.1 and 1.15.3; `xdg-desktop-portal-hyprland` 1.5.0 is in `extra-testing`). No vendor documentation confirms Slack 4.52 or Zoom 7.2 screen sharing through PipeWire on Hyprland, so test a share after install. <!-- UNVERIFIED: screen sharing in Slack and Zoom on Hyprland --> Label: `machine-only`.

## 18.2 Email: Thunderbird

Built-in calendar (CalDAV, Microsoft Graph autodetect in 159), contacts and RSS. Supports Gmail, Outlook and any IMAP/SMTP. 159 adds a Linux tray unread count.

## 18.3 Phone integration: KDE Connect

```bash
sudo pacman -S --needed kdeconnect     # 26.08.2
sudo ufw allow from 192.168.0.0/16 to any port 1714:1764 proto udp
sudo ufw allow from 192.168.0.0/16 to any port 1714:1764 proto tcp
```

The package ships a ufw application profile (`/etc/ufw/applications.d/kdeconnect`), an XDG autostart entry, a D-Bus service and `kdeconnect-indicator` for the tray, and no systemd unit. The rules are scoped to the LAN because the firewall profile in chapter 19 keeps no unconditional inbound allows; use your own subnet, or the unscoped `ufw allow 1714:1764/udp` and `/tcp` from KDE UserBase if the phone is on a changing network.

Checked on the host (Hyprland 0.57 under uwsm): `kdeconnectd` starts from `/etc/xdg/autostart/org.kde.kdeconnect.daemon.desktop` at login. List paired devices with `kdeconnect-cli -l`. Label: `machine-only`.

## Sources

- [Arch wiki: XDG Desktop Portal](https://wiki.archlinux.org/title/XDG_Desktop_Portal), [KDE Connect on UserBase](https://userbase.kde.org/KDE_Connect)
- Ledger: cluster C10, topics `Slack`, `Zoom`, `Wayland screen share portals`, `KDE Connect` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
