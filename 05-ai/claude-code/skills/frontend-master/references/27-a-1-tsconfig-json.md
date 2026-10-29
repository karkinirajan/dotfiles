### A.1 `tsconfig.json`

Next.js adds fields such as `include` entries on first run; keep the strictness flags. Three choices are deliberate:

- `noUnusedLocals` and `noUnusedParameters` are off. Next's generated `.next/dev/types/validator.ts` has unused imports in apps without Route Handlers, and with those flags `next build` fails after a `next dev` run. `@typescript-eslint/no-unused-vars` in A.14 covers unused code.
- `exactOptionalPropertyTypes` is off (TS-02).
- There is no `baseUrl`. `paths` alone resolves `@/*` on TypeScript 6 and 7.

If `tsc` reports a typed-route error for a page that exists, delete `.next`: a stale `.next/cache/.tsbuildinfo` keeps the old error.

`tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "allowJs": false,
    "skipLibCheck": true,
    "noEmit": true,
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.mts",
    "**/*.tsx",
    ".next/types/**/*.ts",
    ".next/dev/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```
