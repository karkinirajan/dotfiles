---
title: Zsh
part: "03"
chapter: "01"
topic: zsh
versions: [zsh]
last_verified: 2026-10-29
status: current
sources:
  - https://github.com/ohmyzsh/ohmyzsh
  - https://github.com/romkatv/zsh-defer
---

# 03.1 · Zsh

Interactive login shell configuration for CachyOS (`03-terminal/zsh/.zshrc`),
plus archived reference configs for macOS and Ubuntu.

```
03-terminal/zsh/
├── README.md       ← you are here
├── .zshrc          → ~/.zshrc (linked via manifest.conf)
├── macos.zshrc     # reference config for macOS hosts (not linked)
└── ubuntu.zshrc    # reference config for Ubuntu/Debian hosts (not linked)
```

## Highlights of `.zshrc`

- **Prompt:** [`starship`](../starship/README.md) (`ZSH_THEME=""` in Oh My Zsh
  so OMZ never loads a competing theme).
- **Fast startup:** Autosuggestions and you-should-use are sourced through
  `zsh-defer`; `zsh-syntax-highlighting` is the last Oh My Zsh plugin, as its
  install notes require. (An earlier version of this page also claimed lazy-loaded
  completions for kubectl, helm and others; the file has no such code.)
- **Tool integrations:** `zoxide`, `fzf` (paired with [`03-terminal/fzf/preview.sh`](../fzf/README.md)),
  `atuin`, `direnv`, `nvm` (`/usr/share/nvm`), `pnpm`, `uv`, and `sccache`.
- **Local LLM environment:** `OLLAMA_HOST` and `HSA_OVERRIDE_GFX_VERSION` are
  exported (see [`05-ai/ollama/`](../../05-ai/ollama/README.md) for what the
  override is for). The `ccl`/`cclf` helpers described in the Ollama benchmark
  notes are **not** part of the tracked `.zshrc`; the benchmark's installer script
  was never applied to it, and the `cc-local`/`cc-fast` models they name have no
  Modelfile in the repo.

## Known behavior

- `fkill` and `duh` call `command ps` and `command du`: the file aliases `ps` to `procs` and `du` to `dust`, and zsh expands aliases when a function body is parsed.
- `$PNPM_HOME/bin` is on `PATH` because pnpm 12 installs global binaries there.
- Oh My Zsh itself should be installed with the git clone shown in [`../README.md`](../README.md) (or the installer with `--unattended --keep-zshrc`); the installer's defaults overwrite `~/.zshrc`.
- `macos.zshrc` and `ubuntu.zshrc` use the pre-split plugin set and the `robbyrussell` theme; nothing links them. Keep them only if non-CachyOS hosts must be supported.

## Verify

```sh
zsh -n ~/.zshrc
```
