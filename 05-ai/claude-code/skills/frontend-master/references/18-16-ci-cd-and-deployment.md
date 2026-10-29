## 16. CI/CD and deployment

- CI-01 (MUST): Pipeline order: frozen install, then typecheck, lint, and unit tests in parallel, then build, then E2E (against the build), Lighthouse CI, and axe in parallel, then security scans, then preview deploy. On `main`: migrate the database, deploy production, run smoke tests, tag the release. Target under 10 minutes. Cache the pnpm store, `.next/cache`, and Playwright browsers.
- CI-02 (MUST): `main` is protected: required checks, no direct pushes, squash merge. `CODEOWNERS` requires review for `supabase/migrations`, `src/lib/auth`, `src/proxy.ts`, security header config, and `.github/workflows`.
- CI-03 (MUST): Every PR gets a preview deployment with its own database (Supabase branch or ephemeral local stack). Secrets are scoped per environment. Production keys never appear in preview or CI.
- CI-04 (MUST): Migrations are forward-only and backward compatible (expand, migrate, contract) so the previous app version keeps working during rollout. They run before the app deploy. Destructive changes ship one release after the code stops using the column. Production has point-in-time recovery enabled and a restore test every quarter.
- CI-05 (SHOULD): Trunk-based development with short-lived branches and feature flags for unfinished work. Changelog generated from Conventional Commits (release-please or similar).
- CI-06 (MUST): Rollback is one step: redeploy the previous artifact (instant rollback on Vercel, previous task definition on ECS). For high-traffic launches use a gradual rollout.
- CI-08 (MUST): Container builds (when self-hosting): multi-stage Dockerfile, `output: 'standalone'`, non-root user, pinned base image digest, health check, no secrets in layers, `NEXT_TELEMETRY_DISABLED=1`, `HOSTNAME=0.0.0.0`, and connection draining at the load balancer (Next.js 16.4 exits immediately with code 143 on SIGTERM and does not finish in-flight requests, so use an ECS deregistration delay or a Kubernetes `preStop` sleep longer than your slowest request). With more than one instance, configure a shared cache handler (for example Redis) so `'use cache'` entries and tag invalidation stay consistent across instances, and persist the image optimizer cache.
- CI-09 (MUST): Promote one artifact through environments (preview, staging, production). Differences are configuration and flags only.
- CI-10 (SHOULD): Costs are budgeted and alerted: image optimization, function duration, bandwidth, database egress and connections. `'use cache'` and tagged caching reduce compute; measure before and after.

Hosting options (decide per project, record in an ADR):

| Option | Strengths | Weaknesses | Pick when |
|---|---|---|---|
| Vercel | Best Next.js integration, Cache Components with PPR automatic, previews, gradual rollouts, observability | Cost at scale, platform coupling | Client MVPs, fast iteration, small teams |
| AWS ECS or Fargate with Docker (standalone) | Cost predictability, VPC control, compliance, your existing AWS expertise | You own scaling, caching layer, patching, observability | Regulated clients, steady high traffic, existing AWS estate |
| Cloudflare via a Next.js adapter | Global edge compute (Workers), KV, R2 | Only an adapter listed as verified in the Next.js deployment docs has passed the shared adapter test suite; others have no such guarantee for Cache Components, Server Actions, or streaming | Edge-heavy, cost-sensitive, simple data access |
| VPS with Docker and Nginx | Lowest cost | Patch SLA (SEC-20) is entirely on you, no managed rollbacks | Small internal tools with a maintenance agreement |

---
