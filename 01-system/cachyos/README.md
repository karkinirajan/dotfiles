# 01.1 · CachyOS System Profile

OS-level documentation, package manifests, database loopback drop-ins, and
reproducible local PKGBUILDs for this CachyOS (Arch) workstation.

```
01-system/cachyos/
├── README.md                 ← you are here
├── setup/                    # 25 numbered chapters (the setup walkthrough)
├── setup.md                  # redirect stub for old links into setup/
├── host-snapshot/            # point-in-time package inventories (pacman -Qe, -Qm)
├── dev-stack.md              # reproducible developer & database stack runbook
├── mariadb-local.cnf         # /etc/my.cnf.d/90-local-dev.cnf (loopback 127.0.0.1 bind)
├── aur/
│   └── upwork/
│       ├── README.md         # why Upwork is built from the bundled .deb
│       └── PKGBUILD          # local PKGBUILD (5.8.0.41; vendor .deb with bundled runtime)
└── packages/
    ├── desktop.txt           # Hyprland, Noctalia, greetd, portals, audio, GUI apps
    ├── system.txt            # Snapper, UFW, power profiles, security daemons
    ├── fonts.txt             # all font families referenced by desktop/terminal/editor configs
    ├── cli.txt               # Zsh, Starship, Kitty, Alacritty, Rust CLI utilities, uv, paru
    ├── developer.txt         # languages, databases, containers, Kubernetes, cloud & IaC
    ├── ai.txt                # Ollama + AMD ROCm/Vulkan stack (RX 6700 XT / gfx1031)
    └── claude-code-tools.txt # optional CLI tools for token-efficient Claude Code workflows
```

## How it is wired in

Nothing in `01-system/cachyos/` is symlinked into `$HOME` by `manifest.conf`
because package installation and `/etc/` files require root privileges:

- **Baseline packages** (`desktop.txt`, `system.txt`, `fonts.txt`, `cli.txt`)
  are installed during initial setup using the command in the root
  [`README.md`](../../README.md#install).
- **Developer stack** (`developer.txt`, `mariadb-local.cnf`, `aur/upwork/PKGBUILD`)
  follows [`dev-stack.md`](dev-stack.md).
- **Local AI packages** (`ai.txt`) pair with [`05-ai/ollama/README.md`](../../05-ai/ollama/README.md).
- **Point-in-time host snapshot** is recorded in [`system-summary.md`](../../system-summary.md).
