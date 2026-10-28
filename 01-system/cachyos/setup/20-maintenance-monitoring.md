---
title: "20 System Maintenance and Monitoring"
part: "01"
chapter: "20"
topic: maintenance-monitoring
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 20 System Maintenance and Monitoring


## 20.1 Btrfs Snapshots — Snapper + Limine

This CachyOS installation uses Limine, not GRUB. `snap-pac` and Snapper create
and retain filesystem snapshots; `limine-snapper-sync` can additionally expose
those snapshots as boot-menu entries. Use the installed Limine integration
instead of installing `grub-btrfs` or regenerating `/boot/grub/grub.cfg`.

```bash
sudo pacman -S --needed snapper snap-pac
if [[ ! -f /etc/snapper/configs/root ]]; then
  sudo snapper -c root create-config /
fi
sudo systemctl enable --now snapper-timeline.timer snapper-cleanup.timer
snapper list
```

The desired menu for this host is **only the primary CachyOS kernel** in
Limine. Do not add Windows detection, secondary kernels, fallback loaders, or
snapshot entries to its menu. Snapshots remain available to `snapper`; they
should not be exposed as boot choices for this profile.

Limine menu entries live in `/boot/limine.conf`; kernel entries are managed by
`limine-entry-tool`, and `/etc/default/limine` overrides its options. Before
changing a live menu, back up the config, inspect the exact entry paths with
`limine-list`, then remove only the unwanted entries using
`limine-entry-tool --remove-entry`. Disable `limine-snapper-sync.service` if
snapshot entries must stay absent, and set `FIND_BOOTLOADERS=no` in
`/etc/default/limine` to stop discovery of fallback EFI loaders. Rebuild with
`sudo limine-update` and verify `limine-list` shows the single CachyOS entry
before rebooting. Do not remove the currently booted kernel or its initramfs.

On this host, the live cleanup is complete. `limine-list` shows only
`CachyOS → linux-cachyos`; LTS and real-time kernel packages are removed,
`limine-snapper-sync.service` is disabled, and `/etc/default/limine` sets
`BOOT_ORDER="linux-cachyos"` and `FIND_BOOTLOADERS="no"`. Snapper snapshots
and the EFI fallback files remain on disk, but are not Limine menu entries.
The generated config defaults directly to `CachyOS/linux-cachyos` and does
not remember another entry. See `system-summary.md` for the full current state.

## 20.2 System Monitoring

```bash
sudo pacman -S btop nvtop mission-center ncdu
```

| Tool | Purpose |
|---|---|
| `btop` | Full system TUI monitor (CPU, RAM, disk, network) |
| `nvtop` | GPU process monitor (supports AMD despite the name) |
| `mission-center` | GTK4 GUI system monitor (like Windows Task Manager) |
| `ncdu` | Interactive disk usage browser |
| `dust` | Visual proportional disk usage (already in CLI tools) |
| `amdgpu_top` | Modern TUI with per-process GPU usage |

## 20.3 Package Cache Cleanup

```bash
sudo pacman -S pacman-contrib
sudo paccache -r             # Keep last 3 versions
sudo paccache -ruk0          # Remove all uninstalled package cache
sudo systemctl enable --now paccache.timer   # Weekly auto-cleanup
```

## 20.4 Mirror Optimization

```bash
sudo pacman -S reflector
sudo reflector --country 'NP,IN,SG' --age 12 --protocol https --sort rate \
  --save /etc/pacman.d/mirrorlist
sudo pacman -S cachyos-rate-mirrors && sudo cachyos-rate-mirrors
sudo systemctl enable --now reflector.timer
```

## 20.5 Update Strategy

Full auto-updates are risky on Arch. CachyOS provides `cachy-update` for interactive reviews:

```bash
# Best practice: review updates → verify snapper has recent snapshot → apply → reboot after kernel updates
paru -Syu   # or use the cachy-update systray notifier
```
