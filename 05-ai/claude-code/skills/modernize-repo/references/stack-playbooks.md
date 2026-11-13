# Stack playbooks

What changed from stack to stack on the 67 repositories. Version numbers are deliberately absent: look them up (see `verification-recipes.md`) and record the source.

## Python, any framework

- `pyproject.toml` with `requires-python`, a dev dependency group, `.python-version`, and `uv.lock` committed. Delete `requirements.txt`, or keep a generated one (`uv export --no-hashes --no-dev --no-emit-project -o requirements.txt`) only when a deployment target needs it.
- A `src/<package>/` layout with an entry point. Split single large scripts into modules with clear seams. Keep the old behavior with golden tests.
- Lint gate with `ruff check`. Add `ruff format` only when the formatting diff stays reviewable, and expect it to reshape any mutation list.
- `pytest` with coverage on the owned code. Test the oldest supported Python as well as the pinned one (a matrix such as the floor and the newest, run locally with uv).
- Dependency audit in CI (`uv audit --preview-features audit-command` was used; check the flag still exists).
- Docker: multi-stage, a pinned uv image tag, a non-root user, bytecode compiled at build, a healthcheck.
- Models, endpoints and timeouts come from settings. Handlers never return `str(error)`.

## Django and DRF

- Move to the current LTS line. Collapse per-environment settings files into one env-driven module with no insecure defaults. Untrack `staticfiles`, media and databases.
- Production safety: `SecurityMiddleware` present, `ALLOWED_HOSTS` and `SECRET_KEY` required, `DEBUG` off, static files served by a safe handler that refuses database files.
- Default deny: a login middleware with an explicit allow-list of public routes, and a test that fails when a route appears outside the list.
- Passwords: replace weak hashers (MD5) with PBKDF2 or Argon2 and upgrade hashes at next login.
- Check each upgrade cliff: removed or renamed third-party packages (an abandoned JWT library replaced behind a compatibility layer that keeps the old header and body contract), lazy related-manager querysets that make copy actions copy nothing, logout over GET, `manage.py` missing from the repo, fixtures with wrong model labels.
- Tests on SQLite and on PostgreSQL. Django Channels: validated consumers, an origin check, a Redis layer, player identity bound to the connection, room registration serialized so a cap cannot be exceeded.
- Check the admin permissions and any rich-text field (sanitize on write and escape on read).

## FastAPI and Flask

- Application factory, settings object, CORS allow-list, optional API-key header, `/health` and `/ready`, bind to loopback by default.
- Flask: CSRF, no `debug=True`, no server started at import time, gunicorn for the smoke run.
- Uploads held in memory or a bounded temp area, never spooled and forgotten.
- A request-size cap set in the framework (Flask's `MAX_CONTENT_LENGTH`) answers 413 when `Content-Length` is over the limit, but under gunicorn a chunked body is cut at the limit without an error, the half document fails to parse, and the answer is 400. Assert "refused, and nothing stored" (400 or 413) in a real-server test.
- Pydantic 2 models with explicit bounds on every field, SQLAlchemy 2 style, psycopg 3.

## Next.js, React, TypeScript

- Move to the current stable major of Next and React, TypeScript and ESLint on their current majors, Vitest and Playwright on current majors. Remove `legacy-peer-deps` and fix the resulting lint findings in code instead of relaxing rules. If a rule must be off for a folder (for example a render-loop folder with intentional mutation), scope it to that folder and document the reason.
- `npm audit` including dev dependencies to zero where achievable, and say what remains and why when not.
- Server actions and route handlers: derive the user from the session inside the function; never export helpers from a `"use server"` file; validate and bound every input; return generic errors.
- Security headers (CSP, HSTS, framing, no `X-Powered-By`) in the framework config or `vercel.json`, checked in a real browser with no CSP violations.
- A rate limiter that survives deploys and instances (database counters with a migration), forwarded-IP headers trusted only behind a configured proxy or an opt-in.
- Cache invalidation: check that an edit is visible after saving, in a real browser.
- A static export is served with a static server, not `next start`. Share images referenced by metadata must exist.
- Build scripts that mutate a database (`prisma db push`) are a hand-off item: provide a `build:check` that does not.
- The project's `AGENTS.md` or contribution notes may require reading the framework docs shipped in `node_modules` before framework changes: read them.
- Design-affecting upgrades (framework, UI kit, CSS engine) are held back when visual baselines exist that cannot be regenerated locally, and recorded in VERSIONS.md with the reason.

## Electron and desktop apps

- Current Electron major. Context isolation and sandbox on, no `nodeIntegration` on any window that loads remote content, a preload with a narrow API, IPC handlers that validate arguments and cannot read arbitrary files.
- `shell.openExternal` and navigation only for `http(s)` URLs, behind a guard module that is itself listed in the packager's files (with a test that fails if it is not).
- Secrets at rest in the OS keyring facility, with migration of old plaintext data.
- Check the package contents by listing them. Run the packaged app headless for a start test. State that installers for other operating systems were not built.
- Keep the application's data folder name stable: a rename would orphan users' data.

## Chrome extensions (Manifest V3)

- Logic with edge cases in pure modules under `lib/` that export for Node tests and attach a global in the browser. Test those with `node --test`, mutate them, and keep `chrome.*` out of the tests.
- A build that validates the manifest and required files, a reproducible package (write it twice and compare hashes), and a CI check that any committed generated copy (such as a web version of the page) matches its generator.
- Permission and host-permission changes, new network requests and storage-shape changes are decisions for the owner: do not make them. Storage shape changes need a migration.
- Verify the extension in a real browser when you can; when you cannot, say the extension APIs were not exercised.

## Static sites and portfolios

- Lint gate that runs, headers, an audit, a real browser pass including WebGL or canvas content if present, working share images and metadata, a tested builder for contact links (no header injection, length limit), and honest README commands.
- Placeholder content (stock photos, fake credits, example social links) is flagged for the owner, not replaced.

## CLIs and automation scripts

- Console entry points, exit codes that tell the truth, bounded input (file size, page counts, zip expansion), retries as loops, secrets from the environment, a dry-run mode where the tool writes to a real system, and saved originals with a restore command when it edits someone else's data.
- Escape or strip control characters from anything printed from files or model output.
- Tests on a fake of the external client layer (Selenium, vendor SDKs) or on the real SDK over a stub transport.

## Data, finance and ML code

- Golden tests that reproduce the original results on the original versions (run the old code in an isolated environment to capture them), then run the same inputs through the new code on the new libraries.
- Boundary tests on both sides of every comparison, hand-computed expected values, look-ahead checks for anything time-indexed, concurrency tests with real file locks where orders are booked.
- Pickle loading of models is a defect; use a safe format or a signed artifact.
- Never contact a market-data or trading service; use recorded or generated data.

## AI-feature projects

- Model IDs, API versions and SDK calls are verified against the vendor's current pages. Replace retired APIs; leave active previous-generation models alone and say so.
- Keep prompts fixed on the server, user text fenced as data, outputs validated, per-user isolation, size and rate limits, timeouts, no key in the browser, no vendor error text returned.
- Tests run against a local fake of the vendor API. No real call is made.

## Content, curriculum and documentation repositories

- Structure it as a book: numbered chapter folders in the learning order, a README with a contents table and a map of the folders, previous and next links, one file per unit. Rename with `git mv` so history follows, and warn in the work-done record that external links to old paths will break.
- Keep every original line. Prove it with a line-by-line diff: only headings, tracker links and deliberate fixes may differ.
- Write a small checker (links, anchors, fences, numbering) with its own tests and mutation list, run it in CI, and verify the fences with a real CommonMark parser when a past change may have broken them.
- Facts that age (runtime versions, end-of-life dates, prices, model lines) are checked against live sources; prose is not rewritten.

## Configuration and tooling repositories

- Test the tooling with known-bad input: build throwaway git repositories with the global git config disabled, and feed the checkers files that must be rejected.
- Never edit the owner's live configuration files. If the owner has uncommitted changes, leave them alone and commit only your own files by path.
- Regenerating a dated snapshot can touch files the owner has open: skip it and say so.
