---
title: "17 Project Management and Freelance"
part: "01"
chapter: "17"
topic: freelance-project-management
versions: []
last_verified: 2026-10-29
status: current
sources:
  - https://hub.docker.com/r/invoiceninja/invoiceninja
  - https://support.upwork.com/hc/en-us/articles/211064108-How-to-troubleshoot-our-desktop-app-Linux
  - https://wiki.archlinux.org/title/Dolphin
---

# 17 Project Management and Freelance

## Purpose

Invoicing, the Upwork desktop app, and the PDF and calendar tools a freelance workflow needs on a Hyprland machine without KDE Plasma.

## 17.1 Invoicing and finance

- **Invoice Ninja** (self-hosted): the old one-line `docker run -d -p 8080:80 invoiceninja/invoiceninja` cannot work. The image runs PHP-FPM on port 9000 and needs `APP_KEY`, a database and a web server, and the `master` branch image is deprecated. Use the Debian image through Docker Compose from the official repository, and generate the key with the Debian image:

  ```bash
  git clone https://github.com/invoiceninja/dockerfiles.git -b debian
  docker run --rm -it invoiceninja/invoiceninja-debian php artisan key:generate --show
  ```

  Put the key in the compose environment file, then `docker compose up -d`. Label: `machine-only`; the stack was not started in the research environment.
- **Wave Accounting**: <https://www.waveapps.com/>. The Starter plan is free (invoices, estimates, manual statement upload); bank import, collaborators and late reminders need Pro ($19 a month). Wave supports the US and Canada only; outside them an invoice can be exported as PDF or a link but not sent through Wave.
- **AND.CO** was shut down: Fiverr Workspace (AND.CO) closed on 2026-03-01 and its data was deleted; `and.co` redirects to `fiverr.com`. The entry was removed.

## 17.2 Upwork app

Install the vendor-package recipe in [`aur/upwork/`](../aur/upwork/README.md). It repackages the official `.deb` with its bundled runtime; the AUR `upwork` package instead depends on `electron36`, which reached end of life on 2025-10-27 (see that README for the trade-off). Upwork's time tracker names only "Ubuntu on Xorg" as supported; screenshot capture does not work in Wayland sessions, so the app launches in Hyprland for chat and contracts but hourly tracking needs a supported Xorg session ([Upwork's Linux guide](https://support.upwork.com/hc/en-us/articles/211064108-How-to-troubleshoot-our-desktop-app-Linux)). <!-- UNVERIFIED: Upwork support position on non-Ubuntu Xorg sessions -->

## 17.3 PDF viewer

```bash
sudo pacman -S --needed okular
```

Okular is not preinstalled here (that was true of CachyOS KDE only). Dolphin, Okular and Ark are all 26.08.2. Outside Plasma, Dolphin's "Open with" list is empty unless a menu file exists:

```bash
sudo pacman -S --needed archlinux-xdg-menu
XDG_MENU_PREFIX=arch- kbuildsycoca6 --noincremental
```

Alternatively export `XDG_MENU_PREFIX=arch-` in the Hyprland/uwsm environment. Label: `machine-only`.

## 17.4 Calendar

`korganizer` is not standalone: the Arch package pulls the Akonadi/PIM stack (39 runtime dependencies). Thunderbird's built-in calendar (CalDAV, and Graph in 158 and 159) is already installed. Lighter standalone options in `extra`, untested on Hyprland: `merkuro` 26.08.2, `gnome-calendar` 51.0, `calcurse` 4.8.2. <!-- UNVERIFIED: usability of the alternatives on Hyprland -->

## Sources

- Ledger: cluster C10, topics `Invoice Ninja`, `Wave`, `AND.CO`, `Upwork`, `Okular`, `korganizer` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
