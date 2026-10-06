# 03 · Terminal

Shells, terminal emulators and the prompt.

| Chapter | Path | Purpose |
|---------|------|---------|
| zsh | [`zsh/`](zsh/.zshrc) | Oh My Zsh, deferred plugin loading, starship/p10k switch. `macos.zshrc` and `ubuntu.zshrc` are per-OS variants |
| bash | [`bash/`](bash/.bashrc) | Bash equivalent for hosts without zsh |
| kitty | [`kitty/`](kitty/kitty.conf) | `kitty.conf` plus two colour themes. `current-theme.conf` is generated and not tracked |
| Alacritty | [`alacritty/`](alacritty/SHORTCUTS.md) | Main config; the Noctalia-generated theme is not tracked |
| starship | [`starship/`](starship/starship.toml) | Prompt modules: battery, git, memory, language versions |

zsh runs starship by default. Switch prompts at runtime with `theme-starship`
or `theme-p10k`; the choice persists in `~/.config/zsh/prompt-framework`.
