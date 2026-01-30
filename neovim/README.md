# Neovim Full-Stack Development Setup Guide

> A comprehensive guide to configuring Neovim for modern full-stack development with MERN, Python (Django/FastAPI/Flask), SQL/NoSQL databases, and DevOps tooling.

## 📚 Table of Contents

### Core Setup

- [Installation & Prerequisites](./docs/01-installation.md)
- [Plugin Manager (lazy.nvim)](./docs/02-plugin-manager.md)
- [LSP Configuration](./docs/03-lsp-setup.md)
- [Treesitter Configuration](./docs/04-treesitter.md)
- [Autocompletion Setup](./docs/05-completion.md)

### Language-Specific Configurations

- [MERN Stack Setup](./docs/06-mern-stack.md)
  - MongoDB, Express, React, Node.js
- [Python Development](./docs/07-python-setup.md)
  - Django, FastAPI, Flask
  - Virtual Environment Management
- [TypeScript/JavaScript](./docs/08-typescript-javascript.md)

### Database Development

- [SQL Databases](./docs/09-sql-databases.md)
  - PostgreSQL, MySQL, SQLite
- [NoSQL Databases](./docs/10-nosql-databases.md)
  - MongoDB, Redis

### DevOps Tools

- [Docker Integration](./docs/11-docker.md)
- [Kubernetes Setup](./docs/12-kubernetes.md)
- [Terraform Configuration](./docs/13-terraform.md)
- [Git & GitHub Integration](./docs/14-git-integration.md)
- [CI/CD Tools](./docs/15-cicd-tools.md)

### Advanced Features

- [Debugging (DAP)](./docs/16-debugging.md)
- [Testing Integration](./docs/17-testing.md)
- [File Explorer & Navigation](./docs/18-file-navigation.md)
- [Themes & UI](./docs/19-themes-ui.md)
- [Performance Optimization](./docs/20-performance.md)

### Complete Configurations

- [Minimal Config (~200 lines)](./configs/minimal-config.lua)
- [Full-Featured Config](./configs/full-config.lua)
- [Project-Specific Configs](./configs/)

## 🎯 Quick Start

```bash
# 1. Install Neovim 0.11+
brew install neovim  # macOS
snap install neovim  # Ubuntu

# 2. Backup existing config
mv ~/.config/nvim ~/.config/nvim.backup

# 3. Clone minimal config
mkdir -p ~/.config/nvim
cp configs/minimal-config.lua ~/.config/nvim/init.lua

# 4. Start Neovim (plugins auto-install)
nvim
```

## 🔧 Tech Stack Covered

### Frontend

- React, Vue, Angular
- TypeScript, JavaScript
- HTML, CSS, Tailwind
- Vite, Webpack

### Backend

- Node.js, Express
- Python (Django, FastAPI, Flask)
- REST APIs, GraphQL

### Databases

- PostgreSQL, MySQL, SQLite
- MongoDB, Redis
- SQL language server

### DevOps

- Docker, Docker Compose
- Kubernetes, Helm
- Terraform, Ansible
- GitHub Actions, GitLab CI

## 📋 Prerequisites

- Neovim >= 0.11.0
- Git
- Node.js >= 18.x (for LSP servers)
- Python >= 3.8
- Rust (for some tools)
- ripgrep, fd (optional but recommended)

## 🌟 Key Features

### LSP & Completion

- **Mason.nvim**: Install & manage LSP servers
- **nvim-lspconfig**: Configure language servers
- **nvim-cmp**: Intelligent autocompletion
- **Treesitter**: Enhanced syntax highlighting

### Development Tools

- **Telescope**: Fuzzy finder
- **nvim-dap**: Debug Adapter Protocol
- **conform.nvim**: Code formatting
- **nvim-lint**: Linting support

### Database Tools

- **vim-dadbod**: Database interaction
- **sqls**: SQL language server
- **dbout.nvim**: Database management UI

### DevOps Integration

- **devops-tools.nvim**: Docker, Kubernetes, Terraform
- **kubectl.nvim**: Kubernetes management
- **fugitive**: Git integration

## 📖 Documentation Structure

Each guide includes:

- ✅ Installation instructions
- ⚙️ Configuration examples
- 🔑 Key mappings
- 💡 Usage tips
- 🐛 Troubleshooting

## 🚀 Philosophy

This setup prioritizes:

1. **Performance**: Fast startup (<100ms)
2. **Modularity**: Easy to customize
3. **Standards**: Uses LSP, DAP, Treesitter
4. **Minimal Dependencies**: Only essential plugins
5. **Production-Ready**: Battle-tested configurations

## 🤝 Contributing

Found an issue or improvement? Feel free to submit a PR or open an issue.

## 📝 License

MIT License - Feel free to use and modify

## 🔗 Resources

- [Neovim Documentation](https://neovim.io/doc/)
- [LSP Server List](https://microsoft.github.io/language-server-protocol/implementors/servers/)
- [Mason Registry](https://mason-registry.dev/)
- [Treesitter Parsers](https://github.com/nvim-treesitter/nvim-treesitter#supported-languages)

---

**Last Updated**: January 2025  
**Neovim Version**: 0.11+
