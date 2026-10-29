---
title: Developer stack on CachyOS
part: "01"
chapter: dev-stack
topic: dev-stack
versions: [python, uv, nodejs, postgresql, mariadb-lts, mongodb, docker, lact]
last_verified: 2026-10-29
status: current
sources:
  - https://www.postgresql.org/docs/18/app-initdb.html
  - https://docs.docker.com/engine/security/rootless/
  - https://mariadb.org/about/
---

# Developer stack on CachyOS

The optional full development profile and the local service choices used on the primary machine. Each step points to the setup chapter that explains and sources it; this page is the ordered runbook. Package lists: [`packages/developer.txt`](packages/developer.txt) (this profile), [`packages/desktop.txt`](packages/desktop.txt) (desktop and greeter), [`packages/system.txt`](packages/system.txt) (security and power). `(AUR)` entries need `paru` or `yay`.

This workstation has Arch's `multilib` repository enabled in `/etc/pacman.conf` for its 32-bit runtime libraries. Keep it enabled so pacman recognises the installed `lib32-*` packages as repository packages.

## 1. Install the package profile

Run everything here as your normal user, from the repository root (`cd ~/dotfiles`), not as root: `$USER` is used as the database role name. Review the list, then install repository and AUR packages separately. Names whose conflicting counterpart is already installed are skipped; never answer `y` to a "`mariadb-lts` and `mariadb` are in conflict, remove?" prompt on a host that already has a MariaDB data directory.

```sh
skip=()
pacman -Q mariadb >/dev/null 2>&1 && skip+=(mariadb-lts)
pacman -Q mullvad-vpn-bin >/dev/null 2>&1 && skip+=(mullvad-vpn)
pacman -Q logseq-desktop-bin >/dev/null 2>&1 && skip+=(logseq-og-bin)
filter() { awk -v s="${skip[*]}" 'BEGIN{n=split(s,a," "); for(i=1;i<=n;i++) k[a[i]]=1} NF && $1 !~ /^#/ && !($1 in k)'; }
mapfile -t repo_packages < <(filter < 01-system/cachyos/packages/developer.txt | awk '$2 != "(AUR)" {print $1}')
mapfile -t aur_packages < <(filter < 01-system/cachyos/packages/developer.txt | awk '$2 == "(AUR)" {print $1}')
sudo pacman -S --needed "${repo_packages[@]}"
aur_helper="$(command -v paru || command -v yay || true)"
if ((${#aur_packages[@]})); then
  "$aur_helper" -S --needed "${aur_packages[@]}"
fi
```

`mullvad-vpn` now comes from Arch `extra`; its package hook may enable `mullvad-daemon.service` and `mullvad-early-boot-blocking.service`. This machine keeps both disabled while Proton VPN is in use (see [chapter 19](setup/19-security-privacy.md)). Run this only if the units exist and are enabled:

```sh
systemctl list-unit-files 'mullvad-*' --no-legend | rg -q . && sudo systemctl disable --now mullvad-daemon.service mullvad-early-boot-blocking.service
```

Install Upwork from its bundled-runtime recipe ([`aur/upwork/`](aur/upwork/README.md)). This is an owner step and is skipped in unattended runs: the vendor CDN refuses scripted downloads, so the `.deb` must be downloaded in a browser first. The command refuses to run without it:

```sh
( cd 01-system/cachyos/aur/upwork && ls upwork_*_amd64.deb >/dev/null && makepkg -si )
```

## 2. Language toolchains

- **Python:** system Python <!-- v:python -->3.14.8<!-- /v --> stays under pacman (PEP 668 blocks global `pip`). `uv` <!-- v:uv -->0.13.6<!-- /v --> provides other interpreters (`uv python install 3.12 3.13`) and isolated tools; start projects with `uv init --python 3.14` (or 3.12) and `uv add`. See [chapter 03](setup/03-python-uv.md).
- **Rust:** `rustup` (extra, 1.29.2) from `packages/developer.txt`, then `rustup default stable` and `rustup component add rustfmt clippy rust-src rust-analyzer`. No setup chapter covers Rust beyond this line.
- **JavaScript/TypeScript:** Node is managed by NVM from pacman; `nvm install --lts` resolves to Node 26 (LTS since 2026-10-28), and Node 24 stays available for projects that pin it. pnpm and Yarn are available. Install TypeScript 6.x for tooling: `typescript@latest` is 7.0.2 (native compiler) and `typescript-eslint` rejects it. Details in [chapter 11](setup/11-frontend.md).
- **Backend frameworks:** per-project environments, for example `uv init --python 3.14 api && cd api && uv add fastapi 'uvicorn[standard]'`. A Django project that also uses `django-celery-beat` resolves to Django 6.0.9 today; pin `django>=5.2,<5.3` for the LTS.

## 3. Local databases and services

PostgreSQL, MongoDB, MariaDB and Valkey run as system services bound to loopback. The full steps, with the reasoning, are in [chapter 06](setup/06-databases.md); the order here is the one to run on a new machine.

**PostgreSQL <!-- v:postgresql -->18.6<!-- /v -->:** `initdb` must run before the service starts and its default authentication is `trust`, so the two auth flags are mandatory:

```sh
sudo pacman -S --needed postgresql pgvector
sudo install -d -o postgres -g postgres -m 700 /var/lib/postgres/data
sudo -u postgres initdb --locale=C.UTF-8 -E UTF8 \
  -D /var/lib/postgres/data --data-checksums \
  --auth-local=peer --auth-host=scram-sha-256
sudo systemctl enable --now postgresql
sudo -u postgres createuser --createdb "$USER"
sudo -u postgres createdb -O "$USER" dev
sudo -u postgres psql -d dev -c 'CREATE EXTENSION vector'
```

**MariaDB:** Arch `mariadb` is 13.0, a rolling release; use the long-term series <!-- v:mariadb-lts -->12.3.3<!-- /v --> (the two packages conflict). The tracked [`mariadb-local.cnf`](mariadb-local.cnf) pins `bind-address = 127.0.0.1`; install it before the first start, because MariaDB's own default is every interface:

Blank machine only (skip if `/var/lib/mysql` already holds data):

```sh
sudo pacman -S --needed mariadb-lts &&
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql &&
sudo install -Dm644 "$HOME/dotfiles/01-system/cachyos/mariadb-local.cnf" /etc/my.cnf.d/90-local-dev.cnf &&
sudo systemctl enable --now mariadb &&
sudo mariadb -e "CREATE DATABASE dev; CREATE USER '$USER'@'localhost' IDENTIFIED VIA unix_socket; GRANT ALL ON dev.* TO '$USER'@'localhost';"
```

**MongoDB:** AUR-only (`mongodb-bin` <!-- v:mongodb -->8.3.9<!-- /v -->). Versions 8.3.0 to 8.3.12 are inside advisory SERVER-131805 (fixed in 8.3.13); the exposure is low on this single-node loopback instance with no replica set, but move to 8.3.13 or 9.x once an AUR binary exists. The AUR package uses `mongodb.service` and `/etc/mongodb.conf` (`bindIp: 127.0.0.1`), authentication is off, and it needs the ownership drop-in described in chapter 06.

**Valkey:** `sudo pacman -S --needed valkey && sudo systemctl enable --now valkey.service`.

```sh
systemctl is-active postgresql mongodb mariadb valkey
psql -d dev -c 'select current_user, current_database()'
mongosh --quiet --eval 'db.runCommand({ping:1})'
mariadb --protocol=socket dev -e 'select database()'
valkey-cli ping
```

Nginx is installed and stays disabled until a project needs it.

**Firewall:** UFW is active with incoming denied, outgoing allowed and no inbound allow rules on the baseline (optional LAN-scoped examples for KDE Connect and Syncthing are in chapters 18 and 19). Local development services stay loopback-only; if a project needs LAN access, add a narrowly scoped rule and remove it afterwards. To reproduce the baseline on a local workstation (never over remote SSH without the SSH allow rule in place):

```sh
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
sudo ufw status verbose
```

**VPN and DNS:** the Proton VPN daemon runs with no active tunnel, and Mullvad's daemon and early-boot blocker are disabled. Do not enable both clients at once. DNSCrypt Proxy, dnsmasq, Fail2ban, Syncthing and AppArmor profiles are installed but not all enabled; the live inventory is in [`system-summary.md`](../../system-summary.md).

## 4. Rootless Docker

Docker runs as the user service `docker.service`; the system daemon is not used and the account is not in the root-equivalent `docker` group. `docker-rootless-extras` is an AUR package (not in Arch extra or the CachyOS repos). Full prerequisites and networking notes: [chapter 08](setup/08-docker-kubernetes.md).

```sh
sudo pacman -S --needed docker docker-compose docker-buildx rootlesskit
paru -S --needed docker-rootless-extras
grep -q "^$USER:" /etc/subuid /etc/subgid || sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 "$USER"   # needs 65536 IDs
dockerd-rootless-setuptool.sh install           # writes the user unit and selects the `rootless` context
systemctl --user enable --now docker
docker run --rm hello-world
```

Do not enable the system `docker.socket`; it starts a rootful daemon. Lingering (`loginctl enable-linger "$USER"`) is optional if the daemon must run while logged out.

The connected Razer Viper Mini uses OpenRazer. Add the account to the `openrazer` group and sign out and back in once:

```sh
sudo gpasswd -a "$USER" openrazer
```

Then verify `systemctl --user status openrazer-daemon`.

## 5. Local AI and hardware

Ollama uses its ROCm backend for the RX 6700 XT (gfx1031) with the tracked systemd drop-ins from [`../../05-ai/ollama/README.md`](../../05-ai/ollama/README.md). On the packaged Ollama the `HSA_OVERRIDE_GFX_VERSION=10.3.0` override is a fallback; it is needed for PyTorch wheels ([chapter 02](setup/02-amd-gpu-rocm.md)). Confirm backend detection with `journalctl -u ollama | rg 'inference compute'`; loading a model is required to confirm GPU layer placement. GPU monitoring: `amdgpu_top`, `nvtop`, `radeontop`, `rocm-smi`, `sensors`. LACT <!-- v:lact -->0.10.1<!-- /v --> needs its daemon, otherwise the GUI cannot apply settings:

```sh
sudo systemctl enable --now lactd
```

CachyOS already provides active zstd zram swap (about 31 GiB). Inspect `zramctl` before changing its size or compression; do not replace the distribution configuration with an example from elsewhere.

## 6. Desktop defaults and optional applications

Brave is the XDG browser default, Zed opens text and source files, and Swash opens images; the shell config, UWSM environment file and systemd user environment all use `BROWSER=brave`. The optional applications (Upwork, VS Code, Sublime Text, PyCharm, DBeaver, MongoDB Compass, Firefox, Obsidian, Anytype, Logseq OG, Todoist, Slack, Signal, Discord, Telegram, Mailspring, Thunderbird, Zoom, Spotify and the media and office applications) are covered in chapters 12 and 15 to 21 and recorded in the host snapshot.

Upwork's time tracker and screenshot capture are not supported in Wayland sessions according to [Upwork's Linux guide](https://support.upwork.com/hc/en-us/articles/211064108-How-to-troubleshoot-our-desktop-app-Linux); the app launches under Hyprland but hourly tracking needs a supported Xorg session.

The exact enabled and disabled service state and package versions are in [`system-summary.md`](../../system-summary.md); the unattended order of operations for a fresh machine is in [`docs/modernization/HANDOFF.md`](../../docs/modernization/HANDOFF.md).

## Verify

```sh
systemctl is-active postgresql mariadb valkey mongodb
systemctl --user is-active docker
docker context show
```

Expected: `active` for each service and `rootless`. Label: `machine-only`.
