---
name: frontend-expert
description: Use for any frontend work on the Next.js (App Router) + React + TypeScript (strict) + Tailwind CSS v4 + shadcn/ui + Supabase + Prisma + TanStack Query stack — building or reviewing a component, page, Server Action, Route Handler, Supabase/Prisma query, styling, auth/RLS, accessibility, performance, testing, CI/CD, or an upgrade. Trigger on requests to build/fix/review a UI, wire up data access, add auth or authorization, style with Tailwind/shadcn, ship a form, optimize Core Web Vitals or bundle size, write tests, configure CI, or upgrade Next.js/React/Tailwind/Prisma/Supabase. This is the full master standards document — exhaustive, versioned, rule-numbered — not a quick checklist.
---

# Frontend Master Standards

Stack: Next.js (App Router) + React + TypeScript (strict) + Tailwind CSS v4 + shadcn/ui + Supabase + Prisma + TanStack Query

Owner: Nirajan Karki (kneeraazon) | Verified against upstream sources: 2026-10-12 | Review cadence: monthly, plus on every Next.js security release

This is the full, verbatim master standards document, split into this orchestrator file plus one reference file per section/appendix subset so a session only loads the part it needs. **Nothing in the source document was shortened, summarized, or dropped** — every rule ID, table, SQL policy, and code template lives in full in its reference file. Read section 0 below for every task; then open only the reference file(s) the task actually touches.

## How to use this document

1. **Project kickoff**: read `reference/02-architecture.md` through `reference/04-typescript.md`, copy templates from the Appendix A reference files, record deviations as ADRs (`reference/19-governance.md`).
2. **Daily work**: use section 0 below as the pre-commit mental checklist and `reference/20-definition-of-done.md` as the Definition of Done.
3. **PR review**: cite rule IDs (for example `SEC-07`, `NEXT-12`). A review comment with an ID needs no further argument. Rule IDs are stable — never renumber; a deprecated rule gets a strikethrough note and new IDs are appended at the end of its section.
4. **AI-assisted development**: drop `reference/appendix-a11-a15-ci-tooling.md`'s `AGENTS.md` template into the repo root so every agent session inherits these rules.

Rule language follows RFC 2119: **MUST** (merge blocker), **SHOULD** (justify deviation in the PR), **MAY** (taste).

Scope decision: "Prism" in the original brief is treated as **Prisma ORM** (server-side data access in the Supabase stack). If Prism.js (syntax highlighting) was meant, see `reference/08-styling-ui.md` §8.3.

## Reference file index

Read the relevant file(s) before acting — do not rely on memory of this list for the actual rule text.

| # | File | Covers |
|---|---|---|
| 1 | `reference/01-versions-and-watch.md` | Verified version pins (2026-10-12), TypeScript 6 vs 7, version rules (VER-*), active security watch and historical CVEs |
| 2 | `reference/02-architecture.md` | Architecture principles (ARCH-*), request flow diagram, where-logic-lives table, rendering model decision table |
| 3 | `reference/03-structure.md` | Full project folder layout, structure rules (STR-*) |
| 4 | `reference/04-typescript.md` | Strict TypeScript rules (TS-*): schemas, discriminated unions, branded types, Result shapes |
| 5 | `reference/05-react.md` | React rules (REACT-*) + TanStack Query rules (RQ-*): server/client boundary, effects, state ownership, forms, correctness hygiene |
| 6 | `reference/06-nextjs.md` | Next.js App Router rules (NEXT-*): config, caching (`'use cache'`, tags), Server Actions/Route Handlers, `proxy.ts`, UI infra |
| 7 | `reference/07-data-layer.md` | Supabase (SB-*) incl. RLS SQL policy patterns, Prisma (PRISMA-*), Data Access Layer (DAL-*) |
| 8 | `reference/08-styling-ui.md` | Tailwind v4 (STYLE-*), shadcn/ui (UI-*), Prism.js/Shiki syntax highlighting (CODE-*) |
| 9 | `reference/09-security.md` | Threat model table, application-layer security (SEC-01 to SEC-19), browser hardening (SEC-08/09/10/17), secrets/privacy/supply chain (SEC-12, 16, 20-25) |
| 10 | `reference/10-accessibility.md` | WCAG 2.2 AA rules (A11Y-*) |
| 11 | `reference/11-performance.md` | Core Web Vitals budgets and performance rules (PERF-*) |
| 12 | `reference/12-testing.md` | Testing pyramid and rules (TEST-*) |
| 13 | `reference/13-observability.md` | Logging, error reporting, tracing, flags, audit log (OBS-*) |
| 14 | `reference/14-i18n-seo.md` | Internationalization (I18N-*) and SEO (SEO-*) |
| 15 | `reference/15-tooling.md` | Package manager, linting, formatting, git hooks, editor setup, AI-agent rules (TOOL-*) |
| 16 | `reference/16-cicd.md` | CI/CD pipeline, branch protection, migrations, rollback, hosting comparison (CI-*) |
| 17 | `reference/17-git-delivery.md` | Commits, PR size/review order, client handoff pack (GIT-*, DEL-*) |
| 18 | `reference/18-upgrade-playbooks.md` | Step-by-step upgrade playbooks: Next 15→16, Cache Components adoption, Tailwind v3→v4, Prisma 6→7, Supabase keys/auth helpers, shadcn/ui bases |
| 19 | `reference/19-governance.md` | ADRs, production-grade bar, doc-vs-upstream precedence (GOV-*) |
| 20 | `reference/20-definition-of-done.md` | Checklists: component, page/route, feature, PR, production release |
| 21 | `reference/21-anti-patterns.md` | Anti-pattern catalog to reject in review, each mapped to its rule ID |
| 22 | `reference/22-references-changelog.md` | Primary sources, standards references, changelog |
| A1–A6 | `reference/appendix-a1-a6-core.md` | `tsconfig.json`, `next.config.ts`, validated env, Supabase clients + `proxy.ts` session refresh, session/DAL, Server Action template |
| A7–A9 | `reference/appendix-a7-a9-styling-prisma.md` | `globals.css` tokens (with contrast table), `components.json` invariants, Prisma 7 setup |
| A10 | `reference/appendix-a10-csp.md` | Content Security Policy in `proxy.ts` — mode A (dynamic nonce) and mode B (static shell) full implementations |
| A11–A15 | `reference/appendix-a11-a15-ci-tooling.md` | GitHub Actions CI, `AGENTS.md`, `pnpm-workspace.yaml`, ESLint flat config, logger + rate limiter |
| A16–A18 | `reference/appendix-a16-a18-shell-tests-repo.md` | App shell/providers/reference routes, Vitest + Playwright test suite, repository files (`package.json`, `.nvmrc`, `justfile`, etc.) |

---

## 0. The rules that matter most

Keep this list in working memory for every task; it is the pre-commit mental checklist (rule 30 of this file maps it to DEL-03/section 20).

1. Server Components by default. `"use client"` only at the leaf that needs state, effects, or browser APIs. (REACT-01)
2. Every Server Action and Route Handler is a public HTTP endpoint. Authenticate, authorize, and validate input inside each one, every time. (SEC-01)
3. `proxy.ts` is for session refresh and coarse routing. It is never your only authorization check. (SEC-02)
4. Authorization lives in the data access layer (DAL) next to the query, not in the UI and not only in the proxy. (SEC-03)
5. RLS is enabled on every table in an exposed schema, with policies written and tested before the first row of data. (SB-01)
6. Never ship a Supabase secret or `service_role` key to the browser. Only the publishable key is public. (SB-02)
7. On the server, trust `supabase.auth.getClaims()` (or `getUser()`), never `getSession()`. (SB-03)
8. Validate every boundary with Zod: forms, actions, route handlers, env vars, webhooks, third-party responses. (TS-06)
9. `strict` TypeScript with `noUncheckedIndexedAccess`. No `any`. No non-null assertions outside tests. (TS-01)
10. Caching is explicit: `'use cache'` with `cacheLife` and `cacheTag`. Never cache per-user data without the user in the cache key. (NEXT-05)
11. Every async boundary has a `Suspense` fallback that matches the final layout. No layout shift. (NEXT-08)
12. Tailwind v4 CSS-first config. Tokens live in `@theme`. No `tailwind.config.js`, no hex literals in components. (STYLE-01)
13. shadcn/ui components are owned code. Edit them in `components/ui`, but wrap rather than fork when behavior diverges. (UI-02)
14. WCAG 2.2 AA is the floor. Keyboard, focus, contrast, target size, reduced motion. (A11Y-01)
15. Mobile first. Design at 360px, then enhance. Use container queries for component-level responsiveness. (STYLE-08)
16. Core Web Vitals budgets at p75: LCP under 2.5s, INP under 200ms, CLS under 0.1. Budgets are CI gates. (PERF-01)
17. Ship less JavaScript: measure the bundle on every PR, justify every dependency over 10 kB gzipped. (PERF-05)
18. Images through `next/image`, fonts through `next/font`, third-party scripts through `next/script` with a strategy. (PERF-08)
19. No `useEffect` for data fetching or derived state. (REACT-06)
20. State has an owner: URL, server, form, or local. Global client stores are the last resort. (REACT-09)
21. Every user-visible list and view has loading, empty, error, and partial states designed. (UI-09)
22. Secrets only in server env. Validate env at boot. `NEXT_PUBLIC_` is a publication, not configuration. (SEC-12)
23. Security releases of Next.js and React are patched within 24 hours for Critical, 72 hours for High. (SEC-20)
24. Lockfile committed, dependencies pinned, install scripts reviewed, provenance checked. (SEC-22)
25. Every feature ships with tests at the lowest level that proves it, plus one Playwright path for money or auth flows. (TEST-01)
26. Structured logging, error boundaries at route level, tracing from browser to database. (OBS-01)
27. Conventional Commits, small PRs, author identity `kneeraazon404`. (GIT-01)
28. Decisions that cost more than a day to reverse get an ADR. (GOV-01)
29. No tutorial-grade code in client work: typed, validated, error-handled, accessible, tested. (GOV-02)
30. When docs and this file disagree, upstream docs win and this file gets fixed within a week. (GOV-03)
