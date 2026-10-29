---
title: Migration map
topic: migration-map
last_verified: 2026-10-29
status: current
---

# Migration map

What moved, what was split, what was removed, and how old paths and anchors keep resolving. `python tools/check_migration.py` enforces the guarantee below on every CI run.

## The guarantee

Every path that existed on `master` before the modernization either still exists at the same path or is listed in [`REMOVALS.md`](REMOVALS.md). No config path changed, so every symlink in `manifest.conf` and every live path under `~` stays valid. Only documentation was restructured.

## Splits and moves

| Before | After | How old links keep working |
|---|---|---|
| `01-system/cachyos/setup.md` (1927 lines, 25 sections) | `01-system/cachyos/setup/01-system-foundation.md` to `25-quick-reference.md`, indexed by `setup/README.md` | `setup.md` stays as a redirect table. Section numbers became chapter numbers, so "section 19.5" is chapter 19, section 19.5 |
| `system-summary.md` package dumps (`pacman -Qe`, `pacman -Qm`) | `01-system/cachyos/host-snapshot/pacman-explicit.txt` and `pacman-foreign.txt` | `system-summary.md` links to both. It is marked `<!-- snapshot: 2026-10-28 -->` and exempt from version checks |
| "Fresh setup order" in `system-summary.md` | `01-system/cachyos/dev-stack.md` (runbook) and `docs/modernization/HANDOFF.md` (unattended order) | `system-summary.md` keeps a pointer table in the same place |
| Pins scattered through prose | `versions.yaml`, referenced by `<!-- v:key -->` markers | `tools/render_versions.py` rewrites markers; `tools/check_versions.py` fails on drift |
| Hand-written chapter table of contents | `INDEX.md` and `01-system/cachyos/setup/README.md`, generated from frontmatter | `python tools/gen_index.py` |

## New files

`versions.yaml`, `INDEX.md`, `ruff.toml`, `.markdownlint-cli2.yaml`, `.github/` (CI, weekly freshness, Dependabot), `tools/`, `01-system/cachyos/setup/`, `01-system/cachyos/host-snapshot/`, `02-desktop/hyprland/lua-migration.md`, `02-desktop/hyprland/hypr/scripts/hypr-dispatch.sh`, `02-desktop/hyprland/hypr/scripts/dpms.sh`, and everything under `docs/modernization/`.

## Removed

See [`REMOVALS.md`](REMOVALS.md): the archived `frontend-expert` skill (superseded by `frontend-master`), 15 tracked `.pyc` files, and the text of `setup.md` that moved into the chapters.

## Content that changed meaning, not location

Some commands and package names were wrong or stale and were corrected in place. The per-claim record (old claim, new claim, source, date, confidence) is [`LEDGER.csv`](LEDGER.csv); the narrative per topic is [`RESEARCH.md`](RESEARCH.md).
