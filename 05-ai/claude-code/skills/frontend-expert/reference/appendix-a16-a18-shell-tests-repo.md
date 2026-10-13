# Appendix A.16–A.18: App shell/providers, tests, repository files

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

## A.16 App shell, providers, and reference routes

Mode A layout: `export const instant = false` and `await connection()` make every route render per request so the nonce reaches every script (SEC-08, in `09-security.md`). `Providers` reads the nonce from the `x-nonce` request header and hands it to `next-themes`. TanStack Query mounts only in the route group that needs it (RQ-01, in `05-react.md`): `getQueryClient` returns a fresh client per call on the server and one shared client in the browser (RQ-02), and `QueryProvider` is mounted in `dashboard/layout.tsx`. The reference routes show a static page, a link, and a dashboard whose per-user content sits inside `Suspense` with a skeleton of the final height (NEXT-08, in `06-nextjs.md`).

`src/app/layout.tsx`

```tsx
import type { Metadata } from 'next';
import { GeistMono } from 'geist/font/mono';
import { GeistSans } from 'geist/font/sans';
import { connection } from 'next/server';
import { Providers } from '@/components/shared/providers';
import './globals.css';

// Mode A (SEC-08): every route renders per request, so the CSP nonce reaches every script tag.
export const instant = false;

export const metadata: Metadata = {
  title: { default: 'Template', template: '%s | Template' },
  description: 'Template app',
};

export default async function RootLayout({ children }: LayoutProps<'/'>) {
  await connection();
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-dvh bg-background text-foreground">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

`src/components/shared/providers.tsx`

```tsx
import { headers } from 'next/headers';
import { ThemeProvider } from 'next-themes';
import type { ReactNode } from 'react';

/** Mode A: next-themes injects an inline script, which only runs when it carries the request nonce. */
export async function Providers({ children }: { children: ReactNode }) {
  const nonce = (await headers()).get('x-nonce') ?? undefined;
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
      nonce={nonce}
    >
      {children}
    </ThemeProvider>
  );
}
```

`src/lib/query/get-query-client.ts`

```ts
import {
  QueryClient,
  defaultShouldDehydrateQuery,
  environmentManager,
} from '@tanstack/react-query';

function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      // Non-zero so hydrated server data is not refetched immediately (RQ-03).
      queries: { staleTime: 60 * 1000 },
      dehydrate: {
        // Include pending queries so prefetches can stream to the client (RQ-06).
        shouldDehydrateQuery: (query) =>
          defaultShouldDehydrateQuery(query) || query.state.status === 'pending',
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined;

/** New client per call on the server (never shared across requests), one per tab in the browser (RQ-02). */
export function getQueryClient(): QueryClient {
  if (environmentManager.isServer()) return makeQueryClient();
  browserQueryClient ??= makeQueryClient();
  return browserQueryClient;
}
```

`src/components/shared/query-provider.tsx`

```tsx
'use client';

import { QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { getQueryClient } from '@/lib/query/get-query-client';

export function QueryProvider({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={getQueryClient()}>{children}</QueryClientProvider>;
}
```

`src/components/shared/empty-state.tsx`

```tsx
import type { ReactNode } from 'react';

type EmptyStateProps = Readonly<{
  title: string;
  description: string;
  action?: ReactNode;
}>;

/** Reason plus primary action (UI-09). */
export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <section className="flex flex-col items-start gap-3 rounded-lg border p-6">
      <h2 className="text-lg font-semibold text-balance">{title}</h2>
      <p className="text-pretty text-muted-foreground">{description}</p>
      {action}
    </section>
  );
}
```

`src/app/page.tsx`

```tsx
import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="mx-auto max-w-prose p-6">
      <h1 className="text-2xl font-semibold text-balance">Template</h1>
      <p className="text-pretty text-muted-foreground">Static content.</p>
      <nav aria-label="Primary" className="mt-4 flex gap-4">
        <Link href="/login" className="underline underline-offset-4">
          Sign in
        </Link>
        <Link href="/dashboard" className="underline underline-offset-4">
          Dashboard
        </Link>
      </nav>
    </main>
  );
}
```

`src/app/login/page.tsx`

```tsx
export default function LoginPage() {
  return (
    <main className="mx-auto max-w-prose p-6">
      <h1 className="text-2xl font-semibold">Sign in</h1>
    </main>
  );
}
```

`src/app/dashboard/layout.tsx`

```tsx
import type { ReactNode } from 'react';
import { QueryProvider } from '@/components/shared/query-provider';

// Mount TanStack Query only in route groups that need client-side server state (RQ-01).
export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <QueryProvider>{children}</QueryProvider>;
}
```

`src/app/dashboard/page.tsx`

```tsx
import { Suspense } from 'react';
import { verifySession } from '@/lib/auth/session';

async function Greeting() {
  const session = await verifySession();
  return <p>Signed in as {session.userId}</p>;
}

export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-prose p-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <Suspense fallback={<p className="h-6 animate-pulse rounded bg-muted" aria-hidden />}>
        <Greeting />
      </Suspense>
    </main>
  );
}
```

## A.17 Tests

Vitest runs in jsdom with the `@` alias and an empty stand-in for `server-only`. The config is `.mts` so Vite loads it as ESM. The action test shows the TEST-04 matrix (in `12-testing.md`): unauthenticated, invalid input, rate limited, not found, and success with the cache invalidation call. Playwright runs against the production build on a fixed port with a mobile and a desktop project. `csp.spec.ts` fails when any script is blocked or the page does not hydrate (verified by running it against the broken nonce-on-prerendered-shell setup, where it reports the violations). `a11y.spec.ts` runs axe against WCAG 2.2 AA in both color schemes, which also checks the A.7 tokens in the browser.

`vitest.config.mts`

```ts
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

const fromRoot = (path: string): string => fileURLToPath(new URL(path, import.meta.url));

export default defineConfig({
  resolve: {
    alias: {
      '@': fromRoot('./src'),
      'server-only': fromRoot('./tests/setup/server-only.ts'),
    },
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}'],
    setupFiles: ['./tests/setup/vitest.setup.ts'],
    env: {
      NODE_ENV: 'test',
      NEXT_PUBLIC_SITE_URL: 'http://localhost:3000',
      NEXT_PUBLIC_SUPABASE_URL: 'http://127.0.0.1:54321',
      NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_test_placeholder',
      SUPABASE_SECRET_KEY: 'sb_secret_test_placeholder',
      REDIS_URL: 'redis://127.0.0.1:6379',
      DATABASE_URL: 'postgresql://postgres:postgres@127.0.0.1:54322/postgres',
      DIRECT_URL: 'postgresql://postgres:postgres@127.0.0.1:54322/postgres',
    },
  },
});
```

`tests/setup/vitest.setup.ts`

```ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

`tests/setup/server-only.ts`

```ts
export {};
```

`src/components/shared/empty-state.test.tsx`

```tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { EmptyState } from '@/components/shared/empty-state';

describe('EmptyState', () => {
  it('exposes the title as a heading and renders the description and action', () => {
    render(
      <EmptyState
        title="No projects yet"
        description="Create a project to get started."
        action={<button type="button">Create project</button>}
      />,
    );

    expect(screen.getByRole('heading', { name: 'No projects yet' })).toBeInTheDocument();
    expect(screen.getByText('Create a project to get started.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create project' })).toBeInTheDocument();
  });
});
```

`src/lib/security/csp.test.ts`

```ts
import { describe, expect, it } from 'vitest';
import { buildCsp } from '@/lib/security/csp';

describe('buildCsp', () => {
  it('allows only the request nonce for scripts and drops unsafe-eval outside development', () => {
    const csp = buildCsp({ nonce: 'abc123', isDev: false });

    expect(csp).toContain("script-src 'self' 'nonce-abc123' 'strict-dynamic'");
    expect(csp).not.toContain('unsafe-eval');
    expect(csp).toContain("object-src 'none'");
  });

  it('derives the Realtime WebSocket origin from the Supabase URL scheme', () => {
    expect(buildCsp({ nonce: 'n', isDev: false })).toContain('ws://127.0.0.1:54321');
  });

  it('adds unsafe-eval only in development', () => {
    expect(buildCsp({ nonce: 'n', isDev: true })).toContain("'unsafe-eval'");
  });
});
```

`src/features/projects/actions.test.ts`

```ts
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { getSession, rateLimit, updateTag, maybeSingle } = vi.hoisted(() => ({
  getSession: vi.fn(),
  rateLimit: vi.fn(),
  updateTag: vi.fn(),
  maybeSingle: vi.fn(),
}));

vi.mock('next/cache', () => ({ updateTag }));
vi.mock('@/lib/auth/session', () => ({ getSession }));
vi.mock('@/lib/rate-limit', () => ({ rateLimit }));
vi.mock('@/lib/logger', () => ({ logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() } }));
vi.mock('@/lib/supabase/server', () => ({
  createClient: () => ({
    from: () => ({ update: () => ({ eq: () => ({ select: () => ({ maybeSingle }) }) }) }),
  }),
}));

import { renameProject } from '@/features/projects/actions';

const PROJECT_ID = '0b8f6f3e-6a54-4f77-9d9e-6b3f1c0a1b2c';

function form(fields: Record<string, string>): FormData {
  const data = new FormData();
  for (const [key, value] of Object.entries(fields)) data.set(key, value);
  return data;
}

describe('renameProject', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getSession.mockResolvedValue({ userId: 'u1', role: 'user', orgId: null });
    rateLimit.mockResolvedValue({ ok: true, remaining: 19, retryAfterSeconds: 0 });
  });

  it('rejects unauthenticated callers before touching the database', async () => {
    getSession.mockResolvedValue(null);
    const result = await renameProject(null, form({ projectId: PROJECT_ID, name: 'A' }));
    expect(result).toEqual({ ok: false, code: 'unauthenticated' });
    expect(maybeSingle).not.toHaveBeenCalled();
  });

  it('returns field errors for invalid input', async () => {
    const result = await renameProject(null, form({ projectId: 'not-a-uuid', name: '   ' }));
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.code).toBe('invalid');
      expect(result.fieldErrors).toHaveProperty('projectId');
      expect(result.fieldErrors).toHaveProperty('name');
    }
  });

  it('returns rate_limited when the limiter rejects', async () => {
    rateLimit.mockResolvedValue({ ok: false, remaining: 0, retryAfterSeconds: 30 });
    const result = await renameProject(null, form({ projectId: PROJECT_ID, name: 'A' }));
    expect(result).toEqual({ ok: false, code: 'rate_limited' });
  });

  it('returns not_found when RLS hides the row', async () => {
    maybeSingle.mockResolvedValue({ data: null, error: null });
    const result = await renameProject(null, form({ projectId: PROJECT_ID, name: 'A' }));
    expect(result).toEqual({ ok: false, code: 'not_found' });
    expect(updateTag).not.toHaveBeenCalled();
  });

  it('invalidates the project tag on success', async () => {
    maybeSingle.mockResolvedValue({ data: { id: PROJECT_ID }, error: null });
    const result = await renameProject(null, form({ projectId: PROJECT_ID, name: 'Roadmap' }));
    expect(result).toEqual({ ok: true, data: { id: PROJECT_ID } });
    expect(updateTag).toHaveBeenCalledWith(`project:${PROJECT_ID}`);
  });
});
```

`playwright.config.ts`

```ts
import { defineConfig, devices } from '@playwright/test';

const PORT = 3100;

export default defineConfig({
  testDir: 'tests/e2e',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['html', { open: 'never' }], ['list']] : 'list',
  use: { baseURL: `http://127.0.0.1:${PORT}`, trace: 'on-first-retry' },
  // Runs against the production build: `pnpm build` first (TEST-05).
  webServer: {
    command: `pnpm exec next start --port ${PORT} --hostname 127.0.0.1`,
    url: `http://127.0.0.1:${PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  projects: [
    {
      name: 'mobile',
      use: { ...devices['Desktop Chrome'], viewport: { width: 390, height: 844 } },
    },
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
    },
  ],
});
```

`tests/e2e/csp.spec.ts`

```ts
import { expect, test } from '@playwright/test';

declare global {
  interface Window {
    __cspViolations: string[];
  }
}

test('the CSP blocks nothing and the page hydrates', async ({ page }) => {
  const pageErrors: string[] = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  await page.addInitScript(() => {
    window.__cspViolations = [];
    document.addEventListener('securitypolicyviolation', (event) => {
      window.__cspViolations.push(`${event.violatedDirective} ${event.blockedURI || 'inline'}`);
    });
  });

  const response = await page.goto('/');
  expect(response?.headers()['content-security-policy']).toBeTruthy();
  await page.waitForLoadState('networkidle');

  // React attaches a fiber to every DOM node it hydrated. No fiber means no script ran.
  const hydrated = await page
    .locator('h1')
    .evaluate((node) => Object.keys(node).some((key) => key.startsWith('__reactFiber')));

  expect(await page.evaluate(() => window.__cspViolations)).toEqual([]);
  expect(pageErrors).toEqual([]);
  expect(hydrated).toBe(true);
});
```

`tests/e2e/a11y.spec.ts`

```ts
import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

for (const colorScheme of ['light', 'dark'] as const) {
  test(`home has no detectable WCAG 2.2 AA violations (${colorScheme})`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    await page.goto('/');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze();
    expect(results.violations).toEqual([]);
  });
}
```

## A.18 Repository files

`package.json` pins every version exactly (VER-01, in `01-versions-and-watch.md`); `postinstall` and the two `DIRECT_URL`/`DATABASE_URL` lines belong to Prisma option B. `pnpm typecheck` runs `next typegen` first because route types (`LayoutProps`, typed routes) are generated. `.env.example` has empty secrets on purpose: an empty value fails the Zod parse at boot. The `justfile` writes `.env.local` from the local Supabase stack, so run `just up` before `pnpm i`.

`package.json`

```json
{
  "name": "app",
  "version": "0.1.0",
  "private": true,
  "engines": {
    "node": ">=24"
  },
  "packageManager": "pnpm@12.11.2",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "postinstall": "prisma generate",
    "typecheck": "next typegen && tsc --noEmit",
    "lint": "eslint .",
    "format:check": "prettier --check .",
    "test": "vitest run",
    "test:e2e": "playwright test",
    "check": "pnpm typecheck && pnpm lint && pnpm format:check && pnpm test && pnpm build"
  },
  "dependencies": {
    "@prisma/adapter-pg": "7.10.0",
    "@prisma/client": "7.10.0",
    "@supabase/ssr": "0.12.7",
    "@supabase/supabase-js": "2.117.3",
    "@tanstack/react-query": "5.104.2",
    "babel-plugin-react-compiler": "1.0.0",
    "geist": "1.7.2",
    "ioredis": "6.0.0",
    "next": "16.4.0",
    "next-themes": "0.4.6",
    "react": "19.3.0",
    "react-dom": "19.3.0",
    "server-only": "0.0.1",
    "tw-animate-css": "1.4.0",
    "zod": "4.6.7"
  },
  "devDependencies": {
    "@axe-core/playwright": "4.13.0",
    "@next/playwright": "16.4.0",
    "@playwright/test": "1.64.0",
    "@tailwindcss/turbopack": "4.3.3",
    "@testing-library/jest-dom": "7.0.1",
    "@testing-library/react": "16.3.3",
    "@types/node": "24.19.2",
    "@types/react": "19.3.0",
    "@types/react-dom": "19.3.0",
    "eslint": "10.12.0",
    "eslint-config-next": "16.4.0",
    "eslint-plugin-jsx-a11y": "6.10.2",
    "jsdom": "30.1.2",
    "prettier": "3.9.10",
    "prettier-plugin-tailwindcss": "0.8.1",
    "prisma": "7.10.0",
    "tailwindcss": "4.3.3",
    "typescript": "6.0.3",
    "typescript-eslint": "8.71.1",
    "vitest": "5.0.4"
  }
}
```

`.nvmrc`

```text
24
```

`.prettierrc.json`

```json
{
  "printWidth": 100,
  "singleQuote": true,
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app/globals.css"
}
```

`.prettierignore`

```text
pnpm-lock.yaml
.next
src/generated
src/lib/supabase/database.types.ts
playwright-report
test-results
```

`.gitignore`

```text
/node_modules
/.next/
/out/
/build
/coverage
/playwright-report
/test-results
/src/generated
.DS_Store
*.pem
npm-debug.log*
.env*
!.env.example
*.tsbuildinfo
next-env.d.ts
```

`.env.example`

```bash
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SECRET_KEY=
REDIS_URL=redis://127.0.0.1:6379
# Prisma option B (A.9). Remove both lines when Prisma is not used.
DATABASE_URL=
DIRECT_URL=
```

`justfile`

```makefile
# Start the local Supabase stack and write .env.local (run before `pnpm i`; postinstall needs DIRECT_URL).
up:
    supabase start
    supabase status -o env --override-name api.url=NEXT_PUBLIC_SUPABASE_URL --override-name auth.publishable_key=NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY --override-name auth.secret_key=SUPABASE_SECRET_KEY --override-name db.url=DIRECT_URL | sed -E 's/^([A-Za-z_]+)="?([^"]*)"?$/\1=\2/' | grep -E '^(NEXT_PUBLIC_SUPABASE_URL|NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY|SUPABASE_SECRET_KEY|DIRECT_URL)=' > .env.local
    echo 'NEXT_PUBLIC_SITE_URL=http://localhost:3000' >> .env.local
    echo 'REDIS_URL=redis://127.0.0.1:6379' >> .env.local
    sed -E 's/^DIRECT_URL=/DATABASE_URL=/' .env.local | grep '^DATABASE_URL=' >> .env.local

# Reset the local database to the current migrations and seed it.
reset:
    supabase db reset --local

# Regenerate database types (TS-11).
types:
    supabase gen types typescript --local > src/lib/supabase/database.types.ts

# Run the pgTAP policy tests (TEST-06).
test-db:
    supabase test db --local
```
