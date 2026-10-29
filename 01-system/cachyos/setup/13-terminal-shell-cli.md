---
title: "13 Terminal, Shell and CLI Tools"
part: "01"
chapter: "13"
topic: terminal-shell-cli
versions: [zsh, starship, fzf, tmux, lazygit]
last_verified: 2026-10-29
status: current
sources:
  - https://github.com/ohmyzsh/ohmyzsh
  - https://starship.rs/config/
  - https://github.com/junegunn/fzf
---

# 13 Terminal, Shell and CLI Tools

## Purpose

The interactive shell, terminals, prompt and the modern command-line tool family. The canonical shell config is [`03-terminal/zsh/.zshrc`](../../../03-terminal/zsh/.zshrc); this chapter is the install reference. zsh is <!-- v:zsh -->5.9.2<!-- /v -->.

## 13.1 Zsh + Oh My Zsh

```bash
sudo pacman -S --needed zsh
chsh -s "$(command -v zsh)"
# Oh My Zsh: the installer's defaults start a new zsh (RUNZSH=yes), change the login shell and
# replace an existing ~/.zshrc with its template (KEEP_ZSHRC=no). On a machine whose ~/.zshrc is
# the repo's linked file, pass the opt-outs:
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended --keep-zshrc

git clone https://github.com/zsh-users/zsh-autosuggestions \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

`~/.zshrc` (`zsh-syntax-highlighting` must be the **last** plugin; `fzf-tab` must load after `compinit` and before widget wrappers; the OMZ `fzf` plugin runs `fzf --zsh` itself, so no `source ~/.fzf.zsh` is needed):

```bash
plugins=(git sudo fzf history zsh-autosuggestions docker kubectl zsh-syntax-highlighting)
```

The tracked `.zshrc` installs five cloned plugins (zsh-defer, fzf-tab, zsh-autosuggestions, you-should-use, zsh-syntax-highlighting) as described in [`03-terminal/README.md`](../../../03-terminal/README.md). Their repositories all exist and are maintained (zsh-defer is dormant since 2024-02). `DISABLE_AUTO_UPDATE=true` still works; the current form is `zstyle ':omz:update' mode disabled`.

## 13.2 Terminal Emulators

| Terminal | Install | Highlights |
|---|---|---|
| **Kitty** (default here) | `sudo pacman -S kitty` | GPU-accelerated, splits, tabs, ligatures, image display |
| **Alacritty** | `sudo pacman -S alacritty` | Fastest, minimalist (pair with tmux) |
| **WezTerm** | `sudo pacman -S wezterm` | GPU-accel, Lua config, built-in multiplexer. The package in `extra` is a 2024-02 git snapshot, a sign of stale upstream releases |
| **Ghostty** | `sudo pacman -S ghostty` | Zig-based, native GPU rendering; in `extra` (1.3.1) |

## 13.3 Starship Prompt

```bash
sudo pacman -S starship
# Add to ~/.zshrc: eval "$(starship init zsh)"
```

Starship <!-- v:starship -->1.27.0<!-- /v -->. Customize via `~/.config/starship.toml` (tracked in `03-terminal/starship/`). It shows git branch, language versions, Docker context and the Kubernetes namespace; the icons need a Nerd Font (`ttf-firacode-nerd`, `ttf-jetbrains-mono-nerd`, v3.5.1).

## 13.4 Terminal Multiplexers

```bash
sudo pacman -S tmux     # 3.8: Ctrl-b c (new window), Ctrl-b % (split); 3.8 adds floating and modal panes (`new-pane`)
sudo pacman -S zellij   # Rust alternative with a bottom help bar
```

## 13.5 Modern CLI Replacements

```bash
sudo pacman -S fzf ripgrep fd bat eza zoxide procs dust duf tokei hyperfine lazygit
```

| Tool | Replaces | Purpose |
|---|---|---|
| `fzf` | n/a | Fuzzy finder for files, history, everything |
| `ripgrep` (`rg`) | `grep` | 10× faster recursive search |
| `fd` | `find` | Fast, intuitive file finder |
| `bat` | `cat` | Syntax highlighting, Git integration |
| `eza` | `ls` | Icons, Git status, tree view |
| `zoxide` | `cd` | Smart directory jumping (learns habits) |
| `procs` | `ps` | Modern process viewer |
| `dust` | `du` | Visual proportional disk usage |
| `duf` | `df` | Colorful disk free output |
| `tokei` | `cloc` | Fast code line counter |
| `hyperfine` | `time` | Command benchmarking with statistics |
| `lazygit` | n/a | Full Git TUI, staging, commits, branches, rebasing |

**Shell aliases** (add to `~/.zshrc`):

```bash
eval "$(zoxide init zsh)"
source <(fzf --zsh)     # fzf 0.48 or newer; the Arch package also ships /usr/share/fzf/{key-bindings,completion}.zsh
alias ls='eza --icons --group-directories-first'
alias ll='eza -la --icons --group-directories-first --git'
alias lt='eza --tree --icons --level=2'
alias cat='bat --style=plain --paging=never'
alias grep='rg'
alias find='fd'
alias du='dust'      # dust has no `du -h`; in scripts and functions call `command du`
alias df='duf'
alias ps='procs'     # `procs aux` is a keyword filter, not ps; use `command ps aux` in functions
alias lg='lazygit'
```

## 13.6 lazydocker

```bash
sudo pacman -S lazydocker   # in extra (0.25.2); TUI for containers, images, volumes; honours the current docker context
alias ld='lazydocker'
```

## System information tools

`neofetch` is archived upstream (2024-04) and only available from the AUR; use `fastfetch` (extra) or `hyfetch`. `macchina` has had no release since 2025-01.

## Verify

```bash
zsh --version
starship --version
zsh -n ~/.zshrc
```

Expected: zsh <!-- v:zsh -->5.9.2<!-- /v -->, Starship <!-- v:starship -->1.27.0<!-- /v -->, and no output from `zsh -n`.

## Sources

- [Oh My Zsh README](https://github.com/ohmyzsh/ohmyzsh), [Starship](https://starship.rs/config/), [fzf](https://github.com/junegunn/fzf)
- Ledger: cluster C7, topics `Oh My Zsh`, `zsh plugin`, `Starship`, `Ghostty` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
