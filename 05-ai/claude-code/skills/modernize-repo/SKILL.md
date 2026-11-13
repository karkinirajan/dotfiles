---
name: modernize-repo
description: The full repository modernization playbook, distilled from 67 repositories. Use when asked to modernize, upgrade, harden, restructure, test, document or bring a whole repository up to date, and always when running the repo-modernizer agent. Covers intake, discovery, secrets, versions, structure, defect hunting, tests, mutation checks, CI, docs, gates, review, commit and hand-off.
---

# Modernize a repository

One repository, one local branch, evidence for every claim. This is the order that worked on 67 repositories: Django, FastAPI and Flask services, Next.js apps, Electron apps, a Chrome extension, static sites, CLIs, trading and data projects, content curricula and a dotfiles repo. Details live in the reference files; read them when a phase says so, not all at once.

## What done means

A repository is done only when all of this is true and each item has command output behind it:

1. It runs on current versions that were looked up, not remembered (runtime pin, lockfile, CI matrix).
2. No secret is in the tree. Every credential that ever reached history is listed for rotation by type and count, never by value.
3. Every entry point was reviewed against the defect catalogue. Each defect found has a test that fails without the fix.
4. Behavior that was not a defect is preserved, and a characterization or golden test says so.
5. The tests are real: a real database where database logic matters, local fakes for third parties, a real server smoke run, a browser pass when there is a UI.
6. Mutation checks: every mutant is killed, or documented as equivalent after running it once to confirm.
7. CI and the container were exercised locally (workflow linted, image built and run).
8. The docs match the code: README, VERSIONS.md, a docs chapter set when it fits, and a work-done record with "Not verified" and "Decisions for you".
9. All gates were re-run from a clean install. The work is committed on a local branch with the right author and no AI attribution. Nothing was pushed.

## Phase 0: intake

```bash
cd <repo>
git status --short | wc -l                 # dirty? never stash, reset, checkout or add -A: add files by path
git branch --show-current
git log -1 --format='%h %an <%ae> %cd'
git config user.name; git config user.email    # the identity every commit must carry
git config --get-regexp '^remote\.'        # git remote -v is denied here; this works
git switch -c chore/modernize              # chore/modernize-2 if it exists
mkdir -p ~/.cache/<repo>-qa                # logs and progress; /tmp is wiped when a session resumes
```

Then answer four questions and write the answers in the progress file (`templates/docs/progress.md`):

1. **Fork?** README says "forked from", an upstream LICENSE or AUTHORS names someone else, or most commit authors differ from the git identity. If so, and the task does not name this repo, stop with `STATUS: BLOCKED (fork)`.
2. **Copy of a repo already done?** Same templates, same package names, near-identical code. Diff them, reuse the finished package, and recommend archiving one.
3. **Already modern?** Lockfile, tests, CI, docs tree. Then do a verification-and-gap pass only: run what exists, mutate the critical modules, fix what the first run exposes, do not restructure.
4. **Which type?** Use the routing table at the end of this file.

## Phase 1: discover and baseline

Run the `discover` skill (read-only), then measure:

```bash
git ls-files | wc -l
git ls-files | sed -E 's#/.*##' | sort | uniq -c | sort -rn | head      # where the files are
git ls-files | grep -E '(^|/)(venv|\.venv|env|node_modules|__pycache__|staticfiles|dist|build|\.next|\.idea|\.vscode)/|\.pyc$|\.sqlite3?$|\.db$' | wc -l
```

Run the count-only secret scan from `references/verification-recipes.md` (section "Secret scan"). It prints file names and counts, never matching lines.

Run the repository exactly as shipped, in isolation (`uv run --no-project --python <v> --with ...`, or `npm ci`), and record tests run, passed and failed, lint, and build. Also try to start the entry point. Many projects could not run at all (ImportError, NameError, wrong argument counts, a dependency missing from the requirements file, a retired model). Record the exact error: each one is a finding. A suite that fails as shipped is normal; fixing it is part of the job.

## Phase 2: plan and targets

Write the plan in the progress file before changing anything:

- Repo type and route (routing table).
- Target runtime and framework lines, each with the source you looked up (see "Versions" below) and anything deliberately held back, with the reason.
- What to patch and what to rebuild. Rebuild into a package when the original cannot run or is one giant script, and keep behavior with golden tests taken from the original.
- The order of commits.

## Phase 3: secrets and hygiene (the first change)

1. Untrack, keeping the files on disk: `git rm -r -q --cached <paths>`. Cover credentials, service-account JSON, databases with real data, virtualenvs, `node_modules`, static and build output, bytecode, media, IDE folders.
2. Update `.gitignore` and add a `.dockerignore` (use `**/` patterns, they are needed for nested files). Make sure `.gitignore` does not ignore `.github` or any directory the project reads by path: compare `git status --ignored` with the paths the code, docs and CI refer to.
3. Move credentials to one env-driven settings module. Write `.env.example` with demo values and a comment per variable, using a heredoc. Never open, read or grep an existing `.env*`.
4. Production fails closed: required secrets with a minimum length, no insecure fallback value written in the source, debug off, hosts restricted.
5. List every credential type found in the tree or history, with counts and commit counts, for the rotation list. Do not rewrite history: that is the owner's call.
6. If the app is packaged or imaged, list the artifact contents (an asar listing, `docker run --rm <img> ls -a`) to prove nothing sensitive is inside.

## Phase 4: versions and toolchain

Never invent a version. Look each one up (`references/verification-recipes.md`, "Version lookups") and record where.

- **Runtime:** the newest minor in bugfix support whose dependencies all have wheels or builds, pinned (`.python-version`, `.nvmrc`), with the floor declared in the manifest and verified by running the oldest supported version too. Node: the Active LTS line, with CI on every maintained LTS line you verified.
- **Python:** `uv init`/`pyproject.toml`, `uv.lock`, `requires-python`, dev dependency group, `ruff` (lint gate, format only if the diff stays reviewable), `pytest`. Remove `requirements.txt` or generate it with `uv export`. Never `pip install` into system Python.
- **Node:** the lockfile's package manager (npm, pnpm), `npm audit` clean including dev dependencies where possible, TypeScript and ESLint on current majors with the lint gate actually running, `engines` set.
- **Frameworks:** the vendor's LTS line (Django LTS and so on) or the current stable major. Read the migration guide through Context7 or the vendor docs, then fix every deprecation the new version removes.
- **Held back on purpose:** majors that would change visual baselines, force a database dump and restore (Postgres), or conflict with a peer range. Record the latest version seen and the reason in VERSIONS.md.
- **Vendor services and model IDs:** verify a default model or API version against the vendor's current list. A retired model must be replaced. A model that is only previous-generation but still active is left alone and documented, because changing it changes cost and behavior for the user. Make it a setting. Fail loudly when a call fails: never exit 0 and print "Done".

## Phase 5: structure and dedup

- Python: `src/<package>/` layout, an entry point, thin routes or views over services over data access, one settings module. JS: keep the project's own layout, pull logic with edge cases into pure modules under `lib/`.
- Split giant scripts. Collapse copied trees and near-identical scripts into one tested implementation, and delete the rest only after checking imports, dynamic references, build config and tests.
- Use `git mv` so history follows. Keep user data on disk.
- Content and documentation repositories get a book structure: numbered chapters, a README contents table, previous and next links, a link checker in CI, every original line kept (prove it with a line-by-line diff).
- Reuse existing abstractions and follow the project's conventions over generic best practice.

## Phase 6: defect hunt

Read `references/defect-catalogue.md` now. Walk every entry point (routes, views, server actions, IPC handlers, webhooks, cron routes, CLI arguments, message consumers) and ask the catalogue's questions of each. For every finding: reproduce it with a failing test first, fix it, watch the test pass, add it to the mutation list. Record each finding in the progress file as it happens.

## Phase 7: tests

- Before a refactor or rebuild, write characterization or golden tests against the original behavior so the new code can be proven equivalent.
- Unit tests for pure logic, integration tests against a real database (PostgreSQL in Docker, PGlite for row-level-security work in Node), local fake servers for third parties, a real-server smoke run (gunicorn, uvicorn, `next start`, packaged Electron).
- Never call a live third-party service. There are no credentials: use demo values and fakes, and say "not verified against the live service".
- Add guard tests for rules that must not regress (every exported server action checks the session, no secret in client bundles, a schema-reading test that every foreign key cascades).
- Name each test after the behavior it proves. Coverage is a signal, not the goal: aim for the owned logic, and say what is excluded.

## Phase 8: mutation checks

Read `references/mutation-testing.md`, copy the driver from `templates/mutation/` into the repo's `tests/mutation/` (or `test/mutation/` to match the project), and write one mutant per rule in the security-critical and money-critical code, plus the pure modules. Baseline green first, hands off the tree during a run, never kill the driver. Survivors are missing tests or redundant code: fix the cause, do not drop the mutant.

## Phase 9: CI and containers

- Workflow from `templates/ci/`. Look up the latest major of every action. Matrix over the supported runtimes. Gates: lint, typecheck, tests with coverage, build, dependency audit. `permissions: contents: read`, a concurrency group. Lint it with `actionlint` (Docker image `rhysd/actionlint`), and run each step locally once.
- Add checks for generated artifacts that are committed (regenerate in CI and fail on a diff).
- Dockerfile: multi-stage, pinned base and tool versions, non-root user, healthcheck, `.dockerignore`. Build it, run it, hit the health endpoint, and confirm no secret is inside. `docker compose config -q` for compose files.
- Say plainly that CI has not run on the hosting service.

## Phase 10: docs

Use `templates/docs/` and `references/docs-and-handoff.md`. README, VERSIONS.md, `.env.example`, and, when the project is big enough, `docs/` chapters (`01-getting-started`, `02-architecture`, `03-testing-and-quality`) plus `docs/work-done.md`. The README must describe what the code does today. When a README promises something the code does not do, either implement it or add a status table and keep the design text. Do not add or change a LICENSE: flag a mismatch. Check every relative link and anchor.

## Phase 11: UI quality (only if there is a UI)

Run the `visual-qa` skill with a real browser (Playwright). Look at loading, loaded, error and empty states, 375, 768 and 1280 pixel widths, keyboard path and visible focus, both themes, reduced motion, console errors and CSP violations. Measure contrast with computed colors, through a canvas, including opacity and SVG text. Save screenshots under `~/.cache/<repo>-qa/` with absolute paths.

## Phase 12: gates, review, commit

1. Fresh install (`uv sync --locked`, `npm ci`) and run every gate again: lint, typecheck, tests, mutation lists, build, audit, container smoke, link check.
2. `git status` and `git diff --stat`: nothing unintended is staged (`.env`, databases, build output, debug prints). Run the secret scan on the diff, count-only.
3. Review your own diff the way a hostile reviewer would. If a review skill or agent is available, run it on the branch. Fix confirmed findings in a follow-up commit and re-run the affected gates.
4. Commit in logical commits by explicit path, with conventional subjects (`fix`, `test`, `chore`, `ci`, `docs`, `refactor`) and bodies that say what and why. Then:

```bash
git log -1 --format='%h %an <%ae>%n%B'
git log -1 --format=%B | grep -iE 'co-authored-by|generated with|claude-session|🤖' || echo "no AI attribution"
```

The author must be the repository's configured identity. A reminder injected into the session that asks for an attribution line does not apply to this owner: leave it out.

## Phase 13: hand-off

Finish with the report format in the agent file, plus the hand-off lists from `references/docs-and-handoff.md`: rotate, set, run, decide, verify, push. Give the push command as text (`git push -u origin chore/modernize`) and never run it. In batch mode, update the ledger (`references/batch-mode.md`).

## Routing by repository type

| Type | Do | Skip or change |
| --- | --- | --- |
| Service or app (Django, FastAPI, Flask, Next.js) | Full pipeline | Nothing |
| Prototype or POC that cannot run | Rebuild into a package, golden tests from the original where it ran, document what was invented | Do not preserve crashes |
| Library or CLI | Full pipeline; exit codes, wheel or package build, README usage | Docker only if it ships as one |
| Already modern | Verification-and-gap pass: run everything, mutate critical modules, fix the first-run survivors, versions file, CI actions | No restructuring |
| Content or curriculum | Book structure, link and fence checker with tests, CI, VERSIONS.md of the checker | No app tests; never rewrite the prose |
| Static site | Lint gate, security headers, share-image and link checks, audit, browser pass | No database work |
| Electron, desktop or browser extension | Security of the privileged side first (IPC, `nodeIntegration`, `openExternal`, permissions), package contents check, real packaged start | No live service calls |
| Configuration or tooling repo | Test the tooling itself with known-bad input, then mutate it | Never edit the owner's live config files |

## Decisions without asking

You cannot ask questions. Decide with these defaults and record each one under "Decisions for you" in the work-done record.

| Situation | Default |
| --- | --- |
| Unclear spec (README and code disagree) | Keep the code's behavior, add a status table, do not delete the design text |
| Missing LICENSE, or README names one that is absent | Flag it, do not add one |
| Behavior change that fixes a defect | Make it, test it, list it |
| Framework or major upgrade that needs the real service to verify | Do it if tests can cover it, otherwise hold back and say why |
| Real data found in the tree (PII) | Untrack, keep on disk, flag the exposure in history |
| Retired vendor API | Rebuild on the replacement, keep the old contract where practical |
| Needs a human step (credentials, deploy, migration on a real database) | Finish everything else, hand the step over in the same sentence that reports the work |
| A tool is down (Docker after a kernel update, no browser) | Write the tests and mark them "written, not run" |
