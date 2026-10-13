# 9. Security

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

Threat model in one table. Re-read it when scoping any feature.

| Asset | Actor | Entry point | Primary controls |
|---|---|---|---|
| User accounts and sessions | Credential stuffers, phishers | Auth forms, OAuth callbacks | SB-08, SEC-10, SEC-15, SEC-06 |
| Tenant data | Other tenants, curious users | IDs in URLs, actions, handlers | RLS (SB-01), DAL authz (SEC-03), pgTAP (SB-10) |
| Server secrets | External attackers, supply chain | Env leaks, vulnerable framework, malicious packages | SEC-12, SEC-20 to SEC-23 |
| Server compute | Anyone on the internet | Server Actions, handlers, image optimizer, RSC protocol | SEC-01, SEC-06, SEC-11, patch SLA |
| Users' browsers | Injected content, third parties | XSS, scripts, links | SEC-07, SEC-08, SEC-17 |

## 9.1 Application layer

- SEC-01 (MUST): Every Server Action and Route Handler is a public endpoint reachable by anyone who can send an HTTP request, whether or not your UI exposes it. Inside each: authenticate, authorize against the specific resource, validate all input with Zod, then act. Hiding a button is not access control.
- SEC-02 (MUST): `proxy.ts` is never the only authorization check. CVE-2025-29927 showed middleware can be bypassed. Authorization is repeated in the DAL (SEC-03) and enforced by RLS.
- SEC-03 (MUST): Prevent IDOR. Never trust an ID from the client. Scope every query by the session user or tenant (`where id = $1 and org_id = $session_org`), or rely on RLS, and verify ownership before returning or mutating.
- SEC-04 (MUST): State changes happen through POST (Server Actions or POST handlers), never GET. Server Actions compare the `Origin` host with `x-forwarded-host` or `host` and reject a mismatch; a request with no `Origin` header is let through with a warning, so authorization (SEC-01) is the real control. Behind a reverse proxy that forwards the public host no setting is needed; otherwise list the browser-visible hosts in `experimental.serverActions.allowedOrigins`. Cookies are `SameSite=Lax` at minimum (`Strict` for admin areas).
- SEC-05 (MUST): Treat all action inputs as hostile: `FormData` entries, bound arguments, and anything derived from closures. Parse with Zod, reject unknown keys on JSON bodies (`.strict()`; for raw `FormData` use `z.object`, which strips them, because Next adds internal `$ACTION_*` fields), cap string lengths and array sizes, never accept table names, column names, or raw SQL fragments from the client.
- SEC-06 (MUST): Rate limit authentication, password reset, OTP, signup, contact forms, and expensive actions per IP and per user (platform firewall or a Redis-based limiter). Set body size limits on handlers, and set `experimental.serverActions.bodySizeLimit` (default 1 MB, applies to the raw multipart body, so leave 10 to 20 KB of headroom for uploads). Return `429` with `Retry-After`.
- SEC-07 (MUST): XSS. React escapes by default; keep it that way. `dangerouslySetInnerHTML` only with sanitized, allow-listed HTML (DOMPurify or `rehype-sanitize`) and a code comment naming the sanitizer. Validate URL protocols before putting user input in `href` or `src` (`https:`, `http:`, `mailto:` only; reject `javascript:` and `data:`). `target="_blank"` always carries `rel="noopener noreferrer"`. React 19.3 supports Trusted Types; evaluate `require-trusted-types-for 'script'` in report-only mode.
- SEC-11 (MUST): SSRF and open redirects. `images.remotePatterns` lists exact hosts. Any server-side `fetch` of a user-supplied URL goes through an allow-list and blocks private and link-local ranges. Redirect targets (`?next=`) must be relative paths or match an allow-list.
- SEC-13 (MUST): Uploads: enforce size and type server-side (check magic bytes, not only the extension), generate random object names, store in a private bucket, scan if the files are shared with other users, serve user content from a separate origin or with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`.
- SEC-14 (MUST): Webhooks: verify the provider signature on the raw body before parsing, enforce a timestamp tolerance, deduplicate by event id, respond fast and process in `after()` or a queue.
- SEC-15 (SHOULD): Auth hardening: generic messages to prevent account enumeration, re-authentication for sensitive operations, backoff after failures, accessible authentication (A11Y-05), optional breached-password check via k-anonymity.
- SEC-18 (MUST): No stack traces, SQL errors, or internal IDs reach users. Return a stable error code and an incident reference (the error digest), log details server-side.
- SEC-19 (MUST): CORS is an explicit allow-list per route. Never `Access-Control-Allow-Origin: *` together with credentials.

## 9.2 Browser hardening

- SEC-08 (MUST): Ship a Content Security Policy with `default-src 'self'`, `object-src 'none'`, `base-uri 'none'`, `frame-ancestors 'none'`, `form-action 'self'`, explicit `connect-src` (your Supabase HTTP and WebSocket origins, analytics), `img-src` for your storage host, `style-src 'self'` plus the nonce, and `style-src-attr 'unsafe-inline'` (React inline `style` attributes). Start in `Content-Security-Policy-Report-Only`, collect reports, then enforce. Choose the script policy from this table. Every row was built with Next.js 16.4.0 and Cache Components on, and run in Chromium.

| Mode | Script policy | Static shell | Result |
|---|---|---|---|
| A. Dynamic nonce | `'self' 'nonce-...' 'strict-dynamic'`, nonce minted in `proxy.ts` and sent as the request header `Content-Security-Policy`; root layout has `export const instant = false` and awaits `connection()` | Lost on every route | Works. Strongest. Default for authenticated apps that handle sensitive data. |
| B. Static shell, inline scripts allowed | `'self' 'unsafe-inline'` | Kept | Works. CSP no longer blocks injected scripts, so XSS defense rests on SEC-07 and the other directives. Default for marketing and content sites, with an ADR. |
| C. Nonce on a prerendered shell | nonce | Kept | Fails. The prerendered HTML has no nonce, the browser blocks every script, and the page never hydrates. Do not ship. |
| D. SRI hashes plus `script-src 'self'` | hashes | Kept | Fails the same way. Do not ship. |
| E. Nonce with `cacheComponents` off | nonce | Not applicable | Works, but gives up Cache Components. Not a reason to turn it off. |

Next.js reads the nonce from the request header `Content-Security-Policy`, so `proxy.ts` sets the header on the forwarded request as well as on the response, and Client Components that inject scripts (for example `next-themes`) take the nonce as a prop (A.10, A.16). The CSP smoke test in A.10 fails the build when scripts are blocked or the page does not hydrate. Full implementation (both modes) is in `appendix-a10-csp.md`.

- SEC-09 (MUST): Response headers on every route: `Strict-Transport-Security` (preload only after verifying all subdomains), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` with unused features disabled, `Cross-Origin-Opener-Policy: same-origin`, `X-Frame-Options: DENY` alongside `frame-ancestors`.
- SEC-10 (MUST): Session cookies are `HttpOnly`, `Secure`, `SameSite=Lax` or stricter, scoped to the narrowest path and domain, with the `__Host-` prefix where the platform allows. No access or refresh tokens in `localStorage` or `sessionStorage`.
- SEC-17 (SHOULD): Third-party scripts are justified, loaded with `next/script` strategies, constrained by CSP, wrapped by a consent check where required, and embedded content uses sandboxed iframes with a minimal `allow` list. Static third-party files get SRI hashes.

## 9.3 Secrets, privacy, and supply chain

- SEC-12 (MUST): Secrets exist only in the platform secret store and server runtime. `lib/env/server.ts` (guarded by `server-only`) and `lib/env/public.ts` validate env with Zod at boot and export `serverEnv` and `publicEnv`. `.env*` is gitignored except `.env.example`. Never define a secret as an inline literal in code, because a source-exposure bug in Server Functions (CVE-2025-55183) leaks inline values. Scan for secrets in pre-commit and CI (gitleaks or equivalent). Rotate on any suspicion.
- SEC-16 (SHOULD): Collect the minimum personal data, keep it out of logs and analytics, document retention, support export and deletion requests, and gate non-essential cookies behind consent where the law requires it.
- SEC-20 (MUST): Patch SLA for Next.js, React, and Supabase and Prisma SDK security releases: Critical within 24 hours, High within 72 hours, others in the next sprint. CI and deploy must be able to ship an emergency bump in under an hour. Never pin to a vulnerable version "until the next release".
- SEC-21 (MUST): Monitor advisories (Next.js feed, GitHub security advisories, Renovate security PRs) and run `pnpm audit` plus an OSV scan in CI. Production deploys fail on known Critical issues in direct dependencies.
- SEC-22 (MUST): Supply chain, configured in `pnpm-workspace.yaml` (A.13, in `appendix-a11-a15-ci-tooling.md`): committed lockfile and `pnpm install --frozen-lockfile` in CI; dependency build scripts denied unless listed in `allowBuilds`; `minimumReleaseAge` at its pnpm 11 default of 1440 minutes, so a pinned version younger than a day fails the install (wait, or list the package in `minimumReleaseAgeExclude` with a dated comment and remove the entry later); `blockExoticSubdeps` at its default `true`; `trustPolicy: no-downgrade`, with each package it flags read and then listed in `trustPolicyExclude`; `overrides` for transitive advisories that `pnpm audit` reports; npm provenance checked for critical packages; and a short review (maintainers, size, license, recent activity) before adding any dependency.
- SEC-23 (MUST): Incident runbook in `docs/security/incident.md`: if a vulnerable version was internet-exposed, assume compromise. Patch, rotate every secret the server could read (Supabase secret keys, database URLs, third-party API keys), revoke sessions, review logs, and notify the client.
- SEC-24 (SHOULD): Before launch, map the app against OWASP ASVS Level 2 and the OWASP Top 10, add `/.well-known/security.txt`, and run a dependency, secrets, and header scan against the preview deployment.
- SEC-25 (SHOULD): Automated security checks in CI: ESLint security rules, Semgrep or CodeQL, RLS pgTAP suite, and an OWASP ZAP baseline against the preview URL for public-facing apps.
