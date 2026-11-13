# Mutation testing

Passing tests prove the code agrees with the tests. A mutation check asks the opposite question: if the code were wrong, would a test notice? Each mutant is a deliberate bug applied alone. The suite must then fail. A survivor is a missing test or redundant code.

On the 67 repositories every list ended fully killed. Typical first runs killed well under all of them, for example 16 of 41 and 52 of 112 against the original tests, and 41 of 66 on a repository that already had a mature suite. The gap is the value.

## Drivers

Copy one into the repository (`tests/mutation/` or `test/mutation/`, matching the project) so it outlives the session.

| Driver | Use when | Template |
| --- | --- | --- |
| `mutate.py` | Any stack. Takes the test command after `--` | `templates/mutation/mutate.py` |
| `mutate.mjs` | Node projects on `node:test`. Each mutant names the test files that exercise it, which is faster | `templates/mutation/mutate.mjs` |
| `check_patterns.py` | After a resume or a reformat: confirms every pattern still matches exactly once | `templates/mutation/check_patterns.py` |

```bash
python3 tests/mutation/mutate.py tests/mutation/mutants.py -- uv run pytest -x -q
python3 tests/mutation/mutate.py tests/mutation/mutants.py auth -- npx vitest run --bail 1     # only names containing "auth"
node tests/mutation/mutate.mjs tests/mutation/mutants.mjs
```

Exit codes: 0 all killed, 1 a survivor or a pattern that did not match exactly once, 2 the baseline suite is red.

## Writing mutants

A mutant is `(name, file, old, new)`. `old` must occur exactly once in `file`, so quote enough context. The mutant must stay valid code: a syntax error is "killed" for the wrong reason.

Write one mutant per rule in the code that guards something:

- Authentication and authorization: remove a check, flip a role comparison, drop an owner filter.
- Boundaries: `>=` to `>`, off-by-one in limits, a default value changed.
- Validation and escaping: remove one escape or one allow-list entry.
- Fail-closed behavior: a required secret becomes optional, a minimum length shrinks.
- Money and counting logic: a swapped operator, a dropped branch.
- Ordering and de-duplication in pure modules.

Assert defaults (limits, minimum lengths, caps) as literals in the tests, not as imported constants, or a mutant that changes the constant survives because the test follows it.

Group lists by area (for example `auth`, `limits`, `validation`) and give each mutant its narrow test list when the driver supports it.

## Equivalent mutants

Some changes cannot alter behavior: a regex reset the engine already does, a guard that a later check repeats. Do not list them. Put each in the list's header comment with the reason.

Confirm every such claim by running it once in a scratch list and seeing it survive. Two claims on one repository looked unobservable and were not (`c.column` throws on a null card; an array is coerced to a string by `exec()`), so they became real mutants and real tests.

## Survivors

1. A missing test: write the one that fails on the mutant and passes on the real code.
2. Redundant code: before deleting a line, write the test that proves it redundant. Twice a "redundant" line was not (an empty JWT `sub` caused a 500; a `.lower()` was already done upstream).

Never drop a mutant because it survives.

## Pitfalls that produced false results

| What happened | Rule |
| --- | --- |
| A red baseline made every mutant "fail the suite", so a run read 100 percent killed and proved nothing | The driver refuses to run unless the suite is green first. Keep that check |
| Source or tests were edited while a run was in progress | Hands off the tree during a run |
| The new test files were not in each mutant's test list, so the result was identical before and after | Add the new test files to the lists, then re-run |
| A run was killed or the session resumed: the driver restores files only in its `finally`, so one mutant stayed applied in an uncommitted tree | Never kill a running driver. After any resume run `git diff --stat` and `check_patterns.py`. A count of 0 is either an applied mutant (the script says "possibly APPLIED"; `git diff -- <file>` confirms it, then swap `new` back to `old`) or a stale pattern. Re-run the suite before relaunching |
| A formatter or Prettier reshaped the code and patterns stopped matching | Re-anchor after any reformat. For Python lists use `ast` line spans, delete and insert bottom-up, never line-start text |
| Two drivers ran in parallel on one tree | Run them one after the other. In parallel each is about three times slower |
| A coverage gate (`--cov`, `fail_under`) was active while mutating, so a mutant that only lowers coverage counted as "killed" for the wrong reason | Run the suite under the driver with coverage off (`pytest --no-cov`, or the equivalent), and keep the coverage gate in the normal test run and CI |
| A long list took too long | Slice the list over separate copies of the repository (rsync without `.git` and `node_modules`, symlink `node_modules`), one slice per copy, each with its own green baseline. The tree you are working in is then never mutated |
| An all-killed result was believed too quickly | Re-run survivors and the whole list against the full suite from a clean state before reporting |

Log runs to `~/.cache/<repo>-qa/`, not `/tmp`.

## Reporting

In the work-done record give: the number of mutants, how many the original tests killed before you wrote anything (run the list against the original tests alone), how many are killed now, the equivalents documented, and the real bugs the run exposed.
