## 4. TypeScript standards

- TS-01 (MUST): `strict: true`, `noUncheckedIndexedAccess: true`, `noImplicitOverride: true`, `noFallthroughCasesInSwitch: true`, `verbatimModuleSyntax: true`, `isolatedModules: true`.
- TS-02 (MAY): `exactOptionalPropertyTypes: true` for packages whose dependencies are typed for it. App code that passes optional props into third-party components (for example `next-themes`) fails type-checking with it on, so the Appendix A.1 template leaves it off.
- TS-03 (MUST NOT): `any`, `// @ts-ignore`, unchecked `as` casts, and `!` non-null assertions in production code. Use `unknown` plus narrowing, `satisfies`, or a Zod parse. `// @ts-expect-error` with a reason comment is the only suppression allowed.
- TS-04 (MUST): Derive types from runtime schemas: `type Input = z.infer<typeof inputSchema>`. One source of truth for shape and validation.
- TS-05 (MUST): Model state with discriminated unions, not boolean flags: `{ status: 'idle' } | { status: 'loading' } | { status: 'error'; error: AppError } | { status: 'ready'; data: T }`.
- TS-06 (MUST): Parse at every boundary: form data, action input, route handler body and params, webhook payloads, `process.env`, `localStorage`, `postMessage`, and third-party API responses. Inside the boundary, types are trusted.
- TS-07 (SHOULD): Use branded types for identifiers that must not mix (`UserId`, `OrgId`) when a mix-up would be a security bug.
- TS-08 (SHOULD): Return `Result` shapes (`{ ok: true; data } | { ok: false; error }`) from actions and DAL functions that can fail expectedly. Throw only for programmer errors and unexpected failures.
- TS-09 (MUST): Exhaustive `switch` on unions with a `never` check helper so adding a variant fails the build.
- TS-10 (SHOULD): Prefer `type` for unions and compositions, `interface` for public object contracts that may be extended. Be consistent within a package.
- TS-11 (MUST): Generated types are checked in or generated in CI, never hand-edited: Supabase (`supabase gen types typescript`), Prisma client, route types (`typedRoutes`).
- TS-12 (SHOULD): Use `import type` for type-only imports (enforced by `verbatimModuleSyntax`).
- TS-13 (MUST): Dates cross boundaries as ISO strings, money as integer minor units plus currency code, IDs as strings. No floats for money.

---

