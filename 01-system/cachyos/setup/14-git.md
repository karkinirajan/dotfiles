---
title: "14 Git and Version Control"
part: "01"
chapter: "14"
topic: git
versions: [git, github-cli, lazygit]
last_verified: 2026-10-29
status: current
sources:
  - https://git-scm.com/docs/git-config
  - https://www.conventionalcommits.org/en/v1.0.0/
  - https://cli.github.com/manual/
---

# 14 Git and Version Control

## Purpose

A sane global Git setup, signed commits, the GitHub CLI and the commit message convention. Git <!-- v:git -->2.56.0<!-- /v --> and GitHub CLI <!-- v:github-cli -->2.102.1<!-- /v --> are the current Arch builds (gh upstream is at 2.103.3).

## 14.1 Git Configuration

```bash
sudo pacman -S git

git config --global user.name "Your Name"
git config --global user.email "you@email.com"

# Signing, option A: GPG
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# Signing, option B: SSH key (Git 2.34 or newer)
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git config --global gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers
gh ssh-key add ~/.ssh/id_ed25519.pub --type signing   # register it on GitHub as a signing key

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
git config --global push.autoSetupRemote true   # `git push` on a new branch creates the upstream (Git 2.37+)
git config --global fetch.prune true
git config --global diff.colorMoved zebra
git config --global merge.conflictstyle zdiff3
git config --global rerere.enabled true
```

Git 2.56 changed none of these defaults (Git 3.0 plans `main`, SHA-256 and reftable for new repositories, so keep `init.defaultBranch main`). `git config` keys are case-insensitive. Optional: `diff.algorithm histogram`, `branch.sort -committerdate`, `column.ui auto`. Label: `machine-only` for SSH signing (not run end to end).

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

Git already reads `~/.config/git/ignore` when `core.excludesFile` is unset, so writing the patterns there makes the config line unnecessary. A global ignore hides `.env`, `build/`, `dist/`, `.vscode/` and `docker-compose.override.yml` in every repository: review it before relying on it for a project that tracks any of them.

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

Format (Conventional Commits 1.0.0): `type(scope)!: description`, then an optional body and footers. `feat` (SemVer MINOR) and `fix` (PATCH) are the only types the specification mandates; the others are convention. A breaking change is marked with `!` before the colon or a `BREAKING CHANGE:` footer (MAJOR).

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
| `build` | Build system or dependencies |
| `style` | Formatting only |
| `revert` | Revert an earlier commit |

Branch naming: `feature/PROJ-123-add-search`, `bugfix/fix-login-crash`, `hotfix/patch-security`

## Verify

```bash
git --version
gh --version
git config --global --get push.autoSetupRemote
```

Expected: Git <!-- v:git -->2.56.0<!-- /v -->, gh <!-- v:github-cli -->2.102.1<!-- /v -->, `true`.

## Sources

- [git-config](https://git-scm.com/docs/git-config), [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/), [GitHub CLI manual](https://cli.github.com/manual/)
- Ledger: cluster C4, topics `git`, `gh`, `conventional-commits` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
