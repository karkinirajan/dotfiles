# Fresh CachyOS Setup — AI-Agent Playbook

Use this runbook to rebuild the CachyOS workstation represented by this repo.
It coordinates the detailed chapter guides; it is not a disk image or an
instruction to clone this machine's IDs, keys, passwords, or private data.

## Target profile

- UEFI x86-64 CachyOS workstation, AMD Ryzen 5 5600 and Radeon RX 6700 XT
  (RDNA2/gfx1031), 32 GiB RAM.
- Btrfs root with Snapper snapshots; GRUB; Windows kept as a boot option when
  dual-booting. The current installation has a separate CachyOS EFI partition.
- Hyprland + Noctalia, launched through UWSM from SDDM. No Plasma session and
  no passwordless autologin. SDDM's greeter uses X11.
- Zsh, Kitty, Starship, development tooling, and an AMD ROCm-backed Ollama
  configuration. See the package lists and chapter guides for the exact scope.
- Current locale is `en_US.UTF-8` (`LC_TIME=C.UTF-8`) and timezone is
  `Asia/Kathmandu`; confirm these with the owner instead of assuming they fit
  a new machine.

This is a rolling distribution. Reproduce the profile and configuration, then
install compatible current package versions from the configured CachyOS/Arch
repositories. Do not pin the historical kernel, library, ROCm, Node, or app
versions written in older notes.

## Agent rules and owner checkpoints

1. Start by reading this file, [`README.md`](README.md),
   [`manifest.conf`](manifest.conf),
   [`01-system/cachyos/setup.md`](01-system/cachyos/setup.md),
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

1. Download the current Desktop ISO from the
   [official CachyOS download page](https://www.cachyos.org/download/) and
   verify its published checksum/signature using the
   [official validation guide](https://wiki.cachyos.org/cachyos_basic/download/).
   Do not use an ISO with a failed or unverified signature/hash.
2. Boot the installer in UEFI mode. For this profile, choose one desktop
   environment only: Hyprland if offered, otherwise the minimal option and
   install the repo's Hyprland packages later. Do not install Plasma alongside
   Hyprland just to remove it afterward.
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
5. Select GRUB for this profile. Secure Boot had to be disabled to install on
   the current setup, then was re-enabled with owner-enrolled custom keys and
   a signed GRUB binary. Have the owner handle the firmware/key enrollment
   screens and follow the current
   [CachyOS Secure Boot guide](https://wiki.cachyos.org/configuration/secure_boot_setup/).
   Generate new keys for the new machine; never copy signing private keys from
   another host. If the owner does not want to do this now, leave Secure Boot
   in its agreed state and document that difference.
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
3. Set up `paru` using a current, reviewed CachyOS/Arch-supported method.
   AUR packages are community build recipes: inspect the selected package and
   build prompts. Keep Hyprland and its runtime libraries on compatible stable
   packages. In particular, do not install `aquamarine-git`,
   `hyprgraphics-git`, `hyprutils-git`, or `hyprlang-git` alongside stable
   Hyprland; that combination produced the dependency warnings this guide is
   intended to prevent.
4. Install the repository's core desktop and font package lists. The commands
   below separate official-repository packages from AUR packages, including
   entries marked `(AUR)` in the files. Review the plan and confirm each
   transaction with the owner. If the checkout is not present yet, clone it
   after agreeing on the remote and authentication method, then enter it:

   ```bash
   git clone git@github.com:karkinirajan/dotfiles.git ~/dotfiles
   cd ~/dotfiles
   mapfile -t repo_packages < <(awk 'NF && $1 !~ /^#/ && $2 != "(AUR)" {print $1}' \
     01-system/cachyos/packages/desktop.txt 01-system/cachyos/packages/fonts.txt)
   mapfile -t aur_packages < <(awk 'NF && $1 !~ /^#/ && $2 == "(AUR)" {print $1}' \
     01-system/cachyos/packages/desktop.txt 01-system/cachyos/packages/fonts.txt)
   sudo pacman -S --needed "${repo_packages[@]}"
   if ((${#aur_packages[@]})); then
     paru -S --needed "${aur_packages[@]}"
   fi
   ```

5. For the full developer/AI workstation, review the complete package and
   service choices in `01-system/cachyos/setup.md` chapter by chapter. To
   match the local AI part of this profile, include
   `01-system/cachyos/packages/ai.txt` for the Ollama/ROCm stack; it is
   GPU- and disk-intensive. Ask before downloading large models. The guide's
   historical bulk command has `--noconfirm`, stale package names, optional
   applications, and a blanket service enable list: **do not run it as
   written**. Translate current, owner-selected packages to interactive
   transactions and initialize each chosen database/service as its own step.

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

### SDDM and UWSM session

1. Install the tracked config and only the managed session entry:

   ```sh
   cd ~/dotfiles
   sudo install -Dm644 02-desktop/hyprland/sddm/hyprland.conf \
     /etc/sddm.conf.d/hyprland.conf
   sudo install -Dm644 02-desktop/hyprland/sddm/sessions/hyprland-uwsm.desktop \
     /usr/local/share/wayland-sessions/hyprland-uwsm.desktop
   ```

2. Ensure `uwsm`, Hyprland, SDDM, and the Hyprland portal are installed. Keep
   autologin disabled. Before making SDDM the only display manager, confirm the
   unit symlink and test the managed session from the current login/TTY. If
   changing display managers, inspect `display-manager.service` and show the
   owner the old/new targets before switching. After the owner approves the
   change, enable SDDM and verify the resulting symlink:

   ```sh
   sudo systemctl enable sddm.service
   readlink -f /etc/systemd/system/display-manager.service
   ```

   Confirm that the link resolves to SDDM. If it points to another display
   manager or the enable command reports a conflict, stop and fix that with the
   owner before disabling anything.
3. After logging in through SDDM, check the active session, compositor config,
   portals, and logs. Require zero Hyprland config errors and a usable terminal
   before considering the login setup complete. Do not troubleshoot a session
   crash by deleting user state or disabling security modules without evidence.

### GRUB, Windows, and snapshots

1. Install the tracked defaults and inspect the bootloader before regenerating
   the menu:

   ```sh
   cd ~/dotfiles
   sudo pacman -S --needed linux-cachyos linux-cachyos-lts
   sudo install -Dm644 01-system/cachyos/grub/default /etc/default/grub
   ```

   Preserve Windows detection only if Windows exists. Ensure the Btrfs
   snapshot tooling is installed/configured per setup.md. The target menu is
   three top-level choices (CachyOS main kernel, CachyOS LTS kernel, and
   Windows when installed) plus one `CachyOS Snapshots (Recovery)` submenu.
   There should be no duplicate snapshot menu or extra Advanced Options
   submenu. If `/etc/grub.d/41_snapshots-btrfs` creates duplicate snapshot
   entries, inspect it and disable that duplicate generator only; keep the
   CachyOS snapshot proxy.
2. Generate and validate the GRUB menu before rebooting:

   ```sh
   sudo grub-mkconfig -o /boot/grub/grub.cfg
   sudo grub-script-check /boot/grub/grub.cfg
   ```

   Review the generated menu entries and `GRUB_DEFAULT`, timeout, boot-next,
   and submenu settings. Do not run `grub-install`, edit EFI variables, or
   change Secure Boot state without a separate owner checkpoint and a recovery
   route. Use the current CachyOS boot-manager guide if firmware/install
   details have changed.
3. Configure Snapper and the pacman/GRUB hook described in
   `01-system/cachyos/setup.md` only after checking the actual filesystem
   layout and current package hooks. Take and verify a snapshot before large
   system changes. Never run `btrfs check --repair` as routine maintenance.

## Phase 6 — Privileged integrations and user services

Install only after their package and firewall/service plans are reviewed:

- **Ollama/ROCm:** follow [`05-ai/ollama/README.md`](05-ai/ollama/README.md).
  This host's backend override is specific to its RX 6700 XT. Validate GPU
  inference with a small model before downloading large models. Never restore
  model cache files unless requested.
- **Nginx:** install
  [`04-networking/nginx/conf.d/00-types-hash.conf`](04-networking/nginx/conf.d/00-types-hash.conf)
  into `/etc/nginx/conf.d/`, run `sudo nginx -t`, then enable/reload only if
  nginx is intended to run on the new machine.
- **DNS filtering/encrypted DNS:** follow `06-tools/focus/README.md` and
  section 19.5 of `01-system/cachyos/setup.md`. Review NetworkManager,
  dnsmasq, dnscrypt-proxy, `/etc/resolv.conf`, and local listening ports as one
  plan before changing DNS; test name resolution and have a rollback ready.
- **SSH:** install the user unit from
  [`04-networking/ssh/README.md`](04-networking/ssh/README.md) only if the
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

1. Use the app chapters in `01-system/cachyos/setup.md` as the catalog for the
   full profile: Python/uv, Node/pnpm, editors, browsers, databases, Docker and
   Kubernetes, cloud CLIs, media and office apps. Show the owner a grouped
   install plan. Resolve renamed/unavailable packages through current official
   package metadata; do not silently substitute an AUR build.
2. Install topgrade and use the tracked config. `assume_yes = false` is
   intentional: dependency conflicts must remain visible for owner review.
   Run a dry run, then update interactively and inspect any `.pacnew` files.
   Do not update Git working trees automatically while this Dotfiles checkout
   has unreviewed changes:

   ```sh
   sudo pacman -S --needed topgrade
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
- SDDM presents the managed UWSM Hyprland session, autologin is off, Hyprland
  has no config errors, and the portal/lock/polkit/session services work.
- `sudo grub-script-check /boot/grub/grub.cfg` succeeds. The menu has the
  intended kernel entries, optional Windows entry, and one recovery submenu;
  Secure Boot state is what the owner selected.
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
installed system and testing another login. Confirm that recovery/Windows
entries remain available where applicable.
