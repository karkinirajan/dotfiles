# Work done: <repo>

Done on <YYYY-MM-DD> on the local branch `chore/modernize`. Nothing has been pushed, published or deployed. This is the plain record: what changed, how each change was checked, what was **not** checked, and what it leaves for you to decide.

## At a glance

| | Before | After |
| --- | --- | --- |
| Tracked files | <n> | <n> |
| Tests | <n> | <n> |
| Statement coverage of owned code | <n or none> | <n> |
| Mutants killed by the original tests | <n of n> | <n of n> |
| Dependency advisories (`npm audit` or `uv audit`) | <n> | <n> |
| Runtime | <version> | <version> |

## What was wrong, and what changed

Security findings first.

| Area | Found | Change |
| --- | --- | --- |
| <area> | <what was wrong, in plain words, with the effect on a user> | <what was done and the test that proves it> |

## How it was checked

| Check | Result |
| --- | --- |
| <command> | <real result: counts, versions, exit status> |

## Not checked

- <live service, installer, browser, CI on the host, Docker if it was down: one per line, and what to try first>

## Decisions for you

1. **<decision>.** <the default taken, and what changing it means>.
2. **ROTATE:** <credential type, where, in how many commits. Never the value>.
3. **SET before deploying:** <variables, minimum lengths, what refuses to start without them>.
4. **RUN:** <migrations or settings on real systems that were not touched>.
5. **Nothing is pushed.** To publish: `git push -u origin chore/modernize`.
