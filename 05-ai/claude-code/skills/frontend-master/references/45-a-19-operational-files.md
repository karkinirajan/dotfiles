### A.19 Operational files

These files satisfy MUST rules that the templates above do not cover: error boundaries (NEXT-03, OBS-04), health and readiness (OBS-08), request error reporting (NEXT-19), metadata routes (NEXT-13), the security contact and incident runbook (SEC-23, SEC-24), review ownership and the PR template (CI-02, GIT-02), ADRs (GOV-01), git hooks (TOOL-04), editor, dependency automation and architecture gates (TOOL-06, TOOL-08, TOOL-09), the container build (CI-08), and the reference database schema with its pgTAP tests (SB-01, SB-10, TEST-06, OBS-07).

Replace every `CHANGEME` before launch. The audit kit's launch profile fails while one remains. `knip.jsonc` lists reference modules that have no consumer yet; delete each entry when its consumer exists. `osv-scanner.toml` carries the one accepted advisory with an expiry date (A.13). `src/app/api/ready` checks the Supabase auth service, so it needs the Supabase stack reachable; `/api/health` has no dependencies. Hooks are installed once per clone with `pnpm exec lefthook install`. lefthook's install script is denied in A.13 and the binary runs without it.

`supabase/migrations/20260101000000_projects_and_audit_log.sql` and its test are the reference schema that A.5 and A.6 query. With Prisma owning the schema (PRISMA-02), put the same SQL inside a Prisma migration instead. `supabase/config.toml` comes from `supabase init`.

#### Routes and instrumentation

`src/app/error.tsx`

```tsx
'use client';

type RouteErrorProps = Readonly<{
  error: Error & { digest?: string };
  reset: () => void;
}>;

export default function RouteError({ error, reset }: RouteErrorProps) {
  return (
    <main id="main" className="mx-auto max-w-prose p-6">
      <div role="alert">
        <h1 className="text-2xl font-semibold text-balance">Something went wrong</h1>
        <p className="text-pretty text-muted-foreground">
          This page could not be loaded. Try again. If it keeps happening, contact support and quote
          the reference below.
        </p>
        {error.digest ? (
          <p className="mt-2 text-sm text-muted-foreground">
            Support reference: <code>{error.digest}</code>
          </p>
        ) : null}
      </div>
      <button
        type="button"
        onClick={reset}
        className="mt-4 inline-flex min-h-11 items-center rounded-md bg-primary px-4 text-primary-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
      >
        Try again
      </button>
    </main>
  );
}
```

`src/app/global-error.tsx`

```tsx
'use client';

import './globals.css';

type GlobalErrorProps = Readonly<{
  error: Error & { digest?: string };
  reset: () => void;
}>;

// Replaces the root layout when it fails, so it renders its own <html> and <body>.
export default function GlobalError({ error, reset }: GlobalErrorProps) {
  return (
    <html lang="en">
      <body className="min-h-dvh bg-background text-foreground">
        <main id="main" className="mx-auto max-w-prose p-6">
          <div role="alert">
            <h1 className="text-2xl font-semibold text-balance">The application hit an error</h1>
            <p className="text-pretty text-muted-foreground">
              Reload to try again. If it keeps happening, contact support and quote the reference
              below.
            </p>
            {error.digest ? (
              <p className="mt-2 text-sm text-muted-foreground">
                Support reference: <code>{error.digest}</code>
              </p>
            ) : null}
          </div>
          <button
            type="button"
            onClick={reset}
            className="mt-4 inline-flex min-h-11 items-center rounded-md bg-primary px-4 text-primary-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            Reload
          </button>
        </main>
      </body>
    </html>
  );
}
```

`src/app/not-found.tsx`

```tsx
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = { title: 'Page not found' };

export default function NotFound() {
  return (
    <main id="main" className="mx-auto max-w-prose p-6">
      <h1 className="text-2xl font-semibold text-balance">Page not found</h1>
      <p className="text-pretty text-muted-foreground">
        The page does not exist or you cannot access it.
      </p>
      <Link href="/" className="mt-4 inline-block underline underline-offset-4">
        Back to the home page
      </Link>
    </main>
  );
}
```

`src/app/api/health/route.ts`

```ts
import { connection } from 'next/server';

/** Liveness: cheap, unauthenticated, no dependencies (OBS-08). */
export async function GET(): Promise<Response> {
  await connection(); // never prerendered at build time
  return Response.json({ status: 'ok' }, { headers: { 'Cache-Control': 'no-store' } });
}
```

`src/app/api/ready/route.ts`

```ts
import 'server-only';
import { connection } from 'next/server';
import { publicEnv } from '@/lib/env/public';
import { requestLogger } from '@/lib/logger';

const TIMEOUT_MS = 2_000;
const HEADERS = { 'Cache-Control': 'no-store' } as const;

/** Readiness: the auth service behind Supabase answers within the timeout (OBS-08). */
export async function GET(): Promise<Response> {
  await connection(); // never prerendered at build time
  const log = await requestLogger();
  try {
    const response = await fetch(`${publicEnv.NEXT_PUBLIC_SUPABASE_URL}/auth/v1/health`, {
      headers: { apikey: publicEnv.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY },
      signal: AbortSignal.timeout(TIMEOUT_MS),
      cache: 'no-store',
    });
    if (!response.ok) {
      log.warn({ status: response.status }, 'readiness check failed');
      return Response.json({ status: 'unavailable' }, { status: 503, headers: HEADERS });
    }
    return Response.json({ status: 'ready' }, { headers: HEADERS });
  } catch (error) {
    log.warn({ reason: error instanceof Error ? error.name : 'unknown' }, 'readiness check failed');
    return Response.json({ status: 'unavailable' }, { status: 503, headers: HEADERS });
  }
}
```

`src/app/robots.ts`

```ts
import type { MetadataRoute } from 'next';
import { publicEnv } from '@/lib/env/public';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: '*', allow: '/', disallow: ['/dashboard', '/settings', '/admin', '/api/'] },
    ],
    sitemap: `${publicEnv.NEXT_PUBLIC_SITE_URL}/sitemap.xml`,
  };
}
```

`src/app/sitemap.ts`

```ts
import type { MetadataRoute } from 'next';
import { publicEnv } from '@/lib/env/public';

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: publicEnv.NEXT_PUBLIC_SITE_URL },
    { url: `${publicEnv.NEXT_PUBLIC_SITE_URL}/login` },
  ];
}
```

`src/instrumentation.ts`

```ts
import type { Instrumentation } from 'next';

export function register(): void {
  // Initialise Sentry or OpenTelemetry here once the provider is chosen in an ADR (OBS-02, OBS-03).
}

function digestOf(error: unknown): string | undefined {
  if (typeof error === 'object' && error !== null && 'digest' in error) {
    return typeof error.digest === 'string' ? error.digest : undefined;
  }
  return undefined;
}

function headerValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

/** Reports every server render, route, action and proxy error with its route context (NEXT-19). */
export const onRequestError: Instrumentation.onRequestError = async (error, request, context) => {
  if (process.env.NEXT_RUNTIME !== 'nodejs') return;
  const { logger } = await import('@/lib/logger');
  logger.error(
    {
      route: context.routePath,
      routeType: context.routeType,
      method: request.method,
      requestId: headerValue(request.headers['x-request-id']),
      digest: digestOf(error),
      errorName: error instanceof Error ? error.name : 'UnknownError',
    },
    'request error',
  );
};
```

#### Security contact, incident runbook, ADRs

`public/.well-known/security.txt`

```text
Contact: mailto:CHANGEME@your-domain.example
Expires: 2027-10-17T00:00:00.000Z
Preferred-Languages: en
Canonical: https://CHANGEME.your-domain.example/.well-known/security.txt
```

`docs/security/incident.md`

```markdown
# Security incident runbook

Owner: CHANGEME. Review after every incident and at least twice a year.

## Rule zero

If a vulnerable version of Next.js, React, Supabase or Prisma packages, or any other dependency, was
internet-exposed, assume compromise. Do not wait for proof of exploitation.

## 1. Triage (first hour)

1. Open a private incident channel and name one incident lead.
2. Record the time you learned of the issue, what you know, and the affected deployments.
3. Freeze deploys that are not the fix.

## 2. Contain and patch

1. Ship the patched version through the normal pipeline (SEC-20: Critical within 24 hours, High within
   72 hours). Use the emergency path, not a hotfix branch that skips checks.
2. If the patch is not available, block the vulnerable route at the platform firewall.
3. Confirm the fix on production with the original reproduction.

## 3. Rotate every secret the server could read

Rotate all of these, even if you only suspect exposure, then redeploy so the new values are live:

- Supabase secret key and legacy `service_role` key, and the JWT signing keys.
- Database passwords and `DATABASE_URL`, `DIRECT_URL`.
- Redis credentials, webhook signing secrets, and every third-party API key in server env.
- CI tokens and deploy tokens that were present in the affected environment.

Rotation order: create the new value, deploy it, confirm traffic works, then revoke the old value.

## 4. Revoke sessions

- Delete rows from `auth.sessions` to end all refresh tokens.
- Access tokens already issued stay valid until they expire. To invalidate them immediately, rotate
  the JWT signing key.

## 5. Review

1. Pull request, auth, database and platform logs for the exposure window.
2. Look for new users, role changes (`audit_log`), new API keys, unexpected storage objects and
   unexpected outbound traffic.
3. Write down what was accessed and what was not, with evidence.

## 6. Notify

1. Tell the client as soon as exposure is plausible, with facts and next steps. Do not wait for the
   final report.
2. Where personal data is involved, legal notification deadlines can apply (GDPR gives 72 hours to
   report to the supervisory authority after becoming aware). The client decides on regulator and
   user notices; give them what they need.

## 7. Follow up

1. Write the post-incident review within five working days: timeline, root cause, what worked, what
   failed, actions with owners and dates.
2. Record any deviation from a MUST rule as an ADR with an expiry date (GOV-04).
```

`docs/adr/0000-template.md`

```markdown
# NNNN. Title

- Status: Proposed | Accepted | Superseded by NNNN
- Date: YYYY-MM-DD
- Owner: name

## Context

What forces are at work: constraints, requirements, rules involved (cite rule IDs).

## Options

1. Option A: what it is, and what it costs.
2. Option B: what it is, and what it costs.

## Decision

The option chosen and the main reason.

## Consequences

What becomes easier, what becomes harder, what must be revisited and when.
```

`docs/adr/0001-auth-cookie-model.md`

```markdown
# 0001. Auth cookie model

- Status: Accepted
- Date: 2026-10-17
- Owner: CHANGEME

## Context

SEC-10 requires session cookies to be `HttpOnly`. `@supabase/ssr` 0.12.7 sets `httpOnly: false` by
default and omits `Secure`, because its browser client must read the session cookie in JavaScript.
That makes the session readable by any script that runs on the page, which turns every XSS bug into
an account takeover.

## Options

1. Server-only auth. Every `setAll` passes cookie options through `hardenCookie` (A.4), so the
   cookies are `HttpOnly`. Sign-in, sign-out and token refresh run on the server (Server Actions and
   `proxy.ts`). The browser client has no session and acts as `anon`.
2. JavaScript-readable cookies (the library default). The browser client keeps a live session, so
   Realtime and client-side queries run as the signed-in user. Compensate with the nonce CSP (SEC-08),
   short JWT lifetimes, and no third-party scripts.

## Decision

Option 1. Browser-side Supabase calls that need the user's identity go through Server Actions or
Route Handlers.

## Consequences

- An XSS bug cannot read the session cookie. It can still act as the user from the page, so SEC-07
  and SEC-08 stay mandatory.
- `createBrowserClient` cannot make authenticated calls. Realtime channels that need the user's
  identity need a server-issued token or Option 2; record that exception in a new ADR with an expiry.
- Revisit if a feature needs authenticated Realtime on the client.
```

#### Review, hooks, editor, dependency automation

`.github/CODEOWNERS`

```text
# Changes here need review from the owner (CI-02).
/supabase/migrations/ @kneeraazon404
/src/lib/auth/ @kneeraazon404
/src/lib/supabase/ @kneeraazon404
/src/lib/security/ @kneeraazon404
/src/proxy.ts @kneeraazon404
/next.config.ts @kneeraazon404
/.github/workflows/ @kneeraazon404
/.github/CODEOWNERS @kneeraazon404
```

`.github/pull_request_template.md`

```markdown
## What and why

## How it was tested

## Screenshots

Mobile and desktop, light and dark. Remove this section for changes with no UI.

## Risk and rollback

## Rule IDs touched

## ADR

Link the ADR if this is an architectural change or deviates from a MUST rule.
```

`lefthook.yml`

```yaml
pre-commit:
  parallel: true
  commands:
    eslint:
      glob: '*.{js,mjs,ts,tsx}'
      run: pnpm exec eslint --max-warnings 0 --no-warn-ignored {staged_files}
    prettier:
      glob: '*.{js,mjs,ts,tsx,json,css,md,yml,yaml}'
      run: pnpm exec prettier --check {staged_files}
    gitleaks:
      run: gitleaks git --staged --redact --no-banner .

commit-msg:
  commands:
    commitlint:
      run: pnpm exec commitlint --edit {1}

pre-push:
  commands:
    author:
      run: test "$(git config user.name)" = "kneeraazon404"
```

`commitlint.config.mjs`

```js
const config = { extends: ['@commitlint/config-conventional'] };

export default config;
```

`.editorconfig`

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
trim_trailing_whitespace = false
```

`.vscode/settings.json`

```json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" },
  "tailwindCSS.classFunctions": ["cn", "cva"]
}
```

`renovate.json`

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:best-practices", ":pinAllExceptPeerDependencies", ":semanticCommits"],
  "timezone": "Asia/Kathmandu",
  "schedule": ["before 9am on weekdays"],
  "minimumReleaseAge": "1 day",
  "vulnerabilityAlerts": { "schedule": ["at any time"], "labels": ["security"] },
  "packageRules": [
    {
      "groupName": "next and react",
      "matchPackageNames": [
        "next",
        "react",
        "react-dom",
        "eslint-config-next",
        "@next/**",
        "@types/react",
        "@types/react-dom"
      ]
    },
    { "groupName": "supabase", "matchPackageNames": ["@supabase/**", "supabase"] },
    { "groupName": "prisma", "matchPackageNames": ["prisma", "@prisma/**"] },
    {
      "groupName": "tailwind",
      "matchPackageNames": ["tailwindcss", "@tailwindcss/**", "prettier-plugin-tailwindcss"]
    },
    { "matchUpdateTypes": ["patch"], "automerge": true },
    { "matchDepTypes": ["devDependencies"], "automerge": true }
  ]
}
```

`.dependency-cruiser.mjs`

```js
/** @type {import('dependency-cruiser').IConfiguration} */
const config = {
  forbidden: [
    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
    {
      name: 'lib-is-a-leaf',
      comment: 'ARCH-02: lib imports nothing from features or app.',
      severity: 'error',
      from: { path: '^src/lib/' },
      to: { path: '^src/(features|app)/' },
    },
    {
      name: 'components-below-features',
      comment: 'ARCH-02: components import lib, never features or app.',
      severity: 'error',
      from: { path: '^src/components/' },
      to: { path: '^src/(features|app)/' },
    },
    {
      name: 'features-below-app',
      comment: 'ARCH-02: features never import routes.',
      severity: 'error',
      from: { path: '^src/features/' },
      to: { path: '^src/app/' },
    },
    {
      name: 'features-are-slices',
      comment:
        'ARCH-03: promote shared code to components/ or lib/ instead of importing a sibling feature.',
      severity: 'error',
      from: { path: '^src/features/([^/]+)/' },
      to: { path: '^src/features/([^/]+)/', pathNot: '^src/features/$1/' },
    },
  ],
  options: {
    tsConfig: { fileName: 'tsconfig.json' },
    doNotFollow: { path: 'node_modules' },
    exclude: { path: '^src/generated/' },
  },
};

export default config;
```

`knip.jsonc`

```text
{
  "$schema": "https://unpkg.com/knip@6/schema.json",
  "entry": ["tests/**/*.spec.ts"],
  "ignoreExportsUsedInFile": true,
  // Reference modules and tools that have no consumer until the first feature needs them.
  // Delete each line when its consumer exists, and delete the file when the project does not need it.
  "ignore": [
    "src/features/projects/queries.ts",
    "src/lib/db/client.ts",
    "src/lib/supabase/admin.ts",
    "src/lib/supabase/database.types.ts", // generated by `just types`, never edited
    "src/lib/supabase/client.ts",
    "tests/setup/server-only.ts",
  ],
  "ignoreDependencies": ["@prisma/adapter-pg", "@prisma/client", "@next/playwright", "lefthook"],
}
```

`osv-scanner.toml`

```text
# Advisories we accept, each with an expiry (GOV-04). Remove the entry when a patched version exists.
# None are accepted today: the braces advisory GHSA-vfj7-8cjw-p6xm was withdrawn on 2026-10-23.
# Example entry:
# [[IgnoredVulns]]
# id = "GHSA-xxxx-xxxx-xxxx"
# ignoreUntil = 2026-12-31
# reason = "why the advisory does not apply (A.13)."
```

`CLAUDE.md`

```markdown
@AGENTS.md
```

#### Container

`Dockerfile`

```dockerfile
# syntax=docker/dockerfile:1
# Self-hosted container (CI-08). Requires `output: 'standalone'` in next.config.ts.
FROM node:24-slim@sha256:a5f4366e834695d5f363b920c104953a535d3a9864d1bdf74566a0ebe01daee5 AS base
ENV NEXT_TELEMETRY_DISABLED=1
RUN corepack enable
WORKDIR /app

FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY prisma ./prisma
COPY prisma.config.ts ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store pnpm install --frozen-lockfile --ignore-scripts

FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Public values are inlined at build time. Pass them as build args; never pass secrets.
ARG NEXT_PUBLIC_SITE_URL
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
ENV BUILD_STANDALONE=1 \
    NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL \
    NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL \
    NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=$NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
# Build-time placeholders satisfy env validation. They exist only in this stage; the runtime image
# receives real values from the platform at run time.
RUN DIRECT_URL=postgresql://build:build@localhost:5432/build pnpm exec prisma generate
RUN DATABASE_URL=postgresql://build:build@localhost:5432/build \
    DIRECT_URL=postgresql://build:build@localhost:5432/build \
    SUPABASE_SECRET_KEY=sb_secret_build_placeholder \
    REDIS_URL=redis://localhost:6379 \
    pnpm build

FROM node:24-slim@sha256:a5f4366e834695d5f363b920c104953a535d3a9864d1bdf74566a0ebe01daee5 AS runtime
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    HOSTNAME=0.0.0.0 \
    PORT=3000
WORKDIR /app
RUN groupadd --system --gid 1001 app && useradd --system --uid 1001 --gid app app
COPY --from=build --chown=app:app /app/.next/standalone ./
COPY --from=build --chown=app:app /app/.next/static ./.next/static
COPY --from=build --chown=app:app /app/public ./public
USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/api/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
# Next.js exits at once on SIGTERM (exit code 143) and does not drain requests. Drain at the load balancer first (CI-08).
CMD ["node", "server.js"]
```

`.dockerignore`

```text
.git
.next
node_modules
.env*
!.env.example
playwright-report
test-results
coverage
docs
```

#### Database

`supabase/migrations/20260101000000_projects_and_audit_log.sql`

```sql
-- Starter schema for the reference app (A.5, A.6). Forward-only: add new migrations, never edit this one.

-- Projects: owner-only rows (SB-01, SEC-03).
create table public.projects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  name text not null check (char_length(name) between 1 and 120),
  created_at timestamptz not null default now()
);

alter table public.projects enable row level security;

create policy projects_select_own on public.projects
  for select to authenticated
  using ((select auth.uid()) = owner_id);

create policy projects_insert_own on public.projects
  for insert to authenticated
  with check ((select auth.uid()) = owner_id);

create policy projects_update_own on public.projects
  for update to authenticated
  using ((select auth.uid()) = owner_id)
  with check ((select auth.uid()) = owner_id);

create policy projects_delete_own on public.projects
  for delete to authenticated
  using ((select auth.uid()) = owner_id);

-- Since 2026-10-30 Supabase no longer exposes new public tables to the Data API automatically
-- (projects created from 2026-05-30 already behave this way): grant each role explicitly.
grant select, insert, update, delete on public.projects to authenticated;
grant select, insert, update, delete on public.projects to service_role;

create index projects_owner_id_idx on public.projects (owner_id);

-- Audit log: append-only, written through a function, readable by admins only (OBS-07).
create table public.audit_log (
  id bigint generated always as identity primary key,
  actor_id uuid references auth.users (id) on delete set null,
  action text not null check (char_length(action) between 1 and 80),
  detail jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.audit_log enable row level security;

-- Read access only; writes go through record_audit_event below.
grant select on public.audit_log to authenticated;
grant select, insert on public.audit_log to service_role;

-- The role comes from app_metadata, which users cannot edit (SB-07).
create policy audit_log_select_admin on public.audit_log
  for select to authenticated
  using (((select auth.jwt()) -> 'app_metadata' ->> 'role') = 'admin');

create index audit_log_actor_id_idx on public.audit_log (actor_id);

revoke insert, update, delete, truncate on public.audit_log from anon, authenticated;

create or replace function public.record_audit_event(p_action text, p_detail jsonb default '{}'::jsonb)
returns void
language sql
security definer
set search_path = ''
as $$
  insert into public.audit_log (actor_id, action, detail)
  values ((select auth.uid()), p_action, p_detail);
$$;

revoke all on function public.record_audit_event(text, jsonb) from public, anon;
grant execute on function public.record_audit_event(text, jsonb) to authenticated;
```

`supabase/tests/projects_and_audit_log.test.sql`

```sql
-- One allowed and one denied case per policy (SB-10, TEST-06). Run: supabase test db
begin;
select plan(15);

insert into auth.users (id, instance_id, aud, role, email)
values
  ('00000000-0000-0000-0000-00000000000a', '00000000-0000-0000-0000-000000000000', 'authenticated', 'authenticated', 'a@example.test'),
  ('00000000-0000-0000-0000-00000000000b', '00000000-0000-0000-0000-000000000000', 'authenticated', 'authenticated', 'b@example.test');

insert into public.projects (id, owner_id, name)
values
  ('10000000-0000-0000-0000-00000000000a', '00000000-0000-0000-0000-00000000000a', 'A project'),
  ('10000000-0000-0000-0000-00000000000b', '00000000-0000-0000-0000-00000000000b', 'B project');

-- Every table in the exposed schema has RLS enabled.
select is(
  (select count(*)::int from pg_class c join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public' and c.relkind = 'r' and not c.relrowsecurity),
  0,
  'every table in public has row level security enabled'
);

-- anon
set local role anon;
-- anon has no grant on projects, so the read is refused outright (an older project with default grants would return 0 rows).
select throws_ok(
  $$select count(*) from public.projects$$,
  '42501', null, 'anon cannot read projects'
);

-- user A
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-00000000000a","role":"authenticated"}', true);

select is((select count(*)::int from public.projects), 1, 'A sees exactly one project');
select is((select name from public.projects), 'A project', 'A sees only their own project');
select is((select count(*)::int from public.projects where id = '10000000-0000-0000-0000-00000000000b'), 0, 'A cannot read the B project by id');

select throws_ok(
  $$insert into public.projects (owner_id, name) values ('00000000-0000-0000-0000-00000000000b', 'spoofed')$$,
  '42501', null, 'A cannot insert a project owned by B'
);

update public.projects set name = 'hijacked' where id = '10000000-0000-0000-0000-00000000000b';
delete from public.projects where id = '10000000-0000-0000-0000-00000000000b';

select lives_ok(
  $$insert into public.projects (name) values ('A second')$$,
  'A can insert a project; owner_id defaults to auth.uid()'
);
update public.projects set name = 'A renamed' where id = '10000000-0000-0000-0000-00000000000a';
select is((select name from public.projects where id = '10000000-0000-0000-0000-00000000000a'), 'A renamed', 'A can update their own project');
select throws_ok(
  $$update public.projects set owner_id = '00000000-0000-0000-0000-00000000000b' where id = '10000000-0000-0000-0000-00000000000a'$$,
  '42501', null, 'A cannot hand a project to another owner'
);
delete from public.projects where name = 'A second';
select is((select count(*)::int from public.projects), 1, 'A can delete their own project');

-- audit log: not an admin
select is((select count(*)::int from public.audit_log), 0, 'a non-admin sees no audit rows');
select throws_ok(
  $$insert into public.audit_log (action) values ('forged')$$,
  '42501', null, 'authenticated users cannot insert into the audit log directly'
);
select lives_ok($$select public.record_audit_event('project.rename', '{"id":"x"}')$$, 'the audit function is callable by authenticated users');

-- user B only: B's project is untouched by A's attempts
reset role;
select is((select name from public.projects where id = '10000000-0000-0000-0000-00000000000b'), 'B project', 'B project survived A''s update and delete attempts');

-- admin: role from app_metadata
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-00000000000b","role":"authenticated","app_metadata":{"role":"admin"}}', true);
select is((select count(*)::int from public.audit_log where action = 'project.rename'), 1, 'an admin reads the audit event A wrote');

select * from finish();
rollback;
```

