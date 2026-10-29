---
title: Starship prompt
part: "03"
chapter: "05"
topic: starship
versions: [starship]
last_verified: 2026-10-29
status: current
sources:
  - https://starship.rs/config/
---

# 03.5 · Starship Prompt

Cross-shell prompt configuration used by Zsh (`eval "$(starship init zsh)"`).

```text
03-terminal/starship/
├── README.md
└── starship.toml    → ~/.config/starship.toml (linked via manifest.conf)
```

## Structure

- **Left prompt (`format`):** single-line powerline segments for OS icon,
  username/SSH host, directory, git branch/status/state/metrics, and the
  language/runtime modules that are enabled (`python`, `nodejs`, `rust`, `golang`,
  `java`, `bun`, `deno`, `docker_context`, `kubernetes`, `terraform`, `aws`,
  `conda`, `direnv`, `memory_usage`). There are no `c`, `php` or `lua` modules.
- **Right prompt:** `right_format` is empty; duration, status and jobs render in the left line.
- **Validation:** every key (116 keys in 34 tables) exists in Starship 1.27.0's
  `config-schema.json`, and `starship 1.27.0` rendered the file with no unknown-key warnings.
- **Known defect, restore on the host:** the file contains **no** Nerd Font
  glyphs from the Basic Multilingual Plane private-use range (U+E000 to U+F8FF)
  in any of its six commits, so the OS icon (`Arch`), git branch, python,
  nodejs, rust, golang, docker_context, java, bun, conda, aws, jobs and status
  symbols render blank. The supplementary-plane `md-*` glyphs (lock, timer,
  terraform, memory) survived and exist in Nerd Fonts 3.5.1. The cause is
  unproven; repair by re-entering the symbols from a Nerd Font glyph picker.
  <!-- UNVERIFIED: cause of the missing glyphs -->
- **Noctalia palette block:** `[palettes.noctalia]` at the bottom of the file is
  updated by Noctalia's `starship` theme template.
