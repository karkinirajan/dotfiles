---
title: Workstation changes, November 2026
part: "01"
chapter: workstation-changes
topic: workstation-changes
last_verified: 2026-11-16
status: current
---

# Workstation changes, November 2026

What changed on the primary workstation between the 2026-10-28 snapshot and 2026-11-16, and why. The package records in [`host-snapshot/`](host-snapshot/README.md) hold the result; this chapter holds the reasons and the way back. Explicitly installed packages went from 324 to 280.

## Defaults

| Setting | Now | Was | Where it lives |
|---|---|---|---|
| Web browser | Google Chrome (2026-11-14) | Brave | `mimeapps.list`, `BROWSER=google-chrome-stable` in `uwsm/env` and `.zshrc` |
| Opens text and source files | Sublime Text (2026-11-16) | Zed | `mimeapps.list` |
| `$EDITOR` and `$VISUAL` | Neovim | Neovim (unchanged by choice) | `.zshrc` |
| Opens images | Swash | Swash | `mimeapps.list` |
| Screenshots | grim, slurp and Satty, Swash as fallback | same | `hypr/scripts/screenshot.sh` |

`mimeapps.list` is now a seed in [`manifest.conf`](../../manifest.conf), so `./install.sh pull` captures a default changed on the machine. Brave stays installed; PDF, XML and RSS now open in Chrome too. Only `ipfs://` and `ipns://` still resolve to Brave.

## Removed

Every package below was removed with `pacman -Rns`. The owner chose the first rows; the "idle" rows were removed because nothing used them: no config or data in the home directory, no running clients.

| Group | Packages | Reason |
|---|---|---|
| Browsers | firefox, chromium | Chrome, Brave and Zen cover the need; Firefox sync holds the data |
| Editors and IDEs | visual-studio-code-bin, pycharm-community-edition, micro, cachyos-micro-settings | Sublime, Zed and Neovim remain |
| Notes, tasks | anytype-bin, todoist-appimage, logseq-desktop-bin | Obsidian is the vault in use |
| Office, PDF | onlyoffice-bin, okular | LibreOffice stays; Chrome opens PDFs |
| Mail, calendar, chat | thunderbird, korganizer, telegram-desktop | Mailspring stays |
| Media | strawberry, obs-studio | mpv and VLC stay |
| Passwords, VPN | keepassxc, bitwarden, proton-vpn-gtk-app, mullvad-vpn-bin, mullvad-vpn-daemon-bin | owner choice; Mullvad's daemon was never enabled, and gnome-keyring is the Secret Service |
| Graphics | gimp, inkscape, blender, cachyos-benchmarker | cachyos-benchmarker requires blender |
| Tools | meld, yazi | owner choice |
| Infrastructure as code | terraform, pulumi | OpenTofu stays |
| Bar and AUR helpers | waybar, claudebar, pamac-aur, libpamac-aur, shelly, hyfetch | Noctalia is the bar; yay and paru stay |
| Idle databases | mongodb-bin, mongosh-bin, mongodb-compass-bin, mariadb, valkey | no clients and about 450 MB of RAM held; MongoDB and Valkey were empty, MariaDB held one database named `dev` (see open items) |
| Idle cloud tools | ansible, azure-cli, aws-cli-v2, act | no credentials directory, no shell history |
| Idle desktop tools | dbeaver, copyq, mission-center, kdiskmark | never launched |
| Idle servers | sddm, netctl, fail2ban, nginx, prometheus, dnscrypt-proxy, nfs-utils, gitlab-runner | none enabled; greetd is the login manager |
| 32-bit libraries | lib32-mesa, lib32-opencl-mesa, lib32-vulkan-radeon, lib32-libxcrypt-compat | no Steam or Wine |
| Fonts | ttf-meslo-nerd, ttf-jetbrains-maple-mono-nf-xx-xx, ttf-jetbrains-maple-mono-xx-xx-ht, ttf-fragment-mono, otf-fragment-mono, ttf-bitstream-vera | no config references them |
| Local AI | ollama, ollama-rocm, ollama-vulkan, hip-runtime-amd, hipblas, rocblas, rocsolver, rocminfo, rocm-smi-lib, openai-codex | no models installed, no clients |

## Installed

| Package | Source | Note |
|---|---|---|
| zen-browser-bin | CachyOS repo | Firefox-based browser, installed 2026-11-11 |

## Kept on purpose

| Package | Why |
|---|---|
| vlc, cpu-x, kubectl, k9s, helm, minikube | owner choice |
| gnome-text-editor, qview | hard dependencies of `cachyos-hypr-noctalia`, the desktop meta-package |
| opentofu | the one infrastructure-as-code tool |

A few small tools were marked as explicitly installed before the removals so the dependency sweep would not take them: whois, systemd-resolvconf, xorg-xauth, perf, lsof, 7zip, bc, time, zenity, dos2unix, xorg-xrandr, wireguard-tools, qt6-imageformats, gst-plugins-base and gst-plugins-good.

## Services and runtimes

| Item | State |
|---|---|
| Root Docker daemon (`docker.service`, `docker.socket`, `containerd.service`) | disabled; the rootless daemon is the one in use |
| mongodb, mariadb, ollama services | disabled with their packages |
| Node.js | 26 is the default through nvm, with 24 installed beside it, so `.nvmrc` files naming 26 work |
| PostgreSQL | 18 with pgvector; demo database in [`06-tools/pgvector-demo/`](../../06-tools/pgvector-demo/README.md) |

## Configuration changes

| Change | File | Reason |
|---|---|---|
| `render.cm_auto_hdr = 0` | `hypr/config/look.lua`, `variables.conf` | entering fullscreen on Brave or Chrome forced an HDR modeset on the DisplayPort monitor and blanked the screen |
| `misc.allow_session_lock_restore = true` and `hypr/scripts/lock.sh` | `look.lua`, `variables.conf`, `hypridle.conf`, `keybinds.*` | waking the monitor after a long DPMS-off removes and re-adds the output, which aborts `hyprlock` and left the permanent lock-crashed screen |
| `special_scale_factor` removed from `dwindle` and `master` | `look.lua`, `variables.conf` | deprecated in Hyprland 0.57 and already inert |

## Open items

| Item | Detail |
|---|---|
| `/var/lib/mysql` | MariaDB's data directory still holds a database named `dev`; delete it only after confirming it is unwanted |
| Rootless Docker unit | `~/.config/systemd/user/docker.service` carries a `PATH` frozen at setup time with stale entries; regenerate it with `dockerd-rootless-setuptool.sh install` |

## Undo

Reinstall any group with `sudo pacman -S --needed` and the names from the table above. The hardware-specific local AI set is still described in [`packages/ai.txt`](packages/ai.txt) and [`05-ai/ollama/`](../../05-ai/ollama/README.md).
