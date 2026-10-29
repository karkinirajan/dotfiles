## 10. Accessibility (WCAG 2.2 AA minimum)

- A11Y-01 (MUST): Target WCAG 2.2 Level AA on every shipped page. Note the 2.2 additions: focus not obscured (2.4.11), dragging alternatives (2.5.7), target size minimum (2.5.8), consistent help (3.2.6), redundant entry (3.3.7), accessible authentication (3.3.8).
- A11Y-02 (MUST): Semantic HTML first. Landmarks (`header`, `nav`, `main`, `footer`), one `h1` per page, ordered headings, real lists, real tables with `th` and `scope`. Buttons perform actions, links navigate. No clickable `div`.
- A11Y-03 (MUST): Everything is keyboard operable with a visible `:focus-visible` indicator meeting 3:1 contrast, a logical tab order (never `tabindex` above 0), a skip-to-content link, focus moved to the page heading or announced on route change, and dialogs that trap and restore focus.
- A11Y-04 (MUST): ARIA is a last resort. Use native elements; when ARIA is needed, use correct roles, states, and relationships (`aria-expanded`, `aria-controls`, `aria-current`). `aria-live="polite"` for status updates, assertive only for urgent errors. Never `aria-hidden` on focusable content.
- A11Y-05 (MUST): Forms: programmatic labels, instructions before the field, errors identified in text and linked with `aria-describedby`, suggestions for fixes, no re-asking for data already given in the flow, authentication that allows paste and password managers and does not require a cognitive test.
- A11Y-06 (MUST): Pointer targets are at least 24 by 24 CSS pixels (aim for 44), and every drag interaction has a single-pointer alternative (buttons, menus).
- A11Y-07 (MUST): Meaning never relies on color alone. Text contrast 4.5:1, large text and UI components 3:1, verified in both themes. Support `prefers-contrast` and `forced-colors` for custom controls.
- A11Y-08 (MUST): Images have alt text by policy: informative images get a concise description, decorative images get `alt=""`, complex images get a longer description nearby. Video has captions and transcripts. No autoplay with sound.
- A11Y-09 (MUST): Respect `prefers-reduced-motion`. No content flashes more than three times per second. Parallax and large motion are removable.
- A11Y-10 (MUST): Layout survives 200 percent text resize and 400 percent zoom (reflow at 320 CSS pixels). Use `rem`, avoid fixed-height text containers, never set `user-scalable=no`.
- A11Y-11 (MUST): `<html lang>` is correct, language changes are marked with `lang`, RTL locales set `dir`, and layout uses logical properties (`ms-`, `me-`, `ps-`, `pe-`, `start-`, `end-`) instead of left and right.
- A11Y-12 (MUST): Test at three levels. Automated: `eslint-plugin-jsx-a11y`, `@axe-core/playwright` on key routes in CI, Testing Library `getByRole` queries. Manual each release: keyboard-only pass, 400 percent zoom, forced colors, reduced motion. Assistive technology each release: Orca with Firefox on Linux, plus VoiceOver (macOS and iOS) or NVDA, and TalkBack on Android for client-facing apps. Automated tools catch only a fraction of issues; they do not replace the manual passes.
- A11Y-13 (SHOULD): Every route has a unique, descriptive `<title>`. Loading regions use `role="status"` or `aria-busy`. Infinite scroll offers a pagination alternative and keeps the footer reachable.
- A11Y-14 (MAY): For enterprise or public-sector clients, produce an accessibility statement and a conformance report (ACR/VPAT) from the manual test results.

---
