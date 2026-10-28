---
title: "03 Python Environment with uv"
part: "01"
chapter: "03"
topic: python-uv
versions: [python, uv, ruff, ruff-pre-commit, pre-commit-hooks]
last_verified: 2026-10-29
status: current
sources:
  - https://docs.astral.sh/uv/
  - https://docs.astral.sh/ruff/configuration/
  - https://devguide.python.org/versions/
  - https://github.com/astral-sh/ruff-pre-commit
---

# 03 Python Environment with uv

## Purpose

Python on Arch/CachyOS without touching the system interpreter: uv for interpreters, projects and tools, ruff and pre-commit for quality gates.

## Prerequisites

- System Python <!-- v:python -->3.14.8<!-- /v --> from pacman (3.14 is supported until 2030-10; free-threaded builds come from uv, not the Arch package). Arch marks the interpreter externally managed (PEP 668), so a global `pip install` fails with `externally-managed-environment`.

## 3.1 Why uv

uv always works inside virtual environments, replaces pyenv (versions), pipx (tool isolation) and pip-tools (lockfiles), and writes `uv.lock` for reproducible builds.

```bash
sudo pacman -S --needed uv        # tracked in packages/cli.txt
```

Add to `~/.zshrc` (the tracked file already does):

```bash
export PATH="$HOME/.local/bin:$PATH"
eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"
```

Since uv 0.13.0 a bare `uv python install` fetches Python 3.15; pass the version you want. uv prefers its own managed interpreters over the system one, so `uvx` tools run on the newest managed Python unless you pass `--python 3.14` or set `UV_PYTHON`.

## 3.2 Python version management

```bash
uv python install 3.12 3.13    # install managed versions
uv python list                 # available and installed
uv python pin 3.12             # writes .python-version
uv python find                 # active interpreter
```

Python 3.13 and 3.12 are security-only now (EOL 2029-10 and 2028-10). A plain `uv add` on the system 3.14 resolved every package group used in chapters 05 and 10 as binary wheels, so no compiler is needed. Do not make 3.15 a project default yet: some packages (for example `pyyaml`, `prefect`, `apache-airflow`) do not resolve on it.

## 3.3 Project workflow

`uv init` makes a **packaged** project since uv 0.12 (`src/<name>/`, `uv_build` backend, `[project.scripts]`); use `--no-package` for the flat layout.

```bash
uv init my-project --python 3.14   # create a project; 3.12 still works
cd my-project

uv add django fastapi 'uvicorn[standard]'   # dependencies
uv add --dev pytest ruff ipykernel          # dev dependencies (a [dependency-groups] dev table)
uv run pytest                               # run in the project venv
uv sync                                     # sync from the lockfile (CI, teammates)
uv lock --check                             # lockfile matches pyproject
uv export --format requirements-txt --no-emit-project > requirements.txt   # Docker or legacy
uv tree                                     # dependency tree
```

`uv export` includes the project itself as `-e .` unless you pass `--no-emit-project`. Label: the commands above were run in the sandbox against uv 0.13.6 (`verified-in-cloud`).

## 3.4 Global CLI tools (replaces pipx)

```bash
uv tool install ruff           # linter and formatter
uv tool install jupyterlab     # exposes jupyter-lab, not `jupyter`; see 3.7
uv tool install httpie
uv tool install pre-commit
uv tool install mypy
uv tool install ipython
uv tool install ansible-core   # `ansible` (the community bundle) only installs ansible-community; pacman ansible is in developer.txt

uv tool list
uv tool upgrade --all
```

Run once without installing: `uvx ruff check .`. Arch also packages ruff (<!-- v:ruff -->0.17.3<!-- /v -->), pyright and mypy if you prefer pacman for editor-facing tools.

## 3.5 Ruff

Ruff <!-- v:ruff -->0.17.3<!-- /v --> replaces black, flake8, isort and pyflakes. Breaking changes since the old text: 0.15 introduced the 2026 formatter style; 0.16 raised the default rule set from 59 to 413 rules and turned on formatting of Markdown code blocks; 0.17 defaults `target-version` to py311, dropped the DTZ rules from the defaults and removed `ruff-lsp`. `select` **replaces** the default set (use `extend-select` to add to it), and `target-version` can be dropped when `requires-python` is set.

```bash
uv tool install ruff
```

`pyproject.toml` (all keys load in 0.17.3):

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "W"]

[tool.ruff.format]
quote-style = "double"
```

`ruff.toml` takes the same schema without the `tool.ruff` prefix (`[lint]`, `[format]`); in one directory `.ruff.toml` beats `ruff.toml` beats `pyproject.toml`.

```bash
ruff check . --fix
ruff format .
```

## 3.6 Pre-commit hooks

`.pre-commit-config.yaml` (tags from the upstream repositories; `ruff-check` is the hook id, `ruff` remains as a legacy alias):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.3
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

Current tags: ruff-pre-commit <!-- v:ruff-pre-commit -->v0.17.3<!-- /v -->, pre-commit-hooks <!-- v:pre-commit-hooks -->v6.0.0<!-- /v -->. The config ran under pre-commit 4.7.0 in the sandbox. Because `ruff-format` now also rewrites ` ```python ` fences inside Markdown, add `types_or: [python, pyi]` to that hook in repositories that are mostly documentation.

```bash
pre-commit install
pre-commit run --all-files
```

## 3.7 Jupyter

```bash
# Option A: inside a project (recommended)
uv add --dev ipykernel
uv run --with jupyter jupyter lab

# Option B: global tool. The uv-installed environment exposes `jupyter-lab` only
uv tool install jupyterlab --with-executables-from jupyter-core   # adds the `jupyter` command
uv run ipython kernel install --user --name=my-project
jupyter lab
```

JupyterLab 4.6 is current. Label: Option A is `verified-in-cloud` (resolution and `jupyter-lab` startup path); Option B needs the host.

## Verify

```bash
uv --version
python --version
uv python list
```

Expected: uv <!-- v:uv -->0.13.6<!-- /v -->, system Python <!-- v:python -->3.14.8<!-- /v -->, and the managed versions you installed.

## Sources

- [uv documentation and changelog](https://docs.astral.sh/uv/)
- [Ruff configuration](https://docs.astral.sh/ruff/configuration/)
- [Python version status](https://devguide.python.org/versions/)
- Ledger: cluster C4, topics `python-versions`, `uv`, `ruff`, `pre-commit` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
