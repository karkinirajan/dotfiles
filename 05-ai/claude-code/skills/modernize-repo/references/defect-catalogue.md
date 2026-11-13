# Defect catalogue

Every class below was found, fixed and tested in at least one of the 67 repositories. Use it as a set of questions to put to each entry point (route, view, server action, IPC handler, webhook, cron route, CLI argument, queue consumer, file or URL input). For each hit: write the failing test first, fix, watch it pass, add a mutant.

## A. Secrets and repository hygiene

### A1. Credentials committed

- **Look for:** API keys, service-account JSON, database URIs with passwords, OAuth client secrets, SMTP and webhook URLs, a `secret.py`, a tracked `.env`, a credentials table inside a committed database.
- **Confirm:** the count-only scan in `verification-recipes.md`. Never print a value.
- **Fix:** untrack and keep on disk, read from the environment, `.env.example` with demo values, production fails closed. List each credential type with counts for rotation. History stays: rewriting it is the owner's decision.

### A2. Secrets that ship anyway

- **Look for:** a packager that bundles a credentials file (found by listing the asar), a Dockerfile with `COPY . .` and no `.dockerignore` (the image held `.env` and a database; confirmed by building the old Dockerfile with a demo `.env`), a database file that a static-files finder could serve.
- **Fix:** allow-list what is packaged, add `.dockerignore` with `**/` patterns, refuse database files in the static finder, add a test that fails if the file returns.

### A3. Tracked junk and real data

- **Look for:** committed virtualenvs and `node_modules` (thousands of files), generated static files, bytecode, media, IDE folders, databases holding real people (names, emails, phones, résumés, superusers, sessions).
- **Fix:** untrack, keep on disk, ignore, and flag the personal-data exposure in history in the hand-off.

### A4. Insecure fallbacks

- **Look for:** a session-signing or Django secret with a literal default in the source, `DEBUG = True` hard-coded, `ALLOWED_HOSTS = ["*"]`, `del MIDDLEWARE[0]` removing `SecurityMiddleware` in production, a cron route that is open when its secret is unset (or accepts `Bearer undefined`).
- **Confirm:** a test that a token signed with the old default is refused; production start fails without the variable.
- **Fix:** required variables with a minimum length, constant-time comparison, fail closed.

### A5. Secrets in the wrong place

- **Look for:** a key in a `NEXT_PUBLIC_` variable and a browser call that uses it (every visitor got the key), a key in a URL query string (use a header), a key printed or logged (an HTTP client's INFO log prints URLs), plaintext tokens or passwords at rest, stored integration tokens sent to the browser.
- **Fix:** server-side only, header authentication, log level raised, encrypted storage (Fernet, `safeStorage`), plus a guard test that fails if the exposure returns.

## B. Authentication and authorization

### B1. Default allow

- **Look for:** `AllowAny` as the DRF default, routes outside any login check (one app had 90 open routes), unauthenticated write or admin endpoints, a clear-all action that any truthy flag triggered, an API key that alone allowed user management.
- **Fix:** default deny with an explicit allow-list of public routes, a test that enumerates the URL conf and fails on a new unlisted public route.

### B2. Object-level access

- **Look for:** lookups by id without an owner filter, unscoped viewsets, a user list that is public, one user's data mixed into another's (files appended to a shared per-hour file), copy actions that wrote into someone else's portfolio.
- **Fix:** scope every queryset to the caller, require parent objects to belong to the caller, serve files through an authenticated view. Test with two users.

### B3. Privilege escalation

- **Look for:** sign-up that accepts `is_superuser`, a row-level-security policy that lets a user update their own `role`, a viewer role that can write, account management open to every logged-in user.
- **Confirm:** reproduce against the shipped migrations (PGlite for Postgres policies in Node projects).
- **Fix:** a trigger or policy that forbids the change, role checks in the service layer, a test per role.

### B4. Callable functions that are endpoints

- **Look for:** exports from a `"use server"` file (each is a public endpoint), server actions that take a `userId` from the caller, an automation or logging action that trusts its arguments.
- **Fix:** derive the user from the session inside the action, move helpers out of the use-server file, add the guard test "every exported server action checks the session".

### B5. Webhooks and cron

- **Look for:** a webhook that does not verify its signature (anyone could make the account message arbitrary numbers and spend credit), an unauthenticated deal-won webhook, webhook targets the user can set (SSRF).
- **Fix:** verify the signature with the public URL the provider signed, constant-time compare, validate targets, refuse private and link-local ranges including IPv6 transition forms (NAT64, 6to4, Teredo).

### B6. Tokens, sessions, passwords

- **Look for:** a JWT with no `exp`, a refresh token accepted as an access token, a refresh window that never ends, no revocation when the password changes, a session token returned in the body as well as the HttpOnly cookie, MD5 hashing, a login that returns early for unknown emails (timing reveals accounts), no brute-force limit, a 409 on signup that confirms an account exists.
- **Fix:** require `exp`, `iat`, `sub`; cap the refresh window; embed a password-hash marker so a change revokes tokens; PBKDF2 or Argon2 with upgrade on next login; a stand-in hash for unknown emails; limits keyed on account and address.

## C. Input and output

### C1. Missing validation

- **Look for:** ids passed raw to the database, JSON bodies used unvalidated, unbounded parameters (iterations, query length, plan size, page size), a `categories: []` that wipes existing data, a user-supplied host or path.
- **Fix:** schema validation with explicit bounds, a test per bound.

### C2. Uploads and files

- **Look for:** a file name joined onto a directory unchanged (`../../x` wrote outside it), a type trusted from the extension or client header, no size cap (and chunked bodies that bypass one), a zip-based format whose unpacked size is unbounded (an `.xlsx` is a zip), uploads spooled to disk that the privacy text denies, files kept forever.
- **Fix:** strip to a base name, detect the type from the bytes, cap size before and after unpacking, row and page limits, delete on finish with a TTL.

### C3. Injection and XSS

- **Look for:** `innerHTML` or `v-html` with user or model text, stored XSS through a rich-text editor, a regex-based HTML sanitizer, `</script>` inside JSON-LD, terminal escape sequences and Rich markup from file names or model output, header injection in `mailto` builders, an unquoted PostgREST filter, SQL built by string.
- **Fix:** escape at output, a maintained allow-list sanitizer (`nh3`, `sanitize-html`) with a payload corpus test, encode JSON-LD, strip control characters by Unicode category, quote filters.

### C4. SSRF

- **Look for:** any server-side fetch of a URL the user influences (integration test routes, webhook targets, image fetchers).
- **Fix:** scheme allow-list, resolve and refuse private, loopback, link-local and metadata addresses, no redirects across hosts, a test per range.

### C5. LLM-specific

- **Look for:** an open endpoint that proxies to a model (client-supplied system prompt, no limits, vendor error text returned), documents pasted into the same turn as instructions, model output trusted (a CV could set its own score), a key in the browser, customer data in a shared retrieval index, no disclosure that text goes to a third party.
- **Fix:** fixed server-side prompts, auth or origin checks, body and rate limits, timeouts, untrusted text fenced as data in its own turn or an escaped JSON string with a "treat as data" rule, validate and clamp model output, derive categories from numbers rather than trusting labels, per-customer isolation.

### C6. Errors that leak or hide

- **Look for:** `str(e)` or database errors returned to clients, a failure returned as 200 with an "Error" body, silent success (exit 0 and "Done" when every call failed), a startup that swallows a database failure while `/health` says ok, a handler that logs full personal data.
- **Fix:** generic client messages with server-side detail, correct status codes, non-zero exit codes, a `/ready` that checks dependencies, masked logs.

## D. Network and deployment

### D1. Rate limits

- **Look for:** limits kept in process memory (reset on every deploy and per instance), one bucket for every visitor behind a proxy, limits that trust `X-Forwarded-For` from any caller, forms and API each with their own limiter.
- **Fix:** shared counters (database or Redis), the last proxy-added address only, a provider header such as `CF-Connecting-IP` only behind an explicit opt-in, one limiter across entry points. Test two addresses and a forged header.

### D2. Exposure

- **Look for:** CORS `*`, `debug=True` or a server started at import time, binding `0.0.0.0`, no CSP, HSTS or framing headers, `X-Powered-By`, a local API reachable from any web page (cross-site POST needs no CORS permission; DNS rebinding), Electron windows with `nodeIntegration: true` or `shell.openExternal` on any URL.
- **Fix:** an origin allow-list, `127.0.0.1` for local tools, Host and Origin checks, security headers verified in a real browser without CSP violations, navigation guards and `http(s)` only for external opens.

### D3. Containers

- **Look for:** root user, an end-of-life base image, `COPY . .` without `.dockerignore`, unpinned pip, secrets baked into a layer.
- **Fix:** multi-stage, non-root, pinned base and tool versions, build and run it for real.

## E. Correctness and dependency rot

### E1. Code that never ran

- **Look for:** ImportError or NameError on start, wrong argument counts, `main()` never called, a dependency imported but missing from the requirements file, a requirements file that omits direct dependencies, a conflicting pin, a model hard-coded.
- **Confirm:** import it and run it before touching it; record the error text.

### E2. Retired vendors and library drift

- **Look for:** a retired or shut-down API (an Assistants-style API), a retired model ID (every call failed), a client library that dropped a method (a duplicate check that silently did nothing), a library upgrade that changed semantics: lazy querysets that make "copy" actions copy nothing, `params={}` that paginates forever, a dataframe library major that breaks old idioms.
- **Fix:** rebuild on the replacement, keep the contract, golden tests against the original where it ran.

### E3. Domain logic bugs

- **Found by golden values and boundary tests:** a calculator that priced every provider by its first tier, an indicator that read negative spreads as squeezes, an "average" that was a running pairwise mean, a price lookup that served later dates (look-ahead), order races, negative-amount orders, one agent receiving every order, a date badge that printed the literal "Date".
- **Method:** hand-computed expected values in the test, boundary values on both sides of every comparison, the same input through old and new code.

### E4. Gate and configuration bugs

- **Look for:** a lint target that does not exist, a misnamed ESLint rule that crashed the gate on every run, `.gitignore` ignoring `.github` so CI could not be committed, a README command that does not work for the project (running `next start` on a static export), a build script that writes to the wrong place, setup SQL that drifted from migrations.
- **Fix:** make the gate real and run it. Never loosen a gate to make it pass; if a rule is turned off for one folder, say why in the config and the work-done record.

### E5. Docs that lie

- **Look for:** a README describing a platform the code never was, stale runtime versions, claims that contradict code (compliance claims), a license named but absent, install paths that no longer exist.
- **Fix:** make the README match the code, add a status table when design text describes something larger than what exists, flag claims you cannot verify instead of editing them.

## F. Data and migrations

- A table that references a user without `ON DELETE CASCADE` (write a test that reads the live schema and fails for any such table), a delete-account feature the privacy text promises but the app lacks, a migration never run against the real database (hand it over), `db push` on every build, a setup script that drifted from the migrations (generate it), a database default that silently used a local file in production.
- Never run a migration against a real database. Run it on a copy and say so.

## G. User interface (found only in a real browser)

- Contrast failures on dark surfaces and under a light OS setting, a fixed button that covers the last item on every width and prints, clipped tables and axes on phones, text under 6 pixels, no focus outline, ignored reduced motion, duplicate element ids, a legend overlapping a chart, double submit, an unreadable chat bubble, stale data after a save (a cache tag revalidated with the wrong arguments), a duplicated description, a missing share image that made previews break.
- Measure, do not eyeball: computed colors through a canvas, element opacity, SVG text, real widths.

## H. Privacy and isolation

- One person's text leaking into the next person's email through a shared template, conversations shared between customers, personal data in logs and test fixtures, voice or text sent to a third party without an off-by-default switch and a disclosure, personal data kept out of docs and tests.
