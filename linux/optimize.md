# cachyos optimization—2026-04-19

Hardware: AMD Ryzen 5 5600 · 16GB RAM · RX 6700 XT (12GB VRAM) · 477GB NVMe (Btrfs) · CachyOS.

**Total disk reclaim**: 211GB → **120GB used** (freed **~91GB**).
**Total RAM improvement**: swappiness/watermark/OOM pressure tuned; zram doubled from 8GB → 15.5GB with ~4:1 compression → effective virtual memory roughly **~60–70GB**.

---

## 1. Memory / Swap / OOM

### zram (primary swap)

- `/etc/systemd/zram-generator.conf` → `zram-size = ram` (15.5GB), `zstd`, priority 100
- Backup of original: `/etc/systemd/zram-generator.conf.backup.20260419`

### VM sysctls (`/etc/sysctl.d/99-swappiness.conf`)

| key | value | why |
|---|---|---|
| `vm.swappiness` | 180 | prefer fast zram over cache eviction |
| `vm.page-cluster` | 0 | single-page reads (optimal for compressed swap) |
| `vm.vfs_cache_pressure` | 50 | retain filesystem metadata |
| `vm.watermark_scale_factor` | 125 | earlier reclaim, avoid allocation stalls |

### systemd-oomd (PSI-based OOM killer)

Slice drop-ins in `/etc/systemd/system/`:

- `-.slice.d/99-oomd.conf` → `ManagedOOMSwap=kill`
- `user.slice.d/99-oomd.conf` → `ManagedOOMMemoryPressure=kill`, limit 50%
- `system.slice.d/99-oomd.conf` → same

Kills worst offender when swap hits 90% OR sustained pressure >50% for 30s.

### Skipped (intentional)

- **Disk swap** — Btrfs swapfiles are fragile; 15.5GB zram is enough.
- **VRAM as swap** — unreliable, PCIe-bound, competes with GPU.

---

## 2. Backup / Snapshots

### Timeshift (rolling 1-snapshot daily)

`/etc/timeshift/timeshift.json`:

- `schedule_daily = true`, `count_daily = 1`
- All other schedules & counts = 0
- Cron hook: `/etc/cron.d/timeshift-hourly` (runs `--check --scripted` every hour)

### Snapper — fully removed

Packages removed: `snapper`, `snap-pac`, `btrfs-assistant`, `timeshift-autosnap`.
`.snapshots` subvolume gone; `/etc/snapper` deleted; leftover masked `snapper-boot.timer` unlinked.

---

## 3. Btrfs / SSD Health

- Mount opts active: `compress=zstd:1, noatime, ssd, discard=async`
- **Defrag pass** run (`btrfs filesystem defragment -r -czstd /`) → re-compressed legacy files (−13GB data block allocation).
- **`fstrim.timer`** enabled (weekly TRIM).
- **`btrfs-scrub@-.timer`** enabled (monthly data integrity check, next ~May 3).

---

## 4. Scheduled Maintenance Timers

| Unit | Schedule | What |
|---|---|---|
| `fstrim.timer` | weekly | SSD TRIM |
| `btrfs-scrub@-.timer` | monthly | bit-rot detection |
| `weekly-cache-clean.timer` | Sun 03:00 | wipe paru/yay/yarn/pip/uv/npm/pnpm/typescript/browser caches |
| `pacman-cache-clean.timer` | Sun 03:30 | `paccache -rk2 -ruk0` |
| `workspace-backup.timer` | Sun 04:00 | **INSTALLED BUT DISABLED** — awaits `rclone config` |

Unit files in `/etc/systemd/system/`.

---

## 5. Services State Changes

| Service | State | Note |
|---|---|---|
| `systemd-oomd` | enabled + active | |
| `ollama.service` | **disabled + inactive** | run `ollama serve` manually when needed |
| `psd.service` (user) | disabled | all supported browsers removed from list |
| snapper timers | uninstalled | |

---

## 6. Toolchain

### Replaced

- `nvm` (~1.9GB) → removed; `~/.nvm` deleted; shell hook replaced
- `pyenv` → uninstalled
- **mise** (`/usr/bin/mise`) now manages Node/Python/Go/Rust per-project via `.tool-versions` or `.mise.toml`

### Added compile caches (env in `~/.zshrc`)

```
eval "$(mise activate zsh)"
export RUSTC_WRAPPER=sccache
export SCCACHE_CACHE_SIZE=10G
export PATH="/usr/lib/ccache/bin:$PATH"
```

### pnpm

Global store configured at `~/.local/share/pnpm/store` — run `pnpm install` in existing Node projects to migrate `node_modules` into hardlinked global store.

### Gaming

`gamemode` + `lib32-gamemode` installed; user added to `gamemode` group. Prefix any game: `gamemoderun <game>`.

### Backup (disabled template)

`rclone` + `restic` installed. Template at `/usr/local/bin/backup-workspace.sh` + `workspace-backup.{service,timer}`. To activate:

```
rclone config             # pick provider (gdrive/b2/r2/…), name remote
export RCLONE_REMOTE=yourname:folder   # or edit script's default
sudo systemctl enable --now workspace-backup.timer
```

---

## 7. Uninstalls (cleanup)

### JetBrains (all of it)

`intellij-idea-ultimate-edition`, `intellij-http-client`, `pycharm`, `rustrover(+jre)`, `webstorm(+jre)`, `datagrip(+jre)`. All config/cache/state dirs purged. JetBrains fonts retained.

### Browsers trimmed to 3

**Kept**: `brave-bin`, `google-chrome`, `librewolf-bin`
**Removed**: `firefox-developer-edition`, `mullvad-browser-bin`, `zen-browser-bin` + `~/.config/mozilla` (4.4GB) + `~/.config/zen` (155MB).

### Journald cap

`/etc/systemd/journald.conf.d/99-size.conf` — `SystemMaxUse=500M`, `SystemMaxFileSize=100M`, `SystemKeepFree=1G`.

---

## 8. Post-reboot verification quick-check

```bash
# Memory subsystem
zramctl                                                   # 15.5G zstd
sysctl vm.swappiness vm.page-cluster vm.watermark_scale_factor vm.vfs_cache_pressure
oomctl | grep -E 'Monitored|Path:'                        # should list slices

# Btrfs
findmnt -no OPTIONS /                                     # compress=zstd:1
systemctl is-enabled fstrim.timer btrfs-scrub@-.timer

# Timeshift
sudo timeshift --list                                     # 1 snapshot, tag D
systemctl list-timers | grep -E 'cache-clean|btrfs-scrub|fstrim'

# Toolchain
command -v mise sccache ccache rclone restic pnpm gamemoderun
```

---

## 9. Pending manual steps

1. **New shell** (or `source ~/.zshrc`) for mise + sccache/ccache to activate.
2. **Log out/in once** so `gamemode` group applies to session.
3. **Cloud backup**: `rclone config` → then enable `workspace-backup.timer`.
4. *(Optional)* Migrate Node projects: `cd ~/Workspace/<proj> && pnpm import && pnpm install` to consolidate into global store.
5. *(Optional)* Review `/opt/rocm` (26GB) — if you don't use AMD GPU compute (ROCm doesn't officially support the RX 6700 XT's gfx1031), consider `sudo pacman -Rns rocm-hip-sdk rocm-opencl-sdk` family.

---

## 10. Rollback cheatsheet

| Change | Reverse |
|---|---|
| zram 16GB | `sudo cp /etc/systemd/zram-generator.conf.backup.20260419 /etc/systemd/zram-generator.conf` |
| VM sysctls | `sudo rm /etc/sysctl.d/99-swappiness.conf && sudo sysctl --system` |
| oomd slice rules | `sudo rm /etc/systemd/system/{-,user,system}.slice.d/99-oomd.conf && sudo systemctl daemon-reload && sudo systemctl restart systemd-oomd` |
| Timeshift config | restore from `/etc/timeshift/timeshift.json.backup` if kept, or re-run `timeshift-gtk` |
| Re-enable ollama | `sudo systemctl enable --now ollama` |
| Remove weekly timers | `sudo systemctl disable --now weekly-cache-clean.timer pacman-cache-clean.timer` + `sudo rm /etc/systemd/system/{weekly-cache-clean,pacman-cache-clean}.{service,timer}` |
| Journald cap | `sudo rm /etc/systemd/journald.conf.d/99-size.conf && sudo systemctl restart systemd-journald` |
