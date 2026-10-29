### A.3 Validated environment (`lib/env/public.ts` and `lib/env/server.ts`)

Public values are read as literal `process.env.NEXT_PUBLIC_*` references so the bundler can inline them. `REDIS_URL` is for the rate limiter (A.15); drop it if a platform firewall does the limiting. `DATABASE_URL` and `DIRECT_URL` are for Prisma option B (A.9); drop them otherwise. A missing variable fails the build or boot loudly. That is the point.

`src/lib/env/public.ts`

```ts
import { z } from 'zod';

const publicSchema = z.object({
  NEXT_PUBLIC_SITE_URL: z.url(),
  NEXT_PUBLIC_SUPABASE_URL: z.url(),
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: z.string().startsWith('sb_publishable_'),
});

// Literal property access is required: the bundler inlines NEXT_PUBLIC_* by exact name.
export const publicEnv = publicSchema.parse({
  NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
  NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
});
```

`src/lib/env/server.ts`

```ts
import 'server-only';
import { z } from 'zod';

const serverSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  SUPABASE_SECRET_KEY: z.string().startsWith('sb_secret_'),
  REDIS_URL: z.url(),
  // Prisma option B only:
  DATABASE_URL: z.url(),
  DIRECT_URL: z.url(),
});

export const serverEnv = serverSchema.parse(process.env);
```
