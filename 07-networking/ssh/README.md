# 07.2 · SSH Connection Helpers

`systemd/user/erke-vps-ssh.service` maintains a persistent SSH multiplexing
(`ControlMaster`) connection to the ERKE Nepal VPS.

- **Status:** Optional reference unit (not linked by `manifest.conf`).
- **Prerequisite:** `~/.ssh/config` must define the `sheesh-vps` host alias,
  `ControlPath`, and key path. Private SSH keys and `~/.ssh/config` host
  details are never stored in this repository.

## Install

Once `sheesh-vps` is configured in `~/.ssh/config` and `~/.ssh/cm` exists:

```sh
mkdir -p ~/.ssh/cm
install -Dm644 07-networking/ssh/systemd/user/erke-vps-ssh.service \
  ~/.config/systemd/user/erke-vps-ssh.service
systemctl --user daemon-reload
systemctl --user enable --now erke-vps-ssh.service
```
