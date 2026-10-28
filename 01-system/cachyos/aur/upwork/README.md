# Upwork Local PKGBUILD (`5.8.0.41`)

Reproducible Arch/CachyOS package recipe that repackages Upwork's official
Debian binary archive (`upwork_5.8.0.41_amd64.deb`) with its bundled runtime.

## Why not the AUR `upwork` package?

The AUR `upwork` recipe (5.8.0.41-5, last updated 2026-03-17) uses the same
`.deb` but depends on `electron36` (with `electron36-bin` as an alternative, so
no compile is needed) and replaces the bundled runtime with it. Electron 36
reached end of life on 2025-10-27 and is not in the Arch repositories, which
ship electron39, 40 and 44. Extracting the official `.deb` directly is fast,
deterministic, and matches the vendor-tested binary.

Neither choice is current: the vendor bundle carries an old Electron (an AUR
comment reports `Electron/18.3.15` for 5.8.0.33; the runtime in 5.8.0.41 was
not read) and the AUR build runs an end-of-life Electron 36. This recipe also
leaves Upwork's self-update enabled. <!-- UNVERIFIED: bundled Electron version of 5.8.0.41; check on the host with `ar x upwork_5.8.0.41_amd64.deb; bsdtar -xf data.tar.xz; strings opt/Upwork/upwork | grep -m1 Electron/` -->

## Build and install

Upwork's download host sits behind a web application firewall that refused
the research environment (HTTP 403), so a plain `makepkg` download may fail.
Download the official `upwork_5.8.0.41_amd64.deb` in a browser from
<https://www.upwork.com/ab/downloads/?os=linux>, place it in this directory
(it must match the `sha256sums` in [`PKGBUILD`](PKGBUILD)), then run:

```sh
cd ~/dotfiles/01-system/cachyos/aur/upwork
makepkg -si
```

> [!NOTE]
> Upwork's support page names only "Ubuntu on Xorg" for the time tracker's
> periodic screenshots. It launches on Wayland/Hyprland for chat and contract
> management, but screenshot capture is not supported under Wayland. Whether an
> Xorg session on Arch satisfies Upwork's support terms is not stated, and
> keystroke counts under XWayland are reported wrong by a third-party README.
> <!-- UNVERIFIED: Upwork support position on non-Ubuntu Xorg sessions -->

After building, run `namcap PKGBUILD` and `namcap upwork-*.pkg.tar.zst`; expect
warnings about bundled libraries. Label: `machine-only`.
