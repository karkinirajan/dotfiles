### A.12 `AGENTS.md` for AI coding assistants

`create-next-app` generates an `AGENTS.md`, and `next dev` maintains the `nextjs-agent-rules` block at the end of it. Keep that block and merge this content above it. Claude Code reads `CLAUDE.md`, not `AGENTS.md`; the one-line `CLAUDE.md` in A.19 imports this file so both tools share one source. The block between the `nextjs-agent-rules` markers is Next.js's own text, copied verbatim from 16.4.0 (it contains em dashes); `next dev` rewrites it, so do not edit it.

`AGENTS.md`

```markdown
# AGENTS.md

Source of truth for conventions: FRONTEND-MASTER.md (repo root). Read sections 0, 5, 6, 7 and 9 before changing code. Cite rule IDs (for example SEC-01) in commit messages and PR descriptions.

## Commands

- `pnpm dev` runs the app locally.
- `pnpm check` runs typecheck, lint, format check, unit tests, and build. It must be green before you claim a task is done.
- `pnpm test:e2e` runs Playwright against a production build (`pnpm build` first).
- `just up` starts local Supabase and Redis and writes `.env.local`; `just down` stops them. `just types` regenerates database types.
- `python3 audit/audit.py run --profile ci` checks every rule a tool can check and must show no FAIL. `python3 audit/audit.py brief <domain>` prints the rules a reviewer judges by hand. `/frontend-audit` runs the full audit (A.21).

## Non-negotiable rules

- Server Components by default. `"use client"` only on the smallest interactive leaf.
- Every Server Action and Route Handler: authenticate, authorize, validate with Zod, then act.
- All data access goes through server-only DAL functions. Never import the admin client or Prisma in components.
- Never expose secret keys. Only `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` is public.
- Use `getClaims()` on the server, never `getSession()`.
- Tailwind v4 tokens only: no raw palette classes, no arbitrary values, no `@apply` in components.
- No `any`, no non-null assertions, no unchecked casts, no `console.log`, no `useEffect` for data fetching.
- Every UI change covers loading, empty, and error states, keyboard use, light and dark themes, and 320px width.

## Do not

- Change auth, RLS policies, `proxy.ts`, security headers, or migrations without calling it out for human review.
- Add a dependency without stating its size, license, and why the platform cannot do the job.
- Commit, push to main, or read production secrets.

## When unsure

Ask one specific question, or present two or three options with trade-offs. Do not guess on security.

## Git

Author `kneeraazon404`. Conventional Commits. One concern per PR.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
```

