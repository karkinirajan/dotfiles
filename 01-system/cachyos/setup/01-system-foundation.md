---
title: "01 System Foundation and Optimization"
part: "01"
chapter: "01"
topic: system-foundation
versions: [cachyos-iso, cachyos-kernel, btrfs-progs]
last_verified: 2026-10-29
status: current
sources:
  - https://wiki.cachyos.org/cachyos_basic/download/
  - https://github.com/CachyOS/CachyOS-Settings
  - https://github.com/CachyOS/CachyOS-PKGBUILDS/tree/master/cachyos-rate-mirrors
  - https://btrfs.readthedocs.io/en/latest/Swapfile.html
---

# 01 System Foundation and Optimization

## Purpose

The state of a fresh CachyOS install that every later chapter assumes: the vendor tuning package, the kernel, swap, mirrors. CachyOS already ships good defaults; this chapter records what they are so nothing is overridden by accident.

## Prerequisites

- A CachyOS install from the desktop ISO (release <!-- v:cachyos-iso -->260809<!-- /v -->), UEFI, Limine, Btrfs. Verification and install choices are in [`fresh-setup.md`](../../../fresh-setup.md).
- Optimized repositories enabled (`cachyos-v3`, `cachyos-core-v3`, `cachyos-extra-v3`, `cachyos`, then Arch). A Ryzen 5 5600 is Zen 3, so the `v3` set is correct.

## 1.1 CachyOS post-install settings

`cachyos-settings` carries the sysctl tweaks, I/O scheduler rules, the ZRAM generator config and audio power rules. It depends on `zram-generator`, `ananicy-cpp`, `cachyos-ananicy-rules`, `inxi`, `iw` and `wireless-regdb`, so one package pulls the rest. `ananicy-cpp` adjusts process priorities for desktop responsiveness.

```bash
sudo pacman -S --needed cachyos-settings
sudo systemctl enable --now ananicy-cpp.service
```

Label: `machine-only`. Proof: `systemctl is-active ananicy-cpp` prints `active`.

## 1.2 Developer sysctl tweaks

The vendor file `/usr/lib/sysctl.d/70-cachyos-settings.conf` sets swappiness 100, `vfs_cache_pressure` 50, dirty-page limits, `nmi_watchdog` 0, `sysrq` 1 and others. It sets none of the keys below, so a drop-in does not conflict:

```ini
# /etc/sysctl.d/99-developer.conf
# Network buffers and TCP Fast Open for API development
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_fastopen = 3

# File watchers for editors and bundlers
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 512
```

```bash
sudo sysctl --system   # apply without reboot
```

Why these values: the kernel default for `inotify.max_user_instances` is 128 and `max_user_watches` is about 1 percent of RAM clamped to 8192..1048576; `tcp_fastopen` defaults to 1 (client only) and 3 enables client and server. Label: `machine-only`. Proof: `sysctl fs.inotify.max_user_watches` prints `524288`.

## 1.3 ZRAM

CachyOS enables ZRAM by default and `cachyos-settings` configures it. The vendor file `/usr/lib/systemd/zram-generator.conf` is:

```ini
[zram0]
compression-algorithm = zstd
zram-size = ram
swap-priority = 100
fs-type = swap
```

On this 32 GiB machine that is one zstd device of about 31.3 GiB. A udev rule from the same package sets `vm.swappiness=150` for ZRAM and turns zswap off. Do not create `/etc/systemd/zram-generator.conf`: files under `/etc` override the vendor file, and a smaller example such as `zram-size = min(ram, 8192)` would cut swap from about 31 GiB to 8 GiB.

Check without changing anything:

```bash
zramctl                                   # one /dev/zram0, about 31.3G, zstd
cat /usr/lib/systemd/zram-generator.conf
```

Label: `machine-only`.

**Optional swapfile on SSD** for extremely heavy workloads. Put it in its own Btrfs subvolume: Btrfs cannot snapshot a subvolume that holds an active swapfile, and Snapper snapshots the root subvolume. `mkswapfile` needs btrfs-progs 6.1 or newer (<!-- v:btrfs-progs -->7.3<!-- /v --> is current).

```bash
sudo btrfs subvolume create /swap
sudo btrfs filesystem mkswapfile --size 8G /swap/swapfile
sudo swapon /swap/swapfile
echo '/swap/swapfile none swap defaults 0 0' | sudo tee -a /etc/fstab
sudo snapper -c root create -d swap-test      # must succeed with swap active
```

Label: `machine-only`. Source: [Btrfs swapfile docs](https://btrfs.readthedocs.io/en/latest/Swapfile.html).

## 1.4 Mirror optimization

Use `cachyos-rate-mirrors` only. It ranks and writes `/etc/pacman.d/mirrorlist` (Arch) and `/etc/pacman.d/cachyos-mirrorlist`, derives `cachyos-v3-mirrorlist` and `cachyos-v4-mirrorlist` from it, picks the country from IP geolocation (override with `RATE_MIRRORS_ENTRY_COUNTRY` in `/etc/conf.d/cachyos-rate-mirrors.env`), and its package enables `cachyos-rate-mirrors.timer` (runs on the 1st, 11th and 21st of each month).

```bash
sudo cachyos-rate-mirrors
systemctl list-timers cachyos-rate-mirrors.timer
```

Do not combine it with `reflector`: both write `/etc/pacman.d/mirrorlist`, and the `cachyos-rate-mirrors` package ships a pacman hook that disables `reflector.timer` whenever `reflector` is installed or upgraded. Label: `machine-only`. Proof: the three mirror lists are rewritten and `reflector.timer` is disabled.

## Verify

```bash
uname -r
pacman-conf --repo-list
/lib/ld-linux-x86-64.so.2 --help | grep supported
```

Expected: `uname -r` starts with <!-- v:cachyos-kernel -->7.3.0<!-- /v --> and ends in `-cachyos`; the repo list is `cachyos-v3`, `cachyos-core-v3`, `cachyos-extra-v3`, `cachyos`, then the Arch repos; the loader line shows `x86-64-v3 (supported, searched)`.

## Version

Kernel `linux-cachyos` <!-- v:cachyos-kernel -->7.3.0<!-- /v --> (CachyOS v3 repo; the generic `cachyos` repo still carries 7.2.7). Upstream Linux 7.3 was released on 2026-10-18 and is not an LTS line.

## Sources

- [CachyOS download verification](https://wiki.cachyos.org/cachyos_basic/download/)
- [CachyOS-Settings](https://github.com/CachyOS/CachyOS-Settings) (zram generator config, sysctl defaults)
- [cachyos-rate-mirrors](https://github.com/CachyOS/CachyOS-PKGBUILDS/tree/master/cachyos-rate-mirrors)
- Ledger: cluster C1, topics `mirrors`, `cachyos-settings`, `cachyos-iso` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
