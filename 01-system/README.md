# 01 · System

Everything below the desktop: the packages the configs depend on, snapshots,
and the update routine.

| Chapter | Path | Purpose |
|---------|------|---------|
| Setup walkthrough | [`cachyos/setup.md`](cachyos/setup.md) | Full install narrative: GPU drivers, toolchains, Kubernetes, Terraform |
| Packages | [`cachyos/packages/`](cachyos/packages/) | `desktop.txt`, `fonts.txt`, `ai.txt` — one package per line, `(AUR)` marks AUR packages |
| Snapshots | [`timeshift/`](timeshift/README.md) | Daily Timeshift snapshot via a systemd timer |
| Updates | [`topgrade/`](topgrade/README.md) | `topgrade.toml` — which update steps run, which are disabled and why |

Packages are not installed by `install.sh`, which runs unprivileged. Install
them with the commands in the root [README](../README.md#install).

Keep `01-system/cachyos/packages/` as the single list of what the machine
needs. If a config names a binary, the package that provides it belongs here.
