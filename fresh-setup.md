# Fresh CachyOS Setup — AI-Agent Playbook

Use this runbook to rebuild the CachyOS workstation represented by this repo.
It coordinates the detailed chapter guides; it is not a disk image or an
instruction to clone this machine's IDs, keys, passwords, or private data.
The point-in-time hardware, package, service, and runtime inventory is in
[`system-summary.md`](system-summary.md).

## Target profile

- UEFI x86-64 CachyOS workstation, AMD Ryzen 5 5600 and XFX Radeon RX 6700 XT
  (RDNA2/gfx1031), 32 GiB DDR4-3600 RAM.
- One observed 512 GB NVMe with a 4 GiB FAT EFI `/boot` partition and Btrfs
  root/home/log/cache subvolumes. Limine is the active bootloader. The desired
  menu is one primary CachyOS kernel entry only; Windows, extra kernels,
  fallback EFI loaders, and Snapper entries should not appear there. No Windows
  firmware entry was present in the observed UEFI boot order.
- Hyprland + Noctalia, launched through UWSM from greetd with the Noctalia
  greeter. SDDM is installed but inactive. No Plasma session.
- Zsh, Kitty, Starship, development tooling, and an AMD ROCm-backed Ollama
  configuration. See the package lists and chapter guides for the exact scope.
- Configured locale is `en_US.UTF-8` (`LC_TIME=en_US.UTF-8`) and timezone is
  `Asia/Kathmandu`; confirm these with the owner instead of assuming they fit
  a new machine.
- UFW is active with deny-incoming/allow-outgoing policy and no allow rules.
  The Proton VPN daemon is active without a tunnel; Mullvad is installed but
  disabled. Local databases and Ollama listen on loopback.

This is a rolling distribution. Reproduce the profile and configuration, then
install compatible current package versions from the configured CachyOS/Arch
repositories. Do not pin the historical kernel, library, ROCm, Node, or app
versions written in older notes.

## Agent rules and owner checkpoints

1. Start by reading this file, [`README.md`](README.md),
   [`manifest.conf`](manifest.conf),
   [`01-system/cachyos/setup/`](01-system/cachyos/setup/README.md),
   [`01-system/cachyos/packages/`](01-system/cachyos/packages/),
   [`02-desktop/hyprland/README.md`](02-desktop/hyprland/README.md),
   [`05-ai/ollama/README.md`](05-ai/ollama/README.md), and
   [`06-tools/focus/README.md`](06-tools/focus/README.md). Use the chapter
   README files for apps they own.
2. Make a phase checklist. Tell the owner what each phase will change and show
   package transaction plans before installing a large set. Help the owner at
   the keyboard for the installer and firmware screens.
3. **Stop for explicit owner input before** changing partitions, formatting,
   enabling/disabling Secure Boot, enrolling keys, changing boot entries,
   configuring encryption, changing the display manager, enabling remote
   access/firewall rules, initializing a database, or deleting packages/data.
   Give the exact device, path, service, or package list and consequence.
4. Never use `--noconfirm` for pacman, paru, or AUR builds. Never run a blanket
   orphan removal such as `pacman -Rns $(pacman -Qtdq)`. Never replace a
   `.pacnew` without reviewing the diff and preserving local settings.
5. Do not copy `/etc/machine-id`, filesystem UUIDs, SSH keys, Secure Boot
   private keys, browser profiles, tokens, credentials, or service data from
   another host. Restore user secrets only from the owner's chosen backup.
6. Do not enable every service just because a package is installed. Present
   services that bind ports, create databases, filter DNS, expose a UI, or
   consume substantial RAM/GPU, and get the owner's choice before starting
   them. Do not run a destructive reboot or disk operation without the owner's
   explicit go-ahead.
7. Keep a progress note: completed phase, command or file changed, result,
   remaining owner action. If the ISO, hardware, repositories, or repo files
   have changed, adapt and explain the difference instead of forcing stale
   instructions.

## Phase 1 — Prepare and inventory

1. Ask whether this is a blank target or a dual-boot replacement, which disk
   is the target, whether existing Windows/data must remain, whether full-disk
   encryption is wanted, and whether the owner has a verified backup.
2. If the old installation is still available and exact package parity matters,
   capture a reviewed inventory to owner-selected external storage before
   touching the target:

   ```sh
   pacman -Qqe
   pacman -Qm
   flatpak list --app
   systemctl list-unit-files --state=enabled
   systemctl --user list-unit-files --state=enabled
   ```

   Keep this as a comparison aid. Review it: do not blindly reinstall stale,
   machine-specific, orphaned, or secret-bearing app state. Do not add private
   inventories to a public Dotfiles remote without the owner's review.
3. Confirm the new machine's CPU, GPU, memory, disks, UEFI mode, monitor, and
   network. The AMD ROCm override in this repo is specific to the RX 6700 XT;
   do not apply it to a different GPU without checking its supported target.

## Phase 2 — Install CachyOS (owner at the machine)

1. Download the current Desktop ISO (release <!-- v:cachyos-iso -->260809<!-- /v -->) from the
   [official CachyOS download page](https://www.cachyos.org/download/) together
   with its `.sha256` and `.sig` files, then verify them as in the
   [official validation guide](https://wiki.cachyos.org/cachyos_basic/download/).
   Do not use an ISO with a failed or unverified signature/hash.

   ```sh
   sha256sum -c cachyos-desktop-linux-<ISO release>.iso.sha256     # expect: <file>: OK
   gpg --keyserver hkps://keys.openpgp.org --recv-key F3B607488DB35A47
   gpg --verify cachyos-desktop-linux-<ISO release>.iso.sig cachyos-desktop-linux-<ISO release>.iso
   ```

   Expect `Good signature` from "CachyOS" with the primary key fingerprint
   `882D CFE4 8E20 51D4 8E25 62AB F3B6 0748 8DB3 5A47`. gpg also prints that
   the key is not certified; that warning is expected.
2. Boot the installer in UEFI mode. For this profile, choose the single
   "CachyOS Hyprland Noctalia" desktop option (added in the June 2026 release;
   the August 2026 release configures `noctalia-greeter` for it). The installer
   allows one desktop environment per install. If the option is absent, pick
   the minimal option and install the repo's Hyprland packages afterward. Do
   not install Plasma alongside Hyprland just to remove it later.
   <!-- UNVERIFIED: exact installer menu label; the wording comes from the release blog -->
3. Prefer manual partitioning. The owner selects the target disk and confirms
   every partition to create, reuse, preserve, or format. For a Windows
   dual-boot, preserve Windows partitions and its EFI partition; install
   CachyOS into its own selected space/EFI partition. Never infer a device
   name from an earlier machine. The current profile uses UEFI/GPT, Btrfs,
   and a separate CachyOS EFI partition.
4. **Encryption decision:** the current root filesystem is Btrfs without a
   LUKS layer. Ask whether to match that or intentionally change it. LUKS must
   be selected during installation; do not improvise it after the OS is
   installed.
5. Select Limine, which is the bootloader used on this profile (the installer
   default since the January 2026 release; the boot partition needs at least
   4 GiB). Secure Boot is disabled on the current host. Match that state unless
   the owner explicitly chooses otherwise; if enabling it, follow the current
   [CachyOS Secure Boot guide](https://wiki.cachyos.org/configuration/secure_boot_setup/)
   and create new keys for this machine. Never copy signing private keys from
   another host. The Limine-specific points of that guide:

   ```sh
   sudo pacman -S sbctl
   sudo sbctl create-keys
   sudo sbctl enroll-keys --microsoft            # Gigabyte boards (this host is a B550 GAMING X V2); other boards: add --firmware-builtin
   # Limine 11.2 and newer enforce BLAKE2B hashes of the config and paths:
   #   set ENABLE_ENROLL_LIMINE_CONFIG=yes in /etc/default/limine, append the
   #   splash hash (b2sum /boot/limine-splash.png) after '#', then:
   sudo limine-enroll-config && sudo limine-update
   sudo sbctl status && sudo sbctl verify          # only the Limine EFI binary needs signing
   ```

   CachyOS-Settings documents `sbctl-batch-sign` as incompatible with Limine;
   follow the Limine section of the guide, not the generic flow.
6. Set the user name, password, keyboard, locale, and timezone with the owner.
   Do not set autologin. Finish the installer and let the owner perform the
   first boot.

## Phase 3 — First boot and base system

1. Verify network access, the root filesystem, boot mode, and that the owner
   can log in from a TTY or the installer-selected desktop. Record:

   ```sh
   cat /etc/os-release
   uname -r
   lsblk -f
   findmnt /
   lspci -nnk
   ```

2. Update the base CachyOS system interactively and reboot only with owner
   approval if the kernel/bootloader changed:

   ```sh
   sudo pacman -Syu
   ```

   Do not start a second package manager while this transaction is active.
3. Set up an AUR helper. The June 2026 installer no longer ships `paru`
   (it recommends Shelly), so a fresh install has none:
   `sudo pacman -S paru` installs the CachyOS build
   (<!-- v:paru -->2.1.0<!-- /v -->). `yay` is the fallback.
   AUR packages are community build recipes: inspect the selected package and
   build prompts, and review every PKGBUILD and install-script change. Arch
   news of 2026-06-12 reports an incident with malicious AUR packages. Keep Hyprland and its runtime libraries on compatible stable
   packages. In particular, do not install `aquamarine-git`,
   `hyprgraphics-git`, `hyprutils-git`, or `hyprlang-git` alongside stable
   Hyprland; that combination produced the dependency warnings this guide is
   intended to prevent.
4. Install the repository's desktop, system, font, CLI, and focus dependency lists.
   The commands below separate official-repository packages from AUR
   packages, including entries marked `(AUR)` in the files. Review the plan
   and confirm each transaction with the owner. If the checkout is not present
   yet, clone it after agreeing on the remote and authentication method:

   ```bash
   git clone git@github.com:karkinirajan/dotfiles.git ~/dotfiles
   cd ~/dotfiles
   package_files=(01-system/cachyos/packages/desktop.txt \
     01-system/cachyos/packages/system.txt \
     01-system/cachyos/packages/fonts.txt \
     01-system/cachyos/packages/cli.txt \
     06-tools/focus/packages.txt)
   mapfile -t repo_packages < <(awk 'NF && $1 !~ /^#/ && $2 != "(AUR)" {print $1}' "${package_files[@]}")
   mapfile -t aur_packages < <(awk 'NF && $1 !~ /^#/ && $2 == "(AUR)" {print $1}' "${package_files[@]}")
   sudo pacman -S --needed "${repo_packages[@]}"
   if ((${#aur_packages[@]})); then
     aur_helper="$(command -v paru || command -v yay || true)"
     if [[ -z "$aur_helper" ]]; then
       echo "Install paru or yay before installing AUR packages" >&2
       exit 1
     fi
     "$aur_helper" -S --needed "${aur_packages[@]}"
   fi
   ```

5. For the full developer/AI workstation, review the complete package and
   service choices in `01-system/cachyos/setup/` chapter by chapter. To
   reproduce the optional full-stack profile, use
   [`01-system/cachyos/dev-stack.md`](01-system/cachyos/dev-stack.md) and its
   `packages/developer.txt` list. Keep project frameworks in project-local
   environments, initialize databases before use, and run Docker rootless.
   The Upwork package is built from the tracked bundled-runtime PKGBUILD; its
   screenshot time tracking requires a supported Xorg session rather than
   Wayland. To
   match the local AI part of this profile, include
   `01-system/cachyos/packages/ai.txt` for the Ollama/ROCm stack; it is
   GPU- and disk-intensive. Ask before downloading large models. The guide's
   package catalog includes optional applications and services. Use the
   package manifests for the baseline; choose optional packages individually
   and initialize each selected database/service as its own step.

   After confirming that the GPU matches the RX 6700 XT profile, install its
   listed repository packages interactively:

   ```bash
   mapfile -t ai_packages < <(awk 'NF && $1 !~ /^#/ && $2 != "(AUR)" {print $1}' \
     01-system/cachyos/packages/ai.txt)
   sudo pacman -S --needed "${ai_packages[@]}"
   ```

## Phase 4 — Apply Dotfiles

1. Use the checkout created in Phase 3. If its remote is private, have the
   owner provide authentication; do not put credentials in commands, shell
   history, or this repo.
2. Preview the manifest before changing user configuration. Existing files
   will be backed up by the installer; inspect the backup plan with the owner:

   ```sh
   cd ~/dotfiles
   ./install.sh --dry-run
   ```

3. After owner review, install and reconcile the manifest, then require a clean
   status report before moving on:

   ```sh
   ./install.sh
   ./install.sh status
   ```

   `install.sh` handles the user-level links and seeded app settings. It does
   not install packages or privileged `/etc` files.
4. Follow [`02-desktop/hyprland/README.md`](02-desktop/hyprland/README.md) for
   remaining Hyprland steps, D-Bus notification override, Noctalia state, and
   plugins. Use the checked-in paths under `01-system/cachyos/packages/`, not
   old `os/cachyos/packages/` paths. Test plugins against the installed
   Hyprland version before enabling them.

## Phase 5 — Boot, login, and recovery configuration

### Display manager (`greetd` + Noctalia greeter) and optional SDDM preset

1. The active profile uses **`greetd` with `noctalia-greeter`**, launching
   Hyprland through UWSM (`uwsm start -- hyprland.desktop`). Confirm `greetd`,
   `noctalia-greeter`, `uwsm`, Hyprland, and `xdg-desktop-portal-hyprland` are
   installed. The greeter wiring (from the
   [Noctalia greeter docs](https://docs.noctalia.dev/greeter/installation/)):
   greetd must launch `noctalia-greeter-session` (not `noctalia-greeter`).
   Merge, do not overwrite, `/etc/greetd/config.toml`:

   ```toml
   [default_session]
   command = "/usr/bin/noctalia-greeter-session"
   user = "greeter"
   ```

   ```sh
   sudo systemd-tmpfiles --create noctalia-greeter.conf
   sudo noctalia-greeter-apply-appearance --setup-system
   systemctl status display-manager.service        # name the current display manager
   sudo systemctl disable --now sddm.service        # or whichever unit the line above names
   sudo systemctl enable --now greetd.service
   readlink -f /etc/systemd/system/display-manager.service   # expect .../greetd.service
   ```

2. SDDM is installed as an **inactive fallback**. The tracked SDDM preset under
   `02-desktop/hyprland/sddm/` can be staged into `/etc/sddm.conf.d/` and
   `/usr/local/share/wayland-sessions/`, but do **not** enable `sddm.service`
   over `greetd.service` unless the owner explicitly asks to switch display
   managers:

   ```sh
   cd ~/dotfiles
   sudo install -Dm644 02-desktop/hyprland/sddm/hyprland.conf \
     /etc/sddm.conf.d/hyprland.conf
   sudo install -Dm644 02-desktop/hyprland/sddm/sessions/hyprland-uwsm.desktop \
     /usr/local/share/wayland-sessions/hyprland-uwsm.desktop
   ```

3. After logging in through the active greeter (`greetd` + Noctalia greeter),
   check the active session, compositor config, portals, and logs. Require zero
   Hyprland config errors and a usable terminal before considering the login
   setup complete. Do not troubleshoot a session crash by deleting user state
   or disabling security modules without evidence.

### Limine, CachyOS, and snapshots

1. Use Limine as the only boot manager. Keep one top-level CachyOS entry for
   the primary `linux-cachyos` kernel. Do not install secondary kernels or add
   Windows, generic fallback EFI loaders, or Snapper snapshot entries to this
   machine's menu. Snapper may retain snapshots for rollback without adding
   them as boot choices.
2. Before editing a live Limine menu, back up `/boot/limine.conf` and inspect
   it with `sudo limine-list`. Check the effective settings in
   `/etc/default/limine` and `/etc/limine-entry-tool.conf`; turn off fallback
   loader discovery (`FIND_BOOTLOADERS="no"`; `BOOT_ORDER` only orders entries,
   it does not hide them) and disable `limine-snapper-sync.service` when the
   menu is intentionally single-entry. Use `limine-entry-tool` to remove specific
   stale paths, preserve the currently booted CachyOS kernel and its initramfs,
   then run `sudo limine-update` and confirm `sudo limine-list` shows exactly
   the primary CachyOS entry before rebooting. Also read the generated
   `cmdline:` line in `/boot/limine.conf`: it must still carry `root=` and
   `rootflags=` (and `lsm=` if AppArmor is enabled), because
   `KERNEL_CMDLINE[default]+=` in `/etc/default/limine` replaces the
   inherited command line when no base line is defined there. Limine 12.9.5
   changed `default_entry:` numbering (entries start at 1); the path form
   `default_entry: CachyOS/linux-cachyos` is unaffected.
3. Do not alter UEFI NVRAM entries or overwrite `EFI/BOOT/BOOTX64.EFI` as part
   of menu cleanup. The current firmware has a Limine entry and a generic UEFI
   OS fallback entry, with no Windows entry observed. Confirm the owner wants
   firmware-level entries removed before changing them.
4. Configure Snapper and its current Limine integration as described in
   `01-system/cachyos/setup/20-maintenance-monitoring.md` only after checking the actual filesystem
   layout and current package hooks. Keep snapshot entries out of the target
   single-entry boot menu. Take and verify a snapshot before large system
   changes. Never run `btrfs check --repair` as routine maintenance.

## Phase 6 — Privileged integrations and user services

Install only after their package and firewall/service plans are reviewed:

- **Ollama/ROCm:** follow [`05-ai/ollama/README.md`](05-ai/ollama/README.md).
  This host's backend override is specific to its RX 6700 XT. Validate GPU
  inference with a small model before downloading large models. Never restore
  model cache files unless requested.
- **Nginx:** install
  [`07-networking/nginx/conf.d/00-types-hash.conf`](07-networking/nginx/conf.d/00-types-hash.conf)
  into `/etc/nginx/conf.d/`, ensure `/etc/nginx/nginx.conf` includes
  `include conf.d/*.conf;` inside `http { ... }`, run `sudo nginx -t`, then
  enable/reload only if nginx is intended to run on the new machine.
- **DNS filtering/encrypted DNS:** follow `06-tools/focus/README.md` and
  section 19.5 of `01-system/cachyos/setup/19-security-privacy.md`. Review NetworkManager,
  dnsmasq, dnscrypt-proxy, `/etc/resolv.conf`, and local listening ports as one
  plan before changing DNS; test name resolution and have a rollback ready.
- **SSH:** install the user unit from
  [`07-networking/ssh/README.md`](07-networking/ssh/README.md) only if the
  owner has configured its host alias in `~/.ssh/config`. The private key is
  supplied by the owner and is never part of this repo. Check the unit's
  journal after startup; no rapid restart loop should remain.
- **Databases, Docker, UFW/Fail2ban, Syncthing, focus services, and other
  daemons:** use their chapter instructions, initialize required state,
  then enable only the selected services. For a remotely administered host,
  prove SSH access and firewall rules before enabling a deny-incoming policy.

Do not copy the old DNSCrypt `.pacnew` over the working file without comparing
it. Preserve the selected upstream servers, local port, and dnsmasq forwarding
relationship when configuring a new machine.

## Phase 7 — Applications, development tools, and updates

1. Use the app chapters in `01-system/cachyos/setup/` as the catalog for the
   full profile: Python/uv, Node/pnpm, editors, browsers, databases, Docker and
   Kubernetes, cloud CLIs, media and office apps. Show the owner a grouped
   install plan. Resolve renamed/unavailable packages through current official
   package metadata; do not silently substitute an AUR build.
2. Install topgrade (`topgrade-bin` from the AUR) and use the tracked config.
   `assume_yes = false` is intentional: dependency conflicts must remain
   visible for owner review. Run a dry run, then update interactively and
   inspect any `.pacnew` files. Do not update Git working trees automatically
   while this Dotfiles checkout has unreviewed changes:

   ```sh
   paru -S --needed topgrade-bin
   topgrade --dry-run
   ```

   Then run `topgrade` interactively and review package removals before
   accepting them.
3. If pnpm falls back to Node because its native executable was skipped, use
   the official `pnpm self-update` flow; do not globally allow every package's
   install scripts to run.
4. Install and configure applications according to their dedicated README
   files. Do not log into personal accounts or sync private browser, cloud,
   password-manager, IDE, or AI-provider state without the owner present.

## Phase 8 — Final acceptance checklist

Have the owner participate in the final login/reboot checkpoint. Before that,
collect evidence for each item and report any mismatch instead of declaring
the setup finished:

- `./install.sh status` reports no missing or drifting entries; all expected
  packages are installed and there are no unresolved dependency warnings.
- `sudo systemctl --failed --no-pager` has no failed units. Every enabled
  network, database, GPU, and desktop service is intentional and starts cleanly.
- `greetd` + Noctalia greeter presents the managed UWSM Hyprland session,
  autologin is off, Hyprland has no config errors, and the
  portal/lock/polkit/session services work.
- `sudo limine-list` shows exactly one primary CachyOS kernel entry. The
  generated config points to existing kernel/initramfs files; there are no
  Windows, secondary-kernel, fallback-loader, or snapshot entries.
- AMD driver and Vulkan are recognized. For an AMD AI setup, `rocminfo` sees
  the GPU and Ollama actually places layers on the GPU before any large-model
  download.
- Btrfs/Snapper snapshots work and the storage device reports healthy SMART
  status. Use a read-only Btrfs scrub for an integrity check; do not reset
  historical counters or run repair commands to make a report look clean.
- Nginx passes `nginx -t` if installed. DNS resolves through the intended
  resolver chain if DNS filtering/encryption is enabled. SSH and firewall
  changes leave the owner with a verified way back in.
- Update tools finish without dependency removals, failed app managers, or
  unreviewed config replacements. Record unresolved firmware, hardware, or
  application-specific warnings with their log evidence.

Only after the checklist passes should the owner approve rebooting into the
installed system and testing another login. Confirm Snapper rollback remains
available independently of the boot menu.
