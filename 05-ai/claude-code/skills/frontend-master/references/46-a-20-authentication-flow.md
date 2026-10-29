### A.20 Authentication flow

Email and password sign-in and sign-out that follow ADR 0001 (A.19): the Server Action signs in, the Supabase SSR helper writes the session cookies through `hardenCookie` (A.4), and the browser never holds a readable token (SEC-10). The action validates with the same Zod schema the form uses (REACT-14), rate limits per IP and per account with the email hashed so no address reaches Redis (SEC-06), answers with one generic message for an unknown account and a wrong password (SEC-15), records `sign_in` and `sign_out` in `audit_log` (OBS-07), and redirects only to a same-origin path (SEC-11). A failed submit keeps the email and never echoes the password (REACT-16).

`tests/e2e/auth.spec.ts` runs against the production build and the local Supabase stack (`just up` writes the `.env.local` it reads). It proves the flow in a real browser: the redirect from a protected page and back, `HttpOnly`, `Secure` and `SameSite=Lax` on every `sb-` cookie, no token in `document.cookie` or web storage, the generic failure message, field errors wired with `aria-describedby`, an external `next` ignored, and sign-out clearing the session.

This is the minimum a project needs to ship the cookie model. Sign-up, password reset, OAuth or OTP, CAPTCHA and MFA (SB-08) are not included; add them with the same action structure and the same tests.

`src/lib/security/redirect.ts`

```ts
import type { Route } from 'next';

/**
 * Returns a same-origin relative path, or `fallback` for anything else (SEC-11).
 * Rejects absolute URLs, protocol-relative URLs (`//host`), and backslash tricks. The path is
 * parsed with the URL parser, so tabs and newlines that browsers strip cannot smuggle a host.
 */
export function safeRedirectPath(value: unknown, fallback: Route = '/dashboard'): Route {
  if (typeof value !== 'string' || !value.startsWith('/') || value.includes('\\')) return fallback;
  try {
    const url = new URL(value, 'http://localhost');
    if (url.origin !== 'http://localhost') return fallback;
    // The one cast: the string is a same-origin path by construction, but typed routes cannot know it.
    return `${url.pathname}${url.search}${url.hash}` as Route;
  } catch (error) {
    if (error instanceof TypeError) return fallback;
    throw error;
  }
}
```

`src/lib/security/redirect.test.ts`

```ts
import { describe, expect, it } from 'vitest';
import { safeRedirectPath } from '@/lib/security/redirect';

describe('safeRedirectPath', () => {
  it.each([
    ['/dashboard', '/dashboard'],
    ['/settings?tab=billing', '/settings?tab=billing'],
    ['/a/b#section', '/a/b#section'],
  ])('keeps the same-origin path %s', (input, expected) => {
    expect(safeRedirectPath(input)).toBe(expected);
  });

  it.each([
    'https://evil.example',
    '//evil.example',
    '/\\evil.example',
    '/\t/evil.example',
    '/\n/evil.example',
    'javascript:alert(1)',
    'dashboard',
    '',
  ])('falls back for %j', (input) => {
    expect(safeRedirectPath(input)).toBe('/dashboard');
  });

  it('falls back for non-strings', () => {
    expect(safeRedirectPath(undefined)).toBe('/dashboard');
    expect(safeRedirectPath(['/a'])).toBe('/dashboard');
  });

  it('uses the caller fallback', () => {
    expect(safeRedirectPath('//x', '/login')).toBe('/login');
  });
});
```

`src/lib/audit.ts`

```ts
import 'server-only';
import type { SupabaseClient } from '@supabase/supabase-js';
import { requestLogger } from '@/lib/logger';
import type { Database } from '@/lib/supabase/database.types';

/**
 * Appends a security event to `audit_log` through the SECURITY DEFINER function (OBS-07).
 * The caller's JWT identifies the actor. A failure is logged and never blocks the user.
 */
export async function recordAuditEvent(
  supabase: SupabaseClient<Database>,
  action: string,
  detail: Record<string, string | number | boolean | null> = {},
): Promise<void> {
  const { error } = await supabase.rpc('record_audit_event', {
    p_action: action,
    p_detail: detail,
  });
  if (error)
    (await requestLogger()).error({ code: error.code, action }, 'audit event not recorded');
}
```

`src/features/auth/schemas.ts`

```ts
import { z } from 'zod';

/** Shared by the form (inline hints) and the Server Action (authoritative validation). */
export const signInSchema = z.object({
  email: z.email('Enter a valid email address.').max(254),
  password: z.string().min(1, 'Enter your password.').max(256),
  next: z.string().max(512).optional(),
});
```

`src/features/auth/actions.ts`

```ts
'use server';

import { createHash } from 'node:crypto';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import { z } from 'zod';
import { signInSchema } from '@/features/auth/schemas';
import type { ActionResult } from '@/lib/action-result';
import { recordAuditEvent } from '@/lib/audit';
import { getSession } from '@/lib/auth/session';
import { requestLogger } from '@/lib/logger';
import { rateLimit } from '@/lib/rate-limit';
import { safeRedirectPath } from '@/lib/security/redirect';
import { createClient } from '@/lib/supabase/server';

/** First hop of x-forwarded-for. Only trustworthy behind a proxy that sets it (Vercel, ALB). */
function clientIp(requestHeaders: Headers): string {
  const first = requestHeaders.get('x-forwarded-for')?.split(',')[0]?.trim();
  if (!first) return 'unknown';
  return first;
}

function sha256(value: string): string {
  return createHash('sha256').update(value).digest('hex');
}

export async function signIn(
  _previous: ActionResult<null> | null,
  formData: FormData,
): Promise<ActionResult<null>> {
  const started = performance.now();
  const log = await requestLogger();

  const parsed = signInSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    const rawEmail = formData.get('email');
    return {
      ok: false,
      code: 'invalid',
      fieldErrors: z.flattenError(parsed.error).fieldErrors,
      values: { email: typeof rawEmail === 'string' ? rawEmail : '' },
    };
  }
  const { email, password, next } = parsed.data;

  // Per IP and per account, so one address cannot be guessed from many IPs (SEC-06).
  const ip = clientIp(await headers());
  const [byIp, byEmail] = await Promise.all([
    rateLimit({ key: `sign-in:ip:${ip}`, limit: 20, windowSeconds: 60 }),
    rateLimit({ key: `sign-in:email:${sha256(email.toLowerCase())}`, limit: 5, windowSeconds: 60 }),
  ]);
  if (!byIp.ok || !byEmail.ok) return { ok: false, code: 'rate_limited', values: { email } };

  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) {
    // One generic outcome for unknown account and wrong password (SEC-15). The reason stays in the log.
    log.warn({ action: 'signIn', outcome: 'rejected', code: error.code }, 'sign-in rejected');
    return { ok: false, code: 'unauthenticated', values: { email } };
  }

  await recordAuditEvent(supabase, 'sign_in');
  log.info(
    { action: 'signIn', outcome: 'ok', durationMs: Math.round(performance.now() - started) },
    'action completed',
  );
  redirect(safeRedirectPath(next));
}

export async function signOut(): Promise<void> {
  const session = await getSession();
  const supabase = await createClient();
  if (session) await recordAuditEvent(supabase, 'sign_out');
  const { error } = await supabase.auth.signOut();
  if (error)
    (await requestLogger()).error({ action: 'signOut', code: error.code }, 'sign-out failed');
  redirect('/login');
}
```

`src/features/auth/actions.test.ts`

```ts
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { signInWithPassword, signOutClient, rpc, getSession, rateLimit, redirect } = vi.hoisted(
  () => ({
    signInWithPassword: vi.fn(),
    signOutClient: vi.fn(),
    rpc: vi.fn(),
    getSession: vi.fn(),
    rateLimit: vi.fn(),
    redirect: vi.fn((path: string) => {
      throw new Error(`NEXT_REDIRECT:${path}`);
    }),
  }),
);

vi.mock('next/navigation', () => ({ redirect }));
vi.mock('next/headers', () => ({
  headers: () => Promise.resolve(new Headers({ 'x-forwarded-for': '203.0.113.9, 10.0.0.1' })),
}));
vi.mock('@/lib/auth/session', () => ({ getSession }));
vi.mock('@/lib/rate-limit', () => ({ rateLimit }));
vi.mock('@/lib/logger', () => {
  const log = { info: vi.fn(), warn: vi.fn(), error: vi.fn() };
  return { logger: log, requestLogger: () => Promise.resolve(log) };
});
vi.mock('@/lib/supabase/server', () => ({
  createClient: () =>
    Promise.resolve({ auth: { signInWithPassword, signOut: signOutClient }, rpc }),
}));

import { signIn, signOut } from '@/features/auth/actions';

function form(fields: Record<string, string>): FormData {
  const data = new FormData();
  for (const [key, value] of Object.entries(fields)) data.set(key, value);
  return data;
}

const GOOD = { email: 'user@example.test', password: 'correct horse' };

describe('signIn', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    rateLimit.mockResolvedValue({ ok: true, remaining: 4, retryAfterSeconds: 0 });
    signInWithPassword.mockResolvedValue({ error: null });
    rpc.mockResolvedValue({ error: null });
  });

  it('returns field errors and keeps the email for invalid input', async () => {
    const result = await signIn(null, form({ email: 'not-an-email', password: '' }));
    expect(result).toMatchObject({ ok: false, code: 'invalid', values: { email: 'not-an-email' } });
    expect(signInWithPassword).not.toHaveBeenCalled();
  });

  it('never echoes the password back', async () => {
    const result = await signIn(null, form({ email: 'bad', password: 'secret-value' }));
    expect(JSON.stringify(result)).not.toContain('secret-value');
  });

  it('is rate limited per IP and per account before it calls the auth service', async () => {
    rateLimit.mockResolvedValueOnce({ ok: true, remaining: 1, retryAfterSeconds: 0 });
    rateLimit.mockResolvedValueOnce({ ok: false, remaining: 0, retryAfterSeconds: 30 });
    const result = await signIn(null, form(GOOD));
    expect(result).toMatchObject({ ok: false, code: 'rate_limited' });
    expect(rateLimit).toHaveBeenCalledWith(
      expect.objectContaining({ key: 'sign-in:ip:203.0.113.9' }),
    );
    expect(signInWithPassword).not.toHaveBeenCalled();
  });

  it('does not put the email address into the rate limit key', async () => {
    await signIn(null, form(GOOD)).catch(() => undefined);
    const keys = rateLimit.mock.calls.map(([arg]) => (arg as { key: string }).key);
    expect(keys.join(' ')).not.toContain('user@example.test');
  });

  it('gives one generic answer for a rejected sign-in (unauthenticated)', async () => {
    signInWithPassword.mockResolvedValue({ error: { code: 'invalid_credentials' } });
    const result = await signIn(null, form(GOOD));
    expect(result).toEqual({ ok: false, code: 'unauthenticated', values: { email: GOOD.email } });
    expect(rpc).not.toHaveBeenCalled();
  });

  it('records the audit event and redirects to the dashboard on success', async () => {
    await expect(signIn(null, form(GOOD))).rejects.toThrow('NEXT_REDIRECT:/dashboard');
    expect(rpc).toHaveBeenCalledWith('record_audit_event', { p_action: 'sign_in', p_detail: {} });
  });

  it('follows a safe next path and ignores an external one', async () => {
    await expect(signIn(null, form({ ...GOOD, next: '/settings' }))).rejects.toThrow(
      'NEXT_REDIRECT:/settings',
    );
    await expect(signIn(null, form({ ...GOOD, next: 'https://evil.example' }))).rejects.toThrow(
      'NEXT_REDIRECT:/dashboard',
    );
  });
});

describe('signOut', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    rpc.mockResolvedValue({ error: null });
    signOutClient.mockResolvedValue({ error: null });
  });

  it('records the event, ends the session and redirects to the login page', async () => {
    getSession.mockResolvedValue({ userId: 'u1', role: 'user', orgId: null });
    await expect(signOut()).rejects.toThrow('NEXT_REDIRECT:/login');
    expect(rpc).toHaveBeenCalledWith('record_audit_event', { p_action: 'sign_out', p_detail: {} });
    expect(signOutClient).toHaveBeenCalledOnce();
  });

  it('still redirects when nobody is signed in (unauthenticated)', async () => {
    getSession.mockResolvedValue(null);
    await expect(signOut()).rejects.toThrow('NEXT_REDIRECT:/login');
    expect(rpc).not.toHaveBeenCalled();
  });
});
```

`src/features/auth/login-form.tsx`

```tsx
'use client';

import { useActionState } from 'react';
import { useFormStatus } from 'react-dom';
import { signIn } from '@/features/auth/actions';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="inline-flex min-h-11 items-center justify-center rounded-md bg-primary px-4 text-primary-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:opacity-60"
    >
      {pending ? 'Signing in…' : 'Sign in'}
    </button>
  );
}

const FORM_ERRORS = {
  unauthenticated: 'The email or password is not correct.',
  rate_limited: 'Too many attempts. Wait a minute and try again.',
  server_error: 'Something went wrong on our side. Try again.',
} as const;

export function LoginForm({ next }: Readonly<{ next?: string }>) {
  const [state, formAction] = useActionState(signIn, null);
  const failure = state?.ok === false ? state : null;
  const emailError = failure?.fieldErrors?.email?.[0];
  const passwordError = failure?.fieldErrors?.password?.[0];
  const formError =
    failure && failure.code in FORM_ERRORS
      ? FORM_ERRORS[failure.code as keyof typeof FORM_ERRORS]
      : null;

  return (
    <form action={formAction} className="flex max-w-sm flex-col gap-4" noValidate>
      {next ? <input type="hidden" name="next" value={next} /> : null}

      <div className="flex flex-col gap-1">
        <label htmlFor="email" className="font-medium">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          defaultValue={failure?.values?.email}
          aria-invalid={emailError ? true : undefined}
          aria-describedby={emailError ? 'email-error' : undefined}
          className="min-h-11 rounded-md border border-input bg-background px-3"
        />
        {emailError ? (
          <p id="email-error" className="text-sm text-destructive">
            {emailError}
          </p>
        ) : null}
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="password" className="font-medium">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          aria-invalid={passwordError ? true : undefined}
          aria-describedby={passwordError ? 'password-error' : undefined}
          className="min-h-11 rounded-md border border-input bg-background px-3"
        />
        {passwordError ? (
          <p id="password-error" className="text-sm text-destructive">
            {passwordError}
          </p>
        ) : null}
      </div>

      {formError ? (
        <p role="alert" className="text-sm text-destructive">
          {formError}
        </p>
      ) : null}

      <SubmitButton />
    </form>
  );
}
```

`src/features/auth/login-form.test.tsx`

```tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('@/features/auth/actions', () => ({ signIn: vi.fn() }));

import { LoginForm } from '@/features/auth/login-form';

describe('LoginForm', () => {
  it('labels both fields and exposes a submit button', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText('Email')).toHaveAttribute('autocomplete', 'email');
    expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'password');
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeEnabled();
  });

  it('carries the validated next path in a hidden field', () => {
    const { container } = render(<LoginForm next="/settings" />);
    expect(container.querySelector('input[name="next"]')).toHaveValue('/settings');
  });
});
```

`tests/e2e/auth.spec.ts`

```ts
import { randomUUID } from 'node:crypto';
import { createClient } from '@supabase/supabase-js';
import { expect, test, type Page } from '@playwright/test';

test.describe.configure({ mode: 'serial' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const secretKey = process.env.SUPABASE_SECRET_KEY;

function adminClient() {
  if (!supabaseUrl || !secretKey) {
    throw new Error(
      'auth.spec.ts needs NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SECRET_KEY (run `just up`).',
    );
  }
  return createClient(supabaseUrl, secretKey, { auth: { persistSession: false } });
}

const email = `e2e-${randomUUID()}@example.test`;
const password = `Pw-${randomUUID()}`;
let userId = '';

test.beforeAll(async () => {
  const { data, error } = await adminClient().auth.admin.createUser({
    email,
    password,
    email_confirm: true,
  });
  if (error) throw error;
  userId = data.user.id;
});

test.afterAll(async () => {
  if (userId) await adminClient().auth.admin.deleteUser(userId);
});

async function signIn(page: Page, next?: string) {
  await page.goto(next ? `/login?next=${encodeURIComponent(next)}` : '/login');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
}

test('an anonymous visitor is sent to the login page and back after signing in', async ({
  page,
}) => {
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/\/login\?next=%2Fdashboard$/);
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText(`Signed in as ${userId}`)).toBeVisible();
});

test('session cookies are HttpOnly, SameSite=Lax and Secure, and JavaScript cannot read them (SEC-10)', async ({
  page,
  context,
}) => {
  await signIn(page);
  await expect(page).toHaveURL(/\/dashboard$/);

  const session = (await context.cookies()).filter((c) => c.name.startsWith('sb-'));
  expect(session.length).toBeGreaterThan(0);
  for (const cookie of session) {
    expect(cookie, cookie.name).toMatchObject({ httpOnly: true, sameSite: 'Lax', secure: true });
  }
  expect(await page.evaluate(() => document.cookie)).not.toContain('sb-');
  expect(
    await page.evaluate(() =>
      JSON.stringify([Object.entries(localStorage), Object.entries(sessionStorage)]),
    ),
  ).not.toMatch(/access_token|refresh_token/);
});

test('a wrong password and an unknown account get the same generic answer (SEC-15)', async ({
  page,
}) => {
  for (const address of [email, `nobody-${randomUUID()}@example.test`]) {
    await page.goto('/login');
    await page.getByLabel('Email').fill(address);
    await page.getByLabel('Password').fill('definitely-wrong');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(
      page.getByRole('alert').filter({ hasText: 'The email or password is not correct.' }),
    ).toBeVisible();
    await expect(page).toHaveURL(/\/login$/);
  }
});

test('invalid input shows field errors tied to the inputs and keeps the email (REACT-16)', async ({
  page,
}) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('not-an-email');
  await page.getByLabel('Password').fill('x');
  await page.getByRole('button', { name: 'Sign in' }).click();
  const field = page.getByLabel('Email');
  await expect(field).toHaveAttribute('aria-invalid', 'true');
  await expect(field).toHaveAttribute('aria-describedby', 'email-error');
  await expect(page.locator('#email-error')).toHaveText('Enter a valid email address.');
  await expect(field).toHaveValue('not-an-email');
});

test('an external next parameter never leaves the site (SEC-11)', async ({ page, baseURL }) => {
  await signIn(page, 'https://evil.example/phish');
  await expect(page).toHaveURL(`${baseURL}/dashboard`);
});

test('signing out ends the session', async ({ page, context }) => {
  await signIn(page);
  await expect(page).toHaveURL(/\/dashboard$/);
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page).toHaveURL(/\/login$/);
  expect(
    (await context.cookies()).filter((c) => c.name.startsWith('sb-') && c.value !== ''),
  ).toEqual([]);
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/\/login/);
});
```
