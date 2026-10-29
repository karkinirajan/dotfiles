---
name: frontend-master
description: Frontend standards for Next.js App Router, React, TypeScript, Tailwind v4, shadcn/ui, Supabase and Prisma, covering security, performance, accessibility, testing and CI. Use when building, reviewing or auditing frontend code, or when a rule ID such as SEC-01 is cited.
---

# Frontend Master Standards (router)

The files under `references/` are the source of truth in this repository. They were originally generated from a `FRONTEND-MASTER.md` source and a build script that are not vendored here, so edit the reference files directly. `references/_manifest.json` records the hashes of the generated state and will no longer match after an edit.

Rule language: MUST is a merge blocker, SHOULD needs a justification in the PR, MAY is taste.
Cite rule IDs (for example `SEC-01`) in commits, PRs and review comments.

## 0. The rules that matter most

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

---

## How to load the rest

Read only the files the task needs. Every file below is under `references/`.
Appendix A holds the exact files that passed typecheck, lint, build and browser tests: a path in code font,
then a fenced block. Copy from those blocks (the `A.*` files below) or from the matching file already in the repo; never retype from memory.
Blocks labeled "(mode B)" replace the mode A file of the same path (static-shell CSP variant, SEC-08).

| Task | Read |
| --- | --- |
| Start a project, pin or upgrade versions | `03-1-baseline-and-version-policy.md`, `04-2-architecture-principles.md`, `05-3-project-structure.md`, `20-18-upgrade-playbooks.md`, `27-a-1-tsconfig-json.md`, `28-a-2-next-config-ts.md`, `39-a-13-pnpm-workspace-yaml-pnpm-12.md`, `44-a-18-repository-files.md` |
| New page or route | `04-2-architecture-principles.md`, `08-6-next-js-app-router-standards.md`, `12-10-accessibility-wcag-2-2-aa-minimum.md`, `13-11-performance.md`, `42-a-16-app-shell-providers-and-reference-routes.md`, `22-20-definition-of-done-checklists.md` |
| New feature end to end (action, form, query) | `06-4-typescript-standards.md`, `07-5-react-standards.md`, `09-7-data-layer-supabase-prisma-and-the-dal.md`, `11-9-security.md`, `29-a-3-validated-environment-lib-env-public-ts-and.md`, `31-a-5-session-and-dal.md`, `32-a-6-server-action-template.md` |
| Supabase, RLS, migrations, storage | `09-7-data-layer-supabase-prisma-and-the-dal.md`, `11-9-security.md`, `14-12-testing.md`, `30-a-4-supabase-clients-and-session-proxy.md` |
| Prisma | `09-7-data-layer-supabase-prisma-and-the-dal.md`, `35-a-9-prisma-7-only-when-prisma-01-selects-option.md` |
| Styling, tokens, shadcn/ui components | `10-8-styling-design-system-and-ui.md`, `12-10-accessibility-wcag-2-2-aa-minimum.md`, `33-a-7-globals-css-tailwind-v4-tokens-shadcn-compat.md`, `34-a-8-components-json-invariants.md` |
| Security review, headers, CSP, secrets | `11-9-security.md`, `18-16-ci-cd-and-deployment.md`, `36-a-10-content-security-policy-in-proxy-ts.md`, `37-a-11-github-actions-github-workflows-ci-yml.md` |
| Performance work | `13-11-performance.md`, `08-6-next-js-app-router-standards.md`, `28-a-2-next-config-ts.md` |
| Tests, lint, CI | `14-12-testing.md`, `17-15-tooling-and-developer-experience.md`, `18-16-ci-cd-and-deployment.md`, `37-a-11-github-actions-github-workflows-ci-yml.md`, `40-a-14-eslint-config-mjs-eslint-10-flat-config.md`, `43-a-17-tests.md` |
| Logging, errors, observability | `15-13-observability-and-error-handling.md`, `41-a-15-logger-and-rate-limiter.md` |
| i18n and SEO | `16-14-cross-cutting-concerns.md` |
| Review, PR, Definition of Done | `19-17-git-review-and-delivery.md`, `21-19-governance.md`, `22-20-definition-of-done-checklists.md`, `23-21-anti-pattern-catalog-reject-in-review.md` |
| Repo files, tooling, AI assistant rules | `17-15-tooling-and-developer-experience.md`, `38-a-12-agents-md-for-ai-coding-assistants.md`, `40-a-14-eslint-config-mjs-eslint-10-flat-config.md`, `44-a-18-repository-files.md` |
| Sign-in, sign-out, session cookies | `11-9-security.md`, `30-a-4-supabase-clients-and-session-proxy.md`, `46-a-20-authentication-flow.md` |
| Operations: health, errors, ADRs, runbooks, Docker, hooks, Renovate | `15-13-observability-and-error-handling.md`, `18-16-ci-cd-and-deployment.md`, `45-a-19-operational-files.md` |
| Auditing a project against these rules | `47-a-21-audit-and-agent-kit.md`, `22-20-definition-of-done-checklists.md` |

## Rule index

Each rule ID is defined in exactly one file.

- `03-1-baseline-and-version-policy.md`: VER-01 VER-02 VER-03 VER-04 VER-05 VER-06
- `04-2-architecture-principles.md`: ARCH-01 ARCH-02 ARCH-03 ARCH-04 ARCH-05 ARCH-06 ARCH-07
- `05-3-project-structure.md`: STR-01 STR-02 STR-03 STR-04 STR-06 STR-07 STR-08 STR-09
- `06-4-typescript-standards.md`: TS-01 TS-02 TS-04 TS-05 TS-06 TS-07 TS-08 TS-09 TS-10 TS-11 TS-12 TS-13
- `07-5-react-standards.md`: REACT-01 REACT-02 REACT-03 REACT-04 REACT-05 REACT-07 REACT-08 REACT-09 REACT-10 REACT-11 REACT-12 REACT-13 REACT-14 REACT-15 REACT-16 REACT-17 REACT-18 REACT-19 REACT-20 REACT-21 REACT-22 REACT-23 REACT-24 RQ-01 RQ-02 RQ-03 RQ-04 RQ-05 RQ-06 RQ-07 RQ-08
- `08-6-next-js-app-router-standards.md`: NEXT-01 NEXT-02 NEXT-03 NEXT-04 NEXT-05 NEXT-05a NEXT-06 NEXT-07 NEXT-08 NEXT-09 NEXT-10 NEXT-11 NEXT-12 NEXT-13 NEXT-14 NEXT-15 NEXT-16 NEXT-17 NEXT-18 NEXT-19 NEXT-20 NEXT-21 NEXT-22 NEXT-25 NEXT-26
- `09-7-data-layer-supabase-prisma-and-the-dal.md`: DAL-01 DAL-02 DAL-03 DAL-04 DAL-05 DAL-06 PRISMA-01 PRISMA-02 PRISMA-03 PRISMA-04 PRISMA-05 PRISMA-06 PRISMA-07 PRISMA-08 PRISMA-09 SB-01 SB-02 SB-03 SB-04 SB-05 SB-06 SB-07 SB-08 SB-09 SB-10 SB-11 SB-12 SB-13
- `10-8-styling-design-system-and-ui.md`: CODE-01 CODE-02 CODE-03 STYLE-01 STYLE-02 STYLE-03 STYLE-04 STYLE-06 STYLE-07 STYLE-08 STYLE-09 STYLE-10 STYLE-12 STYLE-13 UI-01 UI-02 UI-03 UI-04 UI-05 UI-06 UI-07 UI-08 UI-09 UI-10 UI-11 UI-12 UI-13 UI-14
- `11-9-security.md`: SEC-01 SEC-02 SEC-03 SEC-04 SEC-05 SEC-06 SEC-07 SEC-08 SEC-09 SEC-10 SEC-11 SEC-12 SEC-13 SEC-14 SEC-15 SEC-16 SEC-17 SEC-18 SEC-19 SEC-20 SEC-21 SEC-22 SEC-23 SEC-24 SEC-25
- `12-10-accessibility-wcag-2-2-aa-minimum.md`: A11Y-01 A11Y-02 A11Y-03 A11Y-04 A11Y-05 A11Y-06 A11Y-07 A11Y-08 A11Y-09 A11Y-10 A11Y-11 A11Y-12 A11Y-13 A11Y-14
- `13-11-performance.md`: PERF-01 PERF-02 PERF-03 PERF-04 PERF-05 PERF-06 PERF-07 PERF-08 PERF-09 PERF-10 PERF-11 PERF-12 PERF-13 PERF-14 PERF-15 PERF-16
- `14-12-testing.md`: TEST-01 TEST-02 TEST-03 TEST-04 TEST-05 TEST-06 TEST-07 TEST-08 TEST-09 TEST-10 TEST-11 TEST-12 TEST-13 TEST-14
- `15-13-observability-and-error-handling.md`: OBS-01 OBS-02 OBS-03 OBS-04 OBS-05 OBS-06 OBS-07 OBS-08 OBS-09 OBS-10 OBS-11
- `16-14-cross-cutting-concerns.md`: I18N-01 I18N-02 I18N-03 I18N-04 SEO-01 SEO-02
- `17-15-tooling-and-developer-experience.md`: TOOL-01 TOOL-02 TOOL-03 TOOL-04 TOOL-05 TOOL-06 TOOL-07 TOOL-08 TOOL-09 TOOL-10
- `18-16-ci-cd-and-deployment.md`: CI-01 CI-02 CI-03 CI-04 CI-05 CI-06 CI-08 CI-09 CI-10
- `19-17-git-review-and-delivery.md`: DEL-01 DEL-02 DEL-03 GIT-01 GIT-02 GIT-03 GIT-04
- `21-19-governance.md`: GOV-01 GOV-02 GOV-03 GOV-04 GOV-05

## Templates

Appendix A defines 89 files (mode A, dynamic CSP nonce) and 5 mode B replacements (static shell).

## Verify

- `pnpm check` must pass before a task is called done.
- `pnpm test:e2e` runs the browser tests against a production build.
- `python3 audit/audit.py run --profile ci` must show no FAIL (see `audit/README.md`). `/frontend-audit` runs the full audit. The `audit/` kit ships separately and is not in this repository, so this step and the `frontend-audit` skill need it copied into the project first.
