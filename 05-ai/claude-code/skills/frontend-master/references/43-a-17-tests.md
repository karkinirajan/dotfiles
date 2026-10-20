### A.17 Tests

Vitest runs in jsdom with the `@` alias and an empty stand-in for `server-only`. The config is `.mts` so Vite loads it as ESM. The action test shows the TEST-04 matrix: unauthenticated, invalid input, rate limited, not found, and success with the cache invalidation call. Playwright runs against the production build on a fixed port with a mobile and a desktop project. `csp.spec.ts` fails when any script is blocked or the page does not hydrate (verified by running it against the broken nonce-on-prerendered-shell setup, where it reports the violations). `a11y.spec.ts` runs axe against WCAG 2.2 AA in both color schemes, which also checks the A.7 tokens in the browser.

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
vi.mock('@/lib/logger', () => {
  const log = { info: vi.fn(), warn: vi.fn(), error: vi.fn() };
  return { logger: log, requestLogger: () => Promise.resolve(log) };
});
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

// Tests that call Supabase directly (auth.spec.ts) read the same .env.local the app does.
try {
  process.loadEnvFile('.env.local');
} catch (error) {
  if (!(error instanceof Error && 'code' in error && error.code === 'ENOENT')) throw error;
}

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

