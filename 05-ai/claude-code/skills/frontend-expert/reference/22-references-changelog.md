# 22. References and sources

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

Primary sources used to verify section 1 on 2026-10-12:

- Next.js 16.4 release notes: https://nextjs.org/blog/next-16-4
- Next.js 16.3 release notes: https://nextjs.org/blog/next-16-3
- Next.js 16 release notes: https://nextjs.org/blog/next-16
- Next.js upcoming security update (2026-10-14): https://nextjs.org/blog/upcoming-nextjs-security-update-october-2026
- Next.js security update 2025-12-11: https://nextjs.org/blog/security-update-2025-12-11
- Next.js RCE advisory GHSA-9qr9-h5gf-34mp: https://github.com/vercel/next.js/security/advisories/GHSA-9qr9-h5gf-34mp
- React critical vulnerability disclosure: https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components
- React 19.3 announcement: https://react.dev/blog/2026/09/09/react-19-3
- Supabase SSR for Next.js: https://supabase.com/docs/guides/auth/server-side/nextjs
- Supabase API keys: https://supabase.com/docs/guides/api/api-keys
- Supabase JWT signing keys: https://supabase.com/blog/jwt-signing-keys
- shadcn/ui CLI v4: https://ui.shadcn.com/docs/changelog/2026-03-cli-v4
- shadcn/ui Base UI default: https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default
- shadcn/ui React Aria base: https://ui.shadcn.com/docs/changelog/2026-07-react-aria
- Prisma 7 upgrade guide: https://www.prisma.io/docs/orm/more/upgrade-guides/upgrading-versions/upgrading-to-prisma-7
- Tailwind CSS upgrade guide: https://tailwindcss.com/docs/upgrade-guide
- pnpm build settings: https://pnpm.io/settings/build
- pnpm dependency resolution settings: https://pnpm.io/settings/dependency-resolution

Standards and general references:

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Core Web Vitals: https://web.dev/articles/vitals
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- OWASP Top 10: https://owasp.org/www-project-top-ten/

## Changelog

- 2026-10-12: Initial version. Verified against Next.js 16.4, React 19.3, Tailwind 4.3, shadcn/ui CLI v4 (Base UI default), Supabase `getClaims` and publishable keys, Prisma 7.
- 2026-10-12 (rev 2): Appendix A regenerated from a project that was typechecked, linted, formatted, unit-tested, built with `next build`, audited, and browser-tested (Chromium, Playwright, axe, CSP smoke test). Added exact version pins (1.1), TS 6 vs TS 7 (1.1.1), the CSP and Cache Components matrix (SEC-08), pnpm 12 supply-chain settings (SEC-22, A.13), and ESLint 10 config (A.14). Removed unverified-claim notices. Not exercised: the Supabase Docker stack and Redis; their templates are compiled and linted only.
- 2026-10-13: Imported into the `frontend-expert` Claude Code skill, split section-by-section into this reference directory so a session loads only the part a task touches. No content was shortened, summarized, or dropped in the split — every rule ID, table, SQL policy, and code template from the source document is preserved verbatim in its reference file.
