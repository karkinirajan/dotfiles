### A.6 Server Action template

`z.object` strips unknown keys, so it is the right choice for raw `FormData`: do not use `.strict()` there, because Next adds internal `$ACTION_*` fields for progressive enhancement. Use `.strict()` for JSON bodies. RLS hides rows the user may not touch, so "missing" and "not yours" look identical; that is intended. Non-idempotent creates (orders, payments) additionally take an idempotency key generated once per form mount and enforced by a unique column (REACT-17).

`src/lib/action-result.ts`

```ts
export type ActionErrorCode =
  'unauthenticated' | 'forbidden' | 'invalid' | 'rate_limited' | 'not_found' | 'server_error';

export type ActionResult<T> =
  | { ok: true; data: T }
  | {
      ok: false;
      code: ActionErrorCode;
      fieldErrors?: Record<string, string[] | undefined>;
      /** Non-secret field values to redisplay after a failed submit (REACT-16). Never a password. */
      values?: Record<string, string>;
    };
```

`src/features/projects/actions.ts`

```ts
'use server';

import { updateTag } from 'next/cache';
import { z } from 'zod';
import type { ActionResult } from '@/lib/action-result';
import { getSession } from '@/lib/auth/session';
import { requestLogger } from '@/lib/logger';
import { rateLimit } from '@/lib/rate-limit';
import { createClient } from '@/lib/supabase/server';

const renameProjectSchema = z.object({
  projectId: z.uuid(),
  name: z.string().trim().min(1).max(120),
});

export async function renameProject(
  _previous: ActionResult<{ id: string }> | null,
  formData: FormData,
): Promise<ActionResult<{ id: string }>> {
  const started = performance.now();
  const log = await requestLogger();

  const session = await getSession();
  if (!session) return { ok: false, code: 'unauthenticated' };

  const limit = await rateLimit({
    key: `rename-project:${session.userId}`,
    limit: 20,
    windowSeconds: 60,
  });
  if (!limit.ok) return { ok: false, code: 'rate_limited' };

  const parsed = renameProjectSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return { ok: false, code: 'invalid', fieldErrors: z.flattenError(parsed.error).fieldErrors };
  }
  const { projectId, name } = parsed.data;

  const supabase = await createClient();
  const { data, error } = await supabase
    .from('projects')
    .update({ name })
    .eq('id', projectId)
    .select('id')
    .maybeSingle();

  if (error) {
    log.error(
      { action: 'renameProject', code: error.code, userId: session.userId },
      'action failed',
    );
    return { ok: false, code: 'server_error' };
  }
  if (!data) return { ok: false, code: 'not_found' };

  updateTag(`project:${projectId}`);

  log.info(
    { action: 'renameProject', outcome: 'ok', durationMs: Math.round(performance.now() - started) },
    'action completed',
  );
  return { ok: true, data: { id: data.id } };
}
```

