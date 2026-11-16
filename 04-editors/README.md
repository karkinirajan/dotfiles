# 04 · Editors

| Chapter | Path | Notes |
|---------|------|-------|
| VS Code | [`vscode/`](vscode/README.md) | Reference only: VS Code was uninstalled on 2026-11-11 and its seed entries left `manifest.conf`; settings, keybindings and `extensions.sh` stay for a reinstall |
| Zed | [`zed/`](zed/README.md) | Settings linked to `~/.config/zed/settings.json`; Ollama agent and MCP context servers (the Ollama provider needs the Ollama service, which is no longer installed) |
| Sublime Text | [`sublime/`](sublime/README.md) | The default opener for text and source files (see `mimeapps.list`); reference Python/Anaconda, REPL, and user preferences |

Zed (`link`) is managed by [`manifest.conf`](../manifest.conf), and so is the
default-application file `02-desktop/hyprland/mimeapps.list` that makes Sublime
Text the opener for text files. Neovim stays `$EDITOR`. Sublime Text files are
versioned here as reference configs and copied by hand; see
[`sublime/README.md`](sublime/README.md).
