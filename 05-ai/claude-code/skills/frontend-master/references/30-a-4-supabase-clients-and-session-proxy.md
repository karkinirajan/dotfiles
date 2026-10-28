### A.4 Supabase clients and session proxy

`updateSession` takes the request headers that `proxy.ts` built (nonce and CSP) and forwards them to the render. When Supabase refreshes the session, `setAll` receives the cache headers as its second argument; they go on the response so a CDN never caches a response that carries auth cookies. The redirect copies both the cookies and those headers. The redirect is a convenience: the DAL (A.5) and RLS still enforce access (SEC-02).

Supabase's SSR helper sets `httpOnly: false` and omits `Secure` on its cookies (verified against `@supabase/ssr` 0.12.7 and a local Supabase 2.121.0 auth server on 2026-10-17), because its browser client has to read the session in JavaScript. SEC-10 forbids that, so every `setAll` below passes its options through `hardenCookie`, and the browser client has no session (ADR 0001, A.19).

`src/lib/supabase/cookie-options.ts`

```ts
import type { CookieOptions } from '@supabase/ssr';

/**
 * @supabase/ssr sets `httpOnly: false` and omits `Secure`, so any script on the page can read the
 * session cookie. Every `setAll` in this repo passes its options through here (SEC-10, ADR 0001).
 */
export function hardenCookie(options: CookieOptions): CookieOptions {
  return {
    ...options,
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
  };
}
```

`src/lib/supabase/cookie-options.test.ts`

```ts
import { describe, expect, it } from 'vitest';
import { hardenCookie } from '@/lib/supabase/cookie-options';

describe('hardenCookie', () => {
  it('forces HttpOnly over the library default', () => {
    expect(hardenCookie({ httpOnly: false }).httpOnly).toBe(true);
  });

  it('keeps path and lifetime from the library', () => {
    const result = hardenCookie({ path: '/', maxAge: 60 });
    expect(result.path).toBe('/');
    expect(result.maxAge).toBe(60);
  });

  it('never weakens SameSite below lax', () => {
    expect(hardenCookie({ sameSite: 'none' }).sameSite).toBe('lax');
  });
});
```

`src/lib/supabase/client.ts`

```ts
import { createBrowserClient } from '@supabase/ssr';
import { publicEnv } from '@/lib/env/public';
import type { Database } from '@/lib/supabase/database.types';

export function createClient() {
  return createBrowserClient<Database>(
    publicEnv.NEXT_PUBLIC_SUPABASE_URL,
    publicEnv.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
  );
}
```

`src/lib/supabase/server.ts`

```ts
import 'server-only';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import { publicEnv } from '@/lib/env/public';
import { hardenCookie } from '@/lib/supabase/cookie-options';
import type { Database } from '@/lib/supabase/database.types';

export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient<Database>(
    publicEnv.NEXT_PUBLIC_SUPABASE_URL,
    publicEnv.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          try {
            for (const { name, value, options } of cookiesToSet) {
              cookieStore.set(name, value, hardenCookie(options));
            }
          } catch {
            // Server Components cannot write cookies. proxy.ts refreshes the session on every request.
          }
        },
      },
    },
  );
}
```

`src/lib/supabase/admin.ts`

```ts
import 'server-only';
import { createClient } from '@supabase/supabase-js';
import { publicEnv } from '@/lib/env/public';
import { serverEnv } from '@/lib/env/server';
import type { Database } from '@/lib/supabase/database.types';

export const supabaseAdmin = createClient<Database>(
  publicEnv.NEXT_PUBLIC_SUPABASE_URL,
  serverEnv.SUPABASE_SECRET_KEY,
  { auth: { persistSession: false, autoRefreshToken: false } },
);
```

`src/lib/supabase/proxy.ts`

```ts
import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';
import { publicEnv } from '@/lib/env/public';
import { hardenCookie } from '@/lib/supabase/cookie-options';
import type { Database } from '@/lib/supabase/database.types';

const PROTECTED_PREFIXES = ['/dashboard', '/settings', '/admin'] as const;

const REQUEST_ID_PATTERN = /^[A-Za-z0-9_-]{8,64}$/;

/** Keeps a caller's id only when it cannot carry log-injection characters (newlines, quotes). */
function resolveRequestId(inbound: string | null): string {
  return inbound && REQUEST_ID_PATTERN.test(inbound) ? inbound : crypto.randomUUID();
}

function isProtected(pathname: string): boolean {
  return PROTECTED_PREFIXES.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}

/**
 * Refreshes the Supabase session and returns the response that carries the refreshed cookies.
 * `requestHeaders` are forwarded to the render (nonce, CSP) and must be the same object the caller built.
 * Every request gets an id (DAL-06): a well-formed inbound `x-request-id` is kept, anything else is replaced.
 */
export async function updateSession(
  request: NextRequest,
  requestHeaders: Headers,
): Promise<NextResponse> {
  const requestId = resolveRequestId(request.headers.get('x-request-id'));
  requestHeaders.set('x-request-id', requestId);
  let response = NextResponse.next({ request: { headers: requestHeaders } });

  const supabase = createServerClient<Database>(
    publicEnv.NEXT_PUBLIC_SUPABASE_URL,
    publicEnv.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet, cacheHeaders) => {
          for (const { name, value } of cookiesToSet) request.cookies.set(name, value);
          requestHeaders.set('cookie', request.headers.get('cookie') ?? '');
          response = NextResponse.next({ request: { headers: requestHeaders } });
          for (const { name, value, options } of cookiesToSet)
            response.cookies.set(name, value, hardenCookie(options));
          // A response that sets auth cookies must never be cached by a CDN or proxy.
          for (const [key, value] of Object.entries(cacheHeaders)) response.headers.set(key, value);
        },
      },
    },
  );

  // Run nothing between createServerClient and getClaims.
  const { data } = await supabase.auth.getClaims();

  if (!data?.claims && isProtected(request.nextUrl.pathname)) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = '/login';
    loginUrl.search = '';
    loginUrl.searchParams.set('next', request.nextUrl.pathname); // relative path only; validate on use (SEC-11)
    const redirect = NextResponse.redirect(loginUrl);
    for (const cookie of response.cookies.getAll()) redirect.cookies.set(cookie);
    for (const [key, value] of response.headers) {
      if (['cache-control', 'expires', 'pragma'].includes(key)) redirect.headers.set(key, value);
    }
    redirect.headers.set('x-request-id', requestId);
    return redirect;
  }

  response.headers.set('x-request-id', requestId);
  return response;
}
```

`src/lib/supabase/database.types.ts` is generated by `just types` (TS-11), never edited by hand. The file below is the real output of `supabase gen types typescript --local` (CLI 2.121.0) for the reference migration in A.19, so the templates compile before your first generation. Regenerate it after every migration; the audit kit's `types-drift` check fails when it differs from the database.

`src/lib/supabase/database.types.ts`

```ts

export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[]

export type Database = {
  
  "graphql_public": {
          Tables: {
            [_ in never]: never
          }
          Views: {
            [_ in never]: never
          }
          Functions: {
            "graphql":
{ Args: { "extensions"?: Json,"operationName"?: string,"query"?: string,"variables"?: Json }; Returns: Json
                           }
          }
          Enums: {
            [_ in never]: never
          }
          CompositeTypes: {
            [_ in never]: never
          }
        },"public": {
          Tables: {
            "audit_log": {
                  Row: {
                    "action": string,"actor_id": string | null,"created_at": string,"detail": NonNullable<Json>,"id": number
                  }
                  ComputedFields: never
                  Insert: {
                    "action": string,"actor_id"?: string | null,"created_at"?: string,"detail"?: NonNullable<Json>,"id"?: never
                  }
                  Update: {
                    "action"?: string,"actor_id"?: string | null,"created_at"?: string,"detail"?: NonNullable<Json>,"id"?: never
                  }
                  Relationships: [
                    
                  ]
                },"projects": {
                  Row: {
                    "created_at": string,"id": string,"name": string,"owner_id": string
                  }
                  ComputedFields: never
                  Insert: {
                    "created_at"?: string,"id"?: string,"name": string,"owner_id"?: string
                  }
                  Update: {
                    "created_at"?: string,"id"?: string,"name"?: string,"owner_id"?: string
                  }
                  Relationships: [
                    
                  ]
                }
          }
          Views: {
            [_ in never]: never
          }
          Functions: {
            "record_audit_event":
{ Args: { "p_action": string,"p_detail"?: Json }; Returns: undefined
                           }
          }
          Enums: {
            [_ in never]: never
          }
          CompositeTypes: {
            [_ in never]: never
          }
        }
}

type DatabaseWithoutInternals = Omit<Database, '__InternalSupabase'>

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never
> = DefaultSchemaTableNameOrOptions extends { schema: keyof DatabaseWithoutInternals }
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
  ? (DefaultSchema["Tables"] & DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
      Row: infer R
    }
    ? R
    : never
  : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never
> = DefaultSchemaTableNameOrOptions extends { schema: keyof DatabaseWithoutInternals }
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
  ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
      Insert: infer I
    }
    ? I
    : never
  : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never
> = DefaultSchemaTableNameOrOptions extends { schema: keyof DatabaseWithoutInternals }
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
  ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
      Update: infer U
    }
    ? U
    : never
  : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof DatabaseWithoutInternals }
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
  ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
  : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never
> = PublicCompositeTypeNameOrOptions extends { schema: keyof DatabaseWithoutInternals }
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
  ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
  : never

export const Constants = {
  "graphql_public": {
          Enums: {
            
          }
        },"public": {
          Enums: {
            
          }
        }
} as const
```
