### A.9 Prisma 7 (only when PRISMA-01 selects option B)

The datasource URL lives in `prisma.config.ts`, not in `schema.prisma`. Prisma 7 does not load `.env` files, so the config loads `.env.local` when it exists; CI supplies real variables. `postinstall` runs `prisma generate`, which needs `DIRECT_URL` at install time (`just up` writes it; A.18). The generated client is not committed (`src/generated` is gitignored). Seeding no longer runs automatically; run `prisma db seed`. Supabase connection details are in PRISMA-03.

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

