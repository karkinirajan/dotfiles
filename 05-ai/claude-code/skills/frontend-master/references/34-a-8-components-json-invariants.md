### A.8 `components.json` invariants

Create the file with `pnpm dlx shadcn@latest init` and choose the base deliberately (UI-01); `--base` accepts `base`, `radix`, or `aria`. The base is encoded in the `style` value, which is prefixed `radix-`, `base-`, or `aria-` followed by a style name, so do not hand-write it. After init, check these fields against the published schema (`https://ui.shadcn.com/schema.json`):

- `tailwind.config` is an empty string (Tailwind v4 has no JS config).
- `tailwind.css` points to `src/app/globals.css` and `tailwind.cssVariables` is `true`.
- `rsc` is `true` and `tsx` is `true`.
- `aliases` maps `components` and `utils` (required) and `ui`, `lib`, `hooks` (optional) to the paths in section 3.
- `iconLibrary` is `lucide` (the schema accepts any string).
- No `tailwind.config.*` file exists in the repository.

