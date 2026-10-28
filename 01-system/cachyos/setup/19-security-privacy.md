---
title: "19 Security and Privacy"
part: "01"
chapter: "19"
topic: security-privacy
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 19 Security and Privacy


## 19.1 Firewall — UFW

```bash
sudo pacman -S ufw ufw-extras
sudo ufw default deny incoming
sudo ufw default allow outgoing
# Local workstation profile keeps zero inbound allow rules.
# Add SSH or KDE Connect rules only if explicitly needed on a trusted LAN:
# sudo ufw allow ssh
# sudo ufw allow 1714:1764/udp
# sudo ufw allow 1714:1764/tcp
sudo ufw --force enable
sudo systemctl enable --now ufw.service
```

## 19.2 Fail2ban

```bash
sudo pacman -S fail2ban
```

Create `/etc/fail2ban/jail.local`:

```ini
[DEFAULT]
bantime = 1d
findtime = 10m
maxretry = 5

[sshd]
enabled = true
backend = systemd
maxretry = 3
bantime = 2w
```

```bash
sudo systemctl enable --now fail2ban.service
```

## 19.3 SSH Hardening

```bash
ssh-keygen -t ed25519 -a 100 -C "you@email.com"
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host
```

Edit `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
AllowUsers yourusername
```

```bash
sudo systemctl restart sshd
```

## 19.4 Password Managers

```bash
sudo pacman -S bitwarden keepassxc
```

| Tool | Use Case |
|---|---|
| **Bitwarden** | Cloud-synced across all devices, browser extension, team sharing |
| **KeePassXC** | Local/offline, sync `.kdbx` file via Syncthing, maximum control |

## 19.5 Encrypted DNS

```bash
sudo pacman -S dnscrypt-proxy
```

Edit `/etc/dnscrypt-proxy/dnscrypt-proxy.toml`:

```toml
server_names = ['cloudflare', 'quad9-dnscrypt-ip4-nofilter-pri']
listen_addresses = ['127.0.0.1:5300', '[::1]:5300']
require_dnssec = true
require_nolog = true
```

> **Note on DNS services:** On this CachyOS profile, `systemd-resolved` is active by default while `dnsmasq` and `dnscrypt-proxy` are installed but disabled until explicitly enabled (for example, when using [`06-tools/focus/`](../../../06-tools/focus/README.md) or forwarding `dnsmasq` to `dnscrypt-proxy` on port `5300`).

```bash
sudo systemctl enable --now dnscrypt-proxy.service
```

## 19.6 VPN

```bash
# Mullvad VPN (no email, no account, anonymous payment):
paru -S mullvad-vpn-bin
sudo systemctl enable --now mullvad-daemon.service
mullvad account login <ACCOUNT_NUMBER>
mullvad connect

# ProtonVPN (free tier available):
sudo pacman -S proton-vpn-gtk-app
```

## 19.7 AppArmor

```bash
sudo pacman -S apparmor
sudo pacman -S apparmor.d   # Community profiles (complain mode — safe, logs violations)
```

Add the kernel parameter to `KERNEL_CMDLINE[default]` in
`/etc/default/limine`:

```
KERNEL_CMDLINE[default]+=" lsm=landlock,lockdown,yama,integrity,apparmor,bpf"
```

```bash
sudo limine-update
sudo systemctl enable apparmor.service
# Reboot required. Verify: sudo aa-status
```

> **CachyOS note:** After reboot, AppArmor loads profiles in complain mode (logs but doesn't block). Switch individual profiles to enforce mode with `sudo aa-enforce /etc/apparmor.d/<profile>`.

## 19.8 Disk Encryption (LUKS)

Must be configured at install time. CachyOS installer has a LUKS checkbox.

```bash
# Verify:  lsblk -f   (look for crypto_LUKS)
# Backup:  sudo cryptsetup luksHeaderBackup /dev/sdXn --header-backup-file /safe/header.img
```

## 19.9 File Sync — Syncthing

```bash
sudo pacman -S syncthing
systemctl --user enable --now syncthing.service
# Or:
sudo systemctl enable --now syncthing@$USER.service
# Web UI: http://127.0.0.1:8384
```
