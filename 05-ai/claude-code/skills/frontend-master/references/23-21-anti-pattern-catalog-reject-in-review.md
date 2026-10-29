## 21. Anti-pattern catalog (reject in review)

| Anti-pattern | Why it fails | Do instead | Rule |
|---|---|---|---|
| `"use client"` on a layout or page | Ships the whole subtree to the browser | Push the boundary to the interactive leaf | REACT-01 |
| `useEffect` to fetch or derive data | Waterfalls, flicker, races | Server fetch, TanStack Query, derive in render | REACT-06 |
| `getSession()` on the server | Does not revalidate the token | `getClaims()` or `getUser()` | SB-03 |
| Secret or `service_role` key in client code | Full database access for anyone | Publishable key only in the browser | SB-02 |
| Table without RLS | Public table | Enable RLS, write and test policies | SB-01 |
| Auth only in `proxy.ts` | Bypassable (CVE-2025-29927) | Repeat in the DAL, enforce with RLS | SEC-02 |
| Action without validation or authz | Public unauthenticated endpoint | Template A.6 | SEC-01 |
| `select('*')` or unbounded lists | Over-fetching, slow, leaks fields | Named columns, bounded pagination | SB-13, DAL-04 |
| Caching per-user output with `'use cache'` and no user key | Cross-user data leak | Pass user in the key or do not cache | NEXT-05a |
| Barrel files everywhere | Slow builds, cycles, bloated bundles | Direct imports | STR-05 |
| `h-screen` on mobile | Broken by dynamic toolbars | `min-h-dvh` | STYLE-08 |
| String-built Tailwind classes | Classes missing from the build | Complete literal classes via maps | STYLE-06 |
| `@apply` component classes | Recreates CSS-in-the-dark | Components plus utilities | STYLE-11 |
| Blanket `suppressHydrationWarning` | Hides real bugs | Fix the mismatch, scope to one element | REACT-19 |
| Hand-rolled modal or dropdown | Broken focus and a11y | Library primitives | UI-06 |
| `div` with `onClick` | Not focusable, no semantics | `button` or `a` | A11Y-02 |
| Placeholder as label | Disappears, inaccessible | Visible label | UI-04 |
| Spinner with no layout | Layout shift, perceived slowness | Skeleton with final dimensions | NEXT-08 |
| `NEXT_PUBLIC_` for anything secret | Inlined into the bundle | Server env only | SEC-12 |
| Tokens in `localStorage` | Readable by any XSS | HttpOnly cookies | SEC-10 |
| `catch {}` that swallows errors | Silent failure | Typed result, log, surface to the user | TS-08, OBS-04 |
| Floats for money | Rounding bugs | Integer minor units plus currency | TS-13 |
| `any` and `as` to silence types | Type safety lost at the worst place | Parse with Zod, narrow | TS-03 |
| Polling without backoff | Self-inflicted outage | Backoff with jitter, or Realtime | OBS-11 |
| Unpinned deps, no lockfile discipline | Supply chain risk | Pinned versions, frozen installs | SEC-22 |
| Postponing a Critical Next.js patch | Active exploitation window | Ship within 24 hours | SEC-20 |

---
