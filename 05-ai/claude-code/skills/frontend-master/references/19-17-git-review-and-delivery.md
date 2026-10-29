## 17. Git, review, and delivery

- GIT-01 (MUST): Conventional Commits (`feat:`, `fix:`, `perf:`, `refactor:`, `test:`, `docs:`, `chore:`, `ci:`), enforced by commitlint. Commit identity is `kneeraazon404` (set `user.name` and the GitHub-provided noreply `user.email` per repo and verify in a pre-push check).
- GIT-02 (MUST): PRs change at most about 400 lines and one concern. The template asks: what and why, how it was tested, screenshots (mobile and desktop, light and dark), risk and rollback, rule IDs touched, ADR link if architectural.
- GIT-03 (SHOULD): Branches named `feat/`, `fix/`, `chore/`. Squash merge with a Conventional Commit title.
- GIT-04 (MUST): Review order: security and data access first, then correctness, then accessibility, then performance, then style. Style is automated and never debated in review.
- DEL-01 (MUST): Client handoff pack: README in the house format (left-aligned, no centering markup, two-column stack table), environment variable table, architecture diagram, ADRs, runbooks (deploy, rollback, incident, key rotation, database restore), design token overview, test instructions, cost model, an account ownership matrix (hosting, database, domain, analytics, email) with transfer steps, dependency licenses (`pnpm licenses list`), and the accessibility statement.
- DEL-02 (MUST): Estimates are vertical slices that include accessibility, security, tests, performance, and docs. "Polish later" is not a line item.
- DEL-03 (SHOULD): Milestone acceptance criteria reference Definition of Done IDs from section 20. Distinguish "demo-ready" from "production-ready" in the contract.

---
