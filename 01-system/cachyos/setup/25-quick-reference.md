---
title: "25 Quick Reference and Services"
part: "01"
chapter: "25"
topic: quick-reference
versions: []
last_verified: 2026-10-29
status: current
sources: []
---

# 25 Quick Reference and Services

## Quick Reference Card

| Need | Tool | Command |
|---|---|---|
| Install Python packages | `uv add <pkg>` | Inside project |
| Install CLI tools globally | `uv tool install <tool>` | Isolated env |
| Run scripts | `uv run python script.py` | Project venv |
| Run LLMs locally | `ollama run llama3.1:8b` | Uses AMD GPU |
| Chat UI for LLMs | Open WebUI | http://localhost:3000 |
| GPU monitoring | `amdgpu_top` / `rocm-smi` | Real-time |
| Docker management | `lazydocker` | TUI |
| Git management | `lazygit` | TUI |
| API testing | Thunder Client | VS Code extension |
| Smart directory jump | `z <partial-path>` | zoxide |
| Fuzzy file search | `Ctrl+T` | fzf |
| System snapshot | `snapper list` | Btrfs snapshots |
| Password manager | `bitwarden` / `keepassxc` | Desktop + browser. Arch `bitwarden` is 2026.3.1 (upstream desktop 2026.10.1); KeePassXC 2.8.0 is current |
| VPN | `mullvad connect` | Mullvad VPN (`sudo pacman -S mullvad-vpn`, then `systemctl enable --now mullvad-daemon.service`) |
| Time tracking | Toggl Track | https://track.toggl.com |
| Note-taking | Obsidian | Desktop app (`sudo pacman -S obsidian`) |
| Project management | Linear / ClickUp | Browser |

## Services in the full developer profile

```bash
# System services in this profile:
systemctl is-active postgresql mariadb valkey mongodb ollama ananicy-cpp ufw
# Docker runs rootless in the user's systemd manager:
systemctl --user is-active docker
```

| Service | Scope | Purpose |
|---|---|---|
| `docker` | User | Rootless container runtime; no system daemon or `docker` group membership |
| `postgresql` | System | Local PostgreSQL development database |
| `mariadb` | System | Local MySQL-compatible database, bound to loopback |
| `valkey` | System | Local Redis-compatible key-value store |
| `mongodb` | System | Local document database, bound to loopback |
| `ollama` | System | Local LLM inference on the AMD GPU |
| `ananicy-cpp` | System | Process priority management |
| `ufw` | System | Active firewall: deny incoming, allow outgoing, no inbound allow rules |
| `proton.VPN` | System | VPN client daemon; running with no active VPN tunnel |
| `openrazer-daemon` | User | Razer peripheral control; requires group membership and a fresh login |

Nginx, DNS filtering, file sync, Mullvad, Fail2ban, and AppArmor enforcement
remain disabled or unconfirmed until configured for the machine's network and
use case. The active Proton VPN daemon is not connected. See
[`dev-stack.md`](../dev-stack.md) for local database initialization, toolchain
setup, and host-specific defaults.

## Sources

- Each row links back to its chapter: tools in chapters 03, 04, 08, 13 and 14, apps in 15 to 21, security in 19. Ledger: cluster C10 in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
