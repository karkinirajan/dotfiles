# 07 · Networking

Host-level and user-level networking configuration that lives outside the
distraction blocker in [`06-tools/focus/`](../06-tools/focus/README.md).

| Chapter | Path | What it is |
|---------|------|------------|
| **07.1** | [`nginx/`](nginx/README.md) | Reverse-proxy MIME hash table tuning (`/etc/nginx/conf.d/00-types-hash.conf`) |
| **07.2** | [`ssh/`](ssh/README.md) | Persistent SSH ControlMaster user unit (`erke-vps-ssh.service`) |

Neither chapter is auto-linked by [`manifest.conf`](../manifest.conf): `nginx/`
installs into `/etc/nginx/` (requires root) and `ssh/` depends on a private host
alias in `~/.ssh/config` that is intentionally not tracked in git.
