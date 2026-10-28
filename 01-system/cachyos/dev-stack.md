# Developer stack on CachyOS

This records the optional full development profile and the local service
choices used on the primary machine. The developer packages are listed in
[`packages/developer.txt`](packages/developer.txt); it is kept separate from
the lightweight desktop baseline. `(AUR)` entries need `yay` or `paru`.
Core desktop applications and the active greetd/Noctalia greeter are listed in
[`packages/desktop.txt`](packages/desktop.txt); system security and power
services are in [`packages/system.txt`](packages/system.txt).
Upwork is built from its official vendor package using
[`aur/upwork/PKGBUILD`](aur/upwork/PKGBUILD).

This workstation has Arch's `multilib` repository enabled in
`/etc/pacman.conf` for its installed 32-bit runtime libraries. Keep that repo
enabled so pacman and yay recognize those `lib32-*` packages as repository
packages rather than reporting them as foreign/AUR misses.

## Install the package profile

Review the list, then install repository packages and AUR packages separately:

```sh
mapfile -t repo_packages < <(awk 'NF && $1 !~ /^#/ && $2 != "(AUR)" {print $1}' \
  01-system/cachyos/packages/developer.txt)
mapfile -t aur_packages < <(awk 'NF && $1 !~ /^#/ && $2 == "(AUR)" {print $1}' \
  01-system/cachyos/packages/developer.txt)
sudo pacman -S --needed "${repo_packages[@]}"
aur_helper="$(command -v paru || command -v yay || true)"
if ((${#aur_packages[@]})); then
  "$aur_helper" -S --needed "${aur_packages[@]}"
fi
```

The Mullvad package's install hook may enable its daemon and early-boot
blocker. This machine keeps those services disabled while using Proton VPN:

```sh
sudo systemctl disable --now mullvad-daemon.service mullvad-early-boot-blocking.service
```

Install Upwork from its bundled runtime package:

```sh
cd 01-system/cachyos/aur/upwork
makepkg -si
```

## Language toolchains

- **Python:** the system Python stays managed by pacman. `uv` provides Python
  3.12 and 3.13 and isolated tools (`ruff`, `pyright`, `mypy`, `pre-commit`,
  `ipython`, `httpie`, and JupyterLab). Start each project with
  `uv init --python 3.12` and add application dependencies with `uv add`.
- **Rust:** rustup stable is the default, with `rustfmt`, `clippy`, `rust-src`,
  and `rust-analyzer`. Keep project dependencies in each Cargo manifest.
- **JavaScript/TypeScript:** Node is managed by NVM; the default is the current
  LTS release. pnpm and Yarn are available, with TypeScript, its language
  server, ESLint, Prettier, and Tailwind CSS language tooling installed for
  the user. Start a frontend project with `pnpm create vite` and add framework
  dependencies to the project instead of the global toolchain.
- **Backend frameworks:** use per-project Python environments, for example
  `uv init --python 3.12 api && cd api && uv add fastapi 'uvicorn[standard]'`.
  This keeps frameworks and database drivers pinned with the project.

## Local databases and services

PostgreSQL, MongoDB, MariaDB, and Valkey run as system services and bind only
to loopback. PostgreSQL has a local peer-authenticated `kneeraazon` role and a
`dev` database with `pgvector` enabled. MariaDB has a `dev` database with
socket authentication for the matching Unix user. MongoDB uses its packaged
configuration at `/etc/mongodb.conf` (`bindIp: 127.0.0.1`).

MariaDB reads [`mariadb-local.cnf`](mariadb-local.cnf) through
`/etc/my.cnf.d`; install it as `/etc/my.cnf.d/90-local-dev.cnf` before
starting MariaDB on a new machine. This prevents the server from listening on
every network interface.

```sh
systemctl is-active postgresql mongodb mariadb valkey
psql -d dev -c 'select current_user, current_database()'
mongosh --quiet --eval 'db.runCommand({ping:1})'
mariadb --protocol=socket -u "$USER" dev -e 'select database()'
valkey-cli ping
```

Nginx is installed but stays disabled until a project needs a web server.

UFW is active with incoming traffic denied by default, outgoing traffic
allowed, and no inbound allow rules. Local development services remain
loopback-only. If a project needs LAN access, add a narrowly scoped firewall
rule for that service and remove it when no longer needed.

To reproduce this firewall baseline on a local workstation, inspect the rules
first, then set the defaults and enable UFW. Do not run this over remote SSH
unless the required SSH allow rule is already in place:

```sh
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
sudo ufw status verbose
```

The Proton VPN daemon is running, but the current network has no VPN tunnel.
Mullvad is also installed; its daemon and early-boot blocker are disabled.
Do not enable both VPN clients at once. DNSCrypt Proxy, dnsmasq, Fail2ban,
Syncthing, and AppArmor profiles are installed, but the associated services
are not all enabled; see the live inventory in `system-summary.md`.

## Rootless Docker

Docker runs as the user service `docker.service`; the system-wide daemon is
not used, and the account is not added to the root-equivalent `docker` group.
The `rootless` CLI context is selected. The service starts with the user's
systemd session; lingering is optional if it must run while logged out.

```sh
systemctl --user enable --now docker
docker context use rootless
docker run --rm hello-world
```

The connected Razer Viper Mini uses OpenRazer. Add the account to the
`openrazer` group and sign out and back in once so the user service manager
receives the new supplementary group:

```sh
sudo gpasswd -a "$USER" openrazer
```

The daemon is enabled for the next user session. Then verify
`systemctl --user status openrazer-daemon` and `openrazer-daemon --verbose`.

## Local AI and hardware

The host uses Ollama's ROCm backend for its RX 6700 XT (gfx1031), with the
tracked systemd drop-ins and `HSA_OVERRIDE_GFX_VERSION=10.3.0` from
[`../../05-ai/ollama/README.md`](../../05-ai/ollama/README.md). Confirm actual
backend detection in `journalctl -u ollama`; loading a model is required to
confirm GPU layer placement. GPU telemetry includes `amdgpu_top`, `nvtop`,
`radeontop`, `rocm-smi`, and `sensors`.

CachyOS already provides active zstd zram swap on this machine (about 31 GiB).
Inspect `zramctl` before changing its size or compression settings; do not
replace the distribution configuration with the smaller example elsewhere
in this guide without checking current memory and workload needs.

## Desktop defaults and optional applications

Brave is the XDG browser default, Zed opens text and source files, and Swash
opens images. The shell config, UWSM environment file, running Hyprland
session, and systemd user environment all use `BROWSER=brave`.

Upwork, VS Code, Sublime Text, PyCharm Community, DBeaver, MongoDB Compass,
Firefox, Obsidian, Notion, Anytype, Logseq, Todoist, Slack, Signal, Discord,
Telegram, Mailspring, Thunderbird, Zoom, Spotify, and the installed media and
office applications are recorded in the package inventory.

Upwork's time tracker and screenshot capture are not supported in Wayland
sessions according to [Upwork's Linux troubleshooting guide](https://support.upwork.com/hc/en-us/articles/211064108-How-to-troubleshoot-our-desktop-app-Linux).
The app can be installed and launched under Hyprland, but hourly contract
tracking that requires screenshots needs a supported Xorg session.

See [`system-summary.md`](../../system-summary.md) for the exact enabled and
disabled service state, package versions, and the complete fresh-setup order.
