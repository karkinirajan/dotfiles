# SSH connection helpers

`systemd/user/erke-vps-ssh.service` maintains the SSH multiplexing connection
used for the ERKE Nepal VPS. The unit uses the `sheesh-vps` alias from
`~/.ssh/config` and retries at a modest interval when the remote host is
unavailable.

Install or refresh the user unit with:

```sh
install -Dm644 04-networking/ssh/systemd/user/erke-vps-ssh.service \
  ~/.config/systemd/user/erke-vps-ssh.service
systemctl --user daemon-reload
systemctl --user enable --now erke-vps-ssh.service
```
