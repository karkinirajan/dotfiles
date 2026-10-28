# Current System Summary

**Snapshot:** 2026-10-27, Asia/Kathmandu (refreshed after Stremio installation)  
**Host:** CachyOS x86-64, user `kneeraazon`  
**Purpose:** current host inventory and the ordered procedure to reproduce its configured development workstation from this repository.

This file records the machine as it is, including enabled services, package versions, local defaults, and the remaining login refresh. It intentionally omits passwords, network addresses, disk UUIDs, serial numbers, and other machine-specific identifiers. Package versions are a point-in-time snapshot; use current CachyOS/Arch and AUR packages during a fresh setup.

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
| Limine policy | `/etc/default/limine`: `BOOT_ORDER="linux-cachyos"`, `FIND_BOOTLOADERS="no"`; `/boot/limine.conf`: default `CachyOS/linux-cachyos`, `remember_last_entry: no` |

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
- Limine manages the CachyOS, LTS, real-time, and Snapper snapshot entries.
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

The tracked Zsh config, tracked UWSM environment, XDG defaults, and systemd user-manager environment now select Brave. The already-running Hyprland process still has `BROWSER=firefox`, inherited before those changes. The user manager has `BROWSER=brave`, and new interactive Zsh shells export Brave.

The account was also added to the `openrazer` group for the connected Razer Viper Mini. Existing processes and the running user service manager do not gain that new supplementary group until a fresh login. **One sign-out/sign-in is still needed** to refresh both Hyprland's inherited browser environment and the OpenRazer group. This session was left running to avoid closing the user's applications. After logging back in, check the browser environment and `systemctl --user status openrazer-daemon`.

## Shell and language toolchains

### Zsh and terminal

- `/usr/bin/zsh` is the login shell; Oh My Zsh and Starship are configured.
- `~/.zshrc` is syntax-checked and integrates NVM from `/usr/share/nvm`.
- Kitty, FZF, zoxide, Atuin, eza, bat, ripgrep, fd, lazygit, tmux, and other command-line tools are in the package lists.
- `./install.sh status` reports 31 managed entries OK, 0 drift, 0 missing, and 0 errors. `git diff --check` and `zsh -n ~/.zshrc` pass.

### Python

- System Python: 3.14.8, managed by pacman.
- uv: 0.13.5; uv-managed CPython 3.12.15 and 3.13.17.
- User tools: Ruff, Pyright, mypy, pre-commit, IPython, HTTPie, and JupyterLab.
- Add frameworks and database drivers to each project with `uv add`; no project framework is installed into the system Python.

### JavaScript and TypeScript

- System Node: 26.12.1; NVM's default LTS in the interactive user shell: Node 24.22.1 and npm 11.19.1.
- pnpm 12.15.0; Yarn 1.22.22.
- Global user tools: TypeScript 7, TypeScript language server, ESLint, Prettier, and Tailwind CSS language server.
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
| OpenRazer | Razer Viper Mini connected. User was added to `openrazer`; enabled user unit is inactive until the next login refreshes group membership. |
| AppArmor | `apparmor.d` profiles installed and kernel module reports loaded, but `aa-status` says the AppArmor filesystem is not mounted. Do not treat profile enforcement as active. |
| Fail2ban | Installed, service not enabled. |
| DNSCrypt/dnsmasq | Installed, services not enabled. DNS/network-manager configuration was left intact. |
| Syncthing | Installed, service not enabled. |
| Nginx | Installed, service not enabled. |
| SDDM | Installed, service disabled/inactive; greetd is the active greeter. |
| Rootful Docker daemon | Not used. Docker operates as the rootless user service; the user is not in the `docker` group. |

Other notable active services include NetworkManager, systemd-resolved, systemd-timesyncd, power-profiles-daemon (performance profile), Avahi, Ananicy-C++, bpftune, dmemcg-booster, and Limine/Snapper synchronization.

## Dotfiles and package records

- Checkout: `~/dotfiles`, remote `https://github.com/karkinirajan/dotfiles.git`.
- Root README install instructions cover the desktop, system, font, CLI, and focus manifests. `01-system/cachyos/dev-stack.md` documents the optional developer profile; `05-ai/ollama/README.md` documents the AMD-specific Ollama configuration.
- The desktop manifest reflects the active greetd/Noctalia greeter and the installed desktop applications. The system manifest records UFW, power management, snapshot packages, and installed-but-disabled optional security services.
- The tracked MariaDB loopback configuration is `01-system/cachyos/mariadb-local.cnf`; the reproducible bundled-runtime Upwork package is `01-system/cachyos/aur/upwork/PKGBUILD`.
- At snapshot time, pacman listed 1,713 installed packages: 324 explicitly installed and 78 foreign packages not found in enabled sync repositories. The complete explicit and foreign package/version snapshots are below.
- The checkout has uncommitted local changes from the desktop, shell, system, and developer-profile work. It has not been committed or pushed.

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

The CachyOS package `docker-rootless-extras` installs a user unit. Enable it, create/select the rootless context if needed, and run the smoke test:

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

The following is the sorted live `pacman -Qe` output captured on 2026-10-27 after removing Google Cloud CLI, enabling the matching multilib repository, installing paru, and installing Stremio. It records explicitly installed package names and versions; dependency packages are omitted. The second list records packages not present in enabled sync repositories (`pacman -Qm`), including AUR build dependencies.

<details>
<summary>Explicitly installed packages (pacman -Qe)</summary>

```text
accountsservice 26.27.3-1.1
act 0.2.89-1.1
ai-usagebar-bin 1.44.0-1
alacritty 0.17.0-1.2
alsa-firmware 1.2.4-4
alsa-plugins 1:1.2.12-6.1
alsa-utils 1.2.16-1.1
amd-ucode 1:20261019-1
amdgpu_top 0.11.5-1.1
ansible 14.5.0-1
antigravity 2.26.0-1
antigravity-cli 1.4.8_5447777392656384-1
antigravity-ide 2.5.5-2
anytype-bin 0.57.4-1
apparmor.d 0.4915.0-1
ark 26.08.2-1.1
atuin 18.24.2-1.1
awesome-terminal-fonts 1.1.0-5
aws-cli-v2 2.37.9-1
azure-cli 2.90.0-1
base 3-3
base-devel 1-2
bash-completion 2.18.0-1
bind 9.20.30-1.1
bitwarden 2026.3.1-2.1
bluez 5.87-2.1
bluez-hid2hci 5.87-2.1
bluez-libs 5.87-2.1
bluez-obex 5.87-2.1
bluez-utils 5.87-2.1
bpftune-git r764.4712347-1
brave-bin 1:1.98.60-1
btop 1.4.7-1.1
btrfs-assistant 3.0.0-1.1
btrfs-progs 7.3-1
cachyos-benchmarker 0.8.0-2
cachyos-drm-awaiter 7-1
cachyos-fish-config 16-1
cachyos-hello 0.28.1-1
cachyos-hooks 2026.10.23-1
cachyos-hypr-noctalia 1.2.6-1
cachyos-kernel-manager 1.19.0-1
cachyos-keyring 20240331-1
cachyos-micro-settings 1.0.0-1
cachyos-mirrorlist 27-1
cachyos-packageinstaller 1.6.2-1
cachyos-plymouth-bootanimation 2-4
cachyos-plymouth-theme 1-2
cachyos-rate-mirrors 24-1
cachyos-settings 1:1.4.1-1
cachyos-snapper-support 1.0.2-1
cachyos-v3-mirrorlist 27-1
cachyos-v4-mirrorlist 27-1
cachyos-wallpapers r23.964263e-1
cachyos-zsh-config 1.0.3-1
cantarell-fonts 1:0.311-1
chwd 1.25.0-1
claude-code 2.1.310-1
claude-desktop 3.6556.2-1
cliphist 1:0.7.0-2.1
copyq 16.0.0-1.1
cpu-x 5.4.1-1.1
cpupower 7.3-1
cryptsetup 2.8.8-1.1
dbeaver 26.2.2-1.1
deluge-gtk 1:2.2.0-8.1
device-mapper 2.03.43-2.1
diffutils 3.12-2.1
direnv 2.38.2-1.1
discord 1:1.0.167-1
dmemcg-booster 0.1.3-1
dmidecode 3.7-1
dmraid 1.0.0.rc16.3-15.1
dnscrypt-proxy 2.1.19-1.1
dnsmasq 2.93-1.1
docker 1:29.9.2-1.1
docker-buildx 0.38.1-1.1
docker-compose 5.6.1-1.1
docker-machine 0.16.2-6
docker-rootless-extras 29.9.2-1
dolphin 26.08.2-1.1
dosfstools 4.2-5.1
duf 0.9.1-1.1
dust 1.2.6-1.1
e2fsprogs 1.47.4-1.1
efibootmgr 18-4.1
efitools 1.9.2-7.1
ethtool 1:7.2-1.1
exfatprogs 1.4.3-1.1
f2fs-tools 1.17.0-1.1
fail2ban 1.1.1-1
fastfetch 2.70.0-1.1
ffmpegthumbnailer 2.3.1-1.1
ffmpegthumbs 26.08.2-1.1
firefox 158.0.1-1.1
flameshot 14.0.0-1.1
fsarchiver 0.8.9-1.1
gimp 3.2.6-2.1
git 2.56.0-1.1
gitlab-runner 19.5.1-1.1
glances 4.5.8-1
gparted 1.8.1-2.1
gst-libav 1.28.8-1
gst-plugin-pipewire 1:1.6.10-1
gst-plugin-va 1.28.8-1
gst-plugins-bad 1.28.8-1
gst-plugins-ugly 1.28.8-1
hdparm 9.65-3.1
helm 4.3.0-1.1
hip-runtime-amd 7.2.4-1.1
hipblas 7.2.4-1.1
hwdetect 2026.10.01.1149-1
hwinfo 26.0-1.1
hyfetch 2.1.0-1.1
hypridle 0.1.8-2.1
hyprland 0.56.2-4.1
hyprlock 0.9.6-3.1
hyprpm 0.56.2-4.1
hyprpolkitagent 0.2.0-1.1
hyprsunset 0.4.0-3.1
hyprwayland-scanner 0.4.6-1.1
inetutils 2.8-1.1
inkscape 1.4.4-7.1
inotify-tools 4.26.270-1.1
inter-font 4.1-1
iwd 3.12-2.1
jfsutils 1.1.15-9.1
just 1.59.0-1.1
k9s 0.51.0-1.1
kdeconnect 26.08.2-1.1
kdegraphics-thumbnailers 26.08.2-1.1
kdiskmark 3.3.0-1.1
keepassxc 2.8.0-3.1
kitty 0.49.2-1.1
korganizer 26.08.2-1
kubectl 1.37.1-1
lact 0.10.1-1.1
lazygit 0.66.2-1.1
less 1:710-1.1
lib32-mesa 3:26.2.5-1
lib32-opencl-mesa 3:26.2.5-1
lib32-vulkan-radeon 3:26.2.5-1
libdvdcss 1.6.0-1.1
libgsf 1.14.60-1.1
libmythes 1:1.2.6-1.1
libopenraw 0.3.7-2.1
libreoffice-fresh 26.8.1-2.1
limine 12.9.4-1
limine-mkinitcpio-hook 1.40.0-1
limine-snapper-sync 1.32.1-1
linux-cachyos 7.3.0-4
linux-cachyos-headers 7.3.0-4
linux-firmware 1:20261019-1
logrotate 3.22.0-1.1
logseq-desktop-bin 0.10.15-1
lsb-release 2.0.r55.a25a4fc-1
lsscsi 0.32-2.2
lvm2 2.03.43-2.1
macchina 6.4.0-3.1
mailspring 1.26.2-1
man-db 2.13.1-2.1
man-pages 6.19-1
mariadb 13.0.2-2.1
mdadm 4.6-2
meld 3.24.1-1
mesa-utils 9.0.0-7.1
micro 2.0.15-3.1
minikube 1.38.1-2.1
mission-center 1.2.0-1.1
mkinitcpio 42.2-1
modemmanager 1.24.2-2.1
mongodb-bin 8.3.9-1
mongodb-compass-bin 1.53.0-1
mpv 1:0.41.0-6.1
mtools 1:4.0.49-1.1
mullvad-vpn-bin 2026.5-1
nano 9.2-1.1
nano-syntax-highlighting 2025.07.01.r0.g256995b-2
ncdu 2.9.2-1.1
neofetch 7.1.0-2
neovim 0.12.6-1.1
netctl 1.29-2
networkmanager 1.58.1-2
networkmanager-openvpn 1.12.5-2.1
nfs-utils 3.1.1-1.1
nginx 1.30.6-2.1
nilfs-utils 2.3.1-1.1
noctalia-greeter 1.7.0-1.1
notion-app-enhanced 2.0.18-1
noto-fonts 1:2026.10.01-1
noto-fonts-cjk 20240730-1
noto-fonts-emoji 1:2.057-1
nss-mdns 0.15.1-3.1
nvm 0.40.8-1
nvtop 3.3.2-1.1
obs-studio 32.2.2-1.1
obsidian 1.14.5-1
okular 26.08.2-1.1
ollama 0.40.11-1.1
ollama-rocm 0.40.11-1.1
ollama-vulkan 0.40.11-1.1
onlyoffice-bin 10.0.0-1
openai-codex 0.164.0-1.1
opencl-mesa 3:26.2.5-1
opendesktop-fonts 1.4.2-7
openrazer-daemon 3.12.4-1
openssh 10.6p1-2.1
opentofu 1.13.2-1.1
os-prober 1.85-1.1
otf-font-awesome 7.3.1-1
otf-fragment-mono 1.21-1
pacman-contrib 1.13.1-1.2
paru 2.1.0-3
pavucontrol 1:6.2-2.1
perl 5.44.0-1.1
pgvector 0.8.7-1.1
pipewire-alsa 1:1.6.10-1
pipewire-pulse 1:1.6.10-1
pkgfile 27-1.1
playerctl 2.4.1-5.1
plocate 1.1.25-1.1
plymouth 26.134.222-5
pnpm 12.15.0-1.1
poppler-glib 26.10.0-1.1
postgresql 18.6-4.1
power-profiles-daemon 0.30-3
procs 0.14.12-1.1
prometheus 3.15.1-1.1
proton-vpn-gtk-app 4.18.7-1
pulumi 3.272.0-1.1
pv 1.12.0-1.1
pycharm-community-edition 2026.2.3-1.1
python 3.14.8-1
python-defusedxml 0.7.1-8
python-packaging 26.3-1
radeontop 1.4-3.1
realtime-privileges 5-1
rebuild-detector 4.4.5-1
reflector 2023-5
ripgrep 15.2.0-1
rocblas 7.2.4-3
rocm-smi-lib 7.2.0-2.1
rocminfo 7.2.4-1.1
rocsolver 7.2.4-1
rootlesskit 3.3.0-1.1
rsync 3.5.1-3.1
rustup 1.29.2-1
s-nail 14.9.25-1.1
satty 0.22.0-1.1
sccache 0.19.0-1.1
sddm 0.21.0-8
sg3_utils 1.49-1.1
shelly 3.1.9-2
signal-desktop 8.32.0-1
slack-desktop 4.52.182-1
slirp4netns 1.3.6-1.1
smartmontools 7.5-2.1
snapper 0.13.2-1.1
sof-firmware 2026.09.2-1
speedtest-cli 2.1.3-11
spotify 1:1.3.4.258-2
starship 1.27.0-1
strawberry 1.2.31-1.1
stremio-linux-shell 1:1.2.2-1
sublime-text-4 4.4215-1
sudo 1.9.17.p2-6.1
swappy 1.8.0-1.1
syncthing 2.1.7-1.1
sysfsutils 2.1.1-2.2
telegram-desktop 7.3.3-1.1
terraform 1.15.9-1.1
texinfo 7.3-3.1
thunderbird 158.0.1-1.1
tmux 3.8-1.1
todoist-appimage 9.32.0-1
topgrade-bin 17.14.1-1
ttf-bitstream-vera 1.10-16
ttf-dejavu 2.37+18+g9b5d1b2f-8
ttf-fira-code 6.2-4
ttf-firacode-nerd 3.5.1-2
ttf-fragment-mono 1.21-1
ttf-jetbrains-maple-mono-nf-xx-xx 1.2304.76-1
ttf-jetbrains-maple-mono-xx-xx-ht 1.2304.73-1
ttf-jetbrains-mono 2.304-2
ttf-jetbrains-mono-nerd 3.5.1-2
ttf-liberation 2.1.5-2
ttf-meslo-nerd 3.5.1-2
ttf-opensans 3.003-1
ttf-roboto 3.016-1
ttf-weather-icons 2.0.12-1
ufw 0.36.2-7
ufw-extras 1.3.0-1
unrar 1:7.3.1-1.1
unzip 6.0-23.1
upower 1.91.5-1.1
upwork 5.8.0.41-6
usb_modeswitch 2.6.2.20251207-1.1
usbutils 019-1.1
uv 0.13.6-1.1
valkey 9.1.2-1.1
vim 9.2.1178-1.1
visual-studio-code-bin 1.143.1-1
vlc 3.0.24-1.1
vlc-plugins-all 3.0.24-1.1
vulkan-radeon 3:26.2.5-1
waybar 0.15.0-3.1
wget 1.25.0-6.1
which 2.25-1.1
wireplumber 0.5.18-1.1
wpa_supplicant 2:2.12-1.1
xdg-user-dirs 0.20-1.1
xf86-video-amdgpu 25.0.0-1.1
xfsprogs 7.2.1-1.1
xl2tpd 1.3.20-1.1
xorg-fonts-alias-misc 1.0.6-1
xorg-fonts-misc 1.0.4-2
xorg-server 21.1.25-2.1
yarn 1.22.22-2
yay 13.0.1-1
yazi 26.9.1-2.1
zapzap 7.5.1-1
zed 1.25.3-1
zoom 7.2.1-1
zoxide 0.10.0-1.1
```
</details>

<details>
<summary>Foreign packages (pacman -Qm)</summary>

```text
ai-usagebar-bin 1.44.0-1
antigravity 2.26.0-1
antigravity-cli 1.4.8_5447777392656384-1
antigravity-ide 2.5.5-2
anytype-bin 0.57.4-1
appimagelauncher 3.0.0_beta_3-1
docker-rootless-extras 29.9.2-1
logseq-desktop-bin 0.10.15-1
mongodb-bin 8.3.9-1
mongodb-compass-bin 1.53.0-1
mongosh-bin 2.14.0-1
mullvad-vpn-bin 2026.5-1
mullvad-vpn-daemon-bin 2026.5-1
neofetch 7.1.0-2
notion-app-enhanced 2.0.18-1
otf-fragment-mono 1.21-1
slack-desktop 4.52.182-1
spotify 1:1.3.4.258-2
stremio-linux-shell 1:1.2.2-1
sublime-text-4 4.4215-1
todoist-appimage 9.32.0-1
topgrade-bin 17.14.1-1
ttf-fragment-mono 1.21-1
ttf-jetbrains-maple-mono-nf-xx-xx 1.2304.76-1
ttf-jetbrains-maple-mono-xx-xx-ht 1.2304.73-1
ttf-weather-icons 2.0.12-1
upwork 5.8.0.41-6
visual-studio-code-bin 1.143.1-1
zapzap 7.5.1-1
zoom 7.2.1-1
```
</details>

## Claude Code update (2026-10-27)

- Claude Code `2.1.310` and Claude Desktop are installed. Its global configuration, agents, and skills are linked from this repository; 24 skills were already present. Added `token-efficient-workflow` as an on-demand skill. Restart Claude Code to refresh skill discovery, then invoke `/token-efficient-workflow` or let it trigger for relevant work.
- Installed user-level `ccusage` `20.0.45` with pnpm. It reports local Claude Code usage with `ccusage claude daily` and `ccusage claude session`; it does not change usage by itself.
- Added an optional package set for structural search, diffs, shell/workflow validation, benchmarking, and file watching. These eight pacman packages are documented but not installed: `ast-grep`, `actionlint`, `difftastic`, `git-delta`, `hyperfine`, `shellcheck`, `shfmt`, and `watchexec`. The install command is in `05-ai/claude-code/README.md`.
- Claude Code skills validated successfully with `claude plugin validate --strict`. `claude doctor` reports no installation issues.

## Limine menu cleanup (2026-10-27)

- The live menu was reduced to the sole entry `CachyOS → linux-cachyos`; `limine-list` confirmed it.
- Removed packages: `linux-cachyos-lts`, `linux-cachyos-lts-headers`, `linux-rt`, and `linux-rt-headers` (918.04 MiB). The running `linux-cachyos` kernel and its boot files were checked before the change and preserved.
- Removed menu-only paths: `CachyOS/Snapshots`, `Other systems and bootloaders` (including Windows Boot Manager), and `EFI fallback`. Bootable EFI fallback files, Snapper snapshots, and firmware NVRAM entries were left intact.
- Disabled `limine-snapper-sync.service`; Snapper itself remains configured. Set `BOOT_ORDER="linux-cachyos"` and `FIND_BOOTLOADERS="no"` in `/etc/default/limine`; set `default_entry: CachyOS/linux-cachyos` and `remember_last_entry: no` in `/boot/limine.conf`.
- Backups were written beside the active configs before editing. `limine-update` rebuilt the initramfs successfully and the final menu list contained only the intended entry.
