---
name: visual-qa
description: Verify rendered UI against a mockup or the project's own design tokens by actually looking at the running app, not just reading the source. Use after any non-trivial UI change, or whenever a mockup/design reference exists to compare against.
---

Source code correctness doesn't prove the UI looks or behaves right. This skill is the verification pass that closes that gap — run it after `frontend-engineer` (or any UI change), before calling the work done.

## When a mockup/reference exists

1. Read the mockup and the current rendered result side by side (Read the image, then look at the actual running app — `chrome-devtools` / `claude-in-chrome` skill, or a screenshot).
2. Compare concretely: spacing, typography (size/weight/line-height), color values against the project's actual design tokens (not eyeballed — check the token file), border radius, shadows, icon choice, alignment.
3. List every gap found, fix them, re-render, re-compare. Repeat until no material gaps remain — don't stop after one pass if gaps were found.

## Always, mockup or not

Check the actual rendered app (dev server up, real interaction) for:
- Both themes if the project has light/dark — not just whichever one happened to be active.
- All four states for anything async: loading, loaded, error, empty.
- Responsive behavior at mobile/tablet/desktop breakpoints — not just resizing a desktop browser slightly.
- Keyboard navigation (tab order, visible focus ring) and hover states on every interactive element.
- Color contrast on real text/background pairs, not just "it looks fine" — color should never be the only signal for state (error, required, selected).
- Animations respect `prefers-reduced-motion` if the project has any.

## Reporting

State what you actually looked at (screenshots taken, breakpoints checked, states triggered) and what you found — "looks good" is not a finding. If you can't run the app to verify (no dev server available, no browser tool), say so explicitly rather than claiming visual verification happened.
