---
title: "19 Security and Privacy"
part: "01"
chapter: "19"
topic: security-privacy
versions: [ufw, fail2ban, openssh, dnscrypt-proxy, dnsmasq, syncthing, mullvad-vpn, proton-vpn]
last_verified: 2026-10-29
status: current
sources:
  - https://wiki.cachyos.org/
  - https://wiki.archlinux.org/title/Uncomplicated_Firewall
  - https://wiki.archlinux.org/title/OpenSSH
  - https://wiki.archlinux.org/title/Dnscrypt-proxy
  - https://apparmor.pujol.io/
---

# 19 Security and Privacy

## Purpose

The security baseline of the workstation and the optional hardening layers. Which of them are active on the primary host is recorded in [`system-summary.md`](../../../system-summary.md): UFW is active, everything else here is installed but off or optional.

## Prerequisites

- A working CachyOS install ([chapter 01](01-system-foundation.md)).
- For remote administration: a proven SSH way back in before any deny-incoming policy is enabled.

## 19.1 Firewall: UFW

UFW <!-- v:ufw -->0.36.2<!-- /v --> (upstream has had no release since 2023-05; Arch builds 0.36.2-7). CachyOS also enables it by default. `ufw-extras` only adds application profiles under `/etc/ufw/applications.d` (KDE Connect, LocalSend, mDNS, Samba, Steam, Tailscale and others) and is optional.

```bash
sudo pacman -S --needed ufw ufw-extras
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw --force enable
sudo systemctl enable --now ufw.service
sudo ufw status verbose
```

The local-workstation profile keeps zero inbound allow rules. Add rules only for a service that must be reachable on a trusted LAN, and remove them afterwards:

```bash
sudo ufw allow ssh                  # only if sshd is enabled on purpose
sudo ufw allow kdeconnect           # ufw-extras profile, TCP and UDP 1714-1764; only if KDE Connect is used (chapter 18)
sudo ufw allow syncthing            # profile shipped by the syncthing package, see 19.9
```

Run `sudo ufw status verbose` after every reboot: Launchpad has open reports of a failed reload writing `ENABLED=no` and of kernel freezes with UFW logging on kernel 7.2. Expected: `Status: active`, `Default: deny (incoming), allow (outgoing)`. Label: `machine-only`.

## 19.2 Fail2ban

Fail2ban <!-- v:fail2ban -->1.1.1<!-- /v -->. It only protects a service that is running: no `sshd` runs on the primary host, so the jail below does nothing until SSH is enabled. Arch's `paths-arch.conf` already selects the systemd backend for sshd. Fail2ban 1.1.1 defaults to the iptables multiport action; with UFW use the `ufw` action.

```bash
sudo pacman -S --needed fail2ban
```

`/etc/fail2ban/jail.local`:

```ini
[DEFAULT]
bantime = 1d
findtime = 10m
maxretry = 5
banaction = ufw

[sshd]
enabled = true
maxretry = 3
bantime = 2w
```

```bash
sudo systemctl enable --now fail2ban.service
sudo fail2ban-client status sshd     # jail listed, no errors
```

Label: `machine-only`.

## 19.3 SSH hardening

OpenSSH <!-- v:openssh -->10.6p1<!-- /v -->. Since 10.0 DSA is removed and sshd turns the modp DH groups off by default; 10.1 moved agent sockets under `~/.ssh/agent`. Use drop-ins rather than editing the vendor file, and test before restarting.

```bash
ssh-keygen -t ed25519 -a 100 -C "you@email.com"
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host
```

`/etc/ssh/sshd_config.d/10-hardening.conf`:

```text
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
X11Forwarding no
MaxAuthTries 3
AllowUsers yourusername
```

```bash
sudo sshd -t                         # no output means the configuration parses
sudo systemctl restart sshd
```

Keep an existing session open while testing a second login. Label: `machine-only`.

## 19.4 Password managers

```bash
sudo pacman -S --needed bitwarden keepassxc
```

| Tool | Use case |
|---|---|
| Bitwarden | Cloud-synced across devices, browser extension, team sharing. The Arch `bitwarden` desktop package lags the upstream desktop release by several months; the web vault and browser extension are current |
| KeePassXC | Local and offline, sync the `.kdbx` file with Syncthing, maximum control |

## 19.5 Encrypted DNS

dnscrypt-proxy <!-- v:dnscrypt-proxy -->2.1.20<!-- /v -->. All keys below exist in 2.1.x; both resolvers are listed in the public resolver list with DNSSEC, no-log and no-filter properties, so the `require_*` filters keep them.

```bash
sudo pacman -S --needed dnscrypt-proxy
```

`/etc/dnscrypt-proxy/dnscrypt-proxy.toml`:

```toml
server_names = ['cloudflare', 'quad9-dnscrypt-ip4-nofilter-pri']
listen_addresses = ['127.0.0.1:5300', '[::1]:5300']
require_dnssec = true
require_nolog = true
```

Pick one activation mode. With `listen_addresses` set, run the service; socket activation (`dnscrypt-proxy.socket`) requires `listen_addresses = []` and the two are mutually exclusive.

```bash
sudo systemctl enable --now dnscrypt-proxy.service
dig +short example.com @127.0.0.1 -p 5300
```

To put dnsmasq in front (this is what the focus tool does for its blocklist, see [`06-tools/focus/`](../../../06-tools/focus/README.md)), forward everything to dnscrypt-proxy and disable plain upstreams:

```text
# /etc/dnsmasq.d/10-dnscrypt.conf
no-resolv
server=127.0.0.1#5300
server=::1#5300
```

The tracked `06-tools/focus/dnsmasq/dnsmasq.conf` currently forwards to the plain resolvers 1.1.1.1 and 9.9.9.9. Choose one: either keep focus self-contained, or replace those `server=` lines with the two above. systemd-resolved listens on 127.0.0.53 and dnsmasq on 127.0.0.1, so they do not clash. On this profile `systemd-resolved` is active by default while `dnsmasq` and `dnscrypt-proxy` are installed but disabled. Label: `machine-only`.

## 19.6 VPN

Mullvad is in Arch extra (`mullvad-vpn` <!-- v:mullvad-vpn -->2026.5<!-- /v -->, daemon split into `mullvad-vpn-daemon`); Mullvad itself documents it as "available in the official repository (not maintained by us)". The AUR `mullvad-vpn-bin` conflicts with it and is no longer needed. The package install may enable `mullvad-daemon.service` and `mullvad-early-boot-blocking.service`; this machine keeps both disabled while Proton VPN is the active client. Use one VPN client at a time.

```bash
# Mullvad (no email, no account, anonymous payment)
sudo pacman -S --needed mullvad-vpn
sudo systemctl enable --now mullvad-daemon.service
mullvad account login <ACCOUNT_NUMBER>
mullvad connect

# Proton VPN (free tier available): needs NetworkManager and a Secret Service provider
sudo pacman -S --needed proton-vpn-gtk-app gnome-keyring
```

Proton VPN <!-- v:proton-vpn -->4.18.7<!-- /v --> stores credentials through the Secret Service API; KWallet was removed with Plasma on this machine, so install `gnome-keyring` (or another provider) before the first login. Its daemon unit is `proton.VPN.service`. Mullvad wants systemd-resolved or resolvconf to manage DNS, which conflicts with the focus tool's static `/etc/resolv.conf` while focus is on. <!-- UNVERIFIED: the interaction is inferred, not reproduced --> Label: `machine-only`.

## 19.7 AppArmor

Optional and **not enabled** on the primary host. `linux-cachyos` is built with AppArmor (`CONFIG_SECURITY_APPARMOR=y`), but its default `CONFIG_LSM` is `landlock,lockdown,yama,integrity,bpf`, so the module is present and inactive until the boot command line lists it. That is why `aa-status` reports "apparmor module is loaded" and "apparmor filesystem is not mounted".

```bash
sudo pacman -S --needed apparmor apparmor.d
```

Add `lsm=landlock,lockdown,yama,integrity,apparmor,bpf` to the kernel command line in `/etc/default/limine`:

```text
KERNEL_CMDLINE[default]+=" lsm=landlock,lockdown,yama,integrity,apparmor,bpf"
```

`+=` only appends when the base parameters (`root=`, `rootflags=`) already live in `/etc/default/limine`. Apply and inspect the generated line **before** rebooting:

```bash
sudo limine-update
grep -n 'cmdline:' /boot/limine.conf     # must still contain root= and rootflags= plus the lsm= string
sudo systemctl enable apparmor.service
```

CachyOS also recommends a policy cache in `/etc/apparmor/parser.conf`:

```text
write-cache
Optimize=compress-fast
cache-loc /etc/apparmor/earlypolicy/
```

After a reboot: `cat /sys/kernel/security/lsm` lists `apparmor`, `aa-enabled` prints `Yes`, and `sudo aa-status` shows profiles in **complain** mode (log, do not block). Switch single profiles with `sudo aa-enforce /etc/apparmor.d/<profile>`.

The apparmor.d project documents support for GNOME/GDM, KDE/SDDM and XFCE/LightDM only. Hyprland with greetd and Noctalia is outside that list, so expect gaps and run a week in complain mode with `aa-log` before enforcing anything. Label: `machine-only`.

## 19.8 Disk encryption (LUKS)

Choose it at install time: the CachyOS installer has an Encrypt checkbox, and encryption cannot be added afterward without reinstalling. With Limine the FAT `/boot` partition stays unencrypted. The primary host's root is Btrfs without LUKS.

```bash
lsblk -f                                   # look for crypto_LUKS
sudo cryptsetup luksHeaderBackup /dev/<device> --header-backup-file <file>   # keep the file offline
```

cryptsetup 2.8.8 is current. Label: `machine-only`. A note for later: mkinitcpio 42 changed the TPM2 PCR set, so TPM2-bound LUKS keys need re-enrolment (not applicable while root is unencrypted).

## 19.9 File sync: Syncthing

Syncthing <!-- v:syncthing -->2.1.7<!-- /v -->. Version 2 migrated the database from LevelDB to SQLite (one database per folder) on first start and no longer creates a default folder. Use either the user unit or the system unit, not both.

```bash
sudo pacman -S --needed syncthing
systemctl --user enable --now syncthing.service     # user unit, starts at login
# or: sudo systemctl enable --now syncthing@$USER.service
sudo ufw allow syncthing                            # TCP 22000, UDP 22000 (QUIC), UDP 21027; do not add syncthing-gui
```

The web UI is `http://127.0.0.1:8384` (loopback by default). Label: `machine-only`.

## Verify

```bash
sudo ufw status verbose
systemctl is-active ufw
sudo sshd -t
```

Expected: UFW reports `Status: active` with deny-incoming and allow-outgoing defaults and no allow rules; `sshd -t` prints nothing.

## Sources

- [Arch Wiki: Uncomplicated Firewall](https://wiki.archlinux.org/title/Uncomplicated_Firewall), [OpenSSH](https://wiki.archlinux.org/title/OpenSSH), [dnscrypt-proxy](https://wiki.archlinux.org/title/Dnscrypt-proxy)
- [apparmor.d](https://apparmor.pujol.io/)
- [Mullvad: install on Linux](https://mullvad.net/en/help/install-mullvad-app-linux)
- Ledger: clusters C1 and C10, topics `limine`, `openssh`, `apparmor`, `dnscrypt-proxy`, `mullvad`, `protonvpn`, `syncthing`, `luks`, `ufw`, `fail2ban` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
