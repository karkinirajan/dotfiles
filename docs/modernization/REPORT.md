---
title: Modernization report
topic: report
last_verified: 2026-10-29
status: current
---

# Modernization report

Branch `modernize/2026-10`, date of record 2026-10-29. Author `karkinirajan`. Every commit is free of AI attribution (owner rule, [DECISIONS D-04](DECISIONS.md)), so this description and the commits carry no generated-with footer.

**Repo versus upstream is done and verified. Repo versus machine is not checked.** No command in this run touched, audited or scripted against the owner's machine. Every machine step is in [`HANDOFF.md`](HANDOFF.md) and is `machine-only`.

## Summary

- 823 claims were researched across 10 topic clusters by parallel read-only subagents, each against a source retrieved in this session. 307 changed, 450 were confirmed, 66 could not be verified and were kept and tagged. The evidence ledger is [`LEDGER.csv`](LEDGER.csv); the narrative is [`RESEARCH.md`](RESEARCH.md).
- The 1927-line `setup.md` became 25 numbered chapters (plus a redirect stub, a generated index and a host snapshot). No config path moved, so every live symlink stays valid ([`MIGRATION.md`](MIGRATION.md), enforced by `tools/check_migration.py`).
- `versions.yaml` is the single source of truth: 146 entries, 7 compatibility constraints, inline markers in prose, a drift check in CI and a weekly live comparison against Arch, CachyOS, the AUR, npm and PyPI.
- A fresh-eyes check re-verified a random 20% of the changed claims (61 rows): 48 confirmed, 12 partial, 0 refuted, 1 unverifiable. See [`VERIFICATION.md`](VERIFICATION.md). An independent read-only audit of install, security and data-loss content found 0 blockers, 3 high and 16 medium issues; all 3 high and all 16 medium were fixed (list below).

## Findings that change what you should do

1. **Hyprland 0.57.0 (Arch `extra`) removed the hyprlang `.conf` parser.** With only `hyprland.conf` it ignores the whole `hypr/config/` tree. CachyOS and the machine are on 0.56.2. The repo held `hyprland` and `hyprpm` with `IgnorePkg` until a Lua config was validated. After the run the Lua port was written and validated (`--verify-config` on 0.56.2 and 0.57.0, plus a nested 0.57.0 compositor); see [`lua-migration.md`](../../02-desktop/hyprland/lua-migration.md). Lifting the hold is the owner's upgrade step.
2. **PostgreSQL 18 `initdb` defaults to `trust` authentication.** The `--auth-local=peer --auth-host=scram-sha-256` flags are now mandatory in every doc that initializes a cluster.
3. **Next.js 16.4.0 is vulnerable** (two Critical RCEs, one High); the frontend templates now pin 16.4.3 and React 19.3.1.
4. **MariaDB 13.0 is a rolling release;** `mariadb-lts` 12.3.3 is the stable series. The machine runs 13.0.2 and cannot downgrade, so the handoff keeps it.
5. **MongoDB `mongodb-bin` 8.3.9 is inside advisory SERVER-131805** (fixed in 8.3.13). Exposure on the loopback single node is low; no fixed AUR binary exists.
6. **The focus nftables file was not idempotent** (reloading duplicated all six rules). It now uses table `inet focus` and flushes its own chain; reloading was tested in a network namespace.
7. **Supabase stops exposing new `public` tables to the Data API automatically on 2026-10-30;** the starter migration and its pgTAP test now grant explicitly.
8. **`docker-rootless-extras` is AUR-only; `mullvad-vpn` and `librewolf` are in repos (`librewolf-bin` is gone from the AUR; `mullvad-vpn-bin` conflicts with the repo package); `notion-app-enhanced` and AND.CO are dead;** the package lists and chapters say so.
9. **ROCm:** Arch ships the legacy 7.2 train (7.2.4). gfx1031 is unofficial. `HSA_OVERRIDE_GFX_VERSION` is needed for PyTorch wheels (use the `rocm7.2` index) but only a fallback for the packaged Ollama.

## Changes by topic

| Topic | Claims | Changed | Unverified |
|---|---|---|---|
| OS, boot, security | 79 | 24 | 4 |
| Desktop (Hyprland, Noctalia) | 77 | 44 | 4 |
| GPU and local AI | 82 | 35 | 13 |
| Languages and tooling | 80 | 25 | 2 |
| DevOps and containers | 59 | 30 | 2 |
| Databases | 73 | 25 | 15 |
| Editors, shell, terminal | 109 | 38 | 5 |
| Claude Code and AI tooling | 78 | 16 | 9 |
| Frontend skills | 80 | 35 | 4 |
| Apps and misc | 106 | 35 | 8 |

Narrative of the edits, by commit group: structure and migration; versions source of truth; OS and security (chapters 01, 19, 20); GPU and local AI (02, 04, 24, `05-ai/ollama/`); languages (03, 05, 10, 11, 14); DevOps (07, 08, 09); databases (06); desktop (`02-desktop/hyprland/`, new `lua-migration.md`, dual-form dispatch helper and `dpms.sh`); editors, shell, terminal (12, 13, zsh, kitty, alacritty, Zed, VS Code); Claude Code docs, skills and `frontend-master` pins; apps (15 to 18, 21, 25, Upwork recipe); setup runbook (`dev-stack.md`, `system-summary.md`); tooling and CI; README and index; handoff.

## Before and after

| | Before | After |
|---|---|---|
| Setup guide | one 1927-line `setup.md` | 25 chapters of 20 to 200 lines under `01-system/cachyos/setup/`, generated `README.md`, `setup.md` is a redirect stub |
| Version facts | hand-typed in prose, partly stale | `versions.yaml` plus markers, checked in CI |
| Chapter metadata | none | frontmatter (`title`, `topic`, `versions`, `last_verified`, `status`) on every chapter |
| Checks | none | links and anchors, version drift, configs parse, style (no em dashes, fence languages), generated index, migration map, ruff, shellcheck, zsh and bash syntax, markdownlint, `install.sh` smoke test, weekly freshness workflow, Dependabot |
| Package inventories | inside `system-summary.md` | `01-system/cachyos/host-snapshot/` |
| Tracked junk | 15 `.pyc` files, the duplicate `frontend-expert` skill | removed, listed in [`REMOVALS.md`](REMOVALS.md) |

## Confidence distribution

| Confidence | Ledger rows |
|---|---|
| high | 625 |
| medium | 159 |
| low | 39 |

Source types: 535 primary documentation, 152 package registries, 111 local runs in the cloud sandbox, 25 secondary. Local runs covered the PyTorch `uv lock`, the nft idempotency test, the dual-form dispatch helper, the compose YAML parse, `actionlint`, `install.sh` in a throwaway `HOME`, `zsh -n`, and the package-list resolution.

## Sources that were refused (gaps, not worked around)

The GitHub API and `github.com` advisory and release pages, the Arch wiki and `gitlab.archlinux.org`, the AUR (Anubis challenge page), Upwork's download CDN and some vendor help pages. Claims that depended only on them were kept and tagged `UNVERIFIED`.

## Unverified items

39 inline tags in the docs and 66 ledger rows with status `unverified`. The inline tags:

| Where | What is unverified |
|---|---|
| `01-system/cachyos/aur/upwork/README.md:39` | Upwork support position on non-Ubuntu Xorg sessions |
| `01-system/cachyos/setup/02-amd-gpu-rocm.md:42` | both are hypotheses |
| `01-system/cachyos/setup/02-amd-gpu-rocm.md:71` | native gfx1031 on Ollama 0.40.11 and kernel 7.3 |
| `01-system/cachyos/setup/04-ai-llm-stack.md:74` | TensorFlow on gfx1031 |
| `01-system/cachyos/setup/04-ai-llm-stack.md:137` | (claim on this line) |
| `01-system/cachyos/setup/04-ai-llm-stack.md:148` | (claim on this line) |
| `01-system/cachyos/setup/04-ai-llm-stack.md:162` | runtime on gfx1031 |
| `01-system/cachyos/setup/04-ai-llm-stack.md:185` | (claim on this line) |
| `01-system/cachyos/setup/04-ai-llm-stack.md:197` | Milvus Lite index types |
| `01-system/cachyos/setup/06-databases.md:49` | Arch upgrade procedure and the pgvector caveat; not run |
| `01-system/cachyos/setup/06-databases.md:86` | exact steps, only the overview page was readable |
| `01-system/cachyos/setup/06-databases.md:99` | the permission problem and this fix are recorded from this host only |
| `01-system/cachyos/setup/06-databases.md:163` | (claim on this line) |
| `01-system/cachyos/setup/08-docker-kubernetes.md:49` | (claim on this line) |
| `01-system/cachyos/setup/08-docker-kubernetes.md:111` | both image tags |
| `01-system/cachyos/setup/08-docker-kubernetes.md:112` | the exact map count Elasticsearch needs for one node |
| `01-system/cachyos/setup/09-iac-ci-cd.md:67` | act with rootless Docker and node24-based actions |
| `01-system/cachyos/setup/10-data-engineering.md:45` | Redpanda command syntax and the "~512MB RAM, no JVM" claim |
| `01-system/cachyos/setup/12-editors-ides.md:50` | per-ID publish status of the remaining extensions |
| `01-system/cachyos/setup/15-browsers.md:43` | Chrome Web Store availability and manifest version of each extension on Brave; check each listing before relying on it |
| `01-system/cachyos/setup/16-knowledge-productivity.md:38` | whether Bases fully replaces Dataview and Calendar for this vault |
| `01-system/cachyos/setup/16-knowledge-productivity.md:44` | upstream Todoist Linux version |
| `01-system/cachyos/setup/17-freelance-project-management.md:31` | country limits rest on 2020 to 2021 search snippets; Wave's help article returned 403 |
| `01-system/cachyos/setup/17-freelance-project-management.md:36` | Upwork support position on non-Ubuntu Xorg sessions |
| `01-system/cachyos/setup/17-freelance-project-management.md:55` | usability of the alternatives on Hyprland |
| `01-system/cachyos/setup/18-communication.md:41` | screen sharing in Slack and Zoom on Hyprland |
| `01-system/cachyos/setup/19-security-privacy.md:175` | the interaction is inferred, not reproduced |
| `01-system/cachyos/setup/20-maintenance-monitoring.md:48` | whether BOOT_ORDER hides unlisted entries |
| `01-system/cachyos/setup/20-maintenance-monitoring.md:52` | (claim on this line) |
| `01-system/topgrade/README.md:15` | the Antigravity probe and `agy update` behaviour are recorded from this host only, not reproducible without the packages |
| `02-desktop/hyprland/README.md:270` | the claim that every hyprexpo fork is broken |
| `02-desktop/hyprland/README.md:312` | bug status on 5.4.0 |
| `02-desktop/hyprland/README.md:357` | the Chromium SIGSEGV under a systemd service scope (needs coredumpctl on the machine) |
| `04-editors/zed/README.md:30` | the replacement model tag |
| `05-ai/claude-code/skills/mongodb-schema-design/SKILL.md:12` | growth mechanism |
| `05-ai/claude-code/skills/mongodb-schema-design/SKILL.md:20` | 100MB stage limit on current releases |
| `05-ai/ollama/README.md:111` | native gfx1031 on Ollama 0.40.11 and kernel 7.3 |
| `fresh-setup.md:117` | exact installer menu label; the wording comes from the release blog |
| `system-summary.md:53` | (claim on this line) |

The ledger rows without an inline tag are information-only (for example vendor version numbers that moved) or live in [`LEDGER.csv`](LEDGER.csv) with `status=unverified`.

## Machine-only steps

All of [`HANDOFF.md`](HANDOFF.md) section 2 (S00 to S11) is `machine-only`: snapshot, `IgnorePkg` hold, mirrors, upgrade, conflict-aware package install, `./install.sh`, `hyprctl reload`, Ollama drop-ins, `lactd`, the focus nft reload, and the read-only verification block. Chapters mark further machine-only commands inline (rootless Docker, database initialization, VPN, Limine, Secure Boot), and the handoff lists which of them the unattended run must not execute.

## Audit findings: applied and left open

Applied: MariaDB and Mullvad conflict guards in the runbook; the chained loopback bind for MariaDB with an absolute path; the Upwork build refuses to run without the downloaded `.deb`; AppArmor boot-parameter backups and a gate; SSH hardening placeholder and reload; Mullvad block marked as the alternative client; UFW rules scoped to the LAN and stated as optional; Secure Boot signing order; the Hyprland hold on blank installs; `ai.txt` header; minikube `--cpus` and subuid remedies; persistent `vm.max_map_count`; Prometheus loopback note; idempotent fstab append; the focus script now checks dnsmasq before touching `/etc/resolv.conf`.

Left open (low or owner-scope), none blocks the handoff:

- Fixed after the run: `install.sh status` now exits 1 on link drift, missing entries or errors (seed drift stays 0); `pull` copies before replacing the repo file; the script refuses to run as root.
- `focus off` writes plain-DNS `/etc/resolv.conf`, bypassing the encrypted DNS of chapter 19 even with focus off; the focus scripts hardcode `/home/kneeraazon`. Fixed after the run: `focus-page` falls back to 8080 when nginx holds port 80; `gnome-keyring` is in `desktop.txt` and unlocks at login (chapter 02.3).
- Fixed after the run: the chapter 08 compose Elasticsearch publishes 9201, beside the chapter 06 node on 9200. Still open: `redis/redisinsight:latest` is unpinned.
- `fresh-setup.md` stops the running display manager from inside its own session.

## Owner decisions still open

Hyprspace for Hyprland 0.57 (the machine runs 0.57.0 on the Lua port since 2026-10-29; Hyprspace does not build there yet and its hyprpm repo was removed); the Zed default-model replacement (`deepseek-v4-flash:cloud` was retired 2026-09-25); the `claude-brain` hooks (private tool, cannot be verified from public sources); whether to switch MariaDB to the LTS series by dump and re-initialize; the Logseq and Mullvad package variants; whether `paru --skipreview` is acceptable for the unattended run; lifting the `CLAUDE.md` rules against `sudo` and `git fetch` for that session.

## Risks

| Risk | Mitigation |
|---|---|
| The unattended run executes a command that was never run on the host | Every machine step is labeled, idempotent, guarded where data could be lost, and has an expected output; stop conditions are explicit |
| `IgnorePkg` on Hyprland breaks a library dependency | Pacman refuses the upgrade ("breaks dependency"); the handoff says stop and report |
| Frontend pins other than Next and React are behind the registry | They match the templates and the trust-policy exclusions; the newer versions are listed and the live check records the hold |
| Package names drift again | Weekly `freshness.yml` runs `check_versions.py --live` and `pkg_lookup.py` |

## Rollback

All work is on `modernize/2026-10`; the default branch is untouched and the pull request is not merged. Revert one commit with `git revert <sha>` or close the pull request. Nothing changed on the machine, so there is nothing to roll back there; the handoff has its own rollback table (Snapper snapshot first).

## Index of this folder

[`DISCOVERY.md`](DISCOVERY.md), [`RESEARCH.md`](RESEARCH.md), [`LEDGER.csv`](LEDGER.csv), [`PLAN.md`](PLAN.md), [`DECISIONS.md`](DECISIONS.md), [`REMOVALS.md`](REMOVALS.md), [`MIGRATION.md`](MIGRATION.md), [`VERIFICATION.md`](VERIFICATION.md), [`STATE.md`](STATE.md), [`HANDOFF.md`](HANDOFF.md), and this report.
