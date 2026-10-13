# 19. Governance

Part of the `frontend-expert` skill. See `../SKILL.md` for the rule-ID index.

- GOV-01 (MUST): Architecture Decision Records in `docs/adr/NNNN-title.md` with Context, Options, Decision, Consequences, Status, Date, Owner. Required for: component base, data access model, hosting, CSP strategy, any dependency over the budget, and any deviation from a MUST rule.
- GOV-02 (MUST): Production-grade only. Every function is typed, validated at boundaries, error-handled, accessible, logged, and tested at the right level. No tutorial or demo code in client repositories.
- GOV-03 (MUST): Upstream documentation outranks this file. When they disagree, fix this file within a week and note it in the changelog.
- GOV-04 (SHOULD): Exceptions carry an ADR and an expiry date. Expired exceptions are reviewed monthly.
- GOV-05 (SHOULD): Monthly review: read release notes for Next.js, React, Tailwind, shadcn/ui, Supabase, and Prisma. Re-read every version in `01-versions-and-watch.md` §1.1 against the registry, update section 1, retire or add rules, and append to the changelog (`22-references-changelog.md`).
