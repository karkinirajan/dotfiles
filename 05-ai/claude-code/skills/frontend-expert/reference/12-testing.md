# 12. Testing

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

- TEST-01 (MUST): Test at the lowest level that proves the behavior. Unit (Vitest) for pure logic and schemas. Component (Vitest plus Testing Library) for interaction. Integration (MSW) for client data flows and route handlers. Database (pgTAP) for RLS. End-to-end (Playwright) for auth, payments, and core CRUD. Visual and accessibility checks on key screens.
- TEST-02 (MUST): Test behavior, not implementation. Query by role and accessible name first, `data-testid` last. Use `user-event` for interaction. No large DOM snapshots.
- TEST-03 (MUST): Async Server Components are not unit-tested in jsdom. Extract logic into pure functions and DAL functions that are tested directly, and cover the rendered result with Playwright.
- TEST-04 (MUST): Server Actions are tested as async functions with a controlled session and a real local database where possible. Every action has tests for: unauthenticated, unauthorized, invalid input, success, idempotent retry, and the cache invalidation call.
- TEST-05 (MUST): Playwright runs against a production build (`next build` then `next start`), with traces on first retry, authentication state created through the API in `globalSetup` and reused via `storageState`, web-first assertions (no `waitForTimeout`), isolated data per test, projects for mobile (390 by 844) and desktop (1440 by 900), and the `instant()` helper from `@next/playwright` for navigation assertions (an experimental API that requires Cache Components). Production builds disable the testing API; build the E2E artifact with `EXPOSE_TESTING_API=1`, which A.2 maps to `experimental.exposeTestingApiInProductionBuild`, and never deploy that build.
- TEST-06 (MUST): Every RLS policy has pgTAP tests for allowed and denied access. The negative case (user A cannot read user B) is mandatory.
- TEST-07 (SHOULD): Coverage is a signal. Gate on diff coverage (at least 80 percent of changed lines) and hold auth, money, and permission modules to 90 percent branch coverage.
- TEST-08 (MUST): A flaky test is quarantined within 24 hours and fixed within a week. CI retries once and always uploads the trace.
- TEST-09 (SHOULD): Public utility types get type tests (`expectTypeOf`).
- TEST-10 (SHOULD): Third-party APIs are mocked with recorded fixtures (MSW) in CI, with a nightly live smoke test.
- TEST-11 (SHOULD): Visual regression via Playwright `toHaveScreenshot` on key screens at three viewports and both themes, dynamic regions masked, captured only in the CI Linux container to avoid rendering drift.
- TEST-12 (SHOULD): Test data comes from factories. No shared mutable fixtures. Each test creates and cleans its own data.
- TEST-13 (MAY): Mutation testing (Stryker) on critical domain modules.
- TEST-14 (SHOULD): Name tests as behavior: `describe('calculateInvoice')` and `it('rounds tax per line before summing')`. Arrange, act, assert.
