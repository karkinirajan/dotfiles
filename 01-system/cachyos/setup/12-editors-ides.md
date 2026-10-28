---
title: "12 Code Editors and IDEs"
part: "01"
chapter: "12"
topic: editors-ides
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 12 Code Editors and IDEs


## 12.1 VS Code ⭐

```bash
paru -S visual-studio-code-bin   # Microsoft build (full marketplace, Copilot, Remote Dev)
sudo pacman -S code               # Open-source build (Open VSX marketplace)
```

**Install all essential extensions:**

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-azuretools.vscode-docker
code --install-extension eamodio.gitlens
code --install-extension ms-vscode-remote.remote-ssh
code --install-extension ms-vscode-remote.remote-containers
code --install-extension ms-toolsai.jupyter
code --install-extension Continue.continue
code --install-extension rangav.vscode-thunder-client
code --install-extension bradlc.vscode-tailwindcss
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension usernamehw.errorlens
code --install-extension Gruntfuggly.todo-tree
code --install-extension PKief.material-icon-theme
```

**`settings.json`:**

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
  "python.analysis.typeCheckingMode": "basic",
  "files.autoSave": "onFocusChange",
  "terminal.integrated.defaultProfile.linux": "zsh",
  "git.autofetch": true,
  "workbench.iconTheme": "material-icon-theme"
}
```

## 12.2 Cursor (AI-First Editor)

```bash
paru -S cursor-bin
```

VS Code fork with deep Claude/GPT-4 integration for code generation, editing, and chat.

## 12.3 Zed (Modern GPU-Accelerated Editor)

```bash
sudo pacman -S zed
```

Built in Rust, extremely fast, built-in AI assistant, multiplayer editing.

## 12.4 Neovim + LazyVim

```bash
sudo pacman -S neovim
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
nvim   # Plugins auto-install on first launch
# Type :LazyExtras and enable lang.python
```

## 12.5 PyCharm

```bash
sudo pacman -S pycharm-community-edition   # Free — Python + Django
paru -S pycharm-professional               # Paid — FastAPI, Docker, DB tools, Remote Dev
```

## 12.6 VS Codium (Telemetry-Free)

```bash
paru -S vscodium-bin
```
