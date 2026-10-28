## How to use this document

1. Project kickoff: read sections 1 to 4, copy Appendix A templates, record deviations as ADRs (section 19).
2. Daily work: use section 0 as the pre-commit mental checklist and section 20 as the Definition of Done.
3. PR review: cite rule IDs (for example `SEC-07`, `NEXT-12`). A review comment with an ID needs no further argument.
4. AI-assisted development: drop the Appendix A.12 `AGENTS.md` into the repo root so every agent session inherits these rules.

Rule language follows RFC 2119: MUST (merge blocker), SHOULD (justify deviation in the PR), MAY (taste).

Rule IDs are stable. Never renumber; deprecate with a strikethrough note and add new IDs at the end of a section. IDs are grouped by topic, so numbers inside a section are not always sequential.

Scope decision: "Prism" in the original brief is treated as Prisma ORM (server-side data access in the Supabase stack). If Prism.js (syntax highlighting) was meant, see section 8.3.

Contents: 0 Top rules | 1 Baseline and versions | 2 Architecture | 3 Structure | 4 TypeScript | 5 React | 6 Next.js | 7 Data layer (Supabase, Prisma, DAL) | 8 Styling and UI (Tailwind, shadcn/ui) | 9 Security | 10 Accessibility | 11 Performance | 12 Testing | 13 Observability | 14 i18n and SEO | 15 Tooling | 16 CI/CD and hosting | 17 Git and delivery | 18 Upgrade playbooks | 19 Governance | 20 Definition of Done | 21 Anti-patterns | 22 References | Appendix A Templates

---
