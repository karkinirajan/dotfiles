# Appendix A.1–A.6: Core config, env, Supabase clients, DAL, Server Action template

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index and `22-references-changelog.md` for the verification note: every file below was extracted from the source document into an empty project and exercised on 2026-10-12 with the exact versions in `01-versions-and-watch.md` §1.1: `next typegen && tsc --noEmit` (TypeScript 6.0.3), ESLint 10 with the A.14 config, `prettier --check`, Vitest, `prisma generate`, `next build`, `next start` and `next dev` with Chromium (CSP, hydration, axe at WCAG 2.2 AA in both color schemes, `instant()`), and `pnpm audit --prod` (clean). Each file is labeled with its path in code font on the line above its fence. Replace `PROJECT_REF` in A.2 with your Supabase project reference.

## A.1 `tsconfig.json`

Next.js adds fields such as `include` entries on first run; keep the strictness flags. Three choices are deliberate:

- `noUnusedLocals` and `noUnusedParameters` are off. Next's generated `.next/dev/types/validator.ts` has unused imports in apps without Route Handlers, and with those flags `next build` fails after a `next dev` run. `@typescript-eslint/no-unused-vars` in A.14 covers unused code.
- `exactOptionalPropertyTypes` is off (TS-02).
- There is no `baseUrl`. `paths` alone resolves `@/*` on TypeScript 6 and 7.

If `tsc` reports a typed-route error for a page that exists, delete `.next`: a stale `.next/cache/.tsbuildinfo` keeps the old error.

`tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "allowJs": false,
    "skipLibCheck": true,
    "noEmit": true,
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.mts",
    "**/*.tsx",
    ".next/types/**/*.ts",
    ".next/dev/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

## A.2 `next.config.ts`

The `turbopack.rules` entry wires `@tailwindcss/turbopack`. `headers` returns a promise instead of being `async` because the lint rule `require-await` is on. `exposeTestingApiInProductionBuild` stays false unless `EXPOSE_TESTING_API=1` is set (TEST-05). The Content Security Policy is set per request in `proxy.ts` (`appendix-a10-csp.md`).

`next.config.ts`

```ts
import type { NextConfig } from 'next';

const securityHeaders: { key: string; value: string }[] = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=(), payment=()' },
  { key: 'Cross-Origin-Opener-Policy', value: 'same-origin' },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains' },
];

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  reactCompiler: true,
  typedRoutes: true,
  poweredByHeader: false,
  // output: 'standalone', // self-hosting in a container (CI-08)
  turbopack: {
    rules: {
      '*.css': { loaders: ['@tailwindcss/turbopack'], as: '*.css' },
    },
  },
  images: {
    formats: ['image/avif', 'image/webp'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'PROJECT_REF.supabase.co',
        pathname: '/storage/v1/object/public/**',
      },
    ],
  },
  experimental: {
    // E2E builds only: EXPOSE_TESTING_API=1 pnpm build. Never deploy that build.
    exposeTestingApiInProductionBuild: process.env.EXPOSE_TESTING_API === '1',
  },
  headers: () => Promise.resolve([{ source: '/:path*', headers: securityHeaders }]),
};

export default nextConfig;
```

## A.3 Validated environment (`lib/env/public.ts` and `lib/env/server.ts`)

Public values are read as literal `process.env.NEXT_PUBLIC_*` references so the bundler can inline them. `REDIS_URL` is for the rate limiter (A.15, in `appendix-a11-a15-ci-tooling.md`); drop it if a platform firewall does the limiting. `DATABASE_URL` and `DIRECT_URL` are for Prisma option B (A.9, in `appendix-a7-a9-styling-prisma.md`); drop them otherwise. A missing variable fails the build or boot loudly. That is the point.

`src/lib/env/public.ts`

```ts
import { z } from 'zod';

const publicSchema = z.object({
  NEXT_PUBLIC_SITE_URL: z.url(),
  NEXT_PUBLIC_SUPABASE_URL: z.url(),
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: z.string().startsWith('sb_publishable_'),
});

// Literal property access is required: the bundler inlines NEXT_PUBLIC_* by exact name.
export const publicEnv = publicSchema.parse({
  NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
  NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
});
```

`src/lib/env/server.ts`

```ts
import 'server-only';
import { z } from 'zod';

const serverSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  SUPABASE_SECRET_KEY: z.string().startsWith('sb_secret_'),
  REDIS_URL: z.url(),
  // Prisma option B only:
  DATABASE_URL: z.url(),
  DIRECT_URL: z.url(),
});

export const serverEnv = serverSchema.parse(process.env);
```

## A.4 Supabase clients and session proxy

`updateSession` takes the request headers that `proxy.ts` built (nonce and CSP) and forwards them to the render. When Supabase refreshes the session, `setAll` receives the cache headers as its second argument; they go on the response so a CDN never caches a response that carries auth cookies. The redirect copies both the cookies and those headers. The redirect is a convenience: the DAL (A.5) and RLS still enforce access (SEC-02).

`src/lib/supabase/client.ts`

```ts
import { createBrowserClient } from '@supabase/ssr';
import { publicEnv } from '@/lib/env/public';
import type { Database } from '@/lib/supabase/database.types';

export function createClient() {
  return createBrowserClient<Database>(
    publicEnv.NEXT_PUBLIC_SUPABASE_URL,
    publicEnv.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
  );
}
```

`src/lib/supabase/server.ts`

```ts
import 'server-only';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import { publicEnv } from '@/lib/env/public';
import type { Database } from '@/lib/supabase/database.types';

export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient<Database>(
    publicEnv.NEXT_PUBLIC_SUPABASE_URL,
    publicEnv.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          try {
            for (const { name, value, options } of cookiesToSet) {
              cookieStore.set(name, value, options);
            }
          } catch {
            // Server Components cannot write cookies. proxy.ts refreshes the session on every request.
          }
        },
      },
    },
  );
}
```

`src/lib/supabase/admin.ts`

```ts
import 'server-only';
import { createClient } from '@supabase/supabase-js';
import { publicEnv } from '@/lib/env/public';
import { serverEnv } from '@/lib/env/server';
import type { Database } from '@/lib/supabase/database.types';

export const supabaseAdmin = createClient<Database>(
  publicEnv.NEXT_PUBLIC_SUPABASE_URL,
  serverEnv.SUPABASE_SECRET_KEY,
  { auth: { persistSession: false, autoRefreshToken: false } },
);
```

`src/lib/supabase/proxy.ts`

```ts
import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';
import { publicEnv } from '@/lib/env/public';
import type { Database } from '@/lib/supabase/database.types';

const PROTECTED_PREFIXES = ['/dashboard', '/settings', '/admin'] as const;

function isProtected(pathname: string): boolean {
  return PROTECTED_PREFIXES.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}

/**
 * Refreshes the Supabase session and returns the response that carries the refreshed cookies.
 * `requestHeaders` are forwarded to the render (nonce, CSP) and must be the same object the caller built.
 */
export async function updateSession(
  request: NextRequest,
  requestHeaders: Headers,
): Promise<NextResponse> {
  let response = NextResponse.next({ request: { headers: requestHeaders } });

  const supabase = createServerClient<Database>(
    publicEnv.NEXT_PUBLIC_SUPABASE_URL,
    publicEnv.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet, cacheHeaders) => {
          for (const { name, value } of cookiesToSet) request.cookies.set(name, value);
          requestHeaders.set('cookie', request.headers.get('cookie') ?? '');
          response = NextResponse.next({ request: { headers: requestHeaders } });
          for (const { name, value, options } of cookiesToSet)
            response.cookies.set(name, value, options);
          // A response that sets auth cookies must never be cached by a CDN or proxy.
          for (const [key, value] of Object.entries(cacheHeaders)) response.headers.set(key, value);
        },
      },
    },
  );

  // Run nothing between createServerClient and getClaims.
  const { data } = await supabase.auth.getClaims();

  if (!data?.claims && isProtected(request.nextUrl.pathname)) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = '/login';
    loginUrl.search = '';
    loginUrl.searchParams.set('next', request.nextUrl.pathname); // relative path only; validate on use (SEC-11)
    const redirect = NextResponse.redirect(loginUrl);
    for (const cookie of response.cookies.getAll()) redirect.cookies.set(cookie);
    for (const [key, value] of response.headers) {
      if (['cache-control', 'expires', 'pragma'].includes(key)) redirect.headers.set(key, value);
    }
    return redirect;
  }

  return response;
}
```

`src/lib/supabase/database.types.ts` is generated by `just types` (TS-11); this placeholder lets the templates compile before the first generation.

`src/lib/supabase/database.types.ts`

```ts
export type Database = {
  public: {
    Tables: {
      projects: {
        Row: { id: string; name: string; owner_id: string; created_at: string };
        Insert: { id?: string; name: string; owner_id: string; created_at?: string };
        Update: { id?: string; name?: string; owner_id?: string; created_at?: string };
        Relationships: [];
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
    CompositeTypes: Record<string, never>;
  };
};
```

## A.5 Session and DAL

`src/lib/auth/session.ts`

```ts
import 'server-only';
import { cache } from 'react';
import { redirect } from 'next/navigation';
import { z } from 'zod';
import { createClient } from '@/lib/supabase/server';

export type Session = Readonly<{
  userId: string;
  role: 'user' | 'admin';
  orgId: string | null;
}>;

const claimsSchema = z.object({
  sub: z.uuid(),
  app_metadata: z
    .object({
      role: z.enum(['user', 'admin']).default('user'),
      org_id: z.uuid().nullish(),
    })
    .default({ role: 'user' }),
});

/** Null when unauthenticated. Use in Server Actions and Route Handlers. */
export const getSession = cache(async (): Promise<Session | null> => {
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getClaims();
  if (error || !data?.claims) return null;

  const parsed = claimsSchema.safeParse(data.claims);
  if (!parsed.success) return null;

  return {
    userId: parsed.data.sub,
    role: parsed.data.app_metadata.role,
    orgId: parsed.data.app_metadata.org_id ?? null,
  };
});

/** Redirects when unauthenticated. Use in Server Components and DAL reads. */
export async function verifySession(): Promise<Session> {
  const session = await getSession();
  if (!session) redirect('/login');
  return session;
}
```

`src/features/projects/queries.ts`

```ts
import 'server-only';
import { cache } from 'react';
import { verifySession } from '@/lib/auth/session';
import { createClient } from '@/lib/supabase/server';
import { logger } from '@/lib/logger';

export type ProjectDTO = Readonly<{ id: string; name: string; ownerId: string; createdAt: string }>;

export const getProject = cache(async (id: string): Promise<ProjectDTO | null> => {
  await verifySession();
  const supabase = await createClient(); // user-scoped client: RLS enforces row access

  const { data, error } = await supabase
    .from('projects')
    .select('id, name, owner_id, created_at')
    .eq('id', id)
    .maybeSingle();

  if (error) {
    logger.error({ code: error.code, projectId: id }, 'project query failed');
    throw new Error('PROJECT_QUERY_FAILED');
  }
  if (!data) return null;

  return { id: data.id, name: data.name, ownerId: data.owner_id, createdAt: data.created_at };
});
```

When the data access model is Prisma (PRISMA-01 option B, in `07-data-layer.md`), RLS does not apply. Add the ownership predicate to the query (`where: { id, ownerId: session.userId }`) and keep the `verifySession` result in use.

## A.6 Server Action template

`z.object` strips unknown keys, so it is the right choice for raw `FormData`: do not use `.strict()` there, because Next adds internal `$ACTION_*` fields for progressive enhancement. Use `.strict()` for JSON bodies. RLS hides rows the user may not touch, so "missing" and "not yours" look identical; that is intended. Non-idempotent creates (orders, payments) additionally take an idempotency key generated once per form mount and enforced by a unique column (REACT-17).

`src/lib/action-result.ts`

```ts
export type ActionErrorCode =
  'unauthenticated' | 'forbidden' | 'invalid' | 'rate_limited' | 'not_found' | 'server_error';

export type ActionResult<T> =
  | { ok: true; data: T }
  | { ok: false; code: ActionErrorCode; fieldErrors?: Record<string, string[] | undefined> };
```

`src/features/projects/actions.ts`

```ts
'use server';

import { updateTag } from 'next/cache';
import { z } from 'zod';
import type { ActionResult } from '@/lib/action-result';
import { getSession } from '@/lib/auth/session';
import { logger } from '@/lib/logger';
import { rateLimit } from '@/lib/rate-limit';
import { createClient } from '@/lib/supabase/server';

const renameProjectSchema = z.object({
  projectId: z.uuid(),
  name: z.string().trim().min(1).max(120),
});

export async function renameProject(
  _previous: ActionResult<{ id: string }> | null,
  formData: FormData,
): Promise<ActionResult<{ id: string }>> {
  const started = performance.now();

  const session = await getSession();
  if (!session) return { ok: false, code: 'unauthenticated' };

  const limit = await rateLimit({
    key: `rename-project:${session.userId}`,
    limit: 20,
    windowSeconds: 60,
  });
  if (!limit.ok) return { ok: false, code: 'rate_limited' };

  const parsed = renameProjectSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return { ok: false, code: 'invalid', fieldErrors: z.flattenError(parsed.error).fieldErrors };
  }
  const { projectId, name } = parsed.data;

  const supabase = await createClient();
  const { data, error } = await supabase
    .from('projects')
    .update({ name })
    .eq('id', projectId)
    .select('id')
    .maybeSingle();

  if (error) {
    logger.error(
      { action: 'renameProject', code: error.code, userId: session.userId },
      'action failed',
    );
    return { ok: false, code: 'server_error' };
  }
  if (!data) return { ok: false, code: 'not_found' };

  updateTag(`project:${projectId}`);

  logger.info(
    { action: 'renameProject', outcome: 'ok', durationMs: Math.round(performance.now() - started) },
    'action completed',
  );
  return { ok: true, data: { id: data.id } };
}
```
