# Verification recipes

How each kind of claim was proven. Every recipe prints evidence; none needs a live third-party service or a real credential.

## Secret scan

Count-only. Names and numbers go to the output, matching lines never do, and `.env*` files are excluded from every file-list grep.

Write the patterns once to `~/.cache/<repo>-qa/secret-patterns.txt`, one alternative per line:

```text
sk-[A-Za-z0-9_-]{20,}
AKIA[0-9A-Z]{16}
-----BEGIN [A-Z ]*PRIVATE KEY-----
(mongodb|postgres(ql)?|mysql|redis|amqp)(\+srv)?://[^ "']+:[^ "'@]+@
(api[_-]?key|secret|token|passw(or)?d)[ ]*[=:][ ]*["'][A-Za-z0-9_./+=-]{12,}
xox[bap]-[A-Za-z0-9-]{10,}
ghp_[A-Za-z0-9]{30,}
AIza[0-9A-Za-z_-]{30,}
```

Then:

```bash
P=~/.cache/<repo>-qa/secret-patterns.txt
# files in the tree that match (names only)
git ls-files -z ':(exclude,glob)**/.env*' | xargs -0 grep -IlE -f "$P" 2>/dev/null
# how many added lines in all of history match (a number, never the lines)
git log --all -p --format= | grep -E '^\+' | grep -cE -f "$P"
# risky file names that were ever committed
git log --all --name-only --format= | grep -iE '(^|/)\.env($|\.)|\.pem$|id_rsa|credentials[^/]*\.json$|service[-_]?account|\.p12$|\.keystore$' | sort -u
# how many commits touched them
git log --all --oneline -- <path> | wc -l
```

Record, per credential type: where, how many commits, and that it must be rotated. A scan that finds nothing is reported as "scan clean, patterns listed", not as "no secrets".

## Versions and lifecycle

Look every version up and write the source in VERSIONS.md.

```bash
# PyPI
curl -s https://pypi.org/pypi/<pkg>/json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["info"]["version"], d["info"]["requires_python"])'
# npm
npm view <pkg> version; npm outdated
# Python and framework support windows, and most products (python, django, nodejs, postgresql, redis, ubuntu ...)
curl -s https://endoflife.date/api/<product>.json | python3 -m json.tool | head -40
# Node.js lines, LTS and end-of-life dates
curl -s https://raw.githubusercontent.com/nodejs/Release/main/schedule.json
# Latest release of a GitHub Action, and of a tool such as uv
curl -s https://api.github.com/repos/actions/checkout/releases/latest | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["tag_name"], d["published_at"][:10])'
```

Vendor model and API lists (model IDs, API versions, shutdown dates) come from the vendor's own page or SDK reference. Library migration guides come from Context7 (`resolve-library-id`, then `query-docs`) or the vendor docs. If a source is unreachable, write "unverified" in VERSIONS.md instead of a number.

## Isolated runs

Do not touch system Python. Use uv.

```bash
uv run --no-project --python 3.13 --with <dep> --with pytest python -m pytest      # as-shipped baseline without installing into the repo
uv sync --locked && uv run pytest -q                                                 # after the pyproject exists
uv python install 3.12 3.13 3.14                                                     # multi-version runs
UV_PYTHON=3.12 uv run pytest -q                                                      # set UV_PYTHON for the whole run: a nested uv run inside a test fixture otherwise rebuilds the environment under another version
```

Several Node versions without installing them: run a copy of the project in `node:<n>-slim` containers.

```bash
docker run --rm -v "$PWD:/src:ro" node:22-slim sh -c 'mkdir /work && cd /src && tar --exclude=node_modules --exclude=dist -cf - . | tar -xf - -C /work && cd /work && npm ci --no-audit --no-fund && npm test'
```

The test runner's output format differs between Node lines (`# pass` on 22, `ℹ pass` on 24 and 26): judge by exit code, then count.

## Real database

- PostgreSQL in Docker (`postgres:17` and the newest major) for Django, SQLAlchemy and raw SQL work. Run the whole suite on both. Test migrations on a copy of real data when the schema changes.
- Row-level-security and policy work in Node: PGlite, reproduced against the shipped migration files.
- A test that reads the live schema and fails when a table that references a user lacks `ON DELETE CASCADE`.

## Fakes for third parties

- Write a small local HTTP server that speaks the vendor's wire format, point the real SDK at it through its base-URL setting, and run the flow. The SDK usage is then real and the service is the only fake.
- Where a base URL cannot be set, give the SDK a stub transport.
- State in the work-done record: "No live call to <vendor> was made."

## Real server smoke

Start the production entry point (gunicorn, uvicorn, `next start`, the packaged app), call the health route, one authenticated route, one forbidden route, and one bad-input route. For a container: build, run, hit health, `docker run --rm <img> ls -a` to prove no `.env` or database, check the user is not root, then `docker rmi`. For compose: `docker compose config -q` with demo values.

If Docker cannot run (for example after a kernel update until a reboot), write the tests and mark them "written, not run" in the work-done record.

## Browser pass

Use the `visual-qa` skill. Playwright through a throwaway uv environment (the Chromium cache in `~/.cache/ms-playwright` survives resumes):

```bash
uv run --no-project --with playwright python script.py
```

Checklist and measurements:

- Real server, not the dev overlay. Capture console errors and CSP violations.
- Widths 375, 768, 1280. Loading, loaded, error and empty states. Keyboard path with visible focus.
- Both themes; if the app's theme is manual, click its toggle (emulating the OS setting does nothing).
- Contrast: read computed colors, convert through a canvas (modern CSS may compute `oklab(...)`, which parsing as rgb gets wrong), include element opacity and SVG text.
- Stub `window.prompt` and `window.confirm` with `evaluate` before triggering them (a native dialog makes the Playwright tool return early).
- Save screenshots with absolute paths under `~/.cache/<repo>-qa/`.

## Workflow files

```bash
docker run --rm -v "$PWD:/repo:ro" -w /repo rhysd/actionlint:latest; echo "exit $?"
```

Read the exit code directly (a pipe to `tail` replaces it). Then run each step of the workflow locally once, including a negative control for any "generated files are current" check: edit a generated file by hand and confirm the check notices and the generator repairs it.

## Generated and ignored artifacts

Before running any script that writes output (zip, build, export), list what already exists and is ignored: `git status --ignored -s | head`. A release package that is git-ignored and looks like leftover output may be the owner's real artifact. If you must write to it, build the original from the untouched base branch in a scratch directory first and restore it afterwards, and say so.

## Evidence rules

- A claim in a report is a command you ran and its output. If you did not run it, it goes under "Not verified".
- Never state a number you did not measure. Counts of tests, mutants and advisories come from the tool output.
- Before and after numbers (advisories, tracked files, tests, mutants killed by the original tests) make the work-done record useful. Measure the "before" before you change anything.
