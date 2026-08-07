# Runtime Version Manager Reference (mise)

## Install mise

```sh
curl https://mise.run | sh
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc
```

---

## Core Commands

```sh
mise ls                        # list installed tools
mise ls --current              # show active versions
mise outdated                  # check for updates
mise upgrade                   # upgrade all tools
mise doctor                    # diagnose issues
```

---

## Node.js

```sh
mise use -g node@lts            # install + set global LTS
mise use -g node@22             # specific major
mise use node@20                # project-local (writes .mise.toml)
mise ls node                    # list installed node versions
node --version
```

---

## Python

```sh
mise use -g python@3.12         # install + set global
mise use python@3.11            # project-local
python3 --version
```

---

## Bun

```sh
mise use -g bun@latest
mise use bun@1.1
bun --version
```

---

## Go

```sh
mise use -g go@latest
mise use go@1.22
go version
```

---

## Ruby

```sh
mise use -g ruby@latest
mise use ruby@3.3
ruby --version
```

---

## Rust (via rustup, not mise)

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup update
rustup default stable
rustup install nightly
rustup show                     # list installed toolchains
rustc --version
```

---

## pnpm (Node package manager)

```sh
mise use -g pnpm@latest
pnpm --version
pnpm env use --global lts       # switch node via pnpm (if not using mise for node)
```

---

## uv (Python package/project manager)

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12          # install a python version
uv python pin 3.12              # pin for current project
uv python list                  # list available versions
uv venv                         # create virtualenv using pinned version
```

---

## Project-local config

```sh
# Creates/updates .mise.toml in current dir
mise use node@22
mise use python@3.12

# .mise.toml example:
# [tools]
# node = "22"
# python = "3.12"
# bun = "latest"
```

---

## Global config location

```
~/.config/mise/config.toml
```

---

## Switching versions

```sh
mise use -g node@18             # switch global
mise use node@18                # switch project-local
mise shell node@18              # switch for current shell session only
```

---

## Remove a version

```sh
mise uninstall node@18
mise uninstall python@3.10
```

---

## Add a plugin (for tools not built-in)

```sh
mise plugins install java
mise use -g java@21
```
