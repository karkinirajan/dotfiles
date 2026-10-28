# 03.1 · Zsh

Interactive login shell configuration for CachyOS (`03-terminal/zsh/.zshrc`),
plus archived reference configs for macOS and Ubuntu.

```
03-terminal/zsh/
├── README.md       ← you are here
├── .zshrc          → ~/.zshrc (linked via manifest.conf)
├── macos.zshrc     # reference config for macOS hosts (not linked)
└── ubuntu.zshrc    # reference config for Ubuntu/Debian hosts (not linked)
```

## Highlights of `.zshrc`

- **Prompt:** [`starship`](../starship/README.md) (`ZSH_THEME=""` in Oh My Zsh
  so OMZ never loads a competing theme).
- **Fast startup:** Heavy completions (`kubectl`, `helm`, `minikube`, `terraform`,
  `aws`, `gh`, `docker`, `cargo`, `rustup`, `pip`) are lazy-loaded on first tab
  completion; syntax highlighting and autosuggestions are deferred via `zsh-defer`.
- **Tool integrations:** `zoxide`, `fzf` (paired with [`03-terminal/fzf/preview.sh`](../fzf/README.md)),
  `atuin`, `direnv`, `nvm` (`/usr/share/nvm`), `pnpm`, `uv`, and `sccache`.
- **Local LLM helpers:** `ccl` (`cc-local` / `gemma4:12b`) and `cclf` (`cc-fast`
  / `qwen3-coder:30b`) run Claude Code against the local Ollama instance without
  polluting the global environment.

## Verify

```sh
zsh -n ~/.zshrc
```
