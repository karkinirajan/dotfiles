---
description: Run the real build/lint/typecheck/test/security gates before declaring work done — not a guess
---

Before claiming the current work is complete, actually run the verification gates that apply to this project. Detect the stack from what's present (`pyproject.toml`/`requirements.txt` → Python; `package.json` → JS/TS) rather than assuming — run only what applies, and say explicitly which gates don't apply here rather than silently skipping them.

**Python**: `pytest` (or the project's actual test runner/config), `ruff check` (or configured linter), `mypy`/`pyright` if the project uses one. Use whatever the project's own scripts/Makefile/CI config actually invoke if they differ from these defaults — that's the real gate, not a generic guess.

**JS/TS**: the project's own `lint`, `typecheck`/`tsc --noEmit`, test, and `build` scripts from `package.json` — run them, don't assume what they'd do.

**If this touched UI**: verify the actual rendered app (dev server, real navigation) covers loading/error/empty states, keyboard navigation, and both themes if the project has light/dark — not just that the component compiles.

**If this touched auth, user input handling, or added a dependency**: do a quick pass for the obvious risks (secrets in code/logs, injection, missing input validation, a newly-added package with known CVEs) — full security audit isn't required for every change, but skipping this check on the changes that touch these surfaces is how real bugs ship.

**Always**: `git status` and `git diff` — confirm nothing unintended is staged (`.env`, build output, credentials, debug prints left in) and that the diff actually matches what was asked for, not more and not less.

Report each gate as pass/fail with the actual command output that proves it, not "should work." If a gate fails, fix the root cause and re-run that gate — don't report done with a known-failing gate. If a gate is inapplicable to this change, say so explicitly rather than omitting it.
