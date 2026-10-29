---
title: Handoff for the machine session
topic: handoff
last_verified: 2026-10-29
status: archived
---

# Handoff for the machine session

> **Completed 2026-10-29; kept as a record.** Every step ran on the machine. Do not re-run S02: the Hyprland hold was lifted the same day, when the machine moved to 0.57.0 on the Lua config ([`lua-migration.md`](../../02-desktop/hyprland/lua-migration.md)).

This file lets a separate session apply the modernized repo to the owner's existing CachyOS machine in full-auto mode. The cloud session that wrote it changed nothing on the machine and checked nothing against it. Every step below is `machine-only`: it has not been run on the host.

This file supersedes the owner-checkpoint prose of [`fresh-setup.md`](../../fresh-setup.md) for this run. `fresh-setup.md` still applies to a blank-disk install.

## 0. Read before starting

**Scope.** This is a convergence run on a machine that already works, not a reinstall. Do not partition, format, change Secure Boot, enrol keys, edit `/boot/limine.conf` or `/etc/default/limine`, change the display manager, or delete data. The steps below are the complete list of changes.

**Two standing rules in the owner's `05-ai/claude-code/CLAUDE.md` collide with an unattended run:**

1. "Never run `sudo` yourself." Every privileged step below is marked `sudo`. Either the owner runs them (the session hands over each command) or the owner lifts the rule for this session before it starts. Without one of these the session stops at S01.
2. "Never run `git push`, `pull` or `fetch`." Step S00 is therefore a hand-off command for the owner to type.

**Commit rule.** Any commit the session makes carries no AI attribution of any kind (no `Co-Authored-By`, no session link, no "Generated with" footer). Author `karkinirajan`.

**Never** use `--noconfirm` on pacman or paru. Answer the `[Y/n]` prompts after reading the plan. Never run a blanket orphan removal.

**Stop conditions.** Stop and report, without trying a workaround, if: `pacman -Syu` reports a file conflict or a broken dependency; `hyprctl configerrors` prints anything after S09; `./install.sh status` shows `DRIFT` on a `link` entry; any step below prints something other than its expected output.

## 1. Facts the run depends on

Versions come from [`versions.yaml`](../../versions.yaml); the plain numbers below were read from it on 2026-10-29.

### Compatibility constraints

| Constraint | Meaning for this run |
|---|---|
| `hyprland-hold` (replaced by `hyprland-lua` after the run) | Hyprland 0.57.0 (Arch `extra`) removed the hyprlang `.conf` parser; with only `hyprland.conf` it ignores `hypr/config/` and writes a default Lua config. CachyOS repos, which come first in pacman's order, still carry 0.56.2. Hold `hyprland` and `hyprpm` with `IgnorePkg` (S02) until a Lua config is validated ([`lua-migration.md`](../../02-desktop/hyprland/lua-migration.md)) |
| `rocm-pytorch-index` | ROCm is the legacy 7.2 train (7.2.4). PyTorch wheels must come from the `rocm7.2` index. Upstream's new "ROCm Core SDK" 10.1.0 is not packaged by Arch; do not install it |
| `pgvector-pg18` | pgvector 0.8 supports PostgreSQL 18 |
| `ts-eslint` | Use TypeScript 6.x for tooling; `typescript@latest` is 7.0.2 and `typescript-eslint` rejects it |
| `next-patched` | Next.js below 16.4.1 has a Critical RCE; the frontend templates pin 16.4.3 |
| `node-for-prisma` | Prisma 7 needs Node 20.19 or newer; Node 26 is current LTS |
| `python-uv-managed` | System Python is 3.14.8. Open WebUI via pip needs Python below 3.13: run it with `uvx --python 3.12` |

### Upstream versus distro gaps (installed version wins, upstream recorded)

| Package | Machine gets | Upstream | Note |
|---|---|---|---|
| hyprland | 0.56.2 (CachyOS) | 0.57.0 | Held, see above |
| ROCm | 7.2.4 | Core SDK 10.1.0 | Not packaged by Arch |
| ollama | 0.40.11 | 0.40.13 | Repo package; do not use the upstream installer |
| pnpm | 12.15.0 | 12.16.1 | Pacman copy is fine |
| Thunderbird | 158.0.1 | 159.0 | Arch lags a few days |
| CopyQ | 16.0.0 | 17.0.0 | Optional app |
| Bitwarden desktop | 2026.3.1 | 2026.10.1 | Arch lags seven months; browser extension is current |
| Mailspring | 1.23.0 (CachyOS repo) | 1.26.2 (AUR) | The machine runs the AUR build; do not downgrade |
| Brave | 1.98.60 (CachyOS repo) | 1.98.62 (AUR) | Either works |
| `mongodb-bin` | 8.3.9 | 9.0; 8.3.13 fixes SERVER-131805 | Loopback single node, low exposure; no AUR binary of a fixed version yet |
| `xdg-desktop-portal-hyprland` | 1.4.1 | 1.5.0 in `extra-testing` | Stay on `extra` |
| MariaDB | 13.0.2 installed | 12.3.3 LTS recommended | The installed data directory cannot be downgraded; see S05 |

### Per-machine decisions already made (defaults for the unattended run)

| Topic | Default | Why |
|---|---|---|
| MariaDB | Keep installed `mariadb` 13.0.2; do not install `mariadb-lts` | `mariadb` and `mariadb-lts` conflict and a 13.0 data directory cannot go back to 12.3 |
| Mullvad | Keep installed `mullvad-vpn-bin` and `mullvad-vpn-daemon-bin`; do not install `mullvad-vpn` | The packages conflict. Switching to the `extra` package is optional and needs the daemon stopped |
| Logseq | Keep `logseq-desktop-bin`; do not install `logseq-og-bin` | Both own the same app name; the owner picks |
| Hyprland Lua port | Not applied | Needs a live compositor; documented only |
| Zed local model | Not changed | `deepseek-v4-flash:cloud` is retired; choosing a replacement is the owner's call |
| Starship glyphs | Restored after the run | From `starship preset nerd-font-symbols` and Starship defaults |
| Limine, Secure Boot | Not touched | Out of scope for a convergence run |

## 2. Steps

Run in order. Each step is idempotent. Paths are relative to `~/dotfiles`.

### S00. Get the branch (owner types)

```bash
cd ~/dotfiles && git fetch origin modernize/2026-10 && git switch modernize/2026-10
```

Expected: the branch checks out; `git log -1 --format='%an'` prints `karkinirajan`. If the owner merged the pull request instead, `git switch master && git pull` gives the same tree.

### S01. Snapshot first

```bash
sudo snapper -c root create -d "pre-modernize-2026-10"
sudo snapper -c root list | tail -3
```

Expected: a new numbered snapshot with the description above. If Snapper has no `root` config, stop; do not continue without a restore point.

### S02. Hold Hyprland (before any upgrade)

```bash
grep -q '^IgnorePkg.*hyprland' /etc/pacman.conf || sudo sed -i '/^#IgnorePkg/a IgnorePkg = hyprland hyprpm' /etc/pacman.conf
pacman-conf IgnorePkg
pacman -Q hyprland hyprpm
```

Expected: `pacman-conf` prints `hyprland` and `hyprpm`; `pacman -Q` prints `hyprland 0.56.2-4.1` (the exact pkgrel may differ) and a matching `hyprpm`. If `pacman -Q hyprland` already shows 0.57.x, stop: the config tree is not read; follow [`lua-migration.md`](../../02-desktop/hyprland/lua-migration.md) before anything else.

### S03. Mirrors

```bash
sudo cachyos-rate-mirrors
systemctl list-timers cachyos-rate-mirrors.timer
pacman-conf --repo-list | head -8
```

Expected: the timer is listed with a next run on the 1st, 11th or 21st; the repo list starts with `cachyos-v3`, `cachyos-core-v3`, `cachyos-extra-v3`, `cachyos`, then Arch repos. Do not install `reflector`. If the `cachyos` repositories are missing, stop.

### S04. Full system upgrade

```bash
sudo pacman -Syu
```

Expected: a plan that ignores `hyprland` and `hyprpm` ("ignoring package upgrade") only if a newer build exists; no file conflicts. Review any `.pacnew` with `pacdiff` and keep local settings. If pacman reports that an upgrade "breaks dependency" of the held `hyprland`, stop and report which library; do not remove the hold to force it.

### S05. Packages, conflict-aware

Install the tracked lists, skipping names whose conflicting counterpart is already installed. AUR builds use `--needed` and are reviewed by the owner's existing trust in these maintainers; use `paru --skipreview` only if the owner approved that for this run.

```bash
cd ~/dotfiles
files=(01-system/cachyos/packages/desktop.txt 01-system/cachyos/packages/system.txt
  01-system/cachyos/packages/fonts.txt 01-system/cachyos/packages/cli.txt
  01-system/cachyos/packages/developer.txt 01-system/cachyos/packages/ai.txt
  06-tools/focus/packages.txt)
skip=()
pacman -Q mariadb >/dev/null 2>&1 && skip+=(mariadb-lts)
pacman -Q mullvad-vpn-bin >/dev/null 2>&1 && skip+=(mullvad-vpn)
pacman -Q logseq-desktop-bin >/dev/null 2>&1 && skip+=(logseq-og-bin)
filter() { awk -v s="${skip[*]}" 'BEGIN{n=split(s,a," "); for(i=1;i<=n;i++) k[a[i]]=1} NF && $1 !~ /^#/ && !($1 in k)'; }
mapfile -t repo_packages < <(cat "${files[@]}" | filter | awk '$2 != "(AUR)" {print $1}')
mapfile -t aur_packages  < <(cat "${files[@]}" | filter | awk '$2 == "(AUR)" {print $1}')
printf 'skipping: %s\n' "${skip[*]:-none}"
sudo pacman -S --needed "${repo_packages[@]}"
"$(command -v paru || command -v yay)" -S --needed "${aur_packages[@]}"
```

Expected: `skipping: mariadb-lts mullvad-vpn logseq-og-bin` on the current machine, then `there is nothing to do` for most packages and a short list of genuinely new or changed ones. `docker-machine` and `notion-app-enhanced` are no longer listed and stay installed until the owner removes them. `ollama-rocm` and `ollama-vulkan` come from `ai.txt`. A package that does not resolve is a stop condition.

### S06. Apply the dotfiles

```bash
cd ~/dotfiles
./install.sh --dry-run
./install.sh
./install.sh status
zsh -n ~/.zshrc
```

Expected: the dry run lists only changes; `status` exits 0 with every `link` entry `ok`; it exits 1 on link drift, a missing entry or an error. A `seed` entry may report `DRIFT` (counted as `seed-drift`): that is the live file moving ahead, not an error; run `./install.sh pull` only if the owner wants it captured. A real file in the way is moved to `<path>.bak-<timestamp>`. `zsh -n` prints nothing.

### S07. Reload the compositor config

```bash
hyprctl reload
hyprctl configerrors
```

Expected: `configerrors` prints nothing or `no errors`. Anything else is a stop condition. The session must not log out or restart Hyprland.

### S08. Ollama on ROCm

```bash
cd ~/dotfiles/05-ai/ollama
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo cp systemd/claude-code.conf /etc/systemd/system/ollama.service.d/
sudo cp systemd/backend-rocm.conf /etc/systemd/system/ollama.service.d/backend.conf
sudo cp bin/ollama-backend /usr/local/sbin/ollama-backend && sudo chmod 755 /usr/local/sbin/ollama-backend
sudo systemctl daemon-reload && sudo systemctl restart ollama
journalctl -u ollama -b --no-pager | rg 'inference compute'
```

Expected: a line with `library=ROCm` and `total="12.0 GiB"`. Do not apply `setcap cap_perfmon` or the setcap hook: they are for the Vulkan backend only. Do not download a model. To prove GPU use, the owner loads a small model and checks `ollama ps` for `100% GPU`.

### S09. LACT daemon

```bash
sudo systemctl enable --now lactd
systemctl is-active lactd
```

Expected: `active`.

### S10. Focus nftables table (idempotent reload)

The repo renamed the table from `inet filter` to `inet focus` and made the file reload-safe.

```bash
cd ~/dotfiles
sudo install -d -m 755 /etc/nftables.d
sudo cp 06-tools/focus/nftables/focus-filter.nft /etc/nftables.d/focus-filter.nft
sudo nft list tables
```

If the output lists `table inet filter` and `sudo nft list table inet filter` shows a set named `blocked_ips`, that is the old focus table: remove it with `sudo nft delete table inet filter`. If `inet filter` does not contain `blocked_ips`, leave it alone. Then:

```bash
sudo nft -f /etc/nftables.d/focus-filter.nft
sudo nft -f /etc/nftables.d/focus-filter.nft
sudo nft list chain inet focus output | rg -c 'reject'
```

Expected: loading twice succeeds and the count of `reject` rules is `2` (not 4: one IPv4 and one IPv6 rule). Do not enable the focus services; focus mode is the owner's switch.

### S11. Verify, read only

```bash
systemctl is-active postgresql mariadb valkey mongodb ollama ufw
systemctl --user is-active docker
docker context show
psql -d dev -c 'select current_user, current_database()'
mongosh --quiet --eval 'db.runCommand({ping:1})'
mariadb --protocol=socket dev -e 'select database()'
valkey-cli ping
sudo ufw status verbose | head -4
hyprctl version | head -2
pacman -Q hyprland ollama rocm-hip-sdk nodejs python
./install.sh status
```

Expected: `active` for each service and the user Docker unit; `rootless` for the context; the `dev` database answers; `PONG`; UFW `Status: active` with `Default: deny (incoming), allow (outgoing)`; Hyprland 0.56.x; Node 26.x, Python 3.14.x.

## 3. What the run must not do

- Run `initdb`, `mariadb-install-db` or any database initialization: the data directories exist. The scripts in chapter 06 and `dev-stack.md` are for a blank machine. On a fresh machine PostgreSQL 18 needs `--auth-local=peer --auth-host=scram-sha-256`, because its `initdb` default is `trust`.
- Switch MariaDB, Mullvad or Logseq packages (see the defaults table).
- Enable `docker.socket`, `mullvad-daemon`, `mullvad-early-boot-blocking`, focus services, Nginx or Fail2ban. The focus scripts and units hardcode `/home/kneeraazon`; they are root-run and would create that path on a differently named account.
- Run the AppArmor kernel-parameter step (chapter 19.7) or the Limine single-entry procedure (chapter 20.1); both edit the boot command line and are out of scope for a convergence run.
- Install the upstream Ollama script, the ROCm Core SDK, or `reflector`.
- Run the Hyprland Lua port or `hyprpm update` against a newer Hyprland.

## 4. Rollback

| Change | Undo |
|---|---|
| Any package or config change | `sudo snapper -c root list`, then `sudo snapper -c root undochange <pre-snapshot>..0` for files, or boot the snapshot from Limine if the session no longer starts |
| Dotfile links | Files replaced by the installer are at `<path>.bak-<timestamp>`; `./install.sh restore` re-applies the repo version, `git checkout master` and `./install.sh` returns the old tree |
| Hyprland hold | Remove the `IgnorePkg = hyprland hyprpm` line from `/etc/pacman.conf` only after a Lua config is validated |
| Ollama drop-ins | Delete `/etc/systemd/system/ollama.service.d/backend.conf` and `claude-code.conf`, `daemon-reload`, restart |
| Focus table | `sudo nft delete table inet focus` |

## 5. Open items for the owner

These stay open after the run and are listed with the full set in [`REPORT.md`](REPORT.md): the Hyprland Lua config port; the Zed default-model replacement; the `claude-brain` hooks, which cannot be verified from public sources; and the claims tagged `<!-- UNVERIFIED -->` in the chapters.
