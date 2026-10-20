## 14. Cross-cutting concerns

### 14.1 Internationalization

- I18N-01 (MUST): If more than one locale is possible, route through a `[locale]` segment from day one, negotiate in `proxy.ts`, and keep messages in typed catalogs (`next-intl` 4.14.9 supports Next.js 16). Retrofitting i18n is expensive.
- I18N-02 (MUST): No string concatenation for sentences. Use ICU message formats for plurals and gender. Format dates, numbers, currency, lists, and relative time with `Intl`. Store timestamps in UTC, display in the user's zone.
- I18N-03 (SHOULD): Complex scripts (for example Devanagari): choose a font with proper conjunct shaping (Noto family), subset by unicode-range, test line height (taller than Latin), test numeral and calendar expectations with native speakers, and test input methods.
- I18N-04 (SHOULD): Pseudo-localize in CI (expanded, accented strings) to catch truncation and hard-coded text. Use logical CSS properties (A11Y-11).

### 14.2 SEO

- SEO-01 (MUST): Server-render all indexable content. One `h1`, descriptive titles under about 60 characters, meta descriptions, canonical URLs, `hreflang` for locales, structured data (JSON-LD) matching visible content, `sitemap.ts`, `robots.ts`, correct status codes (404 for missing, 301 for permanent moves in `next.config.ts` redirects), and `noindex` on private and staging environments.
- SEO-02 (SHOULD): Crawlable links (`<a href>` via `<Link>`), meaningful alt text, fast Core Web Vitals, no content that appears only after client JavaScript.

---

