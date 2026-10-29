### A.13 `pnpm-workspace.yaml` (pnpm 12)

`allowBuilds` lists the dependencies whose install scripts may run; pnpm 11 removed `onlyBuiltDependencies` and `ignoredBuiltDependencies`. `trustPolicy: no-downgrade` rejected `lefthook@2.2.2` on 2026-10-17 (published from a personal npm account without provenance, while 2.2.1 was published by GitHub Actions with provenance), so the template pins `lefthook` 2.2.1 instead of excluding it. It also rejected two packages on 2026-10-12, and both exclusions are scoped to one exact version: `prisma@7.10.0` (the npm registry shows no provenance attestation on it, while 7.9.0 and `@prisma/client` 7.10.0 have one) and `semver@6.3.1` (transitive, through `eslint-config-next`). Remove an exclusion when the package moves on. When pnpm meets a pinned version younger than `minimumReleaseAge` (1440 minutes), it appends the package to `minimumReleaseAgeExclude` itself; delete those entries once the versions are a day old. `overrides` clear the two transitive advisories (`mysql2`, `deepmerge-ts`) that `pnpm audit --prod --audit-level=high` reported on a clean Prisma 7.10.0 install; re-check on every Prisma bump. The full `pnpm audit` (dev dependencies included) had reported `braces` 3.0.3 (GHSA-vfj7-8cjw-p6xm, CVE-2026-93687); GitHub withdrew that advisory on 2026-10-23 as not practically exploitable, and the full audit on this scaffold now prints "No known vulnerabilities found". CI still gates on `pnpm audit --prod` (A.11), because dev dependencies never ship in the build. pnpm 12 prints unmet-peer warnings for `eslint-plugin-jsx-a11y` 6.10.2, `eslint-plugin-react` 7.37.5 and `eslint-plugin-import` 2.32.0 against ESLint 10; lint still passes.

`pnpm-workspace.yaml`

```yaml
# pnpm 12. Dependency settings live here, not in package.json.
allowBuilds:
  lefthook: false # its install script is not needed; run `pnpm exec lefthook install` once per clone
  '@prisma/engines': true
  prisma: true
  sharp: true
  unrs-resolver: true

# minimumReleaseAge defaults to 1440 minutes and blockExoticSubdeps to true; both stay on.
# A pinned version younger than a day fails the install. Wait, or list the package here
# with a dated comment and remove the entry once the version is a day old:
# minimumReleaseAgeExclude:
#   - zod # 2026-10-12, remove after 2026-10-13

trustPolicy: no-downgrade
# Add a package here only after reading why trustPolicy flagged it.
trustPolicyExclude:
  - semver@6.3.1
  - prisma@7.10.0

# Transitive advisories reported by `pnpm audit --prod --audit-level=high`. Re-check on every Prisma bump.
overrides:
  mysql2: '>=3.23.1'
  deepmerge-ts: '>=8.0.0'
minimumReleaseAgeExclude:
  - '@tanstack/query-core@5.104.2'
  - '@tanstack/react-query@5.104.2'
  - '@vitest/mocker@5.0.4'
  - '@vitest/spy@5.0.4'
  - vitest@5.0.4
  - zod@4.6.7
```
