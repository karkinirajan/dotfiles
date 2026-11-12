---
title: Work done, 2026-11 pass
topic: modernization
last_verified: 2026-11-12
status: current
---

# Work done, 2026-11 pass

A second pass over this repository, done on 2026-11-12 on the local branch `chore/modernize`. Nothing has been pushed. The first pass
(2026-10-29, see [REPORT.md](REPORT.md)) built the structure, the versions source of truth, the checkers and CI. This pass did not
redo any of that. It asked what had drifted since, and whether anything proves the checkers themselves work.

## What was found

- `master` had **7 uncommitted changes**: unattended `--noconfirm` updates (the topgrade config, its README, the Zsh `update` function,
  two notes in `fresh-setup.md` and one in the CachyOS maintenance chapter), Zed with `disable_ai`, and the Claude Code default model
  set to `opus`. They are the owner's decisions, dated 2026-11-04, and were **left exactly as they were**: not edited, not committed,
  not stashed. `05-ai/claude-code/settings.json` is a live symlink target, so nothing under `05-ai/claude-code/` was touched.
- Every offline gate of the first pass was still green on 2026-11-12:

| Gate | Result |
| --- | --- |
| `check_links.py` | 168 Markdown files, 0 broken |
| `check_versions.py` | 146 entries, 0 offline problems |
| `gen_index.py --check` | current |
| `check_style.py` | 167 files, 0 problems |
| `check_configs.py` | 43 config files plus `manifest.conf`, 0 problems |
| `check_migration.py` | 332 base paths, 0 unresolved |
| `ruff check tools` | clean |
| `bash -n`, `zsh -n`, shellcheck (`-S warning`) | clean |
| `smoke_install.sh` | passed |

- **The checkers had no tests.** About 1,500 lines of code that every other guarantee in the repository rests on, with nothing to show
  that a checker would catch the defect it exists for.

## What was added

- `tools/tests/`: 294 pytest tests for the offline checkers. Each one that needs a repository builds a throwaway git repository with the
  owner's global git configuration switched off. The URL probe is tested against a scripted fake, so no test touches the network.
- `tools/mutation/`: a mutation driver and 122 deliberate bugs. The suite has to fail for each of them. Final run: **122 of 122 killed,
  files restored**. `mutants.py` lists, with reasons, the six mutants that cannot change behaviour.
- CI runs the tests (`python -m pytest tools/tests -q`) after the Python lint. `pytest` is in `tools/requirements.txt`.
- `ruff.toml` gained one scoped ignore, `E501` for `tools/mutation/mutants.py` only (one mutant per line, as `gen_index.py` already
  has for its long table lines). The driver itself was rewritten in this repository's lint-clean style rather than ignored.

## Defects the tests found, all fixed

| Where | Defect |
| --- | --- |
| `check_links.py` | A heading with inline code (`` ## `x` ``) was anchored without its code text, so a link to the real anchor was reported broken. |
| `check_links.py` | Two consecutive reference definitions: the first swallowed the second, which was never checked. |
| `check_versions.py` | A constraint naming a field an entry does not have crashed with a bare `KeyError` instead of naming the rule. |
| `_lib.py` | An impossible date in frontmatter (`2026-13-45`) escaped as a bare `ValueError`, without the "invalid frontmatter" context. |
| `check_configs.py` | `strip_jsonc` removed comma-like text inside strings (`",}"` became `"}"`), against its own documented contract. |
| `check_configs.py` | A missing `manifest.conf` crashed with a traceback. |
| `check_migration.py` | A missing `REMOVALS.md` crashed with a traceback, and a removed root-level file could not be recorded at all (only tokens containing `/` were accepted). |

Mutation checking also found dead code (`.removeprefix("./")` in `gen_index.py`, which pathlib makes a no-op), which was removed.
The real repository still passes every gate after these fixes, including the link check, which now examines more links than before.

## Freshness

`check_versions.py --live` against Arch, CachyOS, the AUR, npm and PyPI, on 2026-11-12:

- **53 of 146 entries are behind** their upstream or distribution version, 14 days after the 2026-10-29 snapshot. Most are patch
  releases on a rolling distribution (for example `hyprland` 0.57.0 against 0.57.2, `nodejs` 26.12.1 against 26.13.1, `mesa`, `docker`,
  `ruff`). A few are larger gaps (`kitty` 0.49.2 against 0.50.0, `zed` 1.25.3 against 1.28.1, `docker-compose` 5.6.1 against 5.7.1).
- **0 lookups failed.** 28 entries are deliberate holds and say why.
- `versions.yaml` was **not changed**. Refreshing targets means re-rendering version markers across the documents, and
  `fresh-setup.md` carries markers and has uncommitted owner changes; each target also has its own `verify` step. This is the weekly
  cycle's work.

## Not done, not verified

- `pkg_lookup.py`, `gen_apps_inventory.py` and the `--live` paths need the network and have no tests.
- The Ollama benchmark harness and the focus page server are linted by ruff but have no tests.
- The CI workflow has not run on GitHub. Its `push` trigger covers `master` and `modernize/**`, so a branch named `chore/modernize`
  only runs CI through a pull request.

## Decisions for you

1. The 7 uncommitted changes are still uncommitted on this branch. Commit, stash or revert them as you see fit.
2. To publish: `git push -u origin chore/modernize`.
3. Refresh `versions.yaml` when you next run the weekly cycle (`python tools/check_versions.py --live`, then edit targets, then
   `python tools/render_versions.py`). Do it after the 7 changes are committed, so the render cannot touch them.
