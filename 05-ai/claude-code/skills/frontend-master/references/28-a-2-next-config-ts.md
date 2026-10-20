### A.2 `next.config.ts`

The `turbopack.rules` entry wires `@tailwindcss/turbopack`. `headers` returns a promise instead of being `async` because the lint rule `require-await` is on. `exposeTestingApiInProductionBuild` stays false unless `EXPOSE_TESTING_API=1` is set (TEST-05). The Content Security Policy is set per request in `proxy.ts` (A.10).

`next.config.ts`

```ts
import type { NextConfig } from 'next';

const securityHeaders: { key: string; value: string }[] = [
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

