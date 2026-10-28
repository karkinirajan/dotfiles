---
title: Host system summary
topic: system-summary
last_verified: 2026-10-29
status: reference
---

# Current System Summary

<!-- snapshot: 2026-10-28 -->
**Snapshot:** 2026-10-28, Asia/Kathmandu (full repository audit and host reconciliation)  
**Host:** CachyOS x86-64, user `kneeraazon`  
**Purpose:** inventory of the primary workstation as it was on the snapshot date. The ordered procedure to reproduce it lives in [`fresh-setup.md`](fresh-setup.md), [`01-system/cachyos/dev-stack.md`](01-system/cachyos/dev-stack.md) and [`docs/modernization/HANDOFF.md`](docs/modernization/HANDOFF.md).

This file records the machine as it was, including enabled services, package versions, and local defaults. It intentionally omits passwords, network addresses, disk UUIDs, serial numbers, and other machine-specific identifiers. Every version below is a dated observation, not a target: the targets are in [`versions.yaml`](versions.yaml), and a fresh setup installs current CachyOS/Arch and AUR packages. Statements about behavior (why a service is off, which package a unit comes from) were re-checked on 2026-10-29 and corrected where wrong.

## At a glance

- **OS/kernel:** CachyOS rolling release, kernel `7.3.0-4-cachyos`.
- **CPU/memory:** AMD Ryzen 5 5600, 6 cores / 12 threads; 32 GiB DDR4 in four 8 GiB DIMMs, configured at 3600 MT/s.
- **GPU:** XFX Radeon RX 6700 XT, Navi 22 / RDNA2, 12 GiB VRAM, `amdgpu`.
- **Storage:** one 512 GB Western Digital NVMe; 4 GiB EFI `/boot`; Btrfs root. About 418 GiB was free at this snapshot.
- **Desktop:** Hyprland + Noctalia on Wayland, started through UWSM and greetd's Noctalia greeter. SDDM is installed but inactive.
- **Shell:** Zsh is the account's login shell; Oh My Zsh, Starship, Kitty, and the tracked Zsh/FZF configuration are installed.
- **Development:** Python 3.14 system runtime plus uv-managed 3.12/3.13; rustup stable; Node LTS via NVM; pnpm, Yarn, TypeScript, frontend language tools, backend and cloud tools, and local databases.
- **Containers/AI:** rootless Docker works; Ollama detects the RX 6700 XT via ROCm. No model is installed, so model inference and GPU layer placement have not yet been checked.
- **Network protection:** UFW is active with deny-incoming/allow-outgoing policy and no inbound allow rules. The Proton VPN daemon is running without a tunnel. Mullvad is installed but disabled.
- **Updates:** no pending official-repository or AUR updates were reported by `pacman -Qu` and `yay -Qua` at snapshot time. AUR metadata still marks `logseq-desktop-bin` and `ttf-jetbrains-maple-mono-nf-xx-xx` out of date; this is maintainer status, not a pending update from the installed package manager.

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
| Bootloader | Limine 12.9.4; active firmware entry is Limine |
| Limine menu | Exactly `CachyOS → linux-cachyos`; default entry is set to that kernel, with last-entry memory disabled |
| Firmware boot entries | Limine and generic `UEFI OS` fallback entries; no Windows entry was present in the UEFI boot order |
| Kernels | `linux-cachyos` 7.3.0-4 is the only installed CachyOS kernel package; LTS and RT kernels were removed to prevent menu regeneration |
| Snapshots | Snapper root snapshots remain enabled; `limine-snapper-sync.service` is disabled/inactive and snapshots are hidden from Limine |
| Other menu entries | Windows Boot Manager and the Limine EFI fallback entry were removed from `/boot/limine.conf`; EFI fallback files and firmware entries were preserved |
| Limine policy | `/etc/default/limine`: `BOOT_ORDER="linux-cachyos"` (ordering only; it is not documented as hiding entries), `FIND_BOOTLOADERS="no"` (stops discovery of other loaders); `/boot/limine.conf`: default `CachyOS/linux-cachyos`, `remember_last_entry: no`. The single-entry menu comes from removing the other kernel packages and disabling `limine-snapper-sync`. Whether manual `default_entry` edits survive `limine-update` is undocumented upstream: re-run `sudo limine-list` after each kernel update. <!-- UNVERIFIED --> |

Only the primary `linux-cachyos` kernel package remains installed. The running kernel is `7.3.0-4-cachyos`.

### Memory, thermals, and GPU tools

- Active swap is `/dev/zram0`: 31.3 GiB, zstd, priority 100. Usage was only a few MiB while idle. Leave the CachyOS zram setup as-is unless a workload measurement supports changing it.
- `lm_sensors`, `inxi`, `cpu-x`, `glances`, `mission-center`, `amdgpu_top`, `nvtop`, `radeontop`, `rocm-smi-lib`, and LACT are installed.
- Temperature readings are transient; use `sensors`, `inxi -Fxxxz`, or the GPU monitor tools when diagnosing a live problem.
- CPU power profile was `performance` at inspection.

## Operating system and desktop

- `/etc/os-release`: CachyOS Linux, rolling release.
- Active session: Hyprland `0.56.2`, Wayland; Noctalia Shell `5.4.0`.
- Active login manager: `greetd` with `/usr/bin/noctalia-greeter-session`. SDDM remains installed but disabled and inactive.
- Limine exposes only `CachyOS → linux-cachyos`; Snapper snapshots remain available for rollback but are hidden from the boot menu.
- Locale configuration: `en_US.UTF-8`, including `LC_TIME=en_US.UTF-8`. Timezone: `Asia/Kathmandu`; system clock sync is enabled.
- Audio session: PipeWire, PipeWire Pulse, and WirePlumber.
- Display server compatibility: Xwayland is installed for X11 applications.

### Default applications

| Use | Default |
|---|---|
| Web browser / HTTP links | Brave (`brave-browser.desktop`) |
| Plain text/source files | Zed (`dev.zed.Zed.desktop`) |
| PNG/JPEG images | Swash (`dev.lemmy.swash.desktop`) |
| PDF files | Brave |
| Login shell | `/usr/bin/zsh` |

Firefox is installed as an alternate browser. Vim and Neovim are installed. Other installed editors include VS Code, Sublime Text, PyCharm Community, and Zed. Desktop applications also include DBeaver, MongoDB Compass, Obsidian, Notion, Anytype, Logseq, Todoist, Slack, Discord, Signal, Telegram, Zoom, Mailspring, Thunderbird, Spotify, VLC, mpv, OBS Studio, GIMP, Inkscape, LibreOffice, OnlyOffice, Okular, and Strawberry.

### Current session environment refresh

The tracked Zsh config, tracked UWSM environment, XDG defaults, running Hyprland session (`BROWSER=brave`), and systemd user-manager environment all select Brave.

The account is in the `openrazer` supplementary group (`id` includes `953(openrazer)`) and the user unit `openrazer-daemon.service` is active for the connected Razer Viper Mini.

## Shell and language toolchains

### Zsh and terminal

- `/usr/bin/zsh` is the login shell; Oh My Zsh and Starship are configured.
- `~/.zshrc` is syntax-checked and integrates NVM from `/usr/share/nvm`.
- Kitty, FZF, zoxide, Atuin, eza, bat, ripgrep, fd, lazygit, tmux, and other command-line tools are in the package lists.
- `./install.sh status` reports all 32 managed entries in sync. `git diff --check` and `zsh -n ~/.zshrc` pass.

### Python

- System Python: 3.14.8, managed by pacman.
- uv: 0.13.6; uv-managed CPython 3.12.15 and 3.13.17.
- User tools: Ruff, Pyright, mypy, pre-commit, IPython, HTTPie, and JupyterLab.
- Add frameworks and database drivers to each project with `uv add`; no project framework is installed into the system Python.

### JavaScript and TypeScript

- System Node: 26.12.1; NVM's default LTS in the interactive user shell at the snapshot: Node 24.22.1 and npm 11.19.1. Node 26 became LTS on 2026-10-28 and moved Node 24 to Maintenance on 2026-10-20, so `nvm install --lts` now resolves to 26.x.
- pnpm 12.15.0; Yarn 1.22.22.
- Global user tools: TypeScript 7, TypeScript language server, ESLint, Prettier, and Tailwind CSS language server. Caveat found on 2026-10-29: TypeScript 7.0.2 ships no JS API and no `tsserver.js`, so `typescript-language-server` fails to start unless `typescript@6` (Arch `typescript`) is installed beside it, and `typescript-eslint` rejects TypeScript 7.
- Create frontend projects with `pnpm create vite`; keep framework versions and project dependencies in the project manifest.

### Rust

- rustup stable is the default: rustc/cargo 1.99.1.
- Installed components: rustfmt, clippy, rust-src, rust-analyzer, rust-docs, and the x86-64 standard library.

### Development, cloud, and data tools

Installed tools include PostgreSQL 18 with pgvector, MariaDB 13, MongoDB 8.3, Valkey 9.1, SQLite, Docker/Compose/Buildx, Kubernetes (`kubectl`, minikube, Helm, k9s), AWS CLI, Azure CLI, Terraform, OpenTofu, Pulumi, Ansible, GitLab Runner, and `act`. Stremio's native Linux client is installed from the official Stremio Linux shell project. Google Cloud CLI was removed on 2026-10-27. Nginx is installed but disabled. Cloud accounts and credentials are not configured in the dotfiles.

## Databases and local service endpoints

The database directories were initialized from empty state. No production data or database backups are part of this dotfiles checkout.

| Service | State and local configuration |
|---|---|
| PostgreSQL | Enabled/active, v18.6, listens on localhost:5432. Peer-authenticated `kneeraazon` role with `CREATEDB`; local `dev` database; `vector` extension enabled. Host authentication uses SCRAM. |
| MongoDB | Enabled/active, v8.3.9, `/etc/mongodb.conf` binds `127.0.0.1:27017`. No authentication configured; remains loopback-only and behind UFW. |
| MariaDB | Enabled/active, v13.0.2, bound to `127.0.0.1:3306` by `/etc/my.cnf.d/90-local-dev.cnf`. Local `dev` database; Unix socket authentication for `kneeraazon`. |
| Valkey | Enabled/active, v9.1.2, binds `127.0.0.1` and `::1` on port 6379; protected mode is on. |
| Ollama | Enabled/active, v0.40.11, listens on `127.0.0.1:11434`; no model is installed. |
| Rootless Docker | User service active/enabled; selected CLI context is `rootless`; `hello-world` completed successfully. |

`nginx` is installed but not enabled. The database and Ollama listeners were checked on loopback; they are not exposed for LAN use.

## Local AI and graphics stack

- AMDGPU kernel driver, Mesa/RADV Vulkan, ROCm/HIP runtime 7.2, rocBLAS, rocSOLVER, HIPBLAS, `rocminfo`, `rocm-smi`, and Ollama ROCm/Vulkan packages are installed.
- Ollama service drop-ins are tracked under `05-ai/ollama/systemd/` and installed under `/etc/systemd/system/ollama.service.d/`. The active backend sets `HSA_OVERRIDE_GFX_VERSION=10.3.0`; `cap_perfmon=ep` is set and reapplied by a pacman hook.
- Ollama startup detected `AMD Radeon RX 6700 XT`, ROCm compute `gfx1030`, and 12.0 GiB VRAM. This confirms device discovery only. Since no model is installed, inference speed and actual GPU layer placement remain untested.
- Do not download a large model as part of a fresh setup. For a GPU smoke test, choose a small model, run a short prompt, then confirm GPU residency with `ollama ps` and the Ollama journal before choosing larger models.
- ZRAM was already active and suitable; no zram change was made.

## Security, VPN, and service state

UFW is enabled and active: default incoming deny, outgoing allow, routed traffic disabled, and no inbound allow rules. A remote administration setup needs a reviewed SSH rule before enabling that policy.

| Component | Current state |
|---|---|
| Proton VPN | Package installed; `proton.VPN.service` active; no VPN tunnel/interface in the active network connections. |
| Mullvad | Package installed; daemon and early-boot blocker disabled/inactive. Its package hook had enabled them during installation; they were explicitly disabled afterward. |
| OpenRazer | Razer Viper Mini connected. User is in `openrazer` group; user unit `openrazer-daemon.service` is enabled and active. |
| AppArmor | `apparmor.d` profiles installed. `linux-cachyos` is built with AppArmor (`CONFIG_SECURITY_APPARMOR=y`) but its default `CONFIG_LSM` is `landlock,lockdown,yama,integrity,bpf`, so `aa-status` reports the module loaded and the filesystem not mounted until the boot command line carries `lsm=landlock,lockdown,yama,integrity,apparmor,bpf`. Not enforcing. See [chapter 19](01-system/cachyos/setup/19-security-privacy.md) for the enablement steps; apparmor.d does not list greetd or Hyprland among supported desktops. |
| Fail2ban | Installed, service not enabled. |
| DNSCrypt/dnsmasq | Installed, services not enabled. DNS/network-manager configuration was left intact. |
| Syncthing | Installed, service not enabled. |
| Nginx | Installed, service not enabled. |
| SDDM | Installed, service disabled/inactive; greetd is the active greeter. |
| Rootful Docker daemon | Not used. Docker operates as the rootless user service; the user is not in the `docker` group. |

Other notable active services include NetworkManager, systemd-resolved, systemd-timesyncd, power-profiles-daemon (performance profile), Avahi, Ananicy-C++, bpftune, and dmemcg-booster (`limine-snapper-sync.service` is intentionally disabled so Snapper snapshots stay out of the single-entry Limine boot menu).

## Dotfiles and package records

- Checkout: `~/dotfiles`, remote `https://github.com/karkinirajan/dotfiles.git`.
- Root README install instructions cover the desktop, system, font, CLI, and focus manifests. `01-system/cachyos/dev-stack.md` documents the optional developer profile; `05-ai/ollama/README.md` documents the AMD-specific Ollama configuration.
- The desktop manifest reflects the active greetd/Noctalia greeter and the installed desktop applications. The system manifest records UFW, power management, snapshot packages, and installed-but-disabled optional security services.
- The tracked MariaDB loopback configuration is `01-system/cachyos/mariadb-local.cnf`; the reproducible bundled-runtime Upwork package is `01-system/cachyos/aur/upwork/PKGBUILD`.
- At snapshot time, pacman listed 1,730 installed packages: 324 explicitly installed and 30 foreign packages not found in enabled sync repositories. The complete explicit and foreign package/version snapshots are below.

## Fresh setup order

The following rebuilds this workstation's profile. Keep package versions rolling; do not copy this machine's IDs, filesystem UUIDs, credentials, or private data. Restore personal data and secrets separately from backups.

### 1. Inspect the target and install the CachyOS baseline

Confirm UEFI mode, disks, GPU, network access, and available backups before running the installer. Do not format or repartition to match the snapshot. Clone the public repository and follow the package command in the root README:

```sh
git clone https://github.com/karkinirajan/dotfiles.git ~/dotfiles
cd ~/dotfiles
sudo pacman -Syu
```

Install the tracked desktop, system, font, CLI, and focus package lists using the README's repository/AUR split. The baseline includes the active greetd/Noctalia greeter and UFW packages. Review the package plan, especially AUR packages.

### 2. Install the optional developer and application profile

Follow `01-system/cachyos/dev-stack.md` to install `packages/developer.txt` and the optional AUR applications. Build Upwork from the tracked local PKGBUILD, not the AUR recipe that compiles Electron/Chromium. After the Mullvad package finishes, keep both Mullvad services disabled unless choosing Mullvad as the active VPN.

### 3. Apply the dotfiles and refresh session environment

Preview, install, and check the managed links:

```sh
./install.sh --dry-run
./install.sh
./install.sh status
zsh -n ~/.zshrc
```

The user environment file selects `BROWSER=brave` and configures NVM. Sign out and back in after environment changes so Hyprland and user systemd services inherit the updated values.

### 4. Initialize local databases

Initialize PostgreSQL only if `/var/lib/postgres/data/PG_VERSION` does not exist. Keep the database bound to localhost:

```sh
sudo install -d -o postgres -g postgres -m 700 /var/lib/postgres/data
sudo -u postgres initdb --locale=C.UTF-8 -E UTF8 \
  -D /var/lib/postgres/data --data-checksums \
  --auth-local=peer --auth-host=scram-sha-256
sudo systemctl enable --now postgresql
sudo -u postgres createuser --createdb "$USER"
sudo -u postgres createdb -O "$USER" dev
sudo -u postgres psql -d dev -c 'CREATE EXTENSION vector'
```

For MariaDB, initialize its data directory only if it is empty, install the tracked local bind configuration, and start the service:

```sh
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo install -Dm644 01-system/cachyos/mariadb-local.cnf \
  /etc/my.cnf.d/90-local-dev.cnf
sudo systemctl enable --now mariadb
```

Then, using the local root socket, create database `dev`, create the matching Unix-socket user, and grant that user access to `dev`. Start MongoDB and Valkey only after confirming their loopback bindings. No service in this profile needs a public listener.

### 5. Enable rootless Docker

`docker-rootless-extras` is an AUR package (it is in neither Arch extra nor the CachyOS repos); with the `rootlesskit` and `slirp4netns` packages it provides the rootless setup tooling, and `dockerd-rootless-setuptool.sh install` creates the user unit. Enable it, create/select the rootless context if needed, and run the smoke test:

```sh
systemctl --user enable --now docker
```

If the context is missing, create it with `docker context create rootless --docker "host=unix:///run/user/$(id -u)/docker.sock"`, then run `docker context use rootless` and `docker run --rm hello-world`. Do not add the user to the root-equivalent `docker` group. Lingering is not enabled on this host.

### 6. Enable the AMD Ollama backend

Check that the target GPU is the RX 6700 XT before using this host-specific override. Install the package set from `01-system/cachyos/packages/ai.txt`, copy the tracked ROCm and Claude Code drop-ins, backend helper, and pacman hook as described in `05-ai/ollama/README.md`, then:

```sh
sudo setcap cap_perfmon+ep /usr/bin/ollama
sudo systemctl daemon-reload
sudo systemctl enable --now ollama
journalctl -u ollama -b --no-pager | rg 'inference compute'
```

Do not download a large model during setup. Choose a small model for an inference smoke test and confirm actual GPU layer placement before scaling up.

### 7. Restore firewall and Razer behavior

For a local workstation, reproduce UFW's deny-incoming/allow-outgoing policy after confirming no remote SSH session depends on inbound access. Do not add inbound database rules. Add the account to `openrazer`, sign out/in, then confirm the Razer Viper Mini daemon starts. Leave VPN services disconnected until the user signs in to the selected VPN provider.

### 8. Verify the resulting host

```sh
systemctl is-active postgresql mongodb mariadb valkey ollama ufw
systemctl --user is-active docker openrazer-daemon
psql -d dev -c 'select current_user, current_database()'
mongosh --quiet --eval 'db.runCommand({ping:1})'
mariadb --protocol=socket -u "$USER" dev -e 'select database()'
valkey-cli ping
docker context show
docker run --rm hello-world
zramctl
./install.sh status
```

Also verify that database and Ollama TCP listeners use loopback, XDG defaults are Brave/Zed/Swash, the user environment has `BROWSER=brave`, and the OpenRazer user service is active after the login refresh.

## Beyond the base setup

- Start each Python service inside its own uv environment, e.g. `uv init --python 3.12 api && cd api && uv add fastapi 'uvicorn[standard]'`.
- Start each frontend in its own package manifest, e.g. `pnpm create vite`; select React/Vue/Svelte/other dependencies per project.
- Create Rust projects with `cargo new`; retain dependencies in `Cargo.toml`.
- Start minikube only when a local Kubernetes cluster is needed; it is installed but not running in the current profile.
- Install Nginx, Syncthing, DNS filtering, Fail2ban, or AppArmor enforcement only after reviewing the target network, kernel support, and service rules.
- Download an Ollama model only after selecting its size and workload; confirm VRAM placement with `ollama ps` during inference.
- Keep personal application sign-ins, credentials, SSH keys, project files, databases, and Ollama model data outside this repository and restore them from their own backups.

## Complete explicit package snapshot

The files below are the sorted live `pacman -Qe` output captured on 2026-10-28 (explicitly installed names and versions; dependencies omitted) and the `pacman -Qm` output (packages not present in enabled sync repositories).

Package snapshots (captured 2026-10-28):

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
