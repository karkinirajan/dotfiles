# Timeshift

Daily btrfs snapshots of `/`, keeping exactly one. Each new daily snapshot
replaces the previous one (`count_daily: 1` in `/etc/timeshift/timeshift.json`).

Snapshots are btrfs subvolumes on the same partition as `/`
(`/dev/nvme0n1p5`), so they protect against bad updates and config mistakes,
not against disk failure. `/home` is excluded.

## Files

- `timeshift-daily.service` / `timeshift-daily.timer` — runs `timeshift --check`
  once a day. Timeshift's own schedule (`schedule_daily`) does the real work;
  the timer only triggers it. Root-owned, so copied by hand (not linked by
  `install.sh`).

## Install

```sh
sudo cp tools/timeshift/timeshift-daily.service tools/timeshift/timeshift-daily.timer /etc/systemd/system/
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
