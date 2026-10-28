---
title: "16 Knowledge Management and Productivity"
part: "01"
chapter: "16"
topic: knowledge-productivity
versions: [obsidian]
last_verified: 2026-10-29
status: current
sources:
  - https://obsidian.md/changelog/
  - https://github.com/logseq/og
  - https://docs.plane.so/
---

# 16 Knowledge Management and Productivity

## Purpose

Note-taking, task, screenshot, time-tracking and clipboard tools, with the install path that works today on this machine.

## 16.1 Notes and knowledge bases

| Tool | Install | Best for |
|---|---|---|
| **Obsidian** | `sudo pacman -S obsidian` (<!-- v:obsidian -->1.14.5<!-- /v -->) | Personal knowledge base, local Markdown, Git-friendly, offline |
| **Notion** | Use the web app (Brave app mode or install as a PWA) | Client wikis, team databases, shared project docs |
| **Logseq OG** | `paru -S logseq-og-bin` (1.0.0, file-graph Markdown) | Outliner-style journaling on a Markdown folder |
| **Anytype** | `paru -S anytype-bin` (0.57.4, repackaged AppImage) | Open-source local-first Notion alternative |

**Notion:** there is no official Notion Linux app. The AUR `notion-app-enhanced` repackages Notion desktop 2.0.18 (Electron 18, 2022) with notion-enhancer 0.11.0, whose own docs say recent Notion updates broke the enhancer; Notion desktop is at 7.40.0. Use the browser.

**Logseq:** the project split on 2026-04-24 into Logseq OG (file/Markdown graphs, security and Electron upgrades only; AUR `logseq-og-bin`) and Logseq 2.x (database graphs, beta; AUR `logseq-appimage`). The old `logseq-desktop-bin` (0.10.15, the last legacy release) is flagged out of date.

**Anytype:** if the AppImage fails with a Chromium SUID sandbox error, `/tmp` is mounted `nosuid`; run it from another directory.

**Recommended:** Obsidian as primary, Notion in the browser for client-facing work.

**Obsidian plugins:** Templater, Git, Advanced Tables and Excalidraw are maintained. Dataview works but has had no release since 0.5.70 (2025-04); Kanban (now `obsidian-community/obsidian-kanban`, 2.0.51) has had none since 2024-05; Calendar (1.5.10) looks unmaintained. Obsidian's core Bases plugin covers many table and card views, and the core Daily notes plugin replaces Calendar for most uses. <!-- UNVERIFIED: whether Bases fully replaces Dataview and Calendar for this vault -->

## 16.2 Task management

| Tool | Use |
|---|---|
| **Todoist** | `paru -S todoist-appimage` (AUR 9.32.0, community build; Todoist officially supports Snap and AppImage on Ubuntu/GNOME only). Upstream's current version could not be verified. <!-- UNVERIFIED: upstream Todoist Linux version --> |
| **Linear** | <https://linear.app>, developer-focused, GitHub integration |
| **ClickUp** | <https://clickup.com>, all-in-one project management |
| **Plane** | Self-hosted Linear alternative. The documented Docker Compose install (`curl -fsSL https://prime.plane.so/install/ \| sh -`) installs the Commercial edition (free plan, 12 seats); the Community edition is still available, see <https://developers.plane.so/self-hosting/methods/docker-compose> |

## 16.3 Screenshots and screen recording

```bash
sudo pacman -S --needed grim slurp obs-studio
sudo pacman -S --needed swash   # CachyOS repo only (1.5.1); on plain Arch use the AUR package
```

- `grim` + `slurp` capture a region, window or screen and are wired to the Print key through `~/.config/hypr/scripts/screenshot.sh`.
- `swash` is the only screenshot annotator on this machine; it is in the `cachyos` repo and the AUR, not in Arch extra.
- `obs-studio` (33.0.0) records and streams on Wayland through PipeWire. OBS 33 overhauled plugin loading, so out-of-tree plugins may need rebuilding.

## 16.4 Time tracking

- **Toggl Track**: <https://track.toggl.com/> (free tier, project and client categories)
- **Clockify**: <https://app.clockify.me/>. Since April 2026 the free plan covers up to 5 users with unlimited tracking and PDF export; invoicing, billable rates and CSV export are paid.
- **WakaTime**: VS Code extension `WakaTime.vscode-wakatime` (automatic coding time)

## 16.5 Clipboard manager

Clipboard history is already provided by `cliphist`: `autostart.conf` runs `wl-paste --watch cliphist store`. KDE was removed from this machine (see [`KDE-REMOVAL.md`](../../../02-desktop/hyprland/KDE-REMOVAL.md)), so there is no Klipper.

```bash
sudo pacman -S --needed copyq   # optional GUI manager; Arch extra has 16.0.0 (upstream 17.0.0)
```

CopyQ monitors the clipboard natively on Hyprland; global shortcuts need the portal, and paste or window-title features need its Wayland support command plus `ydotool`, `grim` and `slurp`.

## Verify

```bash
obsidian --version 2>/dev/null; pacman -Q obsidian grim slurp
```

Expected: obsidian <!-- v:obsidian -->1.14.5<!-- /v -->. Label: `machine-only`.

## Sources

- [Obsidian changelog](https://obsidian.md/changelog/), [Logseq OG](https://github.com/logseq/og), [Plane self-hosting](https://developers.plane.so/self-hosting/methods/docker-compose)
- Ledger: cluster C10, topics `Obsidian`, `Notion`, `Logseq`, `Todoist`, `Clockify`, `CopyQ` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
