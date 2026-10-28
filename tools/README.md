---
title: Repo tooling
topic: tools
last_verified: 2026-10-29
status: current
---

# Tools

Checks that keep the book and its configs correct. They run in CI on every push (`.github/workflows/ci.yml`) and the live ones run weekly (`.github/workflows/freshness.yml`).

```sh
python -m pip install -r tools/requirements.txt
python tools/check_links.py        # relative links and anchors (add --external for URLs)
python tools/check_versions.py     # markers vs versions.yaml, constraints (add --live for freshness)
python tools/check_configs.py      # TOML, JSON, YAML, units, manifest.conf, package lists
python tools/check_style.py        # no em dashes, frontmatter, fenced languages
python tools/gen_index.py --check  # INDEX.md and setup/README.md are current
bash tools/smoke_install.sh        # install.sh against a throwaway HOME
```

| Tool | Purpose |
|---|---|
| `check_links.py` | Relative links and `#anchors` across Markdown; `--external` also checks URLs |
| `check_versions.py` | Version markers equal `versions.yaml`; constraint rules hold; `--live` compares with Arch, CachyOS, AUR, npm and PyPI |
| `render_versions.py` | Rewrites `<!-- v:key -->` marker text from `versions.yaml` |
| `gen_index.py` | Generates `INDEX.md` and `01-system/cachyos/setup/README.md` from frontmatter |
| `check_configs.py` | Parses every shipped config and validates `manifest.conf` and package lists |
| `check_style.py` | Repo style rules (em dashes, frontmatter, code fence languages) |
| `pkg_lookup.py` | Resolves package names against Arch, CachyOS and AUR; run with `--lists` on the package files |
| `smoke_install.sh` | Runs `install.sh` in a temporary `HOME` and asserts it links, is idempotent and backs up real files |

`pkg_lookup.py` and `check_versions.py --live` need network access. Everything else is offline.
