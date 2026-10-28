---
title: "03 Python Environment with uv"
part: "01"
chapter: "03"
topic: python-uv
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 03 Python Environment with uv


## 3.1 Why uv

On Arch/CachyOS, `pip install` globally throws `error: externally-managed-environment` (PEP 668). **uv solves this permanently:**

- Always operates inside virtual environments
- 10-100× faster than pip (Rust implementation + global cache)
- Replaces pyenv (version management), pipx (tool isolation), pip-tools (lockfiles)
- Generates `uv.lock` for reproducible builds

```bash
# Installed via pacman on CachyOS (tracked in packages/cli.txt):
sudo pacman -S uv
```

Add to `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"
```

## 3.2 Python Version Management

```bash
uv python install 3.12 3.13    # Install versions
uv python list                  # List all available/installed
uv python pin 3.12              # Pin project (creates .python-version)
uv python find                  # Show active Python path
```

## 3.3 Project Workflow

```bash
uv init my-project --python 3.12   # Create project
cd my-project

uv add django fastapi uvicorn[standard]   # Add dependencies
uv add --dev pytest ruff ipykernel        # Dev dependencies
uv run python manage.py runserver         # Run in project venv
uv run pytest                             # Run tests
uv sync                                   # Sync from lockfile (CI/teammates)
uv export --format requirements-txt > requirements.txt   # Docker/legacy
uv tree                                   # Dependency tree
```

## 3.4 Global CLI Tools (replaces pipx)

```bash
uv tool install ruff         # Linter + formatter (replaces black, flake8, isort)
uv tool install jupyterlab   # Jupyter notebook server
uv tool install httpie       # Modern HTTP client
uv tool install pre-commit   # Git hook manager
uv tool install mypy         # Static type checker
uv tool install ipython      # Enhanced Python REPL
uv tool install ansible      # Configuration management

uv tool list                 # Show installed tools
uv tool upgrade --all        # Upgrade everything
```

**Run tools ephemerally without installing:**

```bash
uvx ruff check .      # Run ruff once
uvx black --check .   # Run black once
```

## 3.5 Ruff — All-in-One Linter & Formatter

Replaces black, flake8, isort, pyflakes, and more — 30-100× faster.

```bash
uv tool install ruff
```

`pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "W"]

[tool.ruff.format]
quote-style = "double"
```

```bash
ruff check . --fix   # Lint and auto-fix
ruff format .        # Format (Black-compatible)
```

## 3.6 Pre-commit Hooks

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

```bash
pre-commit install            # Install hooks
pre-commit run --all-files    # Run on all files now
```

## 3.7 Jupyter Notebook/Lab

```bash
# Option A — Within project (recommended):
uv add --dev ipykernel
uv run --with jupyter jupyter lab

# Option B — Global tool:
uv tool install jupyterlab
uv run ipython kernel install --user --name=my-project
jupyter lab
```
