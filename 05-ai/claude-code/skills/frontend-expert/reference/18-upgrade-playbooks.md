# 18. Upgrade playbooks

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

## 18.1 Next.js 15 to 16 (and on to 16.4)

1. Branch. Confirm Node 20.9 or newer and TypeScript 5.1 or newer (this file's baseline is Node 24 and TypeScript 6.0.3). Upgrade `next`, `react`, `react-dom` together. Try `npx next@canary upgrade --agent=latest` for version-specific guidance and codemods, and review every change.
2. Rename `middleware.ts` to `proxy.ts` and the exported function to `proxy` (Node.js runtime only; keep `middleware.ts` only if you must stay on the Edge runtime).
3. Make every `params`, `searchParams`, `cookies()`, and `headers()` access async.
4. Replace `next lint` with the ESLint CLI. Replace `images.domains` with `remotePatterns`. Remove `next/legacy/image`.
5. Update `revalidateTag(tag)` calls to `revalidateTag(tag, 'max')` and use `updateTag` for read-your-writes in actions.
6. Turbopack is the default bundler. Custom webpack config must be migrated or explicitly opted out of with a documented reason.
7. Replace `experimental.ppr` and `experimental.dynamicIO` with `cacheComponents`. Add `default.tsx` to parallel route slots.
8. Review image default changes, run the full E2E suite, then ship. Enable Cache Components in a separate PR (18.2).

## 18.2 Adopting Cache Components

1. Enable `cacheComponents: true` on a branch. Fix build errors by wrapping dynamic reads in `Suspense` and caching stable reads with `'use cache'`, `cacheLife`, `cacheTag`. The adoption Skill helps; review its output.
2. Audit every cached function for user scope (NEXT-05a, in `06-nextjs.md`).
3. Add tags and wire `updateTag` and `revalidateTag` into actions.
4. Enable `partialPrefetching`, add `ensureStatic` to static routes, add `instant()` assertions to E2E.
5. Compare web vitals and server cost before and after.

## 18.3 Tailwind CSS v3 to v4

1. Run `npx @tailwindcss/upgrade` on a branch. Replace `@tailwind` directives with `@import "tailwindcss"`. Move theme config into `@theme` in CSS. Switch the build plugin to `@tailwindcss/turbopack` (or `@tailwindcss/postcss` on webpack).
2. Replace `tailwindcss-animate` with `tw-animate-css`. Delete `tailwind.config.*` and set `"config": ""` in `components.json`.
3. Check renamed or re-defaulted utilities (shadow, blur, ring, outline, border color defaults) with visual regression.
4. Browser baseline for v4 is modern evergreen (Safari 16.4, Chrome 111, Firefox 128 or newer). Check client analytics before upgrading; Tailwind's guidance is to stay on v3.4 when older browsers must be supported.

## 18.4 Prisma 6 to 7

1. Node 20.19 or newer and TypeScript 5.4 or newer. Update `prisma` and `@prisma/client` to 7.10.0, pinned.
2. Switch to `provider = "prisma-client"` with `output`. Add `@prisma/adapter-pg` and pass the adapter to `new PrismaClient`. Add `prisma.config.ts`.
3. Prisma 7 does not load `.env` files; load them explicitly (A.9 does it in `prisma.config.ts`, see `appendix-a7-a9-styling-prisma.md`). Replace `$use` middleware with Client Extensions (`$extends`). Set explicit pool timeouts. The `pg` driver validates SSL certificates, so an untrusted certificate fails with `P1010` (PRISMA-03). Seeding no longer runs automatically; run `prisma db seed`. `migrate dev` and `db push` no longer run `prisma generate`.

## 18.5 Supabase keys and auth helpers

1. Create publishable and secret keys. Replace `anon` with the publishable key in browser and SSR code, and `service_role` with a secret key in server code and Edge Functions. Send them in the `apikey` header only.
2. Migrate to JWT signing keys and `getClaims()`. Remove `@supabase/auth-helpers-nextjs` in favor of `@supabase/ssr`.
3. Test in staging, rotate, then disable the legacy keys in the dashboard. Finish before the end of 2026, when `anon` and `service_role` are deprecated.

## 18.6 shadcn/ui bases

1. Radix projects: `shadcn migrate radix` moves to the unified `radix-ui` package.
2. Radix to Base UI has no CLI migration (`shadcn migrate` offers `cn`, `icons`, `base-color`, `radix`, and `rtl`). Run it through the shadcn skill and an agent, component by component, behind visual regression, with an ADR. Do not mix bases within one project.
