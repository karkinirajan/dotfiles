### A.16 App shell, providers, and reference routes

Mode A layout: `export const instant = false` and `await connection()` make every route render per request so the nonce reaches every script (SEC-08). `Providers` reads the nonce from the `x-nonce` request header and hands it to `next-themes`. TanStack Query mounts only in the route group that needs it (RQ-01): `getQueryClient` returns a fresh client per call on the server and one shared client in the browser (RQ-02), and `QueryProvider` is mounted in `dashboard/layout.tsx`. The reference routes show a static page, a link, a login page backed by the A.20 flow (its `searchParams` read sits inside `Suspense`), and a dashboard whose per-user content sits inside `Suspense` with a skeleton of the final height (NEXT-08). A visually hidden skip link in the root layout targets `id="main"` on every page's `<main>` (A11Y-03).

`src/app/layout.tsx`

```tsx
import type { Metadata } from 'next';
import { GeistMono } from 'geist/font/mono';
import { GeistSans } from 'geist/font/sans';
import { connection } from 'next/server';
import { Providers } from '@/components/shared/providers';
import './globals.css';

// Mode A (SEC-08): every route renders per request, so the CSP nonce reaches every script tag.
export const instant = false;

export const metadata: Metadata = {
  title: { default: 'Template', template: '%s | Template' },
  description: 'Template app',
};

export default async function RootLayout({ children }: LayoutProps<'/'>) {
  await connection();
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

`src/components/shared/providers.tsx`

```tsx
import { headers } from 'next/headers';
import { ThemeProvider } from 'next-themes';
import type { ReactNode } from 'react';

/** Mode A: next-themes injects an inline script, which only runs when it carries the request nonce. */
export async function Providers({ children }: { children: ReactNode }) {
  const nonce = (await headers()).get('x-nonce') ?? undefined;
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
      nonce={nonce}
    >
      {children}
    </ThemeProvider>
  );
}
```

`src/lib/query/get-query-client.ts`

```ts
import {
  QueryClient,
  defaultShouldDehydrateQuery,
  environmentManager,
} from '@tanstack/react-query';

function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      // Non-zero so hydrated server data is not refetched immediately (RQ-03).
      queries: { staleTime: 60 * 1000 },
      dehydrate: {
        // Include pending queries so prefetches can stream to the client (RQ-06).
        shouldDehydrateQuery: (query) =>
          defaultShouldDehydrateQuery(query) || query.state.status === 'pending',
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined;

/** New client per call on the server (never shared across requests), one per tab in the browser (RQ-02). */
export function getQueryClient(): QueryClient {
  if (environmentManager.isServer()) return makeQueryClient();
  browserQueryClient ??= makeQueryClient();
  return browserQueryClient;
}
```

`src/components/shared/query-provider.tsx`

```tsx
'use client';

import { QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { getQueryClient } from '@/lib/query/get-query-client';

export function QueryProvider({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={getQueryClient()}>{children}</QueryClientProvider>;
}
```

`src/components/shared/empty-state.tsx`

```tsx
import type { ReactNode } from 'react';

type EmptyStateProps = Readonly<{
  title: string;
  description: string;
  action?: ReactNode;
}>;

/** Reason plus primary action (UI-09). */
export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <section className="flex flex-col items-start gap-3 rounded-lg border p-6">
      <h2 className="text-lg font-semibold text-balance">{title}</h2>
      <p className="text-pretty text-muted-foreground">{description}</p>
      {action}
    </section>
  );
}
```

`src/app/page.tsx`

```tsx
import Link from 'next/link';

export default function HomePage() {
  return (
    <main id="main" className="mx-auto max-w-prose p-6">
      <h1 className="text-2xl font-semibold text-balance">Template</h1>
      <p className="text-pretty text-muted-foreground">Static content.</p>
      <nav aria-label="Primary" className="mt-4 flex gap-4">
        <Link href="/login" className="underline underline-offset-4">
          Sign in
        </Link>
        <Link href="/dashboard" className="underline underline-offset-4">
          Dashboard
        </Link>
      </nav>
    </main>
  );
}
```

`src/app/login/page.tsx`

```tsx
import type { Metadata } from 'next';
import { Suspense } from 'react';
import { LoginForm } from '@/features/auth/login-form';
import { safeRedirectPath } from '@/lib/security/redirect';

export const metadata: Metadata = { title: 'Sign in' };

async function LoginContent({
  searchParams,
}: Readonly<{ searchParams: PageProps<'/login'>['searchParams'] }>) {
  const { next } = await searchParams;
  const target = typeof next === 'string' ? safeRedirectPath(next) : undefined;
  return <LoginForm next={target} />;
}

export default function LoginPage(props: PageProps<'/login'>) {
  return (
    <main id="main" className="mx-auto max-w-prose p-6">
      <h1 className="mb-4 text-2xl font-semibold text-balance">Sign in</h1>
      <Suspense
        fallback={<div className="h-64 max-w-sm animate-pulse rounded-md bg-muted" aria-hidden />}
      >
        <LoginContent searchParams={props.searchParams} />
      </Suspense>
    </main>
  );
}
```

`src/app/dashboard/layout.tsx`

```tsx
import type { ReactNode } from 'react';
import { QueryProvider } from '@/components/shared/query-provider';

// Mount TanStack Query only in route groups that need client-side server state (RQ-01).
export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <QueryProvider>{children}</QueryProvider>;
}
```

`src/app/dashboard/page.tsx`

```tsx
import { Suspense } from 'react';
import { signOut } from '@/features/auth/actions';
import { verifySession } from '@/lib/auth/session';

async function Greeting() {
  const session = await verifySession();
  return <p>Signed in as {session.userId}</p>;
}

export default function DashboardPage() {
  return (
    <main id="main" className="mx-auto max-w-prose p-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <Suspense fallback={<p className="h-6 animate-pulse rounded bg-muted" aria-hidden />}>
        <Greeting />
      </Suspense>
      <form action={signOut} className="mt-4">
        <button
          type="submit"
          className="inline-flex min-h-11 items-center underline underline-offset-4"
        >
          Sign out
        </button>
      </form>
    </main>
  );
}
```

