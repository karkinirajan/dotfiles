### A.10 Content Security Policy in `proxy.ts`

Choose the mode from the SEC-08 table first. Mode A (dynamic nonce) is the default below; mode B (static shell, inline scripts allowed) follows as replacement files. Start with `Content-Security-Policy-Report-Only` as the response header name, collect violations, then switch to enforce. Details that were found by running the browser:

- Next.js reads the nonce from the request header `Content-Security-Policy`, so `proxy.ts` sets it on the forwarded request headers and on the response.
- A nonce in `style-src` makes browsers ignore `'unsafe-inline'` there, and dev tooling injects `<style>` tags without a nonce. `buildCsp` therefore drops the nonce from `style-src` in development. React's inline `style` attributes are allowed through `style-src-attr`.
- `'unsafe-eval'` is added to `script-src` in development only.
- `next-themes` injects an inline script; it runs only because `Providers` passes the nonce (A.16).
- The mode A root layout awaits `connection()` and exports `instant = false` (A.16). Without them the prerendered shell has no nonce and the page never hydrates.
- The matcher excludes prefetch requests and static assets; the CSP smoke test in A.17 runs against the production build in CI.

`src/lib/security/csp.ts`

```ts
import { publicEnv } from '@/lib/env/public';

export function buildCsp({ nonce, isDev }: { nonce: string; isDev: boolean }): string {
  const supabaseOrigin = new URL(publicEnv.NEXT_PUBLIC_SUPABASE_URL).origin;
  const supabaseRealtime = supabaseOrigin.replace(/^http/, 'ws'); // https -> wss, http -> ws

  const directives: Record<string, string[]> = {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      `'nonce-${nonce}'`,
      "'strict-dynamic'",
      ...(isDev ? ["'unsafe-eval'"] : []),
    ],
    // A nonce makes browsers ignore 'unsafe-inline', and dev tooling injects un-nonced <style> tags.
    'style-src': isDev ? ["'self'", "'unsafe-inline'"] : ["'self'", `'nonce-${nonce}'`],
    'style-src-attr': ["'unsafe-inline'"],
    'img-src': ["'self'", 'blob:', 'data:', supabaseOrigin],
    'font-src': ["'self'"],
    'connect-src': ["'self'", supabaseOrigin, supabaseRealtime],
    'object-src': ["'none'"],
    'base-uri': ["'none'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
  };

  return Object.entries(directives)
    .map(([name, values]) => `${name} ${values.join(' ')}`)
    .join('; ');
}
```

`src/proxy.ts`

```ts
import type { NextRequest, NextResponse } from 'next/server';
import { buildCsp } from '@/lib/security/csp';
import { updateSession } from '@/lib/supabase/proxy';

// Next.js reads the nonce from the request header named Content-Security-Policy.
// Switch the response header name to Content-Security-Policy-Report-Only while rolling out.
const CSP_RESPONSE_HEADER = 'Content-Security-Policy';

export async function proxy(request: NextRequest): Promise<NextResponse> {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
  const csp = buildCsp({ nonce, isDev: process.env.NODE_ENV === 'development' });

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-nonce', nonce);
  requestHeaders.set('Content-Security-Policy', csp);

  const response = await updateSession(request, requestHeaders);
  response.headers.set(CSP_RESPONSE_HEADER, csp);
  return response;
}

export const config = {
  matcher: [
    {
      source:
        '/((?!api/webhooks|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|avif|ico|css|js|woff2?)$).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
};
```

Mode B replacements. The policy is static (set in `next.config.ts`), so the nonce, the `x-nonce` header, and the dynamic root layout go away and the prerendered shell survives. `proxy.ts` only refreshes the session, `Providers` no longer reads headers, and `navigation.spec.ts` (A.17) joins the E2E suite because routes now have a static shell for `instant()` to assert on. Build the E2E artifact with `EXPOSE_TESTING_API=1`.

`next.config.ts` (mode B)

```ts
import type { NextConfig } from 'next';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
if (!supabaseUrl) throw new Error('NEXT_PUBLIC_SUPABASE_URL is required');
const supabaseOrigin = new URL(supabaseUrl).origin;
const supabaseRealtime = supabaseOrigin.replace(/^http/, 'ws'); // https -> wss, http -> ws

// Mode B (SEC-08): one static policy. Scripts may be inline so the prerendered shell still runs.
const contentSecurityPolicy = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline'${process.env.NODE_ENV === 'development' ? " 'unsafe-eval'" : ''}`,
  "style-src 'self' 'unsafe-inline'",
  `img-src 'self' blob: data: ${supabaseOrigin}`,
  "font-src 'self'",
  `connect-src 'self' ${supabaseOrigin} ${supabaseRealtime}`,
  "object-src 'none'",
  "base-uri 'none'",
  "form-action 'self'",
  "frame-ancestors 'none'",
].join('; ');

const securityHeaders: { key: string; value: string }[] = [
  { key: 'Content-Security-Policy', value: contentSecurityPolicy },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=(), payment=()' },
  { key: 'Cross-Origin-Opener-Policy', value: 'same-origin' },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains' },
];

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  reactCompiler: true,
  typedRoutes: true,
  poweredByHeader: false,
  // Container builds (CI-08) set BUILD_STANDALONE=1; `next start` does not work with standalone output.
  output: process.env.BUILD_STANDALONE === '1' ? 'standalone' : undefined,
  turbopack: {
    rules: {
      '*.css': { loaders: ['@tailwindcss/turbopack'], as: '*.css' },
    },
  },
  images: {
    formats: ['image/avif', 'image/webp'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'PROJECT_REF.supabase.co',
        pathname: '/storage/v1/object/public/**',
      },
    ],
  },
  experimental: {
    // E2E builds only: EXPOSE_TESTING_API=1 pnpm build. Never deploy that build.
    exposeTestingApiInProductionBuild: process.env.EXPOSE_TESTING_API === '1',
    // SEC-06: the default is 1 MB. The reference has no uploads, so 100 kB is plenty; when you add one,
    // set the file limit plus 10 to 20 kB of multipart overhead.
    serverActions: { bodySizeLimit: '100kb' },
  },
  headers: () => Promise.resolve([{ source: '/:path*', headers: securityHeaders }]),
};

export default nextConfig;
```

`src/proxy.ts` (mode B)

```ts
import type { NextRequest, NextResponse } from 'next/server';
import { updateSession } from '@/lib/supabase/proxy';

export async function proxy(request: NextRequest): Promise<NextResponse> {
  return updateSession(request, new Headers(request.headers));
}

export const config = {
  matcher: [
    {
      source:
        '/((?!api/webhooks|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|avif|ico|css|js|woff2?)$).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
};
```

`src/components/shared/providers.tsx` (mode B)

```tsx
import { ThemeProvider } from 'next-themes';
import type { ReactNode } from 'react';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      {children}
    </ThemeProvider>
  );
}
```

`src/app/layout.tsx` (mode B)

```tsx
import type { Metadata } from 'next';
import { GeistMono } from 'geist/font/mono';
import { GeistSans } from 'geist/font/sans';
import { Providers } from '@/components/shared/providers';
import './globals.css';

export const metadata: Metadata = {
  title: { default: 'Template', template: '%s | Template' },
  description: 'Template app',
};

export default function RootLayout({ children }: LayoutProps<'/'>) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-dvh bg-background text-foreground">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-background focus:px-4 focus:py-2 focus:text-foreground"
        >
          Skip to content
        </a>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

`tests/e2e/navigation.spec.ts` (mode B)

```ts
import { instant } from '@next/playwright';
import { expect, test } from '@playwright/test';

// Mode B only: needs a build made with EXPOSE_TESTING_API=1 and routes that have a static shell.
test('the sign-in shell renders without waiting for dynamic data', async ({ page }) => {
  await page.goto('/');

  await instant(page, async () => {
    await page.getByRole('link', { name: 'Sign in' }).click();
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });
});
```
