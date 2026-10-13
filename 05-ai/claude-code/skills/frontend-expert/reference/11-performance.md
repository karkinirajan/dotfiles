# 11. Performance

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

- PERF-01 (MUST): Field budgets at p75 on mobile: LCP at most 2.5 s, INP at most 200 ms, CLS at most 0.1, TTFB at most 0.8 s, FCP at most 1.8 s. Measured by real-user monitoring per route and device class.
- PERF-02 (MUST): Lab gate in CI on key routes: Lighthouse CI on a mid-range mobile profile (4x CPU slowdown, slow 4G), performance score at least 90, failing on a regression of more than 5 points.
- PERF-03 (MUST): House JavaScript budget per route (compressed, first load): 150 kB target, 250 kB hard limit. Exceeding the limit requires an ADR. These are internal numbers, not web standards.
- PERF-04 (MUST): No request waterfalls. Parallelize fetches, stream with `Suspense`, preload known next data, and never chain client fetches behind effects.
- PERF-05 (MUST): Dependency discipline. Every dependency over 10 kB gzipped is justified in the PR. Prefer platform features (`Intl`, `structuredClone`, `URLSearchParams`, `fetch`). One date library. No Moment, no Lodash (use native methods or a small modular utility). Named imports for icon sets. Use `optimizePackageImports` for large barrel libraries.
- PERF-06 (SHOULD): Inspect bundles on every dependency change with the Turbopack Bundle Analyzer (`next analyze`) and diff snapshots between releases.
- PERF-07 (MUST): INP discipline. No task over 50 ms on interaction paths. Use `startTransition` and `useDeferredValue` for expensive updates, move heavy computation to a Web Worker, virtualize large lists, debounce high-frequency inputs, and keep client component trees small to cut hydration cost.
- PERF-08 (MUST): Assets. The LCP image is not lazy and gets `priority`. Correct `sizes` on every responsive image. AVIF and WebP. Below-the-fold images lazy. Video has a poster and `preload="none"` unless it is the hero. Fonts self-hosted through `next/font`, subsetted, variable where possible, at most two families.
- PERF-09 (SHOULD): Cache aggressively at the edge: immutable hashed static assets (`Cache-Control: public, max-age=31536000, immutable`; Next.js sets it for hashed files under `/_next/static`, and adapters can serve them from `/_next/static/immutable/*`), public API GETs with `s-maxage` and `stale-while-revalidate`, tagged server caches (NEXT-05). `preconnect` only to the one or two origins on the critical path (for example the Supabase host).
- PERF-10 (MUST): Third parties are budgeted. Load after interaction when possible, use facades for embeds (video, maps, chat), and measure their impact with the Lighthouse third-party summary.
- PERF-11 (MUST): No layout shift. Reserve space with `width` and `height` or `aspect-ratio`, size skeletons like content, never inject banners above existing content, and animate with `transform`.
- PERF-12 (MUST): Database performance is frontend performance. Index every column used in RLS policies and filters, kill N+1 in the DAL, paginate, inspect slow queries with `EXPLAIN`, and fix Supabase performance advisor findings.
- PERF-13 (SHOULD): Prefetch deliberately. Default link prefetching is cheap with Partial Prefetching. Use explicit `prefetch` for high-intent links, and use `navigation()` or `prefetch()` to defer expensive cached content (NEXT-07). Do not prefetch long lists of heavy routes.
- PERF-14 (MUST): Measure continuously. Report web vitals with `useReportWebVitals` or the `web-vitals` library to your analytics or a speed-insights product, review p75 by route weekly, and alert on regressions. Use the React Performance Tracks (React 19.2) in Chrome DevTools to find render costs.
- PERF-15 (SHOULD): Optimize perceived speed: instant navigations (Next 16.3), optimistic UI, skeletons, View Transitions, and progress feedback for operations over one second.
- PERF-16 (MUST): No leaks. Clean up effects and subscriptions, abort superseded fetches with `AbortController`, avoid holding large objects in module scope.
