## 3. Project structure

### 3.1 Single app layout (default)

```text
.
├── AGENTS.md                     # agent instructions, points to FRONTEND-MASTER.md
├── FRONTEND-MASTER.md            # this file
├── docs/adr/                     # architecture decision records
├── prisma/                       # schema.prisma, migrations (only if Prisma is used)
├── prisma.config.ts
├── supabase/                     # config.toml, migrations/, seed.sql, tests/ (pgTAP), functions/
├── public/
├── src/
│   ├── app/                      # routes only: page, layout, loading, error, not-found, route handlers
│   │   ├── (marketing)/
│   │   ├── (app)/
│   │   │   └── dashboard/
│   │   ├── api/                  # route handlers (webhooks, public API) only
│   │   ├── globals.css           # Tailwind v4 entry, tokens
│   │   └── layout.tsx
│   ├── features/
│   │   └── billing/
│   │       ├── components/       # feature UI (server and client)
│   │       ├── actions.ts        # 'use server' mutations
│   │       ├── queries.ts        # server-only reads (DAL functions)
│   │       ├── schemas.ts        # zod schemas shared by form and action
│   │       ├── domain/           # pure logic
│   │       └── *.test.ts(x)      # tests sit beside the code they cover (STR-03, STR-07)
│   ├── components/
│   │   ├── ui/                   # shadcn/ui primitives (owned code)
│   │   └── shared/               # cross-feature composites (PageHeader, DataTable, EmptyState)
│   ├── lib/
│   │   ├── supabase/             # client.ts, server.ts, proxy.ts (session updater)
│   │   ├── db/                   # prisma client singleton (server-only)
│   │   ├── auth/                 # verifySession, requireRole (server-only)
│   │   ├── env/                  # public.ts and server.ts (validated env, server file is server-only)
│   │   ├── logger.ts
│   │   ├── utils.ts              # tiny pure helpers (shadcn init adds cn() here or re-exports it from the cn package)
│   │   └── query/                # TanStack Query client factory, key factories
│   ├── hooks/                    # client hooks only
│   ├── styles/                   # extra CSS layers if needed (rare)
│   └── proxy.ts
├── tests/
│   ├── e2e/                      # Playwright
│   └── setup/
└── .github/workflows/
```

### 3.2 Structure rules

- STR-01 (MUST): `app/` contains routing files only. No business logic, no reusable components. A `page.tsx` composes feature components and exports metadata.
- STR-02 (MUST): Files that touch secrets or the database start with `import 'server-only'`. Files that touch `window` or hooks start with `"use client"`. Nothing is ambiguous.
- STR-03 (MUST): Naming: folders and files `kebab-case` (shadcn/ui generates `button.tsx`, so one convention covers owned and generated code), React components exported as `PascalCase` symbols (`empty-state.tsx` exports `EmptyState`), hooks `use-thing.ts` exporting `useThing`, schemas `thing.schema.ts` or `schemas.ts`, tests `thing.test.ts(x)` beside the code.
- STR-04 (SHOULD): Named exports everywhere except Next.js route files (which require default). Default exports make rename refactors and grep unreliable.
- STR-05 (MUST NOT): No barrel files (`index.ts` re-exports) in `features/` or `components/`. They defeat tree shaking, slow Turbopack, and create import cycles. A single `index.ts` per feature exposing its public surface is allowed only if lint-enforced.
- STR-06 (MUST): Import alias `@/*` to `src/*`. No `../../..` chains deeper than two levels.
- STR-07 (SHOULD): Colocate: a component's test, story, and styles sit beside it. Delete the whole folder to delete the component.
- STR-08 (SHOULD): Use route groups `(group)` for layout boundaries, private folders `_name` for colocated non-route files inside `app/`.
- STR-09 (MAY): Move to a Turborepo monorepo (`apps/web`, `packages/ui`, `packages/config`, `packages/db`) only when a second deployable app or a shared design system package exists. Never at kickoff by default.

---
