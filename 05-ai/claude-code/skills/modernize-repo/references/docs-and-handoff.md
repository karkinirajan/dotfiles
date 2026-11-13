# Docs and hand-off

The shape of the written output. The templates are in `../templates/docs/`.

## README

Sections, in this order: description (what it is and who it is for), features, quickstart, configuration (a table of every environment variable with its default and purpose), project structure, testing, versions (link to VERSIONS.md), deployment when relevant, license.

Rules:

- Describe what the code does today. Check each command in the README by running it.
- When the old README promised more than the code does, add a status table (built, partial, not built) and keep the design text.
- No personal data, no live secrets, no invented badges or claims.
- Do not add or change a LICENSE. If the README names a license that has no file, flag it.
- Keep it short when a `docs/` set exists, and link to it.

## VERSIONS.md

A dated record, not a wish list. Start with "Checked on YYYY-MM-DD" and say where something could not be verified.

| Section | Content |
| --- | --- |
| Runtimes and tooling | Component, version, where it is pinned, why this one (with the lifecycle source) |
| Where it was actually run | What ran on which version, and a "Not run" line |
| Application dependencies | Package, locked version, declared range. Floors equal the tested versions |
| Deliberately not upgraded | Package, latest seen, why not |
| Known advisories | Before and after counts and what remains and why |
| Third-party service model IDs | Default, checked against what, and what was not exercised |
| Things to watch | Deprecation warnings and upcoming removals |

## docs/ chapters

Use them when the repository is big enough that the README would grow past a screen or two of setup. Name them like a book: `docs/README.md` (the contents table), `01-getting-started.md`, `02-architecture.md`, `03-testing-and-quality.md`, further numbered chapters as needed, and `work-done.md`. Tiny repositories skip `docs/` and put the work-done record at the root.

The testing chapter says what each check proves, what is not covered, how mutation checks work and how to add a module, and how to read a CI failure.

## The work-done record

One file, `docs/work-done.md` (or `work-done.md` at the root for small repositories). Plain language. It starts with the branch, the date, and "nothing has been pushed". Sections:

1. **At a glance:** before and after numbers (tracked files, tests, coverage, mutants killed by the original tests and now, advisories, versions).
2. **What was wrong, and what changed:** a table of area, what was found, what changed. Findings that were security problems go first.
3. **How it was checked:** a table of check and result with the real counts and versions.
4. **Not checked:** each item on its own line: live third-party services, installers, other browsers, CI on the hosting service, Docker if it was down.
5. **Decisions for you:** numbered, each one actionable, with the default you took.
6. **To publish:** the push command as text.

Report each item as a fact with its status in the same sentence: "done, but the deploy step is waiting on you", never just "done".

## Hand-off lists

Put these in the work-done record and repeat the short form in the final report. Never include a secret value.

| List | Contents |
| --- | --- |
| ROTATE | Each credential type found, where, and in how many commits; the old session or signing secret; anything an old image may have contained |
| SET | Environment variables to set before deploying, with the minimum length for secrets, and what refuses to start without them |
| RUN | Migrations to run against real databases (never run by you), storage policies and settings to check on the hosting service |
| DECIDE | Product choices you left alone: license, rejected URL schemes, model defaults, dead code that may be wanted, placeholder content, behavior changes |
| VERIFY | What was never run against the real service, and the first thing to try |
| PUSH | `git push -u origin chore/modernize` as text. Add merge, CI check and checkout cleanup as separate commands only if the owner asked for them. History rewrite (`git filter-repo`) is offered, never run |

## The final report

Use the owner's structured status block, then the lists in short form:

```text
STATUS: COMPLETE | BLOCKED | PARTIAL
Changed: ...
Verified: ... (commands actually run, not "should work")
Remaining: ...
Risk: ...
```

Keep it short. The detail lives in the work-done record, and the report points to it.
