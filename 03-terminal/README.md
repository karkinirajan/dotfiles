---
title: Part 03 Terminal
part: "03"
topic: terminal
last_verified: 2026-10-29
status: current
---

# 03 · Terminal

Shells, terminal emulators and the prompt.

| Chapter | Path | Purpose |
|---------|------|---------|
| zsh | [`zsh/`](zsh/README.md) | Oh My Zsh, deferred plugin loading, Starship prompt, tool integrations |
| bash | [`bash/`](bash/README.md) | Bash reference config for subshells or hosts without zsh |
| kitty | [`kitty/`](kitty/README.md) | `kitty.conf` plus Catppuccin Mocha & Gruvbox Dark Hard themes |
| Alacritty | [`alacritty/`](alacritty/README.md) | Primary terminal config (`alacritty.toml`) and [`SHORTCUTS.md`](alacritty/SHORTCUTS.md) |
| starship | [`starship/`](starship/README.md) | Prompt modules: OS, git, memory, command duration, language & cloud versions |
| fzf preview | [`fzf/`](fzf/README.md) | File and directory preview script (`preview.sh`) used by the zsh fzf bindings |

zsh runs `starship` (`03-terminal/starship/starship.toml`) as its prompt (`ZSH_THEME=""`).

Install the baseline CLI dependencies from
[`01-system/cachyos/packages/cli.txt`](../01-system/cachyos/packages/cli.txt)
before linking the configs. The zsh file degrades cleanly when optional
programs or Oh My Zsh plugins are missing. Install Oh My Zsh and its optional
plugins to enable the complete interactive setup:

```sh
git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git ~/.oh-my-zsh
zsh_custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins"
mkdir -p "$zsh_custom"
git clone --depth=1 https://github.com/romkatv/zsh-defer.git "$zsh_custom/zsh-defer"
git clone --depth=1 https://github.com/Aloxaf/fzf-tab.git "$zsh_custom/fzf-tab"
git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions.git "$zsh_custom/zsh-autosuggestions"
git clone --depth=1 https://github.com/MichaelAquilina/zsh-you-should-use.git "$zsh_custom/you-should-use"
git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git "$zsh_custom/zsh-syntax-highlighting"
```

`install.sh` links the fzf preview helper and the dedicated Kitty profile used
by the optional `psql` function. Install PostgreSQL separately if you want its
client and local database service.
