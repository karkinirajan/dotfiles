# Appendix A.7–A.9: Tailwind tokens, components.json, Prisma 7

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index. Every file below was exercised against the exact versions in `01-versions-and-watch.md` §1.1 — see `appendix-a1-a6-core.md`'s header note for the full verification method.

## A.7 `globals.css` (Tailwind v4 tokens, shadcn compatible)

Generate the base file with the shadcn CLI, then align it with this structure. Contrast was computed with the WCAG relative-luminance formula on these exact OKLCH values, alpha composited over the background. Every text pair in the file clears 4.5:1 in both themes. Two details differ from stock shadcn themes: `--input` is a mid-gray, because a border of `oklch(0.922 0 0)` measures 1.26:1 against white and fails the 3:1 non-text rule for control boundaries, and the base layer uses `outline-ring` at full opacity, because `outline-ring/50` measures 2.14:1 in light and 2.75:1 in dark, below the 3:1 focus-indicator floor. `--border` stays light because it draws decorative dividers only.

| Pair (foreground on background) | Need | Light | Dark |
|---|---|---|---|
| `--foreground` on `--background` | 4.5:1 | 19.79 | 18.96 |
| `--muted-foreground` on `--background` | 4.5:1 | 6.00 | 7.98 |
| `--muted-foreground` on `--muted` | 4.5:1 | 5.50 | 6.09 |
| `--primary-foreground` on `--primary` | 4.5:1 | 17.16 | 14.22 |
| `--destructive-foreground` on `--destructive` | 4.5:1 | 5.20 | 6.79 |
| `--success-foreground` on `--success` | 4.5:1 | 5.37 | 8.54 |
| `--warning-foreground` on `--warning` | 4.5:1 | 9.53 | 10.22 |
| `--info-foreground` on `--info` | 4.5:1 | 5.47 | 7.92 |
| `--ring` on `--background` | 3:1 | 6.00 | 7.98 |
| `--input` on `--background` | 3:1 | 3.64 | 4.62 |
| `--input` on `--card` | 3:1 | 3.64 | 4.18 |

Recompute the table whenever a token changes (STYLE-03). `color-scheme` follows the theme class, so form controls and scrollbars match the active theme even when the user overrides the system preference. The font variables come from `geist` (`--font-geist-sans`, `--font-geist-mono`) as set in A.16 (`appendix-a16-a18-shell-tests-repo.md`).

`src/app/globals.css`

```css
@import 'tailwindcss';
@import 'tw-animate-css';

@custom-variant dark (&:is(.dark *));

:root {
  color-scheme: light;
  --radius: 0.625rem;

  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.5 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.55 0.22 27);
  --destructive-foreground: oklch(0.985 0 0);
  --success: oklch(0.5 0.15 150);
  --success-foreground: oklch(0.985 0 0);
  --warning: oklch(0.8 0.17 80);
  --warning-foreground: oklch(0.2 0.03 80);
  --info: oklch(0.52 0.2 260);
  --info-foreground: oklch(0.985 0 0);
  --border: oklch(0.922 0 0);
  --input: oklch(0.62 0 0);
  --ring: oklch(0.5 0 0);
}

.dark {
  color-scheme: dark;
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.72 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.7 0.19 22);
  --destructive-foreground: oklch(0.145 0 0);
  --success: oklch(0.72 0.17 150);
  --success-foreground: oklch(0.145 0 0);
  --warning: oklch(0.82 0.16 80);
  --warning-foreground: oklch(0.2 0.03 80);
  --info: oklch(0.72 0.14 260);
  --info-foreground: oklch(0.145 0 0);
  --border: oklch(1 0 0 / 12%);
  --input: oklch(0.58 0 0);
  --ring: oklch(0.72 0 0);
}

@theme inline {
  --font-sans: var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif;
  --font-mono: var(--font-geist-mono), ui-monospace, monospace;

  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-success: var(--success);
  --color-success-foreground: var(--success-foreground);
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
  --color-info: var(--info);
  --color-info-foreground: var(--info-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);

  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}

@layer base {
  * {
    @apply border-border outline-ring;
  }
  body {
    @apply bg-background text-foreground antialiased;
  }
}
```

## A.8 `components.json` invariants

Create the file with `pnpm dlx shadcn@latest init` and choose the base deliberately (UI-01, in `08-styling-ui.md`); `--base` accepts `base`, `radix`, or `aria`. The base is encoded in the `style` value, which is prefixed `radix-`, `base-`, or `aria-` followed by a style name, so do not hand-write it. After init, check these fields against the published schema (`https://ui.shadcn.com/schema.json`):

- `tailwind.config` is an empty string (Tailwind v4 has no JS config).
- `tailwind.css` points to `src/app/globals.css` and `tailwind.cssVariables` is `true`.
- `rsc` is `true` and `tsx` is `true`.
- `aliases` maps `components` and `utils` (required) and `ui`, `lib`, `hooks` (optional) to the paths in `03-structure.md`.
- `iconLibrary` is `lucide` (the schema accepts any string).
- No `tailwind.config.*` file exists in the repository.

## A.9 Prisma 7 (only when PRISMA-01 selects option B)

The datasource URL lives in `prisma.config.ts`, not in `schema.prisma`. Prisma 7 does not load `.env` files, so the config loads `.env.local` when it exists; CI supplies real variables. `postinstall` runs `prisma generate`, which needs `DIRECT_URL` at install time (`just up` writes it; A.18, in `appendix-a16-a18-shell-tests-repo.md`). The generated client is not committed (`src/generated` is gitignored). Seeding no longer runs automatically; run `prisma db seed`. Supabase connection details are in PRISMA-03 (`07-data-layer.md`).

`prisma/schema.prisma`

```prisma
generator client {
  provider = "prisma-client"
  output   = "../src/generated/prisma"
}

datasource db {
  provider = "postgresql"
}

model Project {
  id        String   @id @default(uuid()) @db.Uuid
  name      String
  ownerId   String   @map("owner_id") @db.Uuid
  createdAt DateTime @default(now()) @map("created_at")

  @@index([ownerId])
  @@map("projects")
}
```

`prisma.config.ts`

```ts
import { existsSync } from 'node:fs';
import { defineConfig, env } from 'prisma/config';

// Prisma 7 does not load .env files. Load the local file when present; CI provides real variables.
if (existsSync('.env.local')) process.loadEnvFile('.env.local');

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: { path: 'prisma/migrations' },
  datasource: { url: env('DIRECT_URL') },
});
```

`src/lib/db/client.ts`

```ts
import 'server-only';
import { PrismaPg } from '@prisma/adapter-pg';
import { PrismaClient } from '@/generated/prisma/client';
import { serverEnv } from '@/lib/env/server';

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

function createPrismaClient(): PrismaClient {
  const adapter = new PrismaPg({
    connectionString: serverEnv.DATABASE_URL,
    max: serverEnv.NODE_ENV === 'production' ? 5 : 3,
    connectionTimeoutMillis: 5_000,
    idleTimeoutMillis: 30_000,
  });
  return new PrismaClient({ adapter });
}

export const db = globalForPrisma.prisma ?? createPrismaClient();

if (serverEnv.NODE_ENV !== 'production') globalForPrisma.prisma = db;
```
