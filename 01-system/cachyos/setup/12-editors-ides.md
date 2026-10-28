---
title: "12 Code Editors and IDEs"
part: "01"
chapter: "12"
topic: editors-ides
versions: [vscode, zed, neovim, pycharm]
last_verified: 2026-10-29
status: current
sources:
  - https://code.visualstudio.com/docs
  - https://zed.dev/docs/
  - https://www.lazyvim.org/
  - https://www.jetbrains.com/pycharm/
---

# 12 Code Editors and IDEs

## Purpose

Install notes for the editors in use. Tracked configuration lives in [`04-editors/`](../../../04-editors/README.md); this chapter covers installation and the package-source choices.

## 12.1 VS Code

Two builds exist. The Microsoft build (AUR `visual-studio-code-bin`, <!-- v:vscode -->1.144.0<!-- /v -->) uses the Visual Studio Marketplace and is required for Remote-SSH, Dev Containers, the C/C++ and C# Dev Kit extensions and Pylance. Arch's `code` (1.138.0) is Code - OSS and uses Open VSX. Microsoft's FAQ says other products may not use the Marketplace.

```bash
paru -S --needed visual-studio-code-bin   # Microsoft build
# or: sudo pacman -S code                 # Code - OSS, Open VSX
```

**Extensions.** The curated list is [`vscode-extensions.json`](../../../04-editors/vscode/vscode-extensions.json), installed with `04-editors/vscode/extensions.sh` (a failing ID is reported and skipped). Removed from it on 2026-10-29: IntelliCode (both IDs, deprecated, support ended) and `donjayamanne.python-environment-manager` (replaced by `ms-python.vscode-python-envs`, which `ms-python.python` bundles). `ms-python.python` now bundles Pylance, debugpy and python-envs, so those entries are optional. `Continue.continue` is unmaintained (read-only repository, last release 2.0.0) and is not recommended. `charliermarsh.ruff` and `ms-python.black-formatter` are both alive; pick one formatter (this repo's Python tooling is Ruff).

```bash
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension ms-azuretools.vscode-docker
code --install-extension eamodio.gitlens
code --install-extension ms-vscode-remote.remote-ssh
code --install-extension ms-vscode-remote.remote-containers
code --install-extension ms-toolsai.jupyter
code --install-extension rangav.vscode-thunder-client
code --install-extension bradlc.vscode-tailwindcss
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension usernamehw.errorlens
code --install-extension Gruntfuggly.todo-tree
code --install-extension PKief.material-icon-theme
```

The marketplace gives no machine-readable deprecation status, so about 60 of the IDs in the curated list could not be checked individually. <!-- UNVERIFIED: per-ID publish status of the remaining extensions -->

**`settings.json` essentials** (the full tracked file is seeded from `04-editors/vscode/vscode-settings.json`; two keys in it were wrong and were fixed: `typescript.inlayHints.returnTypes.enabled` is now `js/ts.inlayHints.functionLikeReturnTypes.enabled`, and `editor.findMatchHighlightLimit` does not exist and was removed. The `typescript.*`/`javascript.*` keys for parameter-name and variable-type hints, `importModuleSpecifier` and `suggest.autoImports` are deprecated in favour of the unified `js/ts.*` names but are still migrated):

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "[javascript][typescript][typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "python.analysis.typeCheckingMode": "standard",
  "files.autoSave": "onFocusChange",
  "terminal.integrated.defaultProfile.linux": "zsh",
  "git.autofetch": true,
  "workbench.iconTheme": "material-icon-theme"
}
```

The tracked file sets `python.analysis.typeCheckingMode` to `standard`, which is the current default. Label: `machine-only`.

## 12.2 Cursor (AI-first editor)

```bash
paru -S --needed cursor-bin
```

A VS Code fork with built-in AI features (AUR build 3.28.5; the CachyOS repo carries 3.27.14). It follows its own update cadence behind VS Code.

## 12.3 Zed

```bash
sudo pacman -S --needed zed
```

Zed <!-- v:zed -->1.25.3<!-- /v --> is Rust-based and GPU-accelerated, with a built-in agent panel and multiplayer editing. Python (basedpyright, ruff, ty), TypeScript, ESLint actions and Tailwind support are native; see [`04-editors/zed/README.md`](../../../04-editors/zed/README.md) for the settings and the retired default model.

## 12.4 Neovim and LazyVim

Neovim <!-- v:neovim -->0.12.6<!-- /v -->. LazyVim 16 needs Neovim 0.11.2 or newer built with LuaJIT, git 2.19 or newer, a C compiler, curl and `tree-sitter-cli`; a Nerd Font is optional.

```bash
sudo pacman -S --needed neovim tree-sitter-cli base-devel
[[ -e ~/.config/nvim ]] && echo "back up ~/.config/nvim, ~/.local/share/nvim, ~/.local/state/nvim and ~/.cache/nvim first"
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
nvim      # plugins install on first launch
# inside nvim: :LazyExtras (enable lang.python; pyright and ruff by default), then :LazyHealth
```

## 12.5 PyCharm

JetBrains merged the Community and Professional editions into one product (from 2025.1; migration in 2025.3): a free core tier, a 30-day Pro trial, and Pro on subscription. Two packages exist:

```bash
sudo pacman -S --needed pycharm-community-edition   # built from source, open-source parts only (no Django support)
paru -S --needed pycharm                            # unified PyCharm (replaces the removed pycharm-professional)
```

The Arch `pycharm-community-edition` (<!-- v:pycharm -->2026.2.3<!-- /v -->) is **not** the unified free tier, and "Free - Python + Django" in the previous text was wrong: Django tooling is not in the open-source build. `pycharm-professional` no longer exists in the AUR.

## 12.6 VSCodium (telemetry-free)

```bash
paru -S --needed vscodium-bin
```

VSCodium uses Open VSX by default, so Microsoft-only extensions are unavailable (same constraint as Code - OSS).

## Verify

```bash
code --version
zed --version
nvim --version | head -1
```

Expected: VS Code <!-- v:vscode -->1.144.0<!-- /v --> (Microsoft build), Zed <!-- v:zed -->1.25.3<!-- /v -->, Neovim <!-- v:neovim -->0.12.6<!-- /v -->.

## Sources

- [VS Code FAQ on the Marketplace](https://code.visualstudio.com/docs/supporting/faq), [LazyVim installation](https://www.lazyvim.org/installation), [Zed docs](https://zed.dev/docs/)
- Ledger: cluster C7, topics `VS Code`, `Zed`, `Neovim`, `PyCharm` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
