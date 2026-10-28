---
title: "01 System Foundation and Optimization"
part: "01"
chapter: "01"
topic: system-foundation
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 01 System Foundation and Optimization


## 1.1 CachyOS Post-Install Settings

CachyOS ships `cachyos-settings` with sysctl tweaks, I/O scheduler rules, ZRAM config, and audio power management. `ananicy-cpp` auto-adjusts process priorities for desktop responsiveness.

```bash
sudo pacman -S cachyos-settings ananicy-cpp cachyos-ananicy-rules
sudo systemctl enable --now ananicy-cpp.service
```

## 1.2 Developer sysctl Tweaks

Create `/etc/sysctl.d/99-developer.conf`:

```ini
# Network performance for API development
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_fastopen = 3

# File watchers for VS Code, webpack, etc.
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 512
```

```bash
sudo sysctl --system   # Apply without reboot
```

## 1.3 ZRAM Configuration (32GB RAM)

CachyOS enables ZRAM by default. Tune `/etc/systemd/zram-generator.conf`:

```ini
[zram0]
zram-size = min(ram, 8192)
compression-algorithm = zstd
```

**Why:** Creates an 8GB compressed swap device in RAM using zstd. When RAM fills under heavy AI workloads (Ollama + Docker + VS Code + browser), cold pages compress in RAM (~37ns) instead of hitting SSD (~100µs). Effectively gives you ~36-40GB usable memory.

**Check the live CachyOS configuration first.** The current host already has
zstd zram swap sized to about 31 GiB. See
[`dev-stack.md`](../dev-stack.md); do not replace it with the 8 GiB example
without measuring the workload and checking the distribution's configuration.

**Optional SSD swap fallback** for extremely heavy workloads (Btrfs):

```bash
sudo btrfs filesystem mkswapfile --size 8G /swap/swapfile
sudo swapon /swap/swapfile
echo '/swap/swapfile none swap defaults 0 0' | sudo tee -a /etc/fstab
```

## 1.4 Mirror Optimization

```bash
sudo pacman -S reflector cachyos-rate-mirrors
sudo reflector --country 'NP,IN,SG' --age 12 --protocol https --sort rate \
  --save /etc/pacman.d/mirrorlist
sudo cachyos-rate-mirrors
sudo systemctl enable --now reflector.timer
```
