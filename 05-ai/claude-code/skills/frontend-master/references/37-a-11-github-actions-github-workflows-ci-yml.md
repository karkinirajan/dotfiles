### A.11 GitHub Actions (`.github/workflows/ci.yml`)

Every action is pinned to a full commit SHA with its version in a trailing comment; Renovate maintains the pins. The SHAs below were read from each repository's tags on 2026-10-12. `pnpm/action-setup` takes the pnpm version from `packageManager`. The Supabase step maps the local stack's values onto the variable names the app validates, using the CLI's `--override-name` flag (the key paths come from the CLI itself), and strips the quotes the `env` output format adds, because `GITHUB_ENV` would keep them literally. Gitleaks runs from its release tarball with a pinned checksum, so the scan depends on no third-party action or license. For mode B, run `EXPOSE_TESTING_API=1 pnpm build` in the `e2e` job. The `verify` job also runs `pnpm knip` and `pnpm deps:check` (TOOL-08), the `e2e` job runs the pgTAP suite (`supabase test db`, TEST-06), and the `security` job scans the lockfile with osv-scanner (pinned release, checksum verified) and runs the audit kit's static checks when `audit/audit.py` exists. Add Lighthouse CI as a further job once the key routes are defined (PERF-02).

`.github/workflows/ci.yml`

```yaml
name: ci

on:
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

env:
  NEXT_TELEMETRY_DISABLED: '1'

jobs:
  verify:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    env:
      NEXT_PUBLIC_SITE_URL: http://localhost:3000
      NEXT_PUBLIC_SUPABASE_URL: http://127.0.0.1:54321
      NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: sb_publishable_ci_placeholder
      SUPABASE_SECRET_KEY: sb_secret_ci_placeholder
      REDIS_URL: redis://127.0.0.1:6379
      DATABASE_URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres
      DIRECT_URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: pnpm/action-setup@d9184bf108216479bc5a137cc391f4d7b14c870b # v6.1.0
      - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0
        with:
          node-version-file: .nvmrc
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm typecheck
      - run: pnpm lint
      - run: pnpm format:check
      - run: pnpm knip
      - run: pnpm deps:check
      - run: pnpm test
      - run: pnpm audit --prod --audit-level=high
      - uses: actions/cache@55cc8345863c7cc4c66a329aec7e433d2d1c52a9 # v6.1.0
        with:
          path: .next/cache
          key: next-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}-${{ hashFiles('src/**') }}
          restore-keys: next-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}-
      - run: pnpm build

  e2e:
    needs: verify
    runs-on: ubuntu-latest
    timeout-minutes: 25
    services:
      redis:
        image: redis:8-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: pnpm/action-setup@d9184bf108216479bc5a137cc391f4d7b14c870b # v6.1.0
      - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0
        with:
          node-version-file: .nvmrc
          cache: pnpm
      - uses: supabase/setup-cli@45a513f8c64c0bc8e0e3dfe572b5c95be85f6359 # v3.0.1
        with:
          version: 2.121.0
      - run: supabase start
      - run: supabase test db
      - name: Export local Supabase settings
        run: |
          supabase status -o env \
            --override-name api.url=NEXT_PUBLIC_SUPABASE_URL \
            --override-name auth.publishable_key=NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY \
            --override-name auth.secret_key=SUPABASE_SECRET_KEY \
            --override-name db.url=DIRECT_URL \
            | sed -E 's/^([A-Za-z_]+)="?([^"]*)"?$/\1=\2/' \
            | grep -E '^(NEXT_PUBLIC_SUPABASE_URL|NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY|SUPABASE_SECRET_KEY|DIRECT_URL)=' \
            > "$RUNNER_TEMP/supabase.env"
          cat "$RUNNER_TEMP/supabase.env" >> "$GITHUB_ENV"
          sed -E 's/^DIRECT_URL=/DATABASE_URL=/' "$RUNNER_TEMP/supabase.env" | grep '^DATABASE_URL=' >> "$GITHUB_ENV"
          echo "NEXT_PUBLIC_SITE_URL=http://127.0.0.1:3100" >> "$GITHUB_ENV"
          echo "REDIS_URL=redis://127.0.0.1:6379" >> "$GITHUB_ENV"
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec playwright install --with-deps chromium
      # Mode B (SEC-08) builds with EXPOSE_TESTING_API=1 so instant() works. Never deploy that build.
      - run: pnpm build
      - run: pnpm test:e2e
      - uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2
        if: failure()
        with:
          name: playwright-report
          path: playwright-report
          retention-days: 7

  security:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    env:
      GITLEAKS_VERSION: 8.30.1
      GITLEAKS_SHA256: 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
      OSV_VERSION: 2.7.0
      OSV_SHA256: 160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          fetch-depth: 0
      - name: Install gitleaks
        run: |
          curl -fsSL -o "$RUNNER_TEMP/gitleaks.tgz" "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"
          echo "${GITLEAKS_SHA256}  $RUNNER_TEMP/gitleaks.tgz" | sha256sum -c -
          tar -xzf "$RUNNER_TEMP/gitleaks.tgz" -C "$RUNNER_TEMP" gitleaks
      - name: Scan history for secrets
        run: $RUNNER_TEMP/gitleaks git --redact --no-banner .
      - name: Install osv-scanner
        run: |
          curl -fsSL -o "$RUNNER_TEMP/osv-scanner" "https://github.com/google/osv-scanner/releases/download/v${OSV_VERSION}/osv-scanner_linux_amd64"
          echo "${OSV_SHA256}  $RUNNER_TEMP/osv-scanner" | sha256sum -c -
          chmod +x "$RUNNER_TEMP/osv-scanner"
      - name: Scan the lockfile for known vulnerabilities
        run: $RUNNER_TEMP/osv-scanner scan source --lockfile pnpm-lock.yaml
      - name: Static audit (Semgrep, SQL and structure checks)
        if: hashFiles('audit/audit.py') != ''
        run: |
          pip install semgrep==1.181.0
          python3 audit/audit.py run --profile ci
```

