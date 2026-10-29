# Timeshift (Archived)

> [!IMPORTANT]
> **Archived, not the active snapshot system.** This CachyOS workstation uses
> Snapper (`snapper`, `cachyos-snapper-support`, `snap-pac`) for Btrfs root
> snapshots. `timeshift` conflicts with `cachyos-snapper-support` and is not
> installed on the live host. Do not install or enable anything in this
> directory unless intentionally replacing Snapper with Timeshift.

This directory documents Timeshift as an alternative snapshot setup. On
CachyOS, check whether `cachyos-snapper-support` is installed before choosing
Timeshift: the two packages conflict and cannot be installed together. Configure
Timeshift's snapshot policy and create an initial snapshot before enabling the
daily timer. The timer only runs `timeshift --check`; Timeshift's own
configuration controls whether that check creates a snapshot and retention.
Install Timeshift only after choosing it instead of the Snapper packages:
`sudo pacman -S timeshift`.

On a Btrfs root, snapshots are subvolumes on the same filesystem. They can help
recover from bad updates and config mistakes, but do not protect against disk
failure. Choose whether to include `/home` in Timeshift's setup.

## Files

- `timeshift-daily.service` / `timeshift-daily.timer`, runs `timeshift --check`
  once a day. Root-owned, so copied by hand (not linked by `install.sh`).

## Install

```sh
sudo install -Dm644 01-system/timeshift/timeshift-daily.service /etc/systemd/system/timeshift-daily.service
sudo install -Dm644 01-system/timeshift/timeshift-daily.timer /etc/systemd/system/timeshift-daily.timer
sudo systemctl daemon-reload
sudo systemctl enable --now timeshift-daily.timer
```

Optional first snapshot now:

```sh
sudo timeshift --create --comments "baseline" --tags D
```

## Check

```sh
systemctl list-timers timeshift-daily.timer
sudo timeshift --list
```
