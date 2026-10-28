---
title: "16 Knowledge Management and Productivity"
part: "01"
chapter: "16"
topic: knowledge-productivity
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 16 Knowledge Management and Productivity


## 16.1 Notes & Knowledge Bases

| Tool | Install | Best For |
|---|---|---|
| **Obsidian** ⭐ | `sudo pacman -S obsidian` | Personal KB, local Markdown, Git-friendly, works offline |
| **Notion** | `paru -S notion-app-enhanced` | Client wikis, team databases, shared project docs |
| **Logseq** | `paru -S logseq-desktop-bin` | Outliner-style daily journaling, block-level referencing |
| **AnyType** | `paru -S anytype-bin` | Open-source local-first Notion alternative |

**Recommended:** Obsidian as primary. Notion for client-facing work.

**Obsidian recommended plugins:** Templater, Dataview, Calendar, Kanban, Git, Advanced Tables, Excalidraw

## 16.2 Task Management

| Tool | Use |
|---|---|
| **Todoist** | `paru -S todoist-appimage` — Personal task manager |
| **Linear** | https://linear.app — Developer-focused, GitHub integration |
| **ClickUp** | https://clickup.com — All-in-one project management |
| **Plane** | Self-hosted Linear alternative (Docker) |

## 16.3 Screenshots & Screen Recording

```bash
sudo pacman -S grim slurp swash obs-studio
# grim + slurp     — capture (region/window/screen), wired to the Print key
#                    via ~/.config/hypr/scripts/screenshot.sh
# swash            — the only screenshot annotator/editor on this machine
# obs-studio       — recording and streaming (Wayland via PipeWire)
```

## 16.4 Time Tracking (Essential for Freelancing)

- **Toggl Track** ⭐ — https://track.toggl.com/ (free tier, project/client categorization)
- **Clockify** — https://app.clockify.me/ (unlimited users free, timesheets, invoicing)
- **WakaTime** — VS Code extension `WakaTime.vscode-wakatime` (automatic coding time tracking)

## 16.5 Clipboard Manager

```bash
sudo pacman -S copyq   # Feature-rich clipboard manager
# Klipper is pre-installed with KDE Plasma (system tray)
```
