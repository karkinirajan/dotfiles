### A.14 `eslint.config.mjs` (ESLint 10, flat config)

`eslint-config-next/core-web-vitals` already registers `react-hooks` (with the compiler rules), `jsx-a11y`, and the Next plugin. The strict a11y rules are added by spreading only the rule set, because registering the plugin a second time throws "Cannot redefine plugin". Typed linting uses `projectService`, so every linted `.ts` and `.mts` file must be in `tsconfig.json`'s `include` (A.1).

`eslint.config.mjs`

```js
import { defineConfig, globalIgnores } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import tseslint from 'typescript-eslint';

export default defineConfig([
  // Already registers react-hooks (compiler rules), jsx-a11y, and the Next plugin.
  ...nextVitals,
  // Strict a11y rules only: registering the plugin again throws "Cannot redefine plugin".
  { rules: jsxA11y.flatConfigs.strict.rules },
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      'no-console': 'error',
      '@next/next/no-img-element': 'error',
      '@typescript-eslint/consistent-type-imports': ['error', { fixStyle: 'inline-type-imports' }],
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/switch-exhaustiveness-check': 'error',
      '@typescript-eslint/restrict-template-expressions': ['error', { allowNumber: true }],
    },
  },
  {
    // Plain JavaScript config files are outside tsconfig, so typed rules are off for them.
    files: ['**/*.mjs'],
    ...tseslint.configs.disableTypeChecked,
  },
  globalIgnores([
    '.next/**',
    'out/**',
    'build/**',
    'next-env.d.ts',
    'src/generated/**',
    'src/lib/supabase/database.types.ts',
    'playwright-report/**',
    'test-results/**',
  ]),
]);
```
