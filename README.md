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
├── linux/                      # Linux shell configurations
│   ├── arch/
│   │   ├── .bashrc             # Bash config for Arch/Manjaro
│   │   └── .zshrc              # Zsh config for Arch/Manjaro (p10k + Starship)
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
└── vscode/                     # Visual Studio Code configuration
    ├── extensions.sh           # Shell script to bulk-install extensions
    ├── vscode-extensions.json  # Curated extension list (80+)
    ├── vscode-keybindings.json # Custom keyboard shortcuts
    └── vscode-settings.json    # Editor settings (font, theme, AI, language rules)
```

---

## Categories at a Glance

### Shell & Terminal

| File | Platform | Highlights |
|------|----------|------------|
| `linux/arch/.zshrc` | Arch/Manjaro | Powerlevel10k, Zsh plugins, pacman/yay aliases |
| `linux/arch/.bashrc` | Arch/Manjaro | Bash config, git prompt, NVM |
| `linux/ubuntu/.zshrc` | Ubuntu/Debian | apt aliases, ss networking |
| `mac/.zshrc` | macOS | Homebrew, macOS utilities, flush-dns |
| `linux/starship.toml` | All platforms | Battery, Git status, memory, language versions |

### Editors

| Tool | Config Files | Key Features |
|------|-------------|--------------|
| VS Code | `vscode/` (4 files) | Copilot, GitLens, 80+ extensions |
| Sublime Text | `sublime/` (3 files) | Python/Anaconda, Predawn theme |

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

### 3. VS Code
```bash
cp vscode/vscode-settings.json ~/Library/Application\ Support/Code/User/settings.json
bash vscode/extensions.sh   # install all extensions
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
