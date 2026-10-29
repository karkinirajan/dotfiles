## 1. Baseline and version policy

### 1.1 Verified versions (2026-10-29)

Each version below was read from the npm registry or the project's release notes on 2026-10-29. The Appendix A templates were built against the 2026-10-12 pins (type-check, lint, `next build`, `next start`, Chromium). Only Next.js, `eslint-config-next`, `@next/playwright`, React and React DOM moved since then, because 16.4.0 is vulnerable (1.3); `typescript-eslint` 8.72.1 and pnpm 12.16.1 were also run against the A.13 and A.14 templates. Every other row is held at its tested pin, because the `trustPolicyExclude` list in A.13 names exact versions (a bump can make `pnpm install` fail), and the newer registry versions are listed in 1.1.2. Pin exactly (VER-01) and run `pnpm check` after any bump.

| Layer | Pin | Notes |
|---|---|---|
| Next.js | 16.4.3 (released 2026-10-23) | 16.3 (2026-08-03) shipped Instant Navigations. Cache Components is the recommended model for every new app and becomes the default in Next.js 17. |
| React | 19.3.1 | 19.2 added `<Activity>`, `useEffectEvent`, `cacheSignal`. 19.3 adds stable View Transitions (with `addTransitionType`), Fragment Refs, `browser()`, Trusted Types support. |
| React Compiler | `babel-plugin-react-compiler` 1.0.0 | Enable with `reactCompiler: true`. |
| Bundler | Turbopack | Default. Webpack only by explicit opt-out for an unsupported plugin. |
| Node.js | 24 (Maintenance LTS since 2026-10-20, supported to 2028-04-30) | Node 26 "Lithium" became LTS on 2026-10-28 (v26.13.0). Keep 24 until one CI run is green on 26, then move `engines.node` and `.nvmrc` to 26; `nvm install --lts` already resolves to 26. Next 16 requires 20.9 or newer, Prisma 7 requires 20.19 or newer. Pin with `.nvmrc` or `mise`. |
| Package manager | pnpm 12.11.2 | Set in `packageManager`. Settings live in `pnpm-workspace.yaml` (A.13). |
| TypeScript | 6.0.3 | See 1.1.1. Do not install TypeScript 7 as `typescript`. |
| Tailwind CSS | 4.3.3 | CSS-first. `@tailwindcss/turbopack` is what `create-next-app` installs. `@tailwindcss/postcss` is for webpack builds and other toolchains. |
| shadcn/ui | CLI `shadcn` 4.21.4 | Bases: `base` (Base UI, default for new projects), `radix`, `aria`. |
| Supabase | `@supabase/supabase-js` 2.117.3, `@supabase/ssr` 0.12.7 | `getClaims()` for server auth. Publishable and secret keys. The legacy `anon` and `service_role` keys are deprecated at the end of 2026. |
| Prisma | `prisma`, `@prisma/client`, `@prisma/adapter-pg` 7.10.0 | `prisma-client` generator with required `output`, driver adapters mandatory, `prisma.config.ts` at the project root. The npm `latest` tag of the `prisma` CLI points at an 8.0.0 release candidate (rc.28 on 2026-10-27), so always pin 7.10.0 and never run an unpinned `npx prisma`. Prisma 7 keeps bug and security fixes for 18 months after ORM 8 reaches GA. |
| Zod | 4.6.7 | Zod 4 idioms only: `z.url()`, `z.uuid()`, `z.flattenError(error).fieldErrors`. |
| TanStack | Query 5.104.2, Table 9.3.1, Form 1.33.5, Virtual 3.14.17 | Query: `environmentManager.isServer()` decides server vs browser client. |
| Forms | `react-hook-form` 7.90.0, `@hookform/resolvers` 5.9.1 | Only for forms that need it (REACT-15). |
| Testing | Vitest 5.0.4, `@testing-library/react` 16.3.3, `@testing-library/user-event` 14.6.7, Playwright and `@playwright/test` 1.64.0, `@next/playwright` 16.4.3, MSW 3.0.3, `@axe-core/playwright` 4.13.0 | |
| Lint and format | ESLint 10.12.0, `typescript-eslint` 8.71.1, `eslint-plugin-react-hooks` 7.1.1, `eslint-plugin-jsx-a11y` 6.10.2, Prettier 3.9.10, `prettier-plugin-tailwindcss` 0.8.1 | `eslint-config-next` 16.4.3 already registers react-hooks, jsx-a11y, and the Next plugin. |
| UI libraries | `next-themes` 0.4.6, `lucide-react` 1.55.0, `tw-animate-css` 1.4.0, `sonner` 2.0.8, `shiki` 4.5.0, `motion` 14.1.0, `zustand` 5.0.15, `nuqs` 2.10.2 | |
| Observability | `@sentry/nextjs` 11.7.0 | |

#### 1.1.1 TypeScript 6 and TypeScript 7

TypeScript 7.0 is the native compiler. It ships no JavaScript API, drops `baseUrl` and `node10` module resolution, and `typescript-eslint` 8.71.1 requires TypeScript below 6.1, so ESLint crashes when `typescript` resolves to 7. Two supported setups, both built and linted in a real Next.js 16.4 project:

| Option | `package.json` | Trade-off |
|---|---|---|
| A. TypeScript 6 only (default) | `"typescript": "6.0.3"` | One compiler, every tool works. Type-checking is slower on very large codebases. |
| B. TypeScript 7 for the type-check, 6 for tooling | `"typescript": "npm:@typescript/typescript6@6.0.2"` and `"@typescript/native": "npm:typescript@7.0.2"` | `tsc` runs 7.0.2 and the `tsc6` binary plus the `typescript` module stay on 6, so ESLint and Next keep working. Two compilers to keep in step. |

Neither option uses `baseUrl`; the `@/*` alias is a `paths` entry (A.1). Re-evaluate when `typescript-eslint` supports TypeScript 7.

#### 1.1.2 Newer registry versions not adopted (2026-10-29)

| Package | Pin above | Registry | Why held |
|---|---|---|---|
| `pnpm` | 12.11.2 | 12.16.1 | Ran the A.13 and A.18 templates unchanged on both; bump `packageManager` at will. Arch and CachyOS package 12.15.0. |
| `typescript-eslint` | 8.71.1 | 8.72.1 | A.14 runs unchanged on 8.72.1; safe to bump. |
| `shadcn` | 4.21.4 | 4.23.0 | Not rebuilt. |
| `@supabase/supabase-js` | 2.117.3 | 2.118.0 | Not rebuilt. |
| `prisma` family | 7.10.0 | 7.10.1 | A.13 trust-policy findings are scoped to 7.10.0. |
| TanStack | Query 5.104.2, Virtual 3.14.17 | Query 5.105.0, Virtual 3.14.23 | A.13 excludes `@tanstack/*@5.104.2` from the trust policy. |
| `react-hook-form` | 7.90.0 | 7.91.0 | Not rebuilt. `@hookform/resolvers` 6.0.2 is a new major; Zod 4 compatibility was not checked, stay on 5.9.1. |
| Vitest, Playwright, user-event, axe | 5.0.4, 1.64.0, 14.6.7, 4.13.0 | 5.0.5, 1.64.1, 14.6.8, 4.14.0 | Vitest is in the A.13 trust-policy exclusions; the rest were not rebuilt. |
| ESLint | 10.12.0 | 10.13.0 | Not rebuilt. |
| `lucide-react`, `motion`, `zustand` | 1.55.0, 14.1.0, 5.0.15 | 1.63.0, 14.7.1, 5.0.16 | Not rebuilt. |
| `@sentry/nextjs` | 11.7.0 | 11.10.0 | Sentry configuration not re-checked on 11.10. |
| A.18 extras | `geist` 1.7.2, `@commitlint/*` 21.2.3, `dependency-cruiser` 18.6.0, `jsdom` 30.1.2, `knip` 6.41.0, `lefthook` 2.2.1 | 1.8.2, 21.2.4, 18.7.0, 30.1.3, 6.43.0, 2.2.2 | Not rebuilt. `lefthook` 2.2.2 is rejected by the template trust policy. |

An `npm audit` bulk query over the 57 pinned packages on 2026-10-29 returned advisories only for `next` 16.4.0 (fixed in 16.4.1) and `sharp` below 0.35.5 (Next 16.4.3 depends on `sharp` ^0.35.5, so it is clean). Prisma and Supabase GitHub advisory pages could not be read from the research environment.

### 1.2 Version rules

- VER-01 (MUST): Pin exact versions in `package.json` for `next`, `react`, `react-dom`, `typescript`, `tailwindcss`, `@supabase/*`, `prisma`, `@prisma/*`. Let Renovate propose bumps.
- VER-02 (MUST): `engines.node` and `packageManager` fields set. CI uses the same versions as local.
- VER-03 (MUST): One package manager per repo. Default: `pnpm`. Commit the lockfile.
- VER-04 (SHOULD): Stay on the latest Next.js minor within 30 days of release. Skipping a minor is allowed only if a changelog item blocks you; record it in an ADR.
- VER-05 (MUST): Major upgrades (Next, React, Tailwind, Prisma, Supabase SDK) run on a branch with the upgrade playbook in section 18 and a full E2E pass.
- VER-06 (SHOULD): Run `npx next@canary upgrade --agent=latest` (Next 16.4+) to get version-specific migration guidance and codemods, then review the diff by hand.

### 1.3 Security watch (act on this first)

- The 2026-10-14 out-of-band security update shipped in Next.js 16.4.1 (Active LTS) and 15.5.28 (Maintenance LTS): two Critical (a `use cache` remote code execution with no workaround, GHSA-673q-mjm6-r5xr, and CVE-2026-96889 / GHSA-2464-fhr4-w9xw) and one High (GHSA-p3m5-59mp-jv5r). Next.js 16.0.0 through 16.4.0 are affected, so require 16.4.1 or newer (this document pins 16.4.3) and `sharp` 0.35.5 or newer. Keep CI and deploy able to ship a dependency bump in under an hour.
- Next.js now runs a monthly scheduled security release: the next is announced for Tuesday 2026-11-03 and covers seven Medium vulnerabilities (posted 2026-10-27); earlier releases were 2026-07-20, 2026-08-25, 2026-09-22 (out of band, critical) and 2026-09-30. The team announces releases before they ship. Subscribe to `https://nextjs.org/feed.xml` and GitHub security advisories for `vercel/next.js`, `facebook/react`, `supabase/supabase-js`, `prisma/prisma`.
- Historical lessons that shaped rules below: CVE-2025-29927 (middleware authorization bypass, March 2025), CVE-2025-55182 "React2Shell" (unauthenticated RCE in React Server Components, CVSS 10, December 2025), CVE-2025-55183 (Server Function source exposure), CVE-2025-55184 and CVE-2025-67779 (RSC denial of service).

---
