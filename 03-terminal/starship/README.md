# 03.5 · Starship Prompt

Cross-shell prompt configuration used by Zsh (`eval "$(starship init zsh)"`).

```
03-terminal/starship/
├── README.md
└── starship.toml    → ~/.config/starship.toml (linked via manifest.conf)
```

## Structure

- **Left prompt (`format`):** Single-line powerline segments for OS icon,
  username/SSH host, directory, git branch/status/state/metrics, and active
  language/runtime toolchains (`python`, `nodejs`, `rust`, `golang`, `java`,
  `c`, `php`, `lua`, `docker_context`, `kubernetes`, `terraform`, `aws`,
  `conda`).
- **Right prompt (`right_format`):** Command duration, exit status, background
  jobs, RAM usage, and local clock.
- **Noctalia palette block:** `[palettes.noctalia]` at the bottom of the file is
  updated by Noctalia's `starship` theme template.
