# 01 · System

Everything below the desktop: the packages the configs depend on, snapshots,
and the update routine.

| Chapter | Path | Purpose |
|---------|------|---------|
| CachyOS profile | [`cachyos/`](cachyos/README.md) | Overview of OS configs, `mariadb-local.cnf`, and local PKGBUILDs |
| Setup walkthrough | [`cachyos/setup/`](cachyos/setup/README.md) | 25 numbered chapters: foundation, GPU drivers, toolchains, databases, Kubernetes, editors, apps, security. `cachyos/setup.md` is a redirect stub for old links |
| Packages | [`cachyos/packages/`](cachyos/packages/) | Desktop, system, font, CLI, developer, Claude Code, and local-AI package lists |
| Full developer profile | [`cachyos/dev-stack.md`](cachyos/dev-stack.md) | Optional toolchains, local databases, rootless Docker, and host-specific setup |
| Host snapshot | [`cachyos/host-snapshot/`](cachyos/host-snapshot/README.md) | Point-in-time `pacman -Qe` and `pacman -Qm` output (2026-10-28) |
| Snapshots (archived) | [`timeshift/`](timeshift/README.md) | Archived Timeshift alternative; current CachyOS host uses Snapper |
| Updates | [`topgrade/`](topgrade/README.md) | `topgrade.toml`, which update steps run, which are disabled and why |

Packages are not installed by `install.sh`, which runs unprivileged. Install
them with the commands in the root [README](../README.md#install). Focus mode
has its own dependency list at [`../06-tools/focus/packages.txt`](../06-tools/focus/packages.txt);
installing those packages does not enable DNS filtering.

Keep `01-system/cachyos/packages/` as the single list of what the machine
needs. If a config names a binary, the package that provides it belongs here.
The optional full development profile is documented in
[`cachyos/dev-stack.md`](cachyos/dev-stack.md) and listed in
[`cachyos/packages/developer.txt`](cachyos/packages/developer.txt); it is not
part of the base dotfiles package transaction.
