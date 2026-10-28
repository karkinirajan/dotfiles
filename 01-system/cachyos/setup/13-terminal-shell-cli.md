---
title: "13 Terminal, Shell and CLI Tools"
part: "01"
chapter: "13"
topic: terminal-shell-cli
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 13 Terminal, Shell and CLI Tools


## 13.1 Zsh + Oh My Zsh

```bash
sudo pacman -S zsh
chsh -s $(which zsh)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

git clone https://github.com/zsh-users/zsh-autosuggestions \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

`~/.zshrc`:

```bash
plugins=(git sudo fzf history zsh-autosuggestions zsh-syntax-highlighting docker kubectl)
```

## 13.2 Terminal Emulators

| Terminal | Install | Highlights |
|---|---|---|
| **Kitty** ⭐ | `sudo pacman -S kitty` | GPU-accelerated, splits, tabs, ligatures, image display |
| **Alacritty** | `sudo pacman -S alacritty` | Fastest, minimalist (pair with tmux) |
| **WezTerm** | `sudo pacman -S wezterm` | GPU-accel, Lua config, built-in multiplexer |
| **Ghostty** | `paru -S ghostty` | Zig-based, extremely fast, native GPU rendering |

## 13.3 Starship Prompt

```bash
sudo pacman -S starship
# Add to ~/.zshrc: eval "$(starship init zsh)"
```

Customize via `~/.config/starship.toml`. Shows git branch, Python version, Docker context, K8s namespace.

## 13.4 Terminal Multiplexers

```bash
sudo pacman -S tmux     # Classic — Ctrl-b c (new window), Ctrl-b % (split vertical)
sudo pacman -S zellij   # Modern Rust alternative — beginner-friendly bottom help bar
```

## 13.5 Modern CLI Replacements

```bash
sudo pacman -S fzf ripgrep fd bat eza zoxide procs dust duf tokei hyperfine lazygit
```

| Tool | Replaces | Purpose |
|---|---|---|
| `fzf` | — | Fuzzy finder for files, history, everything |
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
| `lazygit` | — | Full Git TUI — staging, commits, branches, rebasing |

**Shell aliases** (add to `~/.zshrc`):

```bash
eval "$(zoxide init zsh)"
source /usr/share/fzf/key-bindings.zsh
source /usr/share/fzf/completion.zsh
alias ls='eza --icons --group-directories-first'
alias ll='eza -la --icons --group-directories-first --git'
alias lt='eza --tree --icons --level=2'
alias cat='bat --style=plain --paging=never'
alias grep='rg'
alias find='fd'
alias du='dust'
alias df='duf'
alias ps='procs'
alias lg='lazygit'
```

## 13.6 lazydocker

```bash
paru -S lazydocker   # TUI for Docker containers, images, volumes
alias ld='lazydocker'
```
