# 03 · Terminal

Shells, terminal emulators and the prompt.

| Chapter | Path | Purpose |
|---------|------|---------|
| zsh | [`zsh/`](zsh/.zshrc) | Oh My Zsh, deferred plugin loading, starship/p10k switch. `macos.zshrc` and `ubuntu.zshrc` are per-OS variants |
| bash | [`bash/`](bash/.bashrc) | Bash equivalent for hosts without zsh |
| kitty | [`kitty/`](kitty/kitty.conf) | `kitty.conf` plus two colour themes. `current-theme.conf` is generated and not tracked |
| Alacritty | [`alacritty/`](alacritty/SHORTCUTS.md) | Main config; the Noctalia-generated theme is not tracked |
| starship | [`starship/`](starship/starship.toml) | Prompt modules: battery, git, memory, language versions |
| fzf preview | [`fzf/preview.sh`](fzf/preview.sh) | File and directory previews used by the zsh fzf bindings |

zsh runs starship by default. Switch prompts at runtime with `theme-starship`
or `theme-p10k`; the choice persists in `~/.config/zsh/prompt-framework`.

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
