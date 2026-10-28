---
title: "14 Git and Version Control"
part: "01"
chapter: "14"
topic: git
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 14 Git and Version Control


## 14.1 Git Configuration

```bash
sudo pacman -S git

git config --global user.name "Your Name"
git config --global user.email "you@email.com"

# GPG signing
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# Aliases
git config --global alias.st "status -sb"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.ci "commit"
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.last "log -1 HEAD --stat"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.unstage "reset HEAD --"

# Defaults
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global fetch.prune true
git config --global diff.colorMoved zebra
git config --global merge.conflictstyle zdiff3
git config --global rerere.enabled true
```

## 14.2 Global .gitignore

```bash
cat > ~/.gitignore_global << 'EOF'
# OS
.DS_Store
Thumbs.db

# Editors
.idea/
.vscode/
*.swp
*.swo
*~

# Python
__pycache__/
*.pyc
*.pyo
.venv/
*.egg-info/
dist/
build/

# Node
node_modules/

# Environment
.env
.env.local
.env.*.local

# Docker
docker-compose.override.yml
EOF

git config --global core.excludesfile ~/.gitignore_global
```

## 14.3 GitHub CLI

```bash
sudo pacman -S github-cli
gh auth login       # Interactive browser auth
gh auth status      # Verify

gh repo create my-project --public --clone
gh pr create --title "feat: add search" --body "Adds semantic search"
gh pr list
gh issue create --title "Bug: API timeout"
gh release create v1.0.0
```

## 14.4 Conventional Commits

Format: `type(scope): description`

| Type | Use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change, no feature/fix |
| `test` | Adding tests |
| `chore` | Build/tools/dependencies |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

Branch naming: `feature/PROJ-123-add-search`, `bugfix/fix-login-crash`, `hotfix/patch-security`
