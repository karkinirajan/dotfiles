## 13. Observability and error handling

- OBS-01 (MUST): Server logging is structured JSON through `lib/logger.ts` (level, message, request id, route, duration, outcome). No `console.log` in production code (lint rule). No personal data or secrets in logs.
- OBS-02 (MUST): Errors are reported to Sentry or an equivalent from browser, server, and edge through `instrumentation.ts` (`register` and `onRequestError`). Source maps are uploaded in CI and not publicly served. Releases are tagged with the git SHA. PII scrubbing is on.
- OBS-03 (SHOULD): Distributed tracing with OpenTelemetry (`@vercel/otel` or the Sentry SDK). Propagate the trace id from browser to server to database calls. Wrap DAL functions in spans.
- OBS-04 (MUST): Error boundaries at the route level (`error.tsx`) and at the root (`global-error.tsx`). The message shown to users contains a plain explanation, a retry action, and the error digest as a support reference. Not-found (404) and server errors (500) are distinct experiences.
- OBS-05 (SHOULD): Product analytics are privacy-first (PostHog, Plausible, or equivalent), behind a typed `track()` wrapper with a documented event taxonomy (`noun_verb`, snake case), consent-gated, with no personal data in event properties.
- OBS-06 (MUST): Feature flags live in one typed registry with an owner and an expiry date. Remove a flag within 30 days of full rollout. No nested flags.
- OBS-07 (MUST): Security-relevant events (sign-in, role change, data export, deletion, key creation) are written to an append-only `audit_log` through the DAL. RLS allows inserts only through a function and selects only for admins.
- OBS-08 (MUST): `/api/health` (cheap, unauthenticated) and `/api/ready` (checks Supabase connectivity) exist and are monitored by an external uptime check.
- OBS-09 (SHOULD): Define SLOs per client app (availability, error rate, p95 route latency, web vitals p75) and alert on burn rate. Keep alerts few and actionable.
- OBS-10 (MUST): Server Actions log the action name, duration, and outcome code, never the input payload.
- OBS-11 (MUST): Client resilience: capture `unhandledrejection` and `error` events, show an offline indicator, retry idempotent requests with exponential backoff and jitter, do not retry 4xx responses, and always give the user a way forward.

---
