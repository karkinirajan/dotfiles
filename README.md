# Development Environment Configuration

Personal configuration files and setup guides for Linux (Arch, Ubuntu) and macOS development environments.

## Repository Structure

```
dotfiles/
├── backend/                    # Backend development guides
│   └── django/
│       ├── deploy-django-production.md   # Gunicorn + Nginx + PostgreSQL deployment
│       └── django-querysets.md           # QuerySet API reference & optimisation
│
├── cachyos/                    # CachyOS (Arch) AI/ML workstation setup
│   ├── cachyos-setup-dev.md    # AMD GPU, ROCm, AI/ML stack, DevOps tooling
│   └── cachyos_dev_artifact.md # Alternative comprehensive setup reference
│
├── databases/                  # Database setup and reference
│   └── psql/
│       └── postgresql-setup-linux.md     # PostgreSQL: install → advanced reference
│
├── git-github/                 # Version control reference
│   ├── git-commands.md         # All Git commands with advanced topics
│   └── git-commands.pdf        # PDF version
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
├── neovim/                     # Neovim IDE setup
│   ├── README.md               # Quick start + full table of contents
│   └── docs/                   # 20-part guide: core → advanced
│       ├── INDEX.md
│       ├── 01-installation.md  ─┐
│       ├── 02-plugin-manager.md  │ Core Setup
│       ├── 03-lsp-setup.md      │
│       ├── 04-treesitter.md     │
│       ├── 05-completion.md    ─┘
│       ├── 06-mern-stack.md    ─┐
│       ├── 07-python-setup.md   │ Language Stacks
│       ├── 08-typescript-javascript.md
│       ├── 09-sql-databases.md  │
│       ├── 10-nosql-databases.md─┘
│       ├── 11-docker.md        ─┐
│       ├── 12-kubernetes.md     │ DevOps
│       ├── 13-terraform.md      │
│       ├── 14-git-integration.md│
│       ├── 15-cicd-tools.md    ─┘
│       ├── 16-debugging.md     ─┐
│       ├── 17-testing.md        │ Advanced
│       ├── 18-file-navigation.md│
│       ├── 19-themes-ui.md      │
│       └── 20-performance.md   ─┘
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
| Neovim | `neovim/docs/` (20 guides) | Full LSP, DAP, Treesitter, AI, DevOps |
| VS Code | `vscode/` (4 files) | Copilot, GitLens, 80+ extensions |
| Sublime Text | `sublime/` (3 files) | Python/Anaconda, Predawn theme |

### Backend & Databases

| File | Topics |
|------|--------|
| `backend/django/deploy-django-production.md` | Gunicorn, Nginx, SSL, PostgreSQL on VPS |
| `backend/django/django-querysets.md` | ORM: filter, annotate, Q/F objects, optimisation |
| `databases/psql/postgresql-setup-linux.md` | Install → roles → DCL/DDL/DML → indexes → backup |

### DevOps & AI/ML

| File | Topics |
|------|--------|
| `cachyos/cachyos-setup-dev.md` | AMD GPU (ROCm), PyTorch/TF, LangChain, Ollama, K8s, Terraform |

### Version Control

| File | Topics |
|------|--------|
| `git-github/git-commands.md` | Config → workflow → branching → remotes → advanced (worktrees, bisect, hooks) |

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

### 4. Neovim
```bash
# See neovim/README.md for full setup guide
mkdir -p ~/.config/nvim
# Follow neovim/docs/01-installation.md
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
