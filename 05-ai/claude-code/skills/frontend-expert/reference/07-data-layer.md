# 7. Data layer: Supabase, Prisma, and the DAL

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

## 7.1 Supabase

- SB-01 (MUST): Row Level Security is enabled on every table in an exposed schema, with explicit policies per operation (`select`, `insert`, `update`, `delete`) scoped `to authenticated` or `to anon` deliberately. A table without RLS is a public table.
- SB-02 (MUST): Only the publishable key (`sb_publishable_...`) reaches the browser. Secret keys (`sb_secret_...`) and legacy `service_role` stay in server-only env and server-only modules. The legacy `anon` and `service_role` keys are deprecated at the end of 2026 and stay valid until you disable them in the dashboard; migrate off them now. Send the new keys on the `apikey` header only, never as a Bearer token.
- SB-03 (MUST): Server code verifies identity with `supabase.auth.getClaims()` or `getUser()`. `getClaims()` verifies the JWT signature locally against the project's cached JWKS when the project uses asymmetric signing keys, and calls the Auth server when it uses a symmetric secret. `getUser()` always calls the Auth server. Never trust `getSession()` on the server; it does not revalidate the token.
- SB-04 (MUST): Three clients, three files. Browser client (`createBrowserClient`, publishable key). Server client (`createServerClient` with the `next/headers` cookie adapter), created per request and never at module scope. Admin client (secret key, `import 'server-only'`, used only by trusted jobs, webhooks, and admin tooling, never to serve user requests).
- SB-05 (MUST): `proxy.ts` refreshes the session through the SSR helper on every matched request and returns the response that carries the refreshed cookies. If you build a new `NextResponse`, copy the cookies over. `setAll` also receives cache headers; set them on every response that carries auth cookies (A.4) so a CDN never caches a session. On Next 15 and earlier the file must be `middleware.ts`; on 16 it must be `proxy.ts` or sessions silently stop refreshing.
- SB-06 (MUST): The client is typed: `createClient<Database>()` with types from `supabase gen types typescript`, regenerated in CI and committed (or verified for drift).
- SB-07 (MUST): Authorization data comes from `app_metadata`, custom claims issued by an access-token hook, or tables. `user_metadata` is user-editable and never used for authorization.
- SB-08 (SHOULD): Auth defaults: OAuth plus email OTP or magic link, email confirmation required, redirect URLs allow-listed per environment, CAPTCHA on sign-up and password reset, TOTP MFA required for admin roles, short JWT expiry with refresh, sign-out invalidates refresh tokens.
- SB-09 (MUST): Schema changes only through `supabase/migrations/*.sql` (created with the CLI, reviewed in PRs, applied by CI). No dashboard edits on production. Local stack via `supabase start` (Docker or Podman). Preview environments use Supabase branches.
- SB-10 (MUST): Run the Supabase advisors (security and performance) in CI or at least weekly, and fix every ERROR-level finding. Policies are tested with pgTAP (`supabase test db`): one test per policy for allowed and denied access.
- SB-11 (MUST): Storage buckets are private by default. Access via short-lived signed URLs. Object paths start with the owner or tenant id and policies match on `(storage.foldername(name))[1]`. Validate MIME type and size server-side before issuing an upload URL.
- SB-12 (SHOULD): Realtime subscriptions live in a client island, filter server-side, unsubscribe on cleanup, handle reconnect, and fall back to polling. Use Broadcast for high-frequency events.
- SB-13 (MUST): Query hygiene: select named columns (no `select('*')` in production paths), always check `error`, use `.maybeSingle()` when zero rows is valid, bound every list with `.range()` or keyset pagination, avoid `count: 'exact'` on large tables (use `estimated` or `planned`), put multi-step atomic work in a Postgres function called via `rpc`.

Policy patterns (copy, then adapt). Wrap `auth.uid()` in a scalar subquery so Postgres evaluates it once per statement, and index every column a policy filters on.

```sql
-- Owner-only rows
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

create index projects_owner_id_idx on public.projects (owner_id);

-- Tenant membership via a security definer helper in a non-exposed schema
create schema if not exists private;
grant usage on schema private to authenticated;

create or replace function private.is_org_member(target_org uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from public.org_members m
    where m.org_id = target_org
      and m.user_id = (select auth.uid())
  );
$$;

revoke all on function private.is_org_member(uuid) from public, anon;
grant execute on function private.is_org_member(uuid) to authenticated;

create policy docs_select_member on public.docs
  for select to authenticated
  using (private.is_org_member(org_id));

-- Role from a trusted claim (app_metadata), never user_metadata
create policy audit_select_admin on public.audit_log
  for select to authenticated
  using (((select auth.jwt()) -> 'app_metadata' ->> 'role') = 'admin');

-- Views must run with the caller's privileges
create view public.project_summaries with (security_invoker = true) as
  select id, name, owner_id from public.projects;
```

## 7.2 Prisma (server-side data access)

- PRISMA-01 (MUST): Choose the data access model per project and record it in an ADR. Never mix two migration tools on one schema.

| Option | Use when | Cost |
|---|---|---|
| A. `supabase-js` + generated types only | CRUD-heavy apps, client-visible realtime, simple relations. RLS enforced on every query. | No ORM ergonomics for complex joins and transactions |
| B. Prisma for server reads and writes, Supabase for auth, storage, realtime | Complex domain logic, reporting, multi-table transactions, large teams that want a schema file | Prisma connects with a privileged role, so RLS does not protect those queries. Authorization is the DAL's job (DAL-01) |
| C. Prisma with a restricted role and per-transaction JWT claims (Client Extension) | Compliance needs RLS as defense in depth while keeping Prisma | Highest complexity. Needs `SET LOCAL` claims handling and thorough pgTAP tests. Adopt only with a written reason |

Default recommendation: A for most client apps, B when the domain logic justifies it. C is exceptional.

- PRISMA-02 (MUST): One migration authority. If Prisma owns the schema, Prisma Migrate manages application tables, and RLS policies and Supabase-specific SQL ship as raw SQL inside Prisma migration files (Prisma does not model policies). Prisma never migrates Supabase-managed schemas (`auth`, `storage`, `realtime`). If Supabase migrations own the schema, Prisma uses `db pull` and read-only introspection.
- PRISMA-03 (MUST): Prisma 7 setup: generator `prisma-client` with a required `output` path (generated in `postinstall` and CI, not committed), driver adapter `@prisma/adapter-pg` passed to `new PrismaClient({ adapter })`, `prisma.config.ts` at the project root declaring schema path, migrations path, seed, and datasource URL. Long-running servers (ECS, VPS) use the session pooler (port 5432) at runtime; serverless uses the transaction pooler (port 6543) with `pgbouncer=true` appended, as the Supabase guide specifies. Migrations use the direct or session URL (`DIRECT_URL`). Prisma 7 does not load `.env` files, so load them in `prisma.config.ts` (A.9). Create a dedicated `prisma` database role instead of connecting as `postgres`. Turn on SSL enforcement in Supabase, connect with `sslmode=verify-full`, and give Node the Supabase CA through `NODE_EXTRA_CA_CERTS` (or the adapter's `ssl.ca`); an untrusted certificate fails with `P1010`, and `rejectUnauthorized: false` is forbidden in production. Node 20.19 or newer. Do not pass `prisma://` Accelerate URLs to a driver adapter.
- PRISMA-04 (MUST): `lib/db/client.ts` begins with `import 'server-only'`, builds one adapter-backed client, and caches it on `globalThis` in development so HMR does not exhaust connections.
- PRISMA-05 (MUST): Configure pool limits explicitly (`max`, `connectionTimeoutMillis`, `idleTimeoutMillis`). The `pg` driver has no connection timeout by default, unlike Prisma 6. Serverless runtimes use a small `max` behind the pooler.
- PRISMA-06 (MUST): Prisma types never reach Client Components. Map to DTOs; convert `Decimal`, `BigInt`, and `Date` to serializable values at the DAL boundary.
- PRISMA-07 (SHOULD): Query discipline: explicit `select`, bounded `take`, cursor pagination for large sets, `$transaction` for multi-write invariants, `@@index` for every filtered or joined column, typed error mapping for `P2002` (unique) and `P2025` (not found).
- PRISMA-08 (SHOULD): Tests run against a real Postgres (local Supabase or Testcontainers), isolated per test by transaction rollback or truncate, with factories for data.
- PRISMA-09 (MAY): Watch Prisma Next (early access) but do not adopt it in client work until stable.

## 7.3 Data access layer (DAL)

- DAL-01 (MUST): All reads and writes go through server-only functions in `features/*/queries.ts` or `lib/dal/`. Components, actions, and handlers never import the Supabase admin client or the Prisma client directly.
- DAL-02 (MUST): Every exported DAL function starts with `const session = await verifySession()` (a React `cache()`d function) and authorizes the specific resource, not just "is logged in".
- DAL-03 (MUST): DAL functions return DTOs containing only fields the caller may see. Field-level authorization happens here.
- DAL-04 (MUST): Lists enforce a server-side maximum page size regardless of what the client asks for.
- DAL-05 (SHOULD): Expected failures return typed results (`not_found`, `forbidden`, `conflict`); the caller maps them to `notFound()`, a forbidden view, or form errors.
- DAL-06 (MUST): Log with a request id. Never log tokens, cookies, passwords, or personal data.
