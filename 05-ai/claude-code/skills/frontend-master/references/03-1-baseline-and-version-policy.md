## 1. Baseline and version policy

### 1.1 Verified versions (2026-10-12)

Each version below was read from the npm registry or the project's release notes on 2026-10-12, and the Appendix A templates were built against exactly these versions (type-check, lint, `next build`, `next start`, Chromium). Pin exactly (VER-01).

| Layer | Pin | Notes |
|---|---|---|
| Next.js | 16.4.0 (released 2026-10-06) | 16.3 (2026-08-03) shipped Instant Navigations. Cache Components is the recommended model for every new app and becomes the default in Next.js 17. |
| React | 19.3.0 | 19.2 added `<Activity>`, `useEffectEvent`, `cacheSignal`. 19.3 adds stable View Transitions (with `addTransitionType`), Fragment Refs, `browser()`, Trusted Types support. |
| React Compiler | `babel-plugin-react-compiler` 1.0.0 | Enable with `reactCompiler: true`. |
| Bundler | Turbopack | Default. Webpack only by explicit opt-out for an unsupported plugin. |
| Node.js | 24 (Active LTS) | Node 26 enters LTS on 2026-10-28; move after one green CI run on it. Next 16 requires 20.9 or newer, Prisma 7 requires 20.19 or newer. Pin with `.nvmrc` or `mise`. |
| Package manager | pnpm 12.11.2 | Set in `packageManager`. Settings live in `pnpm-workspace.yaml` (A.13). |
| TypeScript | 6.0.3 | See 1.1.1. Do not install TypeScript 7 as `typescript`. |
| Tailwind CSS | 4.3.3 | CSS-first. `@tailwindcss/turbopack` is what `create-next-app` installs. `@tailwindcss/postcss` is for webpack builds and other toolchains. |
| shadcn/ui | CLI `shadcn` 4.21.4 | Bases: `base` (Base UI, default for new projects), `radix`, `aria`. |
| Supabase | `@supabase/supabase-js` 2.117.3, `@supabase/ssr` 0.12.7 | `getClaims()` for server auth. Publishable and secret keys. The legacy `anon` and `service_role` keys are deprecated at the end of 2026. |
| Prisma | `prisma`, `@prisma/client`, `@prisma/adapter-pg` 7.10.0 | `prisma-client` generator with required `output`, driver adapters mandatory, `prisma.config.ts` at the project root. The npm `latest` tag of the `prisma` CLI points at 8.0.0-rc.22, so always pin 7.10.0 and never run an unpinned `npx prisma`. |
| Zod | 4.6.7 | Zod 4 idioms only: `z.url()`, `z.uuid()`, `z.flattenError(error).fieldErrors`. |
| TanStack | Query 5.104.2, Table 9.3.1, Form 1.33.5, Virtual 3.14.17 | Query: `environmentManager.isServer()` decides server vs browser client. |
| Forms | `react-hook-form` 7.90.0, `@hookform/resolvers` 5.9.1 | Only for forms that need it (REACT-15). |
| Testing | Vitest 5.0.4, `@testing-library/react` 16.3.3, `@testing-library/user-event` 14.6.7, Playwright and `@playwright/test` 1.64.0, `@next/playwright` 16.4.0, MSW 3.0.3, `@axe-core/playwright` 4.13.0 | |
| Lint and format | ESLint 10.12.0, `typescript-eslint` 8.71.1, `eslint-plugin-react-hooks` 7.1.1, `eslint-plugin-jsx-a11y` 6.10.2, Prettier 3.9.10, `prettier-plugin-tailwindcss` 0.8.1 | `eslint-config-next` 16.4.0 already registers react-hooks, jsx-a11y, and the Next plugin. |
| UI libraries | `next-themes` 0.4.6, `lucide-react` 1.55.0, `tw-animate-css` 1.4.0, `sonner` 2.0.8, `shiki` 4.5.0, `motion` 14.1.0, `zustand` 5.0.15, `nuqs` 2.10.2 | |
| Observability | `@sentry/nextjs` 11.7.0 | |

#### 1.1.1 TypeScript 6 and TypeScript 7

TypeScript 7.0 is the native compiler. It ships no JavaScript API, drops `baseUrl` and `node10` module resolution, and `typescript-eslint` 8.71.1 requires TypeScript below 6.1, so ESLint crashes when `typescript` resolves to 7. Two supported setups, both built and linted in a real Next.js 16.4 project:

| Option | `package.json` | Trade-off |
|---|---|---|
| A. TypeScript 6 only (default) | `"typescript": "6.0.3"` | One compiler, every tool works. Type-checking is slower on very large codebases. |
| B. TypeScript 7 for the type-check, 6 for tooling | `"typescript": "npm:@typescript/typescript6@6.0.2"` and `"@typescript/native": "npm:typescript@7.0.2"` | `tsc` runs 7.0.2 and the `tsc6` binary plus the `typescript` module stay on 6, so ESLint and Next keep working. Two compilers to keep in step. |

Neither option uses `baseUrl`; the `@/*` alias is a `paths` entry (A.1). Re-evaluate when `typescript-eslint` supports TypeScript 7.


### 1.2 Version rules

- VER-01 (MUST): Pin exact versions in `package.json` for `next`, `react`, `react-dom`, `typescript`, `tailwindcss`, `@supabase/*`, `prisma`, `@prisma/*`. Let Renovate propose bumps.
- VER-02 (MUST): `engines.node` and `packageManager` fields set. CI uses the same versions as local.
- VER-03 (MUST): One package manager per repo. Default: `pnpm`. Commit the lockfile.
- VER-04 (SHOULD): Stay on the latest Next.js minor within 30 days of release. Skipping a minor is allowed only if a changelog item blocks you; record it in an ADR.
- VER-05 (MUST): Major upgrades (Next, React, Tailwind, Prisma, Supabase SDK) run on a branch with the upgrade playbook in section 18 and a full E2E pass.
- VER-06 (SHOULD): Run `npx next@canary upgrade --agent=latest` (Next 16.4+) to get version-specific migration guidance and codemods, then review the diff by hand.

### 1.3 Security watch (act on this first)

- A Next.js out-of-band security update is announced for 2026-10-14 covering two Critical and one High vulnerability in upstream dependencies. Until it ships: keep production on the latest 16.x patch, make sure CI and deploy can ship a dependency bump in under an hour, and bump the same day it lands.
- The Next.js team announces security updates before they ship (the 2026-10-08 post announced the 2026-10-14 update). Subscribe to `https://nextjs.org/feed.xml` and GitHub security advisories for `vercel/next.js`, `facebook/react`, `supabase/supabase-js`, `prisma/prisma`.
- Historical lessons that shaped rules below: CVE-2025-29927 (middleware authorization bypass, March 2025), CVE-2025-55182 "React2Shell" (unauthenticated RCE in React Server Components, CVSS 10, December 2025), CVE-2025-55183 (Server Function source exposure), CVE-2025-55184 and CVE-2025-67779 (RSC denial of service).

---

