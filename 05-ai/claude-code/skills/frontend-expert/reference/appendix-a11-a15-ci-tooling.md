# Appendix A.11–A.15: GitHub Actions, AGENTS.md, pnpm-workspace, ESLint, logger/rate-limit

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

## A.11 GitHub Actions (`.github/workflows/ci.yml`)

Every action is pinned to a full commit SHA with its version in a trailing comment; Renovate maintains the pins. The SHAs below were read from each repository's tags on 2026-10-12. `pnpm/action-setup` takes the pnpm version from `packageManager`. The Supabase step maps the local stack's values onto the variable names the app validates, using the CLI's `--override-name` flag (the key paths come from the CLI itself), and strips the quotes the `env` output format adds, because `GITHUB_ENV` would keep them literally. Gitleaks runs from its release tarball with a pinned checksum, so the scan depends on no third-party action or license. For mode B (see `appendix-a10-csp.md`), run `EXPOSE_TESTING_API=1 pnpm build` in the `e2e` job. Add Lighthouse CI as a further job once the key routes are defined (PERF-02, in `11-performance.md`).

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
          version: 2.120.0
      - run: supabase start
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
```

## A.12 `AGENTS.md` for AI coding assistants

`create-next-app` generates an `AGENTS.md`, and `next dev` maintains the `nextjs-agent-rules` block at the end of it. Keep that block and merge this content above it. The block between the `nextjs-agent-rules` markers is Next.js's own text, copied verbatim from 16.4.0 (it contains em dashes); `next dev` rewrites it, so do not edit it.

`AGENTS.md`

```markdown
# AGENTS.md

Source of truth for conventions: FRONTEND-MASTER.md (repo root), or the `frontend-expert` skill if this project uses Claude Code skills. Read sections 0, 5, 6, 7 and 9 before changing code. Cite rule IDs (for example SEC-01) in commit messages and PR descriptions.

## Commands

- `pnpm dev` runs the app locally.
- `pnpm check` runs typecheck, lint, format check, unit tests, and build. It must be green before you claim a task is done.
- `pnpm test:e2e` runs Playwright against a production build (`pnpm build` first).
- `just up` starts local Supabase and writes `.env.local`. `just types` regenerates database types.

## Non-negotiable rules

- Server Components by default. `"use client"` only on the smallest interactive leaf.
- Every Server Action and Route Handler: authenticate, authorize, validate with Zod, then act.
- All data access goes through server-only DAL functions. Never import the admin client or Prisma in components.
- Never expose secret keys. Only `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` is public.
- Use `getClaims()` on the server, never `getSession()`.
- Tailwind v4 tokens only: no raw palette classes, no arbitrary values, no `@apply` in components.
- No `any`, no non-null assertions, no unchecked casts, no `console.log`, no `useEffect` for data fetching.
- Every UI change covers loading, empty, and error states, keyboard use, light and dark themes, and 320px width.

## Do not

- Change auth, RLS policies, `proxy.ts`, security headers, or migrations without calling it out for human review.
- Add a dependency without stating its size, license, and why the platform cannot do the job.
- Commit, push to main, or read production secrets.

## When unsure

Ask one specific question, or present two or three options with trade-offs. Do not guess on security.

## Git

Author `kneeraazon404`. Conventional Commits. One concern per PR.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
```

## A.13 `pnpm-workspace.yaml` (pnpm 12)

`allowBuilds` lists the dependencies whose install scripts may run; pnpm 11 removed `onlyBuiltDependencies` and `ignoredBuiltDependencies`. `trustPolicy: no-downgrade` rejected two packages on 2026-10-12, and both exclusions are scoped to one exact version: `prisma@7.10.0` (the npm registry shows no provenance attestation on it, while 7.9.0 and `@prisma/client` 7.10.0 have one) and `semver@6.3.1` (transitive, through `eslint-config-next`). Remove an exclusion when the package moves on. When pnpm meets a pinned version younger than `minimumReleaseAge` (1440 minutes), it appends the package to `minimumReleaseAgeExclude` itself; delete those entries once the versions are a day old. `overrides` clear the two transitive advisories (`mysql2`, `deepmerge-ts`) that `pnpm audit --prod --audit-level=high` reported on a clean Prisma 7.10.0 install; re-check on every Prisma bump. The full `pnpm audit` (dev dependencies included) reports one high advisory on 2026-10-12: `braces` 3.0.3, CVE-2026-93687 (published 2026-09-18, stack exhaustion on deeply nested brace patterns), reached only through `eslint-config-next` > `@next/eslint-plugin-next` > `fast-glob` > `micromatch`. No patched `braces` release exists, so no override can fix it. It runs inside ESLint on your own glob patterns and never ships in the build, which is why CI gates on `pnpm audit --prod` (A.11 above). Re-run the full audit when `eslint-config-next` bumps.

`pnpm-workspace.yaml`

```yaml
# pnpm 12. Dependency settings live here, not in package.json.
allowBuilds:
  '@prisma/engines': true
  prisma: true
  sharp: true
  unrs-resolver: true

# minimumReleaseAge defaults to 1440 minutes and blockExoticSubdeps to true; both stay on.
# A pinned version younger than a day fails the install. Wait, or list the package here
# with a dated comment and remove the entry once the version is a day old:
# minimumReleaseAgeExclude:
#   - zod # 2026-10-12, remove after 2026-10-13

trustPolicy: no-downgrade
# Add a package here only after reading why trustPolicy flagged it.
trustPolicyExclude:
  - semver@6.3.1
  - prisma@7.10.0

# Transitive advisories reported by `pnpm audit --prod --audit-level=high`. Re-check on every Prisma bump.
overrides:
  mysql2: '>=3.23.1'
  deepmerge-ts: '>=8.0.0'
minimumReleaseAgeExclude:
  - '@tanstack/query-core@5.104.2'
  - '@tanstack/react-query@5.104.2'
  - '@vitest/mocker@5.0.4'
  - '@vitest/spy@5.0.4'
  - vitest@5.0.4
  - zod@4.6.7
```

## A.14 `eslint.config.mjs` (ESLint 10, flat config)

`eslint-config-next/core-web-vitals` already registers `react-hooks` (with the compiler rules), `jsx-a11y`, and the Next plugin. The strict a11y rules are added by spreading only the rule set, because registering the plugin a second time throws "Cannot redefine plugin". Typed linting uses `projectService`, so every linted `.ts` and `.mts` file must be in `tsconfig.json`'s `include` (A.1, in `appendix-a1-a6-core.md`).

`eslint.config.mjs`

```js
import { defineConfig, globalIgnores } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import tseslint from 'typescript-eslint';

export default defineConfig([
  // Already registers react-hooks (compiler rules), jsx-a11y, and the Next plugin.
  ...nextVitals,
  // Strict a11y rules only: registering the plugin again throws "Cannot redefine plugin".
  { rules: jsxA11y.flatConfigs.strict.rules },
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      'no-console': 'error',
      '@next/next/no-img-element': 'error',
      '@typescript-eslint/consistent-type-imports': ['error', { fixStyle: 'inline-type-imports' }],
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/switch-exhaustiveness-check': 'error',
      '@typescript-eslint/restrict-template-expressions': ['error', { allowNumber: true }],
    },
  },
  {
    // Plain JavaScript config files are outside tsconfig, so typed rules are off for them.
    files: ['**/*.mjs'],
    ...tseslint.configs.disableTypeChecked,
  },
  globalIgnores([
    '.next/**',
    'out/**',
    'build/**',
    'next-env.d.ts',
    'src/generated/**',
    'src/lib/supabase/database.types.ts',
    'playwright-report/**',
    'test-results/**',
  ]),
]);
```

## A.15 Logger and rate limiter

The logger writes JSON lines to stdout and stderr, so no `console.*` call exists in application code (OBS-01, in `13-observability.md`). The limiter is a fixed window on Redis. It fails open on Redis errors so an outage does not lock users out, and it logs every failure; for brute-force-sensitive endpoints (sign-in, OTP) switch the `catch` branch to `ok: false`.

`src/lib/logger.ts`

```ts
import 'server-only';

type Level = 'debug' | 'info' | 'warn' | 'error';
type Fields = Record<string, unknown>;

const LEVEL_RANK: Record<Level, number> = { debug: 10, info: 20, warn: 30, error: 40 };
const MIN_LEVEL: Level = process.env.NODE_ENV === 'production' ? 'info' : 'debug';

function write(level: Level, fields: Fields, message: string): void {
  if (LEVEL_RANK[level] < LEVEL_RANK[MIN_LEVEL]) return;
  const line = JSON.stringify({ level, time: new Date().toISOString(), message, ...fields });
  // stdout/stderr directly: structured, no console.* in application code.
  (level === 'error' || level === 'warn' ? process.stderr : process.stdout).write(`${line}\n`);
}

export const logger = {
  debug: (fields: Fields, message: string): void => {
    write('debug', fields, message);
  },
  info: (fields: Fields, message: string): void => {
    write('info', fields, message);
  },
  warn: (fields: Fields, message: string): void => {
    write('warn', fields, message);
  },
  error: (fields: Fields, message: string): void => {
    write('error', fields, message);
  },
} as const;
```

`src/lib/rate-limit.ts`

```ts
import 'server-only';
import Redis from 'ioredis';
import { serverEnv } from '@/lib/env/server';
import { logger } from '@/lib/logger';

export type RateLimitInput = Readonly<{ key: string; limit: number; windowSeconds: number }>;
export type RateLimitResult = Readonly<{
  ok: boolean;
  remaining: number;
  retryAfterSeconds: number;
}>;

const globalForRedis = globalThis as unknown as { redis?: Redis };
const redis =
  globalForRedis.redis ??
  new Redis(serverEnv.REDIS_URL, { maxRetriesPerRequest: 1, lazyConnect: true });
if (serverEnv.NODE_ENV !== 'production') globalForRedis.redis = redis;

/** Fixed-window limiter. Fails open on Redis errors for availability; the failure is logged. */
export async function rateLimit({
  key,
  limit,
  windowSeconds,
}: RateLimitInput): Promise<RateLimitResult> {
  try {
    const bucket = `rl:${key}`;
    const count = await redis.incr(bucket);
    if (count === 1) await redis.expire(bucket, windowSeconds);
    const ttl = await redis.ttl(bucket);
    return {
      ok: count <= limit,
      remaining: Math.max(0, limit - count),
      retryAfterSeconds: Math.max(ttl, 1),
    };
  } catch (error) {
    logger.error(
      { err: error instanceof Error ? error.message : 'unknown', key },
      'rate limiter unavailable',
    );
    return { ok: true, remaining: limit, retryAfterSeconds: 0 };
  }
}
```
