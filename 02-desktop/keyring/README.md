---
title: Login keyring
part: "02"
chapter: "03"
topic: keyring
last_verified: 2026-10-29
status: current
sources:
  - https://wiki.archlinux.org/title/GNOME/Keyring
---

# 02.3 · Login Keyring (`gnome-keyring`)

Unlocks the "Default keyring" with the login password, so apps that store
secrets (Proton VPN, Electron apps, browsers) do not ask for it after login.

```text
02-desktop/keyring/
├── README.md
└── dbus-override/
    └── org.freedesktop.secrets.service   → ~/.local/share/dbus-1/services/ (linked by manifest.conf)
```

## Why two pieces

- **One daemon.** The packaged D-Bus file starts its own `gnome-keyring-daemon`
  when an app asks for `org.freedesktop.secrets` before the systemd user socket
  has started one, which left two daemons running. The override adds
  `SystemdService=gnome-keyring-daemon.service`, so D-Bus activation starts
  the systemd unit instead.
- **Unlock at login.** greetd's PAM stack (`/etc/pam.d/greetd`) did not load
  `pam_gnome_keyring.so`, so nothing passed the login password to the daemon.
  Add, after the existing lines (label: `machine-only`):

```text
auth       optional     pam_gnome_keyring.so
session    optional     pam_gnome_keyring.so auto_start
```

The keyring password must equal the login password. If the prompt still
appears after a fresh login, change the "Default keyring" password to the
login password once (Seahorse: right-click the keyring, Change Password).
