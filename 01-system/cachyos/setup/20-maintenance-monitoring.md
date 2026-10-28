---
title: "20 System Maintenance and Monitoring"
part: "01"
chapter: "20"
topic: maintenance-monitoring
versions: [snapper, limine, btrfs-progs, paru]
last_verified: 2026-10-29
status: current
sources:
  - https://github.com/CachyOS/CachyOS-PKGBUILDS
  - https://gitlab.com/Zesko/limine-entry-tool
  - https://btrfs.readthedocs.io/
  - https://wiki.cachyos.org/
---

# 20 System Maintenance and Monitoring

## Purpose

Keep a rolling system recoverable: Btrfs snapshots, the Limine boot menu, monitoring, cache cleanup and an update routine that makes a bad update reversible.

## Prerequisites

- Btrfs root with the CachyOS subvolume layout ([chapter 01](01-system-foundation.md)).
- CachyOS repos enabled. Package versions: Snapper <!-- v:snapper -->0.13.2<!-- /v -->, Limine <!-- v:limine -->12.9.4<!-- /v --> from the CachyOS repo (Arch extra already has 12.9.6).

## 20.1 Btrfs snapshots: Snapper and Limine

This installation uses Limine, not GRUB. `snap-pac` and Snapper create and retain filesystem snapshots on every pacman transaction; `limine-snapper-sync` can additionally expose those snapshots as boot-menu entries. Use the Limine integration instead of `grub-btrfs` or regenerating `/boot/grub/grub.cfg`.

`cachyos-snapper-support` (depends on `snapper` and `snap-pac`, conflicts with `timeshift`) creates the `root` config from its `cachyos-root` template and enables `snapper-cleanup.timer`. The template sets `TIMELINE_CREATE="no"`, `NUMBER_LIMIT="50"` and `NUMBER_LIMIT_IMPORTANT="15"`, and it leaves `snapper-timeline.timer` off: the timeline timer only does something if you set `TIMELINE_CREATE="yes"`.

```bash
sudo pacman -S --needed cachyos-snapper-support btrfs-assistant
sudo snapper -c root get-config | grep -E 'TIMELINE_CREATE|NUMBER_LIMIT'
sudo systemctl enable --now snapper-cleanup.timer
snapper list
```

For a plain Arch install without `cachyos-snapper-support`, create the config first (`sudo snapper -c root create-config /`) and install `snap-pac`.

**Boot menu policy for this host.** Only the primary CachyOS kernel appears in Limine. Windows detection, secondary kernels, fallback loaders and snapshot entries are not in the menu; snapshots stay available to `snapper`.

Limine entries live in `/boot/limine.conf`; `limine-entry-tool` manages them and `/etc/default/limine` overrides its options. To get a single-entry menu:

1. Back up `/boot/limine.conf` and `/etc/default/limine` (`sudo cp -a`), note the booted kernel with `uname -r`, then inspect the exact entry paths with `sudo limine-list`.
2. Remove the other kernel packages (`linux-cachyos-lts`, `linux-rt`, and their headers) so their entries are not regenerated. The installer ships the Stable and LTS kernels, so removing LTS leaves no fallback kernel; `linux-cachyos-lts` stays available in the repo if one is wanted.
3. Set `FIND_BOOTLOADERS="no"` in `/etc/default/limine` to stop discovery of other EFI loaders. `BOOT_ORDER` only orders entries (default `"*, *fallback, Snapshots"`, sorting applies only when `ENABLE_SORT=yes`); it is not documented as a filter. <!-- UNVERIFIED: whether BOOT_ORDER hides unlisted entries -->
4. Disable `limine-snapper-sync.service` so snapshot entries stay absent.
5. Remove any remaining stale path with `limine-entry-tool --remove-entry <path>`, run `sudo limine-update`, and confirm `sudo limine-list` shows the single entry. Never remove the booted kernel (compare with `uname -r`) or its initramfs, and double-check the argument: `--remove-entry` with position 0 removes every match.

Limine 12.9.5 changed `default_entry:` numbering (a number now starts at 1) and 12.9.6 requires global options before the first entry. The path form `default_entry: CachyOS/linux-cachyos` and `remember_last_entry: no` are unaffected. Whether manual `default_entry` edits survive `limine-update` is not documented: re-check after each kernel update. <!-- UNVERIFIED -->

On the primary host the cleanup is done: `limine-list` shows only `CachyOS → linux-cachyos`, `limine-snapper-sync.service` is disabled, `/etc/default/limine` sets `BOOT_ORDER="linux-cachyos"` and `FIND_BOOTLOADERS="no"`, and the generated config defaults to `CachyOS/linux-cachyos`. See [`system-summary.md`](../../../system-summary.md).

**Btrfs health.** Snapshots live on the same disk and do not protect against disk failure. Scrub roughly monthly with a read-only check, and never run `btrfs check --repair` as routine maintenance:

```bash
sudo btrfs scrub start -B -r /
sudo btrfs scrub status /
```

Label for this section: `machine-only`. Proof: `snapper list` shows pre/post pairs after a pacman transaction; scrub status reports 0 errors.

## 20.2 System monitoring

```bash
sudo pacman -S --needed btop nvtop mission-center ncdu
```

| Tool | Purpose |
|---|---|
| `btop` | Full system TUI monitor (CPU, RAM, disk, network) |
| `nvtop` | GPU process monitor (supports AMD despite the name) |
| `mission-center` | GTK4 GUI system monitor |
| `ncdu` | Interactive disk usage browser |
| `dust` | Proportional disk usage (in the CLI package list) |
| `amdgpu_top` | TUI with per-process GPU usage |

`prometheus` is in `packages/developer.txt` but is not enabled. Its default listen address is `0.0.0.0:9090`, so bind it to loopback before enabling it: in `/etc/conf.d/prometheus` set `PROMETHEUS_ARGS="--web.listen-address=127.0.0.1:9090"`. <!-- UNVERIFIED: the Arch unit reads /etc/conf.d/prometheus (Arch package files were only readable through old snippets) -->

## 20.3 Package cache cleanup

```bash
sudo pacman -S --needed pacman-contrib
sudo paccache -r             # keep the last 3 versions
sudo paccache -ruk0          # remove the cache of uninstalled packages
sudo systemctl enable --now paccache.timer   # weekly cleanup
```

## 20.4 Mirrors

Covered once, in [chapter 01, section 1.4](01-system-foundation.md#14-mirror-optimization): use `cachyos-rate-mirrors` and do not add `reflector`.

## 20.5 Update strategy

Full auto-updates are risky on a rolling distribution. Update interactively, always as a full upgrade (never `pacman -Sy <pkg>`), and handle `.pacnew` files.

```bash
# review Arch news → confirm a recent snapper snapshot → apply → reboot after kernel updates
sudo snapper -c root list | tail -3
paru -Syu          # or topgrade (see 01-system/topgrade), or the cachy-update systray notifier
```

CachyOS ships `shelly` as its default GUI package manager and `cachy-update` (systray notifier). `topgrade` with the tracked config wraps `paru`, does not pass `--noconfirm`, and lists `.pacnew` files after the run. Label: `machine-only`.

## Verify

```bash
snapper --version
sudo limine-list
systemctl is-enabled snapper-cleanup.timer
```

Expected: Snapper <!-- v:snapper -->0.13.2<!-- /v -->; `limine-list` shows exactly the intended entries; the cleanup timer is `enabled`.

## Sources

- [CachyOS-PKGBUILDS](https://github.com/CachyOS/CachyOS-PKGBUILDS) (`cachyos-snapper-support`)
- [limine-entry-tool README](https://gitlab.com/Zesko/limine-entry-tool)
- [Btrfs documentation](https://btrfs.readthedocs.io/)
- Ledger: cluster C1, topics `limine`, `snapper`, `btrfs` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
