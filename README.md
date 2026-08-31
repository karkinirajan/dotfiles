# Development Environment Configuration

Personal configuration files and setup guides for Linux (Arch, Ubuntu) and macOS development environments.

## Repository Structure

```
dotfiles/
├── cachyos/                    # CachyOS (Arch) AI/ML workstation setup
│   ├── cachyos-complete-setup.md   # Full system setup walkthrough
│   ├── cachyos-setup-dev.md        # AMD GPU, ROCm, AI/ML stack, DevOps tooling
│   └── cachyos_dev_artifact.md     # Comprehensive setup reference
│
├── claude/                     # Claude Code global config (agents, commands, skills, settings)
│   ├── CLAUDE.md               # Global engineering profile/preferences
│   ├── settings.json           # Permissions, hooks, enabled plugins
│   ├── agents/                 # Custom subagents (backend/frontend/db/ai-agent/release/qa/data-ml)
│   ├── commands/                # Custom slash commands (/discover, /shipcheck)
│   └── skills/                  # Stack-specific architecture/security skills + claude-brain, visual-qa
│
├── focus/                      # System-wide distraction blocker (dnsmasq + nftables)
│   ├── scripts/                # focus, focus-refresh, focus-page
│   ├── systemd/                # services, schedule timers, list watcher
│   ├── networkmanager/         # resolv.conf ownership (dns=none)
│   └── block.list, allow.list  # what to block / CDN-IP exemptions
│
├── hyprland/                   # Hyprland compositor + Noctalia shell (CachyOS/Arch Wayland)
│   ├── hypr/                   # hyprland.conf, keybinds/colors/autostart, hyprlock/hypridle/hyprpaper
│   └── noctalia/                # bar/launcher/clipboard/control-center — replaces Waybar/wofi/mako
│
├── kitty/                      # Kitty terminal configuration
│   ├── kitty.conf              # Fonts, keybindings, splits, performance
│   └── gruvbox-dark-hard.conf  # Colour scheme (matches the zsh palette)
│
├── linux/                      # Linux shell configurations
│   ├── arch/
│   │   ├── .bashrc             # Bash config for Arch/Manjaro
│   │   └── .zshrc              # Zsh config for Arch/Manjaro (OMZ + starship/p10k)
│   ├── ubuntu/
│   │   └── .zshrc              # Zsh config for Ubuntu (apt aliases)
│   └── starship.toml           # Cross-platform terminal prompt configuration
│
├── mac/                        # macOS shell configuration
│   └── .zshrc                  # Zsh config for macOS (Homebrew, macOS utilities)
│
├── sublime/                    # Sublime Text configuration
│   ├── anaconda-sublime.json   # Anaconda (Python) plugin settings
│   ├── sublime-repl.json       # Python REPL configuration
│   └── sublime-settings.json   # Editor settings (theme, font)
│
├── vscode/                     # Visual Studio Code configuration
│   ├── extensions.sh           # Shell script to bulk-install extensions
│   ├── vscode-extensions.json  # Curated extension list (80+)
│   ├── vscode-keybindings.json # Custom keyboard shortcuts
│   └── vscode-settings.json    # Editor settings (font, theme, AI, language rules)
│
└── zed/                        # Zed editor configuration
    ├── README.md                # Extension list — Zed has no CLI installer, install manually
    └── zed-settings.json        # Editor + language server + agent/MCP settings
```

---

## Categories at a Glance

### Shell & Terminal

| File | Platform | Highlights |
|------|----------|------------|
| `kitty/kitty.conf` | All platforms | FiraCode Nerd Font + ligatures, splits, vim-style navigation |
| `linux/arch/.zshrc` | Arch/Manjaro | Oh My Zsh, starship/p10k toggle, deferred plugin loading |
| `linux/arch/.bashrc` | Arch/Manjaro | Bash config, git prompt, NVM |
| `linux/ubuntu/.zshrc` | Ubuntu/Debian | apt aliases, ss networking |
| `mac/.zshrc` | macOS | Homebrew, macOS utilities, flush-dns |
| `linux/starship.toml` | All platforms | Battery, Git status, memory, language versions |

The Arch zsh config runs **starship by default** and ships a Powerlevel10k
setup alongside it. Only one prompt is ever active — switch at runtime with
`theme-starship` / `theme-p10k`; the choice persists in
`~/.config/zsh/prompt-framework`.

### Editors

| Tool | Config Files | Key Features |
|------|-------------|--------------|
| VS Code | `vscode/` (4 files) | Copilot, GitLens, 80+ extensions |
| Zed | `zed/` (2 files) | Ollama Cloud agent, MCP context servers, per-language LSP config |
| Sublime Text | `sublime/` (3 files) | Python/Anaconda, Predawn theme |

### Productivity

| Tool | Config | Key Features |
|------|--------|--------------|
| focus | `focus/` | OS-level site blocking via dnsmasq + nftables, schedule timers, lock mode |

See [`focus/README.md`](focus/README.md) for how it works and how to install it.

### DevOps & AI/ML

| File | Topics |
|------|--------|
| `cachyos/cachyos-setup-dev.md` | AMD GPU (ROCm), PyTorch/TF, LangChain, Ollama, K8s, Terraform |

---

## Quick Start

### 1. Shell (Arch Linux)
```bash
cp linux/arch/.zshrc ~/.zshrc
cp linux/starship.toml ~/.config/starship.toml
```

### 2. Shell (macOS)
```bash
cp mac/.zshrc ~/.zshrc
cp linux/starship.toml ~/.config/starship.toml
```

### 3. Kitty terminal
```bash
mkdir -p ~/.config/kitty
cp kitty/kitty.conf kitty/gruvbox-dark-hard.conf ~/.config/kitty/
```
Requires a Nerd Font (`ttf-firacode-nerd` on Arch) for prompt glyphs.
Reload a running kitty with `ctrl+shift+f5`.

### 4. VS Code
```bash
cp vscode/vscode-settings.json ~/Library/Application\ Support/Code/User/settings.json
bash vscode/extensions.sh   # install all extensions
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
