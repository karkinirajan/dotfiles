# Dotfiles

Personal configuration for a CachyOS (Arch) Wayland workstation: Hyprland +
Noctalia desktop, kitty/zsh terminal, editors, and the tooling around them.

The repo is the single source of truth. `install.sh` reads `manifest.conf` and
symlinks each live path back into the repo, so editing either side edits the
same file and the two cannot drift apart.

```
dotfiles/
├── install.sh              # link/seed everything; also `status` and `pull`
├── manifest.conf           # the map: <type> <repo path> <live path>
│
├── wm/hyprland/            # Hyprland compositor + Noctalia shell  → see its README
│   ├── hypr/               # hyprland.conf, config/, scripts/, hyprlock, hypridle
│   ├── noctalia/           # bar/shell settings.toml, custom palettes, dbus override
│   ├── sddm/               # login manager session preset
│   ├── README.md           # the detailed one — read this for the desktop
│   ├── KDE-REMOVAL.md      # how Plasma was removed from this dual-DE install
│   └── hyprland-shortcuts.md
│
├── fonts/
│   └── fontconfig/fonts.conf   → ~/.config/fontconfig/fonts.conf
│                           # rendering rules only (hintslight, rgb subpixel,
│                           #   synthetic oblique/embolden). Font FILES are not
│                           #   tracked — they come from packages, listed in
│                           #   os/cachyos/packages/fonts.txt.
│
├── terminal/
│   ├── zsh/.zshrc          # Oh My Zsh, starship/p10k toggle, deferred plugins
│   ├── bash/               # bash equivalents
│   ├── kitty/              # kitty.conf + catppuccin-mocha / gruvbox-dark-hard
│   └── starship/starship.toml
│
├── editors/                # vscode/, zed/, sublime/
│
├── tools/
│   ├── ollama/             # local LLM inference — ROCm on an unsupported gfx1031
│   │                       #   card, benchmark-tuned systemd drop-ins, bench.py
│   ├── claude/             # Claude Code global config (agents, commands, skills)
│   ├── focus/              # dnsmasq + nftables site blocker  → see focus README
│   └── mise/
│
└── os/cachyos/
    ├── setup.md            # full system setup walkthrough
    └── packages/
        ├── desktop.txt     # compositor, shell, and the helpers configs call
        ├── fonts.txt       # every font package, with what needs which
        └── ai.txt          # Ollama + the ROCm stack for GPU inference
```

---

## Install

```bash
git clone <this repo> ~/dotfiles && cd ~/dotfiles

./install.sh --dry-run     # show what would change, touch nothing
./install.sh               # link/seed everything in manifest.conf
./install.sh status        # report ok / drift / missing per entry
```

Any existing real file is backed up to `<path>.bak-<timestamp>` before being
replaced, so a first run on a machine that already has configs is safe.

For the desktop specifically, install the packages first — the configs name
fonts and helper binaries and fail quietly without them:

```bash
sudo pacman -S --needed $(grep -v '^#' os/cachyos/packages/desktop.txt | awk '{print $1}')
sudo pacman -S --needed $(grep -v '^#' os/cachyos/packages/fonts.txt   | awk '{print $1}')
paru        -S --needed $(grep    '(AUR)' os/cachyos/packages/*.txt    | awk '{print $1}')
```

Then follow [`wm/hyprland/README.md`](wm/hyprland/README.md) for the parts the
manifest does not cover (hyprpm plugins, the D-Bus notification override).

---

## Two kinds of managed file

`manifest.conf` marks every entry `link` or `seed`, and the distinction is the
thing most likely to bite:

| | `link` | `seed` |
|---|---|---|
| What it does | symlinks live → repo | copies repo → live, only if live is missing |
| Can it drift? | **No** — one file, two names | **Yes** — two separate files |
| Used for | configs only you edit | files a program rewrites itself |

Seeded files move in both directions, and each needs a deliberate step:

```bash
./install.sh status        # DRIFT on a seeded file = live has moved ahead
./install.sh pull          # live → repo: capture what you changed
git diff                   # review, then commit

./install.sh restore       # repo → live: put the tracked version back
```

`restore` is the recovery path when a program resets its own config. It backs
up the live file first. To return to an *older* state, check that version out
of git, restore it, then drop the checkout:

```bash
git checkout <commit> -- wm/hyprland/noctalia/state/settings.toml
./install.sh restore
git checkout HEAD -- wm/hyprland/noctalia/state/settings.toml
```

**For Noctalia, use `wm/hyprland/hypr/scripts/noctalia-restore.sh` instead** —
it does the same job but stops the shell first, because a config restored
underneath a running Noctalia just gets overwritten from memory:

```bash
~/.config/hypr/scripts/noctalia-restore.sh              # the tracked version
~/.config/hypr/scripts/noctalia-restore.sh HEAD~3       # three commits back
~/.config/hypr/scripts/noctalia-restore.sh --list       # available restore points
```

This matters most for `~/.local/state/noctalia/settings.toml`. Noctalia
rewrites that file itself — on every settings-GUI change, and on upgrade for
schema migrations. A symlink there would be destroyed by a replace-style write
and the repo would silently track nothing. It is also not hypothetical: the
5.0.1 upgrade reset the whole bar styling block to stock defaults while leaving
the widget list intact, which is exactly the kind of change that is invisible
until something compares the two copies.

---

## Categories at a glance

### Desktop

| Path | What |
|------|------|
| `wm/hyprland/hypr/` | compositor config — gaps, borders, keybinds, window rules, autostart |
| `wm/hyprland/noctalia/` | the shell: bar layout and widgets, palettes, theme source |
| `fonts/fontconfig/` | font rendering rules |

The session deliberately starts on an **empty workspace** — no applications are
launched at login, from either `exec-once` or XDG autostart.

### Shell & terminal

| Path | Highlights |
|------|------------|
| `terminal/kitty/kitty.conf` | FiraCode Nerd Font + ligatures, splits, vim-style navigation |
| `terminal/zsh/.zshrc` | Oh My Zsh, starship/p10k toggle, deferred plugin loading |
| `terminal/bash/` | bash config, git prompt, NVM |
| `terminal/starship/starship.toml` | battery, git status, memory, language versions |

zsh runs **starship by default** with a Powerlevel10k setup alongside it. Only
one prompt is ever active — switch at runtime with `theme-starship` /
`theme-p10k`; the choice persists in `~/.config/zsh/prompt-framework`.

### Editors

| Tool | Config | Key features |
|------|--------|--------------|
| VS Code | `editors/vscode/` | Copilot, GitLens, 80+ extensions |
| Zed | `editors/zed/` | Ollama Cloud agent, MCP context servers, per-language LSP |
| Sublime Text | `editors/sublime/` | Python/Anaconda, Predawn theme |

### Tooling

| Path | What |
|------|------|
| `tools/claude/` | Claude Code global config — agents, commands, skills, settings |
| `tools/ollama/` | Local LLM inference — GPU-accelerated on an officially unsupported card, tuned by benchmark |
| `tools/focus/` | OS-level site blocking (dnsmasq + nftables), schedule timers, lock mode |
| `os/cachyos/setup.md` | AMD GPU (ROCm), PyTorch/TF, LangChain, Ollama, K8s, Terraform |

See [`tools/focus/README.md`](tools/focus/README.md) for how the blocker works.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
