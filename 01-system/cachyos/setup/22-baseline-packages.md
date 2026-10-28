---
title: "22 Baseline Package Installation"
part: "01"
chapter: "22"
topic: baseline-packages
versions: []
last_verified: 2026-10-29
status: current
sources: []
---

# 22 Baseline Package Installation

The baseline and optional profiles are managed in these package manifests:

- `01-system/cachyos/packages/desktop.txt`: Hyprland, Noctalia, greetd, portals, and desktop applications.
- `01-system/cachyos/packages/system.txt`: CachyOS Snapper support, UFW, power profiles, and security packages.
- `01-system/cachyos/packages/fonts.txt`: fonts referenced by the desktop, terminal, and editor configs.
- `01-system/cachyos/packages/cli.txt`: shell, terminal, and command-line utilities.
- `01-system/cachyos/packages/developer.txt`: optional full-stack developer, database, container, and cloud profile (see [`dev-stack.md`](../dev-stack.md)).
- `01-system/cachyos/packages/claude-code-tools.txt`: optional CLI tools for token-efficient Claude Code workflows.
- `01-system/cachyos/packages/ai.txt`: optional Ollama/ROCm/Vulkan packages for the matching AMD GPU.
- `06-tools/focus/packages.txt`: dependencies for the optional focus DNS/firewall blocker.

Use the interactive installation command in the repository [README](../../../README.md#install).
AUR packages are marked `(AUR)` and must be reviewed and built with an installed
AUR helper. Installing a package does not initialize databases, expose network
services, change DNS, enable services, or download AI models.

The remainder of this guide is a catalog of optional tools. Select only the
applications and services needed for this machine; do not combine the catalog
into a blanket transaction.
