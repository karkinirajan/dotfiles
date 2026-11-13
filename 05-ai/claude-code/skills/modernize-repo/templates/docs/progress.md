# <repo> modernize progress

Copy to `~/.cache/<repo>-qa/progress.md` at the start. Update it after every phase. If a run is interrupted or resumed, read it first and continue from the first unchecked phase.

- Started: <date>
- Repository: <absolute path>
- Branch: chore/modernize
- Identity (every commit must carry it): <git user.name and user.email>
- Type and route: <service, prototype, library or CLI, already modern, content, static site, desktop or extension, tooling>
- Fork or copy of another repo: <no, or what>
- Dirty tree at start: <no, or the files that are the owner's: do not touch>

## Phases

- [ ] 0 Intake
- [ ] 1 Discover and baseline (as-shipped results recorded)
- [ ] 2 Plan and targets (sources for each version)
- [ ] 3 Secrets and hygiene
- [ ] 4 Versions and toolchain
- [ ] 5 Structure and dedup
- [ ] 6 Defect hunt
- [ ] 7 Tests
- [ ] 8 Mutation checks
- [ ] 9 CI and containers
- [ ] 10 Docs
- [ ] 11 UI quality (if there is a UI)
- [ ] 12 Gates, review, commit
- [ ] 13 Hand-off

## Baseline as shipped

- Tests: <run, passed, failed, or "could not run: error">
- Lint, build: <results>
- Entry point starts: <yes, or the exact error>
- Tracked files: <n>; junk among them: <n>
- Secret scan (names and counts only): <result>
- Advisories: <n by severity>

## Findings (append as you go)

- <class from the defect catalogue>: <where>: <test that reproduces it>

## Decisions taken (these become "Decisions for you")

- <decision and default>

## Not verified (these become "Not checked")

- <item>

## How to re-run the gates

- <exact commands>
