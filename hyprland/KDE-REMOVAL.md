# KDE/Plasma Removal Notes

This machine originally ran CachyOS with a full KDE Plasma install alongside
Hyprland (dual-DE setup, common on CachyOS installs). This document records
how it was fully removed, keeping Hyprland/Noctalia intact, for anyone
following these dotfiles onto a similar dual-DE CachyOS install — or for
re-doing this after a fresh CachyOS-with-Plasma install.

**Result**: 205 packages removed across three passes, zero KDE/Plasma-tagged
packages remain, Hyprland and Noctalia untouched throughout (same PIDs
before and after every transaction).

## Two landmines found before removing anything

1. **`dolphin` was a hard dependency of `cachyos-hypr-noctalia`** — the
   meta-package CachyOS uses to bundle this exact Hyprland+Noctalia setup.
   `pacman -Qi dolphin` showed `Required By: cachyos-hypr-noctalia
   dolphin-plugins`. Removing Dolphin meant also removing that meta-package.

   Checking `cachyos-hypr-noctalia`'s own dependency list
   (`pacman -Qi cachyos-hypr-noctalia`) showed it depends on Hyprland/Noctalia
   (not the other way around) and nothing requires it — so removing *it* is
   safe. But several of *its* other dependencies (things it merely bundles,
   not KDE at all) had no other anchor and would have been swept away as
   orphans in the same transaction:
   `xdg-desktop-portal-hyprland`, `uwsm`, `brightnessctl`, `satty`,
   `nwg-look`, `gnome-text-editor`, `gnome-calculator`,
   `cachyos-alacritty-config`, `adw-gtk-theme`, `xcur2png`, `xorg-xhost`.

   **Fix**: mark those explicit *before* removing the meta-package, so
   pacman's orphan detection leaves them alone:
   ```sh
   sudo pacman -D --asexplicit xorg-xhost xdg-desktop-portal-hyprland uwsm \
     satty nwg-look xcur2png gnome-text-editor gnome-calculator \
     cachyos-alacritty-config brightnessctl adw-gtk-theme
   ```
   Always dry-run first (`pacman -Rsp <targets>`) and grep the output against
   this protect-list before actually removing anything.

2. **`plasmalogin.service` was the active login manager.** Removing
   `plasma-login-manager` without a working replacement already in place
   would have meant no graphical login at all next boot.

   **Fix**: switch to SDDM (already installed, just disabled) *before*
   removing anything, and verify a real reboot + login actually works:
   ```sh
   sudo mkdir -p /etc/sddm.conf.d
   # content: sddm/hyprland.conf in this repo
   sudo cp sddm/hyprland.conf /etc/sddm.conf.d/hyprland.conf
   sudo systemctl enable sddm.service
   sudo systemctl disable plasmalogin.service
   ```
   **Gotcha hit here**: if `/etc/systemd/system/display-manager.service`
   already exists as a symlink to the old display manager,
   `systemctl enable sddm.service` fails *silently in effect* — it errors
   with `File ... already exists and is a symlink to
   .../plasmalogin.service`, and if you then disable the old one without
   noticing that error, the symlink gets removed entirely and **neither**
   display manager is enabled — worse than before, since now nothing starts
   graphically at all. Check `readlink -f
   /etc/systemd/system/display-manager.service` points at `sddm.service`
   after enabling, not just that the enable command didn't visibly explode.
   Reboot and confirm an actual login before touching any KDE package.

## The three removal passes

Each pass: build the target list from `pacman -Qe | grep -iE
'plasma|^kde|...'` (explicitly-installed KDE-tagged packages), dry-run with
`pacman -Rsp`, check the dry-run output against the protect-list above,
adjust, re-dry-run, then execute for real with `pacman -Rs`.

**Pass 1** (148 packages): the meta-package plus the whole explicit-install
KDE/Plasma surface — `plasma-desktop`, `plasma-workspace` (pulled in once
its last two anchors, `powerdevil` and `xdg-desktop-portal-kde`, were added
to the target list), `kwin`, `dolphin`, `okular`, `ark`, `spectacle`,
`partitionmanager`, `kwallet-pam`, `kwalletmanager`, `bluedevil`,
`kinfocenter`, the three `cachyos-*-kde-theme` packages, `qt6ct-kde`, and
everything else only *they* depended on (kdeclarative, kio, kwindowsystem's
whole dependent tree, baloo, signon/kaccounts stack, poppler/ghostscript for
kdegraphics thumbnailers, etc.) — none of it had any dependent outside this
graph.

**Pass 2** (52 packages): a handful of Qt/KDE framework libraries that
survived pass 1 because something else still needed them —
`hyprqt6engine` ("QT6 Theme Provider for Hyprland", genuinely part of this
Hyprland setup, not KDE) was still pulling in `kiconthemes` →
`kwindowsystem`/`kwallet`/`kio` and their own dependents (`kcalc`,
`kvantum-theme-nordic-git`, `crow-translate`, `plymouth-kcm`,
`kdenetwork-filesharing` → `samba`, etc.). This was an explicit choice, not
automatic — removing `hyprqt6engine` trades away consistent Qt-app
icon-theming under Hyprland for a truly KDE-free system. Verified `samba`
was `disabled`/`inactive` (installed only for KDE's file-sharing GUI, never
actually running) before including it.

**Pass 3** (4 packages): `pacman -Qtdq` after pass 2 listed 37 orphans, but
**most of that list was not KDE** — `mako`, `grimblast-git`, `wob`,
`wlogout`, `pamixer`, `network-manager-applet`, various unrelated `python-*`
packages, fonts, vulkan libs. Blanket-removing "all orphans" would have
broken things this setup actively depends on (`mako`'s package is kept
deliberately — see the main README's D-Bus override note — and
`grimblast-git`/`wob` are wired into `keybinds.conf`/`autostart.conf`
directly). Only `kdoctools` (+ its own now-orphaned deps `karchive`,
`docbook-xsl`, `docbook-xml`) was actually KDE; removed that one
specifically, left the rest of the orphan list alone.

**Lesson for next time**: never run `pacman -Rns $(pacman -Qtdq)` blind on a
system with a curated Hyprland setup like this one. Always read the orphan
list before touching it — most of what shows up there long after a big
removal has nothing to do with what you just removed.

## Leftover home-directory config/cache (packages ≠ user data)

`pacman -Rs` only removes the packages — it never touches `~/.config`,
`~/.local/share`, or `~/.cache`. A KDE-heavy home directory leaves a *lot*
behind: `dolphinrc`, `konsolerc`, `kwinrc`, `plasma*rc`, `~/.config/kdeglobals`,
`~/.local/share/{plasma,dolphin,baloo,akonadi,kwalletd,kwin}`,
`~/.cache/{plasmashell,kwin,spectacle,plasma_theme_*.kcache}`, and more.
None of it is needed once the software is gone.

**Two categories needed a judgment call, not a blind `rm -rf`:**
- `~/.local/share/kwalletd` (KWallet's encrypted secret store) — could hold
  real saved credentials (wifi passwords, app secrets). Only delete this if
  you're sure nothing there needs recovering; the data becomes unusable the
  moment the `kwallet` package is gone anyway, since nothing can read it.
- `~/.local/share/akonadi` (KDE PIM backend — email/contacts/calendar,
  ~100MB+, mostly its own embedded MySQL/MariaDB instance) — check
  `~/.config/akonadi_*resource*rc` for real configured accounts before
  assuming it's just default first-run scaffolding.

**A stale process gotcha, same shape as the Hyprland-restart issue above**:
`kwalletd6` was still running *after* the `kwallet` package was removed —
its binary was deleted from disk but the already-running process kept going
(and kept re-touching its own state directory, meaning `rm -rf
~/.local/share/kwalletd` looked like it silently came back). `pkill
kwalletd6` (or just reboot) before doing a final check.

**Two `exec-once` lines in `autostart.conf` silently die once their
packages are gone**, and are easy to miss since Hyprland doesn't error
loudly on a failed exec-once:
- `polkit-kde-authentication-agent-1` → replaced with **hyprpolkitagent**
  (already installed as a dependency of something else, just never
  autostarted) — enabled as its own systemd `--user` service instead of
  another `exec-once`, since it ships one and isn't a launcher whose
  children would inherit a service's cgroup (unlike the Noctalia case this
  same repo works around with `noctalia-watchdog.sh`):
  ```sh
  systemctl --user enable --now hyprpolkitagent.service
  ```
- `kwalletd6` + `pam_kwallet_init` (KWallet PAM auto-unlock) — just deleted
  outright once `kwallet` itself is gone; nothing to replace it with unless
  you specifically want a secret-storage daemon again (`gnome-keyring` is
  the usual non-KDE choice).
