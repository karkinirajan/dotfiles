# 15. Tooling and developer experience

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

- TOOL-01 (MUST): pnpm via the `packageManager` field, Node pinned via `.nvmrc` or `mise`. One command boots a fresh clone: `just up && pnpm i && pnpm dev`.
- TOOL-02 (MUST): Linting runs through the ESLint CLI (`next lint` was removed in Next 16) with the ESLint 10 flat config in A.14 (`appendix-a11-a15-ci-tooling.md`). It layers `eslint-config-next/core-web-vitals` (which already registers `eslint-plugin-react-hooks` with the compiler rules, `eslint-plugin-jsx-a11y`, and the Next plugin), the strict jsx-a11y rule set (added as `{ rules: jsxA11y.flatConfigs.strict.rules }`, because registering the plugin a second time throws "Cannot redefine plugin"), `typescript-eslint` `strictTypeChecked` and `stylisticTypeChecked`, `no-console`, `consistent-type-imports`, `no-floating-promises`, `no-misused-promises`, and `switch-exhaustiveness-check`. Import boundaries (ARCH-02) are enforced by `dependency-cruiser` (TOOL-08). Generated files are ignored.

| Toolchain | Strength | Weakness | Pick when |
|---|---|---|---|
| ESLint + Prettier | Widest rule coverage, type-aware rules, Next and a11y plugins | Slower, two tools | Default for client work |
| Biome (lint + format) | Very fast, one tool | Fewer type-aware and framework rules | Speed matters and rule gaps are covered by `tsc` and tests |
| oxlint + Prettier | Very fast linting | Smaller plugin ecosystem | Large monorepos where lint time dominates |

- TOOL-03 (MUST): Prettier with `prettier-plugin-tailwindcss`, format on save, `--check` in CI.
- TOOL-04 (MUST): Git hooks via lefthook (or husky plus lint-staged): staged ESLint and Prettier, gitleaks (`gitleaks git --staged --redact --no-banner .`), commitlint. Hooks finish in under 10 seconds. Full typecheck and tests run in CI and in `pnpm check`.
- TOOL-05 (MUST): `pnpm check` runs exactly what CI runs (`next typegen && tsc --noEmit`, lint, unit tests, build). Route types come from `next typegen`, so a type-check without it fails on `LayoutProps` and typed routes. It is green before every push.
- TOOL-06 (SHOULD): Editor setup committed: `.editorconfig`, `.vscode/settings.json` (TypeScript SDK from the workspace, Tailwind `classRegex` for `cn` and `cva`). For Neovim: TypeScript LSP, `tailwindcss-language-server`, ESLint LSP, Prettier through a formatter plugin, Tailwind class sorting on save.
- TOOL-07 (SHOULD): A `justfile` (or Makefile) wraps local infrastructure: `just up` (Supabase stack via Docker or Podman, recipes in A.18), `just reset` (reset and seed), `just types` (generate DB types), `just test-db` (pgTAP). Linux-native: install the Supabase CLI from the package manager or run it through `pnpm dlx`.
- TOOL-08 (SHOULD): Use `knip` to find unused files, exports, and dependencies, and `dependency-cruiser` for cycles and boundary violations, both in CI.
- TOOL-09 (SHOULD): Renovate: grouped updates, automerge for passing patch and dev-dependency bumps, immediate security PRs, GitHub Actions pinned by digest, weekday schedule.
- TOOL-10 (MUST): AI-assisted development rules:
  - `AGENTS.md` (Appendix A.12, in `appendix-a11-a15-ci-tooling.md`) is present and points to this file. `next dev` writes a `<!-- BEGIN:nextjs-agent-rules -->` block into it that sends agents to the version-matched docs in `node_modules/next/dist/docs/`; commit that block and leave it in place.
  - Add the shadcn skill (`pnpm dlx skills add shadcn/ui`) and the first-party Next.js Skills (Cache Components adoption, bundle optimizer) when relevant.
  - Agents run `pnpm check` before claiming a task is done.
  - Changes to auth, RLS policies, `proxy.ts`, security headers, and migrations always get human review. Agents never receive production secrets.
  - Prefer fetching docs through a docs MCP server or the official docs over trusting model memory for APIs that changed in the last year.
