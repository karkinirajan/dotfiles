### A.5 Session and DAL

`getSession` awaits `connection()` first. The Supabase auth client reads the clock, and Cache Components rejects clock reads during prerenders (NEXT-04); without the call every authenticated render logged `Route "/dashboard": Next.js encountered the unstable value Date.now() while prerendering` (seen on 2026-10-17 once real sign-in existed).

`src/lib/auth/session.ts`

```ts
import 'server-only';
import { cache } from 'react';
import { redirect } from 'next/navigation';
import { connection } from 'next/server';
import { z } from 'zod';
import { createClient } from '@/lib/supabase/server';

export type Session = Readonly<{
  userId: string;
  role: 'user' | 'admin';
  orgId: string | null;
}>;

const claimsSchema = z.object({
  sub: z.uuid(),
  app_metadata: z
    .object({
      role: z.enum(['user', 'admin']).default('user'),
      org_id: z.uuid().nullish(),
    })
    .default({ role: 'user' }),
});

/** Null when unauthenticated. Use in Server Actions and Route Handlers. */
export const getSession = cache(async (): Promise<Session | null> => {
  await connection(); // the auth client reads the clock; keep it out of prerenders (NEXT-04)
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getClaims();
  if (error || !data?.claims) return null;

  const parsed = claimsSchema.safeParse(data.claims);
  if (!parsed.success) return null;

  return {
    userId: parsed.data.sub,
    role: parsed.data.app_metadata.role,
    orgId: parsed.data.app_metadata.org_id ?? null,
  };
});

/** Redirects when unauthenticated. Use in Server Components and DAL reads. */
export async function verifySession(): Promise<Session> {
  const session = await getSession();
  if (!session) redirect('/login');
  return session;
}
```

`src/features/projects/queries.ts`

```ts
import 'server-only';
import { cache } from 'react';
import { verifySession } from '@/lib/auth/session';
import { createClient } from '@/lib/supabase/server';
import { requestLogger } from '@/lib/logger';

export type ProjectDTO = Readonly<{ id: string; name: string; ownerId: string; createdAt: string }>;

export const getProject = cache(async (id: string): Promise<ProjectDTO | null> => {
  await verifySession();
  const supabase = await createClient(); // user-scoped client: RLS enforces row access

  const { data, error } = await supabase
    .from('projects')
    .select('id, name, owner_id, created_at')
    .eq('id', id)
    .maybeSingle();

  if (error) {
    (await requestLogger()).error({ code: error.code, projectId: id }, 'project query failed');
    throw new Error('PROJECT_QUERY_FAILED');
  }
  if (!data) return null;

  return { id: data.id, name: data.name, ownerId: data.owner_id, createdAt: data.created_at };
});
```

When the data access model is Prisma (PRISMA-01 option B), RLS does not apply. Add the ownership predicate to the query (`where: { id, ownerId: session.userId }`) and keep the `verifySession` result in use.

