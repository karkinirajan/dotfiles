---
title: "17 Project Management and Freelance"
part: "01"
chapter: "17"
topic: freelance-project-management
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 17 Project Management and Freelance


## 17.1 Invoicing & Finance

- **Invoice Ninja** — `docker run -d -p 8080:80 invoiceninja/invoiceninja` (self-hosted)
- **Wave Accounting** — https://www.waveapps.com/ (free cloud accounting)
- **AND.CO** — https://www.and.co/ (free proposals, contracts, invoicing — by Fiverr)

## 17.2 Upwork App

Install the bundled-runtime package in [`aur/upwork/`](../aur/upwork/). The
standard AUR recipe depends on Electron 36 and builds Chromium from source.
Upwork's screenshot/time tracker is not supported in Wayland sessions; see
[Upwork's Linux troubleshooting guide](https://support.upwork.com/hc/en-us/articles/211064108-How-to-troubleshoot-our-desktop-app-Linux).
The app can launch in Hyprland, but screenshot-based hourly tracking needs a
supported Xorg session.

## 17.3 PDF Viewer

```bash
sudo pacman -S okular   # KDE PDF viewer (pre-installed on CachyOS KDE)
```

## 17.4 Calendar

```bash
sudo pacman -S korganizer   # Standalone KDE calendar
# Or use Thunderbird's built-in calendar
```
