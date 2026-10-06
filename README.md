# Dotfiles

Personal configuration for a CachyOS (Arch) Wayland workstation — Hyprland +
Noctalia desktop, kitty/zsh terminal, editors, local LLM inference, and the
tooling around them.

Read it like a book. Each numbered **part** is a folder, each part's
`README.md` is its introduction, and each **chapter** is a subfolder with its
own README. Start at Part 00 and go in order, or jump to the part you need.

---

## Contents

| Part | Folder | Covers |
|------|--------|--------|
| **00** | [Start here](#00--start-here) | install, layout, how the repo stays in sync |
| **01** | [`01-system/`](01-system/README.md) | the OS: packages, backups, update automation |
| **02** | [`02-desktop/`](02-desktop/README.md) | the graphical session: Hyprland, Noctalia, fonts |
| **03** | [`03-terminal/`](03-terminal/README.md) | shells, terminal emulators, prompts |
| **04** | [`04-editors/`](04-editors/README.md) | VS Code, Zed, Sublime |
| **05** | [`05-ai/`](05-ai/README.md) | Claude Code, local LLMs (Ollama), and AI resources |
| **06** | [`06-tools/`](06-tools/README.md) | standalone utilities: the focus site-blocker |
| **99** | [Appendix](#99--appendix) | reference material and the links behind it |

### 00 · Start here

| Chapter | File |
|---------|------|
| How the repo is wired to your home directory | [`manifest.conf`](manifest.conf) — the map: `<type> <repo path> <live path>` |
| The installer | [`install.sh`](install.sh) — link, seed, status, pull, restore |

### 01 · System — [`01-system/`](01-system/README.md)

| Chapter | Path |
|---------|------|
| CachyOS setup walkthrough (AMD GPU, toolchains, Kubernetes, Terraform) | [`01-system/cachyos/setup.md`](01-system/cachyos/setup.md) |
| Package lists: desktop, fonts, AI stack | [`01-system/cachyos/packages/`](01-system/cachyos/packages/) |
| Timeshift daily snapshots | [`01-system/timeshift/`](01-system/timeshift/README.md) |
| topgrade — update everything | [`01-system/topgrade/`](01-system/topgrade/README.md) |

### 02 · Desktop — [`02-desktop/`](02-desktop/README.md)

| Chapter | Path |
|---------|------|
| Hyprland compositor, Noctalia shell, keybinds, scripts | [`02-desktop/hyprland/`](02-desktop/hyprland/README.md) |
| Plasma removal log | [`02-desktop/hyprland/KDE-REMOVAL.md`](02-desktop/hyprland/KDE-REMOVAL.md) |
| Font rendering rules | [`02-desktop/fonts/`](02-desktop/fonts/fontconfig/fonts.conf) |

### 03 · Terminal — [`03-terminal/`](03-terminal/README.md)

| Chapter | Path |
|---------|------|
| zsh (starship/p10k toggle, deferred plugins) | [`03-terminal/zsh/`](03-terminal/zsh/.zshrc) |
| bash | [`03-terminal/bash/`](03-terminal/bash/.bashrc) |
| kitty (with catppuccin and gruvbox themes) | [`03-terminal/kitty/`](03-terminal/kitty/kitty.conf) |
| Alacritty | [`03-terminal/alacritty/`](03-terminal/alacritty/SHORTCUTS.md) |
| starship prompt | [`03-terminal/starship/`](03-terminal/starship/starship.toml) |

### 04 · Editors — [`04-editors/`](04-editors/README.md)

| Chapter | Path |
|---------|------|
| VS Code | [`04-editors/vscode/`](04-editors/vscode/) |
| Zed | [`04-editors/zed/`](04-editors/zed/README.md) |
| Sublime Text | [`04-editors/sublime/`](04-editors/sublime/) |

### 05 · AI — [`05-ai/`](05-ai/README.md)

| Chapter | Path |
|---------|------|
| Claude Code: global instructions, subagents, skills, settings | [`05-ai/claude-code/`](05-ai/claude-code/README.md) |
| Ollama: ROCm and Vulkan backends, systemd drop-ins, benchmarks | [`05-ai/ollama/`](05-ai/ollama/README.md) |
| Reading list and reference projects | [`05-ai/RESOURCES.md`](05-ai/RESOURCES.md) |

### 06 · Tools — [`06-tools/`](06-tools/README.md)

| Chapter | Path |
|---------|------|
| focus: dnsmasq + nftables site blocker with schedule and lock mode | [`06-tools/focus/`](06-tools/focus/README.md) |

### 99 · Appendix

| Item | File |
|------|------|
| Licence | [`LICENSE`](LICENSE) |

---

## Conventions

These rules keep the repo predictable as it grows:

- **Folders are numbered by reading order**, `NN-name/`. Numbers only change
  when a part is added or moved, and nothing else depends on them.
- **Folders and files are lowercase kebab-case**, except files a program
  requires verbatim (`.zshrc`, `CLAUDE.md`, `SKILL.md`, `README.md`).
- **Each part and chapter has a README** that says what it is, how it is
  wired in, and what to run. A folder without one should not exist.
- **Config lives with its tool, not in a bucket.** Anything a program reads
  from a fixed path is listed in `manifest.conf`. Anything not listed is
  reference material and is labelled as such.
- **Runtime state is never tracked.** `.gitignore` covers caches, logs,
  session data and the installer's own backups.

---

## Install

```bash
git clone git@github.com:karkinirajan/dotfiles.git ~/dotfiles && cd ~/dotfiles

./install.sh --dry-run     # show what would change, touch nothing
./install.sh               # link/seed everything in manifest.conf
./install.sh status        # report ok / drift / missing per entry
```

An existing real file is moved to `<path>.bak-<timestamp>` before it is
replaced, so a first run on a machine that already has configs is safe.
A symlink that points somewhere else is skipped unless you pass `--force`.

Install the packages before the configs. The configs name fonts and helper
binaries and fail quietly without them:

```bash
sudo pacman -S --needed $(grep -v '^#' 01-system/cachyos/packages/desktop.txt | awk '{print $1}')
sudo pacman -S --needed $(grep -v '^#' 01-system/cachyos/packages/fonts.txt   | awk '{print $1}')
paru        -S --needed $(grep    '(AUR)' 01-system/cachyos/packages/*.txt    | awk '{print $1}')
```

Then follow [`02-desktop/hyprland/README.md`](02-desktop/hyprland/README.md)
for the parts the manifest does not cover (hyprpm plugins, the D-Bus
notification override).

---

## Two kinds of managed file

`manifest.conf` marks every entry `link` or `seed`:

| | `link` | `seed` |
|---|---|---|
| What it does | symlinks live → repo | copies repo → live, only if live is missing |
| Can it drift? | **No** — one file, two names | **Yes** — two separate files |
| Used for | configs only you edit | files a program rewrites itself |

For a seeded file, each direction is a deliberate step:

```bash
./install.sh status        # DRIFT on a seeded file = live has moved ahead
./install.sh pull          # live → repo: capture what you changed
git diff                   # review, then commit

./install.sh restore       # repo → live: put the tracked version back
```

`restore` backs up the live file first. To return to an older state, check
that version out of git, restore it, then drop the checkout:

```bash
git checkout <commit> -- 02-desktop/hyprland/noctalia/state/settings.toml
./install.sh restore
git checkout HEAD -- 02-desktop/hyprland/noctalia/state/settings.toml
```

**For Noctalia, use `02-desktop/hyprland/hypr/scripts/noctalia-restore.sh`
instead.** It does the same job but stops the shell first, because a config
restored underneath a running Noctalia gets overwritten from memory:

```bash
~/.config/hypr/scripts/noctalia-restore.sh              # the tracked version
~/.config/hypr/scripts/noctalia-restore.sh HEAD~3       # three commits back
~/.config/hypr/scripts/noctalia-restore.sh --list       # available restore points
```

This matters most for `~/.local/state/noctalia/settings.toml`, which Noctalia
rewrites itself. A symlink there would be destroyed by a replace-style write,
which is why that file is seeded.

---

## License

MIT License — see [LICENSE](LICENSE).
