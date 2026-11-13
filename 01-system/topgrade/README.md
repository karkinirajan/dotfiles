# Topgrade

`topgrade` updates every supported step it detects: system packages, language
toolchains and package managers, editors, plugins, containers, and other
installed tools. The Arch system step is explicitly set to `paru`, which uses
`pacman` for repository packages and handles AUR packages. The Zsh `upgrade`
command likewise prefers `paru` and falls back to `yay`.

There is no `only` list; Topgrade's detection decides which steps apply. The
Antigravity extension check is disabled because in the installed Topgrade
version, probing `antigravity --version` opens the IDE and returns no version.
The Antigravity CLI step is disabled too: it runs `agy update`, which tries to
overwrite `/usr/bin/agy` and fails because that path is not writable. Both
binaries come from the `antigravity` and `antigravity-cli` packages, which
`paru` already updates in the system step. <!-- UNVERIFIED: the Antigravity probe and `agy update` behaviour are recorded from this host only, not reproducible without the packages --> Helm's native step is replaced by a
conditional custom command: it runs `helm repo update` only when at least one
Helm repository is configured, so a fresh Helm install does not fail every
upgrade with “no repositories found.”
Topgrade's built-in self-updater is disabled because Topgrade itself is
installed as an AUR package and is updated by `paru` in the system step.
Confirmation prompts are off (`assume_yes = true`, an owner choice made
2026-11-04): the Arch step runs `paru -Syu --noconfirm`, so every prompt takes
its default answer. Failed steps do not retry automatically. The Zsh
`update`/`upgrade` function matches this: it passes `--noconfirm` to both the
upgrade and the cache cleanup.

## Install

```sh
paru -S --needed topgrade-bin
```

Linked via `manifest.conf` to `~/.config/topgrade.toml`, edit either side.
