---
title: Host system summary
topic: system-summary
last_verified: 2026-11-16
status: reference
---

# Current System Summary

<!-- snapshot: 2026-11-16 -->
**Snapshot:** 2026-11-16, Asia/Kathmandu (re-snapshot after the November workstation trim; the previous full audit was 2026-10-28)  
**Host:** CachyOS x86-64, user `kneeraazon`  
**Purpose:** inventory of the primary workstation as it was on the snapshot date. The ordered procedure to reproduce it lives in [`fresh-setup.md`](fresh-setup.md), [`01-system/cachyos/dev-stack.md`](01-system/cachyos/dev-stack.md) and [`docs/modernization/HANDOFF.md`](docs/modernization/HANDOFF.md).

This file records the machine as it was, including enabled services, package versions, and local defaults. It intentionally omits passwords, network addresses, disk UUIDs, serial numbers, and other machine-specific identifiers. Every version below is a dated observation, not a target: the targets are in [`versions.yaml`](versions.yaml), and a fresh setup installs current CachyOS/Arch and AUR packages. Hardware, boot and the dated logs at the end are unchanged from 2026-10-28; the software, defaults, databases, services and package counts were re-checked on 2026-11-16. What was removed or changed since the first snapshot, and why, is in [`01-system/cachyos/workstation-changes.md`](01-system/cachyos/workstation-changes.md).

## At a glance

- **OS/kernel:** CachyOS rolling release, kernel `7.3.4-1-cachyos`.
- **CPU/memory:** AMD Ryzen 5 5600, 6 cores / 12 threads; 32 GiB DDR4 in four 8 GiB DIMMs, configured at 3600 MT/s.
- **GPU:** XFX Radeon RX 6700 XT, Navi 22 / RDNA2, 12 GiB VRAM, `amdgpu`.
- **Storage:** one 512 GB Western Digital NVMe; 4 GiB EFI `/boot`; Btrfs root. About 263 GiB was free at the 2026-11-16 snapshot (55 GiB used of 323 GiB).
- **Desktop:** Hyprland + Noctalia on Wayland, started through UWSM and greetd's Noctalia greeter. SDDM was removed on 2026-11-12.
- **Shell:** Zsh is the account's login shell; Oh My Zsh, Starship, Kitty, and the tracked Zsh/FZF configuration are installed.
- **Development:** Python 3.14 system runtime plus uv-managed interpreters that projects pin; rustup stable; Node 26 default through NVM with 24 installed beside it; pnpm, Yarn, TypeScript, frontend language tools, PostgreSQL with pgvector, and Kubernetes tools.
- **Containers/AI:** rootless Docker works. The local LLM stack (Ollama and the ROCm libraries) was removed on 2026-11-12: no model was ever installed and nothing connected to it.
- **Network protection:** UFW is active (policy as recorded on 2026-10-28: deny incoming, allow outgoing; not re-read on 2026-11-16 because it needs root). Proton VPN and Mullvad were removed.
- **Updates:** the package set was brought up to date by the owner's updates through 2026-11-16 (kernel 7.3.4, Hyprland 0.57.2, Noctalia 5.5.0). Pending updates were not re-checked because `pacman -Qu` needs a fresh sync.

## Hardware, boot, and filesystems

| Component | Detected state |
|---|---|
| Motherboard | Gigabyte B550 GAMING X V2 |
| Firmware | UEFI, American Megatrends, dated 2024-03-22 |
| CPU | AMD Ryzen 5 5600, 6C/12T, boost up to about 4.47 GHz |
| Memory | 4 × 8 GiB DDR4, configured 3600 MT/s |
| GPU | XFX Speedster QICK 319 RX 6700 XT, 12 GiB, `amdgpu` |
| Monitor | MSI MAG 275QF, 2560 × 1440, connected over DisplayPort |
| Network | Realtek RTL8111/8168 gigabit Ethernet, `r8169`, NetworkManager |
| Audio | PipeWire, PipeWire Pulse, WirePlumber; HyperX Cloud III headset |
| Other USB devices | Razer Viper Mini, LUMINOUS C50 camera, Evision RGB keyboard |
| Disk | Western Digital PC SN520, 512 GB NVMe |
| EFI | 4 GiB FAT `/boot` partition |
| Root/data | One Btrfs partition; `/`, `/home`, `/var/log`, and `/var/cache` use subvolumes |
| Compression/mount | Btrfs `compress=zstd:1`, `noatime`, SSD discard enabled |
| Bootloader | Limine 12.10.0; active firmware entry is Limine |
| Limine menu | Exactly `CachyOS → linux-cachyos`; default entry is set to that kernel, with last-entry memory disabled |
| Firmware boot entries | Limine and generic `UEFI OS` fallback entries; no Windows entry was present in the UEFI boot order |
| Kernels | `linux-cachyos` 7.3.4-1 is the only installed CachyOS kernel package; LTS and RT kernels were removed to prevent menu regeneration |
| Snapshots | Snapper root snapshots remain enabled; `limine-snapper-sync.service` is disabled/inactive and snapshots are hidden from Limine |
| Other menu entries | Windows Boot Manager and the Limine EFI fallback entry were removed from `/boot/limine.conf`; EFI fallback files and firmware entries were preserved |
| Limine policy | `/etc/default/limine`: `BOOT_ORDER="linux-cachyos"` (ordering only; it is not documented as hiding entries), `FIND_BOOTLOADERS="no"` (stops discovery of other loaders); `/boot/limine.conf`: default `CachyOS/linux-cachyos`, `remember_last_entry: no`. The single-entry menu comes from removing the other kernel packages and disabling `limine-snapper-sync`. Whether manual `default_entry` edits survive `limine-update` is undocumented upstream: re-run `sudo limine-list` after each kernel update. <!-- UNVERIFIED --> |

Only the primary `linux-cachyos` kernel package remains installed. The running kernel is `7.3.4-1-cachyos`.

### Memory, thermals, and GPU tools

- Active swap is `/dev/zram0`: 31.3 GiB, zstd, priority 100. Usage was only a few MiB while idle. Leave the CachyOS zram setup as-is unless a workload measurement supports changing it.
- `lm_sensors`, `inxi`, `cpu-x`, `glances`, `btop`, `amdgpu_top`, `nvtop`, `radeontop`, and LACT are installed. `mission-center` and `rocm-smi-lib` were removed on 2026-11-12.
- Temperature readings are transient; use `sensors`, `inxi -Fxxxz`, or the GPU monitor tools when diagnosing a live problem.
- CPU power profile was `performance` at inspection.

## Operating system and desktop

- `/etc/os-release`: CachyOS Linux, rolling release.
- Active session: Hyprland `0.57.2` (Lua config), Wayland; Noctalia Shell `5.5.0`.
- Active login manager: `greetd` with `/usr/bin/noctalia-greeter-session`. SDDM was removed; its presets stay in `02-desktop/hyprland/sddm/` as reference.
- Limine exposes only `CachyOS → linux-cachyos`; Snapper snapshots remain available for rollback but are hidden from the boot menu.
- Locale configuration: `en_US.UTF-8`, including `LC_TIME=en_US.UTF-8`. Timezone: `Asia/Kathmandu`; system clock sync is enabled.
- Audio session: PipeWire, PipeWire Pulse, and WirePlumber.
- Display server compatibility: Xwayland is installed for X11 applications.

### Default applications

| Use | Default |
|---|---|
| Web browser / HTTP links | Google Chrome (`google-chrome.desktop`), set 2026-11-14 |
| PDF, XML and RSS files | Google Chrome |
| Plain text/source files (opened from the file manager or a browser) | Sublime Text (`sublime_text.desktop`), set 2026-11-16 |
| `$EDITOR` and `$VISUAL` in the shell | Neovim |
| PNG/JPEG/WebP/GIF images | Swash (`dev.lemmy.swash.desktop`) |
| Mail links | Mailspring |
| Login shell | `/usr/bin/zsh` |

These defaults live in `~/.config/mimeapps.list`, which is tracked as a seed in [`manifest.conf`](manifest.conf). Brave and Zen are installed as additional browsers. Vim and Neovim are installed. The editors are Neovim, Vim, Sublime Text, Zed, GNOME Text Editor (a hard dependency of `cachyos-hypr-noctalia`) and the Antigravity IDE. The desktop applications are Obsidian, Slack, Discord, Signal, Zoom, Mailspring, Spotify, Stremio, VLC, mpv, LibreOffice, Deluge, Upwork, Claude Desktop, Antigravity and ZapZap. Everything removed from the first snapshot is listed in [`workstation-changes.md`](01-system/cachyos/workstation-changes.md).

### Current session environment refresh

The tracked Zsh config, tracked UWSM environment, XDG defaults and systemd user-manager environment all select Google Chrome (`BROWSER=google-chrome-stable`). The running Hyprland session picks up the UWSM change at the next login.

The account is in the `openrazer` supplementary group (`id` includes `953(openrazer)`) and the user unit `openrazer-daemon.service` is active for the connected Razer Viper Mini.

## Shell and language toolchains

### Zsh and terminal

- `/usr/bin/zsh` is the login shell; Oh My Zsh and Starship are configured.
- `~/.zshrc` is syntax-checked and integrates NVM from `/usr/share/nvm`.
- Kitty, FZF, zoxide, Atuin, eza, bat, ripgrep, fd, lazygit, tmux, and other command-line tools are in the package lists.
- `./install.sh status` reports all 39 managed entries in sync, and `zsh -n ~/.zshrc` passes. `~/.zshrc` is a symlink into the repo again: some tool had replaced it with a plain copy whose only difference was an appended `# pnpm` PATH block, which is now in the repo copy.

### Python

- System Python: 3.14.10, managed by pacman.
- uv: 0.13.8; uv-managed CPython versions are fetched as projects pin them. 3.13 must stay: all seven `uv tool` installs run on it.
- User tools (uv tools): Ruff 0.17.5, Pyright, mypy, pre-commit, IPython, HTTPie, and JupyterLab.
- Add frameworks and database drivers to each project with `uv add`; no project framework is installed into the system Python.

### JavaScript and TypeScript

- System Node: 26.13.1. NVM's default is 26 (26.13.1) with 24.22.1 installed beside it, so `.nvmrc` files naming 26 or 24 both resolve. Node 26 became LTS on 2026-10-28 and moved Node 24 to Maintenance on 2026-10-20.
- pnpm 12.20.0; Yarn 1.22.22.
- Global user tools: TypeScript 7, TypeScript language server, ESLint, Prettier, and Tailwind CSS language server. Caveat found on 2026-10-29 and still true on 2026-11-16: TypeScript 7.0.2 ships no JS API and no `tsserver.js` (none exists under the pnpm global store), so `typescript-language-server` fails to start unless `typescript@6` (Arch `typescript`) is installed beside it, and `typescript-eslint` rejects TypeScript 7.
- Create frontend projects with `pnpm create vite`; keep framework versions and project dependencies in the project manifest.

### Rust

- rustup stable is the default: rustc 1.100.0.
- Installed components: cargo, rustfmt, clippy, rust-src, rust-analyzer, and the x86-64 standard library. The `rust-docs` component (917 MB) was removed on 2026-11-12; no Rust project lives on this machine.

### Development, cloud, and data tools

Installed tools include PostgreSQL 18 with pgvector, SQLite, Docker/Compose/Buildx, Kubernetes (`kubectl`, minikube, Helm, k9s) and OpenTofu. Stremio's native Linux client is installed from the official Stremio Linux shell project. Removed since the first snapshot: Google Cloud CLI (2026-10-27), then MariaDB, MongoDB, Valkey, AWS CLI, Azure CLI, Terraform, Pulumi, Ansible, GitLab Runner, `act` and Nginx (2026-11-11 and 2026-11-12). Cloud accounts and credentials are not configured in the dotfiles.

## Databases and local service endpoints

The database directories were initialized from empty state. No production data or database backups are part of this dotfiles checkout.

| Service | State and local configuration |
|---|---|
| PostgreSQL | Enabled/active, v18.7, listens on localhost:5432. Peer-authenticated `kneeraazon` role with `CREATEDB`; databases `dev`, `pgvector_demo` and `postgres`; the `vector` extension is enabled in `dev` and `pgvector_demo`. Host authentication uses SCRAM. The demo is described in [`06-tools/pgvector-demo/`](06-tools/pgvector-demo/README.md). |
| Rootless Docker | User service active/enabled; selected CLI context is `rootless`. The root Docker daemon (`docker.service`, `docker.socket`, `containerd.service`) is disabled. |

MongoDB, MariaDB, Valkey and Ollama were removed on 2026-11-11 and 2026-11-12 (no clients, about 450 MB of RAM held by the first two). MariaDB's data directory `/var/lib/mysql` still exists and holds one database named `dev`; it is the only leftover. The PostgreSQL listener was checked on loopback and is not exposed for LAN use.

## Local AI and graphics stack

- AMDGPU kernel driver and Mesa/RADV Vulkan are installed, with LACT for GPU settings.
- The Ollama, ROCm/HIP, rocBLAS, rocSOLVER and HIPBLAS packages were removed on 2026-11-12. During their life Ollama detected `AMD Radeon RX 6700 XT` (ROCm `gfx1030`, 12.0 GiB VRAM) but no model was ever installed, so inference was never measured. The recipe stays in `05-ai/ollama/` and `01-system/cachyos/packages/ai.txt` for when local inference is wanted again.
- ZRAM was already active and suitable; no zram change was made.

## Security, VPN, and service state

UFW is enabled and active: default incoming deny, outgoing allow, routed traffic disabled, and no inbound allow rules. A remote administration setup needs a reviewed SSH rule before enabling that policy.

| Component | Current state |
|---|---|
| VPN | Proton VPN and Mullvad were removed on 2026-11-11 and 2026-11-12; no VPN client is installed. |
| OpenRazer | Razer Viper Mini connected. User is in `openrazer` group; user unit `openrazer-daemon.service` is enabled and active. |
| AppArmor | `apparmor.d` profiles installed. `linux-cachyos` is built with AppArmor (`CONFIG_SECURITY_APPARMOR=y`) but its default `CONFIG_LSM` is `landlock,lockdown,yama,integrity,bpf`, so `aa-status` reports the module loaded and the filesystem not mounted until the boot command line carries `lsm=landlock,lockdown,yama,integrity,apparmor,bpf`. Not enforcing. See [chapter 19](01-system/cachyos/setup/19-security-privacy.md) for the enablement steps; apparmor.d does not list greetd or Hyprland among supported desktops. |
| Fail2ban, DNSCrypt, Nginx, SDDM | Removed on 2026-11-12 (none was enabled; greetd is the greeter). |
| dnsmasq | Installed, service not enabled. DNS/network-manager configuration was left intact. |
| Syncthing | Installed, service not enabled. |
| Rootful Docker daemon | Disabled on 2026-11-12. Docker operates as the rootless user service; the user is not in the `docker` group. |

Other notable active services include NetworkManager, systemd-resolved, systemd-timesyncd, power-profiles-daemon (performance profile), Avahi, Ananicy-C++, bpftune, and dmemcg-booster (`limine-snapper-sync.service` is intentionally disabled so Snapper snapshots stay out of the single-entry Limine boot menu).

## Dotfiles and package records

- Checkout: `~/dotfiles`, remote `https://github.com/karkinirajan/dotfiles.git`.
- Root README install instructions cover the desktop, system, font, CLI, and focus manifests. `01-system/cachyos/dev-stack.md` documents the optional developer profile; `05-ai/ollama/README.md` documents the AMD-specific Ollama configuration.
- The desktop manifest reflects the active greetd/Noctalia greeter and the installed desktop applications. The system manifest records UFW, power management and snapshot packages.
- The MariaDB loopback configuration `01-system/cachyos/mariadb-local.cnf` is kept as reference only (MariaDB is removed); the reproducible bundled-runtime Upwork package is `01-system/cachyos/aur/upwork/PKGBUILD`.
- At the 2026-11-16 snapshot, pacman listed 1,383 installed packages: 280 explicitly installed and 27 foreign packages not found in enabled sync repositories (1,730, 324 and 30 on 2026-10-28). The complete explicit and foreign package/version snapshots are below.

## Fresh setup order

The ordered, unattended procedure for rebuilding this workstation lives in [`docs/modernization/HANDOFF.md`](docs/modernization/HANDOFF.md) (full-auto order of operations with expected output per step). The explanations behind each step are in the setup chapters, and the interactive checkpoints in [`fresh-setup.md`](fresh-setup.md). Keep package versions rolling; do not copy this machine's IDs, filesystem UUIDs, credentials or private data, and restore personal data and secrets separately from backups.

| Step | Where it is documented |
|---|---|
| 1. Inspect the target, install the CachyOS baseline, refresh mirrors | [`fresh-setup.md`](fresh-setup.md), [chapter 01](01-system/cachyos/setup/01-system-foundation.md) |
| 2. Install the desktop, system, font, CLI and focus package lists | [chapter 22](01-system/cachyos/setup/22-baseline-packages.md), root [`README.md`](README.md#install) |
| 3. Install the developer and application profile (Upwork from the tracked PKGBUILD) | [`dev-stack.md`](01-system/cachyos/dev-stack.md) section 1 |
| 4. Apply the dotfiles (`./install.sh`) and refresh the session environment | root [`README.md`](README.md#install) |
| 5. Initialize local databases (PostgreSQL 18 needs the `initdb` auth flags) | [`dev-stack.md`](01-system/cachyos/dev-stack.md) section 3, [chapter 06](01-system/cachyos/setup/06-databases.md) |
| 6. Enable rootless Docker | [`dev-stack.md`](01-system/cachyos/dev-stack.md) section 4, [chapter 08](01-system/cachyos/setup/08-docker-kubernetes.md) |
| 7. Optional, skipped on this machine since 2026-11-12: enable the AMD Ollama backend (ROCm, Vulkan, LACT) | [`dev-stack.md`](01-system/cachyos/dev-stack.md) section 5, [`05-ai/ollama/README.md`](05-ai/ollama/README.md), [chapter 02](01-system/cachyos/setup/02-amd-gpu-rocm.md) |
| 8. Restore firewall and Razer behavior, verify the host | [`dev-stack.md`](01-system/cachyos/dev-stack.md) sections 3 to 4 and Verify |

## Beyond the base setup

- Start each Python service inside its own uv environment, e.g. `uv init --python 3.12 api && cd api && uv add fastapi 'uvicorn[standard]'`.
- Start each frontend in its own package manifest, e.g. `pnpm create vite`; select React/Vue/Svelte/other dependencies per project.
- Create Rust projects with `cargo new`; retain dependencies in `Cargo.toml`.
- Start minikube only when a local Kubernetes cluster is needed; it is installed but not running in the current profile.
- Install Nginx, Syncthing, DNS filtering, Fail2ban, or AppArmor enforcement only after reviewing the target network, kernel support, and service rules.
- If local inference is wanted again, install the optional `ai.txt` set, download a model only after selecting its size and workload, and confirm VRAM placement with `ollama ps` during inference.
- Keep personal application sign-ins, credentials, SSH keys, project files, databases, and any model data outside this repository and restore them from their own backups.

## Complete explicit package snapshot

The files below are the sorted live `pacman -Qe` output captured on 2026-11-16 (explicitly installed names and versions; dependencies omitted) and the `pacman -Qm` output (packages not present in enabled sync repositories).

Package snapshots (captured 2026-11-16):

- [`01-system/cachyos/host-snapshot/pacman-explicit.txt`](01-system/cachyos/host-snapshot/pacman-explicit.txt): `pacman -Qe`, name and version, sorted.
- [`01-system/cachyos/host-snapshot/pacman-foreign.txt`](01-system/cachyos/host-snapshot/pacman-foreign.txt): `pacman -Qm`, packages not in an enabled sync repository.

## Claude Code update (2026-10-28)

- Claude Code `2.1.311` and Claude Desktop are installed. Its global configuration, agents, and skills are linked from this repository; 25 skills are present including `token-efficient-workflow`. Restart Claude Code to refresh skill discovery, then invoke `/token-efficient-workflow` or let it trigger for relevant work.
- Installed user-level `ccusage` `20.0.45` with pnpm. It reports local Claude Code usage with `ccusage claude daily` and `ccusage claude session`; it does not change usage by itself.
- Added an optional package set for structural search, diffs, shell/workflow validation, benchmarking, and file watching. These eight pacman packages are documented but not installed: `ast-grep`, `actionlint`, `difftastic`, `git-delta`, `hyperfine`, `shellcheck`, `shfmt`, and `watchexec`. The install command is in `05-ai/claude-code/README.md`.
- Claude Code skills validated successfully with `claude plugin validate --strict`. `claude doctor` reports no installation issues.

## Limine menu cleanup (2026-10-27)

- The live menu was reduced to the sole entry `CachyOS → linux-cachyos`; `limine-list` confirmed it.
- Removed packages: `linux-cachyos-lts`, `linux-cachyos-lts-headers`, `linux-rt`, and `linux-rt-headers` (918.04 MiB). The running `linux-cachyos` kernel and its boot files were checked before the change and preserved.
- Removed menu-only paths: `CachyOS/Snapshots`, `Other systems and bootloaders` (including Windows Boot Manager), and `EFI fallback`. Bootable EFI fallback files, Snapper snapshots, and firmware NVRAM entries were left intact.
- Disabled `limine-snapper-sync.service`; Snapper itself remains configured. Set `BOOT_ORDER="linux-cachyos"` and `FIND_BOOTLOADERS="no"` in `/etc/default/limine`; set `default_entry: CachyOS/linux-cachyos` and `remember_last_entry: no` in `/boot/limine.conf`.
- Backups were written beside the active configs before editing. `limine-update` rebuilt the initramfs successfully and the final menu list contained only the intended entry.
