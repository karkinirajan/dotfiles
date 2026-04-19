# Documentation Index

Complete reference for all 20 Neovim setup guides.

---

## Core Setup

| # | File | Content |
|---|------|---------|
| 01 | [01-installation.md](01-installation.md) | Neovim install (Linux/macOS/Windows), Node.js, Python, Rust, Git, ripgrep, fd, lazygit |
| 02 | [02-plugin-manager.md](02-plugin-manager.md) | lazy.nvim bootstrap, plugin structure, lockfile, UI |
| 03 | [03-lsp-setup.md](03-lsp-setup.md) | Mason, nvim-lspconfig, keymaps, diagnostics, conform.nvim, nvim-lint |
| 04 | [04-treesitter.md](04-treesitter.md) | Parsers, syntax highlighting, text objects, incremental selection, folding |
| 05 | [05-completion.md](05-completion.md) | nvim-cmp, LuaSnip, friendly-snippets, sources, cmdline completion |

---

## Language Stacks

| # | File | Content |
|---|------|---------|
| 06 | [06-mern-stack.md](06-mern-stack.md) | TypeScript, React, Express, MongoDB, testing |
| 07 | [07-python-setup.md](07-python-setup.md) | Django, FastAPI, Flask, venv, pyright, ruff, debugging |
| 08 | [08-typescript-javascript.md](08-typescript-javascript.md) | typescript-tools, ESLint, Prettier, inlay hints, import management |

---

## Databases

| # | File | Content |
|---|------|---------|
| 09 | [09-sql-databases.md](09-sql-databases.md) | vim-dadbod, sqls, PostgreSQL, MySQL, SQLite |
| 10 | [10-nosql-databases.md](10-nosql-databases.md) | MongoDB, Redis integration |

---

## DevOps

| # | File | Content |
|---|------|---------|
| 11 | [11-docker.md](11-docker.md) | Dockerfile LSP, docker-compose, container management |
| 12 | [12-kubernetes.md](12-kubernetes.md) | kubectl.nvim, YAML LSP, Helm |
| 13 | [13-terraform.md](13-terraform.md) | Terraform LSP, formatting, linting |
| 14 | [14-git-integration.md](14-git-integration.md) | vim-fugitive, gitsigns, lazygit, diffview, git worktrees, GitHub |
| 15 | [15-cicd-tools.md](15-cicd-tools.md) | GitHub Actions schemas, GitLab CI, bashls, shellcheck, SchemaStore |

---

## Advanced Features

| # | File | Content |
|---|------|---------|
| 16 | [16-debugging.md](16-debugging.md) | nvim-dap for Python and JavaScript/TypeScript |
| 17 | [17-testing.md](17-testing.md) | Neotest adapters (pytest, Jest, Vitest), coverage, DAP integration |
| 18 | [18-file-navigation.md](18-file-navigation.md) | Telescope, Neo-tree, Harpoon, Flash.nvim, Oil.nvim |
| 19 | [19-themes-ui.md](19-themes-ui.md) | Catppuccin, lualine, bufferline, dashboard, indent guides, noice |
| 20 | [20-performance.md](20-performance.md) | Profiling, lazy-loading, large file handling, LSP & TS tuning |

---

## Quick Navigation

### By Task

**I want to set up LSP for a new language**
→ [03-lsp-setup.md](03-lsp-setup.md) → run `:MasonInstall <server>`

**I want better completions / snippets**
→ [05-completion.md](05-completion.md)

**I want to debug my code**
→ [16-debugging.md](16-debugging.md)

**I want to run tests inside Neovim**
→ [17-testing.md](17-testing.md)

**My Neovim is slow**
→ [20-performance.md](20-performance.md)

**I want a better UI / color scheme**
→ [19-themes-ui.md](19-themes-ui.md)

**I want to navigate files faster**
→ [18-file-navigation.md](18-file-navigation.md)

**I want Git integration**
→ [14-git-integration.md](14-git-integration.md)

**I'm setting up CI/CD YAML**
→ [15-cicd-tools.md](15-cicd-tools.md)

---

## Plugin Ecosystem at a Glance

### Core

| Plugin | Purpose |
|--------|---------|
| `lazy.nvim` | Plugin manager |
| `nvim-lspconfig` | LSP configuration |
| `mason.nvim` | LSP/tool installer |
| `nvim-treesitter` | Syntax + text objects |
| `nvim-cmp` + `LuaSnip` | Completion + snippets |

### UI

| Plugin | Purpose |
|--------|---------|
| `catppuccin` | Color scheme |
| `lualine.nvim` | Status line |
| `bufferline.nvim` | Buffer tab bar |
| `neo-tree.nvim` | File explorer |
| `noice.nvim` | Enhanced command UI |
| `which-key.nvim` | Keymap discovery |

### Navigation

| Plugin | Purpose |
|--------|---------|
| `telescope.nvim` | Fuzzy finder |
| `harpoon` | Quick file marks |
| `flash.nvim` | Screen motion jumps |
| `oil.nvim` | Filesystem as buffer |

### Development

| Plugin | Purpose |
|--------|---------|
| `conform.nvim` | Formatting |
| `nvim-lint` | Linting |
| `nvim-dap` | Debugging (DAP) |
| `neotest` | Test runner |
| `vim-fugitive` | Git client |
| `gitsigns.nvim` | Inline diff signs |
| `diffview.nvim` | Diff viewer |
| `lazygit.nvim` | Terminal Git UI |
