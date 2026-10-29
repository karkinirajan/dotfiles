## 8. Styling, design system, and UI

### 8.1 Tailwind CSS v4

- STYLE-01 (MUST): CSS-first. `@import "tailwindcss";` in `globals.css`, tokens in `@theme`, built by `@tailwindcss/turbopack` (the `create-next-app` default; use `@tailwindcss/postcss` only on webpack or another toolchain). No `tailwind.config.js` or `.ts`. Use `@config` only for a plugin that requires it, with a comment.
- STYLE-02 (MUST): Three token tiers. Primitives (raw OKLCH scales) feed semantic tokens (`--background`, `--foreground`, `--primary`, `--muted`, `--accent`, `--destructive`, `--border`, `--ring`, plus `--success`, `--warning`, `--info`), which feed component styles. Components use semantic tokens only. Raw palette classes (`bg-blue-500`) are forbidden outside the token file.
- STYLE-03 (MUST): Colors in OKLCH. Every foreground and background pair is checked for contrast (WCAG 2.2 AA: 4.5:1 text, 3:1 large text and UI components) in light and dark.
- STYLE-04 (SHOULD): Typography: at most two families, fluid type tokens with `clamp()`, `tabular-nums` for numeric columns, 60 to 75 characters line length for prose, `text-balance` on headings, `text-pretty` on paragraphs.
- STYLE-05 (MUST NOT): No arbitrary values (`w-[137px]`) unless a third-party constraint forces it, with a comment. A value used twice becomes a token.
- STYLE-06 (MUST): Compose classes with `cn()`. New shadcn projects import it from the `cn` package (`import { cn } from "cn"`); a project with a local `clsx` plus `tailwind-merge` helper converts with `shadcn migrate cn` (Tailwind v3 projects stay on `tailwind-merge` 2). Variants with `cva`. No string-built class names (`bg-${color}-500`); the scanner cannot see them. Map to complete literal class names.
- STYLE-07 (SHOULD): `prettier-plugin-tailwindcss` for ordering. Optionally a Tailwind lint rule set for canonical class names.
- STYLE-08 (MUST): Mobile first. Design at 360px, verify at 320 (no horizontal scroll, WCAG reflow), 768, 1024, 1440, and at 200 percent zoom. Use container queries (`@container`, `@md:`) for components placed in variable-width slots. Use `min-h-dvh`, not `h-screen`. Respect safe areas (`env(safe-area-inset-*)`). Touch targets at least 44 by 44 CSS pixels (the AA floor is 24). Hover-only affordances need a touch equivalent.
- STYLE-09 (MUST): Dark mode via `@custom-variant dark` and `next-themes` (`attribute="class"`, `defaultTheme="system"`, `suppressHydrationWarning` on `<html>`). No flash of wrong theme. Set `color-scheme` in the token file (`:root { color-scheme: light }`, `.dark { color-scheme: dark }`). Under a nonce CSP, pass the nonce to `ThemeProvider` so its inline script runs (A.16). Review images, shadows, charts, and syntax themes in both modes.
- STYLE-10 (MUST): Motion: 150 to 250 ms for micro-interactions, 400 ms maximum for transitions, animate `transform` and `opacity` only, `motion-reduce:` honored everywhere, no autoplay longer than 5 seconds without a pause control. Use `tw-animate-css` (the Tailwind v4 replacement for `tailwindcss-animate`). Reach for the `motion` library only for gesture or layout animation CSS cannot do, and lazy-load it.
- STYLE-11 (MUST NOT): No `@apply` in component code and no hand-made `.btn` classes. `@apply` is allowed only in the global base layer for third-party markup (MDX, prose).
- STYLE-12 (SHOULD): Z-index from a token scale. `@layer` for ordering. No `!important` except to override third-party CSS.
- STYLE-13 (SHOULD): Support `forced-colors:` for custom controls and a print stylesheet for invoice, receipt, and report pages.

### 8.2 shadcn/ui

- UI-01 (MUST): Pick one component base per project at `init` and record it in an ADR. Existing projects stay on their current base and migrate deliberately.

| Base | Choose when | Notes |
|---|---|---|
| Base UI | Greenfield default (shadcn default since July 2026) | Stable, from the Radix, MUI, and Floating UI authors. Composes with a `render` prop |
| Radix | Existing codebase, or a dependency that targets Radix APIs | Mature, fully supported, composes with `asChild`. Some third-party kits (for example AI chat elements) were reported to target Radix, so check before choosing Base UI |
| React Aria | Heavy internationalization, date and color pickers, strictest accessibility | New in July 2026, first-class in the CLI (`--base aria`) |

- UI-02 (MUST): shadcn/ui is owned code in `components/ui`. Before updating a component run `shadcn add <name> --diff` and `--dry-run` (CLI v4), inspect with `--view`, and never `--overwrite` without reading the diff. Keep customization in tokens, `cva` variants, and wrappers in `components/shared`.
- UI-03 (MUST): Build app-level composites once (`PageHeader`, `DataTable`, `ConfirmDialog`, `EmptyState`, `FormField`, `ErrorState`) from primitives. Features consume composites, not raw primitives repeated per page.
- UI-04 (MUST): Every input has a visible label, helper text, and an error message wired with `aria-describedby`. Placeholder is not a label.
- UI-05 (SHOULD): Data tables use TanStack Table with server-side pagination, sorting, and filtering driven by URL state, typed column definitions, sticky header, keyboard support, density control, and virtualization for large sets.
- UI-06 (MUST): Do not build custom modals, popovers, menus, or comboboxes. Use the primitives (focus trap, escape, return focus, scroll lock included). Destructive confirmations use the alert dialog pattern. On mobile prefer a drawer or sheet over a centered dialog for long content.
- UI-07 (MUST): One toast library per project (ARCH-04): the shadcn `toast` component (`shadcn add toast`) or `sonner` (`shadcn add sonner`), never both. Toasts are for non-critical confirmations. Errors that need action stay inline.
- UI-08 (SHOULD): Icons from one library (`lucide-react`), named imports, size tokens, `aria-hidden` when decorative, an accessible name on icon-only buttons.
- UI-09 (MUST): Design all states before building: loading (skeleton), empty (reason plus primary action), error (what happened, what to do, retry), partial, offline, forbidden, not found, success.
- UI-10 (SHOULD): Charts use the shadcn chart wrapper, lazy-loaded, with token colors, a text or table alternative, and no color-only encoding.
- UI-11 (SHOULD): Token names in Figma variables equal the CSS custom property names so design handoff is mechanical.
- UI-12 (SHOULD): Content design: sentence case, verb-first buttons, no "click here", errors describe the system state not user blame, numbers and dates through `Intl`, truncation with an accessible full value, allow 30 percent text expansion for translation.
- UI-13 (SHOULD): Visual QA through Playwright snapshots of key screens at 3 viewports and 2 themes. Add Storybook only when building a shared design-system package.
- UI-14 (SHOULD): One place defines `h1` to `h6`, body, caption, and code styles. `@tailwindcss/typography` (`prose`) is for markdown and MDX content only.

### 8.3 Syntax highlighting (Prism.js or Shiki)

Only relevant if "Prism" meant Prism.js.

- CODE-01 (SHOULD): Prefer Shiki rendered in a Server Component (zero client JavaScript, VS Code themes, accurate grammars). Use Prism.js only for legacy compatibility, and then load it lazily.
- CODE-02 (MUST): Code blocks are keyboard reachable (`tabIndex={0}` on a horizontally scrollable region), have an accessible copy button with a live-region confirmation, and use theme colors that meet contrast in both color schemes.
- CODE-03 (MUST): HTML produced by a highlighter is generated server-side from escaped source. Never pass user-supplied HTML to `dangerouslySetInnerHTML`.

---
