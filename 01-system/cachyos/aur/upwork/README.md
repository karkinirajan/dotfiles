# Upwork Local PKGBUILD (`5.8.0.41`)

Reproducible Arch/CachyOS package recipe that repackages Upwork's official
Debian binary archive (`upwork_5.8.0.41_amd64.deb`) with its bundled runtime.

## Why not the AUR `upwork` package?

The upstream AUR `upwork` recipe attempts to rebuild Electron/Chromium wrapper
layers and can trigger multi-hour source compilations or Electron ABI mismatches
on rolling CachyOS updates. Extracting the official `.deb` directly is fast,
deterministic, and matches the vendor-tested binary.

## Build and install

Ensure the official `upwork_5.8.0.41_amd64.deb` installer is placed in this
directory (matching the `sha256sums` in [`PKGBUILD`](PKGBUILD)), then run:

```sh
cd ~/dotfiles/01-system/cachyos/aur/upwork
makepkg -si
```

> [!NOTE]
> Upwork's desktop time tracker requires an Xorg session for periodic desktop
> screenshots. It launches on Wayland/Hyprland for chat and contract management,
> but active time-tracking screenshot capture is not supported under Wayland.
