# 5. React standards

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

## 5.1 Server and client boundary

- REACT-01 (MUST): Components are Server Components unless they need state, effects, event handlers, refs to DOM, or browser-only APIs. Add `"use client"` to the smallest leaf that needs it.
- REACT-02 (MUST): Keep client boundaries thin. Pass Server Components into Client Components as `children` or slot props so the server subtree is not pulled into the client bundle.
- REACT-03 (MUST): Props crossing the boundary are serializable and public. Anything passed to a Client Component is visible in the browser. Never pass secrets, full database rows, or objects with extra fields. Pass DTOs.
- REACT-04 (SHOULD): Prefer composition over configuration. Compound components and slot props beat boolean prop piles. A component with more than seven props needs a redesign.
- REACT-05 (MUST): Do not hand-write `useMemo`, `useCallback`, or `memo` with the React Compiler on. Add them only when a profiler trace proves a regression the compiler did not fix, and leave a comment with the trace link. Keep `eslint-plugin-react-hooks` (v7 or newer) compiler rules at error level so code stays compiler-safe (pure render, no mutation of props or state).

## 5.2 Effects, data, and state

- REACT-06 (MUST NOT): No `useEffect` for data fetching, derived state, resetting state on prop change, or event logic. Fetch on the server or with TanStack Query. Derive during render. Reset with a `key`. Handle events in event handlers.
- REACT-07 (MUST): Effects exist only to synchronize with external systems (subscriptions, timers, imperative widgets, analytics). Every effect has cleanup. Use `useEffectEvent` for logic that reads latest props or state but must not retrigger the effect.
- REACT-08 (SHOULD): Use `use(promise)` inside `Suspense` to stream server-started promises into Client Components. Create the promise on the server, never inside the client component.
- REACT-09 (MUST): State has exactly one owner. Pick from this table before writing `useState`.

| State kind | Owner | Tool |
|---|---|---|
| Filters, sort, pagination, tab, selected item, dialog open (shareable) | URL | `searchParams`, `<Link>`, `nuqs` 2.10.2 for typed client access |
| Remote data | Server, with client cache only when needed | RSC + DAL, TanStack Query for live or optimistic needs |
| Form values and validation | Form | `<form action>` + `useActionState`, React Hook Form for complex client forms |
| Ephemeral UI (hover, popover, local toggle) | Component | `useState` |
| Cross-component client state (cart draft, editor tool state) | Small store | Zustand 5 scoped to the feature |
| Dependency injection (theme, session DTO, feature flags) | Context | Split by change frequency, provider placed low |

- REACT-10 (MUST): Keys are stable domain IDs. Never array index for lists that reorder, filter, or insert.
- REACT-11 (MUST): Context holds stable, low-frequency values only. High-frequency state in context re-renders every consumer. Split contexts by update rate.
- REACT-12 (SHOULD): Use `<Activity mode="hidden">` to preserve state for tabs, wizards, and sidebars instead of unmount and remount.

## 5.3 Forms and mutations

- REACT-13 (MUST): Default form pattern: native `<form action={serverAction}>`, `useActionState` for result and pending state, `useFormStatus` in submit buttons, `useOptimistic` for instant list updates. Works without JavaScript, which is also the most robust path under bad networks.
- REACT-14 (MUST): One Zod schema per form, imported by both the client (inline hints) and the Server Action (authoritative validation). The server result carries field-level errors keyed by field name.
- REACT-15 (SHOULD): Use React Hook Form (with `@hookform/resolvers/zod`) or TanStack Form only for forms with dynamic field arrays, multi-step wizards, or cross-field live validation. Do not add it for a three-field form.
- REACT-16 (MUST): Disable double submit (pending state), show inline errors tied to inputs with `aria-describedby` and `aria-invalid`, move focus to the first invalid field on failed submit, and keep user input after server errors.
- REACT-17 (MUST): Mutations are idempotent where the user can retry (payments, orders). Send an idempotency key generated once per form mount.

## 5.4 Correctness hygiene

- REACT-18 (MUST): Render is pure. No `Date.now()`, `Math.random()`, `window` access, or mutation during render. Use `useId` for ids, `useSyncExternalStore` for external stores, and effects for browser-only reads.
- REACT-19 (SHOULD): `suppressHydrationWarning` only on single elements that legitimately differ (theme class on `<html>`, a client-formatted timestamp). Never as a blanket fix.
- REACT-20 (MUST): Never define components inside components. Never mutate props.
- REACT-21 (SHOULD): Refs are plain props in React 19; do not add `forwardRef` to new code. Ref callbacks may return cleanup functions.
- REACT-22 (SHOULD): Components stay under about 150 lines. Extract when a component has more than one reason to change or more than three levels of nesting.
- REACT-23 (MUST): Virtualize or paginate lists beyond about 200 rows (`@tanstack/react-virtual`, or server pagination). Prefer server pagination with URL state for anything that is also searchable.
- REACT-24 (SHOULD): Use View Transitions (stable in React 19.3) for route and list transitions, gated by `prefers-reduced-motion`.

## 5.5 TanStack Query rules (client-side server state)

- RQ-01 (MUST): Use it only for data that must live and refresh on the client: polling, infinite scroll, optimistic collaborative lists, dependent live queries. If a Server Component can render it, do not add a query.
- RQ-02 (MUST): Create the `QueryClient` per request on the server and once per browser session on the client. Never a module-level singleton on the server (cross-request data leak).
- RQ-03 (MUST): Set a non-zero `staleTime` (for example 60 seconds) when hydrating server-prefetched data so the client does not refetch immediately.
- RQ-04 (MUST): Query keys come from a key factory per feature (`todoKeys.list(filters)`). Never inline string arrays in components.
- RQ-05 (SHOULD): Share `queryOptions()` between server prefetch and client hooks so keys and fetchers cannot drift.
- RQ-06 (MUST): Prefetch on the server and pass `dehydrate(queryClient)` through `HydrationBoundary` for first paint. Do not fetch the same data in a Server Component and again in a client query.
- RQ-07 (MUST): Mutations invalidate by key or update the cache directly. Optimistic updates snapshot, apply, and roll back on error.
- RQ-08 (SHOULD): Use `useSuspenseQuery` with a `Suspense` boundary and `QueryErrorResetBoundary` so loading and error UI live in boundaries, not in every component.
