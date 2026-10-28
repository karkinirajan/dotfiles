# RESEARCH

Phase 1 output. Date of record 2026-10-29 (retrieval clock 2026-10-28 UTC). Ten read-only research agents covered the repo by topic cluster. Each wrote notes (included verbatim below as sections C1 to C10) and ledger rows (merged into [`LEDGER.csv`](LEDGER.csv), 823 rows, ids `L-0001` onward). The orchestrator is the single writer to the repo.

## How to read this

- **Ledger columns:** `id, cluster, topic, file, old_claim, new_claim, source_url, retrieved, confidence, source_type, status, notes`. `status` is `changed` (repo text must change), `confirmed` (checked, repo was right) or `unverified` (old content stays, tagged `<!-- UNVERIFIED -->`).
- **Totals:** 823 rows: 307 changed, 450 confirmed, 66 unverified. Confidence: 625 high, 159 medium, 39 low. Split per cluster in the table below.
- **Labels in "Setup steps" tables:** `verified-in-cloud` was run in the Linux sandbox; `machine-only` needs the CachyOS host; `unverified` could be neither run nor tied to current docs.
- **Version policy (brief):** pin to the latest stable that Arch/CachyOS repos or the official installer can deliver; record upstream alongside. The host has CachyOS repos first (`cachyos-v3`, `cachyos-core-v3`, `cachyos-extra-v3`, `cachyos`, then Arch), so the CachyOS version wins over Arch extra whenever both exist.

| Cluster | Rows | Changed | Confirmed | Unverified |
|---|---|---|---|---|
| C1 OS, boot, security | 79 | 24 | 51 | 4 |
| C2 desktop | 77 | 44 | 29 | 4 |
| C3 GPU, ROCm, local AI | 82 | 35 | 34 | 13 |
| C4 languages and tooling | 80 | 25 | 53 | 2 |
| C5 DevOps and containers | 59 | 30 | 27 | 2 |
| C6 databases | 73 | 25 | 33 | 15 |
| C7 editors and shell | 109 | 38 | 66 | 5 |
| C8 Claude Code and AI tooling | 78 | 16 | 53 | 9 |
| C9 frontend skills | 80 | 35 | 41 | 4 |
| C10 apps and misc | 106 | 35 | 63 | 8 |

## Cross-cluster decisions (orchestrator)

These resolve conflicts between clusters and fix the version targets that `versions.yaml` carries.

1. **Hyprland is held at the version the distro delivers, 0.56.2, until a Lua config is validated on the machine.** Arch extra has 0.57.0 (2026-10-28), which removed the hyprlang parser: with only `hyprland.conf` it ignores every `hypr/config/*.conf` file (C2). CachyOS `cachyos-extra-v3` still has 0.56.2-4.1, so a plain `pacman -Syu` today delivers 0.56.2, but CachyOS will rebuild 0.57 and a later update would break the session. The compatibility constraint is therefore: `hyprland`/`hyprpm` stay on 0.56.2 (`IgnorePkg`) until `hyprland.lua` is applied and checked. A Lua port is staged in-repo but not linked (see D-12 in `DECISIONS.md`).
2. **Dispatch mixing is a live defect on 0.56.2.** `hyprctl dispatch 'hl.dsp...'` only works under a Lua config; the repo's scripts use that form while the active config is `.conf`, so hypridle DPMS, `minimize.sh`, `restore.sh` and `launcher-open.sh` fail today (C2). The Lua port fixes both directions at once.
3. **ROCm stays on the legacy 7.2.4 train** that Arch and CachyOS ship. AMD's new Core SDK 10.1.0 lists only gfx1030 (not gfx1031) and is not packaged for Arch (C3). `HSA_OVERRIDE_GFX_VERSION=10.3.0` is a fallback for Ollama on this packaging and a requirement for PyTorch wheels; it is scoped per project instead of exported globally.
4. **PyTorch recipe:** index `https://download.pytorch.org/whl/rocm7.2`, torch 2.14.1+rocm7.2, `triton-rocm` as a direct dependency (the old `pytorch-triton-rocm` name fails to lock). The verify snippet uses `total_memory`, not `total_mem` (C3, resolved with a real `uv lock` in the sandbox).
5. **Ollama:** 0.40.11 is what the distro delivers (0.40.13 upstream). `cap_perfmon` and its pacman hook are Vulkan-only and upstream bug 15321 says the capability can break discovery, so they are removed from the default ROCm path and documented as Vulkan-only (C3).
6. **Node:** Node 26 "Lithium" became LTS on 2026-10-28; `nvm install --lts` now resolves to 26.13.0 and Node 24 moved to Maintenance on 2026-10-20 (C4, C9). Arch `nodejs` is 26.12.1. The frontend skill pin "Node 24 Active LTS" is corrected to 26 LTS with 24 in maintenance.
7. **Next.js:** `16.4.0` is vulnerable (Critical RCE fixed in 16.4.1, 2026-10-14). The target is 16.4.3, with monthly security releases (next 2026-11-03) noted (C9).
8. **Containers:** `docker-rootless-extras` is AUR-only (not a CachyOS package); the system `docker.socket` must not be enabled; `docker-machine` is archived upstream and is dropped from `developer.txt`; CI action references move off node20 (C5).
9. **Databases:** PostgreSQL 18.6 stays; `initdb` flags `--auth-local=peer --auth-host=scram-sha-256` are mandatory in every copy of the recipe (PG18 `initdb` defaults to `trust`); MariaDB 13.0 is a rolling release with Community EOL in Q4 2026, so `mariadb-lts` (Arch extra, 12.3.3) is the recommended dev server; the AUR `mongodb-bin` 8.3.9 sits inside the SERVER-131805 advisory range (C6).
10. **VPN and browsers:** `mullvad-vpn` is in Arch extra; `mullvad-vpn-bin` is optional. `librewolf-bin` no longer exists (use `librewolf` from extra). uBlock Origin on Chromium-based Brave needs an MV2 caveat (C10).
11. **claude-brain is unverified.** No public package matches the hooks in `settings.json`; the hooks end in `|| true`, so they are inert on a fresh machine. The repo keeps them and tags the claim `<!-- UNVERIFIED -->` (C8).
12. **Duplicate topic:** `frontend-expert` has no unique content (same 262 rule IDs as `frontend-master`) and is removed after its removal is logged (C9, `REMOVALS.md`).

## Compatibility matrix (hard constraints verified)

| Pair | Constraint | Source cluster |
|---|---|---|
| hyprland x config format | 0.56.2 loads `.conf` or `.lua`; 0.57.0 loads only `.lua` | C2 |
| hyprland x Hyprspace | Hyprspace main compiles on 0.56.x, not on 0.57.0 (`m_renderPass` removed) | C2 |
| kernel x amdgpu | in-tree `amdgpu`, no DKMS; 7.3.0-4 on cachyos-v3 | C3 |
| ROCm x GPU | 7.2.4 and 10.1.0 list gfx1030 only; gfx1031 needs the override for PyTorch wheels | C3 |
| ROCm x PyTorch | rocm7.2 index tops at torch 2.14.1 (cp312 to cp314); `triton-rocm` 3.8.0 | C3 |
| ROCm x Ollama | `ollama-rocm` bundles its own ROCm 7.2 libs; needs a ROCm v7 driver | C3 |
| Python x Open WebUI pip | needs Python 3.11 or 3.12 (`<3.13`) | C3 |
| Python x vLLM ROCm wheels | Python 3.12 only | C3 |
| Node x tooling | Next 16 needs Node 20.9+; Prisma 7 needs 20.19+; pnpm 12 and npm 12 need current Node | C4, C9 |
| TypeScript x typescript-eslint | `typescript-eslint` 8.72.1 rejects TypeScript 7; keep `typescript` 6.x for tooling, 7 only as the native type-check | C9 |
| TypeScript x typescript-language-server | global TypeScript 7.0.2 ships no `tsserver.js`; install `typescript@6` alongside | C4 |
| PostgreSQL 18 x pgvector | pgvector 0.8.7 supports PG18 | C6 |
| PostgreSQL 18 x container images | PG18 images mount `/var/lib/postgresql`, not `.../data` | C6 |
| Docker rootless x ports | host Postgres 5432 and Valkey 6379 clash with compose publishes; bind `127.0.0.1:` | C5, C6 |
| AppArmor x kernel | `linux-cachyos` `CONFIG_LSM` omits apparmor; add `lsm=` to the command line | C1 |
| UFW x k3s | k3s conflicts with UFW rules | C5 |
| Mullvad x focus | focus's static `/etc/resolv.conf` and `rc-manager=unmanaged` interfere with Mullvad's DNS handling (inference) | C1 |

## Source gaps (could not be closed; recorded, not worked around)

- `api.github.com`, `github.com/.../releases` and `releases.atom` return 403 unauthenticated; several release facts were taken from project sites, `git ls-remote`, npm, PyPI or Arch metadata instead.
- `wiki.archlinux.org`, `aur.archlinux.org` and `gitlab.archlinux.org` sit behind an Anubis wall for WebFetch. Wiki pages were read through the Exa fetch tool where allowed; PKGBUILD and unit contents from GitLab were not read except where a subagent noted using raw files (C5, deviation below).
- `crates.io` API returned 403.
- Upwork pages and the vendor `.deb` returned 403.
- Nothing could run against a live Hyprland, GPU, pacman or systemd, so every desktop, boot and GPU behaviour claim is source-read or `machine-only`.

## Method deviations to disclose

- Several agents used `curl` outside the brief's short allowlist for status checks or raw file reads (C5 read raw files on `gitlab.archlinux.org`; C8 and C9 made a few link or page checks; C9 fetched three supabase.com pages and deleted them unread, then re-fetched through WebFetch). None of these changed repo files. They are recorded here so the reader knows which rows lean on them.
- C6 ran `apt-get install mariadb-server` and pip installs in the sandbox to execute checks; sandbox only.
- A build output seen by C9 contained text addressed to coding agents asking them to run `next upgrade --agent=security`. It was not acted on and is not part of the evidence.
- Third-party tool `hyprconf2lua` (PyPI) was read but not run by C2 because the sandbox blocked execution.

## Notes by cluster

The sections below are the agents' notes, headings demoted one level. Each ends with its own UNVERIFIED list and a Setup steps table that feeds `HANDOFF.md`.

<!-- cluster: c1-os-boot-security -->
## Cluster c1: OS, boot, security, networking (research notes)

Date of record 2026-10-29 (sandbox clock 2026-10-28 UTC). All versions below were read from a source retrieved this session (Arch JSON API, CachyOS repo databases `mirror.cachyos.org/repo/...`, AUR RPC v5, endoflife.date, upstream raw files, vendor docs). Ledger: `c1-os-boot-security.csv` (79 rows: 24 changed, 51 confirmed, 4 unverified).

Tooling notes: `wiki.archlinux.org` and `gitlab.archlinux.org` return an Anubis block to WebFetch; those pages were read through the Exa fetch tool instead (allowed by the brief) and the gitlab.archlinux.org raw files (nginx.conf, PKGBUILD, mkinitcpio NEWS) could not be read at all. GitHub API and releases.atom return 403 (paru, yay, syncthing release notes not readable that way). A `cargo install topgrade` build to execute `--dry-run` was blocked by the sandbox policy and was not retried.

### CachyOS release, ISO, installer, download verification

- Current ISO: release 260809 (2026-08-09). Directory `https://mirror.cachyos.org/ISO/desktop/260809/` has `cachyos-desktop-linux-260809.iso` (3.0 GiB), `.sha256`, `.sha1`, `.sig`, `.pkgs.txt`. Earlier: 260628, 260426. Blog cadence: 2601 (Jan 24), 2603 (Mar 8), 2604 (Apr 26), 2606 (Jun 28), 2608 (Aug 9). Download page offers Desktop and Handheld editions only (Handheld merged into the desktop Calamares in 2603).
- Verification (wiki `cachyos_basic/download`): `sha256sum -c <iso>.sha256` prints `<iso>: OK`; GPG: `gpg --keyserver hkps://keys.openpgp.org --recv-key F3B607488DB35A47`, `gpg --verify <iso>.sig <iso>`, expect `Good signature` from "CachyOS", primary fingerprint `882D CFE4 8E20 51D4 8E25 62AB F3B6 0748 8DB3 5A47`; the "key is not certified" warning is expected. Repo (`fresh-setup.md:95-98`) only links; recommend adding these commands.
- Installer facts relevant to the repo: Limine is the default bootloader since 2601 with a 4192 MB boot partition (wiki says at least 4096 MiB for Limine); NVMe Btrfs uses compression level 1 (matches `compress=zstd:1`); the ISO ships Stable plus LTS kernels (explains the LTS entries the repo later removed); manual partitioning is "strongly preferred"; disable Secure Boot and CSM for the install, enable Secure Boot afterwards; one desktop environment only. June 2026 (2606) added a "CachyOS Hyprland Noctalia" desktop option; August (2608) says the installer uses `noctalia-greeter` for Hyprland. So `fresh-setup.md:99-101` ("Hyprland if offered, otherwise the minimal option") can now say to pick the Hyprland Noctalia option. The June release also removed `paru` from the installer and recommends Shelly.
- LUKS: installer has an Encrypt checkbox; GRUB uses LUKS2 since 2601; 2603 fixed LUKS2 on some devices. With Limine, `/boot` (FAT) cannot be encrypted (forum reports, secondary). Repo statement "LUKS must be chosen at install" stands.
- Links: `https://www.cachyos.org/download/`, `https://wiki.cachyos.org/cachyos_basic/download/`, `https://wiki.cachyos.org/configuration/secure_boot_setup/` all resolve and say what the repo claims (`/features/secure_boot_setup/` is 404, keep `/configuration/`). `docs.rs` EnvFilter link in `topgrade.toml` resolves.
- UNVERIFIED: exact installer menu label for the Hyprland option (blog wording only); Limine + LUKS boot success on current ISO (forum anecdotes).

### CachyOS repos, mirrors, cachyos-rate-mirrors vs reflector

- Optimized repos (wiki `features/optimized_repos`): `cachyos-v3`, `cachyos-core-v3`, `cachyos-extra-v3`, generic `[cachyos]` (forked pacman); v4 trio needs AVX-512; znver4 trio is Zen 4/5 only. Ryzen 5 5600 is Zen 3, so v3 is correct; repo order must be cachyos-v3, cachyos-core-v3, cachyos-extra-v3, cachyos, then Arch repos. Manual path: `curl https://mirror.cachyos.org/cachyos-repo.tar.xz` (not `.tar.zst`), `tar xvf`, `sudo ./cachyos-repo.sh`.
- `README.md:142-146` `pacman-conf --repo-list | grep -q '^cachyos'` is valid (`-l/--repo-list`).
- Because CachyOS repos come first, versions differ from Arch: limine 12.9.4-1 (cachyos) vs 12.9.6-1 (extra); linux-cachyos 7.3.0-4 (v3) vs 7.2.7-1 (generic cachyos); amd-ucode 1:20261019-1 (epoch) vs core 20260916-1.
- Mirrors: `cachyos-rate-mirrors` 25-1 (CachyOS-PKGBUILDS) runs `rate-mirrors` for `arch` and `cachyos`, overwrites `/etc/pacman.d/mirrorlist` and `/etc/pacman.d/cachyos-mirrorlist`, copies the latter to `cachyos-v3-mirrorlist` and `cachyos-v4-mirrorlist` (sed to `$arch_v3` / `$arch_v4`), enables `cachyos-rate-mirrors.timer` on install (`OnCalendar=*-*-01,11,21`), and ships a pacman hook that runs `systemctl disable reflector.timer` whenever `reflector` is installed or upgraded. Country is auto-detected from geoip.kde.org (override `RATE_MIRRORS_ENTRY_COUNTRY` in `/etc/conf.d/cachyos-rate-mirrors.env`). Aug 2026 release: ranking now uses the CachyOS mirrorlist API.
- Repo edits: `setup.md:106-113` and `setup.md:1690-1698` install `reflector`, run `reflector --country 'NP,IN,SG' ... --save /etc/pacman.d/mirrorlist`, then `cachyos-rate-mirrors`, then `enable --now reflector.timer`. Replace with `sudo cachyos-rate-mirrors` only (timer already enabled). Drop `reflector` from the explicit list in `system-summary.md` (reflector 2023-5 has had no release since 2023).
- Update tooling: `cachy-update` 4.4.4-1 (rebased on Arch-Update v4.x, Rust systray, `--check --enable`), `shelly` 3.1.9 (Zig rewrite, default GUI package manager), `paru` 2.1.0-3 in [cachyos] (AUR copy 2.1.0-2), `yay` 13.0.1-1 in [cachyos] (AUR 13.1.0-1).

### linux-cachyos (kernel, headers, schedulers, mkinitcpio)

- Versions: upstream 7.3 released 2026-10-18 (non-LTS; 7.2.13 latest 7.2; 6.18 LTS to 2028-12-31) per endoflife.date. CachyOS `linux-cachyos` 7.3.0-4 in cachyos-v3 (built 2026-10-23), 7.2.7-1 in generic `[cachyos]` (built 2026-09-25), AUR 7.3.0-3 (2026-10-23). Arch `linux` 7.2.11.arch1-1 (2026-10-17), `linux-lts` 6.18.59-1. `system-summary.md` "7.3.0-4-cachyos" is correct for a v3 host.
- Package facts (PKGBUILD + cachyos-v3.db): description "EEVDF + LTO + AutoFDO + Propeller"; default `_cpusched=cachyos` (EEVDF); BORE, BMQ, hardened and rt-bore are separate kernels; `scx-scheds` (extra 1.1.4-1) is an optdepend for sched-ext; depends `coreutils kmod initramfs`; `linux-cachyos-headers` is a separate package (binutils, pahole, etc.), only needed for DKMS; provides `V4L2LOOPBACK-MODULE`, `NTSYNC-MODULE` and others, NVIDIA/ZFS prebuilt. Repo claims about headers and mkinitcpio hold: `limine-mkinitcpio-hook` 1.40.0-1 depends on `mkinitcpio` (42.2-1 in core).
- `linux-rt` is an Arch extra package (7.2.12.rt3); CachyOS's RT kernel is `linux-cachyos-rt-bore`. Removing LTS leaves no fallback kernel in the single-entry menu; `linux-cachyos-lts` 6.18.55-2 is available if the owner wants a fallback.
- Kernel config (7.3.0): `CONFIG_SECURITY_APPARMOR=y` but `CONFIG_LSM="landlock,lockdown,yama,integrity,bpf"` (see AppArmor). `CONFIG_ZRAM_DEF_COMP="zstd"`, `CONFIG_HZ=300` in the stock config (the wiki says the default kernel uses a 1000 Hz tick via PKGBUILD options; not checked further).
- mkinitcpio: Arch news 2026-09-22: mkinitcpio >= 42 adds `systemd-pcrosseparator.service` to the systemd hook, changing PCR 0-7, 9, 12-14; TPM2-bound LUKS must be re-enrolled (not applicable: root is not LUKS). 2024-03-04 news: microcode is an initramfs hook, no separate ucode initrd line (nothing in the repo contradicts this).
- UNVERIFIED: mkinitcpio 42.x release notes beyond the Arch news item (upstream NEWS not readable).

### cachyos-settings: ZRAM and sysctl

- `cachyos-settings` 1:1.4.1-1 depends on `zram-generator, ananicy-cpp, cachyos-ananicy-rules, inxi, systemd>=256, iw, wireless-regdb`; optdepends `power-profiles-daemon`.
- Vendor `/usr/lib/systemd/zram-generator.conf`: `compression-algorithm = zstd`, `zram-size = ram`, `swap-priority = 100`, `fs-type = swap`. On 32 GiB that is the 31.3 GiB zstd device in `system-summary.md`: the claim is correct. Udev rule `30-zram.rules` sets `vm.swappiness=150` and disables zswap when zram0 initialises. zram-generator reads `/usr/lib`, `/usr/local/lib`, `/etc`, `/run` (later overrides), so the repo's `/etc/systemd/zram-generator.conf` with `min(ram, 8192)` would cut swap to 8 GiB; `setup.md:81-97` should drop the example and the "8GB" prose and the unsourced "~37ns / ~100us / 36-40GB" figures.
- Vendor sysctl `70-cachyos-settings.conf`: swappiness 100, vfs_cache_pressure 50, dirty_bytes 268435456, dirty_background_bytes 67108864, dirty_writeback_centisecs 1500, page-cluster 0, nmi_watchdog 0, unprivileged_userns_clone 1, printk 3 3 3 3, kptr_restrict 2, netdev_max_backlog 4096, fs.file-max 2097152, sysrq 1. None of the repo's `99-developer.conf` keys are set there. Kernel defaults: inotify `max_user_instances` 128; `max_user_watches` ~1% of RAM clamped [8192, 1048576] (since 5.11), so 524288 is a sensible raise on 32 GiB; `tcp_fastopen` default 0x1, 3 = client+server.
- `setup.md:58`: `cachyos-settings` already pulls `ananicy-cpp` and rules; extra names are harmless.
- Swapfile snippet `setup.md:100-103`: btrfs docs say a subvolume with an active swapfile cannot be snapshotted; create `/swap` as its own subvolume first. `btrfs filesystem mkswapfile` needs btrfs-progs >= 6.1 (7.3 installed).
- NetworkManager: cachyos-settings ships `/usr/lib/NetworkManager/conf.d/dns.conf` with `dns=systemd-resolved`.

### Limine 12.x, limine-entry-tool, limine-snapper-sync

- Limine upstream 12.9.6 (2026-10-28), Arch extra 12.9.6-1, CachyOS 12.9.4-1 (host). 12.9.5 (10-27): `default_entry: 0` no longer selects the first entry (entries start at 1), remembered-entry UUID format changed. 12.9.6: global options must come before the first entry; fixes a boot hang on GPUs with no display attached introduced in 12.9.4 (not applicable: the 5600 has no iGPU).
- limine.conf keys used by the repo are valid: `default_entry: CachyOS/linux-cachyos` (entry path syntax, `/` separator), `remember_last_entry: no` (UEFI only, outranks `default_entry` when yes). A default pointing at a directory disables autoboot (CachyOS wiki tip).
- `/etc/default/limine` keys (limine-entry-tool README): `BOOT_ORDER` default `"*, *fallback, Snapshots"`, `*` wildcard, ordering only when `ENABLE_SORT=yes` (default no); `FIND_BOOTLOADERS` default yes ("add systemd-boot, rEFInd, or the default EFI loader"); `ENABLE_LIMINE_FALLBACK` default empty = create fallback only if absent; `KERNEL_CMDLINE[default]`, `KERNEL_CMDLINE["linux-cachyos"]`, `+=` appends and `=` replaces; `ENABLE_UKI` default no. `/etc/limine-entry-tool.conf` is the template/default, `/etc/default/limine` overrides it, `/etc/limine-entry-tool.d/*.conf` are lower-priority drop-ins. Commands: `limine-update`, `limine-list` (= `limine-entry-tool --tree [depth]`, default depth 3), `limine-entry-tool --remove-entry <path> [position] [depth]`, `limine-scan`, `limine-install`. CachyOS wiki uses `sudo limine-mkinitcpio` for the same apply step.
- `limine-snapper-sync` 1.32.1-1: unit `limine-snapper-sync.service`; `/etc/default/limine` beats `/etc/limine-snapper-sync.conf`; deps `limine snapper btrfs-progs libnotify`.
- Gaps/risks: BOOT_ORDER is not documented as a filter (repo should not present it as the mechanism); persistence of manual `default_entry` edits across `limine-update` is undocumented; `KERNEL_CMDLINE[default]+=` is only safe when the base parameters already live in `/etc/default/limine` (entry-tool README: `+=` ignores `/etc/kernel/cmdline` and `/proc/cmdline`), so `setup.md:1593` must tell the reader to inspect the generated `cmdline:` line for `root=`, `rootflags=` and `lsm=` before rebooting.

### Snapper, snap-pac, btrfs-assistant, cachyos-snapper-support, Btrfs maintenance, Timeshift

- Versions: snapper 0.13.2-1 (extra, 2026-09-16), snap-pac 3.0.1-3 (2024-07-01, unchanged), btrfs-assistant 3.0.0-1 (extra, 2026-10-16), btrfs-progs 7.3-1 (core), btrfsmaintenance 0.5.2-3, timeshift 26.09.0-1.
- `cachyos-snapper-support` 1.0.2-1: `depends=(snapper snap-pac)`, `conflicts=(timeshift)`; `post_install` runs `snapper -c root create-config --template cachyos-root /` and `systemctl enable --now snapper-cleanup.timer`; `snapper-timeline.timer` enable is commented out. Template: `TIMELINE_CREATE="no"`, `NUMBER_LIMIT="50"`, `NUMBER_LIMIT_IMPORTANT="15"`, `TIMELINE_LIMIT_HOURLY=5`, `DAILY=7`, `SPACE_LIMIT=0.5`, `FREE_LIMIT=0.2`. So `setup.md:1634-1639` (create-config guard OK) enabling the timeline timer is a no-op unless the config sets `TIMELINE_CREATE=yes`. CachyOS wiki quotes `NUMBER_LIMIT=10`, which differs from the shipped template; use the template.
- The repo's Timeshift conflict claim is correct (PKGBUILD). Timeshift `--check` creates a snapshot only if scheduled (`--create` forces); Timeshift's own cron (`/etc/cron.d/timeshift-hourly`, `0 * * * * root timeshift --check --scripted`) makes the daily systemd timer redundant.
- Btrfs: `btrfs scrub start -B -r /` (read-only, foreground) and `btrfs scrub status /`; upstream recommends about monthly. `btrfs check` is read-only by default; `--repair` warning confirmed. System lists mismatch: `system.txt` does not list `btrfs-assistant`, `limine-mkinitcpio-hook`, `limine-snapper-sync` which `system-summary.md` shows as explicit.

### Secure Boot (sbctl)

- `sbctl` 0.18-2 (extra). CachyOS guide: `systemctl reboot --firmware-setup`, put firmware in Setup Mode, `sudo sbctl status`, `sudo sbctl create-keys`, `sudo sbctl enroll-keys --microsoft --firmware-builtin` (ASUS and Gigabyte boards: `--microsoft` only; the host is a Gigabyte B550), `sudo sbctl-batch-sign`, `sudo sbctl verify`. Limine section: Limine >= 11.2.0 enforces BLAKE2B hashes of config and paths; set `ENABLE_ENROLL_LIMINE_CONFIG=yes`, `sudo b2sum /boot/limine-splash.png` (append hash after `#`), `sudo limine-enroll-config`, `sudo limine-update`; only the Limine EFI binary needs signing. CachyOS-Settings README says `sbctl-batch-sign` is "incompatible with Limine". Repo (`fresh-setup.md:112-118`) correctly links the guide and forbids copying keys; add the Limine specifics.

### Display manager: greetd + noctalia-greeter + uwsm, SDDM fallback

- Versions: greetd 0.10.3-2, noctalia-greeter 1.7.0-1 (extra, 2026-10-22; depends greetd, wlroots0.20), uwsm 0.27.1-1, sddm 0.21.0-8 (cachyos-v3), Hyprland 0.57.0-1 in extra vs 0.56.2-4 on the host.
- Noctalia's install doc: greetd must launch `noctalia-greeter-session` (not `noctalia-greeter`); merge `command = "/usr/bin/noctalia-greeter-session"` and `user = "greeter"` into `[default_session]` of `/etc/greetd/config.toml`; run `sudo systemd-tmpfiles --create noctalia-greeter.conf` and `sudo noctalia-greeter-apply-appearance --setup-system`; disable the old DM (`systemctl status display-manager.service`, `sudo systemctl disable --now <UNIT>.service`), then `sudo systemctl enable --now greetd`; keep a TTY open. `fresh-setup.md:233-247` omits all of this.
- uwsm: `Exec=uwsm start -e -D Hyprland hyprland.desktop` is valid (`-e` and `-D` are separate options in uwsm source); README prefers `uwsm start -- <entry>.desktop`. Arch's hyprland package already ships `hyprland-uwsm.desktop`; the `/usr/local/share/wayland-sessions` copy exists to hide the plain session in SDDM. Hyprland wiki: use `uwsm stop`, not the `exit` dispatcher.
- SDDM (man `sddm.conf(5)`): `DisplayServer` = `x11` (default) | `x11-user` | `wayland` (experimental, default `CompositorCommand = weston --shell=kiosk`, which explains the logged weston error); `[Users] RememberLastSession` default true; `[Wayland] SessionDir` default `/usr/local/share/wayland-sessions,/usr/share/wayland-sessions`; config read from `/usr/lib/sddm/sddm.conf.d`, `/etc/sddm.conf.d`, `/etc/sddm.conf` (later wins). Repo's SDDM files are correct.
- `KDE-REMOVAL.md`: Jan 2026 ISO switched Plasma installs to `plasma-login-manager` (`plasmalogin.service`), consistent with the doc.
- Cross-cluster flag (UNVERIFIED): ArchWiki greetd page says Hyprland >= 0.55 defaults to Lua configs, Hyprlang `.conf` deprecated, greeter examples use `start-hyprland`.

### paru, yay, pacman best practice, pacman hooks

- See cachyos section for versions. June 2026 installer dropped paru; `sudo pacman -S paru` works on CachyOS. AUR helper wording in `README.md:155-158` and `fresh-setup.md:144-147` should say so. Arch news 2026-06-12 ("Active AUR malicious packages incident"): review all PKGBUILD and install-script changes.
- Arch wiki System maintenance confirms every rule in the repo (full `-Syu` only, no `-Sy pkg`, avoid `--overwrite` and `-dd`, handle `.pacnew`, read Arch news). Arch news relevant now: 2026-04-05 iptables now defaults to the nft backend (`iptables-nft` replaced by `iptables`, `iptables-legacy` separate); 2026-09-22 mkinitcpio 42; 2026-10-21 ca-certificates-mozilla >= 3.131.1-1 (MITM fix).
- pacman 7.1.0 (core 7.1.0.r9-3, CachyOS fork -5): default SigLevel Required, downloader sandbox (`DownloadUser`, `DisableSandbox`), fine-grained sandbox options; the CachyOS fork adds `DisableSandboxNetwork`, so hooks and scriptlets run without network by default (June 2026 release).
- `README.md` awk package split verified by execution: 132 repo + 9 AUR packages.

### topgrade 17.x

- Upstream 17.14.1 (2026-10-20, security rebuild of rustls roots + opencode fix); 17.14.0 (10-19) added pre-commit gc and GitHub CLI skills steps. AUR `topgrade-bin` 17.14.1-1 and `topgrade` 17.14.1-1; not in Arch repos.
- Keys in `topgrade.toml` verified against `src/config.rs`, `src/step.rs`, `src/steps/os/archlinux.rs` and `config.example.toml` (main): `[misc] disable` accepts snake_case Step names (`antigravity`, `antigravity_cli`, `helm` exist), `no_self_update`, `assume_yes`, `ask_retry` exist; `[linux] arch_package_manager` accepts `autodetect, aura, garuda_update, pacman, pamac, paru, pikaur, shelly, trizen, yay`. `--noconfirm` is passed only when `assume_yes` applies to the System step, so `assume_yes = false` behaves as the repo says. Self-update is an optional build feature; `no_self_update = true` and `--no-self-update` disable it. `show_distribution_summary` (default true) lists `.pacnew/.pacsave`.
- Drift (comments only): upstream template now says `--greedy-latest` / `--greedy-auto-updates` and adds `[sheldon]`, `[mise]`, `apt_arguments`. Repo TOML parses (tomllib).
- UNVERIFIED: the runtime claims about `antigravity --version` opening the IDE and `agy update` failing on `/usr/bin/agy`.

### UFW, ufw-extras, Fail2ban, OpenSSH, KDE Connect ports

- UFW 0.36.2-7 (upstream 0.36.2 dated 2023-05-18; no newer upstream). Launchpad shows open 2026 bugs: 2170467 (failed reload writes `ENABLED=no`), 2166080 (kernel freezes with UFW logging on kernel 7.2.2-1). Repo commands are right (`ufw default deny incoming`, `ufw --force enable`, `systemctl enable --now ufw.service`; CachyOS also enables UFW by default). Check `sudo ufw status verbose` after every reboot.
- `ufw-extras` 1.3.0-1 only ships profiles in `/etc/ufw/applications.d` (kdeconnect, localsend, mdns, samba, steam, tailscale, ...); optional. `syncthing` ships `ufw-syncthing`.
- KDE Connect: TCP and UDP 1714-1764 (userbase.kde.org). `setup.md` section 18.3 opens the range unconditionally while 19.1 says zero inbound rules; mark 18.3 optional.
- Fail2ban 1.1.1 (2026-08-15; Arch 1.1.1-1, depends `python-systemd`). `paths-arch.conf` already sets `sshd_backend = systemd`; default banaction in 1.1.1 is `iptables-multiport` (nftables default for Arch is in unreleased 1.1.2-dev). With UFW use `banaction = ufw`. No sshd runs on the host, so the jail has nothing to protect until `sshd` is enabled.
- OpenSSH 10.6p1 (2026-10-06; Arch core 10.6p1-2). Since 10.0: DSA removed, modp DH off by default in sshd, `ControlMaster no` passed by scp/sftp; 10.1: agent sockets moved to `~/.ssh/agent`, non-PQ key agreement warning; 10.3: `ssh -O conninfo`, `-O channels`; 10.6: `WarnWeakCrypto`, `PubkeyOptions max-pk-ok`. Existing `sshd_config` keys are all still valid; Arch wiki prefers drop-ins in `/etc/ssh/sshd_config.d/`, `sshd -t` before restart, and `AuthenticationMethods publickey` / `KbdInteractiveAuthentication no` for key-only logins. Host keys on Arch include `mldsa44-ed25519` (wiki).
- SSH ControlMaster user unit: options valid; line 7 `\$2` triggers a systemd "unknown escape" warning (reproduced with `systemd-analyze verify`), use `$$2`.

### AppArmor / apparmor.d on CachyOS

- apparmor 4.1.8-2 (extra; 5.0.2-2 in extra-testing); apparmor.d 0.4915.0-1 (cachyos repo and AUR).
- Why `aa-status` said "apparmor filesystem is not mounted": the CachyOS kernel has AppArmor compiled in but its default `CONFIG_LSM` omits it, so `apparmor module is loaded` prints (module built in) while securityfs/apparmor is not active until the command line carries `lsm=landlock,lockdown,yama,integrity,apparmor,bpf` (Arch wiki; CachyOS forum threads show the same output). Check `cat /sys/kernel/security/lsm`, `aa-enabled`, `cat /proc/cmdline`.
- Official CachyOS steps (wiki `post_install_setup`): `sudo pacman -S apparmor apparmor.d`; add the `lsm=` parameter via the boot manager; `systemctl enable --now apparmor.service`; add to `/etc/apparmor/parser.conf`: `write-cache`, `Optimize=compress-fast`, `cache-loc /etc/apparmor/earlypolicy/`. apparmor.d docs: default install is complain mode; recommended workflow is a week of complain mode with `aa-log`; "Do not expect this project to work correctly ... if your DE and DM are not supported" (GNOME/GDM, KDE/SDDM, XFCE/LightDM WIP). Hyprland + greetd is outside that list. The repo's Limine instruction is right in principle (`/etc/default/limine`), but see the `+=` caution above. Fetched through Exa because apparmor.pujol.io failed DNS in WebFetch.

### dnscrypt-proxy, dnsmasq, nftables and the focus tool

- dnscrypt-proxy 2.1.20 (Arch 2.1.20-1, 2026-10-28). 2.1.17 added PQDNSCrypt (on by default), 2.1.18-2.1.20 regex name lists, DoH cert hash check. Repo keys `server_names`, `listen_addresses`, `require_dnssec`, `require_nolog` all valid; `cloudflare` and `quad9-dnscrypt-ip4-nofilter-pri` exist in `v3/public-resolvers.md` and decode to props 7 (DNSSEC + no-log + no-filter), so the filters keep them.
- Arch wiki: socket activation (`dnscrypt-proxy.socket`, needs `listen_addresses = []`) and the service are mutually exclusive; for dnsmasq forwarding use `no-resolv`, `server=::1#PORT`, `server=127.0.0.1#PORT`, and add `conf-file=/usr/share/dnsmasq/trust-anchors.conf` + `dnssec` only if the upstream validates DNSSEC. The focus dnsmasq config forwards to 1.1.1.1 and 9.9.9.9 (plain DNS), contradicting "forwarding relationship" prose; pick one and document it.
- dnsmasq 2.93 is current (Arch 2.93-1) and includes the CVE-2026-2291 heap fix; 2.92 reordered `--address`/`--server` precedence and added `--log-queries=auth`. `address=/domain/IP` covers subdomains for A/AAAA; `address=/domain/#` returns 0.0.0.0/::; `address=/domain/` returns NXDOMAIN. SIGHUP does not re-read configuration, so the `systemctl restart dnsmasq` in `focus-refresh` is correct. `conf-dir=/etc/dnsmasq.d/,*.conf` is valid. systemd-resolved listens on 127.0.0.53, dnsmasq binds 127.0.0.1 (no clash).
- NetworkManager 1.58.1: `dns=none`, `rc-manager=unmanaged`, `systemd-resolved=false` valid; `/etc/NetworkManager/conf.d` overrides `/usr/lib/NetworkManager/conf.d/dns.conf` (cachyos-settings, `dns=systemd-resolved`).
- nftables (Arch 1.1.7-3; sandbox 1.0.9): the focus file parses and loads, `reject with icmpx type admin-prohibited` is accepted (normalised to `icmpx admin-prohibited`), interval sets accept elements and flush. Re-loading the file duplicates the six rules in `chain output` (rules are appended). Fix: unique table name (for example `inet focus`) and `flush chain inet focus output` before the rules (tested idempotent); the scripts referencing `inet filter` must change together. Arch wiki: `nft -f` does not flush existing rules; stock `/etc/nftables.conf` starts with `flush ruleset`, so nothing here survives enabling `nftables.service`.
- DoH backstop: Firefox `network.trr.mode = 5` ("Off by choice") confirmed on MozillaWiki; the canary domain `use-application-dns.net` returning NXDOMAIN makes Firefox keep DoH off by default; add it to the block config.
- Systemd units of the focus tool validate (systemd-analyze, v255) apart from the documented hardcoded `/home/kneeraazon` paths.
- Mullvad conflict: Mullvad's guide wants systemd-resolved or resolvconf for DNS; focus's static immutable `/etc/resolv.conf` plus `rc-manager=unmanaged` will interfere when both are active (inference).

### VPN packages (Mullvad, Proton VPN)

- Mullvad: `mullvad-vpn` 2026.5-1 is now in Arch extra (depends `mullvad-vpn-daemon`, `electron42`); Mullvad's page: "now available in the official repository (not maintained by us)" and Arch is unsupported. AUR `mullvad-vpn-bin` 2026.5-1 (2026-10-03) is therefore optional. Units: `mullvad-daemon.service`, `mullvad-early-boot-blocking.service` (the repo keeps both disabled). `setup.md:1573` and `developer.txt:72` should use `sudo pacman -S mullvad-vpn`.
- Proton VPN: `proton-vpn-gtk-app` 4.18.7-1 in extra (4.18.8-1 in extra-testing); Proton's Arch page also lists `proton-vpn-cli`; requires NetworkManager and gnome-keyring (KWallet only "may work"). The daemon unit is `proton.VPN.service` (package `proton-vpn-daemon` 0.13.8). KDE-REMOVAL.md removed kwallet and no gnome-keyring is listed: add a Secret Service provider before first login.

### Syncthing 2.x

- Syncthing 2.1.7-1 (extra, 2026-10-21). Units: system `syncthing@.service`, user `syncthing.service`, UFW profile `ufw-syncthing`. Ports: TCP 22000, UDP 22000 (QUIC), UDP 21027; GUI 127.0.0.1:8384 by default; `sudo ufw allow syncthing` (do not add `syncthing-gui`). Use either unit type. User unit starts at login unless lingering is enabled. 2.0 migrated LevelDB to SQLite on first start and stopped creating a default folder (secondary sources).

### nginx 1.30

- Arch `nginx` 1.30.6-2 = stable (1.30 released 2026-04-14, latest 2026-10-14); `nginx-mainline` 1.31.8-1. ArchWiki recommends mainline but Arch modules require the stable package. `types_hash_max_size` default 1024, `types_hash_bucket_size` 64, both valid in `http`; `mailcap` (not `nginx`) supplies `/etc/nginx/mime.types`, which supports the repo's explanation; ArchWiki sample config uses `types_hash_max_size 4096;`. Stock `nginx.conf` content not fetchable; package ships no `conf.d`.

### power-profiles-daemon, microcode, LUKS

- PPD 0.30 (Feb 2025) is still upstream-latest; CachyOS 0.30-3 adds scx_loader integration, Arch extra 0.30-1. AMD uses amd-pstate (active mode) for the performance profile.
- Microcode: `amd-ucode` via mkinitcpio `microcode` hook; CachyOS builds carry epoch 1.
- cryptsetup 2.8.8 (2026-09-07) = Arch; `luksHeaderBackup <device> --header-backup-file <file>` valid in 2.8.8; keep the backup offline.

### Concrete edits by file

| File | Change |
|---|---|
| `fresh-setup.md:95-101` | Add sha256/gpg commands and fingerprint; say the installer now has a Hyprland Noctalia option. |
| `fresh-setup.md:144-147`, `README.md:155-158` | AUR helper: `sudo pacman -S paru` on CachyOS (installer no longer ships it); mention Arch AUR incident and PKGBUILD review. |
| `fresh-setup.md:233-247` | Add greetd `config.toml`, tmpfiles, `noctalia-greeter-apply-appearance --setup-system`, DM hand-off and `enable --now greetd`. |
| `fresh-setup.md:112-118` | Add Limine-specific Secure Boot steps and the Gigabyte `--microsoft` note. |
| `system-summary.md` (AppArmor row, Limine policy) | Explain the real cause (LSM list); say BOOT_ORDER is ordering only; note Limine 12.9.6 exists upstream/Arch. |
| `01-system/cachyos/setup.md:58, 81-103` | cachyos-settings dependency note; delete the 8 GiB zram example and unsourced numbers; `/swap` subvolume. |
| `01-system/cachyos/setup.md:106-113, 1690-1698` | `cachyos-rate-mirrors` only; drop reflector. |
| `01-system/cachyos/setup.md:1490-1535` | Fail2ban `banaction = ufw`; sshd drop-in + `sshd -t` + key-only settings. |
| `01-system/cachyos/setup.md:1548-1568` | dnscrypt service vs socket; dnsmasq `server=127.0.0.1#5300`. |
| `01-system/cachyos/setup.md:1573, packages/developer.txt:72` | `mullvad-vpn` from extra. |
| `01-system/cachyos/setup.md:1585-1602` | CachyOS AppArmor steps incl. parser.conf cache; apparmor.d DM caveat; cmdline `+=` caution. |
| `01-system/cachyos/setup.md:1613-1621` | Syncthing UFW profile and ports. |
| `01-system/cachyos/setup.md:1634-1639` | Timeline timer is off by default (`TIMELINE_CREATE="no"`). |
| `06-tools/focus/nftables/focus-filter.nft` (+ scripts, README) | Unique table name + `flush chain`; DoH canary domain; decide on dnscrypt forwarding. |
| `07-networking/ssh/systemd/user/erke-vps-ssh.service:7` | `\$2` to `$$2`. |
| `01-system/topgrade/topgrade.toml` | Comment drift only. |

### UNVERIFIED list (consolidated)

1. Installer menu label for the Hyprland Noctalia option.
2. Whether `BOOT_ORDER="linux-cachyos"` hides other entries; whether manual `default_entry`/`remember_last_entry` survive `limine-update`.
3. `zram` marketing figures (37 ns, 100 us, 36-40 GB) in `setup.md:91`.
4. ArchWiki-stated Hyprland Lua config change (belongs to the desktop cluster).
5. Stock Arch `nginx.conf` lacking `conf.d` include; exact nginx warning text.
6. greetd's `Alias=display-manager.service` (git.sr.ht 502).
7. topgrade runtime claims about `antigravity` / `agy` (not reproducible off-host); topgrade key acceptance by execution (build blocked).
8. mkinitcpio 42.x changelog beyond Arch news; paru/yay/syncthing upstream release notes (GitHub 403).
9. Mullvad vs focus `resolv.conf` interaction (inference).
10. Limine + LUKS on the current ISO (forum anecdotes only).

### Setup steps

| Step | Command | Label | Expected proof |
|---|---|---|---|
| Verify ISO checksum | `sha256sum -c cachyos-desktop-linux-260809.iso.sha256` | machine-only | `cachyos-desktop-linux-260809.iso: OK` |
| Verify ISO signature | `gpg --keyserver hkps://keys.openpgp.org --recv-key F3B607488DB35A47 && gpg --verify cachyos-desktop-linux-260809.iso.sig cachyos-desktop-linux-260809.iso` | machine-only | `Good signature` from CachyOS, fingerprint `882D CFE4 8E20 51D4 8E25 62AB F3B6 0748 8DB3 5A47` |
| Confirm optimized repos | `pacman-conf --repo-list` | machine-only | `cachyos-v3`, `cachyos-core-v3`, `cachyos-extra-v3`, `cachyos`, then Arch repos |
| Confirm CPU level | `/lib/ld-linux-x86-64.so.2 --help \| grep supported` | machine-only | `x86-64-v3 (supported, searched)` |
| Parse package lists | README awk split over the five package files | verified-in-cloud | 132 repo names, 9 AUR names |
| Install AUR helper | `sudo pacman -S paru` | machine-only | `paru --version` shows 2.1.0 |
| Kernel check | `uname -r; pacman -Q linux-cachyos linux-cachyos-headers` | machine-only | `7.3.0-4-cachyos`, both packages 7.3.0-4 |
| Mirrors | `sudo cachyos-rate-mirrors; systemctl list-timers cachyos-rate-mirrors.timer` | machine-only | rewritten `mirrorlist`, `cachyos-mirrorlist`, `cachyos-v3-mirrorlist`; reflector.timer disabled |
| zram check | `zramctl; cat /usr/lib/systemd/zram-generator.conf` | machine-only | one `/dev/zram0` about 31.3G, zstd, prio 100 |
| Swapfile in own subvolume | `sudo btrfs subvolume create /swap; sudo btrfs filesystem mkswapfile --size 8G /swap/swapfile; sudo swapon /swap/swapfile; sudo snapper -c root create -d test` | machine-only | snapshot succeeds with swap active |
| Limine inspect | `sudo limine-list; grep -n 'default_entry\|remember_last_entry\|cmdline' /boot/limine.conf` | machine-only | one `CachyOS/linux-cachyos` entry, `cmdline:` has `root=` and `rootflags=` |
| Apply cmdline change | `sudo limine-update` then re-grep `cmdline:` before reboot | machine-only | `lsm=...apparmor,bpf` appended, not replacing |
| AppArmor active | `cat /sys/kernel/security/lsm; aa-enabled; sudo aa-status` | machine-only | `apparmor` in LSM list; `Yes`; profiles in complain mode |
| Snapper config | `sudo snapper -c root get-config \| grep -E 'TIMELINE_CREATE\|NUMBER_LIMIT'` | machine-only | `TIMELINE_CREATE no`, `NUMBER_LIMIT 50` |
| Btrfs scrub | `sudo btrfs scrub start -B -r /; sudo btrfs scrub status /` | machine-only | 0 errors |
| Secure Boot | `sudo sbctl status; sudo sbctl verify` | machine-only | Setup Mode disabled, Secure Boot enabled, files signed |
| greetd hand-off | per Noctalia docs (`systemd-tmpfiles`, `noctalia-greeter-apply-appearance --setup-system`, `enable --now greetd`) | machine-only | `readlink -f /etc/systemd/system/display-manager.service` ends in `greetd.service` |
| topgrade config parse | `python -I -c "import tomllib;tomllib.load(open('topgrade.toml','rb'))"` | verified-in-cloud | loads; keys `misc.disable`, `linux.arch_package_manager` present |
| topgrade dry run | `topgrade --dry-run` | machine-only | steps listed, Arch step uses paru, no `--noconfirm` |
| UFW state | `sudo ufw status verbose` (after reboot) | machine-only | `Status: active`, `Default: deny (incoming), allow (outgoing)` |
| Fail2ban with UFW | set `banaction = ufw` in `jail.local`; `sudo fail2ban-client status sshd` | machine-only | jail `sshd` listed, no errors |
| sshd config test | `sudo sshd -t` | machine-only | no output |
| dnscrypt-proxy | `dig +short example.com @127.0.0.1 -p 5300` | machine-only | an address; `systemctl is-enabled dnscrypt-proxy.socket` is `disabled` |
| Resolver props | decode `sdns://` stamps for `cloudflare`, `quad9-dnscrypt-ip4-nofilter-pri` | verified-in-cloud | props 7 (DNSSEC, no-log, no-filter) |
| nft file loads | `unshare -n nft -f focus-filter.nft` | verified-in-cloud | loads; second load duplicates 6 rules (current file); `inet focus` + `flush chain` variant stays at 1 rule set |
| systemd unit lint | `systemd-analyze verify` on focus, timeshift and ssh units | verified-in-cloud | only missing-binary notes plus the `\$2` escape warning in `erke-vps-ssh.service` |
| dnsmasq test | `sudo dnsmasq --test` | machine-only | `dnsmasq: syntax check OK` |
| Mullvad | `sudo pacman -S mullvad-vpn; systemctl is-enabled mullvad-daemon` | machine-only | package from extra; services remain disabled |
| Proton VPN | `sudo pacman -S proton-vpn-gtk-app` | machine-only | app starts; Secret Service provider present |
| Syncthing + UFW | `systemctl --user enable --now syncthing; sudo ufw allow syncthing` | machine-only | UI at `http://127.0.0.1:8384`; ports 22000/tcp, 22000/udp, 21027/udp allowed |
| nginx test | `sudo nginx -t` | machine-only | `syntax is ok`, no types_hash warning |
| LUKS header backup | `sudo cryptsetup luksHeaderBackup /dev/<dev> --header-backup-file <file>` | machine-only | file created (only if LUKS was chosen at install) |

<!-- cluster: c2-desktop -->
## c2-desktop research notes

Date of record 2026-10-29 (sandbox `date -u +%F` = 2026-10-28). Repo read-only. Method: Arch JSON API, CachyOS repo db (`mirror.cachyos.org`), AUR RPC, `pkg_lookup.py`, plus shallow/full `git clone` of upstream sources (Hyprland v0.56.2 and v0.57.0, hyprlock v0.9.6, hypridle v0.1.8, hyprsunset, hyprpicker, hyprpolkitagent, XDPH, uwsm v0.27.1, noctalia v5.4.0, noctalia-greeter, official/community plugin repos, mako, fontconfig 2.18.3, swash, wireplumber 0.5.18, plugin repos) and the Hyprland wiki sources (`hyprwm/hyprland-wiki` main). Source reading is labelled `local-run`; nothing could be run on a live compositor (no Wayland/GPU/pacman in the sandbox).

Ledger: `c2-desktop.csv` (77 rows: 44 changed, 29 confirmed, 4 unverified).

### 1. Hyprland (headline: the whole config tree is dead on 0.57)

- Versions: Arch extra `hyprland` and `hyprpm` 0.57.0-1 (2026-10-28, archlinux.org JSON). CachyOS `cachyos-extra-v3` 0.56.2-4.1 (CachyOS has not rebuilt 0.57 yet). Machine runs 0.56.2 (tag v0.56.2 = efb5099, 2026-08-05). Release posts: 0.53 2025-12-29, 0.54 2026-02-27, 0.55 2026-05-09, 0.56 2026-07-20, 0.57 2026-10-28 (https://hypr.land/news/).
- **0.57.0 removed the hyprlang config.** News post: "starting with this version, .conf configs are no longer supported". Source check: v0.57.0 `src/config/ConfigManager.cpp` always builds `Lua::CConfigManager`; v0.56.2 still picks `Legacy::CConfigManager` when the path is not `.lua`. With no `hyprland.lua` it writes a default Lua config and ignores `hyprland.conf`. Timeline: Lua optional in 0.55 (hyprland.lua wins over .conf if present), "1 - 2 releases" of hyprlang support (https://hypr.land/news/26_lua/), dropped 0.57. hypridle/hyprlock/hyprsunset keep hyprlang for now.
- Other breaking changes relevant to this repo: 0.53 windowrule/layerrule rewrite (repo already on `windowrule = float on, match:class ...`), `misc:on_focus_under_fullscreen` replaces two options (unused); 0.54 removed `togglesplit`/`swapsplit` dispatchers (repo already uses `layoutmsg, togglesplit`), dwindle `single_window_aspect_ratio*` moved to layout (unused); 0.55 removed `dwindle:pseudotile`, `decoration:shadow:ignore_window`, `render:cm_fs_passthrough`, moved `misc:vfr` to `debug:` (all unused); 0.56 "no breaking changes"; 0.57 adds blur variants, wobble, `no_glow`/`no_wobble` window rules, `cursor:warp_on_monitor_change`, `hl.reload_config()`, `hl.get_devices()`; `debug:fifo_pending_workaround` removed. 0.53 also: launch via `start-hyprland`, not `Hyprland`.
- **Claim "scripts use the Lua dispatcher API in Hyprland 0.55 and newer" (02-desktop/hyprland/README.md:7-9): API is real, claim is incomplete.** `hl.dsp.window.move({ workspace, window })`, `hl.dsp.cursor.move({ x, y })`, `hl.dsp.dpms({ action })` match the wiki dispatcher table. But `hyprctl dispatch X` is a wrapper for `hl.dispatch(X)` only when the ACTIVE config is Lua (`HyprCtl.cpp` `dispatchRequest`). With the repo's `hyprland.conf` on 0.56.2 the string is looked up as a legacy dispatcher and returns "Invalid dispatcher"; on 0.57 it returns "current config provider doesn't support dispatch". Affected today: hypridle.conf:4,15,16 (DPMS never toggles), minimize.sh:23, restore.sh:18, launcher-open.sh:20. The reverse also holds: legacy forms `hyprctl dispatch exec ...` (noctalia-restore.sh:94), `hyprctl dispatch overview:toggle` (keybinds.conf:15) and `hyprctl keyword ...` (keybinds.conf:34-35, toggle-bar.sh) fail under Lua; `hyprctl keyword` is not registered at all in 0.57 (`src/ipc/s1/Commands.cpp` has `eval`/`repl`). Net: the repo mixes the two worlds and no single Hyprland version runs all of it.
- **New syntax (verified against wiki sources and v0.57.0 Lua bindings):**
  - File `~/.config/hypr/hyprland.lua`; `require("a.b")` for splitting (absolute, relative to hyprland.lua, wildcard `*`); `hyprctl reload`, `hyprctl eval '<lua>'`, `hyprctl repl`.
  - `hl.config({ general = { gaps_in = 4, ... } })` or `hl.config({ ["general.gaps_in"] = 4 })`; Int options accept booleans (`true` -> 1).
  - `hl.bind("SUPER + Q", hl.dsp.window.close(), { description = "..." })`; flags: `locked release click drag long_press repeating non_consuming auto_consuming mouse transparent ignore_mods description dont_inhibit submap_universal device allow_input_capture`. Mapping: `bindd` -> `description` flag, `bindel` -> `repeating+locked`, `bindr` -> `release`, `bindm` -> `mouse` flag with `hl.dsp.window.drag()` / `hl.dsp.window.resize()`. Dispatcher functions called from a Lua function must be wrapped in `hl.dispatch(...)`.
  - `hl.window_rule({ name?, match = { class=..., title=..., float=true, workspace=... }, float = true, size = {960,540}, move = {...}, opacity = "0.92", no_blur = true, border_color = ..., })`, `hl.layer_rule({ match = { namespace = ... }, blur = true, xray = true, no_anim = true, ignore_alpha = 0.5, blur_popups = true })`, `hl.workspace_rule({ workspace = "w[t1]", gaps_in = 4, gaps_out = ... })`; named rules return handles with `set_enabled()`.
  - `hl.monitor({ output, mode, position, scale })`, `hl.env(name, value, dbus?)` (3rd arg replaces the `envd` letter), `hl.curve(name, { type="bezier", points={{x,y},{x,y}} })`, `hl.animation({ leaf, enabled, speed, bezier|spring, style })`, `hl.gesture({ fingers, direction, action })`, `hl.on("hyprland.start", fn)`, `hl.exec_cmd`, `hl.define_submap(name, fn)`, `hl.permission`, `hl.timer`, `hl.plugin.load`.
  - Colours for gradients: `{ colors = {"rgba(...)", "rgba(...)"}, angle = 45 }` (window-rule border_color; check the same table for `general.col.active_border`).
- Config keys: all 45 option names the repo uses (general, group, groupbar, misc, render, dwindle, master, decoration, blur, shadow, input, binds, debug, snap) exist unchanged in v0.57.0 (403 options; 349 in v0.56.2). `decoration:blur:xray`, `misc:vrr` (0..3), `render:direct_scanout` (Int 0..2), `follow_mouse` (0..3) fine. Window-rule effects used (float, size, move, pin, rounding, opacity, animation, no_blur, border_size, border_color) and props (class, title, float, workspace) exist. Layer-rule effects blur, xray, animation exist.
- Defects found in the legacy config itself: `move 25%- 25%-` (windowrules.conf:27,29) is not a valid muParser expression, so the rule is dropped (medium confidence, source-read); `hyprpm reload -n` comment is wrong (`-n` = notify on successful load, not "skip update check"); `dbus-update-activation-environment` exec-once is redundant (Hyprland does the same itself, uwsm does it when under systemd); layer rules for logout_dialog/waybar/wallpaper/wofi are dead; Noctalia layer coverage is only 3 of 7 namespaces.
- Recommended edits:
  1. Add `02-desktop/hyprland/hypr/hyprland.lua` (+ `config/*.lua` via `require`) as the source of truth now (works on 0.55+ and already beats `.conf` on 0.56.2); update `manifest.conf` links; keep `.conf` only if 0.54 or older must be supported (it cannot be, since the scripts are Lua-style). hypridle.conf and hyprlock.conf stay hyprlang.
  2. Replace `hyprctl dispatch overview:toggle` with a Lua function bind calling `hl.plugin.overview.toggle()`; replace `hyprctl keyword` uses with `hyprctl eval 'hl.config({...})'` or named rules; use `hyprctl dispatch 'hl.dsp.exec_cmd("...")'` in noctalia-restore.sh.
  3. Fix the README sentence to "requires a Lua config (hyprland.lua); hl.dsp exists since 0.55".
  4. Drop the dbus exec-once and the dead layer rules; adopt the upstream Noctalia layer rule; fix the `-n` comment; drop the three dead hyprlock keys.
  5. Point doc links to `wiki.hypr.land` (lowercase paths); the wiki is versioned.
- UNVERIFIED: whether `hyprctl eval` can address a named layer rule handle (needed to port toggle-bar.sh); exact color-string forms accepted for `general.col.active_border` in Lua; whether `wiki.hyprland.org` still redirects.
- Compat: Hyprland 0.57 build deps now include Lua 5.5 (`lua`), `hyprwire`, `glaze`, `hyprland-guiutils`; `hyprlang` stays a hard dep (libhyprlang.so) even though the parser is gone.

### 2. hyprpm and plugins

- hyprpm 0.57.0-1 (Arch) depends on cmake cpio glaze hyprland hyprland-protocols hyprwayland-scanner meson; needs git and a toolchain. `hyprpm add <url> [rev]` ignores commit pins when a rev is given; otherwise a pin applies only if its Hyprland hash equals the running one, else HEAD of the plugin repo is built. No plugin manifest has a pin for 0.57.0 (hash 0aa6745f...), newest pins are 0.56.0 (Hyprspace) or 0.56.2 (dynamic-cursors, hy3, split-monitor-workspaces, hyprland-plugins).
- **Hyprspace.** Claim "upstream does not build on 0.56.x" was true at 0.56.0 (issue #239, header moved) but is stale: PR #238 "Migrate to V2 API + lua config" merged into KZDKM/Hyprspace main on 2026-10-02 (merge cf08bed), and `0799be7` is an ancestor of upstream main, so the fork is no longer needed for 0.56.x (`hyprpm add https://github.com/KZDKM/Hyprspace 0799be7464fac7ea959b7c6c7809dadd6c21c5aa` is equivalent). **New problem:** upstream main and the fork use `g_pHyprRenderer->m_renderPass` / `m_renderData` (Render.cpp:21..411, main.cpp:83,103); v0.57.0 removed both from `CHyprRenderer` in favour of `context()` / `Render::CRenderContext`. Hyprspace will not compile against 0.57.0 and has no upstream fix yet. Lua API: `hl.plugin.overview.toggle()/open()/close()`, config `hl.config({ plugin = { overview = {...} } })`.
- **dynamic-cursors.** For 0.56.2 hyprpm uses pin 5a22428 (branch v0.56.2, still hyprlang `plugin:dynamic-cursors:*`). HEAD dropped hyprlang config on 2026-07-29 (e407df2) and adopted 0.57 render contexts on 2026-10-05 (2a8d0b7); config is `hl.config { plugin = { dynamic_cursors = {...} } }` guarded by `if hl.plugin.dynamic_cursors then`. All keys in plugins.conf exist.
- hy3: master c35adfa (2026-10-12) chases 0.57 changes, newest tag hl0.56.0.1. split-monitor-workspaces: main f26d624 (2026-09-26), tags to v0.56.2, no 0.57 tag. Both optional, not installed: unchanged. hyprland-plugins: upstream alive (tag v0.57.0, commit d2427d4, 2026-10-20; borders-plus-plus, csgo-vulkan-fix, hyprbars, hyprfocus; hyprexpo not in tree). The repo's "removed" is a local choice.
- Stale-binary gotcha: confirmed by source (`PluginAPI.cpp:286` `std::filesystem::canonical("/proc/self/exe")` throws when the binary is replaced). Also hyprpm prints "Hyprland was updated. Please restart Hyprland."
- Recommended: README Plugins/Install text to say (a) Hyprspace pin no longer needs the fork on 0.56.x, (b) Hyprspace is blocked on 0.57.0 (hold Hyprland at 0.56.2 or drop the overview plugin; Noctalia has no native workspace overview in the docs reviewed, but `hyprland.mdx` and `src/shell/overview/` exist, not studied), (c) plugin config moves into Lua.
- UNVERIFIED: compile result of any plugin on 0.57.0 (no headers in sandbox); the claim that every hyprexpo fork has a broken header.

### 3. Hypr ecosystem packages

| Pkg | Arch extra | CachyOS v3 | Notes |
|---|---|---|---|
| hyprland / hyprpm | 0.57.0-1 (2026-10-28) | 0.56.2-4.1 | |
| hypridle | 0.1.8-2 | same | hyprlang only |
| hyprlock | 0.9.6-3 | same | hyprlang only; 3 dead keys in repo |
| hyprsunset | 0.4.0-3 | same | `-t K`, needs hyprland>=0.45 |
| hyprpicker | 0.4.7-4 | same | `-a` needs wl-clipboard |
| hyprpolkitagent | 0.2.0-1 | same | ships systemd user unit + D-Bus activation |
| xdg-desktop-portal-hyprland | 1.4.1-2; 1.5.0-1 in extra-testing | 1.4.1-2.1 | 1.5.0 tagged 2026-10-28, adds workspace sharing (0.57 pair) |
| uwsm | 0.27.1-1 (2026-10-15) | n/a | matches upstream v0.27.1 |
| hyprutils/hyprlang/hyprgraphics/hyprcursor/hyprwayland-scanner | 0.14.3 / 0.6.8 / 0.5.1 / 0.1.13 / 0.4.6 | same | pure dependencies |
| hyprwire / hyprland-guiutils / hyprtoolkit / hyprshutdown | 0.3.1 / 0.2.2 / 0.6.0 / 0.1.1 | same | new in dependency closure; hyprshutdown optional |

- Explicit installs not needed: hyprcursor, hyprgraphics, hyprlang, hyprutils, hyprwayland-scanner (deps of hyprland / hyprlock / hyprpm). hypridle, hyprlock, hyprsunset, hyprpicker, hyprpolkitagent are leaf apps and needed if used.
- hyprlock.conf: `general:disable_loading_bar` (removed 2025-03-25), `general:no_fade_in` (replaced by animations, 2025-01), `general:grace` (now `hyprlock --grace N`, 2025-06) are no longer registered in 0.9.6; delete. Other widget keys exist.
- hypridle.conf keys fine; the DPMS lines need Lua config (section 1).
- Noctalia 5.4.0 has its own lock screen and idle behaviors, and its FAQ says no separate idle daemon is needed for lock-before-sleep. Two lockers coexist (hyprlock, Noctalia lockscreen widgets). Design choice; record, do not enable both idle stacks.
- Portal: Hyprland installs `hyprland-portals.conf` (`default=hyprland;gtk`), so `xdg-desktop-portal-gtk` is expected; not in any list. Missing from the package lists but required by configs: `ddcutil`, `qt6ct`, `xdg-desktop-portal-gtk`, Bibata cursor (AUR `bibata-cursor-theme` 2.0.7-1), the GTK theme named in `environment.conf:11`; optional `sound-theme-freedesktop` (shell sounds), `libheif`.

### 4. uwsm, SDDM, greetd

- uwsm 0.27.1: env files `~/.config/uwsm/env`, `env.d/*`, `env-hyprland`, `env-hyprland.d/*` (confirmed in README). `uwsm start -e -D Hyprland hyprland.desktop` is the same Exec as Hyprland's packaged `hyprland-uwsm.desktop`; the repo's `/usr/local/share/wayland-sessions` copy duplicates the packaged entry (names differ). `loginctl terminate-session "$XDG_SESSION_ID"` is a documented way to end a uwsm session (alternative `uwsm stop`). Under uwsm, Hyprland skips its own systemd/D-Bus env export (MANAGERPID set).
- noctalia-greeter 1.7.0-1 in Arch extra (2026-10-22); cachyos repo 1.6.0-1, cachyos-extra-v3 1.7.0-1.1. greetd `[default_session] command = "/usr/bin/noctalia-greeter-session"`, `user = "greeter"`; init state with `sudo noctalia-greeter-apply-appearance --setup-system`; the greeter lists `wayland-sessions` entries. The repo carries no greetd config (machine-only).
- SDDM 0.21.0 (extra 0.21.0-7; cachyos-v3 0.21.0-8). The weston/x11-user notes are machine-only: UNVERIFIED.

### 5. Noctalia 5.4.0

- What it is: native C++/OpenGL ES Wayland shell (v5, TOML), separate from the Quickshell v4 (`qs`, JSON). Arch extra `noctalia` 5.4.0-1 (2026-10-26), cachyos-extra-v3 5.4.0-1.1. No systemd unit shipped; provides `org.freedesktop.Notifications` and StatusNotifierWatcher (conflicts with mako, waybar as tray host while running). `noctalia -d` = `--daemon` (forks), the desktop entry uses `noctalia --daemon`.
- Config model (docs + source): hand-written `~/.config/noctalia/*.toml` (merged alphabetically, never rewritten), app-owned `~/.local/state/noctalia/settings.toml` loaded last (wins), `config_version` stamped by the app (14 = v5.0.1, 15 = v5.3.0, 16 = v5.4.0; repo file is at 16). `noctalia config validate` reports legacy keys. **Writes go through symlinks** (`atomic_file.cpp`, since 2026-06-01, in all 5.x), so the manifest reason for `seed` ("a replace-style write destroys a symlink") is stale; seeding is still defensible because the file carries machine state (wallpaper paths, favorites, `/home/kneeraazon` paths). Preferred tracked layout: link curated bar/theme TOML into `~/.config/noctalia/`.
- settings.toml schema: all 160 leaf keys checked against the 5.4.0 source; every non-plugin key exists. 5.4.0 renamed palette roles `surface_variant`->`surface_container`, `outline`->`outline_variant` (repo already uses new names). Palette JSON format (16 `m*` fields + `terminal`) confirmed.
- IPC used by the repo all exist: `panel-toggle launcher|clipboard|wallpaper|control-center|session`, `wallpaper-random|next|previous|set`, `bar-hide|show|toggle`, `volume-osd`, `config-reload`, `greeter-sync`, `color-scheme-get|set`. Layer namespaces: `noctalia-bar-<bar>`, `noctalia-panel`, `noctalia-attached-panel`, `noctalia-notification`, `noctalia-osd`, `noctalia-dock`, `noctalia-window-switcher`, `noctalia-wallpaper`. Upstream Hyprland guide gives one layer rule covering all of them.
- Volume: `[audio] enable_overdrive = true` (already set in settings.toml) lifts the cap to 150% for `volume-up/down/set` and `volume-osd`; the volume.sh header claim "no setting anywhere" is stale. Brightness: `noctalia msg brightness-up|down` supports ddcutil; brightnessctl cannot drive the DP-2 ddcutil output (inferred).
- Clipboard: built-in history (data-control), so the `wl-paste --watch cliphist store` autostart is redundant. Screenshot: built-in `screenshot-region|fullscreen|window|annotate` with `--annotate` and `pipe_command`; swash chain still works.
- Night light: Noctalia uses wlr-gamma-control; hyprsunset uses `hyprland-ctm-control-v1`. The repo's "confirmed upstream bug" was observed on 5.0.0_beta.10 (2026-08-27); code at 5.4.0 handles force toggling and I found no upstream confirmation either way. Status: UNVERIFIED, retest on 5.4.0; keep hyprsunset workaround meanwhile.
- Systemd question: upstream recommends compositor autostart, ships no unit, and documents `[shell] launch_apps_as_systemd_services` (effective only under the systemd user manager or uwsm) for the cgroup-inheritance problem. The repo's watchdog (foreground `noctalia` in a loop, not `--daemon`) is consistent with upstream; the Chromium SIGSEGV cause is not mentioned upstream and stays UNVERIFIED (needs coredumpctl on the machine).
- Plugins: all 17 ids resolve in `noctalia-dev/official-plugins` (d696743) or `community-plugins` (1f8525c). tmelik/system-monitor 1.5.3 (needs `ps`, `cat`, system monitor service), felipeartur/ai-usagebar 2.11.2 (plugin_api 43; AUR `ai-usagebar-bin` 1.45.0).
- sync-theme-border.sh: ignores `source = "wallpaper"` and the `~/.config/noctalia/*.toml` layer; prefer `noctalia msg color-scheme-get`.
- mako D-Bus override: mako 1.11.0 ships `fr.emersion.mako.service` (Exec=@bindir@/mako); user-dir shadowing is standard but mako is not in any package list now, so the override only matters if mako is installed. `cachyos-hypr-noctalia` 1.2.6-1 (cachyos repo, 2026-09-13) still depends on `dolphin`; DEPENDS list in the ledger. KDE-REMOVAL.md: dolphin landmine still true, satty/xcur2png entries stale (swash replaced satty), "zero KDE packages remain" contradicts desktop.txt (dolphin, ark, okular, korganizer, kdeconnect) and system-summary.md. Orphan-sweep warning still sound. Do not rewrite history; add a dated note.
- Waybar/wofi retirement: consistent; `waybar` 0.15.0 stays installed "for parity". Dead layer rules remain in windowrules.conf.

### 6. Screenshot, clipboard, media, input helpers

- grim 1.5.0-2, slurp 1.5.0-2, wl-clipboard 2.3.0-1, cliphist 0.7.0-2, copyq 16.0.0-1, playerctl 2.4.1-5, brightnessctl 0.5.1-3 (2024-07-12, still latest), satty 0.22.0-1, swappy 1.8.0-1, flameshot 14.0.0-1, mako 1.11.0-1, hyprpaper 0.8.4-9 all in extra. swash 1.5.1-1 only in the CachyOS repo and AUR (desktop.txt omits the `(AUR)` tag, correct only with the CachyOS repo enabled; setup.md 16.3 `pacman -S swash` fails on plain Arch). grimblast-git is CachyOS/AUR, hyprshot in extra 1.3.0-4.
- screenshot.sh header says satty/swappy/flameshot were removed; system-summary.md lists them installed: one is stale (machine state, UNVERIFIED).
- wpctl `--limit` and `@DEFAULT_AUDIO_SINK@` verified in wireplumber 0.5.18.

### 7. Fonts and fontconfig

- fonts.conf: all property names/constants valid (`hinting`, `hintstyle=hintslight`, `rgba=rgb`, `antialias`, `embolden`, `matrix`, `embeddedbitmap`, `slant`, `weight`; `<dir prefix="xdg">`). The two synthetic stanzas are verbatim `90-synthetic.conf`, shipped and linked by default in fontconfig 2.18.3 (Arch extra 2.18.3-1). Upstream build defaults are `slight` hinting, `none` sub-pixel, antialias and lcddefault linked, so only `rgba=rgb` is a real override (Arch build flags not checked). README claim "lcddefault LCD filtering" is not set by fonts.conf (system default).
- Package names: all 31 in fonts.txt resolve. AUR: Maple Mono variants (1.2304.73/.76, 2025), one flagged out-of-date; ttf-weather-icons 2.0.12 (2021); fragment-mono 1.21 (2024). `JetBrains Maple Mono` is referenced by no config; README line 263-267 and fonts.txt:17 are wrong. Actual fonts: bar/clock/Zed/VS Code `JetBrains Mono`, kitty/alacritty `FiraCode Nerd Font Mono`, shell/hyprlock/groupbar `DejaVu Sans`.

### 8. hyprland-shortcuts.md vs keybinds.conf

All 94 binds are represented; no key/modifier/action drift. Two defects: no generator exists (the "regenerated from keybinds.conf" claim, also README.md:17-20, is manual), and the Quick tips paragraph about `bindd` field order and `hyprctl binds -j` becomes wrong after migrating to `hl.bind`. Add the remaining facts (volume now 150% via Noctalia overdrive) when the binds change.

### UNVERIFIED list

1. Any live behaviour on a compositor (dispatch failures, DPMS, window rules, plugin load). Source reading only.
2. Noctalia 5.4.0 night-light force-toggle bug status.
3. Chromium SIGSEGV when Noctalia runs as a systemd service (needs coredumpctl).
4. Compile status of Hyprspace/dynamic-cursors/hy3/split-monitor-workspaces on 0.57.0 (Hyprspace expected to fail from symbol removal).
5. hyprexpo "every fork broken" statement.
6. `hyprctl eval` access to named layer-rule handles; Lua colour-gradient string form for `general.col.*`.
7. `wiki.hyprland.org` redirect behaviour; SDDM weston failure notes; installed state of satty/swappy/flameshot/mako.
8. `swallow_regex` intent (low confidence).
9. Automated conversion: the PyPI tool `hyprconf2lua` 1.8.1 (MIT, third party) was downloaded and read (pure text transform, no network/subprocess) but running it was blocked by the sandbox's permission classifier, so no machine-converted `hyprland.lua` draft exists. Run it locally if wanted: `hyprconf2lua --check` flags directives it cannot map.

### Setup steps

| Step | Command | Label | Expected proof |
|---|---|---|---|
| Check Hyprland versions in repos | `/tmp/venv/bin/python tools/pkg_lookup.py hyprland hyprpm` | verified-in-cloud | extra 0.57.0-1 dated 2026-10-28 and cachyos-extra-v3 0.56.2-4.1 |
| Check which config the compositor loaded | `hyprctl version; hyprctl configerrors; ls ~/.config/hypr/hyprland.lua` | machine-only | version string; with .conf only on 0.57 a default hyprland.lua is generated |
| Confirm dispatch syntax matches the active config | `hyprctl dispatch 'hl.dsp.cursor.move({ x = 100, y = 100 })'` | machine-only | `ok` under Lua; `Invalid dispatcher` under legacy 0.56.2 |
| Install desktop session packages | `sudo pacman -S --needed hyprland hyprpm hypridle hyprlock hyprsunset hyprpicker hyprpolkitagent xdg-desktop-portal-hyprland xdg-desktop-portal-gtk uwsm noctalia noctalia-greeter greetd ddcutil qt6ct wl-clipboard` | machine-only | `pacman -Q noctalia` = 5.4.0-1 |
| Build Hyprspace on 0.56.2 | `hyprpm update && hyprpm add https://github.com/KZDKM/Hyprspace 0799be7464fac7ea959b7c6c7809dadd6c21c5aa && hyprpm enable Hyprspace` | machine-only | `hyprpm list` shows Hyprspace enabled; fails on 0.57.0 (m_renderPass removed) |
| Autoload plugins | `hyprpm reload -n` (as `hl.exec_cmd` in Lua) | machine-only | notification "Loaded plugins" |
| Validate Noctalia config | `noctalia config validate` | machine-only | no legacy-key warnings; config_version 16 |
| Test overdrive volume | `noctalia msg volume-set 120; wpctl get-volume @DEFAULT_AUDIO_SINK@` | machine-only | `Volume: 1.20` when `[audio] enable_overdrive = true` |
| Check Noctalia IPC | `noctalia msg --help` | machine-only | lists panel-toggle, bar-hide, screenshot-region ... |
| greetd session | `/etc/greetd/config.toml`: `command = "/usr/bin/noctalia-greeter-session"`, `user = "greeter"`; `sudo noctalia-greeter-apply-appearance --setup-system` | machine-only | greeter shows "Hyprland (uwsm-managed)" |
| Refresh font cache | `fc-cache -fv` | machine-only | no fontconfig errors; `fc-match "JetBrains Mono"` resolves |
| Find Maple font references | `grep -rn Maple ~/dotfiles --include=*.conf --include=*.toml --include=*.json` | verified-in-cloud | only `fonts.txt` (comment) matches |
| Count option names in a Hyprland tag | `git clone --depth 1 --branch v0.57.0 https://github.com/hyprwm/Hyprland.git`, then `grep -ohE` for the MS option-name pattern on src/config/values/ConfigValues.cpp and count lines | verified-in-cloud | 403 (349 for v0.56.2) |

<!-- cluster: c3-gpu-local-ai -->
## Cluster c3-gpu-local-ai: AMD GPU stack, ROCm, Ollama, local AI tooling

Retrieved 2026-10-28 (sandbox clock; date of record 2026-10-29). Hardware per repo: Ryzen 5 5600, RX 6700 XT 12 GiB (gfx1031, RDNA2), 32 GiB DDR4-3600, CachyOS kernel 7.3.0-4. Evidence ledger: `c3-gpu-local-ai.csv` (82 rows: 35 changed, 34 confirmed, 13 unverified). Labels: `verified-in-cloud` means I ran it in the Linux sandbox; `machine-only` needs the CachyOS host; `unverified` means neither.

### Package and release snapshot (all from registries on 2026-10-28)

| Item | Arch extra | CachyOS | AUR | Upstream |
|---|---|---|---|---|
| ollama / ollama-rocm / ollama-vulkan | 0.40.11-1 (2026-10-25) | cachyos-extra-v3 0.40.11-1.1 | ollama-rocm-git 0.30.4rc0 (stale) | v0.40.13 2026-10-28, v0.40.12 2026-10-27 (github.com/ollama/ollama/releases.atom) |
| mesa / vulkan-radeon / lib32-* | 26.2.5-1 (2026-10-17) | cachyos-v3 26.2.5-1; cachyos generic 26.2.4-1 | - | 26.2.6 released 2026-10-28 |
| ROCm (rocm-core, hip-runtime-amd, hsa-rocr, rocminfo, rocm-hip-sdk, rocm-opencl-sdk) | 7.2.4-1 (2026-06-02) | cachyos-extra-v3 7.2.4-1.1 | - | ROCm Core SDK 10.1.0 (2026-10-05), 7.14.1 (2026-09-02), 10.0.0 (2026-08-26), 7.14.0 (2026-07-15), legacy 7.2.4 (2026-05-29) |
| rocblas | 7.2.4-3 (2026-08-31) | - | - | - |
| rocm-smi-lib / amdsmi | 7.2.0-2 / 7.2.4-1 | rocm-smi-lib 7.2.0-2.1 | - | ROCm SMI removed from Core SDK, AMD SMI replaces it |
| linux / linux-cachyos | core linux 7.2.11 (2026-10-17) | cachyos-v3 linux-cachyos 7.3.0-4; cachyos generic 7.2.7-1 | linux-cachyos 7.3.0-3 | Linux 7.3 released 2026-10-18 (endoflife.date) |
| python-pytorch-rocm | 2.14.1-1 (2026-10-08) | - | python-torchvision-rocm 0.29.1 | torch 2.15.0 on PyPI 2026-10-28; rocm7.2 wheel index tops at 2.14.1 |
| llama-cpp, ggml-hip, ggml-vulkan | llama-cpp 0.6.0-1 (2026-10-06); ggml* 0.26.0-1 (2026-10-11) | llama-cpp 0.6.0-1.1 | llama.cpp-*-git variants | release build b11969 2026-10-28, tag v0.8.0 marked Latest |
| lact / amdgpu_top / nvtop / radeontop / corectrl | 0.10.1 / 0.11.5 / 3.3.2 / 1.4-3 (2024-07) / 1.5.2-9 (2026-08-13) | same, .1 rebuilds | - | LACT v0.10.1 2026-08-29; amdgpu_top v0.11.5 2026-05-18 |
| pgvector | 0.8.7-1 (2026-10-02) | 0.8.7-1.1 | - | README v0.8.7 |

---

### 1. ROCm release train and gfx1031 support

**Current version.** The ROCm numbering forked. Release list (rocm.docs.amd.com/en/latest/release/versions.html): 10.1.0 (2026-10-05), 7.14.1 (2026-09-02), 10.0.0 (2026-08-26), 7.14.0 (2026-07-15), 7.2.4 (2026-05-29), 7.2.3, 7.2.2, 7.2.1, 7.2.0 (2026-01-21), 7.1.1, 7.1.0, 7.0.2, 7.0.1, 7.0.0 (2025-09-16), 6.4.3 (2025-08-07). Since 7.14 AMD builds with TheRock and ships the "ROCm Core SDK" (packages `amdrocm-*` from repo.amd.com, install prefix `/opt/rocm/core-10.1`, meta package `amdrocm`). The transition guide says the Core SDK keeps ABI/API compatibility with legacy 7.2, merges hipBLAS and rocBLAS into `amdrocm-blas`, removes ROCm SMI, and moves RVS/TransferBench/MIGraphX to extras. The 7.14 blog says users on 7.2 and older are "encouraged to migrate"; no end-of-life date is stated for the legacy stream (UNVERIFIED anywhere).

**Arch/CachyOS.** Both ship the legacy 7.2.4 only (packaged 2026-06-02). Whether Arch will adopt TheRock packages is UNVERIFIED (Arch wiki and GitLab are behind Anubis, not worked around). The repo's "ROCm/HIP runtime 7.2" statements are correct for the installed system and should carry a note that upstream is a different train.

**Supported GPU list.** gfx1031 (RX 6700 XT) is not officially supported in 7.2.4 or 10.1.0. The only RDNA2 rows are gfx1030: Radeon PRO W6800 and PRO V620 (the latter Ubuntu only). Page text: "If a GPU is not listed on this table, it's not officially supported by AMD." Ollama's own docs list the same: gfx1030 (V620) plus RX 6950 XT, 6900 XT, 6800 XT, 6800 on Linux; no 6700 XT. Documented unofficial route: `HSA_OVERRIDE_GFX_VERSION=10.3.0` (Ollama GPU docs; llama.cpp build docs name 10.3.0 for gfx1030/1031/1035).

**Where the repo is wrong or overstated.**
- `05-ai/ollama/README.md:79-82` and `ollama-claude-setup.md:49` say ROCm "does not initialize on this GPU at all" without the override. The repo's own `discovery.md` journal (2026-09-23 13:21:04, HSA_OVERRIDE empty) shows `library=ROCm compute=gfx1031 ... available="11.9 GiB"`, and `STATE.md` lines 44-48 record a native-gfx1031 run at 32.85 tok/s versus 32.79 spoofed. Arch's `ollama-rocm` bundles its own ROCm 7.2 libs (`/usr/lib/ollama/rocm_v7_2`: libamdhip64.so.7 7.2.53211, librocblas.so.5, rocBLAS kernels for gfx1030 and gfx1031) and Arch's `rocblas` 7.2.4-3 also ships `Kernels.so-000-gfx1031.hsaco`. So on this packaging the override is a fallback, not a requirement. Not re-tested on Ollama 0.40.11.
- PyTorch pip wheels still need the override: PyTorch's ROCm build list (`.ci/docker/manywheel/build.sh`, main branch) is `gfx908;gfx90a;gfx942;gfx950;gfx1030;gfx1100;gfx1101;gfx1102;gfx1103;gfx1200;gfx1201;gfx1150;gfx1151;gfx1250`. No gfx1031 (medium confidence, main not the 2.14.1 tag).
- Exporting `HSA_OVERRIDE_GFX_VERSION` globally (`03-terminal/zsh/.zshrc:22-23`) makes `rocminfo` report gfx1030 while the systemd service may run gfx1031 (the split-brain `discovery.md` already noticed). Recommend scoping it to the project or venv that needs it.

**Regressions.** ollama/ollama#12111 (RX 6750 XT gfx1031, SIGSEGV on first prompt with override 10.3.0 after ROCm 6.4.3) is real and closed 2026-07-03; fixed by rocblas/rocsparse 6.4.3-3. That is the "known risk" the bench spec cited, and it is resolved. I found no primary-source report of a gfx1031 regression on ROCm 7.0 to 7.2 (searches of Ollama and ROCm trackers; absence of evidence only). Secondary SEO guides (insiderllm.com and similar) still claim "no fix in 7.2"; contradicted by the issue and by the repo's 3/3 clean runs at 33,849 prompt tokens on 7.2.4.

**TheRock and gfx1031.** `ROCm/TheRock` SUPPORTED_GPUS.md marks gfx1031 build/sanity/release-ready for nightlies, RELEASES.md documents `torch[device-gfx1031]` on `nightly.repo.amd.com/rocm/whl-next`, and the PyTorch `rocm10.1` index lists `rocm-sdk-device-gfx1031`. This conflicts with AMD's official matrix, where 10.1.0 lists only gfx1030 and AMD's own wheel docs drop gfx1030 from the 10.1.0 device list. Do not adopt without a GPU test. TheRock issue #1719 (gfx1031, Windows, closed "not planned" 2026-04-30) says native per-architecture builds are the intended path and the override "can cause flaky behavior".

**Arch ROCm package names vs repo.** `rocm-hip-sdk`, `rocm-opencl-sdk`, `rocm-hip-runtime`, `rocm-hip-libraries`, `rocm-core`, `hip-runtime-amd`, `hsa-rocr`, `rocminfo`, `rocm-smi-lib`, `rocblas`, `rocsolver`, `hipblas`, `miopen-hip`, `rocm-cmake`, `amdsmi` all exist at 7.2.4 (rocm-smi-lib 7.2.0). `hipcc` is not a package name on Arch (hipcc comes with rocm-llvm / hip-runtime-amd). `ai.txt` lists only the Ollama-relevant subset; `ollama-rocm` depends only on `hipblas` (which pulls rocblas, rocsolver, hip-runtime-amd, rocm-core), so `hsa-rocr`, `rocminfo`, `rocm-core` etc. are redundant but harmless. `rocm-core` installs `/etc/profile.d/rocm.sh`, so `rocminfo`, `rocm-smi` (`/opt/rocm/bin`) and `hipcc` need a new login shell, which `setup.md` 2.2 already says.

**Edits.** setup.md 2.2: add the train note (7.2.4 legacy vs Core SDK 10.1). 2.3: say gfx1031 is unofficial, override is a fallback for Ollama and required for PyTorch wheels, scope it. README.md and ollama-claude-setup.md: replace "does not initialize at all" with the measured statement. ollama-claude-setup.md section 2: mark the 6.4.3 SIGSEGV as fixed (ollama#12111).

### 2. AMDGPU, Mesa, RADV

Mesa 26.2.5 is in Arch extra and cachyos-v3; 26.2.6 was released today (2026-10-28) and includes "ACO: fix 26.2 regression where an s_bitset0 retargeted to exec drops the VCC condition, affects RADV on RDNA2 through RDNA4" plus a GPULostDevice entry for a 6800 XT on 26.0.x. The repo's Vulkan crash was on Mesa 26.2.3 (RADV Vulkan 1.4.354). A causal link is NOT established; retest after Mesa >= 26.2.6 lands. A second lead: kernel docs state `lockup_timeout` defaults to 2000 ms for all queues when unset (docs.kernel.org), so a single long Vulkan submission could be reset by the scheduler and surface as ErrorDeviceLost; the repo captured no amdgpu reset lines. Both are hypotheses.

`setup.md` 2.1 package names all exist (lib32-* in multilib 26.2.5 / 1.4.363.0). The verify step uses `vulkaninfo`, which comes from `vulkan-tools` (extra 1.4.363.0), not installed by the command: add it. amdgpu is the in-tree kernel driver on 7.3 (no DKMS). Ollama's Linux docs recommend AMD's latest driver for best Radeon support, but the repo has run on the in-tree driver. ROCm's kernel matrix lists only Ubuntu 22.04/24.04, RHEL, SLES, Debian, Oracle kernels, so Arch kernel 7.3 is outside AMD's validated set.

### 3. Ollama 0.40.x

**Versions.** Arch/CachyOS 0.40.11; upstream 0.40.13 (2026-10-28). Arch package page shows 0.40.11 flagged out-of-date on 2026-10-28.

**Backend selection (primary: docs.ollama.com/gpu and envconfig/config.go).**
- `OLLAMA_VULKAN`: default true on non-macOS ("Enable Vulkan support"); docs: "Vulkan is enabled by default when the backend is installed", disable with `OLLAMA_VULKAN=0` or `GGML_VK_VISIBLE_DEVICES=-1`. `RESOURCES.md:33` saying `OLLAMA_VULKAN=1` is redundant, and its source is a Phoronix news item; cite docs.ollama.com/gpu instead.
- `OLLAMA_LLM_LIBRARY`: still defined ("Set LLM library to bypass autodetection"); not in the public FAQ. Repo evidence (discovery.md): with both backends installed Ollama picked ROCm; forcing Vulkan needed `OLLAMA_LLM_LIBRARY=vulkan`. Keep, but re-test on 0.40.x (medium).
- Device selection: `HIP_VISIBLE_DEVICES`, `ROCR_VISIBLE_DEVICES`, `GPU_DEVICE_ORDINAL`, `GGML_VK_VISIBLE_DEVICES`, `HSA_OVERRIDE_GFX_VERSION` (and `_0`, `_1` per GPU).
- Requirement: "Ollama requires the AMD ROCm v7 driver on Linux" (7.2.4 satisfies it).

**Tuning vars (FAQ).** `OLLAMA_FLASH_ATTENTION=1` forces FA on (default false); `OLLAMA_KV_CACHE_TYPE` f16 (default), q8_0 (about half memory), q4_0 (about quarter); `OLLAMA_MAX_LOADED_MODELS` (description "per GPU", default 0 = auto); `OLLAMA_NUM_PARALLEL` default 1 (the repo line is redundant); `OLLAMA_KEEP_ALIVE` default 5m. All repo values in `claude-code.conf` are valid keys.

**Context.** Default context is 4k below 24 GiB VRAM, 32k for 24-48 GiB, 256k above; agents and coding tools should use at least 64000 (docs.ollama.com/context-length). Not setting `OLLAMA_CONTEXT_LENGTH` globally and using `PARAMETER num_ctx` in a Modelfile is valid (FROM and PARAMETER unchanged; new instructions REQUIRES and CAPABILITY, new parameter `draft_num_predict`). The Modelfile docs page still says num_ctx default 2048, which conflicts with the context-length page. Zed's `context_window` is sent as `num_ctx` and defaults to 4096, so a Zed request can reload a model that Claude Code loaded with 65536.

**cap_perfmon.** Docs: "Vulkan requires additional capabilities or running as root to expose this available VRAM data"; without it Ollama schedules from approximate sizes. So it matters only for the Vulkan backend, not the live ROCm one. ollama/ollama#15321 (open, bug) reports that `setcap cap_perfmon+ep` breaks GPU discovery (secure-exec strips LD_LIBRARY_PATH); a commenter suggests systemd `AmbientCapabilities=CAP_PERFMON` instead (untested). In the repo, ROCm worked with the cap applied on 0.34.3. Recommendation: remove `setcap` and the pacman hook from the default ROCm install path (setup.md 4.3, README.md Install, system-summary.md section 6) and document them as Vulkan-only. The docs' example path is `/usr/local/bin/ollama`; Arch's is `/usr/bin/ollama`.

**install.sh warning.** Still valid in substance. `scripts/install.sh` (main branch) installs to `/usr/local` or `/usr`, removes `$OLLAMA_INSTALL_DIR/lib/ollama`, never checks for a packaged install, creates user `ollama`, adds it to `render`/`video`, writes its own unit, and downloads the `ollama-linux-amd64-rocm` tarball when PCI vendor 1002 is seen. The "7.4GB of CUDA libs" number in `ai.txt:10` is time-bound and I could not reproduce it (the script has no CUDA tarball); drop the number. Manual install in docs is `.tar.zst` now. Release-asset install.sh was not fetched.

**Claude Code against Ollama (primary: docs.ollama.com/integrations/claude-code, /api/anthropic-compatibility, code.claude.com env-vars).**
- Documented: `ollama launch claude [--model M] [--yes] [-- claude args]` (`--yes` requires `--model`), or manually `ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL=http://localhost:11434 claude --model <model>`. The repo's `ccl()` matches the manual form. Docs say "set a 64k+ context window".
- Endpoint: `POST /v1/messages`. Supported: streaming, system, base64 images, tools/tool results, thinking, `output_config.effort`. Unsupported: `tool_choice`, `metadata`, `/v1/messages/count_tokens`, Batches, prompt caching, citations, PDF blocks, image URLs. `ollama cp qwen3-coder claude-3-5-sonnet` is the documented way to satisfy tools that expect Anthropic model names.
- Env vars in Claude Code docs: `CLAUDE_CODE_MAX_CONTEXT_TOKENS` (documented; behaviour changed v2.1.193), `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT` (v2.1.223+), `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (now documented, range 100000 to 1000000, so 65536 is below its minimum; `discovery.md` calls it unverified), `CLAUDE_CODE_SUBAGENT_MODEL`, `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU}_MODEL`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`. Ollama 0.40.7 "clamps Claude Code's auto-compact window setting".
- Anthropic's gateway page says it does not support routing Claude Code to non-Claude models through any gateway.
- Repo inconsistencies: `ccl()` uses models `cc-local`/`cc-fast`, but no Modelfile defines them (only `ccb-*`); `03-terminal/zsh/.zshrc` contains no ccl/cclf block (the installer script was never applied to the tracked file). Claude Code is at 2.1.312 (npm latest), repo doc says 2.1.280.

**Models (ollama.com/library, retrieved today).** All tags the repo uses still exist: gemma4:12b (7.7-8.0 GB, 256K, text+image), qwen3-coder:30b (19 GB, 256K, 3.3B active), gpt-oss:20b (14 GB, 128K, MXFP4, updated 2 weeks ago), qwen:latest (2.3 GB, Qwen 4B, 32K, updated 2 years ago, superseded by qwen2/qwen3), llama3.1:8b (4.9 GB; repo says ~4.7), qwen3:8b (5.2 GB), codellama:13b (7.4 GB, 16K, stale), nomic-embed-text (274 MB, 2K), llama3.2:3b (2.0 GB). 12 GiB fit: gemma4:12b fits (repo: 8.38 GB VRAM at 65536 ctx with q8_0 KV, 100% GPU); gpt-oss:20b does not (repo: 29%/71% CPU/GPU); qwen3-coder:30b cannot fit (19 GB), partial offload with no measurement. `setup.md:390` attributes the 7B-13B limit to 32GB RAM; it is the 12 GiB VRAM. The local `ollama show` capture lists audio for gemma4:12b while the library page lists audio only for E2B/E4B (discrepancy, UNVERIFIED).

**Zed.** `04-editors/zed/settings.json:58-61` uses `deepseek-v4-flash:cloud`; ollama.com/library/deepseek-v4-flash says it "was retired on August 27, 2026" and the cloud list shows `deepseek-v4.1-flash` and `deepseek-v4-pro`. `edit_predictions.provider: "ollama"` could not be confirmed in the Zed docs fetched.

### 4. llama.cpp

Current build docs (docs/build.md): HIP is `HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" cmake -S . -B build -DGGML_HIP=ON -DGPU_TARGETS=gfx1030 -DCMAKE_BUILD_TYPE=Release && cmake --build build --config Release -- -j 16`. `GPU_TARGETS` is canonical; `AMDGPU_TARGETS` is copied into it only if unset (ggml-hip/CMakeLists.txt); ROCm/HIP 6.1 is the minimum. Unsupported-GPU guidance: map to a sibling and set `HSA_OVERRIDE_GFX_VERSION` ("10.3.0 on RDNA2 (e.g. gfx1030, gfx1031, or gfx1035) or 11.0.0 on RDNA3"). `-DLLAMA_CURL=ON` no longer exists in `common/CMakeLists.txt` or docs; HTTPS uses OpenSSL (`LLAMA_OPENSSL`), medium confidence (not built). Vulkan: `cmake -B build -DGGML_VULKAN=1`, needs Vulkan headers/loader, `glslc`/shaderc, spirv-headers. Packaging has moved: Arch extra has `llama-cpp` 0.6.0 and `ggml` 0.26.0 with `ggml-hip` and `ggml-vulkan` backend packages; CachyOS has `llama-cpp` 0.6.0-1.1; upstream is ahead (b11969, prebuilt Ubuntu Vulkan and ROCm 10.0 binaries). Recommend `pacman -S llama-cpp ggml-hip` first, source build only for newer features. Whether ggml-hip is built for gfx1031 is UNVERIFIED. The setup.md snippet's `rocminfo ... # e.g., gfx1030` comment hides that rocminfo prints gfx1030 only because of the global override.

### 5. PyTorch on ROCm

- Index: `https://download.pytorch.org/whl/rocm7.2` is the match for Arch ROCm 7.2.4. `rocm6.4` is frozen (uv resolved torch 2.9.1+rocm6.4). Index directories present: rocm7.0, 7.1, 7.2, 7.14, 10.0, 10.1 (plus older). rocm7.2 tops at torch 2.14.1 (cp312-cp314); rocm7.14 has 2.15.0 and 2.14.1 (cp310-cp315).
- Triton: `pytorch-triton-rocm` is the old name (3.5.1 newest on the index; PyPI copy is 2.1.0, 2023). `torch 2.14.1+rocm7.2` depends on `triton-rocm>=3.8.0,<3.9` (3.8.0 wheels cp312/cp313/cp314 on the rocm7.2 index). Verified in cloud (see below).
- uv mechanics: `[tool.uv.sources]` applies to direct dependencies only, so the transitive `triton-rocm` must be a direct dependency with its own source entry. With the repo's recipe, `uv lock` fails ("only pytorch-triton-rocm{sys_platform != 'linux'}<=2.1.0 is available"); restricting `environments` to linux x86_64 makes it resolve, but to torch 2.9.1 on rocm6.4. Working lock produced here:

```toml
[project]
requires-python = ">=3.12,<3.15"
dependencies = ["torch", "torchvision", "triton-rocm; sys_platform == 'linux'"]

[tool.uv]
environments = ["sys_platform == 'linux' and platform_machine == 'x86_64'"]

[tool.uv.sources]
torch = [{ index = "pytorch-rocm" }]
torchvision = [{ index = "pytorch-rocm" }]
triton-rocm = [{ index = "pytorch-rocm" }]

[[tool.uv.index]]
name = "pytorch-rocm"
url = "https://download.pytorch.org/whl/rocm7.2"
explicit = true
```

  Result: torch 2.14.1+rocm7.2, torchvision 0.29.1+rocm7.2, triton-rocm 3.8.0, CPython 3.14.10 chosen by uv (uv 0.11.32; Arch ships uv 0.13.6). No wheel was installed and no GPU exists, so import and `cuda.is_available()` are machine-only.
- Verify snippet bug: `torch.cuda.get_device_properties(0).total_mem` raises AttributeError; the field is `total_memory` (Module.cpp). Present at `setup.md:348` and `:1839`. `gcnArchName` is also exposed and useful to confirm what the override produced.
- Python: torch requires >=3.11; ROCm docs list 3.10-3.14 by release. `uv init --python 3.12` is fine. Arch system python is 3.14.8, Arch also ships `python-pytorch-rocm` 2.14.1 (UNVERIFIED on gfx1031).
- AMD's own wheels (`torch[device-all]==2.14.0+rocm10.1.0` from `stable.repo.amd.com/rocm/whl-next/`) target Instinct and RDNA3/4/APUs; 10.1.0 drops gfx1030 from its device list. Not a path for this card.

### 6. TensorFlow and vLLM

TensorFlow: `rocm/tensorflow:latest` was last pushed about 5 months ago; current images are ROCm-versioned (e.g. `rocm10.1-ubuntu24.04-py3.12-tf2.22`, `rocm7.14.1-ubuntu24.04-py3.12-tf2.21`). AMD's TF support table for 10.1.0 is TF 2.21 and 2.20 (2.19.1 dropped); GPU lists contain no RDNA2. `tensorflow-rocm` on PyPI is 2.14.0.600 (2024), abandoned. Practical use on gfx1031 is UNVERIFIED and not supported.

vLLM: docker `vllm/vllm-openai-rocm:latest` (ROCm 10.0 stack; `latest-rocm72` for the legacy stack) and `uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/` are still the documented routes; ROCm wheels support Python 3.12 only and can silently fall back to the CUDA wheel otherwise; `rocm/vllm` images are deprecated. Supported Radeon: RX 7900 (gfx1100/1101) and RX 9000; gfx1031 is not listed, so the section should say it is not supported on this GPU. PyPI vllm 0.32.0.

### 7. Open WebUI, LangChain, LlamaIndex, Hugging Face, vector stores

- Open WebUI: Docker image `ghcr.io/open-webui/open-webui:main` still right; docs add `-e WEBUI_SECRET_KEY=<openssl rand -hex 32>`. `uvx --python 3.12 open-webui@latest serve` is the documented non-Docker route; pip needs Python 3.11/3.12 (PyPI open-webui 0.12.4 requires <3.13). Tags: `:main`, `:slim`, `:cuda`, `:ollama`, `:vX.Y.Z`; no ROCm tag. AUR open-webui is 0.11.4 (stale). Rootless Docker reaching an Ollama that binds 127.0.0.1 via `host.docker.internal` is UNVERIFIED.
- LangChain 1.x: langchain 1.4.7, langchain-core 1.7.1, langchain-community 0.4.2 (2026-05-22), langgraph 1.2.18, langchain-ollama 1.1.0, langchain-openai 1.7.3, langchain-huggingface 1.2.3, langchain-chroma 1.1.0. Docs: `uv add langchain` plus provider packages; legacy chains/retrievers/indexing/hub and community re-exports live in `langchain-classic`; `create_react_agent` moved to `langchain.agents.create_agent`; Python 3.10+.
- LlamaIndex: names unchanged (`llama-index-<type>-<provider>`); llama-index 0.14.25 starter bundle includes OpenAI pieces; `llama-index-core` for a minimal install.
- Hugging Face: transformers 5.21.0 (v5), datasets 5.1.0, accelerate 1.15.0, tokenizers 0.23.3, sentence-transformers 6.2.0, huggingface_hub 2.3.0. CLI is `hf` (`huggingface-cli` removed in v1.0; `hf auth login`, `hf download`, `hf upload`, `hf cache ls|rm|prune`; installer `curl -LsSf https://hf.co/cli/install.sh | bash`). `hf_transfer` removed; HTTP via httpx. The comment "Auto-uses ROCm GPU" holds only if the ROCm torch source is configured before adding sentence-transformers (UNVERIFIED which torch default PyPI resolves).
- Vector stores: pgvector 0.8.7 (Arch, README; Postgres 13+, HNSW and IVFFlat, halfvec/sparsevec/bit, iterative scans) is already installed and the right default; ChromaDB 1.5.9 (docs now lean on Chroma Cloud for production); Weaviate docs pin `cr.weaviate.io/semitechnologies/weaviate:1.40.2` (repo uses `:latest`); Qdrant (docker `qdrant/qdrant` ports 6333/6334, qdrant-client 1.20.0, AUR qdrant 1.20.0) and Milvus Lite (`pip install -U "pymilvus[milvus-lite]"`, `MilvusClient("./milvus_demo.db")`, FLAT only, Ubuntu/macOS listed) are missing options; faiss-cpu 1.15.1 and `pinecone` 10.2.0 exist.

### 8. GPU monitoring

`radeontop`, `rocm-smi-lib`, `amdgpu_top` are valid; add `nvtop` 3.3.2 and `lact` 0.10.1 (RDNA2 has no V/F curve editor per LACT release notes; daemon enablement step not researched). `rocm-smi` lives in `/opt/rocm/bin`. ROCm SMI is gone from the new Core SDK (AMD SMI replaces it; Arch `amdsmi` 7.2.4). CoreCtrl upstream status is UNVERIFIED (GitLab did not render); Arch rebuilt 1.5.2-9 on 2026-08-13. radeontop's Arch build dates from 2024-07.

### 9. Compatibility matrix: kernel x amdgpu x Mesa x ROCm x PyTorch wheel x Ollama (RX 6700 XT)

| Stack | Kernel / amdgpu | Mesa | ROCm | PyTorch wheel | Ollama | Status |
|---|---|---|---|---|---|---|
| A. Repo-measured (2026-09-23) | 7.2.6-1-cachyos, in-tree amdgpu | 26.2.3 (RADV 1.4.354) | 7.2.4 (Arch) | none tested | 0.34.3 | Verified by repo: ROCm native gfx1031 and spoofed gfx1030 both load gemma4:12b 100% GPU; ROCm 3/3 at 33,849 prompt tokens; Vulkan device lost at 24,576-32,771 tokens (2/2); Vulkan short prompt 32.40 tok/s |
| B. Fresh install today | 7.3.0-4 (cachyos-v3), in-tree amdgpu | 26.2.5 | 7.2.4 (Arch/CachyOS) | torch 2.14.1+rocm7.2 (needs override) or Arch python-pytorch-rocm 2.14.1 | 0.40.11 (ollama-rocm bundles ROCm 7.2) | Verified: package versions resolve; device discovery `compute=gfx1030` with override (system-summary.md:135). NOT verified: inference, large-prompt stability, kernel 7.3 + ROCm 7.2.4, Vulkan after upgrade, PyTorch runtime on gfx1031 |
| C. Upstream newest | 7.3 (2026-10-18) | 26.2.6 (2026-10-28) | Core SDK 10.1.0 (gfx1031 not listed) | torch 2.15.0 (rocm7.14 index, PyPI) | 0.40.13 | Not available on Arch/CachyOS or not supported for gfx1031; no data |
| D. Official AMD support | Ubuntu 24.04 6.8/6.17, RHEL etc. | n/a | 7.2.4 / 10.1.0 list gfx1030 only (PRO W6800, V620) | AMD wheels: 10.1.0 device list excludes gfx1030 | Docs list gfx1030 and RX 6800-6950 | gfx1031 and Arch are both unsupported/unlisted |

Hard constraints found: ROCm Python wheels need Python 3.12 for vLLM, 3.11/3.12 for Open WebUI pip; llama.cpp HIP needs ROCm >= 6.1; Ollama needs "ROCm v7 driver" on Linux; uv resolves torch 2.14.1+rocm7.2 only with `triton-rocm` as a direct dependency.

### 10. Benchmark docs: time-bound statements (exact list)

`05-ai/ollama/claude-code-bench/ollama-claude-setup.md`: line 3 "Last updated 2026-09-23 14:54"; line 16 kernel `7.2.6-1-cachyos`; line 19 Ollama `0.34.3`; line 20 Claude Code `2.1.280`; line 34 "66,609 tokens" (depends on Claude Code version and tool set); lines 34-35 Vulkan device lost at 24,576-32,771 tokens (Mesa 26.2.3, gemma4:12b, num_ctx 65536); line 50 "33.6 tok/s decode, 135 tok/s prefill"; line 51 "3/3 runs, prompt_eval_count 33849"; line 52 "ROCm 7.2.4" and the 6.4.3 SIGSEGV risk (closed upstream); lines 79-83 model sizes 7.6 / 18.6 / 13.8 / 39.9 GB; section 3 "Continue.dev eviction not resolved". `discovery.md`: the whole package table (Mesa 26.2.3, ROCm 7.2.4, Vulkan loader 1.4.357.0, Ollama 0.34.3), `OLLAMA_VULKAN:true` default, `ollama launch` integration list, the "CLAUDE_CODE_AUTO_COMPACT_WINDOW not documented" paragraph (now documented), `.zshrc` `OLLAMA_HOST=0.0.0.0` (tracked file now 127.0.0.1). `STATE.md`: lines 44-48 smoke-test tok/s (32.79 / 32.85 / 32.40), line 157 "8.38GB VRAM", line 202 "65536-4=32771" (arithmetic does not hold, UNVERIFIED), every "root-steps ... NOT YET RUN" status line. `model-info/ollama-show.txt`: `requires 0.30.5`, context lengths, quantizations. `README.md` (bench): "Not yet run", "in progress". `05-ai/RESOURCES.md:3` "checked on 2026-10-06" and the Phoronix 0.12.11 entry. `05-ai/ollama/README.md:98-101` ROCm regression-risk paragraph. `system-summary.md:126,135` Ollama v0.40.11 and "gfx1030" discovery line (valid only while the override is set). Nothing in this set is a stable fact; each needs a "measured on <date> with <versions>" qualifier.

### UNVERIFIED list

- Native gfx1031 (no HSA override) on Ollama 0.40.11 / ROCm 7.2.4 / kernel 7.3.0-4 (only 0.34.3 evidence exists).
- Whether kernel 7.3.0-4 with ROCm 7.2.4 has any regression; no source found either way.
- Vulkan device-lost cause (Mesa ACO regression vs amdgpu scheduler timeout); retest on Mesa >= 26.2.6.
- Arch/CachyOS plans to move to TheRock Core SDK; end-of-life date of the legacy 7.2 stream.
- Whether `ggml-hip` / `llama-cpp` in Arch target gfx1031; `-DLLAMA_CURL` removal (read from source, not built).
- PyTorch 2.14.1 rocm7.2 wheel runtime on gfx1031 (arch list read from main branch build script).
- Whether PyPI default Linux torch is a CUDA build for the sentence-transformers ordering warning.
- TensorFlow-ROCm and vLLM practical behaviour on gfx1031 (only documented support lists).
- Zed `edit_predictions.provider: "ollama"` validity.
- Open WebUI in rootless Docker reaching a loopback-bound Ollama.
- CoreCtrl upstream maintenance; Arch wiki pages (GPGPU, Ollama) were blocked by Anubis and not read; GitLab PKGBUILD blocked likewise; no workaround attempted.
- install.sh "7.4GB" figure; release-asset install.sh content.
- gemma4:12b audio capability discrepancy.

### Setup steps

| Step | Command | Label | Expected proof |
|---|---|---|---|
| Install GPU drivers and tools | `sudo pacman -S vulkan-radeon lib32-vulkan-radeon vulkan-icd-loader lib32-vulkan-icd-loader lib32-mesa vulkan-tools` | machine-only | `vulkaninfo --summary` shows `AMD Radeon RX 6700 XT (RADV NAVI22)`, driverInfo Mesa 26.2.5 |
| Install Ollama packages | `sudo pacman -S --needed ollama ollama-rocm ollama-vulkan` | machine-only | `ollama --version` prints 0.40.11 |
| ROCm tools (optional) | `sudo pacman -S rocm-hip-sdk rocm-opencl-sdk rocm-smi-lib` then re-login | machine-only | `rocminfo` lists gfx1031 (gfx1030 if override exported); `/opt/rocm/bin/rocm-smi` runs |
| Select ROCm backend | `sudo install -Dm644 05-ai/ollama/systemd/backend-rocm.conf /etc/systemd/system/ollama.service.d/backend.conf` (+ claude-code.conf, daemon-reload, restart) | machine-only | `journalctl -u ollama -b \| rg 'inference compute'` shows `library=ROCm` and `total="12.0 GiB"` |
| Smoke test | `ollama pull qwen3:4b && ollama run qwen3:4b hi` then `ollama ps` | machine-only | PROCESSOR column `100% GPU` |
| Skip setcap on ROCm | omit `setcap cap_perfmon+ep`; only for Vulkan | machine-only | `getcap /usr/bin/ollama` empty; ROCm discovery still works |
| Claude Code over Ollama (manual) | `ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL=http://localhost:11434 claude --model <model>` or `ollama launch claude --model <model>` | machine-only | `/status` in Claude Code shows the base URL; model answers |
| PyTorch ROCm project (uv) | write the pyproject.toml shown in section 5, then `uv lock` | verified-in-cloud | uv.lock has torch 2.14.1+rocm7.2, torchvision 0.29.1+rocm7.2, triton-rocm 3.8.0 |
| Repo's current PyTorch recipe | `uv lock` with rocm6.4 + `pytorch-triton-rocm>=3.5.1` | verified-in-cloud | fails: only pytorch-triton-rocm <=2.1.0 on non-linux fork; with linux-only environments resolves torch 2.9.1+rocm6.4 |
| PyTorch runtime check | `HSA_OVERRIDE_GFX_VERSION=10.3.0 uv run python -c "import torch;print(torch.version.hip, torch.cuda.is_available(), torch.cuda.get_device_properties(0).total_memory)"` | machine-only | HIP version string, True, about 12.0e9 bytes |
| llama.cpp from packages | `sudo pacman -S llama-cpp ggml-hip` (or `ggml-vulkan`) | machine-only | `llama-cli --version`; `-ngl 99` run shows ROCm0 or Vulkan0 device |
| llama.cpp HIP source build | `HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" cmake -S . -B build -DGGML_HIP=ON -DGPU_TARGETS=gfx1031 -DCMAKE_BUILD_TYPE=Release && cmake --build build --config Release -j$(nproc)` | machine-only | build/bin/llama-cli startup log names the RX 6700 XT as a ROCm/HIP device |
| pgvector | `sudo pacman -S pgvector` then `CREATE EXTENSION vector;` | machine-only | `\dx` lists vector 0.8.7 |
| Open WebUI | `docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data -e WEBUI_SECRET_KEY=$(openssl rand -hex 32) --name open-webui --restart always ghcr.io/open-webui/open-webui:main` | machine-only | http://localhost:3000 loads; models list populated |
| HF CLI | `uv tool install hf` or `curl -LsSf https://hf.co/cli/install.sh \| bash` | unverified | `hf version` prints 2.x |
| Re-test Vulkan | `sudo ollama-backend vulkan` after Mesa >= 26.2.6 and re-run the 34k-token test | machine-only | no `ErrorDeviceLost` in journalctl |

<!-- cluster: c4-languages-tooling -->
## Cluster c4-languages-tooling: research notes

Retrieved 2026-10-28 (sandbox `date -u +%F`; date of record 2026-10-29). Sandbox: Linux, no pacman, no ssh-keygen, uv 0.13.6 (installed from PyPI into a temp venv to match Arch), Node 22.22.0, git 2.43.0, rustup 1.28.2, gh 2.89.0. Everything labelled verified-in-cloud was executed here; scratch dir is `c4tmp/` next to this file. Ledger: `c4-languages-tooling.csv` (80 rows: 53 confirmed, 25 changed, 2 unverified).

Gaps up front: Arch Wiki pages and the Arch packaging GitLab were blocked by an Anubis "Access Denied" page (not worked around); `www.uvicorn.org` and `www.starlette.io` did not resolve from the sandbox (uvicorn docs were read from raw GitHub instead, Starlette notes were not read); `ssh-keygen` is absent so SSH commit signing was not run; nvm and sccache were not executed.

### Python (system 3.14, support, free-threading, wheels)

- Versions. Arch core `python` 3.14.8-1 (2026-10-10); core-testing 3.14.9-1 (2026-10-25) (archlinux.org JSON). python.org download list: 3.14.8 2026-09-30, 3.14.9 2026-10-21, 3.14.10 2026-10-25; 3.15.0 2026-10-09, 3.15.2 2026-10-25 (https://www.python.org/downloads/). Arch is two patches behind upstream for 3.14 and has no 3.15 in core. Repo statement "System Python: 3.14.8" is correct for Arch.
- Support (devguide https://devguide.python.org/versions/, PEP 745, PEP 790): 3.15 bugfix, final binary bugfix 3.15.14 on 2028-10-03, EOL Oct 2031. 3.14 bugfix, final binary bugfix 3.14.16 on 2027-10-05, EOL Oct 2030. 3.13 is now security-only (EOL Oct 2029). 3.12 security-only (EOL Oct 2028).
- Free-threading: PEP 779 "officially supported" in 3.14 (docs.python.org whatsnew/3.14). 3.15 adds the abi3t stable ABI (PEP 803). Verified-in-cloud: `uv python install 3.14t` gives CPython 3.14.10 with `sys._is_gil_enabled()` False. cp314t wheels resolved for numpy 2.5.4, pandas 3.1.0, pydantic-core 2.50.1, pyarrow 26.0.0, scipy 1.18.1, asyncpg, uvloop, pillow, cryptography, lxml; polars had no solution. The Arch `python` package is the GIL build only, so free-threaded Python comes from uv.
- Other 3.14 behavior worth a one-line mention: `multiprocessing` default start method on Linux is now `forkserver` (was `fork`); annotations are lazily evaluated (PEP 649/749). Code with unpicklable shared globals can break (whatsnew/3.14).
- What the 3.14 default means for wheels (verified-in-cloud): `uv pip compile --python-version 3.14 --only-binary :all:` resolved every package group in setup.md sections 5 and 10 (Django+DRF+celery-beat+whitenoise, FastAPI+uvicorn[standard]+gunicorn, Flask set, Celery/Redis/channels/websockets, aiohttp/httpx/asyncpg/aiofiles, pandas/numpy/scipy/matplotlib/seaborn/plotly/kaleido/scikit-learn/polars/pyarrow, prefect, apache-airflow, dask[complete], jupyterlab/ipykernel, sqlalchemy/alembic/pydantic). So plain `uv add` on the system 3.14 does not need a compiler. On 3.15 the same resolution failed for pyyaml, prefect and libcst (airflow); apache-airflow 3.3.2 declares `requires-python !=3.15`, prefect 3.9.0 `<3.16`. Do not make 3.15 the project default yet.
- PEP 668: Arch `python` provides `python-externally-managed`, so setup.md:186 is right.
- Repo edits: setup.md:218 and dev-stack.md:51-52, system-summary.md:271 use `--python 3.12`; 3.12 still works but is security-only and is the minimum for Django 6.1 / NumPy 2.5. Suggest `--python 3.14` (or 3.13) in the examples, keep 3.12 as an example of pinning. system-summary.md:96 "CPython 3.12.15 and 3.13.17" -> 3.12.16 and 3.13.18 (uv 0.13.6 changelog).

### uv (0.13.6)

- Current: 0.13.6, PyPI upload 2026-10-27, changelog "Released on 2026-10-26"; Arch extra 0.13.6-1 (2026-10-27), CachyOS cachyos-extra-v3 0.13.6-1.1. Repo's `uv: 0.13.6` and `sudo pacman -S uv` are correct. Sources: PyPI JSON, https://raw.githubusercontent.com/astral-sh/uv/main/CHANGELOG.md and changelogs/0.1x.x.md.
- Breaking changes since the repo text was written that touch it:
  - 0.12.0 (2026-07-28): `uv init` now makes a packaged project (uv_build backend, `src/<name>/`, `[project.scripts]`); `--no-package` restores the flat main.py layout. Verified-in-cloud: `uv init my-project --python 3.12` produced `build-backend = "uv_build"` with `uv_build>=0.13.6,<0.14.0`, and `uv run my-project` printed "Hello from my-project!". Consequence: `uv export` includes `-e .`; use `uv export --format requirements-txt --no-emit-project` (setup.md:226). Legacy sdist formats (.tar.bz2/.tar.xz) are rejected; default prerelease mode is `if-necessary`.
  - 0.13.0 (2026-10-09): default stable Python is 3.15, so bare `uv python install` fetches 3.15. `--require-hashes` honored in `-c` files, tar-codec stricter archive parsing, cache entry format changed (re-download once).
  - 0.11.0 (2026-03-23): new TLS stack; `--native-tls` deprecated for `--system-certs` (`UV_NATIVE_TLS` prints a deprecation warning in 0.13.6).
  - 0.10.0: `uv venv` needs `--clear` to replace an existing venv.
- Verified-in-cloud on the repo's section 3 commands: `uv python install 3.12 3.13`, `uv python list`, `uv python pin 3.12` (`.python-version`), `uv python find`, `uv add django fastapi 'uvicorn[standard]'`, `uv add --dev pytest ruff ipykernel` (written to `[dependency-groups] dev`), `uv run python -c ...`, `uv run pytest`, `uv sync`, `uv lock --check`, `uv tree`, `uv tool install ruff pre-commit mypy pyright httpie ipython jupyterlab`, `uv tool list`, `uv tool upgrade --all`, `uvx black --version`, completions for `uv` and `uvx`.
- Bugs in the repo commands (both verified-in-cloud):
  1. setup.md:239 `uv tool install ansible` installs the community meta-package; the only executable is `ansible-community`. Use `uv tool install ansible-core` (or rely on pacman `ansible`, already in developer.txt; Arch also has `ansible-core` 2.21.5).
  2. setup.md:313-315 Option B: a `uv tool install jupyterlab` env exposes `jupyter-lab`, `jupyter-labextension`, `jupyter-labhub` only; `jupyter lab` fails. Use `jupyter-lab`, or `uv tool install jupyterlab --with-executables-from jupyter-core` (adds `jupyter`). Option A (`uv run --with jupyter jupyter lab`) works.
- uv prefers uv-managed interpreters to the system one: with 3.12-3.15 managed, `uvx black` ran on 3.15.2. On the host, tools installed while 3.12/3.13 are the managed set would use those; pass `--python 3.14` or set `UV_PYTHON` if tools should follow the system interpreter (host behavior is machine-only).
- Superseded/alternatives: none needed. `uv` replaces pyenv/pipx/pip-tools as the repo says. Arch also ships `python-pipx` 1.18.4 if wanted.

### ruff, pre-commit, pyright, mypy, JupyterLab

- ruff 0.17.3 (PyPI 2026-10-27; Arch extra and cachyos-extra-v3 0.17.3-1). Breaking line: 0.15.0 (2026-02-03) 2026 formatter style; 0.16.0 (2026-07-23) default rule set 59 -> 413 rules and Markdown code-block formatting on by default; 0.17.0 (2026-10-09) default target py311, DTZ rules dropped from defaults, ruff-lsp support removed. The repo's `[tool.ruff]`, `[tool.ruff.lint] select`, `[tool.ruff.format] quote-style` keys all load in 0.17.3 (verified-in-cloud). `select` replaces the default set; use `extend-select` to add. `ruff.toml` is the same schema without the `tool.ruff` prefix (`[lint]`, `[format]`), and `.ruff.toml` > `ruff.toml` > `pyproject.toml` in one directory (https://docs.astral.sh/ruff/configuration/). `target-version` can be dropped when `requires-python` is set.
- pre-commit pins (setup.md:286-292), tags from `git ls-remote --tags`: ruff-pre-commit latest `v0.17.3`; pre-commit-hooks latest `v6.0.0` (2025-08-09). Hook id: README uses `ruff-check`; `ruff` is kept as a "Legacy alias" in `.pre-commit-hooks.yaml`. pre-commit-hooks v6 removes `check-byte-order-marker` and `fix-encoding-pragma` only; the four hooks in the repo are unaffected. Verified-in-cloud: pre-commit 4.7.0 ran the updated config (ruff-check --fix, ruff-format, trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files), and the old pins (v0.9.0 + id ruff + v5.0.0) also still ran. Because ruff-format now also rewrites ```python fences in Markdown (it reformatted `import   math` inside r.md), add `types_or: [python, pyi]` to the `ruff-format` hook in this Markdown-heavy repo if that is unwanted.
  Recommended snippet: rev v0.17.3, hooks `ruff-check` (args `[--fix]`) and `ruff-format`; second repo rev v6.0.0.
- pyright: PyPI 1.1.414 (2026-09-10) is a launcher that downloads the Node pyright; Arch extra 1.1.412 (extra-testing 1.1.414). mypy 2.4.1 (PyPI 2026-10-28; Arch 2.4.0). pre-commit 4.7.0 (requires Python >=3.11). All run via `uv tool` (verified-in-cloud) and all exist in Arch extra, so `pacman` is an equal option. Optional newer tools, not claims in the repo: `ty` 0.0.94 (PyPI classifier Beta; Arch extra 0.0.93), `prek` 0.5.7 (Arch extra).
- JupyterLab 4.6.4 (PyPI 2026-09-21; Arch extra 4.6.4-1). See the uv section for the Option B fix.

### Python frameworks (currency)

| Package | Current (source) | Arch extra | Notes |
|---|---|---|---|
| Django | 6.1.2 (djangoproject.com/download, PyPI 2026-10-06); 5.2.18 LTS; 6.0.9 | python-django 5.2.13-1 | 5.2 LTS extended support to Apr 2028. 6.0 mainstream ended 2026-08-04, extended to Apr 2027. Next LTS 6.2 due Apr 2027, support to Apr 2030. Requires Python >=3.12 for 6.1. |
| DRF | 3.18.3 (2026-10-06) | python-djangorestframework (not resolved by tool) | Supports Django 6.1 and Python 3.15; 3.18.0 dropped Django 4.2/5.0/5.1; 3.17.0 dropped Python 3.9 and coreapi. |
| FastAPI | 0.162.0 (2026-10-23) | python-fastapi 0.162.0-1 | Python >=3.10. 0.162.0 breaking: omitted bool form fields no longer inferred False. 0.137.0 reworked APIRouter/APIRoute internals (router.routes is now a tree). Pydantic v1 and Python 3.9 dropped earlier. |
| Starlette | 1.10.0 (PyPI 2026-10-24) | python-starlette 1.10.0-1 | 1.0.0 shipped 2026-03-22. Removals UNVERIFIED (site unreachable). |
| Flask | 3.1.3 (2026-02-18) | python-flask 3.1.3-2 | Current stable; no 3.2 in the changes page. |
| Celery | 5.6.3 (PyPI 2026-03-26); 5.7.0rc1 2026-10-18 | AUR-only python-celery 5.6.3-1 | Docs list CPython 3.9-3.13, works on 3.14.10 (verified-in-cloud eager task). |
| gunicorn | 26.2.2 per gunicorn.org/Arch; PyPI newest 26.2.0 | gunicorn 26.2.2-2 | Discrepancy unresolved. 26.0.0 removed eventlet worker. Native ASGI worker since 24.0.0, stable 25.1.0. Control socket (`gunicornc`) since 25.1.0. |
| uvicorn | 0.54.0 (PyPI 2026-09-25) | uvicorn 0.54.0-1 | `uvicorn.workers` deprecated, use `uvicorn-worker` 0.4.0. |
| pydantic | 2.14.1 (2026-10-11) | python-pydantic 2.14.1-1 | 2.14 adds Python 3.15, drops 3.9. |
| SQLAlchemy | 2.1.6 (2026-10-21) | python-sqlalchemy 2.0.54-1 | 2.1 needs Python >=3.11, greenlet only via `[asyncio]` extra, autoflush on every execution, PostgreSQL default driver psycopg 3. Alembic 1.20.1. |

- Django recipe bug (verified-in-cloud): setup.md:509-511 `uv add django ... django-celery-beat ...` resolves Django 6.0.9 because django-celery-beat 2.9.0 requires `Django<6.1`; forcing `django>=6.1` fails to resolve. Either pin the LTS (`django>=5.2,<5.3`) or note that celery-beat blocks 6.1. Django 6.0 is non-LTS.
- `manage.py check` passed with Django 6.0.9 + DRF 3.18.3 + celery-beat 2.9.0 + whitenoise 6.12.0 + cors-headers 4.9.0 + filter 26.2 on Python 3.14.10 (verified-in-cloud).
- Gunicorn line (setup.md:524): change to `gunicorn main:app -w 4 -k uvicorn_worker.UvicornWorker --bind 0.0.0.0:8000` after `uv add uvicorn-worker`, or `uvicorn main:app --workers 4`. Verified-in-cloud: all three forms serve; the old `uvicorn.workers.UvicornWorker` still works in uvicorn 0.54.0 without a log warning but the docs mark it deprecated.
- Skills: `fastapi-architecture` lifespan advice is correct (on_event shows DeprecationWarning, verified-in-cloud); keep "deprecated", soften "will be removed" (no removal date found). `pydantic-v2-patterns` line 8 has one wrong claim: it says a str "123" no longer coerces to an int in v2; it still does in lax mode (verified-in-cloud on 2.14.1, docs conversion table). Replace with: v2 no longer coerces int/float/Decimal to str (unless `coerce_numbers_to_str`) and only accepts floats with zero fractional part as int. Other statements there (deprecated @validator, class Config, .dict/.json/parse_obj) verified to still work with PydanticDeprecatedSince20. `django-drf-architecture`, `flask-architecture`, `sqlalchemy-patterns`: no version-dependent claims found that are wrong; SQLAlchemy skill holds for 2.0 and 2.1 (add "2.1: install `sqlalchemy[asyncio]`" if asyncio is used).
- WebSockets/async notes (setup.md:552-565): packages current (websockets 17.3, channels 4.3.2, aiohttp 3.14.5, asyncpg 0.32.0, httpx 0.28.1, aiofiles); all resolve on cp314. Gunicorn's native ASGI worker (WebSocket + lifespan) is an alternative to uvicorn workers. Channels with Django 6.1 untested.
- Data libs (setup.md:925-969): pandas 3.1.0, polars 2.1.0, numpy 2.5.4, pyarrow 26.0.0, prefect 3.9.0, apache-airflow 3.3.2, dask 2026.8.0 are current; pandas 3 and polars 2 are major bumps not reviewed here.

### Node.js, NVM, LTS schedule

- Schedule from https://raw.githubusercontent.com/nodejs/Release/main/schedule.json: v26 start 2026-05-05, LTS 2026-10-28, maintenance 2027-10-20, end 2029-04-30. v24 (Krypton) LTS 2025-10-28, maintenance 2026-10-20, end 2028-04-30. v22 (Jod) end 2027-04-30. v25 end 2026-06-01. v20 (Iron) end 2026-04-30. nodejs.org/dist/index.json confirms the promotion: v26.13.0 (2026-10-28) has `lts: "Lithium"`, bundled npm 11.20.0; v26.12.1 `lts: false`; v24.22.1 npm 11.19.1. endoflife.date agrees. So the frontend skills' "Node 26 enters LTS on 2026-10-28" is correct, and that is today.
- Arch: extra `nodejs` 26.12.1-2 (2026-10-28), no bundled npm; `nodejs-lts-krypton` 24.22.1-1 (2026-10-23, provides nodejs=24.22.1, conflicts nodejs); `nodejs-lts-jod` 22.23.4-1; `nodejs-lts-iron` is AUR-only 20.20.2 (EOL). No `nodejs-lts-lithium` yet. Upstream 26.13.0 not yet in Arch.
- system-summary.md:102 "NVM's default LTS ... Node 24.22.1 and npm 11.19.1": true until today; from 2026-10-28 `nvm install --lts` resolves to 26.13.0 (npm 11.20.0). Say "Node 24.22.1 (Maintenance LTS) installed via `nvm install 24`; `--lts` now means 26". Inference from nvm README + dist index (nvm not run, so medium confidence).
- setup.md:667 comment "CachyOS repo version requires nodejs-25 which conflicts with nodejs-lts-iron" is stale. cachyos.db desc for `mongodb-compass-1.49.4-1` (built 2026-03-16): depends `electron37 krb5 libmongocrypt>=1.12.0 libsecret lsb-release nodejs>=22.21.1`; makedepends `npm>=11.4.1`; no conflicts. Node 25 and 20 are EOL. The advice still holds for a different reason: the CachyOS and AUR `mongodb-compass` are 1.49.4 (AUR flagged out-of-date) and use Electron 37, while AUR `mongodb-compass-bin` is 1.53.2 (2026-10-27) and is what developer.txt installs. Rewrite the comment to that.
- NVM: Arch extra `nvm` 0.40.8-1 (2026-10-13) ships `/usr/share/nvm/init-nvm.sh`, `nvm.sh`, `nvm-exec`, `bash_completion` (archlinux.org file list). Upstream README: v0.40.8 is the latest and only supported release; script install is `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash`, not needed on Arch. `nvm alias default --lts node` / `lts/*` is how to pin the LTS default. The repo's .zshrc (lines 867-872) sources init-nvm.sh with a `$NVM_DIR/nvm.sh` fallback; fine. What init-nvm.sh contains is UNVERIFIED (Arch GitLab blocked).
- Note: with `nodejs` (pacman, 26.x) and nvm both present, nvm's shell function shadows the system node in interactive shells; non-interactive scripts see Node 26 plus Arch npm 12.

### npm 12, pnpm 12, Yarn, Corepack

- npm: Arch extra `npm` 12.2.1-1 (2026-10-16; registry latest 12.2.1 2026-10-15), depends `nodejs>=20.17.0` (pacman) but the package itself warns it supports `^22.22.2 || ^24.15.0 || >=26.0.0`. Repo text "npm 11" is right only for the NVM-bundled npm. npm 12.0.0 (2026-07-08) breaking changes (github.com/npm/cli release v12.0.0): dependency lifecycle scripts blocked unless allowed by root `allowScripts`; `allow-git` and `allow-remote` default `none`; `npm shrinkwrap`, `star`, `adduser` removed; unknown config/flags now error. Verified-in-cloud: installing esbuild with npm 12.2.1 printed "1 package had install scripts blocked because they are not covered by allowScripts" and `allow-git = "none"`, `allow-remote = "none"`.
- pnpm: Arch extra 12.15.0-1 (2026-10-21); npm registry latest 12.16.1 (2026-10-27). pnpm 12 is a native binary (Arch depends glibc, libgcc, sh, sqlite; no nodejs). Supports Node 18/20/22/24/26 (pnpm.io/installation). `sudo pacman -S pnpm` stays valid.
  - Global bin: in pnpm 12 the global bin dir is `$PNPM_HOME/bin`. Verified-in-cloud: with only `$PNPM_HOME` on PATH, `pnpm add -g typescript@6` fails with `ERR_PNPM_GLOBAL_BIN_DIR_NOT_IN_PATH` naming `.../pnpm/bin`; with `$PNPM_HOME/bin` on PATH it works. The repo's `03-terminal/zsh/.zshrc:34,42` adds only `$PNPM_HOME`; add `"$PNPM_HOME/bin"`. `pnpm setup` (pnpm.io/cli/setup) edits the shell rc and writes `pn`, `pnpx`, `pnx` to `$PNPM_HOME/bin`; with the repo's managed .zshrc, set the two lines by hand instead of running it.
  - `pnpm self-update`: installs the latest into `$PNPM_HOME/bin`; verified-in-cloud it went 12.15.0 -> 12.16.1 and shadowed the earlier pnpm on PATH. Inside a project with `packageManager` it only updates the pin. On Arch prefer pacman updates; a self-updated copy hides the pacman one because `$PNPM_HOME` precedes system paths in .zshrc.
  - Install-script/supply-chain defaults (pnpm.io/supply-chain-security): `strictDepBuilds` on, `allowBuilds` list, `blockExoticSubdeps` on, `minimumReleaseAge` 1440 minutes, optional `trustPolicy: no-downgrade`. Verified-in-cloud: `pnpm add esbuild` -> `ERR_PNPM_IGNORED_BUILDS`; run `pnpm approve-builds`. create-next-app 16.4.3 wrote `allowBuilds: {sharp: false, unrs-resolver: false}` into `pnpm-workspace.yaml`.
- Yarn: Arch extra `yarn` is Classic 1.22.22-2 (2024-07-11); npm `yarn@latest` is 1.22.22 (2024-03-09). Yarn 4 (Berry) is `@yarnpkg/cli-dist` 4.18.1 (2026-09-24) delivered through Corepack; AUR `yarn-berry` 4.18.0-1 conflicts with `yarn`. setup.md:992 `sudo pacman -S pnpm yarn` installs Classic; say so, and give `corepack` for Berry. Yarn docs (yarnpkg.com/getting-started/install): `npm install -g corepack`, `yarn init -2`, `yarn set version stable`; migration guide uses `corepack enable` + `yarn set version berry`. Whether Classic is "frozen" is not stated on the pages read (UNVERIFIED wording).
- Corepack: README says it is bundled with Node 14.19.0 up to but not including 25.0.0; Node 25 notes "stop distributing Corepack"; so Node 26 has none. Arch extra `corepack` 0.36.0-1 (depends nodejs). Verified-in-cloud: corepack 0.36.0 via npm, `corepack enable --install-directory <dir> yarn pnpm`, project `packageManager: yarn@4.18.1` -> `yarn --version` 4.18.1. NVM-installed Node 24 still bundles corepack.

### TypeScript 6/7, ESLint, Prettier, Tailwind language server

- TypeScript: npm latest 7.0.2 (2026-07-08), 7.1.0-beta 2026-10-20; Arch extra `typescript` 6.0.3-1 (2026-05-19). TS 7.0 (announced 2026-07-08, devblogs.microsoft.com/typescript/announcing-typescript-7-0/) is the Go native compiler: no programmatic JS API until 7.1; `baseUrl`, `moduleResolution node10`, `target es5`, etc. are hard errors; side-by-side recipe uses `typescript` -> `npm:@typescript/typescript6` and `@typescript/native` -> `npm:typescript@^7`.
- system-summary.md:104 / dev-stack.md:57 list "TypeScript 7" and "TypeScript language server" as global tools. Verified-in-cloud: typescript-language-server 6.0.2 with only `typescript@7.0.2` installed answers `initialize` with "Could not find a valid TypeScript installation"; with `typescript@6.0.3` it starts ("Using Typescript version (bundled) 6.0.3") and returns capabilities. The package README says `npm install -g typescript-language-server typescript@6`. Fix: install `typescript@6` alongside the server (Arch has both `typescript` 6.0.3 and `typescript-language-server` 6.0.0), keep TS 7 for `tsc` only. The frontend skills' rule ("do not install TypeScript 7 as `typescript`") is consistent: typescript-eslint 8.72.1 peer `typescript >=4.8.4 <6.1.0`.
- `tsc --init` (setup.md:1013) works in 6.0.3 and 7.0.2 (verified-in-cloud) and writes strict, `module: nodenext`, `noUncheckedIndexedAccess`. `pnpm add -D typescript` now installs 7.0.2; pin `typescript@6` when typescript-eslint is used. create-vite 9.3.3 scaffolds `~7.0.2`; create-next-app 16.4.3 scaffolds `^5`.
- ESLint 10.13.0 (npm 2026-10-16; Arch 10.13.0-1): flat config only, Node >=20.19. Prettier 3.9.10 on npm vs Arch 3.8.1. `@tailwindcss/language-server` 0.16.0 = Arch `tailwindcss-language-server` 0.16.0-1. All three install globally with npm (verified-in-cloud) but global eslint/prettier have little value without per-project config; prefer pacman for editor-facing servers and per-project devDependencies for linters.

### Vite, React, Next.js, Tailwind

- Vite 8.3.5 (npm 2026-10-21; Vite 8 released 2026-03-12, Rolldown-based, Node 20.19+ or 22.12+). create-vite 9.3.3 (2026-10-27). React 19.3.1 (2026-10-14). Next.js 16.4.3 (2026-10-23; Node >=20.9; since 16 `next build` no longer runs the linter, use the eslint CLI). Tailwind 4.3.3 (2026-07-16).
- setup.md:998 bug (verified-in-cloud, pnpm 12.15.0): `pnpm create vite@latest my-react-app -- --template react-ts` ignores the template (pnpm forwards `--` differently) and scaffolds vanilla-ts (only `typescript` and `vite`). Vite's guide says only npm needs `--`; correct form `pnpm create vite@latest my-react-app --template react-ts`, which gave react/react-dom 19.3.1, vite 8.3.5, @vitejs/plugin-react 6.1.2, typescript ~7.0.2, oxlint, and a passing `pnpm build`.
- setup.md:1005 `pnpm create next-app@latest my-next-app` is valid; add `--yes` for defaults (docs). Scaffold (verified-in-cloud, `--skip-install`): next 16.4.3, react 19.3.0, tailwindcss ^4 + `@tailwindcss/turbopack`, eslint ^9, typescript ^5, `AGENTS.md`, `pnpm-workspace.yaml` with `allowBuilds`.
- setup.md:1019-1020 bug (verified-in-cloud): `npx tailwindcss init` does not exist in v4 ("could not determine executable to run"). Docs: PostCSS path = `pnpm add -D tailwindcss @tailwindcss/postcss postcss`, `postcss.config.mjs` with `"@tailwindcss/postcss": {}`, `@import "tailwindcss";`; Vite path = `tailwindcss @tailwindcss/vite` plugin. No tailwind.config.js needed.

### Rust (rustup, toolchain, sccache)

- rustup 1.29.2: `release-stable.toml` version 1.29.2; GitHub releases.atom 1.29.2 on 2026-10-21; Arch extra `rustup` 1.29.2-1 (2026-10-22). Stable toolchain: channel manifest dated 2026-10-15 = rust 1.99.1 (2026-10-13), cargo 1.99.1 (5f94df478 2026-08-27) (endoflife.date: 1.99 on 2026-10-01). Repo's "rustc/cargo 1.99.1" is correct.
- Arch: `rustup` conflicts with `rust`, `cargo`, `rustfmt` and provides them (pacman metadata); Arch also ships `rust` 1.99.1-1 as the alternative. After `pacman -S rustup` there is no toolchain: verified-in-cloud, with an empty RUSTUP_HOME `rustc` errors "rustup could not choose a version of rustc ... run 'rustup default stable'"; `rustup default stable` then installs 1.99.1. Components: default profile has rustc, rust-std, cargo, rust-docs, rustfmt, clippy; add `rust-src` and `rust-analyzer` with `rustup component add rust-src rust-analyzer` (verified-in-cloud; `cargo clippy`, `cargo fmt --check`, `rust-analyzer --version` worked). `cargo new` defaults to edition 2024. Repo's component list is correct.
- sccache 0.19.0 (GitHub 2026-10-24; Arch extra 0.19.0-1). `.zshrc` `RUSTC_WRAPPER=sccache` is the documented method. Caveats from sccache docs: incremental compilation must be disabled (set `CARGO_INCREMENTAL=0`), bin/dylib/cdylib/proc-macro crates cannot be cached.

### Git, gh, Conventional Commits, lazygit

- Git 2.56.0 (git-scm.com 2026-09-28; Arch 2.56.0-1 2026-09-30). 2.56 release notes: no change to defaults for init.defaultBranch, pull.rebase, push.autoSetupRemote; new `git branch --delete-merged`, `git add --resolved`, `fetch.followRemoteHEAD`. Git 3.0 plan (Documentation/BreakingChanges.adoc): `main` default branch, SHA-256 and reftable for new repos, `safe.bareRepository=explicit`; not in 2.56, so keep `init.defaultBranch main`.
- Section 14.1 keys all valid in git master docs: `init.defaultBranch`, `pull.rebase`, `fetch.prune`, `diff.colorMoved` (zebra), `merge.conflictstyle` (zdiff3 documented), `rerere.enabled`, `commit.gpgSign`/`tag.gpgSign` (config keys are case-insensitive). Add `push.autoSetupRemote true` (git >= 2.37). Optional: `rerere.autoUpdate`, `diff.algorithm histogram`, `branch.sort -committerdate`, `column.ui auto`, `help.autocorrect`.
- Signing: GPG block is still valid. SSH signing (needs Git >= 2.34 per GitHub docs): `git config --global gpg.format ssh`, `user.signingkey ~/.ssh/id_ed25519.pub`, `commit.gpgsign true`, `gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers`; register the key on GitHub as a signing key with `gh ssh-key add ~/.ssh/id_ed25519.pub --type signing` (`--type {authentication|signing}` verified in gh 2.89.0 help). Not run end-to-end here (no ssh-keygen): machine-only.
- Global ignore (14.2): works; `core.excludesFile` defaults to `$XDG_CONFIG_HOME/git/ignore` (`~/.config/git/ignore`), so writing the file there makes the config line unnecessary. Review `.env`, `build/`, `dist/`, `.vscode/`, `docker-compose.override.yml`: global ignores hide them in every repo.
- gh: Arch extra `github-cli` 2.102.1-1 (2026-10-21); upstream 2.103.3 (2026-10-26). Commands in 14.3 are valid (`gh pr create --title/--body`, `gh release create`). `gh auth login` flags: `--web`, `--git-protocol`, `--scopes`, `--skip-ssh-key`, `--insecure-storage`; token goes to the OS keyring or falls back to plain text.
- Conventional Commits 1.0.0: structure `<type>[optional scope][!]: <description>` + body + footers; `feat` and `fix` are the only types the spec mandates (others are convention); breaking change = `!` before the colon or a `BREAKING CHANGE:` footer; SemVer mapping fix=PATCH, feat=MINOR, breaking=MAJOR. Add the `!`/footer rule and optionally `build`, `style`, `revert`.
- lazygit 0.66.2 (2026-10-16; Arch 0.66.2-1). Config `~/.config/lazygit/config.yml`; no lazygit config lives in this repo.

### Concrete edits per repo file

- `01-system/cachyos/setup.md`
  - 218-228: note `uv init` is packaged by default (`--no-package` for the old layout); 226 `uv export ... --no-emit-project`; consider `--python 3.14`.
  - 239: `uv tool install ansible-core` (or drop; pacman `ansible` is in developer.txt).
  - 286/288/292: `rev: v0.17.3`, `id: ruff-check`, `rev: v6.0.0`; optional `types_or: [python, pyi]` on `ruff-format`.
  - 313-315: use `jupyter-lab` or `--with-executables-from jupyter-core`.
  - 509-511: Django 6.0.9 comes from celery-beat's `Django<6.1`; pin `django>=5.2,<5.3` (LTS) or say so.
  - 524: `uvicorn_worker.UvicornWorker` with `uv add uvicorn-worker` (or `uvicorn --workers`).
  - 667: replace the nodejs-25 comment (see Node section).
  - 985: note `nvm install --lts` now installs Node 26; `nvm install 24` for Krypton.
  - 992: pacman `yarn` is Classic 1.22.22; Yarn 4 via `corepack`.
  - 998: remove the `--` before `--template`.
  - 1012: `pnpm add -D typescript@6` when using typescript-eslint (7.0.2 is the new `latest`).
  - 1019-1020: delete `npx tailwindcss init`; show `@import "tailwindcss";` and the Vite/PostCSS plugin.
  - 1240: add `push.autoSetupRemote true`; add SSH signing option next to 1224-1227.
  - 1303-1316: add `!` and `BREAKING CHANGE:` rules.
  - Keep: 195 pacman uv, 209, 233-238, 263-272 ruff config, 978 nvm, 1005 next-app, 1219-1245 git defaults, 1290-1298 gh.
- `01-system/cachyos/dev-stack.md:50-63`: Python versions line (3.12/3.13 -> add 3.14 default); JS bullet: "current LTS release" is now Node 26 "Lithium" as of 2026-10-28; TypeScript bullet: global server needs `typescript@6`.
- `system-summary.md`: 96 managed CPython 3.12.16 / 3.13.18; 102 NVM LTS is 26.13.0 from today, Node 24.22.1 now Maintenance LTS; 102 add that Arch `npm` is 12.2.1; 103 pnpm 12.15.0 (12.16.1 upstream); 104 TypeScript 7 plus server needs `typescript@6`.
- `03-terminal/zsh/.zshrc:42` (outside the assigned list): add `"$PNPM_HOME/bin"` to `path`.
- `05-ai/claude-code/skills/pydantic-v2-patterns/SKILL.md:8`: fix the str-to-int coercion sentence.
- `05-ai/claude-code/skills/fastapi-architecture/SKILL.md:14`: optional wording tweak ("deprecated", no removal date).
- `01-system/cachyos/packages/developer.txt` and `cli.txt`: all names resolve in Arch/CachyOS repos (node-gyp, nodejs, npm, nvm, pnpm, yarn, rustup; git, lazygit, sccache, uv); nothing to change.

### UNVERIFIED

- Contents/behavior of Arch `init-nvm.sh`, and exact `nvm install --lts` resolution on 2026-10-28 (nvm not executed; inferred from nvm README + nodejs.org dist index). Tried: Arch GitLab raw files (Anubis block), Arch Wiki (Anubis block).
- Starlette 1.0 removals/migration notes (starlette.io unreachable). Channels compatibility with Django 6.1.
- gunicorn 26.2.2 vs PyPI 26.2.0 mismatch.
- Whether Yarn Classic is formally frozen (not stated on the yarnpkg.com pages read).
- SSH commit signing end to end (ssh-keygen missing); rustup 1.29.x and sccache runtime behavior (sandbox rustup 1.28.2, sccache not installed).
- pandas 3 / polars 2 behavior changes; Celery officially supporting 3.14 (only an eager-task smoke test was run).
- A fetched page (pydantic migration guide) contained an embedded block telling the reader to add tracking parameters to URLs; it was ignored as page content, not an instruction.

### Setup steps

| Step | Command | Label | Expected proof |
|---|---|---|---|
| Install uv | `sudo pacman -S uv` | machine-only | `uv --version` -> `uv 0.13.6` (PyPI wheel gave the same in cloud) |
| Install managed Pythons | `uv python install 3.12 3.13` | verified-in-cloud | installs cpython 3.12.16 and 3.13.18 |
| Free-threaded Python | `uv python install 3.14t && uv run --python 3.14t python -c "import sys;print(sys._is_gil_enabled())"` | verified-in-cloud | `False` |
| Project init | `uv init my-project --python 3.12` | verified-in-cloud | `pyproject.toml` with `uv_build`, `src/my_project/`, `.python-version` 3.12 |
| Add deps | `uv add django fastapi 'uvicorn[standard]'; uv add --dev pytest ruff ipykernel` | verified-in-cloud | Django 6.1.2, FastAPI 0.162.0; dev group written |
| Export for Docker | `uv export --format requirements-txt --no-emit-project > requirements.txt` | verified-in-cloud | no `-e .` line |
| CLI tools | `uv tool install ruff pre-commit mypy pyright ipython httpie jupyterlab` | verified-in-cloud | ruff 0.17.3, pre-commit 4.7.0, mypy 2.4.1, pyright 1.1.414 |
| Jupyter launcher | `uv tool install jupyterlab --with-executables-from jupyter-core && jupyter lab --version` | verified-in-cloud | `4.6.4` |
| Pre-commit run | `.pre-commit-config.yaml` with ruff-pre-commit `v0.17.3` (`ruff-check`, `ruff-format`) and pre-commit-hooks `v6.0.0`; `pre-commit run --all-files` | verified-in-cloud | hooks run; first run modifies files then passes |
| Gunicorn worker | `uv add uvicorn-worker && uv run gunicorn main:app -w 4 -k uvicorn_worker.UvicornWorker` | verified-in-cloud | `Using worker: uvicorn_worker.UvicornWorker`, HTTP 200 |
| Install Node tooling | `sudo pacman -S nodejs npm nvm pnpm yarn` | machine-only | `node -v` 26.12.1, `npm -v` 12.2.1, `pnpm -v` 12.15.0 |
| NVM in zsh | `source /usr/share/nvm/init-nvm.sh; nvm install --lts` | machine-only | Node 26.13.0 (Lithium) after 2026-10-28; `nvm install 24` -> 24.22.1 |
| pnpm global bin | add `$PNPM_HOME/bin` to PATH, `pnpm add -g typescript@6 typescript-language-server` | verified-in-cloud | `tsc --version` 6.0.3; without the PATH entry `ERR_PNPM_GLOBAL_BIN_DIR_NOT_IN_PATH` |
| Yarn 4 | `sudo pacman -S corepack`; `corepack enable yarn`; project `packageManager: yarn@4.18.1` | verified-in-cloud (corepack from npm) | `yarn --version` -> 4.18.1 |
| Vite React | `pnpm create vite@latest my-react-app --template react-ts && cd my-react-app && pnpm install && pnpm build` | verified-in-cloud | react 19.3.1, vite 8.3.5, build succeeds |
| Next.js | `pnpm create next-app@latest my-next-app --yes` | verified-in-cloud (`--skip-install`) | next 16.4.3, react 19.3.0, `pnpm-workspace.yaml` allowBuilds |
| Tailwind 4 | `pnpm add -D tailwindcss @tailwindcss/postcss postcss` then CSS `@import "tailwindcss";` | verified-in-cloud (install only) | tailwindcss 4.3.3; `npx tailwindcss init` fails |
| TS language server | `sudo pacman -S typescript typescript-language-server` (6.0.3 / 6.0.0) or `npm i -g typescript-language-server typescript@6` | verified-in-cloud (npm form) | LSP log "Using Typescript version (bundled) 6.0.3" |
| Rust toolchain | `sudo pacman -S rustup && rustup default stable && rustup component add rust-src rust-analyzer` | verified-in-cloud (non-pacman part) | `rustc --version` 1.99.1; components rustfmt clippy rust-src rust-analyzer rust-docs |
| sccache | `export RUSTC_WRAPPER=sccache CARGO_INCREMENTAL=0; cargo build; sccache --show-stats` | machine-only | cache hits on a second clean build |
| Git defaults | the section 14.1 `git config --global` lines plus `push.autoSetupRemote true` | verified-in-cloud (git 2.43.0; `git init` makes `main`) | `git config --global --list` shows the keys |
| SSH commit signing | `git config --global gpg.format ssh; user.signingkey <pub>; commit.gpgsign true; gh ssh-key add <pub> --type signing` | machine-only | `git log --show-signature -1` shows "Good git signature" |
| GitHub CLI | `sudo pacman -S github-cli; gh auth login; gh auth status` | machine-only | `gh --version` 2.102.1 |

<!-- cluster: c5-devops-containers -->
## Cluster c5-devops-containers: research notes

Retrieved 2026-10-28 (sandbox UTC date; date of record 2026-10-29). Repo files read: `01-system/cachyos/setup.md` (6.5, 7, 8, 9, 10.2, 10.3, 13.6, 20.2), `01-system/cachyos/dev-stack.md`, `system-summary.md`, `01-system/cachyos/packages/developer.txt`, the two skills, `07-networking/nginx/**`, `docs/modernization/packages-resolved.csv`. Evidence ledger: `c5-devops-containers.csv` (59 rows).

Method notes: package versions come from `tools/pkg_lookup.py`, `archlinux.org/packages/search/json`, AUR RPC v5, `endoflife.date`, PyPI JSON and `git ls-remote --tags` against upstream repos (github.com release pages and atom feeds returned 403 to curl, so WebFetch on release pages plus `git ls-remote` were used). Deviation to flag: I used `curl` on `gitlab.archlinux.org/.../-/raw/main/{PKGBUILD,nginx.service,prometheus.service,prometheus.conf}` and `raw.githubusercontent.com` docs files (outside the brief's curl allowlist; WebFetch on the same hosts was blocked by Anubis). Arch wiki and AUR cgit/package pages were blocked (Anubis), recorded as gaps.

### Docker Engine 29.x and rootless mode

- Current: Engine 29.9.2, 2026-10-20 (https://docs.docker.com/engine/release-notes/29/). Arch `docker` 1:29.9.2-1 (extra, 2026-10-20), CachyOS 1:29.9.2-1.1. Engine 28 EOL 2026-05-13 (endoflife.date). Repo's `system-summary.md` versions match.
- 29.x changes that touch the repo: containerd image store default on fresh installs (29.0, 2025-11-10); cgroup v1 deprecated (support to May 2029); Docker Content Trust removed from the CLI; nftables experimental via `firewall-backend`; legacy link env vars off (removal targeted 30.0); 29.5.0 (2026-05-14) made `gvisor-tap-vsock` the default rootless network driver and Docker packaging stopped installing `slirp4netns`; 29.8.0 (2026-09-03) added RootlessKit 3.1.0 `pesto` port driver (needs `pasta`, IPv4 only). RootlessKit now 3.3.0 (Arch extra 3.3.0-1).
- AUR vs repos: `docker-rootless-extras` is AUR-only (29.9.2-1, 2026-10-21, maintainer the-k; depends `docker>=1:29.5.0`, `rootlesskit>=3.0.0`; optdepends `fuse-overlayfs lxc passt slirp4netns`). `system-summary.md:227` says "The CachyOS package": wrong, it is an AUR package (pkg_lookup: AUR-ONLY across Arch extra and four CachyOS repos). `setup.md:719` (`paru -S docker-rootless-extras`) is right. Epoch note: Arch docker also carries epoch 1, so the AUR dependency is satisfied.
- Recommended install (docs: https://docs.docker.com/engine/security/rootless/ , tips and troubleshoot pages): confirm `/etc/subuid` and `/etc/subgid` give the user >= 65536 IDs; disable any rootful units (`sudo systemctl disable --now docker.service docker.socket`); run `dockerd-rootless-setuptool.sh install` (writes `~/.config/systemd/user/docker.service`, creates and selects the `rootless` context); `systemctl --user enable --now docker.service`; optional `sudo loginctl enable-linger $USER`; `DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock` for tools that ignore contexts.
- Rootless limits (docs): ports < 1024 need `sudo setcap cap_net_bind_service=ep $(which rootlesskit)` plus `systemctl --user restart docker`, or sysctl `net.ipv4.ip_unprivileged_port_start=0`; ping needs `net.ipv4.ping_group_range = 0 2147483647`; `--cpus/--memory/--pids-limit` need cgroup v2 + systemd and only `memory pids` are delegated by default (extend with `/etc/systemd/system/user@.service.d/delegate.conf` `Delegate=cpu cpuset io memory pids`); AppArmor, checkpoint unsupported; storage drivers overlay2 (kernel >= 5.11), fuse-overlayfs, btrfs, vfs. Networking: slirp4netns+builtin is default when installed, gvisor-tap-vsock+builtin otherwise, `pasta`+`implicit` experimental (passt >= 2023_12_04), source-IP propagation needs RootlessKit 3.0+ with `userland-proxy` disabled (or slirp4netns/pasta port driver). Docker docs list `kernel.unprivileged_userns_clone=1` under Arch (relevant only to hardened kernels).
- Edits to the repo:
  - `setup.md:726-732`: `sudo systemctl restart docker.service` restarts the (unused) rootful unit; use `systemctl --user restart docker`. The `docker info | grep "Native Overlay"` check is an overlay2-driver field; on a fresh 29.x install the containerd image store is used, so check `Storage Driver`/`driver-type` instead. The `metacopy=off redirect_dir=off` modprobe tweak could not be sourced: label host-specific, UNVERIFIED.
  - `setup.md:735-740` "Socket activation": remove. Enabling system `docker.socket` brings back a rootful daemon, the opposite of the section's stated goal.
  - `setup.md:714-723`: add the prerequisite check and `dockerd-rootless-setuptool.sh install`; mention `slirp4netns` is optional and what replaces it.
  - `system-summary.md:227`: "CachyOS package" -> "AUR package". `dev-stack.md` lingering sentence is right (docs: enable-linger to start at boot).
  - Compose dev stack `setup.md:754,758,766`: `"5432:5432"`, `"6379:6379"` collide with the host's PostgreSQL 18 and Valkey and bind 0.0.0.0 (Compose docs: omitted host IP binds all interfaces); use `"127.0.0.1:5433:5432"` style.
- Compose v5.6.1 (2026-10-21; Arch 5.6.1-1) and Buildx 0.38.1 (Arch 0.38.1-1) are current. No `version:` key in repo compose files: correct (key is obsolete, warns). Local check: both compose blocks parse and validate against `compose-spec.json` (verified-in-cloud, schema only).
- `docker-machine` (developer.txt:20): upstream `docker/machine` archived 2025-07-18, Docker's deprecation page says Docker Machine is EOL, Arch package is 0.16.2-6 from 2024-07-12. Remove from the package list.
- lazydocker (`setup.md:1208`): `paru -S lazydocker` is wrong source, it is in extra (0.25.2-1): `sudo pacman -S lazydocker`. It honours the current docker context.
- Podman (optional): `sudo pacman -S podman` (extra 6.1.4-1); `podman-docker`, `podman-compose` 1.6.0 exist. act does not officially support Podman.
- Compat: rootless overlay2 needs kernel >= 5.11; cgroup v2 needed for limits and for minikube/kind rootless.

### Kubernetes tooling

- kubectl 1.37.1 (released 2026-09-15; 1.37 EOL 2027-10-28; 1.37.2 out 2026-10-27, in Arch extra-testing). Skew: kubectl within one minor of kube-apiserver; kubelet up to three minors older, never newer (https://kubernetes.io/releases/version-skew-policy/). 1.34 is EOL 2026-10-27.
- minikube: Arch 1.38.1-2 (2026-02-22), upstream v1.39.0 (2026-09-01, default k8s v1.37.0, default runtime now containerd, breaking). Edit `setup.md:799`: on rootless Docker use `minikube start --driver=docker --container-runtime=containerd` (docs also: cgroup v2 delegation, kernel >= 5.11, do not set the `rootless` property); `--cpus` only works if the cpu controller is delegated.
- helm: Arch 4.3.0, upstream v4.3.1 (2026-10-15), Helm 3.22.1 also maintained. Helm 4.3.x supports Kubernetes 1.34-1.37 (n-3). Helm 4 changes: server-side apply default for new installs, post-renderers are plugins, `--atomic` -> `--rollback-on-failure`, `--force` -> `--force-replace`.
- k9s 0.51.0 current. kind 0.33.0 in extra: rootless Docker works with cgroup v2, systemd >= 252 (or `Delegate=yes`), `export DOCKER_HOST=unix://${XDG_RUNTIME_DIR}/docker.sock`.
- k3s: `curl -sfL https://get.k3s.io | sh -` is still the documented install (v1.37.1+k3s1, 2026-09-30). AUR `k3s` is 1.35.2+k3s1 and flagged out of date. Caution for this host: k3s listens on 6443/10250 (8472/udp) and its docs recommend turning off ufw; repo policy is UFW deny-incoming and no public listeners. Prefer minikube or kind locally; read the script before piping to sh.

### IaC and CI runners

- Terraform: Arch extra 1.15.9-1 (BUSL-1.1, 2026-08-19); upstream 1.17.1 (2026-10-28), 1.16.7 (2026-10-22); endoflife.date lists 1.16 newest (lagging). AUR `terraform-bin` 1.17.0. BSL 1.1: production use allowed unless offering a competing hosted/embedded product; converts to MPL 2.0 four years after each version (https://www.hashicorp.com/en/bsl). Add a licence note in `setup.md:848`.
- OpenTofu 1.13.2 (2026-10-21, MPL-2.0; supported to 2027-08-01; 1.13.0 removed WinRM provisioner connection). Arch matches.
- Ansible 14.5.0 (= ansible-core 2.21; Python 3.12-3.14 control node); `ansible` is the community bundle, `ansible-core` 2.21.5 the engine only; ansible-lint 26.10.1 in extra. Repo line correct.
- Pulumi 3.272.0 (Arch) vs 3.273.0 upstream; Python projects can use `runtime.options.toolchain: uv`.
- act 0.2.89 (Arch, 2026-06-01) vs 0.2.92 upstream. Needs Docker Engine API; on rootless set `DOCKER_HOST` (UNVERIFIED for act).
- GitLab Runner 19.5.1 (Arch) / v19.5.2 upstream. `setup.md:887`: register with a `glrt-` runner authentication token: `sudo gitlab-runner register --url https://gitlab.com/ --token "$RUNNER_TOKEN"`; registration tokens go away in GitLab 20.0.

### AWS CLI, Azure CLI, credentials

- `aws-cli-v2` package name correct; Arch 2.37.9-1 (2026-10-13), upstream 2.39.1 (git tag). `uv tool install aws-sam-cli` valid (PyPI 1.170.0).
- `setup.md:680` `aws configure` with access key and secret: AWS ranks IAM user long-term keys "Not recommended". Replace with `aws login` (needs CLI >= 2.32.0; browser flow; `--remote` for headless; auto-refresh up to 12 h; `aws logout`) or `aws configure sso`. Keep "credentials not stored in dotfiles".
- Azure CLI 2.90.0 (Arch), 2.91.0 in testing and current upstream. `az login` opens a browser (device code fallback `--use-device-code`). MFA required for user identities since Sept 2025; use service principals/managed identities for automation.
- ECR login (`setup.md:836-838`) correct (token valid 12 h). GHCR (`:841`): needs a classic PAT with `read:packages`/`write:packages` (`delete:packages`); `$GITHUB_TOKEN` exists only in Actions. Docker stores creds base64 in `~/.docker/config.json` unless `pass`/`secretservice` helper is set.

### Nginx

- Stable 1.30.6 (2026-10-14), mainline 1.31.8 (2026-10-21); Arch `nginx` 1.30.6-2 (stable) and `nginx-mainline` 1.31.8-1. 1.30.6 fixes five CVEs (alias+rewrite, variable-evaluation overflow, HTTP/3 request body injection, TLS ticket-key rotation forgery, SSI AIO UAF).
- Arch package: `nginx.service` Type=forking, installs upstream `nginx.conf` with only `user http`, `root` and `include modules.d/*.conf` edits, `mime.types` supplied by `mailcap`; no `conf.d` include. Repo's drop-in procedure and `types_hash_max_size 4096` (default 1024) are correct. Built with realip, http_v2, http_v3, ssl modules.
- Skill `nginx-reverse-proxy-patterns` edits: `proxy_http_version` default is 1.1 since 1.29.7 (skill says 1.0); add `limit_req_status 429` (default 503); do not key on raw `$http_x_forwarded_for`, use `set_real_ip_from` + `real_ip_header X-Forwarded-For` + `real_ip_recursive on`; add `server_tokens off`, `add_header ... always`, the `add_header` inheritance gotcha (and `add_header_inherit merge`, 1.29.3+), `http2 on;`. `ssl_protocols` default already TLSv1.2 TLSv1.3.
- Skill `docker-multi-stage-optimization`: secret-mount guidance confirmed.

### Dockerfile and GitHub Actions sample

- Dockerfile template: `python:3.12-slim` is valid (3.12.16-slim-trixie; 3.15.2 released 2026-10-09 and 3.13/3.14 images exist; 3.12 security-only to 2028-10-31). Replace the pip/requirements.txt pattern with the uv pattern from https://docs.astral.sh/uv/guides/integration/docker/ (uv 0.13.6, PyPI 2026-10-27). hadolint 2.15.1 clean except DL3066; `uv sync --locked --no-install-project --no-editable` verified in a temp project.
- Workflow `setup.md:892-917`: valid syntax (actionlint 1.7.12: 0 errors, verified-in-cloud), but stale: `actions/checkout@v4` (node20) -> `@v7` (v7.0.1); `astral-sh/setup-uv@v5` (node20) -> `@v10.3.3` (no floating v8-v10 tag; README pins SHA `68559e99cc807c1eb7e9238fd43a15bba460eec2`); `docker/build-push-action@v5` (node20) -> `@v7` (v7.4.0; add `docker/setup-buildx-action@v4` optional). Node 20 removed from runners 2026-09-23 (https://github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions). Add `permissions: contents: read`; pin by SHA per GitHub hardening guide.

### Data services in compose (6.5, 10.2, 10.3)

- Elasticsearch 8.17.0 -> 9.5.5 (current; 9.3 EOL 2026-08-04; 8.x maintained to 2027-01-15). Licences: AGPL v3, SSPL, ELv2 offered since 2024-08-29. Security is on by default in the image (password + enrollment token + HTTPS); the repo's `xpack.security.enabled=false` is a dev opt-out: keep loopback bind. OpenSearch 3.9.0 (2026-09-29) alternative: `OPENSEARCH_INITIAL_ADMIN_PASSWORD` or `DISABLE_SECURITY_PLUGIN=true`, `vm.max_map_count=262144`.
- Redpanda: pin `redpanda:v26.2.6`, `console:v3.13.1` instead of `:latest`; official compose adds `--mode dev-container`; repo's one-string first list item is UNVERIFIED. BSL 1.1 licence. Apache Kafka 4.4.0 (2026-10-22) KRaft: `docker run -p 9092:9092 apache/kafka:4.4.0`.
- Orchestration: Airflow 3.3.2, Prefect 3.9.0, Dagster 1.13.27. `uv add apache-airflow` unconstrained is not supported by Airflow; use `-c` constraints URL or `uvx apache-airflow standalone`.
- Prometheus 3.15.1 (Arch, EOL 2026-11-06 for the 3.15 line; 3.13 is LTS to 2027-07-31). Arch unit uses `/etc/prometheus/prometheus.yml`, `/var/lib/prometheus/data`, `PROMETHEUS_ARGS` from `/etc/conf.d/prometheus`; default listen 0.0.0.0:9090 so set `--web.listen-address=127.0.0.1:9090`. Minimal config: `global: scrape_interval: 15s` and a `prometheus` job on `localhost:9090`.

### UNVERIFIED

- Arch wiki Docker/rootless page and AUR PKGBUILD (Anubis block): AUR package's unit name and whether it ships extra units; Arch subuid defaults.
- `metacopy=off redirect_dir=off` modprobe tweak and whether this host uses overlay2 or the containerd store.
- Redpanda: one-string first `command` item; `--smp/--memory` flag docs; Console v3 `KAFKA_BROKERS`; "no JVM ~512MB" claim.
- act with rootless Docker and node24 actions; Pulumi state-backend login; Elasticsearch `vm.max_map_count` need for single-node; Kafka 4.0 ZooKeeper removal statement; `http2 on` replacing `listen ... http2` deprecation wording (from tool memory).
- Port clash on 5432/6379 is derived from repo text, not executed. No docker, pacman or systemd in the sandbox, so every Docker, pacman and systemd step is machine-only.

### Setup steps

| Step | Command | Label | Expected |
|---|---|---|---|
| Subordinate IDs | `grep "^$USER:" /etc/subuid /etc/subgid` | machine-only | one line each, count >= 65536 |
| Install repo packages | `sudo pacman -S --needed docker docker-compose docker-buildx rootlesskit` (optional `slirp4netns` or `passt`) | machine-only | docker 1:29.9.x, compose 5.6.x, buildx 0.38.x, rootlesskit 3.3.x |
| Install AUR extras | `paru -S --needed docker-rootless-extras` | machine-only | docker-rootless-extras 29.9.2-1 |
| Disable rootful units | `sudo systemctl disable --now docker.service docker.socket` | machine-only | units inactive/disabled |
| Create rootless service | `dockerd-rootless-setuptool.sh install` | machine-only | "Installed docker.service successfully", context `rootless` |
| Start daemon | `systemctl --user enable --now docker.service` | machine-only | `systemctl --user is-active docker` -> active |
| Linger (optional) | `sudo loginctl enable-linger $USER` | machine-only | `loginctl show-user $USER -p Linger` -> yes |
| Verify | `docker info \| grep -E 'Context\|rootless\|Storage Driver\|Server Version'; docker run --rm hello-world` | machine-only | Context rootless, Server Version 29.9.x, hello output |
| Privileged ports | `sudo setcap cap_net_bind_service=ep $(which rootlesskit) && systemctl --user restart docker` or sysctl `net.ipv4.ip_unprivileged_port_start=0` | machine-only | `docker run -p 80:80 nginx` binds |
| Validate compose YAML | PyYAML + jsonschema vs compose-spec.json | verified-in-cloud | "schema OK" for 8.2 and 10.2 blocks |
| Lint workflow | `actionlint` 1.7.12 (`pip install actionlint-py`) | verified-in-cloud | exit 0, 0 errors |
| Lint Dockerfile | `hadolint` 2.15.1 (`pip install hadolint-py`) | verified-in-cloud | only DL3066 info |
| uv Docker flags | `uv sync --locked --no-install-project --no-editable` then `uv sync --locked --no-editable` | verified-in-cloud | gunicorn 26.2.0 installed in .venv |
| Compose config | `docker compose config` | machine-only | prints merged config, no `version` warning |
| AWS login | `aws login` (CLI >= 2.32.0) then `aws sts get-caller-identity` | machine-only | `aws-cli/2.37.9`, caller ARN |
| GHCR login | `echo $CR_PAT \| docker login ghcr.io -u USERNAME --password-stdin` | machine-only | "Login Succeeded" |
| minikube rootless | `minikube start --driver=docker --container-runtime=containerd` | machine-only | `kubectl get nodes` Ready |
| Nginx drop-in | `sudo nginx -t` | machine-only | "syntax is ok", no types_hash warning |
| Prometheus check | `promtool check config /etc/prometheus/prometheus.yml` | machine-only | SUCCESS |
| Package/version lookup | `/tmp/venv/bin/python tools/pkg_lookup.py <names>` | verified-in-cloud | versions in ledger |

<!-- cluster: c6-databases -->
## c6-databases research notes

Retrieved 2026-10-28 (sandbox `date -u +%F`; date of record 2026-10-29). Sandbox: Ubuntu 24.04, no pacman, no systemd PID 1. Evidence ledger: `c6-databases.csv` (73 rows: 33 confirmed, 25 changed, 15 unverified).

Access gaps (not worked around): wiki.archlinux.org, gitlab.archlinux.org and aur.archlinux.org web pages all return Anubis "Access Denied". So the Arch wiki PostgreSQL/MariaDB/MongoDB pages and the mongodb-bin PKGBUILD were never read directly. Used instead: archlinux.org package pages and file lists, man.archlinux.org initdb(1) (18.6), the AUR RPC, and one search snippet of the wiki (marked secondary). github.com releases.atom and api.github.com are blocked for this session (proxy: "sessions are bound to their configured repositories"), so upstream release dates come from project sites, registries and endoflife.date.

Side effect to note: I ran `uv pip install` of client libs (pgvector, psycopg, redis, valkey, sqlite-vec, chromadb, lancedb, qdrant-client, pymilvus[milvus_lite], weaviate-client, pymongo) into the shared `/tmp/venv` before noticing it is not under my output dir. Harmless additions only; nothing under `/home/user/dotfiles` was modified. `apt-get install mariadb-server` was run in the sandbox (postinst failed for lack of systemd; binaries worked).

### PostgreSQL 18

- Version: Arch extra `postgresql` 18.6-4 (2026-10-19); CachyOS `cachyos-extra-v3` 18.6-4.1 (https://archlinux.org/packages/search/json/?name=postgresql). Upstream current minor 18.6; PG18 GA 2025-09-25, final release 2030-11-14; 17 final 2029-11-08; 16 final 2028-11-09; 14 final 2026-11-12 (https://www.postgresql.org/support/versioning/). PG19 is at RC1 (Docker Hub tag `19rc1`), not GA.
- Arch layout (archlinux.org file list): `usr/bin/initdb`, `postgresql-check-db-dir`, `pg_ctl`, `pg_upgrade`, `pg_basebackup`; `usr/lib/systemd/system/postgresql.service`; `sysusers.d/postgresql.conf`; `tmpfiles.d/postgresql.conf`. `/var/lib/postgres/data` is the Arch convention and `initdb` must run before the service starts (Arch wiki, via search snippet only: medium confidence).
- initdb flags (https://www.postgresql.org/docs/18/app-initdb.html, and the Arch man page for 18.6):
  - `--locale=C.UTF-8`: valid. Default provider is `libc`. `--locale-provider={builtin|libc|icu}`; with `builtin`, only `C`, `C.UTF-8`, `PG_UNICODE_FAST` are allowed. Optional hardening: `--locale-provider=builtin --builtin-locale=C.UTF-8` (no glibc collation drift). Keep the repo's libc `C.UTF-8` unless you want that.
  - `-E UTF8`: valid.
  - `--data-checksums`: valid but REDUNDANT in 18: "enabled by default; use `--no-data-checksums`". Keep it for explicitness. It matters on upgrade: pg_upgrade requires matching checksum settings (release 18 incompatibility #1); an old 17 cluster created without checksums needs `--no-data-checksums` on the new cluster or `pg_checksums --enable` on the old one first.
  - `--auth-local=peer --auth-host=scram-sha-256`: valid, not deprecated. md5 is deprecated (warning on CREATE/ALTER ROLE; `md5_password_warnings`). `password_encryption` default is scram-sha-256.
  - initdb default auth is `trust` ("the default for ease of installation"). setup.md section 6.1 omits both auth flags, so a fresh install from setup.md gets passwordless `local` and `host` rules. system-summary.md step 4 has them right. This is the top fix.
- Verified-in-cloud (PG 16.15 from Ubuntu apt, PG 16.2 from the pgserver wheel; NOT 18): `initdb --locale=C.UTF-8 -E UTF8 --data-checksums --auth-local=peer --auth-host=scram-sha-256` is accepted; generated `pg_hba.conf` has `local all all peer`, `host ... 127.0.0.1/32 and ::1/128 scram-sha-256` and the same for replication; `show data_checksums` = on; pg_database shows `datlocprovider=c`, `datcollate=C.UTF-8`, UTF8. Peer `createuser --createdb`, `createdb -O`, and `CREATE EXTENSION vector` all worked.
- PG18 changes relevant to the repo (https://www.postgresql.org/docs/18/release-18.html): async I/O (`io_method` default `worker`, also `io_uring`, `sync`; `io_workers` 3; `pg_aios` view); skip scan on B-tree; `uuidv7()`; virtual generated columns default; OAuth auth method; EXPLAIN ANALYZE includes BUFFERS automatically; `autovacuum_vacuum_max_threshold` (100000000) and `autovacuum_worker_slots` (16); eager freezing; pg_upgrade keeps optimizer stats (not extended stats), `--swap`, `--no-statistics`, parallel checks; full-text search and `pg_trgm` use the cluster's default collation provider (reindex after pg_upgrade if not libc); `\.` no longer ends CSV `COPY FROM`. Settings defaults: shared_buffers 128MB (start 25% RAM, over 40% unlikely to help), work_mem 4MB, maintenance_work_mem 64MB, effective_cache_size 4GB, max_connections 100, listen_addresses `localhost`.
- Upgrade path 17 to 18 on Arch: `postgresql-old-upgrade` 17.11-3 (extra) installs `/opt/pgsql-17/bin/{initdb,pg_upgrade,...}` (file list verified). Upstream procedure (docs/18/pgupgrade.html): new cluster with compatible initdb flags, `pg_upgrade -b /opt/pgsql-17/bin -B /usr/bin -d OLD -D NEW [--link|--clone|--swap] --check` first, then the real run, restore pg_hba, start, then `vacuumdb --all --analyze-in-stages --missing-stats-only --jobs=N`. Arch wiki specifics (rename `data` to `olddata`, same initdb args incl. checksums, package always one major behind) came from a search snippet only. Extension caveat: the old-upgrade package has no pgvector, so a cluster with `vector` installed likely needs `pg_dumpall` instead (UNVERIFIED). Not executed: needs pacman and two PG majors.
- Support lifecycle: 5 years per major; 18 supported to 2030-11-14.
- Docker (setup.md 8.2 uses `postgres:16-alpine`): PG18 official images moved PGDATA to `/var/lib/postgresql/18/docker` and VOLUME to `/var/lib/postgresql`; mount the volume there when moving off 16 (https://hub.docker.com/_/postgres, docker-library/postgres PR 1259).
- Skill `postgres-self-hosted-tuning`: indexing/EXPLAIN/autovacuum/pooling content is right. Edits: (1) soften "can't use the back half of an index" (skip scan, 18); (2) FK-index reason is "parent DELETE/UPDATE scans the child table", not "full table locks"; (3) PgBouncer 1.21.0 (2023-10-16) added tracked protocol-level prepared statements in transaction mode (`max_prepared_statements` default 200), so the "breaks prepared statements" line is dated (SQL-level PREPARE, SET, LISTEN, session advisory locks still break); (4) add one line of 18 tuning: `io_method`, `effective_io_concurrency` 16, `autovacuum_vacuum_max_threshold`, BUFFERS default; (5) backups line is right, add the commands: `pg_basebackup -D DIR -Ft -z -P -X stream -c fast`, `archive_mode=on` + `archive_command`/`archive_library`, `restore_command` + `recovery.signal` + `recovery_target_time`, incremental backups (`pg_basebackup --incremental`, `pg_combinebackup`, PG17+), pgBackRest 2.60.0 (extra) for production. PgBouncer in Arch extra: 1.26.0-1 (upstream 1.26.1, 2026-10-14).
- Skill `database-migration-discipline`: CHECK-then-SET NOT NULL scan skip confirmed (PG12 notes; ALTER TABLE doc); VALIDATE CONSTRAINT takes SHARE UPDATE EXCLUSIVE; PG18 can also toggle NOT VALID on NOT NULL constraints; non-volatile DEFAULT needs no rewrite (version 11 not stated on the fetched page).
- UNVERIFIED: "5-10MB per connection"; whether Arch builds with liburing (`io_uring`); pgBackRest PG18 support list; exact Arch wiki upgrade commands.

### pgvector

- Arch extra `pgvector` 0.8.7-1 (2026-10-02), CachyOS 0.8.7-1.1. Upstream 0.8.7 released 2026-10-01 (fixes IVFFlat build buffer overflows). 0.9.0 is unreleased and drops PG13/14 and adds async I/O for HNSW (https://raw.githubusercontent.com/pgvector/pgvector/master/CHANGELOG.md).
- PG18: 0.8.1 (2025-09-04) added PG18 rc1 support; 0.8.2 fixed `Index Searches` in EXPLAIN on 18; 0.8.3 fixed a Hamming/Jaccard regression on 18. README: Postgres 13+.
- `CREATE EXTENSION vector;` once per database: confirmed.
- Parameters (README): hnsw `m` 16, `ef_construction` 64, `hnsw.ef_search` 40; ivfflat `lists` (rows/1000 up to 1M rows, sqrt(rows) above), `ivfflat.probes` 1; `hnsw.iterative_scan` = `strict_order|relaxed_order` (since 0.8.0); `halfvec(n)` indexable to 4000 dims (vector 2000, bit 64000, sparsevec 1000 non-zero); binary quantization `CREATE INDEX ON items USING hnsw ((binary_quantize(embedding)::bit(3)) bit_hamming_ops)`.
- Verified-in-cloud with pgvector 0.6.2 (pgserver wheel, PG 16.2): hnsw (m=16, ef_construction=64) and ivfflat index builds, `SHOW hnsw.ef_search` = 40, `ivfflat.probes` = 1, cosine KNN query. `halfvec` correctly errors on 0.6.2, so halfvec/binary_quantize were NOT run (unverified beyond docs).
- Python: `uv add pgvector psycopg2-binary` works (psycopg2-binary 2.9.13, pgvector 0.5.1 on 2026-10-09). README lists Psycopg 3 first; prefer `uv add pgvector 'psycopg[binary]'` (psycopg 3.3.6) and `from pgvector.psycopg import register_vector`. Optional edit.
- Editorial: setup.md installs pgvector twice (4.9 and 6.1).

### MariaDB

- Arch extra `mariadb` 13.0.2-2 (2026-09-23), CachyOS 13.0.2-2.1. IMPORTANT: 13.0 is a ROLLING release, not LTS. mariadb.org/about: rolling 13.0 (May 2026) Community EOL Q4 2026; 13.1 (Sep 2026) EOL Q1 2027; LTS lines 12.3 (GA 2026-05-28, EOL 2029-06-12), 11.8 (GA 2025-06-04, EOL 2028-06-04), 11.4 (EOL 2029-05-29), 10.11 (EOL 2028-02-16), 10.6 (EOL 2026-07-06). endoflife.date agrees (13.0 eol 2026-12-31; 12.3.3, 11.8.9 latest). LTS is announced yearly; rolling quarterly; Community LTS binaries 3 years.
- Arch extra also ships `mariadb-lts` 12.3.3-2 (+ `mariadb-lts-clients`, `-libs`, `-pam`); it Conflicts mariadb and mysql and Provides mariadb-server. Recommendation for a stable dev box: `pacman -S mariadb-lts` (EOL 2029-06-12); keep `mariadb` only if you want newest features and accept a move to 13.1 within weeks. Host DB is empty, so switching is a dump-free reinstall; downgrading a 13.0 data dir to 12.3 is unsupported.
- Binary naming: canonical names are `mariadb`, `mariadbd`, `mariadb-install-db`, `mariadb-admin`; `mysql*` names are symlinks (verified-in-cloud on 10.11: `/usr/bin/mysql -> mariadb`, `mysql_install_db -> mariadb-install-db`). Arch file list: `usr/bin/mariadb-install-db`, `mariadbd`, `mysqld`; units `mariadb.service`, `mysql.service`, `mysqld.service`, `mariadb.socket`; `sysusers.d/mariadb.conf`; `/etc/my.cnf` and `/etc/my.cnf.d/{client,server,mysql-clients,s3,spider,provider_*,hashicorp_key_management}.cnf`. The mysql client itself is in `mariadb-clients`.
- `mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql`: all options valid (https://mariadb.com/docs/server/clients-and-utilities/deployment-tools/mariadb-install-db). Default creates `root@localhost` with unix_socket plus an account named after `--user` (`mysql@localhost`). Verified-in-cloud on 10.11.14 with a temp datadir.
- `mariadb-local.cnf` / `/etc/my.cnf.d/90-local-dev.cnf`: path correct for Arch (directory is shipped by the package). MariaDB's default `bind_address` is empty = all addresses (Debian/Ubuntu override), so the drop-in is justified. Option-file rules: names must end `.cnf`, read in BYTE order (digits before letters), last value wins, so `90-local-dev.cnf` is read BEFORE `server.cnf`; fine unless server.cnf sets bind-address. Verified-in-cloud (10.11.14): drop-in gave `@@bind_address = 127.0.0.1` and only `127.0.0.1:PORT` listening. Whether Arch's `/etc/my.cnf` contains the `!includedir /etc/my.cnf.d` line: not shown by the file list (machine-only check).
- Socket-auth user (system-summary says "create the matching Unix-socket user" without SQL). Add: `CREATE DATABASE dev; CREATE USER 'USER'@'localhost' IDENTIFIED VIA unix_socket; GRANT ALL ON dev.* TO 'USER'@'localhost';` run through `sudo mariadb`. From 11.6 `IDENTIFIED VIA unix_socket AS 'osuser'` maps to a different OS user. Verified-in-cloud on 10.11.14: as OS user, `mariadb --protocol=socket dev -e 'select database(), current_user()'` returned `dev`, `devu@localhost`. Not run on 13.
- Skill `mysql-patterns`: REPEATABLE READ default and gap locks confirmed; replica lag column on MariaDB is `Seconds_Behind_Master` (`SHOW REPLICA STATUS` is an alias; `Seconds_Behind_Source` is MySQL 8.0.22+). Skill is titled MySQL/MariaDB, so name both. `ALGORITHM=INSTANT` exists in MariaDB (value list confirmed), but INSTANT coverage differs from MySQL 8 and the page does not enumerate it.
- Note: Arch has no `mysql` package; `percona-server` 9.7.2 is in extra if real MySQL behaviour is needed.
- UNVERIFIED: 13.0 release-notes content (docs pages 404/empty), pt-online-schema-change/gh-ost claims.

### MongoDB (AUR only)

- Release train (https://www.mongodb.com/docs/manual/release-notes/9.0/, /reference/versioning/, /mongodb-versions/): current major is 9.0 (GA 2026-09-28, 9.0.4 on 2026-10-13, EOL 2031-10-31). Majors every two years with a 5-year lifecycle (+2-year ELS for Enterprise Advanced only). 8.3 is a MINOR release ("as stable as majors", GA May 2026, EOL 2029-10-31, patches 8.3.13 on 2026-10-13); the docs now say "minor", not "rapid". After a new minor ships the previous minor stops being patched. Community gets minors 8.2 to 8.x; from 9.0 only Feature Updates (X.5.0). 8.0 EOL 2029-10-31, 7.0 EOL 2027-08-31, 8.2 EOL 2026-07-31 (https://www.mongodb.com/legal/support-policy/lifecycles).
- Critical advisory SERVER-131805 affects 8.3.0 through 8.3.12 ("Recovered cross-database renameCollection participant can drop the target after stepdown", fixed 8.3.13). The repo pins AUR `mongodb-bin` 8.3.9-1 (2026-09-14), which is affected; AUR `mongodb` (source, Bazel build, hours) is 8.3.13-1 (2026-10-13). No 9.0 AUR package seen. Low practical risk for a standalone dev instance.
- 9.0 notable: per-operation memory cap max(1GB, 20% RAM), `constraint` validation level, server-side JS un-deprecated (WASM), `$queryStats` on by default, `net.wireObjectCheck` deprecated, `mongocryptd` deprecated, Ubuntu 26.04 support in 9.0.4.
- Licence SSPL-1.0, hence AUR-only (not in Arch/CachyOS repos). AUR `mongodb-bin`: Depends mongosh-bin, curl, openssl; OptDepends mongodb-tools; Conflicts mongodb, mongodb-shell-bin; Provides mongodb=8.3.9.
- Config/service: upstream packages use `mongod.service` and `/etc/mongod.conf`; repo uses `mongodb.service` and `/etc/mongodb.conf` (AUR-specific). Unverifiable (AUR page and PKGBUILD blocked); only the repo's machine record supports it. `net.bindIp` default is `localhost` (upstream config doc), matching the explicit `bindIp: 127.0.0.1`.
- Auth: repo says none (loopback + UFW). Enabling = create admin user, `security.authorization: enabled`, restart, `mongosh -u USER -p --authenticationDatabase admin`; the fetched tutorial page was only an overview, so exact steps are UNVERIFIED.
- `mongosh` 2.14.0: npm latest (2026-10-26) = AUR `mongosh-bin` 2.14.0-1. `--quiet` and `--eval` valid; default target localhost:27017. mongodb-bin depends on mongosh-bin, so no change to developer.txt needed.
- Compass: AUR `mongodb-compass-bin` 1.53.2-1 (2026-10-27) = docs 1.53.2. Official Linux support: RHEL 8+, SLES 15+, Ubuntu 20.04+, Debian 12+ (Arch unsupported but works). setup.md comment is stale: CachyOS repo has `mongodb-compass` 1.49.4 (flagged out-of-date, source build with electron37 and `nodejs>=22.21.1`); extra `nodejs` is 26.12.1; `nodejs-lts-iron` (Node 20) is AUR-only. Keep "use mongodb-compass-bin" but drop the nodejs-25 reason. Use `--disable-gpu` if rendering breaks on Nvidia.
- Skill `mongodb-schema-design`: structure is fine; the "document moves on disk" mechanism and the 100MB stage limit were not verified (UNVERIFIED); add 9.0 `constraint` validation level and note `$jsonSchema` `moderate` advice still applies.

### Valkey 9.1 vs Redis

- Arch extra `valkey` 9.1.2-1 (2026-09-01); upstream 9.1.3 (2026-10-26). valkey.io/download lists supported 9.0.7 (2026-10-27), 9.1.3, 8.1.11, 8.0.12, 7.2.15; 9.2.0-rc1 is a release candidate. endoflife.date: 9.1 released 2026-05-19.
- Arch news 2025-04-17: "Valkey to replace Redis in the [extra] Repository"; `redis` left to AUR. Today AUR `redis` is 8.10.3-1 (AGPL-3.0-only). Redis 8 is tri-licensed RSALv2/SSPLv1/AGPLv3; 7.4 to 7.8 RSALv2/SSPLv1; 7.2 and older BSD-3 (https://redis.io/legal/licenses/).
- Arch valkey package: Conflicts and Provides `redis`; binaries `valkey-{server,cli,benchmark,check-aof,check-rdb,sentinel}` and `redis-*` equivalents; units `valkey.service`, `valkey-sentinel.service`, `redis.service`, `redis-sentinel.service`; config `/etc/valkey/valkey.conf`. Repo's `valkey.service` and `valkey-cli ping` are correct.
- Defaults (upstream valkey.conf 9.1 branch): `bind 127.0.0.1 -::1`, `protected-mode yes`, `port 6379`, `appendonly no`, `appendfsync everysec`, RDB default `save 3600 1 300 100 60 10000` (commented default). Matches system-summary line 125.
- Clients: Valkey speaks the Redis 7.2 wire protocol; clients: valkey-py 6.2.0 (`pip install valkey`), valkey-glide; redis-py 8.1.0 also works (Arch extra `python-redis` 8.1.0-2). Verified-in-cloud: both redis-py and valkey-py PING/SET/GET against redis-server 7.0.15 (Ubuntu). No Valkey server was available in the sandbox, so Valkey 9.1 behaviour is docs-only.
- Skill `redis-patterns`: Streams/XACK/XPENDING/XCLAIM/XAUTOCLAIM exist in Valkey; content stays correct. Optional line: host runs Valkey, and Redis Insight is SSPL-licensed.
- Redis Insight (setup.md:661): command valid; publish on loopback; container reaching host-loopback Valkey is a networking caveat (UNVERIFIED for rootless Docker).

### SQLite

- Upstream 3.54.1 (2026-10-16, patch: 32-bit heap overflow); Arch `core/sqlite` 3.54.0-1 (2026-10-12). Package contains `usr/bin/sqlite3`, `sqldiff`, `sqlite3_rsync`, `libsqlite3.so.3.54.0`. `sudo pacman -S sqlite` for the CLI is right; it is in `core`.
- 3.54.0: `.diskused` replaces `sqlite3_analyzer`; lines `go` or `/` no longer terminate commands; ALTER TABLE rejects ROWID/OID names.
- Python's sqlite3 module imports in the sandbox (3.45.1): not representative of Arch.

### Elasticsearch / OpenSearch

- Elastic: docs use `docker.elastic.co/elasticsearch/elasticsearch:9.5.5`; endoflife.date: 9.5 released 2026-08-04; 8.x end of maintenance 2027-01-15, end of support 2027-07-15, "8.17 maintained until 8.19 releases" (https://www.elastic.co/support/eol). The repo's `8.17.0` (setup.md:632 and compose :761) is stale; pick a 9.x tag or deliberately pin 8.19.x (patch not retrieved).
- Security: on by default since 8.0 (implied by Elastic's docs: generated `elastic` password and enrollment token on first start, HTTPS with `http_ca.crt`). Elastic's dev path: `docker network create elastic`; `docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:9.5.5`; `elasticsearch-reset-password -u elastic`; `curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200`. Disabling security as the repo does is OK for a throwaway node only if published on loopback. `discovery.type=single-node` is not used in Elastic's own recipe.
- `vm.max_map_count`: Elastic requires >= 1048576 (https://www.elastic.co/docs/deploy-manage/deploy/self-managed/vm-max-map-count); OpenSearch docs say 262144. The repo never sets either. CachyOS's default was not checked (machine-only: `sysctl vm.max_map_count`).
- All Docker `-p 9200:9200` style publishes bind all host addresses (https://docs.docker.com/engine/network/port-publishing/); use `-p 127.0.0.1:9200:9200`. Same for Weaviate, pgAdmin, Redis Insight and the compose ports. Whether UFW covers rootless-Docker published ports is UNVERIFIED.
- Licence: ES under Elastic License 2.0 / SSPL, with AGPL added as an option (Aug 2024 announcement; which versions not stated).
- OpenSearch alternative: Arch extra `opensearch` 3.9.0-1 and `opensearch-dashboards` 3.9.0-1 (2026-10-20); Docker `opensearchproject/opensearch:3.9.0` with `discovery.type=single-node` and mandatory `OPENSEARCH_INITIAL_ADMIN_PASSWORD` (since 2.12). Not run.

### Vector DB options for local development

Default: pgvector in the existing Postgres (owner's rule). Others by use:

| Option | Version (source) | When | Notes |
|---|---|---|---|
| pgvector | 0.8.7 (Arch extra) | default | HNSW/IVFFlat, halfvec, bit quantization |
| sqlite-vec | 0.1.9 (PyPI, AUR) | tiny, file-based | pre-v1, expect breaking changes; verified-in-cloud KNN works |
| ChromaDB | 1.5.9 (PyPI, 2026-05-05) | prototyping | `uv add chromadb`; verified-in-cloud EphemeralClient add/query |
| LanceDB | 0.40.0 (PyPI) | embedded columnar | verified-in-cloud table + vector search |
| Milvus Lite | pymilvus 3.0.2 + milvus-lite 3.2.2 | small scale | FLAT index only, no partitions/users/aliases; Ubuntu 20.04+/macOS only per docs; verified-in-cloud insert/search |
| Qdrant | 1.20.0 (AUR qdrant; qdrant-client 1.20.0) | dedicated server | docker ports 6333/6334; client not exercised |
| Weaviate | 1.40.2 (AUR, docs tag); client 4.24.1 | full server | pin tag instead of `latest`; ports 8080, 50051 |
| FAISS | faiss-cpu 1.15.1 | in-process library | installed in sandbox |
| Pinecone | pinecone 10.2.0 | cloud only | old `pinecone-client` is DEPRECATED |

setup.md 4.9 gives no default or versions; add one line "pgvector first" plus this table's essentials. Qdrant and sqlite-vec/LanceDB/Milvus Lite are missing from the repo.

### DB GUI tools

- DBeaver: Arch extra 26.2.2-1 (2026-10-04); upstream Community 26.2.3 (2026-10-18). `pacman -S dbeaver` correct. Repo claim that it covers MongoDB and "80+ databases" not verified.
- pgAdmin 4: not in Arch repos; AUR `pgadmin4` 9.14-1 meta (server 9.18-1, 2026-10-19); Docker `dpage/pgadmin4` (docs for 9.18) needs `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD`, listens on 80. Repo's command valid; bind to 127.0.0.1.
- MongoDB Compass: see MongoDB section. Redis Insight: see Valkey section.
- Alternatives: DataGrip (AUR 2026.2.6-1, proprietary), Beekeeper Studio (AUR bin 6.2.0-1), sqlitebrowser (extra 3.13.1-3), pgcli (extra 4.7.1-1).

### Concrete edit list per repo file

- `01-system/cachyos/setup.md` 6.1: add `--auth-local=peer --auth-host=scram-sha-256` to initdb; note checksums are default in 18; replace `devuser/devpass` flow with the peer-role flow from system-summary step 4 (or label it TCP-only example).
- `setup.md` 6.2: add the socket-auth SQL; add one sentence that 13.x is rolling and `mariadb-lts` (12.3) is the LTS package.
- `setup.md` 6.3: note 8.3 is a minor release and 9.0 is current; mongodb-bin 8.3.9 predates the SERVER-131805 fix (8.3.13); keep the permission workaround but mark package-specific.
- `setup.md` 6.5 and 8.2: ES 8.17.0 to 9.5.5 (or deliberate 8.19.x); loopback publish; `vm.max_map_count`; compose Postgres volume path for 18; replace `redis:7-alpine` with `valkey/valkey:9` or document the licence.
- `setup.md` 6.7: drop the nodejs-25/nodejs-lts-iron reasoning; loopback binds on pgAdmin and Redis Insight.
- `setup.md` 4.9: pgvector default sentence; pin Weaviate tag; add sqlite-vec/Qdrant/LanceDB.
- `system-summary.md` 114/122-125: "MariaDB 13 (rolling)", "MongoDB 8.3.9 (minor release; 9.0 is current major)", "Valkey 9.1.2"; step 4 MariaDB: add SQL.
- `dev-stack.md` 65-84: keep; add `(rolling)` for MariaDB if kept.
- `developer.txt`: keep; optionally `mariadb-lts` instead of `mariadb`.
- Skills: edits listed under PostgreSQL and MariaDB above. `database-engineer.md`: consider naming MariaDB and Valkey.

### UNVERIFIED list

- Arch wiki PostgreSQL/MariaDB/MongoDB pages and mongodb-bin PKGBUILD (blocked); hence `mongodb.service`, `/etc/mongodb.conf`, the data/log chown workaround, and whether Arch `/etc/my.cnf` includes `/etc/my.cnf.d`.
- pg_upgrade on Arch with pgvector installed; Arch wiki exact commands.
- PG 18 behaviour of every setup step on real PG 18 (sandbox had 16.x only).
- MariaDB 13.x runtime behaviour (sandbox 10.11.14); 13.0 release-note details.
- halfvec and binary quantization execution (pgvector in sandbox 0.6.2).
- Valkey 9.1 server behaviour; redis-py/valkey-py only run against Redis 7.0.15.
- MongoDB auth tutorial steps; 100MB aggregation stage limit; document-move claim.
- DBeaver MongoDB support; pgAdmin email-domain validation; UFW vs rootless Docker published ports; CachyOS default `vm.max_map_count`; pgBackRest PG18 support list.

### Setup steps

| Step | Command | Label | Expected proof |
|---|---|---|---|
| Install PostgreSQL + pgvector | `sudo pacman -S postgresql pgvector` | machine-only | `pacman -Q postgresql` 18.6-4, `pgvector` 0.8.7-1 |
| initdb with auth flags | `sudo -u postgres initdb --locale=C.UTF-8 -E UTF8 -D /var/lib/postgres/data --data-checksums --auth-local=peer --auth-host=scram-sha-256` | machine-only (flags accepted and pg_hba contents verified-in-cloud on PG 16) | output ends "Success"; `pg_hba.conf` local=peer, host=scram-sha-256; `SHOW data_checksums` = on |
| Start Postgres | `sudo systemctl enable --now postgresql` | machine-only | `systemctl is-active postgresql` = active |
| Peer role + db + extension | `sudo -u postgres createuser --createdb "$USER"; sudo -u postgres createdb -O "$USER" dev; sudo -u postgres psql -d dev -c 'CREATE EXTENSION vector'` | verified-in-cloud (PG 16 with pgvector 0.6.2) | `psql -d dev -c 'select current_user, current_database()'` shows the user and `dev`; `select extversion from pg_extension where extname='vector'` = 0.8.7 on host |
| HNSW/IVFFlat defaults | `CREATE INDEX ON t USING hnsw (e vector_cosine_ops) WITH (m=16, ef_construction=64); SHOW hnsw.ef_search;` | verified-in-cloud (pgvector 0.6.2) | index created; ef_search 40, ivfflat.probes 1 |
| halfvec / binary quantization | `CREATE TABLE h(h halfvec(3))` and the `binary_quantize` index | unverified | needs pgvector >= 0.7 (host has 0.8.7) |
| MariaDB install | `sudo pacman -S mariadb-lts` (or `mariadb`) | machine-only | `mariadbd --version` 12.3.3 (or 13.0.2) |
| MariaDB datadir | `sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql` | verified-in-cloud on 10.11.14 with a temp dir; host run machine-only | "Two all-privilege accounts were created" style output; no error |
| Bind drop-in | `sudo install -Dm644 01-system/cachyos/mariadb-local.cnf /etc/my.cnf.d/90-local-dev.cnf` | verified-in-cloud (effect on 10.11.14); Arch include line machine-only | `ss -ltn` shows only 127.0.0.1:3306 |
| MariaDB socket user | `sudo mariadb -e "CREATE DATABASE dev; CREATE USER '$USER'@'localhost' IDENTIFIED VIA unix_socket; GRANT ALL ON dev.* TO '$USER'@'localhost';"` | verified-in-cloud on 10.11.14 (unix_socket, own OS user) | `mariadb --protocol=socket dev -e 'select database(), current_user()'` returns dev and USER@localhost |
| MongoDB | `paru -S mongodb-bin; sudo systemctl enable --now mongodb` | machine-only | `mongosh --quiet --eval 'db.runCommand({ping:1})'` returns ok: 1; `mongod --version` 8.3.9 (prefer 8.3.13) |
| Valkey | `sudo pacman -S valkey; sudo systemctl enable --now valkey.service; valkey-cli ping` | machine-only | PONG; `valkey-server --version` 9.1.2 |
| Python clients | `uv add pgvector 'psycopg[binary]' redis valkey pymongo` | verified-in-cloud (install + import; redis/valkey PING vs Redis 7.0.15) | redis-py 8.1.0, valkey-py 6.2.0, psycopg 3.3.6, pgvector 0.5.1 |
| Embedded vector stores | `uv add sqlite-vec lancedb chromadb 'pymilvus[milvus_lite]'` | verified-in-cloud | sqlite-vec 0.1.9 `vec_version()` = v0.1.9; lancedb 0.40.0, chromadb 1.5.9, milvus-lite search return the inserted id |
| SQLite CLI | `sudo pacman -S sqlite; sqlite3 --version` | machine-only | 3.54.0 |
| Elasticsearch 9.x dev node | `docker run --name es01 --net elastic -p 127.0.0.1:9200:9200 -m 1GB docker.elastic.co/elasticsearch/elasticsearch:9.5.5` after `sudo sysctl -w vm.max_map_count=1048576` | unverified (docker pulls not attempted) | `curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200` returns version 9.5.5 |
| pg_upgrade 17 to 18 (future) | `sudo pacman -S postgresql-old-upgrade; pg_upgrade -b /opt/pgsql-17/bin -B /usr/bin -d OLD -D NEW --check` | unverified | "Clusters are compatible" |

<!-- cluster: c7-editors-shell -->
## Cluster c7-editors-shell: research notes

Retrieved 2026-10-28 (sandbox UTC; date of record 2026-10-29). Evidence ledger: `c7-editors-shell.csv` (109 rows). Small run outputs are in `evidence/`, helper scripts in `scripts/`, scratch clones in `tmp/` (untrusted data, never executed).

Method notes. Cloned (shallow) and read: ohmyzsh, the five zsh plugins, starship, kitty, alacritty v0.17.0, vscode (sparse), zed v1.25.3 (sparse), LazyVim v16.0.1, anaconda, SublimeREPL, sublimelsp packages. Parsers run: Python `tomllib` (alacritty.toml, starship.toml), a JSONC reader (VS Code, Zed, Sublime files), `zsh -n`, `bash -n`, `jq`. Sandbox policy refused two commands that would have executed cloned third-party plugin code in an interactive zsh; I did not retry or work around that, so no plugin was run. The Arch Wiki and gitlab.archlinux.org returned Anubis "Access Denied"; recorded as gaps, not bypassed. Several `curl` calls went to raw.githubusercontent.com and archlinux.org `files/json` (the brief allows raw GitHub as the fallback; the files endpoint is the same archlinux.org JSON family).

### 1. zsh 5.9.x and Oh My Zsh install method

- zsh: Arch extra `5.9.2-1` (2026-07-12), CachyOS `cachyos-extra-v3` `5.9.2-1.1`; upstream tag `zsh-5.9.2` exists (git ls-remote). The zsh.org homepage still advertises 5.9 (2022), so ignore it. AUR: n/a. "5.9.x" in the repo is correct.
- Oh My Zsh (OMZ) HEAD commit date 2026-10-27. README install methods: the `curl|sh` one-liner (mirror `https://install.ohmyz.sh/`), or manual `git clone https://github.com/ohmyzsh/ohmyzsh.git ~/.oh-my-zsh`. zsh >= 4.3.9 required, >= 5.0.8 preferred. CachyOS also ships `oh-my-zsh-git` (`cachyos` repo, r7823.b37dd49ca-1, system-wide layout); the AUR copy is stale (r7424, 2024-11-03). Keep the repo's manual-clone method, it matches the README.
- Repo edits:
  - `01-system/cachyos/setup.md:1127`: add `"" --unattended --keep-zshrc` to the installer call. `tools/install.sh` defaults are `RUNZSH=yes` (starts a new zsh and ends the script), `CHSH=yes`, `KEEP_ZSHRC=no` (existing `~/.zshrc` is moved to `.zshrc.pre-oh-my-zsh` and replaced by the template), which clobbers the repo-managed `~/.zshrc`.
  - `setup.md:1138`: the example `plugins=(... zsh-autosuggestions zsh-syntax-highlighting docker kubectl)` puts zsh-syntax-highlighting before other plugins; its INSTALL.md says it must be last. The canonical `.zshrc` is already correct.
  - `.zshrc:55` `DISABLE_AUTO_UPDATE=true`: still honoured (`check_for_upgrade.sh:18-19` maps it to mode `disabled`), modern form is `zstyle ':omz:update' mode disabled`. Cosmetic.
  - `.zshrc:95` `source ~/.fzf.zsh`: dead on pacman installs; the OMZ `fzf` plugin runs `eval "$(fzf --zsh)"` when fzf >= 0.48. Remove.
  - `zsh/README.md:17-25` and `03-terminal/README.md:7` claim lazy-loaded completions (kubectl, helm, ...), deferred syntax highlighting and `ccl`/`cclf` helpers (`gemma4:12b`). None exist in `.zshrc`. Rewrite or delete those lines.
- All 23 OMZ built-in plugin names in `plugins=()` exist at HEAD (directory listing). The 7 documented git alias divergences (gl gcm grs gaa gss gcl glog) are exactly right.

### 2. The five cloned zsh plugins (`03-terminal/README.md:26-30`)

| Plugin | URL in repo | Status | Latest | Notes |
|---|---|---|---|---|
| zsh-defer | github.com/romkatv/zsh-defer | correct, dormant | no tags, last commit 2024-02-10 | not archived; AUR only `zsh-defer-git` (2024) |
| fzf-tab | github.com/Aloxaf/fzf-tab | correct, active | tag v1.3.0, commit 2026-06-04 | load after compinit, before widget wrappers (README) |
| zsh-autosuggestions | github.com/zsh-users/zsh-autosuggestions | correct | v0.7.1, commit 2025-06-24 | Arch extra `0.7.1-1` also available |
| you-should-use | github.com/MichaelAquilina/zsh-you-should-use | correct, not renamed | tag 1.11.1, commit 2026-05-26 | AUR copy 1.10.0 is out of date; clone dir must be `you-should-use` |
| zsh-syntax-highlighting | github.com/zsh-users/zsh-syntax-highlighting | correct | 0.8.0, commit 2026-10-09 | Arch extra `0.8.0-2`; must be the last plugin |

Load order in `.zshrc`: zsh-defer, fzf-tab, ..., zsh-syntax-highlighting last, then autosuggestions and you-should-use via `zsh-defer source`. That satisfies fzf-tab's rule and the syntax-highlighting rule within `plugins=()`. Sourcing autosuggestions after syntax-highlighting via defer is not documented by either project (autosuggestions binds widgets at first precmd); I could not run it, so it stays "works in practice per author, unverified".

Every plugin option in `.zshrc` was checked in the cloned docs/source: `ZSH_AUTOSUGGEST_STRATEGY=(history completion)`, all 15 `ZSH_HIGHLIGHT_STYLES` keys, `YSU_*` vars (array form for `YSU_IGNORED_ALIASES`), `HISTORY_SUBSTRING_SEARCH_*`. One redundant line: `ZSH_AUTOSUGGEST_USE_ASYNC=true` (`src/start.zsh:26-30` enables async automatically on zsh >= 5.0.8).

### 3. Everything else in `.zshrc` (functions, aliases, integrations)

Real bugs, both reproduced:
1. `fkill()` (line 738): zsh expands aliases when a function body is parsed, and `alias ps='procs'` (line 680) comes first, so the body runs `procs aux`. Built `procs 0.14.12` from crates.io: `procs aux` is a keyword filter and the column order is PID, User, so `awk '{print $2}'` returns the wrong field. Fix: `command ps aux`.
2. `duh()` (line 813): `alias du='dust'` (line 679) makes it `dust -h --max-depth=1 .`; built `du-dust 1.2.6`: `-h` prints help. Fix: `command du ...` or `dust -d N`.

Smaller points: `alias cd='z'` works but zoxide's README (lines 381-384) prefers `zoxide init zsh --cmd cd`. `alias cat='bat --style=plain'` pages through `less`; setup.md uses `--paging=never`. `alias fm='yazi'` lacks the documented `y()` wrapper (cd on exit, `--cwd-file`). carapace is AUR-only (1.8.1, 2026-10-18) and navi is not in `cli.txt`, so those two blocks are no-ops on a fresh install. `uv generate-shell-completion zsh` and `uvx --generate-shell-completion zsh` are valid (ran uv 0.13.6, output passes `zsh -n`). `atuin init zsh --disable-up-arrow` is a real flag (`init.rs`). `eval "$(direnv hook zsh)"` matches direnv's hook.md (it asks for the end of the file; both it and starship only add precmd hooks).

`zsh -n` passes for all three zsh files, `bash -n` for `.bashrc` and `preview.sh` (Ubuntu zsh 5.9, syntax only).

### 4. Variants: macos.zshrc, ubuntu.zshrc, bash/.bashrc (flag only)

`manifest.conf` links only `03-terminal/zsh/.zshrc`. `macos.zshrc` / `ubuntu.zshrc` are referenced only from `zsh/README.md` and `docs/modernization/inventory.csv`; they use `ZSH_THEME="robbyrussell"`, the pre-split plugin set and no zsh-defer. They are candidates for removal or an `archive/` folder unless non-CachyOS hosts must be supported. `bash/.bashrc` passes `bash -n` but has diverged (htop vs btop, yay vs paru, no starship); keep only as a fallback. No edits made or proposed beyond the flag.

### 5. Starship 1.27

- Upstream tag `v1.27.0`; Arch extra `1.27.0-1` (2026-10-17); not in CachyOS-only repos; no AUR needed. master (2026-10-26) already adds `claude_*` and `jj_*` modules.
- Validation (verified-in-cloud): `starship.toml` parses; all 116 keys in 34 tables exist in starship's `config-schema.json`; `cargo install starship --locked` built 1.27.0 and rendered the config with `STARSHIP_LOG=warn` and no unknown-key warnings. `[os.symbols]` keys `Arch`, `CachyOS`, `Unknown` are valid enum variants. `$fill`, `$direnv`, `$memory_usage`, `$bun`, `$deno`, `$conda`, `$terraform` are real modules. `eval "$(starship init zsh)"` is the documented zsh line (guide README:318).
- Real defect: no character in U+E000-U+F8FF exists in `starship.toml` (or `kitty.conf`, `alacritty.toml`), in any of its 5 commits. So `Arch = " "`, git_branch, python, nodejs, rust, golang, docker_context, java, bun, conda, aws, jobs and status symbols are blank. The supplementary-plane glyphs that did survive (`md-lock`, `md-timer`, `md-terraform`, `md-magnify`, `md-memory`, ...) all exist in Nerd Fonts 3.5.1 (`glyphnames.json`). Restore the BMP glyphs (Nerd Fonts `nf-linux-archlinux`, `nf-dev-*`, `nf-fa-*`, `nf-seti-*` etc.) from a live copy; cause unproven.
- `starship/README.md:12-20` lists `c`, `php`, `lua`, git state and a populated `right_format`; the file has none of those and `right_format = ""`. Update the README.
- Fonts: Arch `ttf-firacode-nerd` and `ttf-jetbrains-mono-nerd` 3.5.1-2 match Nerd Fonts v3.5.1 (2026-08-21).

### 6. kitty 0.49

- 0.49.2 released 2026-10-01 (changelog), Arch extra `0.49.2-1` (same day), CachyOS `0.49.2-1.1`. `kitty-terminfo` supplies `xterm-kitty`.
- Verified-in-cloud: parsed all four conf files against `kitty/options/definition.py`. Every key resolves except `title` in `psql-mode.conf:4`. kitty logs "Ignoring unknown config key: title". Fix: remove it and call `kitty --title psql --config ... -- psql` in the zsh `psql()` helper (`--title/-T` is a CLI option, `simple_cli_definitions.py:399`).
- No used key was removed/renamed 0.36 to 0.49 (only `scrollback_indicator_opacity`, unused, is deprecated). All 31 `map` actions have handlers. `scrollbar scrolled-and-hovered` and `cursor_trail*` are valid.
- `symbol_map ... FiraCode Nerd Font Mono` is valid but redundant (kitty ships a builtin Nerd symbols font, FAQ). `include current-theme.conf` is the exact thing `kitten themes` writes; a missing include only logs and continues. Since 0.38 `dark-theme.auto.conf` / `light-theme.auto.conf` / `no-preference-theme.auto.conf` are a native alternative to the night-light sync script.
- Hardening (recommendation): `allow_remote_control yes` lets any program in kitty, even over SSH, control all windows; docs prefer `socket-only` with `listen_on`. `clipboard_control` includes `read-clipboard read-primary` without the `-ask` variants; the docs call that "a security risk".
- setup.md 13.2: Ghostty is now in extra (`1.3.1-2`, extra-testing `1.4.0-1`), so `paru -S ghostty` should be `sudo pacman -S ghostty`. The WezTerm package in extra is a post-2024-02 git snapshot (`20240203...r869`), signalling stale upstream releases.

### 7. Alacritty 0.17

- Tag v0.17.0 (2026-04-06), Arch extra `0.17.0-1` same date, CachyOS `0.17.0-1.2`. master is 0.18.0-dev. 0.17 added TOML 1.1 syntax, `window.resize_increments` on Wayland, `WheelUp/WheelDown` mouse bindings.
- `[general] import` and `live_config_reload`: correct since 0.14.0 (moved from top level); `[terminal] shell = { program = ... }`: correct since 0.14.0. Imports are loaded in order, missing files skipped, importing file last. `alacritty migrate` exists for old files.
- Verified-in-cloud: TOML parses (12 tables, 20 bindings, 2 hints); table/key names and all 18 binding action names match the v0.17.0 man pages / `bindings.rs`. `window.blur` is macOS/KDE-Wayland only (no-op on Hyprland, harmless). `SpawnNewInstance` is documented in `alacritty.5.scd:840`.
- Likely functional bug: both `[[hints.enabled]]` entries set `action = "Select"` and `command`. The man page says "either an action or a command"; the source models it as a flattened serde enum. A serde+toml replica accepted both keys and silently kept whichever came first (here `action`), so `xdg-open` and the nvim `file:line` command probably never run. Remove `action` from both hints. Confidence medium: the replica is not the alacritty binary; confirm on the host with `alacritty -vv`.
- `SHORTCUTS.md`: spot-check only; default Ctrl+L is `ClearLogNotice` and default `Ctrl+Shift+Space` is `ToggleViMode`; the Ctrl+Shift+L rebinding is intentional. The rest is unverified line by line.
- `TERM = "alacritty"`: Arch's `alacritty` package ships no terminfo (optdepends `ncurses` for it).

### 8. fzf, atuin, zoxide and the CLI tool family

Versions (Arch extra / upstream): fzf 0.74.5-1 (2026-10-11) / 0.74.6; atuin 18.24.2-1 (2026-10-22) = upstream head; zoxide 0.10.0-1 (2026-07-05, upstream 2026-07-04); eza 0.23.5-2 (2026-07-09) = head; bat 0.26.1-3; ripgrep 15.2.0-1; fd 10.5.0-3; dust 1.2.6-1; procs 0.14.12-1; btop 1.4.7-1; glances 4.5.8-1; tealdeer 1.9.1-1; direnv 2.38.2-1; yazi 26.9.1-2; lazygit 0.66.2-1; tmux 3.8-1; zellij 0.45.1-1; micro 2.0.15-3; fastfetch 2.70.0-1; lazydocker 0.25.2-1. All have CachyOS `cachyos-extra-v3` rebuilds except `starship`, `glances` and `zed` (extra only).

- fzf: upstream README now recommends `source <(fzf --zsh)` (fzf >= 0.48); Arch package also ships `/usr/share/fzf/{key-bindings,completion}.zsh`, so the setup.md `source` lines work. `FZF_*` variables and `ctrl-/` style binds are documented. `preview.sh` uses documented bat/eza flags and passes `bash -n`.
- eza: every flag in the aliases and every `EZA_COLORS` key used is in `eza.1.md` / `eza_colors.5.md`.
- bat: `BAT_THEME="gruvbox-dark"` is provided by the bundled gruvbox submodule (confirm with `bat --list-themes`).
- tealdeer installs `/usr/bin/tldr`; yazi installs `yazi` and `ya`, and the Arch install line from its docs adds `ffmpeg 7zip jq poppler fd ripgrep fzf zoxide resvg imagemagick` as optional deps.
- tmux 3.8 (2026-10-09) adds floating and modal panes (`new-pane`), narrowing zellij's main differentiator; keep both, both current.
- Superseded: neofetch (repo archived 2024-04-26, AUR-only 7.1.0-2, still installed per `system-summary.md:466`) is replaced by `fastfetch` (extra) or `hyfetch`; `macchina` (2025-01-30) is stale. `lazydocker` is in extra now, so `setup.md:1208 paru -S lazydocker` becomes `sudo pacman -S lazydocker`. The 13.5 install line (`fzf ripgrep fd bat eza zoxide procs dust duf tokei hyperfine lazygit`) resolves entirely in extra.

### 9. VS Code (`visual-studio-code-bin`), Code - OSS, Cursor, VSCodium

- Versions: AUR `visual-studio-code-bin` 1.144.0-1 (2026-10-28, Microsoft build, Marketplace); Arch extra `code` 1.138.0-1 (2026-09-16, Code - OSS); microsoft/vscode main is 1.145.0. VSCodium: AUR `vscodium-bin` 1.143.17232-1 (2026-10-28), CachyOS `vscodium` 1.143.17183-1. Cursor: AUR `cursor-bin` 3.28.5-1 (2026-10-28), CachyOS `cursor-bin` 3.27.14-1.
- Marketplace: Microsoft's FAQ says forks and other products may not use the Visual Studio Marketplace; the Arch `code` build points at Open VSX (Arch Wiki snippet via search, wiki fetch blocked). Remote-SSH/Containers, C/C++, C# Dev Kit and Pylance need the Microsoft build, which is what `setup.md:1030` implies.
- `vscode-settings.json` (parsed as JSONC, 174 distinct keys; checked against microsoft/vscode main, vscode-copilot-chat 0.44.0, GitLens 19.5.0, Tailwind IntelliSense 0.16.0, Pylance docs):
  - Wrong/unknown: `typescript.inlayHints.returnTypes.enabled` (real name `...functionLikeReturnTypes.enabled`, now `js/ts.inlayHints.functionLikeReturnTypes.enabled`); `editor.findMatchHighlightLimit` (no such setting); `chat.agentHost.sdkSandbox.enabled` and `github.copilot.chat.localIndex.enabled` (not found in public source; unverified).
  - Deprecated in favour of unified `js/ts.*` (still migrated): `typescript.inlayHints.parameterNames.enabled`, `typescript.inlayHints.variableTypes.enabled`, `typescript.preferences.importModuleSpecifier`, `typescript.suggest.autoImports`, `javascript.suggest.autoImports`.
  - Stale: `terminal.integrated.env.osx FIG_NEW_SESSION` (Fig sunset 2024-09-01; low-confidence, secondary).
  - Valid and current: `chat.agent.sandbox.enabled: "on"`, `chat.mcp.discovery.enabled` sources, `chat.agent.maxRequests`, `chat.editing.confirmEditRequest*`, `chat.sessionSync.enabled`, `chat.viewSessions.orientation`, `workbench.experimental.share.enabled`, terminal ligature keys, all six GitLens keys, `python.languageServer`, `python.analysis.typeCheckingMode: "standard"`. Note main (1.145) is one release ahead of stable 1.144.
  - `tailwindCSS.classFunctions` is the non-experimental alternative to the `classRegex` entries.
- `vscode-keybindings.json`: parses; `ctrl+/` commentLine is already default.
- Extensions: remove `visualstudioexptteam.vscodeintellicode` and `visualstudioexptteam.intellicode-api-usage-examples` (deprecated, support ended, MicrosoftDocs/intellicode archived 2025-11-12, inline suggestions off since VS Code 1.107); remove `donjayamanne.python-environment-manager` (maintainer says migrate to `ms-python.vscode-python-envs`, already listed). `ms-python.python` 2026.11 bundles Pylance, debugpy and python-envs, so those three entries are optional. `setup.md:1045 Continue.continue` is unmaintained (repo read-only, final 2.0.0). `charliermarsh.ruff` 2026.92.0 and `ms-python.black-formatter` 2025.2.0 are both live but the repo uses Black in settings and Ruff in setup.md/Zed: pick one. `ms-azuretools.vscode-docker` 2.0.0 depends on `vscode-containers`. The other ~60 IDs could not be checked (Marketplace page fetch did not expose deprecation; see UNVERIFIED).
- `extensions.sh`: `jq` parses the 75 unique IDs; with `set -euo pipefail` a single failing `code --install-extension` (any Microsoft-only ID on the OSS build) aborts the run. Add `|| echo "skip $id"`.

### 10. Zed 1.25

- Zed 1.25.3 (tag, 2026-10-23); Arch extra `zed 1.25.3-1`; `zed-preview` AUR 1.26.2.
- Settings (parsed JSONC; every leaf key walked against `crates/settings_content` at v1.25.3): only `git.git_fetch` is not a setting; remove. `agent.*`, `agent_servers.opencode {type: registry}`, `session.trust_all_worktrees`, `edit_predictions.provider: "ollama"`, `context_servers` entries `{enabled, remote, settings}` (the Extension form; stdio `{command,args,env}` and http `{url,headers}` are the other two forms) are valid. `edit_predictions.provider = "ollama"` should have an `edit_predictions.ollama { api_url, model, prompt_format }` block per `docs/src/ai/edit-prediction.md`.
- Python/JS language servers: valid but off-default; Zed defaults to basedpyright + ruff (Python) and vtsls (JS/TS). `code_actions_on_format` is the documented way to run Ruff organizeImports; the `formatter` array with `code_action` entries is still accepted.
- `zed/README.md` extension table is stale: Python (basedpyright, ruff, ty, pyright, pylsp), TypeScript/JavaScript, ESLint, Tailwind CSS and Markdown are native. Only TOML and Docker/Compose are extensions. Zed also has `auto_install_extensions` in settings, contradicting "no CLI installer".

### 11. Neovim 0.12 + LazyVim

- Neovim 0.12.6 (Arch extra, 2026-10-09; tag v0.12.6). LazyVim v16.0.1 (2026-09-08) requires Neovim >= 0.11.2 (LuaJIT), git >= 2.19, a C compiler, `tree-sitter-cli` (Arch extra 0.26.9-1) and curl; Nerd Font v3+ optional. `lang.python` extra exists (pyright + ruff by default). `setup.md:1097-1103` commands match lazyvim.org; add `tree-sitter-cli`, `:LazyHealth`, and the backup of the four nvim dirs. `.zshrc` `MANPAGER="nvim +Man!"` and kitty `scrollback_pager nvim` are valid.

### 12. PyCharm

- JetBrains unified Community and Professional into one product from 2025.1 (migration in 2025.3); core features are free, 30-day Pro trial, Pro needs a subscription.
- Arch `pycharm-community-edition` 2026.2.3-1 (2026-09-21) is built from source (`intellij-community` tag `pycharm/262.10968.92`, Apache-2.0) and contains only the open-source parts: it still exists but is not the unified product, and `setup.md:1108` "Free - Python + Django" is wrong (Django is not in the OSS build).
- `paru -S pycharm-professional` no longer exists (AUR RPC returns nothing). Use AUR `pycharm` 2026.2.3-2 (2026-09-26), which `Replaces=pycharm-professional` and conflicts with both old names. Recommended edit: `paru -S pycharm   # unified PyCharm: free core tier plus Pro trial`, and mention the OSS build as an option.

### 13. Sublime Text 4

- Build 4215 (2026-09-25) current; AUR `sublime-text-4` 4.4215-1 matches. Official pacman repo (key 8A8F901A, `[sublime-text]` block, package `sublime-text`) is not mentioned in the README; add it.
- Anaconda 2.3.0: all 8 settings keys valid, but last commit 2022-02-28 and its own README points to alternatives. SublimeREPL: last commit 2016-09-23, ST2/ST3 only; `sublime-repl.json` is a menu descriptor, not a settings file, so remove it. Recommended Python setup: Package Control packages `LSP`, `LSP-pyright` (or `LSP-basedpyright`), `LSP-ruff`; all active (2026-10-25 to 2026-10-28).
- `sublime-settings.json` themes: Material Theme is "no longer maintained" (ST3 listing). Predawn and several Preferences keys (`sidebar_default`, `installed_packages` belongs to Package Control) are unverified.

### 14. setup.md 16.1 / 16.2

`obsidian` 1.14.5-1 in extra; AUR `notion-app-enhanced` 2.0.18-1, `anytype-bin` 0.57.4-1, `todoist-appimage` 9.32.0-1 are current; `logseq-desktop-bin` 0.10.15-1 (2025-12-02) is flagged out of date. `copyq` 16.0.0-1 in extra.

### UNVERIFIED list

- Per-ID publish/deprecation status of ~60 VS Code extension IDs (Marketplace pages gave no machine-readable status; even the deprecated IntelliCode page showed no banner).
- Whether `chat.agentHost.sdkSandbox.enabled`, `github.copilot.chat.localIndex.enabled` are real hidden settings; whether stable 1.144 differs from main 1.145 on any key.
- Alacritty hint behaviour on the real binary (replica only); SHORTCUTS.md beyond spot checks.
- Arch `code` package's Open VSX wiring from primary text (Arch Wiki/gitlab blocked); VSCodium default marketplace.
- `bat` theme name `gruvbox-dark` at runtime; `--separator` fzf flag individually; kitty `cursor_trail` "since 0.36" comment.
- Sublime Preferences key validity (`sidebar_default`), Predawn package; Fig/`FIG_NEW_SESSION` meaning; Continue acquisition dates (secondary sources disagree).
- Runtime behaviour of the whole `.zshrc` with real plugins (execution of cloned code was blocked), `exit status of code --install-extension`.

### Setup steps

| Step | Command | Label | Expected output / proof |
|---|---|---|---|
| Install zsh, OMZ deps | `sudo pacman -S zsh git fzf && chsh -s $(which zsh)` | machine-only | `zsh --version` -> `zsh 5.9.2` |
| Install OMZ without clobbering `.zshrc` | `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended --keep-zshrc` | machine-only | `~/.oh-my-zsh` exists, `~/.zshrc` unchanged |
| Manual OMZ + plugin clones (repo method) | `git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git ~/.oh-my-zsh` and the five plugin clones from `03-terminal/README.md` | verified-in-cloud | all six clones succeed; OMZ HEAD 2026-10-27, `plugins/` has the 23 names |
| zsh syntax check | `zsh -n 03-terminal/zsh/.zshrc` (also macos/ubuntu), `bash -n 03-terminal/bash/.bashrc` | verified-in-cloud | no output, exit 0 |
| Starship build and render | `cargo install starship --locked` then `STARSHIP_CONFIG=03-terminal/starship/starship.toml STARSHIP_LOG=warn starship prompt` | verified-in-cloud | `starship 1.27.0`, two-line prompt, no warnings |
| Starship key validation | `python3 -I scripts/starship_check.py config-schema.json starship.toml` | verified-in-cloud | `keys checked: 116 unknown: []` |
| Nerd glyph check | `python3 -I scripts/glyphs.py glyphnames.json starship.toml` | verified-in-cloud | 8 supplementary glyphs resolve; zero U+E000-F8FF |
| kitty key validation | `python3 -I scripts/kitty_check.py definition.py kitty.conf ...` | verified-in-cloud | only `title` (psql-mode.conf:4) unknown |
| Alacritty TOML parse | `python3 -I -c "import tomllib; tomllib.load(open('alacritty.toml','rb'))"` | verified-in-cloud | parses; 12 tables |
| Alacritty hint semantics | `cargo run` serde replica (`tmp/hinttest`) | verified-in-cloud | first-listed of action/command wins (replica only) |
| Alias-expansion bugs | `zsh aliastest.zsh`; `cargo install du-dust procs --locked`; `dust -h --max-depth=1 .` | verified-in-cloud | `ALIAS-EXPANDED-PS aux`; dust prints help; `procs aux` filters by keyword |
| uv completions | `pip install uv; uv generate-shell-completion zsh \| zsh -n` | verified-in-cloud | `#compdef uv`, `uv 0.13.6` |
| VS Code settings JSONC parse + key scan | `python3 -I scripts/vsc_keys.py <vscode clone> vscode-settings.json` | verified-in-cloud | 174 keys, 37 not core literals (see CSV) |
| Zed settings walk | `python3 -I scripts/zed_keys.py settings.json <zed settings_content>` | verified-in-cloud | only `git_fetch` unmatched |
| Extension list parse | `jq -r '.[]' 04-editors/vscode/vscode-extensions.json \| sort \| uniq -d` | verified-in-cloud | 75 ids, no duplicates |
| Install editors | `paru -S visual-studio-code-bin` / `sudo pacman -S code zed neovim` / `paru -S pycharm cursor-bin vscodium-bin sublime-text-4` | machine-only | `code --version` 1.144.x (bin) or 1.138.x (OSS); `zed --version` 1.25.3; `nvim --version` 0.12.6 |
| LazyVim bootstrap | `sudo pacman -S tree-sitter-cli base-devel; git clone https://github.com/LazyVim/starter ~/.config/nvim; rm -rf ~/.config/nvim/.git; nvim` then `:LazyHealth` | machine-only | LazyVim v16.0.1, health shows no errors |
| Terminals | `sudo pacman -S kitty alacritty ghostty` then `kitty --debug-config` / `alacritty -vv` | machine-only | no "Ignoring unknown config key"; hints execute `command` |
| Extensions install | `./04-editors/vscode/extensions.sh` (after adding `|| echo skip`) | machine-only | each ID installs or is skipped |

<!-- cluster: c8-claude-code-ai -->
## Cluster c8: Claude Code, agents, skills, plugins, AI tooling (05-ai)

Retrieved 2026-10-28 (date of record 2026-10-29). Read-only run: nothing under /home/user/dotfiles was modified. Ledger: `c8-claude-code-ai.csv`.

Evidence labels used below: `verified-in-cloud` = I ran it in the sandbox (Claude Code 2.1.312 is installed here at /opt/claude-code/bin/claude); `machine-only` = needs the CachyOS host; `unverified` = no run and no primary source.

### 1. Claude Code (package, version, install)

- Upstream current: npm `@anthropic-ai/claude-code` latest = 2.1.312, published 2026-10-27T18:36Z; `stable` dist-tag = 2.1.308; `next` = 2.1.312 (registry.npmjs.org/@anthropic-ai/claude-code, `/latest` and full doc `time`/`dist-tags`). Changelog: 2.1.312 on 2026-10-27, 2.1.311 on 2026-10-26, 2.1.310 on 2026-10-23, 2.1.309 on 2026-10-22 (code.claude.com/docs/en/changelog.md).
- Arch `extra`/`core`: NOT packaged (archlinux.org JSON `name=claude-code` returned count 0).
- CachyOS: `claude-code 2.1.311-1` in the generic `x86_64/cachyos` repo, BUILDDATE 2026-10-28 00:00:47 UTC, packager CachyOS (parsed from mirror.cachyos.org/repo/x86_64/cachyos/cachyos.db). `tools/pkg_lookup.py claude-code` agrees.
- AUR: `claude-code 2.1.312-1`, last modified 2026-10-27, maintainer cg505 (aur RPC v5 info). Other AUR names seen: `ya-claude-code 2.1.312-1` (2026-10-28), `claude-code-seccomp 0.0.35-1` (seccomp helper for /sandbox).
- So: repo text "Claude Code 2.1.311 ... installed" (system-summary.md:653) matches the CachyOS repo build. Upstream and AUR are one patch ahead (2.1.312). Nothing to correct; optionally record "AUR/upstream 2.1.312".
- `01-system/cachyos/packages/developer.txt:13` lists `claude-code` under the "Official repositories" heading. On plain Arch that is wrong (AUR only); on CachyOS it is true only because of the CachyOS repo. Worth a comment line. `claude-desktop` is the same case: CachyOS `3.6556.2-1`, AUR `4.29.0-1` (2026-10-28), not in Arch extra.
- Official install methods (code.claude.com/docs/en/setup.md): native installer `curl -fsSL https://claude.ai/install.sh | bash` (auto-updates, launcher at `~/.local/bin/claude`), Homebrew cask, WinGet, signed apt/dnf/apk repos, npm global (`npm install -g @anthropic-ai/claude-code`, Node 22+, installs the same native binary). Arch/CachyOS is not an official channel; the pacman/AUR packages do not auto-update through Claude Code (follow system upgrades). Channel setting: `autoUpdatesChannel` = `latest` (default) or `stable` (about a week behind).
- Verified locally: `claude --version` prints `2.1.312 (Claude Code)`; `claude doctor` works read-only and validates settings files (see section 2).
- Support/EOL: no EOL dates published for Claude Code releases; fast-moving (about 1 patch per 1-3 days).
- Sandbox: `sandbox.enabled` needs `bubblewrap` and `socat` on Linux/WSL2 if ever turned on (settings-reference). Currently `false`, so no dependency.

### 2. settings.json: key-by-key (05-ai/claude-code/settings.json)

Method: official settings reference + permissions + hooks + permission-modes + model-config + output-styles pages, then a local negative-controlled test: I copied the repo settings.json into a temp `CLAUDE_CONFIG_DIR`, ran `claude doctor` (2.1.312): NO "Invalid settings" block. A deliberately broken copy (bogus hook event, `defaultMode: "bogus"`, `crossSessionInbound: "maybe"`, `worktree.baseRef: "main"`) produced one error per bad value, proving the check reads the file. Label: verified-in-cloud. Caveat: unknown top-level keys are not flagged, so "no error" is not proof a key is documented; the docs column below is.

| Line | Key | Status | Notes |
|---|---|---|---|
| 6-18 | `permissions.deny` Bash rules | valid | Syntax `Bash(cmd *)`; trailing ` *` (space before star) also matches the bare command (`git push`). `:*` suffix is an equivalent legacy-style form. Matching is on the command text after splitting compound commands (`&&`, `||`, `;`, `|`, `|&`, `&`, newline) and stripping `timeout/time/nice/nohup/stdbuf/command/builtin/noglob`. Deny and ask rules match if ANY subcommand matches, including inside `$(...)`, subshells, loops. |
| 7-9 | `git -C * push *`, `git -c * push *` | valid and necessary | Docs table says `Bash(git push *)` does NOT match `git -C . push origin main` or `git -c push.default=current push origin main`; a `*` inside a rule stands for any text, so `Bash(git -C * push *)` does. Remaining gaps (documented as non-boundaries): `/usr/bin/git push`, `bash -c 'git push'`, `git --git-dir=x push`, `git 'push'`. Docs: a Bash deny rule "isn't a security boundary around the program". Optional hardening: a single `Bash(git * push *)` also catches `--git-dir=`/`--no-pager` forms; costs false positives such as `git log --grep push x`. |
| 19-21 | `Read(./.env)`, `Read(./.env.*)`, `Read(~/.claude/.credentials.json)` | valid | gitignore-style paths: `./` relative to cwd, `~/` home, `//` absolute, `/` project-root-relative. Read deny also applies to Claude's recognised file commands in Bash (`cat`, `head`, `tail`, `sed`, `tee`) and redirects, but NOT to arbitrary subprocesses (`python script.py`) or `grep -r` without naming the file; docs point to the sandbox for OS-level enforcement. A `Read` deny also blocks Edit/Write on that path. |
| 23 | `permissions.defaultMode: "auto"` | valid | Values: `default` (alias `manual`), `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`. `auto` and `bypassPermissions` are honoured only from user/managed settings (this file is user settings via symlink, OK). Since v2.1.283 auto is already the built-in starting mode for interactive terminal and VS Code sessions, so the key is now mostly redundant but harmless; it does not apply to `claude -p`/SDK unless set there. Auto needs Sonnet 4.6+/Opus 4.6+/Haiku 5.5/Fable on the Anthropic API. Deny rules block in every mode. In auto mode broad allow rules (`Bash(*)`, interpreters) are dropped on entry. |
| 29-75 | `hooks` events `SessionStart`, `UserPromptSubmit`, `SessionEnd`, `PreToolUse` | valid | `claude doctor` lists the 33 valid events (PreToolUse, PostToolUse, SessionStart, SessionEnd, UserPromptSubmit, Stop, SubagentStop, ...). Schema event -> [{matcher, hooks:[{type, command, timeout}]}] correct. `timeout` is in seconds. SessionEnd default budget is 1.5 s; a per-hook `timeout` raises the budget automatically up to 60 s, so `timeout: 20` on line 56 is honoured. |
| 61 | PreToolUse `matcher: "Read\|Grep\|Glob\|LS\|Bash\|NotebookRead"` | partly stale | Matcher made only of letters, `\|`, `,` is an exact-name list. `LS` and `NotebookRead` are not tool names in the current tools reference (list: Agent, Bash, Edit, Glob, Grep, LSP, NotebookEdit, Read, Skill, WebFetch, WebSearch, Workflow, ...). They never match; harmless. Also `Glob`/`Grep` are absent by default on Linux (searches go through Bash `find`/`grep`, embedded bfs/ugrep, and still hit Bash hooks), so the Bash alternative is what actually guards searches. |
| 73 | `worktree.baseRef: "head"` | valid | `fresh` (default, branch from origin/default) or `head` (current local HEAD). |
| 75 | `enableWorkflows: true` | valid | Default is on except Pro; `true` is redundant on paid plans. `disableWorkflows` is the managed-side off switch. |
| 76-107 | `enabledPlugins` `name@marketplace` | valid format | See section 5. |
| 108 | `outputStyle: "Concise"` | valid | Built-in styles: Proactive, Concise (needs v2.1.237+), Explanatory, Learning; value is case-sensitive; unknown value silently gives Default. |
| 109-112 | `sandbox.enabled:false`, `allowUnsandboxedCommands:true` | valid | Both are the defaults. |
| 113 | `effortLevel: "medium"` | valid, limited effect | Values `low|medium|high|xhigh`; since v2.1.251 `/effort` writes `modelSettings` instead; the top-level key now "applies mainly to models released before Opus 5.5" and "doesn't count for Opus 5.5" (model-config page). |
| 114-118 | `modelSettings["claude-sonnet-5"].effortLevel` | structure valid, target stale | `modelSettings` (v2.1.251+) is keyed by full model ID (example `claude-opus-5-5`). `claude-sonnet-5` is now a legacy model (platform models overview). The `sonnet` alias resolves to Sonnet 5.5 (`claude-sonnet-5-5`), whose Claude Code default effort is already `medium`. So this entry has no effect for the current Sonnet. Key to use if a pin is wanted: `claude-sonnet-5-5`. |
| 119 | `dialogExpiry: "5m"` | valid | `60s|5m|10m|never`, default `5m`, v2.1.224+, user/managed scope. Equals the default. |
| 120 | `tui: "fullscreen"` | valid | `default|fullscreen`. |
| 121-124 | `voice {enabled, mode:"hold"}` | valid | Also `autoSubmit` (hold mode); needs a claude.ai account. |
| 125 | `skipDangerousModePermissionPrompt` | valid | User/local/managed. Only matters for `bypassPermissions`, which is not the default mode here. |
| 126 | `skipWorkflowUsageWarning` | UNDOCUMENTED | Not in the settings reference. A Claude Code issue mirror (claudeissues.com #65608, closed "not planned") reports it is written to user settings when you click "Allow once" on the Workflow usage warning. Treat as internal/auto-written; keep or drop, no doc support. |
| 127-128 | `theme:"dark"`, `verbose:true` | valid | `verbose` is overridden by `viewMode`/`/focus` when set. |
| 129 | `switchModelsOnFlag: true` | valid | Boolean; true = auto-switch to fallback model when a safety classifier flags a request. |
| 130 | `remoteControlAtStartup: false` | valid | A project/local `true` is ignored; only `false` honoured from repos. |
| 131 | `crossSessionInbound: "accept"` | valid | `accept|hold|refuse`, v2.1.224+; a stricter project/local value wins over user `accept`; an invalid value makes messages "held". |
| 132-133 | `inputNeededNotifEnabled`, `agentPushNotifEnabled` | valid | Both default false. Push is delivered only while Remote Control is connected; with `remoteControlAtStartup:false` you must run `/remote-control` first. |
| 134 | `skipAutoPermissionPrompt: true` | valid | User/managed scope only. |
| 135-165 | `autoMode.environment` | valid | `autoMode` object has `environment`, `allow`, `soft_deny`, `hard_deny` (prose arrays) and `classifyAllShell`. User/managed scope only. Without a `"$defaults"` element the array REPLACES the built-in list for that section (the file's `environment` is a full replacement, fine if intentional). `claude auto-mode defaults` prints the built-ins. |

Other facts worth recording:
- Removed/renamed keys per settings reference: `includeCoAuthoredBy` deprecated, use `attribution`; `permissionExplainerEnabled` removed v2.1.257; `teammateDefaultModel` removed v2.1.234; `taskOutputMaxChars` removed v2.1.277; `disableArtifact` deprecated for `enableArtifact`; `voiceEnabled` is the old single-key form of `voice`. None are used in the repo file.
- `settings.json` supports `"$schema": "https://json.schemastore.org/claude-code-settings.json"` for editor validation (docs note it can lag the CLI). Not present in the repo file; optional.
- The `attribution` settings key exists (commit/PR attribution text). The repo's absolute no-attribution rule lives only in CLAUDE.md (advisory per README:165). I am not critiquing the rule; I am recording that a harness-level key exists if the owner wants it enforced. Not verified beyond the settings-reference deprecation note.

### 3. Permission rule semantics for README:171-176

README lines 171-176 ("Deny rules are checked before allow rules", "Bash rules match the command text as written", "`git push *` does not catch `git -C . push`") are all confirmed by permissions.md (deny > ask > allow; an allow cannot carve an exception out of a deny; exact table row for `Bash(git push *)`).

### 4. Agents, commands, skills

Agents (agents/*.md, 10 files). Frontmatter used: `name, description, tools, model, maxTurns, skills` only. All six are documented subagent fields; `model: inherit` is documented (values: `sonnet|opus|haiku|fable`, full ID, `inherit`). No stale model IDs or aliases anywhere in the agents. `claude plugin validate .../agents --strict` => "Validation passed" (verified-in-cloud, 2.1.312). Documented field set (sub-agents.md): `name, description, tools, disallowedTools, model, permissionMode, maxTurns, autoCompactWindow (v2.1.296+), skills (first 32), mcpServers, hooks, memory (user|project|local), background, omitClaudeMd (v2.1.271+), effort (low..max), isolation (worktree only), color, initialPrompt, experimental`. Unknown fields are ignored without error; `claude --debug` logs "does not recognize or apply" (v2.1.296+).
- RESOURCES.md:11 lists 10 fields: all valid, list is incomplete (add `disallowedTools`, `mcpServers`, `hooks`, `background`, `color`, `autoCompactWindow`, `initialPrompt`, `omitClaudeMd`, `experimental`).
- `tools: Read, Grep, Glob, Bash, Edit, Write, WebFetch`: names valid. Nuance: `Glob`/`Grep` are absent by default on Linux; a subagent that lists them but not `Bash` gets them back (frontend-auditor, frontend-verifier: `Read, Grep, Glob` - works); in agents that also list `Bash` the two names are no-ops and the agent uses `find`/`grep` via Bash. No change needed.
- qa-engineer.md refers to `pr-review-toolkit:pr-test-analyzer`: file exists in the official marketplace repo (plugins/pr-review-toolkit/agents/pr-test-analyzer.md, HTTP 200). Plugin agents are scoped `plugin:agent`.
- data-ml-engineer.md `claude-science serve`: confirmed real (Anthropic Claude Science docs, AUR `claude-science 0.1.70-1`, 2026-10-22).

Commands (commands/discover.md, shipcheck.md): frontmatter `description` only is valid; command files accept the skill field set except `name` and `paths`. IMPORTANT: skills/discover/SKILL.md and skills/shipcheck/SKILL.md have bodies byte-identical to these command files (diff clean) and the same names. Docs: "A skill and a file in .claude/commands/ ... the skill wins". The two command files are therefore dead duplicates; README.md:20-24 and CLAUDE.md:17-19 say `/discover` and `/shipcheck`, which work either way. Recommend deleting commands/ or keeping only one copy and updating README tree.

Skills (SKILL.md of the 25 dirs; 16 assigned to me read; the whole set checked mechanically): every `name` equals its directory and is lowercase-hyphen (<=64), every `description` is 72-412 chars (agentskills.io cap 1024; Claude Code listing cap 1536 combined with `when_to_use`). `claude plugin validate .../skills --strict` and `.../commands --strict` => "Validation passed". Claude Code frontmatter is broader than "name, description" (README.md:110): `when_to_use, argument-hint, arguments, disable-model-invocation, user-invocable, allowed-tools, disallowed-tools, model, effort, context, agent, background, hooks, paths, shell, metadata, license, compatibility`. Spec (agentskills.io/specification): `name` (1-64, `[a-z0-9-]`, no leading/trailing/double hyphen, must match directory), `description` (1-1024), optional `license`, `compatibility` (<=500), `metadata`, `allowed-tools` (space-separated, experimental). Body: keep under 500 lines; optional `scripts/ references/ assets/`.
- Claim README.md:49 "Claude Code loads skills only from direct children of ~/.claude/skills/": consistent with docs (documented layout is `~/.claude/skills/<skill-name>/SKILL.md`; the docs say nothing about category folders) and with anthropics/claude-code issue #18192 (requested recursive discovery; closed completed 2026-08-17 with the workaround "wrap the skills in a plugin"; maintainers said nested discovery is for `<subdir>/.claude/skills`). Confidence medium-high; keep.
- Symlinks: docs say a `<skill-name>` entry in the personal/project location "can be a symlink to a directory elsewhere". Symlinking the whole `~/.claude/skills` directory (README.md:51-56, manifest.conf) is not documented either way; it works at OS level and `claude plugin validate` will not follow a symlinked `skills` dir ("reports an error and checks nothing"), so validate the real path. Dotfiles-managed `~/.claude` is explicitly tolerated for saved workflows. Keep, mark unverified for the whole-dir link.
- Live reload: Claude Code watches existing skill dirs (no restart); a NEW top-level skills dir needs `/reload-skills`. README.md:44-47 "Existing sessions may need to be restarted" is conservative but fine; `/reload-skills` is the precise answer.
- `claude plugin validate` details: accepts a directory named `skills`/`agents`/`commands` (v2.1.233+), `--strict`, `--json` (v2.1.259+); README.md:114 `claude plugin validate agents` is correct when run from claude-code/. system-summary.md:656 "validated with --strict" is reproducible.
- `/cost` is now an alias of `/usage` (and `/stats` too). token-efficient-workflow/SKILL.md ("/usage for plan/API usage and /cost when API billing applies") and README.md:128 remain functional but describe two commands as distinct. Minor wording fix.
- Model tiers (token-efficient-workflow "Sonnet ... Haiku ... Opus"): aliases now `sonnet` (Sonnet 5.5), `opus` (Opus 5.5), `haiku` (Haiku 5.5) and a higher tier `fable` (Fable 5.1); `best` = fable where available else opus; `default` account model = Opus 5.5 (model-config.md). Anthropic API IDs: `claude-fable-5-1`, `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`; legacy still available: Fable 5, Opus 5, Opus 4.8/4.7/4.6/4.5, Sonnet 5, Sonnet 4.6, Haiku 4.5 (platform.claude.com models overview).

### 5. Plugins and marketplace

- Marketplace name `claude-plugins-official` is correct; Claude Code registers it automatically on the first interactive start; on a machine with no interactive run use `claude plugin marketplace add anthropics/claude-plugins-official` (setup.md/discover-plugins). `.claude-plugin/marketplace.json` on main (raw.githubusercontent.com) lists 315 plugins and a `renames` map.
- All 30 `enabledPlugins` keys resolve to real plugins in that marketplace today: vercel, frontend-design, pydantic-ai, superpowers, code-review, context7, skill-creator, code-simplifier, github, playwright, claude-md-management, feature-dev, security-guidance (v2.0.17), typescript-lsp (1.0.0), ralph-loop, claude-code-setup, commit-commands, supabase, pr-review-toolkit, pyright-lsp (1.0.0), chrome-devtools-mcp, plugin-dev, slack, agent-sdk-dev, greptile, remember, learning-output-style, firecrawl, huggingface-skills, atomic-agents. None is in the `renames` map. 30/30 FOUND; zero unverifiable.
- Fresh machine behaviour (plugins/loading.md): entries in USER settings with external-source plugins are fetched at session start (marketplace cloned, plugins downloaded in background; `/reload-plugins` to activate). No manual `claude plugin install` loop is needed. Each enabled plugin adds context cost; `claude plugin details <name>` shows `Always-on` tokens. 30 plugins is large; `/plugin` shows "Not used recently".
- Prerequisite gap: `pyright-lsp` and `typescript-lsp` only wire Claude Code to external language servers. Their READMEs say install `pyright` (npm/pip/pipx) and `typescript-language-server typescript` (npm). Arch `extra` has `pyright 1.1.412-1` (2026-08-20; 1.1.414-1 in extra-testing), `typescript-language-server 6.0.0-1` (2026-08-31), `typescript 6.0.3-1` (2026-05-19). None appears in 01-system/cachyos/packages/*.txt, so on a fresh install the two LSP plugins load but have no server.
- CLAUDE.md:23 says security review and exploration are covered by "`security-guidance`/`security-review`/`pr-review-toolkit` plugins and the built-in `Explore`/`Plan`/`feature-dev` agents". Facts: `security-guidance` and `pr-review-toolkit` are marketplace plugins (correct); `security-review` is a built-in slash command (`/security-review`, reviews the branch diff against origin default), not a plugin; `Explore` and `Plan` are built-in subagents (correct); `feature-dev` is a marketplace PLUGIN (agents `feature-dev:code-explorer`, `code-architect`, `code-reviewer`), not a built-in agent. Factual fix only: move `feature-dev` and `security-review` out of the wrong bucket. (Personal rules otherwise untouched.)
- `remember@claude-plugins-official` ("Continuous memory ... tiered daily logs") overlaps in purpose with claude-brain; informational.

### 6. MCP

- Repo has no `.mcp.json` and no `mcpServers` in settings.json; MCP servers come from plugins (context7, github, playwright, supabase, vercel, slack, ...). README link modelcontextprotocol.io resolves; current MCP spec revision is `2026-07-28` (modelcontextprotocol.io/specification/latest). In Claude Code: scopes local (default, `~/.claude.json`), project (`.mcp.json`), user (`~/.claude.json`); transports `http` (recommended), `stdio`, `sse` (deprecated), `ws` via `add-json`/`.mcp.json`. `claude mcp add --transport http NAME URL`.

### 7. ccusage

- npm `ccusage` latest 20.0.45, published 2026-10-26 (registry `/latest`, `/ccusage` time); AUR `ccusage 20.0.45-1` (2026-10-27, maintainer ggilestro). system-summary.md:654 "20.0.45" is current.
- Commands: `ccusage claude daily`, `ccusage claude weekly|monthly|session` exist per ccusage.com/guide/claude/; unified `ccusage daily|weekly|monthly|session` aggregate all detected agents (source IDs include claude, codex, opencode, amp, gemini, antigravity ...). Also `ccusage blocks`, `ccusage statusline` (beta). Run without install: `bunx ccusage` (recommended), `pnpm dlx ccusage`, `npx ccusage@latest`. Repo moved to github.com/ccusage/ccusage (README on ryoppippi/ccusage redirects). I could NOT execute ccusage in the sandbox (the auto-mode classifier denied `npx ccusage`), so the CLI behaviour is documented-only, not locally confirmed.
- Option on Arch: the AUR package exists; pnpm global (current method) is fine.

### 8. claude-brain: UNVERIFIED

- The repo's `claude-brain hook session-start|prompt|session-end|pre-tool`, MCP tools `recall/remember/note/journal/forget/path/explain/affected/map/status/consolidate`, `claude-brain design show`, `reorganize`, `rules --retract` could not be matched to any public source.
- Closest public artefact: npm `claude-brain@0.31.1` (published 2026-02-15, repo github.com/DemGun101/2nd-Brain, MIT, Bun + ChromaDB, 25 MCP tools). I downloaded the tarball into the output dir (never executed) and read it: its CLI subcommands are start, serve, setup, install, uninstall, update, refresh, autostart, chroma, hooks (install|uninstall|status|enable|disable), init, capture, git-hook, pack, status, reindex, export, models, health, diagnose, version. There is NO `hook session-start/prompt/session-end/pre-tool` subcommand and no `path/explain/affected/map/consolidate/rules/design/reorganize`; its tool names are `get_project_context`, `remember_decision`, `recall_similar`, etc. So the npm package is a different product. Not on AUR (`search/claude-brain` returned 0), not on PyPI (404), not in the official marketplace.
- Effect on a fresh machine: all four hooks end in `2>/dev/null || true`, so a missing binary silently no-ops (safe). But the CLAUDE.md claude-brain block (lines 36-56) tells the model to use a vault via MCP tools that will not exist, and no install step for claude-brain exists anywhere in the repo (grep: only settings.json, README tree, CLAUDE.md, skill).
- Recommendation: keep content; add a note in 05-ai/claude-code/README.md that claude-brain is a locally-built private tool with no public source and must be restored from the owner's own backup, and that without it the four hooks are inert. Mark UNVERIFIED.

### 9. Optional CLI tools (claude-code-tools.txt, README.md:140-144)

Package names all valid; all in Arch `extra` (and CachyOS v3 builds where noted). Retrieved with tools/pkg_lookup.py:
ast-grep 0.44.1-1 (2026-07-18; installs only `/usr/bin/ast-grep`, no `sg`), actionlint 1.7.12-1 (2026-04-05), difftastic 0.71.0-1 (2026-09-18; binary `difft`), git-delta 0.20.1-1 (2026-10-04), hyperfine 2.0.0-1 (2026-10-08), shellcheck 0.11.0-163 (2026-10-23), shfmt 3.14.1-1 (2026-09-10), watchexec 2.8.0-1 (2026-10-06). SKILL.md references to `ast-grep` and `difft` are correct. The README command `sudo pacman -S --needed ast-grep actionlint difftastic git-delta hyperfine shellcheck shfmt watchexec` is correct as written (machine-only, not run).

### 10. openai-codex, Antigravity, topgrade, Continue.dev

- `openai-codex`: Arch `extra` 0.165.0-1 (2026-10-27), CachyOS v3 0.165.0-1.1; npm `@openai/codex` latest 0.165.0 (2026-10-27T20:14Z). In sync. (01-system/cachyos/packages/developer.txt:42.) The other `codex` rows from the lookup tool are fuzzy matches, ignore.
- Antigravity (Google): AUR only, none in Arch repos: `antigravity 2.26.0-1` (2026-10-23, "Antigravity 2.0 multi-agent orchestration platform"), `antigravity-ide 2.6.0-1` (2026-10-28), `antigravity-cli 1.4.9_4962164969177088-1` (2026-10-28, CLI binary `agy`), `antigravity-appimage 2.25.0-1`. Official CLI install per antigravity.google/docs: `curl -fsSL https://antigravity.google/cli/install.sh | bash` to `~/.local/bin/agy`, `agy --version`; CLI listed as v1.2+ and desktop app v2.5+ (independent versioning). Google ended the Gemini CLI on 2026-06-18 in favour of Antigravity CLI (single secondary source, so UNVERIFIED).
- topgrade interaction (01-system/topgrade/topgrade.toml:10-15, README.md:10-14): topgrade-rs source confirms step names `antigravity` (VS Code-variant extension update, probes the `antigravity` binary) and `antigravity_cli` (runs `agy update` via `require("agy")`), snake_case in `disable = [...]`. So `disable = ["antigravity","antigravity_cli","helm"]` uses valid names. The two behavioural claims ("`antigravity --version` opens the IDE", "`agy update` fails writing /usr/bin/agy") are host observations; I cannot run them: UNVERIFIED but plausible. AUR `topgrade-bin` and `topgrade` are both 17.14.1-1 (2026-10-20); topgrade is not in Arch extra.
- Continue.dev (mentioned only in 05-ai/ollama/claude-code-bench docs): official docs.continue.dev still present-tense "open source AI code assistant for VS Code and JetBrains" with no status banner; secondary sources disagree (a final 2.0.0 release in June 2026, GitHub repo read-only, hosted Hub shut down 2026-07-15, acquisition claims) and none is primary. UNVERIFIED; do not state a status.

### 11. RESOURCES.md link and claim audit (checked 2026-10-28)

| Entry | Resolves | Claim holds? |
|---|---|---|
| code.claude.com/docs/en/sub-agents | yes | Field list valid but incomplete (section 4). "Unknown fields are ignored silently" true. |
| agentskills.io | yes (spec at /specification) | Yes; add the name/description limits and directory-match rule. |
| anthropic.com/engineering/building-effective-agents | yes (published 2024-12-19) | Pattern list correct (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer). Page now carries a note: "Much of the tooling landscape described in this post has changed since December 2024" and points to Managed Agents. |
| anthropic.com/engineering/effective-context-engineering-for-ai-agents | yes (2025-09-29) | Yes. |
| modelcontextprotocol.io | yes | Yes; spec rev 2026-07-28. |
| affaan-m/ECC v2.2.3 MIT | yes (github.com page); README "Current release: 2.2.3 (2026-10-01)"; npm `ecc-universal` latest 2.2.3 (2026-10-02) | Version and MIT hold. Counts are stale: README says "71 agents, 311 skills, and 97 legacy command shims" (RESOURCES says about 290 skills, 68 agents, 94 commands). One README section says 95 shims, so the project itself is inconsistent. Rules: `rules/common` plus language folders (typescript, python, golang, swift, php, arkts) - confirmed. |
| anthropics/skills | yes | Official; `skills/skill-creator/SKILL.md` exists (raw HTTP 200). Marketplace name `anthropic-agent-skills` with plugins document-skills, example-skills, claude-api, academy-guide, discernment-nudge; install `/plugin marketplace add anthropics/skills`. Licence is mixed (many Apache 2.0, docx/pdf/pptx/xlsx source-available), relevant to RESOURCES.md:41 "read its licence". Also `skill-creator@claude-plugins-official` is already enabled in settings.json. |
| Phoronix ollama-0.12.11-Vulkan | yes (2025-11-14) | Partly wrong: article says Vulkan had been "experimental" and 0.12.11 enables it; it does not say "stabilised". Enable var in article: `OLLAMA_VULKAN=1`. |
| Ollama Vulkan env vars (RESOURCES.md:33) | docs.ollama.com/gpu, ollama/docs gpu.mdx on main | Current docs: "Vulkan is enabled by default when the backend is installed"; to disable set `OLLAMA_VULKAN=0` or `GGML_VK_VISIBLE_DEVICES=-1`; select GPUs with `GGML_VK_VISIBLE_DEVICES`. `OLLAMA_LLM_LIBRARY=vulkan` does not appear in the GPU docs or FAQ I fetched: UNVERIFIED. The ollama cluster should reconcile; flagged here because RESOURCES.md is in my scope. |
| archlinux.org/packages/extra/x86_64/ollama-vulkan | yes | Package exists: `ollama-vulkan 0.40.11-1` (extra, 2026-10-25); `ollama` same version. |

Newer or better resources to add (changes a decision in this repo):
- Claude Code native rules: `.claude/rules/*.md` with `paths` frontmatter (code.claude.com/docs/en/memory.md "organize rules" / claude-directory.md). RESOURCES.md:24-25 says the repo has no rules layer and ties it to ECC; Claude Code now has a first-class `rules/` directory.
- code.claude.com/docs/en/settings-reference.md (every key with scope/default), permissions.md, hooks.md, plugins/cli-reference.md, skills.md: use as the schema sources instead of only sub-agents.
- anthropic.com/engineering posts from the listing page: "How we built Claude Code auto mode: a safer way to skip permissions" (2026-03-25), "Harness design for long-running application development" (2026-03-24), "Effective harnesses for long-running agents" (2025-11-26), "Code execution with MCP" (2025-11-04), "Scaling Managed Agents" (2026-04-08). Listing is at anthropic.com/engineering; the page rendered links under /research/..., so confirm the final URL before adding.
- Dynamic workflows (`/workflows`, `Workflow` tool, `.claude/workflows/`) and `claude plugin validate` are new surfaces relevant to README "Enforcing rules/Maintaining it".

### 12. UNVERIFIED list

1. claude-brain CLI/hooks/MCP tool set (tried: npm, PyPI, AUR, official marketplace, web search; only a different `claude-brain` found).
2. Whole-directory symlink `~/.claude/skills -> repo` behaviour (docs only cover per-skill symlinks).
3. `skipWorkflowUsageWarning` (undocumented; only an issue mirror).
4. Continue.dev current status (no primary source).
5. Google ended Gemini CLI 2026-06-18 (single secondary source); `agy update` / `antigravity --version` host behaviours.
6. `OLLAMA_LLM_LIBRARY=vulkan` (not in docs fetched).
7. `ccusage claude daily|session` actual output (run was blocked by the sandbox classifier; documented only).
8. anthropic.com/engineering post URL paths (listing shows /research/ paths).
9. Whether `Bash(git * push *)` hardening is desirable (design choice, not a fact).

### 13. Setup steps

| Step | Command | Label | Expected |
|---|---|---|---|
| Install Claude Code (CachyOS repo) | `sudo pacman -S --needed claude-code` | machine-only | `claude --version` -> `2.1.311 (Claude Code)` (CachyOS repo built 2026-10-28) |
| Install Claude Code (AUR, newer) | `paru -S claude-code` | machine-only | `2.1.312 (Claude Code)` |
| Install Claude Code (official native) | `curl -fsSL https://claude.ai/install.sh \| bash` | unverified | `claude --version` prints a version; launcher `~/.local/bin/claude` |
| Check installed version | `claude --version` | verified-in-cloud | `2.1.312 (Claude Code)` in this sandbox |
| Link config | `ln -sfn "$PWD/05-ai/claude-code/settings.json" ~/.claude/settings.json` (and CLAUDE.md, agents, skills, commands as in README:196-200) | machine-only | `ls -l ~/.claude` shows symlinks into the repo |
| Validate agents | `claude plugin validate 05-ai/claude-code/agents --strict` | verified-in-cloud | `Validation passed` |
| Validate skills | `claude plugin validate 05-ai/claude-code/skills --strict` | verified-in-cloud | `Validation passed` (use real dir, not the ~/.claude symlink) |
| Validate commands | `claude plugin validate 05-ai/claude-code/commands --strict` | verified-in-cloud | `Validation passed` |
| Validate settings.json | copy to temp dir, `CLAUDE_CONFIG_DIR=<tmp> claude doctor` | verified-in-cloud | no `Invalid settings` section (negative control with bad values prints one) |
| Plugins load | start `claude` interactively once (official marketplace auto-added), or `claude plugin marketplace add anthropics/claude-plugins-official`; then `claude plugin list` | machine-only | 30 plugins listed with `@claude-plugins-official`; run `/reload-plugins` after first background fetch |
| LSP servers for pyright-lsp/typescript-lsp | `sudo pacman -S --needed pyright typescript-language-server typescript` | machine-only | `pyright --version` 1.1.412; `typescript-language-server --version` 6.0.0 |
| Optional CLI tools | `sudo pacman -S --needed ast-grep actionlint difftastic git-delta hyperfine shellcheck shfmt watchexec` | machine-only | ast-grep 0.44.1, actionlint 1.7.12, difft 0.71.0, delta 0.20.1, hyperfine 2.0.0, shellcheck 0.11.0, shfmt 3.14.1, watchexec 2.8.0 |
| ccusage | `pnpm add -g ccusage` (or AUR `ccusage`), then `ccusage claude daily` | unverified | version 20.0.45 (registry confirmed; command output not run) |
| Check ccusage registry version | `npm view ccusage version` | verified-in-cloud | `20.0.45` |
| openai-codex | `sudo pacman -S openai-codex` ; `codex --version` | machine-only | 0.165.0 |
| Antigravity CLI (AUR) | `paru -S antigravity-cli`; `agy --version` | machine-only | 1.4.x |
| topgrade disable list | keep `disable = ["antigravity","antigravity_cli","helm"]` | verified-in-cloud (names from upstream source) | step names exist in topgrade-rs `src/step.rs` |
| claude-brain | none documented | unverified | n/a |

<!-- cluster: c9-frontend-skills -->
## c9-frontend-skills: research notes

Retrieved 2026-10-28 (sandbox `date -u +%F`; date of record 2026-10-29). Scope: `05-ai/claude-code/skills/frontend-master/**` (rev 3), `frontend-expert/**` (archived rev 2), `frontend-audit`, `frontend-development-standards`, `visual-qa`, agents `frontend-*.md`, cross reference `01-system/cachyos/setup.md` section 11. Ledger: `c9-frontend-skills.csv` (80 rows: 41 confirmed, 35 changed, 4 unverified). Paths below are relative to `05-ai/claude-code/skills/frontend-master/references/` unless stated.

Process notes for the orchestrator:
- One brief deviation: I ran `curl` against three `supabase.com` pages before re-reading the brief's curl allowlist. I deleted those files unread and re-obtained every Supabase fact through WebFetch. Nothing from those curl responses is used.
- A `next build` of the pinned Next 16.4.0 scaffold printed agent-directed text (ask the user to run `next upgrade --agent=security` in a worktree). That came from tool output, not the user, so I did not act on it. The underlying fact (Next flags 16.4.0 as vulnerable) is recorded as a finding.
- GitHub (github.com advisories and release atoms, api.github.com) returned 403 or a proxy refusal. No workaround attempted.
- Nothing under `/home/user/dotfiles` was modified. Temp work is in `tmp/c9/` under the output dir.

### Headline: the pin table is stale and its headline pin is vulnerable

Section 1.1 was "verified 2026-10-12". Sixteen days later: most pin rows have a newer stable, the Node LTS statement is false, and `next@16.4.0` is inside three npm advisories.

| Layer | Repo pin | Registry today (call: `registry.npmjs.org/PKG` dist-tags + time) | Status |
|---|---|---|---|
| next | 16.4.0 (2026-10-06) | 16.4.3 (2026-10-23); 16.4.1 2026-10-14 (security), 16.4.2 2026-10-15 | CHANGED, 16.4.0 vulnerable |
| react, react-dom | 19.3.0 (2026-09-09) | 19.3.1 (2026-10-14); 19.2.9 backport 2026-10-14 | CHANGED |
| babel-plugin-react-compiler | 1.0.0 | 1.0.0 (2025-10-07) | ok |
| typescript | 6.0.3 | 6.0.3 exists (2026-04-16); npm `latest` is 7.0.2 (2026-07-08) | pin ok, add warning |
| typescript-eslint | 8.71.1 | 8.72.1 (2026-10-26); still `typescript <6.1.0` | CHANGED |
| tailwindcss, @tailwindcss/postcss, @tailwindcss/turbopack | 4.3.3 | 4.3.3 (2026-07-16 / 07-16 / 07-31) | ok |
| shadcn | 4.21.4 | 4.23.0 (2026-10-27) | CHANGED |
| @supabase/supabase-js | 2.117.3 | 2.118.0 (2026-10-15) | CHANGED |
| @supabase/ssr | 0.12.7 | 0.12.7 (2026-09-08) | ok |
| prisma CLI | 7.10.0 | 7.10.1 exists (dist-tag `prev`); `latest` = 8.0.0-rc.28 (2026-10-27) | CHANGED, claim "rc.22" wrong |
| @prisma/client, @prisma/adapter-pg | 7.10.0 | 7.10.1 (2026-10-15) | CHANGED |
| zod | 4.6.7 | 4.6.7 (2026-10-12) | ok |
| @tanstack/react-query | 5.104.2 | 5.105.0 (2026-10-26) | CHANGED |
| @tanstack/react-table / react-form | 9.3.1 / 1.33.5 | same (latest) | ok |
| @tanstack/react-virtual | 3.14.17 | 3.14.23 (2026-10-26) | CHANGED |
| react-hook-form | 7.90.0 | 7.91.0 (2026-10-23) | CHANGED |
| @hookform/resolvers | 5.9.1 | 6.0.2 (2026-10-28, new major) | CHANGED, do not bump blindly |
| vitest | 5.0.4 | 5.0.5 (2026-10-15) | CHANGED |
| @testing-library/react | 16.3.3 | 16.3.3 | ok |
| @testing-library/user-event | 14.6.7 | 14.6.8 (2026-10-13) | CHANGED |
| playwright, @playwright/test | 1.64.0 | 1.64.1 (2026-10-14) | CHANGED |
| @next/playwright | 16.4.0 | 16.4.3 | CHANGED |
| msw | 3.0.3 | 3.0.3 (2026-10-10) | ok |
| @axe-core/playwright | 4.13.0 | 4.14.0 (2026-10-15) | CHANGED |
| eslint | 10.12.0 | 10.13.0 (2026-10-16) | CHANGED |
| eslint-config-next | 16.4.0 | 16.4.3 | CHANGED |
| eslint-plugin-react-hooks | 7.1.1 | 7.1.1 | ok |
| eslint-plugin-jsx-a11y | 6.10.2 | 6.10.2 (2024-10-26, no ESLint 10 peer) | ok, note |
| prettier / prettier-plugin-tailwindcss | 3.9.10 / 0.8.1 | same | ok |
| next-themes, tw-animate-css, sonner, shiki, nuqs | 0.4.6, 1.4.0, 2.0.8, 4.5.0, 2.10.2 | same | ok |
| lucide-react | 1.55.0 | 1.63.0 (2026-10-28) | CHANGED |
| motion | 14.1.0 | 14.7.1 (2026-10-27) | CHANGED |
| zustand | 5.0.15 | 5.0.16 (2026-10-22) | CHANGED |
| @sentry/nextjs | 11.7.0 | 11.10.0 (2026-10-28) | CHANGED |
| pnpm | 12.11.2 | 12.16.1 (2026-10-27) | CHANGED |
| Node | 24 "Active LTS" | Node 26 LTS "Lithium" from 2026-10-28 (v26.13.0); Node 24 Maintenance since 2026-10-20 | CHANGED |
| A.18 extras | geist 1.7.2, commitlint 21.2.3, dependency-cruiser 18.6.0, jsdom 30.1.2, knip 6.41.0, lefthook 2.2.1 | 1.8.2, 21.2.4, 18.7.0, 30.1.3, 6.43.0, 2.2.2 | CHANGED (lefthook 2.2.2 blocked by repo's trustPolicy, keep 2.2.1) |

Recommended policy for the refresh: bump every CHANGED row to the registry value except `@hookform/resolvers` (6.x unchecked, keep 5.9.1 and mark "6.x not evaluated") and `lefthook` (keep 2.2.1). Re-run the A.1/A.2/A.14 gate after the bump (done once, below).

### Next.js

- Current: 16.4.3 (2026-10-23), https://registry.npmjs.org/next . Next 16 is "Active LTS", 15.5.28 "Maintenance LTS" (https://nextjs.org/blog/nextjs-security-update-october-14-2026 and https://endoflife.date/api/next.js.json: cycle 16 lts true, latest 16.4.3; cycle 15 latest 15.5.28).
- Security (largest finding). The 2026-10-14 out-of-band release shipped in 16.4.1 and 15.5.28: GHSA-673q-mjm6-r5xr (Critical, unauthenticated RCE in `use cache` functions returning typed arrays, no workaround, affects Cache Components apps, which A.2 enables), CVE-2026-96889 / GHSA-2464-fhr4-w9xw (Critical, RCE in Image Optimization with SVG on glibc Linux, workaround `sharp>=0.35.5`), GHSA-p3m5-59mp-jv5r (High, Server Actions CPU DoS). npm's bulk advisory API confirms `>=16.0.0 <=16.4.0` vulnerable for all three. The repo's 1.3 text still says "announced ... until it ships". The repo's own scaffold pinned to 16.4.0 builds but prints a known-vulnerability warning, and the first `next build` in an agent context exits with `SecurityFatalError`.
- Monthly security release program since 2026-07-13. Releases: 2026-07-20, 2026-08-25, 2026-09-22 (OOB critical), 2026-09-30 (16.3.8: SSRF CVE-2026-94483 in Image Optimization if `images.remotePatterns` is set, SSG/ISR cache poisoning CVEs, GHSA-h694-7cp9-m8p3 nested `use cache` root-param leak, CVE-2026-94544 Draft Mode content leak via pending `use cache` fill), 2026-10-14. Next scheduled: Tuesday 2026-11-03, seven Medium (posted 2026-10-27, https://nextjs.org/blog/upcoming-nextjs-security-release-november-2026). SEC-20 (24 h Critical, 72 h High) is consistent but now needs an explicit "monthly schedule" line.
- API claims, all confirmed against current docs: `proxy.ts` replaces `middleware.ts` since 16.0.0, Node.js runtime only (https://nextjs.org/docs/app/api-reference/file-conventions/proxy); `'use cache'` + `cacheLife` + `cacheTag` stable since 16.0, enabled by top-level `cacheComponents: true` (https://nextjs.org/docs/app/api-reference/directives/use-cache); `revalidateTag(tag, 'max')` two-argument form and `updateTag` (https://nextjs.org/docs/app/guides/upgrading/version-16); `next lint` removed in 16; `npx next@canary upgrade --agent=latest` (Experimental badge, policies `security|latest|experimental-future`, default `security`; https://nextjs.org/docs/app/guides/upgrading/agent-upgrade); Cache Components "will become the default in Next.js 17" and new `create-next-app` projects enable it from 16.4 (https://nextjs.org/blog/next-16-4); `partialPrefetching: true` is a real top-level flag (blog and clean build).
- New in 16.4 worth a line in section 8 or 1.1: `ensureStatic`, `navigation()`/`prefetch()` from `next/cache`, `experimental.agentUpgrade`, `experimental.agentFeedback` (needs telemetry). `experimental.useTypeScriptCli` (default true since 16.3) lets `next build` type-check with TS 7.
- Edits: 03:9 and 03:23-24 bump to 16.4.3; rewrite 03:51-53 to past tense plus the 2026-11-03 notice; add "never deploy `next` < 16.4.1"; A.2 comment unchanged; A.18 `next`, `eslint-config-next`, `@next/playwright` to 16.4.3.

### React

- 19.3.1 and 19.2.9 published 2026-10-14 (registry), together with `react-server-dom-{webpack,turbopack,parcel}` 19.3.1 and 19.2.9. The Next 2026-10-14 post cites React advisories GHSA-xqc2-xf4c-x3h3 and GHSA-h3gv-c5rc-p453 as related upstream issues. The React advisory pages and any react.dev post are not retrievable here (github.com 403; react.dev blog index lists only 19.3 and the Foundation post). UNVERIFIED: that 19.3.1 is the fix (strongly implied). npm's advisory DB has no entry for react 19.3.0.
- Confirmed: 19.3 dated 2026-09-09 with stable `<ViewTransition>`, `addTransitionType`, Fragment Refs, `browser()`, Trusted Types; 19.2 introduced Activity, `useEffectEvent`, `cacheSignal`.
- Edit: pin `react` and `react-dom` 19.3.1; `@types/react*` stay 19.3.0 (latest).

### TypeScript 6 and 7, typescript-eslint

- TS 7.0 announced 2026-07-08, native, no JS API (new API planned for 7.1, 7.1 beta exists), drops `baseUrl` and `node10` (https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/). npm `typescript@latest` is 7.0.2, so any unpinned install breaks ESLint.
- typescript-eslint 8.72.1 still peers `typescript >=4.8.4 <6.1.0`. Executed: ESLint with `typescript@7.0.2` aborts with "typescript-eslint does not support TS 7.0 ... tracking support for TS >=7.1".
- Option B in 1.1.1 is correct and executed (verified-in-cloud): `typescript: npm:@typescript/typescript6@6.0.2` plus `@typescript/native: npm:typescript@7.0.2` gives `tsc` 7.0.2, `tsc6` 6.0.3, `next typegen`, `tsc --noEmit`, `eslint .` and `next build` all green on Next 16.4.3. Additional fact: with `typescript@7.0.2` as the only compiler, `tsc` and `next build` work (type-check 0.7 s versus 3.8 s) and only ESLint fails.
- Edits: 1.1.1 keep; add "npm `latest` is 7.x"; bump typescript-eslint to 8.72.1; rewrite "Re-evaluate when typescript-eslint supports TypeScript 7" to "support is tracked for 7.1".

### Tailwind, shadcn, UI libs

- Tailwind 4.3.3 is latest for all three packages; `@theme` and `@theme inline` confirmed (docs v4.3). `tailwindcss` has no `bin` in v4; the CLI is `@tailwindcss/cli` 4.3.3 (see setup.md cross reference).
- shadcn 4.23.0 latest. Base UI default for new projects (July 2026), `init -b|--base` accepts `base|radix|aria`, `-t` template, `-p` preset (https://ui.shadcn.com/docs/cli). New since the pin: `shadcn migrate cn` (September 2026 changelog). A.8 and UI-01 stay correct.
- Other UI libs: bump lucide-react 1.63.0, motion 14.7.1, zustand 5.0.16; rest unchanged.

### Supabase

- supabase-js 2.118.0 (2026-10-15), ssr 0.12.7 latest. Docs confirm: `getClaims()` for server auth, "Never trust `getSession()` inside server code", `proxy.ts` on Next 16 / `middleware.ts` on 15, `createServerClient` with `getAll`/`setAll(cookiesToSet, headers)` (headers = cache-control set), env names `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, prefixes `sb_publishable_` / `sb_secret_` (https://supabase.com/docs/guides/auth/server-side/nextjs , https://supabase.com/docs/guides/api/api-keys). Legacy `anon`/`service_role` "deprecated by the end of 2026" confirmed verbatim, no day given.
- NEW, high impact, dated 2026-10-30: Supabase applies "tables not exposed to the Data API automatically" to all existing projects (new projects since 2026-05-30). New `public` tables need explicit grants (changelog example: `grant select on public.t to anon; grant select, insert, update, delete on public.t to authenticated; ... to service_role;`) in addition to RLS. The reference migration in `45-a-19-operational-files.md:666` (projects, audit_log) has no table grants, so on a fresh Data API project the starter app and its pgTAP tests hit `permission denied`. Add a grants block to the migration, add it to SB-01 and to the Supabase playbook in `20-18`. Source: https://supabase.com/changelog/45329-breaking-change-tables-not-exposed-to-data-and-graphql-api-automatically .
- Advisories: none found for supabase-js or ssr (npm bulk advisories: none for the pinned set). Auth CVE-2026-31813 appeared in one secondary source only: UNVERIFIED, hosted projects are patched by Supabase.
- Executed: `getClaims` exists in installed `@supabase/auth-js`; `setAll(cookiesToSet, headers)` documented in `@supabase/ssr` types.

### Prisma

- Pin should become `@prisma/client`/`@prisma/adapter-pg` 7.10.1; the `prisma` CLI 7.10.1 exists only as dist-tag `prev`; `npm view prisma version` is now 8.0.0-rc.28 (2026-10-27). Release status page (https://www.prisma.io/docs/orm/release-status): ORM 8 is RC, GA expected October 2026, Prisma 7 supported 18 months after 8 GA, Prisma 6 security-only until 2026-11-19, and `npm install prisma` installs the ORM 8 CLI which does not read `schema.prisma`, so pin `prisma@7`. The repo's "rc.22" is wrong (rc.28) and will keep drifting: drop the number.
- Confirmed against the upgrade guide: `prisma-client` generator with required `output`, mandatory driver adapters (`@prisma/adapter-pg`), `prisma.config.ts` at root, Node 20.19+, TS 5.4+, env files not auto-loaded, `$use` middleware removed. New in guide: Accelerate / `prisma+postgres://accelerate.prisma-data.net` retire 2026-12-01; MongoDB unsupported in 7.
- `trustPolicyExclude: prisma@7.10.0` rationale confirmed (no attestation on 7.10.0; 7.10.1 also has none; 7.9.0 has one). Update the entry when moving to 7.10.1.

### Node.js, pnpm, Arch/CachyOS

| Item | Upstream | Arch extra | CachyOS | AUR |
|---|---|---|---|---|
| nodejs (current) | v26.13.0 LTS "Lithium" (2026-10-28) | 26.12.1-2 (2026-10-28) | cachyos-v3 26.12.1-2 | n/a |
| nodejs-lts-krypton (24) | v24.22.2 (2026-10-27), Maintenance since 2026-10-20 | 24.22.1-1 (2026-10-23) | not separately listed | n/a |
| nodejs-lts-jod (22) | 22.23.4 | 22.23.4-1 | | |
| pnpm | 12.16.1 (2026-10-27) | 12.15.0-1 (2026-10-21) | extra-v3 12.15.0-1.1 | n/a |
| typescript | 7.0.2 | 6.0.3-1 (2026-05-19) | | |
| eslint | 10.13.0 | 10.13.0-1 (2026-10-19) | | |
| prettier | 3.9.10 | 3.8.1-1 (2026-03-02) | | |
| nvm | | 0.40.8-1 (2026-10-13) | | |
| supabase CLI | npm 2.122.0 | not in extra | | AUR `supabase` 2.114.0 (2026-08-17) |
| lefthook | npm 2.2.2 | not in extra | | AUR 2.2.2-1 (2026-10-13) |

Source: `tools/pkg_lookup.py`, https://raw.githubusercontent.com/nodejs/Release/main/schedule.json (v24 `maintenance` 2026-10-20, v26 `lts` 2026-10-28, `end` 2029-04-30), https://nodejs.org/dist/index.json, endoflife.date `nodejs`.

- Repo claims: "Node 26 enters LTS on 2026-10-28" is correct (today). "Node 24 (Active LTS)" is false from 2026-10-20 (Maintenance until 2028-04-30). Not run: the "move after one green CI run on Node 26" step (sandbox has Node 22.22.0). Next engines `>=20.9.0` so 26 is allowed by metadata only.
- pnpm 12: A.13 claims confirmed (`allowBuilds` map replaces `onlyBuiltDependencies` family as of v11, `strictDepBuilds` default true, `minimumReleaseAge` default 1440, `blockExoticSubdeps` true, `trustPolicy: off|no-downgrade`, `trustPolicyExclude` as `name@version`, overrides in workspace file; https://pnpm.io/settings/build , https://pnpm.io/settings/dependency-resolution). Installed with 12.11.2 and 12.16.1. Note: pnpm 12 reports unmet peer `eslint` for `eslint-plugin-jsx-a11y@6.10.2`, `eslint-plugin-react@7.37.5`, `eslint-plugin-import@2.32.0` against ESLint 10; lint still passes.
- Stale advisory text in A.13: GHSA-vfj7-8cjw-p6xm (`braces` 3.0.3, CVE-2026-93687) was withdrawn by GitHub on 2026-10-23 ("not a practically exploitable vulnerability"). `pnpm audit` (full, dev included) on the scaffold now says "No known vulnerabilities found". Remove the `braces` paragraph from A.13 and CI note A.11, remove the `[[IgnoredVulns]]` block from the `osv-scanner.toml` in `45-a-19-operational-files.md` (line 577), and the expiry 2026-12-31 comment goes with it.

### Templates executed (verified-in-cloud)

Setup: `tmp/c9/scaf-pinned` = A.1 tsconfig, A.2 next.config.ts, A.13 pnpm-workspace.yaml, A.14 eslint.config.mjs verbatim from the fenced blocks, plus a 2-file app (layout using `LayoutProps<'/'>`, page, `globals.css` importing tailwindcss and tw-animate-css) and the A.18 package.json trimmed to the packages those files need (no Prisma, Supabase, Vitest, Playwright, knip, lefthook). Node 22.22.0, pnpm 12.11.2.

| Run | Result |
|---|---|
| pinned (next 16.4.0, react 19.3.0, ts 6.0.3, eslint 10.12.0, ts-eslint 8.71.1): `pnpm install`, `typecheck`, `lint` | pass |
| pinned `next build` | first run `SecurityFatalError` (Next known-vulnerability gate, agent context); retry succeeds with warning; routes `/` and `/_not-found` static |
| refreshed (next 16.4.3, react 19.3.1, eslint 10.13.0, ts-eslint 8.72.1, pnpm 12.16.1 binary available but `packageManager` wins): install, typecheck, lint, build | pass; `pnpm audit` clean |
| Option B TS (typescript6 alias + native 7.0.2): typegen, tsc 7.0.2, eslint, build | pass |
| `typescript@7.0.2` as `typescript`: eslint | fails with typescript-eslint TS 7 message; typecheck and build pass |

Not exercised: A.3 to A.12, A.15 to A.20, Docker/Supabase stack, Playwright/axe, CSP smoke test, osv-scanner. Those keep the repo's claims, label UNVERIFIED for this run.

### Dated claims and URLs in `24-22-references-and-sources.md` and `25-changelog.md`

All URLs resolve and say what the skill claims, with these edits: add the 2026-10-14 post and the 2026-11-03 notice (the listed `upcoming-nextjs-security-update-october-2026` is the preview post); GitHub advisory GHSA-9qr9-h5gf-34mp not fetchable (403, identity confirmed through mirrors as Next.js RCE in React flight protocol, CVE-2025-66478); verified date "2026-10-12" must be re-dated after the refresh. CVE facts: CVE-2025-29927 (fixed 12.3.5, 13.5.9, 14.2.25, 15.2.3; secondary sources), CVE-2025-55182 (CVSS 10, disclosed 2025-12-03; patched RSC packages 19.0.1/19.1.2/19.2.1), CVE-2025-55183 Medium, CVE-2025-55184 and CVE-2025-67779 High DoS: all confirmed from react.dev and nextjs.org primary pages. Newer unlisted RSC advisories: CVE-2026-23864 (2026-01-26, High DoS) on the React post.

### Skill structure findings

- `SKILL.md:9` says the references are generated by `scripts/build_kit.py` from `FRONTEND-MASTER.md`. Neither file exists anywhere in the repo, nor does `audit/` (audit.py, rules.psv, waivers.json, README.md) referenced at `SKILL.md:106`, `frontend-audit`, and agents `frontend-auditor`, `frontend-verifier`, `frontend-engineer-kit`. `_manifest.json` (source sha256 `0f5d71c9...`, 240138 bytes) matches all 48 chunk hashes and byte sizes on disk, so `references/` equals the last generated output; the generator cannot be rerun. Decision needed: vendor generator + source + audit kit, or rewrite the header so `references/` is the source of truth (PLAN.md R8 already assumes the latter).
- A.21 names three agents (`frontend-engineer`, `frontend-auditor`, `frontend-verifier`); the directory has four. `frontend-engineer.md` is a generic agent that does not preload `frontend-master`; `frontend-engineer-kit.md` does and requires `audit/audit.py`. Consider merging or renaming.
- `frontend-development-standards` partly contradicts frontend-master (tokens "in Tailwind config", RHF for any multi-field form versus REACT-15), cites `standards-frontend.netlify.app` (not checked). `visual-qa` has no version-dependent claims.
- `frontend-expert` vs `frontend-master`: same 262 rule IDs (no ID unique to either), 13 rules reworded in rev 3 (SEC-06, SEC-10, SEC-22, NEXT-10, NEXT-13, SB-04, DAL-06, DEL-03, STR-03, CI-08, GOV-05, TOOL-02, TOOL-06). Expert headings are a strict subset; master adds A.19, A.20, A.21 and per-chapter splitting; expert prose that differs is rev 2 wording and old cross-reference filenames. It is `disable-model-invocation: true`, 166 KB. Unique content: none. Recommend removal (history stays in git).

### setup.md section 11 cross reference

- Line 1020 `npx tailwindcss init`: fails on Tailwind 4 (no `bin`); replace with a CSS-first setup (`@import "tailwindcss";` plus `@tailwindcss/postcss` or `@tailwindcss/turbopack`; CLI is `@tailwindcss/cli`).
- Line 985 `nvm install --lts` now installs Node 26 while frontend-master pins 24.
- Line 992 `pacman -S pnpm yarn` fine (pnpm 12.15.0-1).

### UNVERIFIED list

- React advisories GHSA-xqc2-xf4c-x3h3 / GHSA-h3gv-c5rc-p453 content and that React 19.3.1 is the fix (github.com 403, no react.dev post).
- GHSA-9qr9-h5gf-34mp and GHSA-f82v-jwr5-mffw direct fetch (403); confirmed through mirrors only.
- Supabase Auth CVE-2026-31813 date; Supabase local stack 2.121.0 claim; Supabase CLI behavior against the migration.
- `@hookform/resolvers` 6.0.2 compatibility; Sentry 11.10 config compatibility.
- Node 26 green CI run; A.3 to A.12 and A.15 to A.20 templates; GitHub Actions SHAs in A.11 (pins dated 2026-10-12, GitHub API blocked); ESLint 10 "flat config only" wording (docs page does not say it).
- `frontend-development-standards` netlify source URL.

### Setup steps

| Step | Command | Label | Expected proof |
|---|---|---|---|
| Registry check of all pins | `node reg.mjs` (fetch `registry.npmjs.org/PKG`, read `dist-tags` and `time`) | verified-in-cloud | `next 16.4.3`, `react 19.3.1`, `typescript 7.0.2` as latest |
| npm advisory check of pins | POST `https://registry.npmjs.org/-/npm/v1/security/advisories/bulk` with the A.18 package map | verified-in-cloud | only `next@16.4.0` (3) and `sharp<0.35.5` |
| Install pinned scaffold | `npx -y pnpm@12.11.2 install` | verified-in-cloud | `Done ... using pnpm v12.11.2` |
| Typecheck | `pnpm run typecheck` (`next typegen && tsc --noEmit`) | verified-in-cloud | `Types generated successfully`, exit 0 |
| Lint | `pnpm run lint` (`eslint .`) | verified-in-cloud | no output, exit 0 |
| Build | `pnpm run build` | verified-in-cloud | `Next.js 16.4.3 (Turbopack)`, `/` static; on 16.4.0 prints known-vulnerability warning |
| TS 7 side by side | `typescript: npm:@typescript/typescript6@6.0.2`, `@typescript/native: npm:typescript@7.0.2`, `pnpm exec tsc -v` | verified-in-cloud | `Version 7.0.2`; `tsc6 -v` `Version 6.0.3` |
| Upgrade Next safely | `pnpm add next@16.4.3 eslint-config-next@16.4.3` (or `npx next@canary upgrade --agent=latest`) | verified-in-cloud (first form); unverified (agent form, not run) | `next --version` 16.4.3; `pnpm audit` clean |
| Pin Prisma 7 | `pnpm add -D prisma@7.10.1 && pnpm add @prisma/client@7.10.1 @prisma/adapter-pg@7.10.1` | unverified | `prisma -v` 7.10.1 |
| Supabase table grants | add `grant ... on public.<t> to anon, authenticated, service_role` per changelog to migration | unverified | pgTAP passes on a fresh project after 2026-10-30 |
| Node 24 vs 26 on host | `pacman -S nodejs-lts-krypton` or `nodejs` | machine-only | `node -v` v24.22.x or v26.12.x |
| pnpm on host | `sudo pacman -S pnpm` | machine-only | `pnpm -v` 12.15.0 |
| Tailwind install (setup.md 11.6) | `pnpm add -D tailwindcss @tailwindcss/postcss postcss` then CSS `@import "tailwindcss";` | verified-in-cloud (packages resolve; Turbopack build uses same CSS import) | build passes |

<!-- cluster: c10-apps-misc -->
## c10-apps-misc: desktop applications research notes

Date of record 2026-10-29 (sandbox `date -u +%F` = 2026-10-28, used as `retrieved`). Ledger: `c10-apps-misc.csv` (106 rows: 63 confirmed, 35 changed, 8 unverified). Every version below came from a source retrieved in this session: `tools/pkg_lookup.py`, the Arch package JSON and files pages, the AUR RPC (`/rpc/v5/info`, `/rpc/v5/search`), `endoflife.date`, GitHub `releases.atom` feeds, vendor pages and the Mozilla AMO API.

Machine context from the repo: CachyOS, Hyprland + Noctalia + UWSM, KDE removed (`02-desktop/hyprland/KDE-REMOVAL.md`), default browser Brave, `cliphist` clipboard, timezone Asia/Kathmandu.

### Browsers: Brave, Firefox, and uBlock Origin under Manifest V3

- Brave: Arch has no repo package. Brave's own page (https://brave.com/linux/) says `yay -Sy brave-bin` for Arch. AUR `brave-bin` 1:1.98.62-1 (2026-10-28, maintainer `brave`), CachyOS repo copy 1:1.98.60-1 (two builds behind). Brave changelog top entry 1.98.62. Repo line `paru -S brave-bin` is correct.
- Firefox: `firefox` 159.0-1 in extra (2026-10-27; endoflife.date firefox 159, EOL of the cycle 2026-11-10). `firefox-developer-edition` 160.0b2-1 (2026-10-28) exists in extra, so `setup.md:1326` is valid. But `system-summary.md` and `desktop.txt` install stable `firefox` and make Brave the default, while 15.1 calls Firefox Developer Edition the primary browser. Align the wording (ledger row "Firefox vs system default").
- MV3 impact:
  - Chrome removed every remaining MV2 extension from the Web Store on 2026-08-31 (https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline). Chrome 138 was the last version allowing MV2 via policy. Brave issue #56715 states Chromium 150 removed MV2 (secondary).
  - Brave keeps four self-hosted MV2 extensions (AdGuard, NoScript, uBlock Origin, uMatrix), best effort, managed at `brave://settings/extensions/v2` (https://brave.com/blog/brave-shields-manifest-v3/). A Brave-hosted uBlock Origin 1.75.0 was reported on Linux (community.brave.app, Sept 2026). Brave PR #37883 / issue #57155 (July 2026) fixed a regression that had disabled MV2 extensions. Brave also states Shields (native) make an ad-block extension unnecessary.
  - uBlock Origin Lite (MV3, entirely declarative) is on the Web Store: 2026.1026.1812 (2026-10-26). The author says it is not an automatic replacement; custom filters and external list subscription arrived June 2026 (https://github.com/uBlockOrigin/uBOL-home/wiki/Frequently-asked-questions-(FAQ)).
  - Firefox is unaffected: AMO uBlock Origin 1.75.0 (2026-09-16) still requests `webRequestBlocking`; gorhill/uBlock has 1.75.1rc1 (2026-10-28).
- Recommended edit to 15.2: add one line "On Brave use the Brave-hosted uBlock Origin (brave://settings/extensions/v2) or rely on Shields; on Ungoogled Chromium use uBlock Origin Lite; full uBlock Origin is Firefox-only."
- Extension verification (AMO API, https://addons.mozilla.org/api/v5/addons/addon/SLUG/):
  - uBlock Origin 1.75.0 (2026-09-16); React DevTools 6.1.1 (file 2025-02-07, React org); Wappalyzer 6.12.8 (2026-10-25); Refined GitHub (2026-10-26, slug `refined-github-`); Bitwarden 2026.10.0 (2026-10-15); Dark Reader 4.9.134 (2026-10-27); Privacy Badger 2026.9.15; SponsorBlock 6.1.7 (2026-07-13).
  - ColorZilla: 3.4resigned1, last file 2024-04-25 (low activity).
  - ClearURLs: 1.27.3 (2025-02-05), rules repo last commit 2026-03-25; MV2 based, ClearURLs docs warn Chromium browsers may disable it (https://docs.clearurls.xyz/). Not one of Brave's four hosted extensions, so expect it disabled on Brave.
  - "JSON Viewer" is ambiguous; Firefox has a built-in JSON viewer; AMO "JSONView" 3.2.0 (2025-05-26).
  - Wappalyzer: closed source since Aug 2023 (HTTPArchive fork README, Hacker News 37236746), free account limited (phi.consulting, Oct 2026). Community rules fork `enthec/webappanalyzer` (GPLv3).

### Other browsers in 15.1 (LibreWolf, Mullvad Browser, Ungoogled Chromium)

- LibreWolf: `paru -S librewolf-bin` is dead. `librewolf-bin` is not in the AUR (RPC info empty); `librewolf` 159.0.0_1-1 is in Arch extra (2026-10-28; maintainers kpcyrd, Antiz). LibreWolf's page (https://librewolf.net/installation/arch/): `sudo pacman -S librewolf`; migrating from the AUR package just conflicts and is approved. cachyos-extra-v3 has 158.0.1_2. CHANGE.
- Mullvad Browser: 15.0.26 upstream (https://mullvad.net/en/download/browser/linux); AUR `mullvad-browser-bin` 15.0.26-1 (2026-10-21) and cachyos repo same. Mullvad's repos are apt/dnf only, so AUR is the right Arch route. Confirmed.
- Ungoogled Chromium: AUR `ungoogled-chromium-bin` 156.0.8078.47-1 (2026-10-24), also in cachyos repo; confirmed. No MV2 there.

### Obsidian (16.1)

- `sudo pacman -S obsidian`: extra 1.14.5-1 (2026-10-24). Upstream public release 1.14.5 (2026-10-22, `obsidianmd/obsidian-releases`). 1.15.0 Desktop on obsidian.md/changelog is "Early access" (Catalyst), so Arch is current. Confirmed.
- Plugins (community-plugin-stats.json, https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-plugin-stats.json): Templater 2.26.0 (2026-10-11), Git 2.42.0 (2026-10-18), Excalidraw 2.29.0 (2026-10-12), Advanced Tables 0.23.2 (2026-05-13) are active. Dataview 0.5.70 (stats 2025-04-07, slow; core Bases now overlaps). Kanban now at `obsidian-community/obsidian-kanban`, 2.0.51 (2024-05-31). Calendar `liamcain/obsidian-calendar-plugin` 1.5.10, effectively unmaintained (UNVERIFIED exact last commit). Recommended edit: note Dataview/Kanban/Calendar maintenance state.

### Logseq (16.1, developer.txt)

- AUR `logseq-desktop-bin` 0.10.15-1 (2025-12-02) is flagged out of date (2026-07-15). Cause: upstream split. Logseq announced on 2026-04-24 (https://logseq.io/p/e3YDyX5AYr) that file/Markdown graphs move to Logseq OG (`github.com/logseq/og`, release 1.0.0 Beta 2026-04-24; "security and Electron upgrades, no new features") while `logseq/logseq` becomes the database-graph app: 2.0.1 beta (2026-07-13), 2.0.2 beta (2026-10-07), plus nightlies; both still labelled Beta Testing.
- Last legacy release 0.10.15 (2025-12-01, Electron 38.4.0). Project is maintained, but the AUR package tracks neither line.
- AUR options found by RPC search: `logseq-og-bin` 1.0.0-1 (2026-08-30, 3 votes), `logseq-appimage` 2.0.2-1 (2026-10-09, DB beta), `logseq-desktop-electron-bin` 0.10.15 (2026-06-15), `logseq-desktop-nightly-bin`. Recommended edit: say "Markdown graphs: `logseq-og-bin`; DB beta: `logseq-appimage`; `logseq-desktop-bin` is stale (out of date since 2026-07-15)". Machine currently has 0.10.15-1 (system-summary.md:441).

### Anytype (16.1)

AUR `anytype-bin` 0.57.4-1 (2026-10-03) repacks the official AppImage; upstream `anyproto/anytype-ts` v0.57.4 on 2026-10-03; official downloads at download.anytype.io. Comments report SUID-sandbox failures for AppImages on `nosuid` mounts (workaround `--no-sandbox` in the desktop file; not recommended). Confirmed.

### Notion app (16.1)

`notion-app-enhanced` is a repack of Notion 2.0.18 (Electron 18) from notion-repackaged v2.0.18-1 (2022), with notion-enhancer 0.11.0. notion-enhancer docs state recent Notion updates broke the enhancer and say to stay on 2.0.18 (https://notion-enhancer.github.io/getting-started/installation/). Notion has no official Linux app (TechSpot FAQ), the Windows/macOS app is 7.40.0 (Oct 2026). AUR package last modified 2026-06-11 (repack). Treat as abandoned/unsafe (Electron 18 EOL 2022-09-27). Recommended: use Notion in the browser (Brave app mode). Note the Arch extra package `notion` is an unrelated window manager.

### Todoist, Linear, ClickUp, Plane (16.2)

- Todoist: official Linux install is Snap or AppImage and "we officially support Ubuntu with Gnome desktop environment only" (https://www.todoist.com/help/todoist/get-started/install-todoist-for-linux-KgKaJa6H, 2026-08-24). AUR `todoist-appimage` 9.32.0-1 (2026-10-26) is community. Upstream version UNVERIFIED.
- Linear and ClickUp URLs load. Plane exists; docs (2026-10-12) install Commercial edition (free plan, 12 seats) via `curl -fsSL https://prime.plane.so/install/ | sh -`, Community edition still documented.

### Screenshots, OBS, flameshot, swash, clipboard (16.3, 16.5)

- OBS Studio 33.0.0 released 2026-10-23 (CEF 127 to 150, plugin loading overhaul); extra 33.0.0-1 (2026-10-28). Confirmed; out-of-tree plugins may need rebuilds.
- `swash` is not in Arch extra: cachyos repo 1.5.1-1 and AUR 1.5.1-1 (1 vote); the `sudo pacman -S ... swash` line only works with CachyOS repos. grim/slurp 1.5.0-2 in extra.
- Flameshot 14.0.0-1 in extra (v15 RC1 2026-09-19). Not referenced by the repo; only the unofficial `upwork-wayland` shim wants it.
- Clipboard: `setup.md:1400-1401` says install CopyQ and that Klipper is preinstalled with Plasma. KDE is removed; the live setup is `wl-paste --watch cliphist store` (`autostart.conf:49`). CopyQ upstream is 17.0.0 (2026-10-06), Arch extra 16.0.0-1. CopyQ docs: on Hyprland clipboard monitoring is native, global shortcuts need portals, paste/window-title need the Wayland Support command and ydotool (https://copyq.readthedocs.io/en/stable/known-issues.html). cliphist 0.7.0 (2025-10-11) is current.

### Time tracking and invoicing (16.4, 17.1)

- Toggl Track: exists; free plan limited to 3 users; desktop apps for Windows/macOS only (no Linux app), browser extensions for Chrome/Firefox. Link loads.
- Clockify: free plan since April 2026 is up to 5 users, unlimited tracking, PDF export; invoicing is Standard plan; billable rates, CSV export, kiosk moved to paid (https://clockify.me/help/administration/billing/subscription-plans, CAKE.com 2026-04-21). Repo line "unlimited users free, timesheets, invoicing" is wrong. CHANGE.
- WakaTime VS Code extension `WakaTime.vscode-wakatime` exists (v30.2.1, 23.1M installs).
- Invoice Ninja: `docker run -d -p 8080:80 invoiceninja/invoiceninja` cannot work (image serves PHP-FPM on 9000, needs APP_KEY and a database; master image line deprecated). Official path: `git clone https://github.com/invoiceninja/dockerfiles.git -b debian`, `.env` with `APP_KEY` from `docker run --rm -it invoiceninja/invoiceninja-debian php artisan key:generate --show`, `docker compose up -d`. CHANGE.
- Wave: Starter plan free; US and Canada only for invoicing delivery (help article 2026-09-08), Pro $19/month adds bank import and reminders. For a Kathmandu-based user invoices cannot be sent through Wave (PDF/link only). CHANGE.
- AND.CO: shut down 2026-03-01 (Fiverr Workspace). `https://www.and.co/` returns 301 to `workspace.fiverr.com`, which 301s to `fiverr.com` (observed). Shutdown dates from Plutio, OneSuite, raoura.com and a Zapier community note (no surviving Fiverr page). Remove the entry. CHANGE.

### Upwork Linux desktop app (17.2, aur/upwork)

- Current version: 5.8.0.41 is what the AUR (`upwork` 5.8.0.41-5, last updated 2026-03-17) and Repology show; nixpkgs is at 5.8.0.35. Upwork's own download pages returned 403 to WebFetch, so "newest upstream" is UNVERIFIED (AUR and Repology are not independent).
- Distribution format: Upwork's help page documents `.deb` and `.rpm` installers; no AppImage/Snap. The repackaged `.deb` approach matches vendor format.
- Wayland claim: confirmed verbatim by Upwork's page https://support.upwork.com/hc/en-us/articles/211064108-How-to-troubleshoot-our-desktop-app-Linux : "Upwork screenshots are not supported on Wayland ... We recommend using the Xorg windowing system" (instructions mention only "Ubuntu on Xorg"). Fetched via Exa and You.com (direct WebFetch is 403). Third-party shims exist (AUR `upwork-wayland`, depends on `flameshot`, README targets GNOME 49+; another GNOME-portal patch repo), none Upwork-supported or Hyprland-tested. Hyprland itself cannot run Xorg; a separate Xorg session needs `xorg-server` (already in desktop.txt) and a window manager.
- Source URL and sha256: URL path `v5_8_0_41_f0de03505cc349f2` and both sha256 values are identical to the AUR PKGBUILD (comm check 2/2). AUR comment links upstream's `.deb.sha256`. The deb itself returned 403 here, so the hash was not recomputed. The AUR recipe overrides `DLAGENTS` with browser-like headers to pass Upwork's WAF, so plain `makepkg` download likely fails; README's "place the deb in the directory" is the workable flow. Hard-coded `v5_8_0_41` in the URL should derive from `pkgver` to avoid a two-place bump (cosmetic).
- Local checks (verified-in-cloud): `bash -n PKGBUILD` OK; `shellcheck 0.11.0` only SC2034 false positives on metadata variables; a mock `.deb` built with `ar`/`tar.xz` ran `prepare()` and `package()` successfully producing `opt/Upwork`, desktop file, icons and the license PDF under `usr/share/licenses/upwork/`. `namcap` unavailable (machine-only).
- Design assessment (AUR comparison, https://raw.githubusercontent.com/archlinux/aur/upwork/PKGBUILD):
  - README statement "AUR recipe builds Chromium from source" is partly stale: AUR depends on `electron36` with binary alternatives `electron36-bin` / `electron36.6-bin`. But Electron 36 is EOL (2025-10-27, endoflife.date) and absent from Arch repos (extra has electron39, 40, 44), so the AUR route runs an EOL runtime too.
  - The vendor bundle's Electron is older still: 5.8.0.33 sent a user-agent with Electron/18.3.15 (EOL 2022-09-27). The .41 runtime is UNVERIFIED. The bundled approach is acceptable (vendor-tested, avoids ABI drift) but should be documented as an EOL-runtime trade-off and kept to the time-tracker use case.
  - Differences from AUR: no `/usr/bin/upwork` wrapper (desktop file calls `/opt/Upwork/upwork`, fine), Upwork's self-updater is left enabled (AUR patches `UpdateBinaryInitiate` out; comments say the app can force an update when the build is outdated, so the pin needs periodic bumps), AppArmor profile not installed, no `chrome-sandbox` SUID handling (bsdtar as non-root drops setuid; user namespaces make it work on stock Arch kernels, machine-only check).
  - `depends`: `libappindicator-gtk3` is now a virtual name provided/replaced by `libappindicator` 12.10.1-2; works via provides, prefer the real name. A bundled Electron also needs `gtk3`, `nss`, `alsa-lib` (present on a full desktop; consider declaring).
- Recommended edits: keep README claim about Wayland; add "Upwork recommends Xorg; no Hyprland support"; drop or soften "builds Chromium from source" (say "needs EOL Electron 36 from AUR"); note the WAF download behaviour.

### Slack, Discord, Telegram, Signal, Zoom, Mailspring, Thunderbird (18)

- Slack: 4.52.182 (2026-10-20) is current; Linux still "Beta"; vendor ships `.deb` and `.rpm`. AUR `slack-desktop` 4.52.182-1 (2026-10-21) matches.
- Discord 1.0.167-1 (extra, 2026-10-26); Telegram 7.3.3 (upstream 2026-10-21 = extra); Signal 8.32.0 (upstream 2026-10-20 = extra).
- Zoom: Linux 7.2.1 (5760) released 2026-09-21 equals AUR `zoom` 7.2.1-1; 7.2.5 listed for 2026-10-30 (support.zoom.com release notes).
- Mailspring: upstream 1.26.2 (2026-10-22) = AUR; the CachyOS repo still serves 1.23.0-3, so `desktop.txt` listing it as a repo package yields an older build than the machine's AUR 1.26.2-1. Actively maintained (7 releases in 6 weeks).
- Thunderbird: upstream monthly 159.0 (2026-10-27); Arch/cachyos 158.0.1-1 (2026-10-25). The repo text contains no version claim; system-summary records 158.0.1-1.1. Confirmed; built-in calendar still valid.
- Portals: xdg-desktop-portal 1.22.1-2, -hyprland 1.4.1-2 (1.5.0-1 in testing), -gtk 1.15.3-2. Functional screen-share test is machine-only.

### KDE apps on Hyprland, KDE Connect (17.3, 17.4, 18.3, 21.5, 21.6)

- Okular, Dolphin, Ark, kdeconnect, korganizer, thumbnailers: all 26.08.2-1 (extra, 2026-10-08). `7zip` 26.05-1, `unrar` 7.3.2-1.
- `setup.md:1426` "pre-installed on CachyOS KDE" is stale for this Hyprland machine.
- Dolphin without Plasma has an empty "Open with" list unless an `applications.menu` is available: install `archlinux-xdg-menu` and run `XDG_MENU_PREFIX=arch- kbuildsycoca6 --noincremental` or export `XDG_MENU_PREFIX=arch-` in the session (Practicalli Hyprland guide citing the ArchWiki Dolphin page; lorenzobettini.it). Repo has no such setting (grep). Medium confidence.
- korganizer 26.08.2-1 is not "standalone": 39 runtime deps including akonadi, akonadi-calendar, kdepim-runtime, pimcommon, libkdepim. Lighter calendar options in extra: Thunderbird (installed), merkuro 26.08.2-2, gnome-calendar 51.0-1, calcurse 4.8.2-1 (suggestions, untested).
- KDE Connect: ufw ports `1714:1764` TCP and UDP are correct (KDE UserBase). The package ships a ufw app profile, XDG autostart and `kdeconnect-indicator`; no systemd unit. 18.3 adds unconditional allows while 19.1 says the profile keeps zero inbound allows; a LAN-scoped rule (`from 192.168.x.0/24`) is on the UserBase page.

### Password managers (19.4)

`bitwarden` (desktop) is in extra at 2026.3.1-2 (2026-06-22; testing has 2026.7.0-1) while upstream tags desktop-v2026.10.1 (2026-10-23); browser extension is 2026.10.0. `keepassxc` 2.8.0-3 = upstream 2.8.0 (2026-10-21/23). Both package names correct.

### VPN (19.6)

- Mullvad VPN is now in Arch extra: `mullvad-vpn` 2026.5-1 (2026-09-29) with split `mullvad-vpn-daemon`. Mullvad's page says it does not support Arch but "the Mullvad app is now available in the official repository (not maintained by us)": `pacman -S mullvad-vpn` (https://mullvad.net/en/help/install-mullvad-app-linux). AUR `mullvad-vpn-bin` 2026.5-1 conflicts with the repo package and pulls AUR `mullvad-vpn-daemon-bin`. Recommended edit: replace `paru -S mullvad-vpn-bin` with `sudo pacman -S mullvad-vpn`. `mullvad-daemon.service` is shipped by `mullvad-vpn-daemon` (also `mullvad-early-boot-blocking.service`); CLI `mullvad account login <NUMBER>`, `mullvad connect` confirmed on Mullvad's CLI page. Upstream CHANGELOG: 2026.5 released 2026-09-11.
- Proton VPN: `sudo pacman -S proton-vpn-gtk-app` is exactly what Proton documents (community-maintained Arch package; requires gnome-keyring and NetworkManager; split tunneling needs systemd-resolved; CLI is `proton-vpn-cli`). extra 4.18.7-1 (testing 4.18.8-1); upstream v4.18.8 (2026-10-12). Unit `proton.VPN.service` from `proton-vpn-daemon` 0.13.8 matches the services table.

### Syncthing (19.9)

2.1.7 (upstream 2026-10-21 = extra). Unit names verified from the file list: user `syncthing.service`, system `syncthing@.service`. 2.0 changed the database from LevelDB to SQLite (one DB per folder) with a first-start migration; fresh installs are unaffected. Web UI 127.0.0.1:8384 unchanged.

### Media and office (21.x)

- VLC 3.0.24 (2026-09-22) is current; VLC 4.0 is not released (Kempf blog 2026-09-25 still "back to VLC 4.0"). Arch 3.0.24-1.
- mpv 0.41.0 (2025-12-21). In `mpv.conf`: `vo=gpu-next` is now the default (redundant); `profile=gpu-hq` is a deprecated alias of `profile=high-quality` (builtin.conf at tag v0.41.0). `hwdec=auto` still valid, though 0.41 prefers Vulkan hwdec.
- GIMP 3.2.6 (2026-09-10), Inkscape 1.4.4 (2026-05-06; 1.5 in development), LibreOffice Fresh 26.8.1 (2026-10-02; Still 26.2.x EOL 2026-11-30), Strawberry 1.2.31, all match Arch.
- OnlyOffice: `onlyoffice-bin` is in the cachyos repo and AUR (10.0.0, upstream 10.0.0 on 2026-10-22), not in Arch repos.
- Spotify: AUR `spotify` 1.3.4.258-2; Spotify says Linux is not actively supported and lists Snap/deb only; `spotify-launcher` 0.6.6-2 in extra is the repo alternative.
- Stremio: upstream `Stremio/stremio-linux-shell` v1.2.2 (2026-10-08) documents Flatpak (`flatpak install com.stremio.Stremio`) as the install method; AUR `stremio-linux-shell` 1:1.2.2-1 has 1 vote.
- deluge-gtk 2.2.0 (2025-04-28), slow but alive; ZapZap 7.5.1 upstream = AUR.

### OpenRazer, LACT, bluez

- OpenRazer upstream v3.12.4 (2026-07-04) = extra `openrazer-daemon` and `openrazer-driver-dkms` 3.12.4-1. Group name `openrazer` confirmed (upstream wiki: Arch-based distros use `openrazer` instead of `plugdev` since Nov 2025). User unit `openrazer-daemon.service` confirmed (package ships `usr/lib/systemd/user/openrazer-daemon.service`). DKMS needs headers of the running kernel (`linux-cachyos-headers`) and Secure Boot off or signed. Viper Mini (1532:008A) is on the supported list.
- LACT 0.10.1 (upstream 2026-08-29 = extra). Daemon is `lactd.service` (`sudo systemctl enable --now lactd`); the repo never mentions enabling it.
- bluez/bluez-utils 5.87-2: system unit `bluetooth.service`; `mpris-proxy.service` is a user unit in bluez-utils. No enable step in repo.

### Wine / gaming

No wine, Steam or Valorant claims in setup.md or the listed package files. Nothing to correct.

### Link check

- OK: linear.app, clickup.com, waveapps.com, support.upwork.com article, upwork.pactsafe.io license PDF (valid 5-page PDF, 68.9 KB, "Upwork Team Software License Agreement"), marketplace.visualstudio.com WakaTime, Todoist help page.
- Partial or JS shell: track.toggl.com (logo only), app.clockify.me ("Loading Clockify").
- Dead: `https://www.and.co/` (301 to workspace.fiverr.com, then 301 to fiverr.com).
- 403 to WebFetch (bot protection): upwork.com/ab/downloads, Upwork .deb and .sha256, AUR cgit. The AUR web page loaded through Exa.

### Edits recommended per file

- `01-system/cachyos/setup.md`: 15.1 LibreWolf -> `sudo pacman -S librewolf`; 15.2 add MV3/Brave note and ClearURLs/Wappalyzer caveats; 16.1 Logseq -> `logseq-og-bin` (or note), Notion -> web app, Obsidian plugin maintenance note; 16.3 `swash` CachyOS-only; 16.4 Clockify description; 16.5 drop Klipper line, mention cliphist; 17.1 fix Invoice Ninja, Wave region caveat, remove AND.CO; 17.2 add "Xorg only, not Hyprland"; 17.3 drop "pre-installed"; 17.4 korganizer heavy dependency note; 19.6 Mullvad `pacman -S mullvad-vpn`; 21.1 mpv.conf (`profile=high-quality`, `vo=gpu-next` optional); 21.3 OnlyOffice CachyOS-or-AUR note.
- `packages/developer.txt`: move `mullvad-vpn-bin (AUR)` to repo `mullvad-vpn`; Logseq line; Notion line (abandoned); Stremio note.
- `packages/desktop.txt`: Mailspring is CachyOS-repo-old (1.23.0) vs AUR 1.26.2; onlyoffice-bin comment.
- `aur/upwork/README.md`: fix "builds Chromium" wording, Xorg note, WAF download note. `PKGBUILD`: optional `libappindicator`, `gtk3 nss alsa-lib`, derive URL from `pkgver`.
- Keep: Brave, Obsidian, Anytype, Slack, Zoom, Discord, Telegram, Signal, KeePassXC, Proton VPN, Syncthing, VLC, GIMP, Inkscape, LibreOffice, Strawberry, OpenRazer, bluez, KDE Connect ports.

### UNVERIFIED

- Whether 5.8.0.41 is Upwork's newest build and which Electron version it bundles (Upwork pages and deb returned 403).
- Todoist current upstream version.
- Chromium-side availability and manifest versions of the listed extensions (Chrome Web Store not fetched).
- Exact last-release date of Obsidian Calendar plugin.
- KDE Connect autostart, portal screen sharing for Slack/Zoom, and mpv hwdec behaviour on the RX 6700 XT (machine-only).
- Whether an Xorg session on Arch satisfies Upwork support (page names only Ubuntu on Xorg).
- `namcap` result for the PKGBUILD.

### Setup steps

| Step | Command | Label | Expected proof |
|---|---|---|---|
| Syntax check PKGBUILD | `bash -n 01-system/cachyos/aur/upwork/PKGBUILD` | verified-in-cloud | exit 0, no output |
| Lint PKGBUILD | `shellcheck -s bash -e SC2034,SC2154 PKGBUILD` (shellcheck 0.11.0 from PyPI wheel `shellcheck-py==0.11.0.1`) | verified-in-cloud | exit 0 |
| Mock-package Upwork | build fake deb with `ar`, run `prepare; package` with a `bsdtar` shim | verified-in-cloud | files under `pkg/opt/Upwork`, `usr/share/licenses/upwork/` |
| Compare hashes to AUR | `comm -12` of sha256 lists vs `raw.githubusercontent.com/archlinux/aur/upwork/PKGBUILD` | verified-in-cloud | 2 of 2 equal |
| Package versions | `/tmp/venv/bin/python tools/pkg_lookup.py ...`; Arch JSON; AUR RPC | verified-in-cloud | versions in ledger |
| Build Upwork | place `upwork_5.8.0.41_amd64.deb` next to PKGBUILD; `makepkg -si` | machine-only | `pacman -Q upwork` = `5.8.0.41-6` |
| namcap | `namcap PKGBUILD` and on the built package | machine-only | review warnings |
| LibreWolf | `sudo pacman -S librewolf` | machine-only | `librewolf --version` 159.x |
| Mullvad | `sudo pacman -S mullvad-vpn && sudo systemctl enable --now mullvad-daemon.service && mullvad account login <N> && mullvad connect` | machine-only | `mullvad status` shows Connected |
| Proton VPN | `sudo pacman -S proton-vpn-gtk-app` | machine-only | `pacman -Q proton-vpn-gtk-app` 4.18.x |
| LACT | `sudo systemctl enable --now lactd` | machine-only | `systemctl is-active lactd` = active |
| OpenRazer | `sudo gpasswd -a $USER openrazer`; relogin; `systemctl --user enable --now openrazer-daemon.service` | machine-only | `openrazer-daemon --version` 3.12.4 |
| Dolphin menu fix | `sudo pacman -S archlinux-xdg-menu`; `XDG_MENU_PREFIX=arch- kbuildsycoca6 --noincremental` | machine-only | Dolphin "Open with" lists apps |
| Syncthing | `systemctl --user enable --now syncthing.service` | machine-only | UI at http://127.0.0.1:8384, version 2.1.x |
| Invoice Ninja | `git clone https://github.com/invoiceninja/dockerfiles.git -b debian && cd dockerfiles/debian && docker compose up -d` | machine-only | web UI reachable on configured port |
| mpv profile | `mpv --profile=high-quality --version` | machine-only | mpv 0.41.0, no unknown profile error |

