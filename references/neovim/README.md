# Neovim Full-Stack Development Setup

> A complete guide to configuring Neovim as a production-ready IDE for full-stack
> development: MERN, Python (Django/FastAPI/Flask), SQL/NoSQL databases, DevOps,
> and AI-assisted development.

## Quick Start

```bash
# 1. Install Neovim 0.11+
brew install neovim        # macOS
sudo pacman -S neovim      # Arch
sudo snap install nvim --classic  # Ubuntu

# 2. Backup existing config
mv ~/.config/nvim ~/.config/nvim.backup.$(date +%Y%m%d)

# 3. Create config directory
mkdir -p ~/.config/nvim

# 4. Start Neovim — lazy.nvim bootstraps automatically
nvim
```

---

## Table of Contents

### Core Setup

| # | Guide | Topics |
|---|-------|--------|
| 01 | [Installation & Prerequisites](./docs/01-installation.md) | Neovim, Node.js, Python, Rust, Git, ripgrep, fd, lazygit, clipboard |
| 02 | [Plugin Manager (lazy.nvim)](./docs/02-plugin-manager.md) | Bootstrap, plugin structure, UI, lockfile, performance flags |
| 03 | [LSP Configuration](./docs/03-lsp-setup.md) | Mason, nvim-lspconfig, keymaps, diagnostics, conform.nvim, nvim-lint |
| 04 | [Treesitter](./docs/04-treesitter.md) | Parsers, highlighting, text objects, incremental selection, folding |
| 05 | [Autocompletion](./docs/05-completion.md) | nvim-cmp, LuaSnip, friendly-snippets, sources, cmdline completion |

### Language Stacks

| # | Guide | Topics |
|---|-------|--------|
| 06 | [MERN Stack](./docs/06-mern-stack.md) | React, Node.js, Express, MongoDB, testing |
| 07 | [Python Development](./docs/07-python-setup.md) | Django, FastAPI, Flask, venv, pyright, ruff, debugging |
| 08 | [TypeScript & JavaScript](./docs/08-typescript-javascript.md) | typescript-tools, ESLint, Prettier, inlay hints, imports |

### Databases

| # | Guide | Topics |
|---|-------|--------|
| 09 | [SQL Databases](./docs/09-sql-databases.md) | vim-dadbod, sqls, PostgreSQL, MySQL, SQLite |
| 10 | [NoSQL Databases](./docs/10-nosql-databases.md) | MongoDB, Redis |

### DevOps

| # | Guide | Topics |
|---|-------|--------|
| 11 | [Docker](./docs/11-docker.md) | Dockerfile LSP, docker-compose, container management |
| 12 | [Kubernetes](./docs/12-kubernetes.md) | kubectl.nvim, YAML LSP, Helm |
| 13 | [Terraform](./docs/13-terraform.md) | Terraform LSP, formatting, linting |
| 14 | [Git & GitHub](./docs/14-git-integration.md) | vim-fugitive, gitsigns, lazygit, diffview, worktrees, Octo |
| 15 | [CI/CD Tools](./docs/15-cicd-tools.md) | GitHub Actions schemas, GitLab CI, bashls, shellcheck, SchemaStore |

### Advanced Features

| # | Guide | Topics |
|---|-------|--------|
| 16 | [Debugging (DAP)](./docs/16-debugging.md) | nvim-dap, Python debugger, JS/TS debugger, UI |
| 17 | [Testing](./docs/17-testing.md) | Neotest (pytest, Jest, Vitest), coverage, debug tests |
| 18 | [File Navigation](./docs/18-file-navigation.md) | Telescope, Neo-tree, Harpoon, Flash.nvim, Oil.nvim |
| 19 | [Themes & UI](./docs/19-themes-ui.md) | Catppuccin, lualine, bufferline, dashboard, noice, which-key |
| 20 | [Performance](./docs/20-performance.md) | Profiling, lazy-loading, large files, LSP tuning, startup < 100ms |

---

## Prerequisites

- **Neovim** >= 0.11.0
- **Git**
- **Node.js** >= 18.x (for LSP servers)
- **Python** >= 3.10
- **Rust** (for some tools)
- **ripgrep**, **fd** (for Telescope)
- A **Nerd Font** (for icons — e.g. JetBrainsMono Nerd Font)

---

## Key Features

### Core IDE

- **Mason.nvim** — install and manage 200+ LSP servers, formatters, linters
- **nvim-lspconfig** — zero-config LSP setup for 90+ languages
- **nvim-cmp** — intelligent autocompletion with 10+ sources
- **LuaSnip** + **friendly-snippets** — 2000+ community snippets
- **Treesitter** — semantic syntax, text objects, incremental selection
- **conform.nvim** — format on save (Prettier, Black, stylua, shfmt…)
- **nvim-lint** — async linting (ESLint, Ruff, shellcheck, hadolint…)

### Navigation

- **Telescope** — fuzzy find files, grep, LSP symbols, git
- **Harpoon** — instant jump between marked files
- **Flash.nvim** — label-based screen motions
- **Neo-tree** — sidebar file explorer with git status
- **Oil.nvim** — edit the filesystem as a buffer

### Development

- **nvim-dap** — Debug Adapter Protocol (breakpoints, watches, REPL)
- **Neotest** — test runner for pytest, Jest, Vitest, Go, Rust
- **vim-fugitive** + **gitsigns** + **diffview** — full Git workflow
- **vim-dadbod** — database client (PostgreSQL, MySQL, SQLite, MongoDB)
- **typescript-tools** — TypeScript power features (import org, rename file)

### UI

- **Catppuccin** — beautiful, well-integrated color scheme
- **lualine** — fast, configurable status line
- **bufferline** — VSCode-style buffer tabs
- **noice.nvim** — enhanced command-line and notification UI
- **which-key** — discover keymaps on the fly

---

## Philosophy

1. **Performance** — startup < 100ms with aggressive lazy-loading
2. **Modularity** — each plugin in its own file, easy to add/remove
3. **Standards** — LSP, DAP, and Treesitter over custom hacks
4. **Minimal** — only plugins that provide clear value
5. **Production-ready** — battle-tested configurations

---

## Resources

- [Neovim Documentation](https://neovim.io/doc/)
- [Mason Registry](https://mason-registry.dev/)
- [LSP Server List](https://microsoft.github.io/language-server-protocol/implementors/servers/)
- [Treesitter Parsers](https://github.com/nvim-treesitter/nvim-treesitter#supported-languages)
- [lazy.nvim Documentation](https://lazy.folke.io/)
- [awesome-neovim](https://github.com/rockerBOO/awesome-neovim)

---

**Last Updated**: April 2026 | **Neovim Version**: 0.11+
