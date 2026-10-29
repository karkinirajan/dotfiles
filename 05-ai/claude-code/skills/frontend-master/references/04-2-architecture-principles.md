## 2. Architecture principles

- ARCH-01 (MUST): Server-first. Fetch on the server, render on the server, hydrate only interactive islands.
- ARCH-02 (MUST): Dependencies point inward: `app` (routes) imports `features`, `features` import `components` and `lib`, `lib` imports nothing from `features` or `app`. Enforce with ESLint boundaries or `dependency-cruiser` in CI.
- ARCH-03 (MUST): Features are vertical slices (UI, actions, queries, schemas, tests together). Shared code is promoted to `components/` or `lib/` only after a second real consumer.
- ARCH-04 (MUST): One way to do each thing. One data-fetching pattern per rendering context, one form pattern, one toast pattern, one date library, one icon set.
- ARCH-05 (SHOULD): Prefer boring primitives (HTML, CSS, URL, forms) over libraries. Add a library only when the platform cannot do the job at acceptable cost.
- ARCH-06 (SHOULD): Design for deletion. A feature folder should be removable with its route and one line in navigation.
- ARCH-07 (MUST): Pure domain logic (pricing, permissions, formatting) lives in framework-free TypeScript under `lib/` or `features/*/domain` so it is unit-testable without React.

### 2.1 Request flow

```text
Browser
  | HTML stream + RSC payload
  v
proxy.ts            session refresh, coarse redirects, security headers   (NOT an auth boundary)
  v
App Router (Server Components, static shell + dynamic holes)
  |                                        |
  | reads                                  | writes
  v                                        v
DAL (server-only)                    Server Actions / Route Handlers
  verifySession, authorize, DTO            zod parse -> verifySession -> authorize -> mutate -> updateTag
  |                                        |
  +----------------> Supabase (RLS) / Prisma (trusted server role) <---+
```

### 2.2 Where logic lives

| Concern | Home | Why |
|---|---|---|
| Read data for a page | Server Component calling a DAL function | No client waterfall, no API surface |
| Mutate data from your own UI | Server Action | Typed, progressive enhancement, colocated |
| Webhooks, third-party callbacks, public API, file streaming | Route Handler | Needs raw `Request`, custom status and headers |
| Live updates, optimistic lists, infinite scroll, polling | TanStack Query in a Client Component, seeded from the server | Cache, retries, dedupe on the client |
| Invariants that must hold regardless of client | Postgres (constraints, RLS, triggers, functions) | The database is the last line of defense |
| Long-running or scheduled work | Supabase Edge Function or a queue worker | Not in a request path |
| Pure business rules | `lib/` TypeScript | Testable, reusable on client and server |

### 2.3 Rendering model decision table

| Page type | Model | Notes |
|---|---|---|
| Marketing, docs, blog | Static shell, `'use cache'` for content, `ensureStatic = 'navigation'` | Guarantees no accidental request-time work (Next 16.4) |
| Authenticated dashboard | Static shell + `Suspense` holes for per-user data | Instant navigation with Partial Prefetching |
| Highly interactive tool (editor, canvas) | Server shell + one client island, TanStack Query inside | Keep the island's dependency graph isolated and lazy |
| Real-time feed | Server-rendered first page, client subscription (Supabase Realtime) after hydration | Fall back to polling on subscription failure |

---
