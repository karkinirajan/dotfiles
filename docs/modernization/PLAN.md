# PLAN

Written before any content edit (Phase 2). Date of record 2026-10-29. Research results (`RESEARCH.md`, `LEDGER.csv`) feed Phase 3 content; this plan fixes structure, sources of truth, tooling, order and risk, and does not change when research lands (research can only add rows to the content workstream).

## 1. Structure options

| | A. Minimal | B. Book layout kept, docs split, versions centralized (CHOSEN) | C. Re-platform |
|---|---|---|---|
| Idea | Leave layout. Add `versions.yaml`, tooling, fix stale text in place | Keep numbered parts and every config path. Split the 1927-line `setup.md` into numbered chapter files. Add `versions.yaml`, generated index, per-topic template with metadata, tooling, CI | Move docs to a `docs/` book (mdBook), move configs to `config/`, renumber parts |
| Readability | `setup.md` stays a 1927-line scroll | Chapters of 40 to 200 lines, stable numbering, generated index | Best reading UX (rendered site) |
| Scalability | New topics keep landing in `setup.md` | New topic = one new numbered file + one index regeneration | Good, but needs build tooling |
| Risk to the machine | None | None for configs: every symlink target in `manifest.conf` keeps its path | High: every live symlink target moves, `~/.zshrc` and `~/.config/hypr` break until `install.sh` re-runs |
| Risk to links | None | Old doc paths stay as short redirect stubs, plus a migration map | Every inbound link breaks |
| Honors the owner's curriculum rule | Yes | Yes (numbered parts, TOC, one topic per file) | Renumbering parts contradicts "files and folders ... like a book curriculum" and the README's own convention that part numbers rarely change |
| Effort | Low | Medium | High |

Decision: **B**. Reason: it delivers the readability and scalability goals without touching any path the machine links to, which matters because the next session applies this repo to the live machine in full-auto mode. Recorded as D-09 in `DECISIONS.md`.

## 2. Target structure

Only documentation and tooling move. No config file, script, unit, package list or `manifest.conf` target path changes.

```
README.md                     book front page: tech stack table, contents, install, contact footer
INDEX.md                      GENERATED from frontmatter by tools/gen_index.py
versions.yaml                 single source of truth for versions, commands that prove them
install.sh, manifest.conf     unchanged paths
fresh-setup.md                kept (owner content); version tokens driven by versions.yaml
system-summary.md             host facts only (hardware, services, defaults); package dumps moved
01-system/
  cachyos/
    README.md
    setup/                    NEW: the old setup.md as one numbered chapter per file
      README.md               generated chapter table
      01-system-foundation.md ... 24-ai-ml-quickstart.md
    setup.md                  STUB: old-section-to-new-file map (keeps the old path resolvable)
    dev-stack.md              kept, de-duplicated against setup/
    host-snapshot/            NEW: pacman-explicit.txt, pacman-foreign.txt (moved out of system-summary.md)
    packages/*.txt            unchanged paths, contents verified
    aur/upwork/               unchanged paths
tools/                        NEW: link, version-drift, index, config, style, package checks
.github/workflows/            NEW: ci.yml (every push/PR), freshness.yml (weekly)
docs/modernization/           this run's artifacts
```

Reasons: one topic per file keeps diffs reviewable; the numeric prefix preserves the book order (`NN-hyphenated-topic.md`); the generated index removes hand-maintained tables that rot; the stub keeps `fresh-setup.md`'s "section 19.5 of setup.md" style references and any external links working.

Also in this structure:

- `05-ai/claude-code/skills/frontend-expert/` (archived rev 2, `disable-model-invocation: true`, superseded by `frontend-master`) is a duplicated topic. If the research ledger shows it has no unique content, it is removed and listed in `REMOVALS.md`; otherwise its unique content is merged into `frontend-master` first. Skill directories keep their paths; Claude Code loads skills only from direct children of `~/.claude/skills/`.
- 15 tracked `__pycache__/*.pyc` files are untracked and `__pycache__/` plus `*.pyc` are added to `.gitignore` (listed in `REMOVALS.md`).
- Hardcoded `/home/kneeraazon/...` in `06-tools/focus` is documented, not rewritten, unless research shows a safe `$HOME` form; scripts that execute on the machine are not behaviorally changed without a verified reason.

## 3. Single source of truth for versions

`versions.yaml` at the repo root. Schema:

```yaml
schema: 1
as_of: 2026-10-29
policy: "Latest stable that Arch/CachyOS repos or the official installer can deliver; upstream recorded alongside"
entries:
  <key>:
    name: Human name
    target: "x.y.z"          # what the docs state and the machine should report
    upstream: "x.y.z"        # latest upstream stable, if different
    arch: "pkgver-pkgrel"    # Arch extra/core, if packaged
    cachyos: "pkgver-pkgrel" # CachyOS repo, if different
    aur: "pkgver-pkgrel"
    source: arch|cachyos|aur|upstream|registry
    support: "EOL or LTS note with date"
    verify: "command that prints the version"   # used by HANDOFF.md
    expect: "substring of the verify output"
    ledger: [L-0012]          # evidence ledger ids
```

Prose and scripts reference it, never repeat it:

- Prose uses inline markers `<!-- v:hyprland -->0.57.0<!-- /v -->`. `tools/render_versions.py` rewrites the text between markers from `versions.yaml`, and `tools/check_versions.py` fails if any marker text differs from the file or any marker names an unknown key. The value stays visible on GitHub and cannot drift silently.
- Shell and Python tooling read `versions.yaml` (HANDOFF generation, checks).
- Package manifests (`*.txt`) hold names only, never versions.
- Frozen history (changelog entries, dated snapshots, benchmark records) is explicitly marked `<!-- snapshot: 2026-10-28 -->` and exempt, so a record of what was true on a date is never "corrected".

## 4. Per-topic template

Every new or rewritten chapter file starts with frontmatter and then follows this lean skeleton; sections that do not apply are omitted, not left empty. Reference chapters stay free of editorial framing.

```markdown
---
title: <topic>
part: 01
chapter: 06
topic: postgresql
versions: [postgresql, pgvector]      # keys in versions.yaml
last_verified: 2026-10-29
status: current
sources:
  - https://www.postgresql.org/docs/18/
---

# 06 PostgreSQL

## Purpose
## Prerequisites
## Install and setup        (each block labeled verified-in-cloud | machine-only | unverified)
## Core concepts            (ground up, even where already proficient)
## Reference
## Verify                   (command and expected output from versions.yaml)
## Version                  (rendered markers)
## Sources
```

Config chapters (kitty, hyprland, ...) get the same frontmatter and a `Verify` section; their existing structure otherwise stays.

## 5. Migration map and link rewrites

`docs/modernization/MIGRATION.md` (generated at the end of Phase 3 from `git diff -M --name-status`) lists old path, new path, and disposition for every moved, split or removed file. Rules:

1. `git mv` for every move. A split uses `git mv setup.md setup/…` for the largest part so history follows, then new files.
2. Every old doc path that existed before this run still resolves: either the file stays, or a stub file keeps the path and points to the new location(s).
3. `tools/check_links.py` rewrites nothing; link fixes are manual commits followed by a clean run of the checker (relative links and anchors across all Markdown).
4. External references that mention old section numbers (`setup.md section 19.5`) are rewritten to the new chapter path.

## 6. Tooling to keep it correct

| Tool | Runs | Purpose |
|---|---|---|
| `tools/check_links.py` | CI every push; `--external` weekly | Relative links and `#anchors` across Markdown; weekly also external URLs (rate-limited, allowlist for known 403 bot walls) |
| `tools/check_versions.py` | CI every push (offline); `--live` weekly | Marker text equals `versions.yaml`; unknown keys fail; `--live` compares targets with current Arch/CachyOS/AUR/registry data |
| `tools/render_versions.py` | manual / pre-commit | Rewrites marker text from `versions.yaml` |
| `tools/gen_index.py` | CI verifies it is up to date | Generates `INDEX.md` and `setup/README.md` from frontmatter |
| `tools/pkg_lookup.py` | weekly; on demand | Package names in `*.txt` exist in Arch, CachyOS or AUR; reports renames and AUR out-of-date flags |
| `tools/check_configs.py` | CI | Parses TOML (alacritty, starship, topgrade, noctalia settings), JSON (VS Code `jsonc` stripped, zed, palettes), systemd unit syntax subset, `manifest.conf` rows and that every `src` exists |
| `tools/check_style.py` | CI | No em dashes in Markdown; frontmatter present and valid on chapter files; `last_verified` is a date |
| markdownlint-cli2 | CI | Heading levels, fenced languages, list style (config `.markdownlint-cli2.yaml`) |
| shellcheck + `bash -n` | CI | `install.sh`, `*.sh`, pacman hook scripts. Zsh scripts (`focus`, `focus-refresh`, `.zshrc`) get `zsh -n` |
| ruff + `py_compile` | CI | `tools/`, `05-ai/ollama/**.py`, `06-tools/focus/scripts/focus-page` |
| `install.sh` smoke test | CI | `HOME=$(mktemp -d)`: `--dry-run`, install, `status`, second run idempotent, `pull`/`restore` on seeds |
| CI workflows | | `.github/workflows/ci.yml` (push, pull_request) and `freshness.yml` (weekly cron plus manual) |

Actions are pinned to full commit SHAs resolved from the release tags at the time of writing (or major tags where SHAs cannot be retrieved, recorded as a gap), with Dependabot for `github-actions`.

## 7. Risk list

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | A moved doc breaks an inbound link or an agent's reference | Medium | Low | Stubs at old paths, link checker, migration map |
| R2 | A documented command is wrong and the full-auto machine session runs it | Medium | High | Every command either runs in the cloud (labeled), is tied to current primary docs (ledger row), or is labeled `unverified`; independent audit of install, security and data-loss content in Phase 4 |
| R3 | Version targets conflict (ROCm x PyTorch x kernel x Ollama) | Medium | High | Compatibility matrix in `RESEARCH.md`; `versions.yaml` carries a `constraints` block that `check_versions.py` evaluates |
| R4 | Upstream is ahead of the distro (Hyprland 0.57.0 in Arch vs 0.56.2 in CachyOS v3) and a plugin pin breaks | High | Medium | Both versions recorded; plugin pins stated against the distro version actually installed |
| R5 | A source is blocked (GitHub API, crates.io) and a claim cannot be verified | High | Low | Old content kept, `<!-- UNVERIFIED -->`, listed in the report |
| R6 | Mechanical edits (em dash sweep, marker rendering) alter config comments that are parsed | Low | Medium | Em dash sweep limited to Markdown; config files validated before and after |
| R7 | Removing duplicate content loses unique value | Low | Medium | Unique-content diff before any removal; removals logged |
| R8 | `frontend-master` says its references are generated; hand edits are overwritten if the generator turns up | Low | Low | Note in `DECISIONS.md`; generator is not in the repo so edits here are the source of truth now |
| R9 | The repo's own rules (no AI attribution, no push by assistant) conflict with this run | Low | Low | D-04, D-07 |

## 8. Rollback

- All work is on branch `modernize/2026-10`, which diverges from `claude/nifty-feynman-n215z4` at `32527be`. The default branch is never pushed.
- Revert one commit: `git revert <sha>`. Revert the whole run: close the PR, or `git reset --hard 32527be` on a local copy of the branch (the PR is not merged by this session).
- No machine state is changed by this session, so there is nothing to roll back on the host.

## 9. Ordered commit sequence

1. `docs(modernization)`: discovery, decisions, state (done).
2. `chore(tools)`: `tools/pkg_lookup.py`, package resolution data.
3. `docs(modernization)`: research, ledger, this plan.
4. `refactor(docs)`: structure and migration (`git mv`, split `setup.md`, stubs, `host-snapshot/`, untrack `.pyc`, `.gitignore`).
5. `feat(versions)`: `versions.yaml`, `render_versions.py`, `check_versions.py`, marker adoption.
6. `docs(<topic>)`: per-topic content updates in clusters (one commit per cluster: system, desktop, gpu-ai, languages, devops, databases, editors-shell, claude-code, frontend-skills, apps).
7. `docs(setup)`: setup instructions rewritten with labeled steps, `fresh-setup.md`, `dev-stack.md`, `system-summary.md`.
8. `ci(tools)`: remaining checks, `.markdownlint-cli2.yaml`, workflows, Dependabot.
9. `docs(readme)`: README and generated index.
10. `docs(modernization)`: verification results, `HANDOFF.md`, `MIGRATION.md`, `REMOVALS.md`, `REPORT.md`.

`STATE.md` is updated at every phase boundary and after each cluster commit.
