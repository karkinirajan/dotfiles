## 6. Next.js App Router standards

### 6.1 Model and configuration

- NEXT-01 (MUST): New apps enable `cacheComponents: true` and `partialPrefetching: true` (`create-next-app` does this by default from 16.4). Existing apps migrate route group by route group using the Cache Components adoption Skill, with E2E coverage first.
- NEXT-02 (MUST): Request APIs are async: `await params`, `await searchParams`, `await cookies()`, `await headers()`. Use the generated route prop helper types, not hand-written ones.
- NEXT-03 (MUST): Every route segment that fetches data has either a `loading.tsx` or an inline `Suspense` boundary, an `error.tsx` (client component with `reset`), and the app has `not-found.tsx` and `global-error.tsx`.
- NEXT-04 (MUST): With Cache Components, anything that reads request data or is non-deterministic (`cookies()`, `headers()`, uncached `fetch`, database calls without `'use cache'`, `Date.now()`, `Math.random()`) renders inside `Suspense`. The build is the enforcement; never silence it.
- NEXT-17 (MUST): `next.config.ts` is typed, sets `poweredByHeader: false`, `reactCompiler: true`, `typedRoutes: true`, strict `images.remotePatterns` (never wildcard hostnames), and security headers. `typescript.ignoreBuildErrors` and any lint-skipping flag are forbidden.
- NEXT-18 (MUST): All environment access goes through `lib/env/public.ts` and `lib/env/server.ts` (validated, the server file guarded by `server-only`). `NEXT_PUBLIC_*` values are inlined at build time and visible to everyone.
- NEXT-19 (SHOULD): `instrumentation.ts` registers OpenTelemetry or Sentry and exports `onRequestError` so server render errors are reported with route context.

### 6.2 Caching

- NEXT-05 (MUST): Caching is explicit. Use `'use cache'` with `cacheLife(...)` and `cacheTag(...)` at the smallest component or function that is safe to cache. Fetches are not cached by default.
- NEXT-05a (MUST): Never cache user-scoped, tenant-scoped, or permission-dependent output unless the cache key contains the user, tenant, or role (pass it as an argument). Arguments become part of the key. Request APIs cannot be read inside a cached scope; read them outside and pass only the safe value in. Two variants exist for special cases. `'use cache: remote'` stores entries in a platform cache handler (Redis or KV) at the cost of a network round trip; it is for serverless hosts, where default in-memory entries do not survive between requests. `'use cache: private'` may read request data inside the cached scope and exists for compliance cases where you cannot pass runtime values as arguments; use it only with a written reason. Always set `cacheLife` explicitly: without it the `default` profile applies (5 minutes stale, 15 minutes revalidate, never expires by time).
- NEXT-06 (MUST): Invalidation rules:
  - Inside a Server Action, after a write the user must see immediately: `updateTag('tag')` (read your own writes).
  - Background freshness where stale-while-revalidate is acceptable: `revalidateTag('tag', 'max')` (the second argument is required in Next 16).
  - Refresh uncached data in place: `refresh()`.
  - `revalidatePath` only when no tag exists. Tag everything you cache.
- NEXT-07 (SHOULD): Routes intended to be fully static export `ensureStatic = 'navigation'` (or on the layout) so a stray dynamic component fails the build. Use `await navigation()` or `await prefetch()` inside expensive cached children so they are excluded from prefetch and load only on real navigation.
- NEXT-08 (MUST): `Suspense` fallbacks are skeletons with the same dimensions as the final content. No layout shift on resolve. Boundaries wrap the slowest independent region, not the whole page.
- NEXT-09 (MUST): Fetch in parallel by default (`Promise.all`, or sibling components each with their own `Suspense`). Wrap DAL reads in React `cache()` so repeated calls in one render dedupe. A sequential `await` chain needs a comment explaining the dependency.

### 6.3 Mutations, handlers, and the proxy

- NEXT-10 (MUST): Mutations use Server Actions with the template in Appendix A.6. Rules in section 9 (SEC-01 to SEC-06) apply to every action.
- NEXT-11 (MUST): Route Handlers are for webhooks, third-party callbacks, public APIs, and streaming. Export named methods, validate body and params, set explicit CORS only when needed, verify webhook signatures on the raw body before parsing, and return typed JSON errors with correct status codes.
- NEXT-12 (MUST): `proxy.ts` (renamed from `middleware.ts`, Node.js runtime) refreshes the Supabase session, sets request-scoped headers, and does coarse redirects. It uses a narrow `matcher` excluding `_next/static`, `_next/image`, assets, and `api/webhooks`. No database queries beyond session refresh, no heavy computation, no authorization decisions that are not repeated in the DAL.

### 6.4 UI infrastructure

- NEXT-13 (MUST): Metadata via the Metadata API: `metadata` or `generateMetadata` per route, `viewport` export, canonical URLs, `opengraph-image`, `sitemap.ts`, `robots.ts`. JSON-LD is rendered in a `<script type="application/ld+json">` with `<` escaped as `\u003c`.
- NEXT-14 (MUST): `next/image` for all raster images with explicit `width`/`height` or `fill` plus `sizes`, `priority` only for the LCP image, AVIF and WebP enabled. `next/font` for fonts with `display: 'swap'` and subset selection. `next/script` with `strategy` for third parties, loaded after interaction when possible.
- NEXT-15 (MUST): Internal navigation uses `<Link>` (typed routes on). Server-side redirects use `redirect()`, missing resources use `notFound()`. Never `window.location` for internal navigation.
- NEXT-16 (SHOULD): Use `catchError` (Next 16.3) for custom error boundaries that must not intercept `notFound` or `redirect`.
- NEXT-20 (SHOULD): Assert instant navigations in E2E with `instant(page, callback)` from `@next/playwright` on every primary navigation route. The API is experimental; the testing API is on in `next dev` and off in production builds unless `experimental.exposeTestingApiInProductionBuild` is set (TEST-05).
- NEXT-22 (SHOULD): Shareable modals use parallel plus intercepting routes with a `default.tsx` so a hard refresh renders the full page.
- NEXT-25 (MUST): `next/dynamic` with `ssr: false` is allowed only inside Client Components. Lazy-load heavy client-only modules (charts, editors, maps) behind a user-intent trigger or `IntersectionObserver`.
- NEXT-26 (SHOULD): Use `after()` for post-response work (analytics, audit logs, cache warming) so it never delays the response.
- NEXT-21 (SHOULD): Deployment: Vercel (zero-config, PPR with Cache Components), or `output: 'standalone'` in Docker for AWS ECS or any container host. The stable Adapter API (16.2) is the integration point for other platforms; use only an adapter that passes the Next.js adapter test suite (a verified adapter). Record the choice and its cost model in an ADR.

---

