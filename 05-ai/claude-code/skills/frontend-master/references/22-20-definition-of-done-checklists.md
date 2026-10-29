## 20. Definition of Done checklists

### 20.1 Component

- [ ] Server Component unless it needs client features (REACT-01)
- [ ] Props typed, serializable across boundaries, no secrets (REACT-03)
- [ ] Semantic element, accessible name, keyboard operable, visible focus (A11Y-02, A11Y-03)
- [ ] Uses semantic tokens only, no arbitrary values (STYLE-02, STYLE-05)
- [ ] Mobile first, tested at 320 and 1440, container query if slot-based (STYLE-08)
- [ ] Light and dark verified, contrast checked (STYLE-03, STYLE-09)
- [ ] Loading, empty, error, and disabled states exist (UI-09)
- [ ] Reduced motion honored (STYLE-10)
- [ ] Unit or interaction test with role-based queries (TEST-02)

### 20.2 Page or route

- [ ] `loading`, `error`, `not-found` handled; Suspense fallbacks match layout (NEXT-03, NEXT-08)
- [ ] Dynamic data inside Suspense; cached data tagged (NEXT-04, NEXT-05)
- [ ] Metadata, canonical, OG, structured data (NEXT-13, SEO-01)
- [ ] Authorization in the DAL, RLS verified (SEC-03, SB-01)
- [ ] LCP element identified and prioritized, no layout shift (PERF-08, PERF-11)
- [ ] First-load JS within budget (PERF-03)
- [ ] axe clean, keyboard pass done (A11Y-12)
- [ ] E2E path and `instant()` navigation assertion for primary routes (TEST-05, NEXT-20)

### 20.3 Feature

- [ ] Vertical slice in `features/<name>` with schemas, actions, queries, tests (ARCH-03)
- [ ] Zod schema shared by form and action (REACT-14)
- [ ] Action template followed: auth, authz, validate, act, invalidate, typed result (SEC-01, A.6)
- [ ] Rate limits on abuse-prone actions (SEC-06)
- [ ] Migration reviewed, backward compatible, policies and pgTAP tests included (CI-04, SB-10)
- [ ] Audit log entries for security-relevant events (OBS-07)
- [ ] Analytics events documented and consent-gated (OBS-05)
- [ ] Feature flag with owner and expiry if staged (OBS-06)

### 20.4 Pull request

- [ ] `pnpm check` green locally
- [ ] Under about 400 lines, one concern (GIT-02)
- [ ] Screenshots: mobile and desktop, light and dark
- [ ] New dependency justified: size, license, maintenance (PERF-05, SEC-22)
- [ ] No `any`, no `!`, no unchecked casts (TS-03)
- [ ] No `console.log`, no secrets, no PII in logs (OBS-01, SEC-12)
- [ ] ADR linked if architectural (GOV-01)

### 20.5 Production release

- [ ] Next.js, React, and SDKs on latest patched versions (SEC-20)
- [ ] Security headers and CSP verified with a scanner (SEC-08, SEC-09)
- [ ] Supabase advisors clean of ERROR findings, pgTAP green (SB-10)
- [ ] Secrets rotated if staff or contractor access changed (SEC-12)
- [ ] Lighthouse CI and field budgets met (PERF-01, PERF-02)
- [ ] Manual accessibility pass completed and recorded (A11Y-12)
- [ ] Backups and restore tested within the quarter (CI-04)
- [ ] Rollback rehearsed, runbooks present (CI-06, DEL-01)
- [ ] Health checks, alerts, and error reporting verified in production (OBS-02, OBS-08)
- [ ] Source maps uploaded and not public (OBS-02)

---
