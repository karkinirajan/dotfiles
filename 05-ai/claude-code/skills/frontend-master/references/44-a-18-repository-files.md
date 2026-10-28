### A.18 Repository files

`package.json` pins every version exactly (VER-01); `postinstall` and the two `DIRECT_URL`/`DATABASE_URL` lines belong to Prisma option B. `pnpm typecheck` runs `next typegen` first because route types (`LayoutProps`, typed routes) are generated. `.env.example` has empty secrets on purpose: an empty value fails the Zod parse at boot. The `justfile` writes `.env.local` from the local Supabase stack, so run `just up` before `pnpm i`.

`package.json`

```json
{
  "name": "app",
  "version": "0.1.0",
  "private": true,
  "engines": {
    "node": ">=24"
  },
  "packageManager": "pnpm@12.11.2",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "postinstall": "prisma generate",
    "typecheck": "next typegen && tsc --noEmit",
    "lint": "eslint .",
    "format:check": "prettier --check .",
    "test": "vitest run",
    "test:e2e": "playwright test",
    "check": "pnpm typecheck && pnpm lint && pnpm format:check && pnpm test && pnpm build",
    "knip": "knip",
    "deps:check": "depcruise src --config .dependency-cruiser.mjs"
  },
  "dependencies": {
    "@prisma/adapter-pg": "7.10.0",
    "@prisma/client": "7.10.0",
    "@supabase/ssr": "0.12.7",
    "@supabase/supabase-js": "2.117.3",
    "@tanstack/react-query": "5.104.2",
    "babel-plugin-react-compiler": "1.0.0",
    "geist": "1.7.2",
    "ioredis": "6.0.0",
    "next": "16.4.3",
    "next-themes": "0.4.6",
    "react": "19.3.1",
    "react-dom": "19.3.1",
    "server-only": "0.0.1",
    "tw-animate-css": "1.4.0",
    "zod": "4.6.7"
  },
  "devDependencies": {
    "@axe-core/playwright": "4.13.0",
    "@commitlint/cli": "21.2.3",
    "@commitlint/config-conventional": "21.2.3",
    "@next/playwright": "16.4.3",
    "@playwright/test": "1.64.0",
    "@tailwindcss/turbopack": "4.3.3",
    "@testing-library/jest-dom": "7.0.1",
    "@testing-library/react": "16.3.3",
    "@types/node": "24.19.2",
    "@types/react": "19.3.0",
    "@types/react-dom": "19.3.0",
    "dependency-cruiser": "18.6.0",
    "eslint": "10.12.0",
    "eslint-config-next": "16.4.3",
    "eslint-plugin-jsx-a11y": "6.10.2",
    "jsdom": "30.1.2",
    "knip": "6.41.0",
    "lefthook": "2.2.1",
    "prettier": "3.9.10",
    "prettier-plugin-tailwindcss": "0.8.1",
    "prisma": "7.10.0",
    "tailwindcss": "4.3.3",
    "typescript": "6.0.3",
    "typescript-eslint": "8.71.1",
    "vitest": "5.0.4"
  }
}
```

`.nvmrc`

```text
24
```

`.prettierrc.json`

```json
{
  "printWidth": 100,
  "singleQuote": true,
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app/globals.css"
}
```

`.prettierignore`

```text
pnpm-lock.yaml
.next
src/generated
src/lib/supabase/database.types.ts
playwright-report
test-results
/audit
/.claude
/.lighthouseci
FRONTEND-MASTER.md
```

`.gitignore`

```text
/node_modules
/.next/
/out/
/build
/coverage
/playwright-report
/test-results
/src/generated
.DS_Store
*.pem
npm-debug.log*
.env*
!.env.example
*.tsbuildinfo
next-env.d.ts
/audit/report/
/audit/.work/
/audit/verdicts.json
/.lighthouseci
__pycache__/
```

`.env.example`

```bash
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SECRET_KEY=
REDIS_URL=redis://127.0.0.1:6379
# Prisma option B (A.9). Remove both lines when Prisma is not used.
DATABASE_URL=
DIRECT_URL=
```

`justfile`

```makefile
# One Redis container per project directory. Only one project's stack can run at a time: both Supabase and Redis bind fixed local ports.
redis := "redis-" + file_name(justfile_directory())

# Start the local Supabase stack and Redis, and write .env.local (run before `pnpm i`; postinstall needs DIRECT_URL).
up:
    supabase start
    docker start {{redis}} 2>/dev/null || docker run -d --name {{redis}} -p 127.0.0.1:6379:6379 redis:8-alpine
    supabase status -o env --override-name api.url=NEXT_PUBLIC_SUPABASE_URL --override-name auth.publishable_key=NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY --override-name auth.secret_key=SUPABASE_SECRET_KEY --override-name db.url=DIRECT_URL | sed -E 's/^([A-Za-z_]+)="?([^"]*)"?$/\1=\2/' | grep -E '^(NEXT_PUBLIC_SUPABASE_URL|NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY|SUPABASE_SECRET_KEY|DIRECT_URL)=' > .env.local
    echo 'NEXT_PUBLIC_SITE_URL=http://localhost:3000' >> .env.local
    echo 'REDIS_URL=redis://127.0.0.1:6379' >> .env.local
    sed -E 's/^DIRECT_URL=/DATABASE_URL=/' .env.local | grep '^DATABASE_URL=' >> .env.local

# Reset the local database to the current migrations and seed it.
reset:
    supabase db reset --local

# Regenerate database types (TS-11).
types:
    supabase gen types typescript --local > src/lib/supabase/database.types.ts

# Run the pgTAP policy tests (TEST-06).
test-db:
    supabase test db --local

# Stop the local stack (data is kept; `supabase stop --no-backup` discards it).
down:
    supabase stop
    docker stop {{redis}}
```

