---
title: Repo tooling
topic: tools
last_verified: 2026-11-12
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
python tools/check_migration.py    # every path tracked on origin/master resolves or is in REMOVALS.md
bash tools/smoke_install.sh        # install.sh against a throwaway HOME
python -m pytest tools/tests -q    # the checkers' own tests (they build throwaway git repos; no network)
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
| `check_migration.py` | Confirms the migration map: each path on the base branch still exists or is listed in `docs/modernization/REMOVALS.md` |
| `smoke_install.sh` | Runs `install.sh` in a temporary `HOME` and asserts it links, is idempotent and backs up real files |

`pkg_lookup.py` and `check_versions.py --live` need network access. Everything else is offline.

## Tests

`tools/tests/` holds pytest tests for the offline checkers: frontmatter and code-fence parsing, slugs and anchors, link extraction and
resolution, every HTTP branch of the URL probe (against a scripted fake, so nothing touches the network), version parsing and drift,
constraint operators, marker rewriting, index generation, the migration map and every config parser. Each test that needs a repository
creates a throwaway one in a temporary directory, with the owner's global git configuration switched off, so results do not depend on
the machine.

A passing suite only shows the tests agree with the code. `tools/mutation/` checks that they would disagree if the code were wrong: it
applies one deliberate bug at a time (`mutants.py`) and the suite has to fail for each.

```sh
python tools/mutation/mutate.py tools/mutation/mutants.py -- python -m pytest -x -q -p no:cacheprovider tools/tests
```

The driver requires the suite to pass first, requires each pattern to match exactly once, and restores the files in a `finally` block,
so never kill it while it runs and do not edit `tools/` during a run. A survivor is a missing test or redundant code: fix the cause. A
mutant that cannot change behaviour is listed with its reason in the header of `mutants.py` instead.

Not tested: `pkg_lookup.py`, `gen_apps_inventory.py` and the `--live` paths, which need the network.
