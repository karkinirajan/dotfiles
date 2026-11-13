# Batch mode

Running the playbook over many repositories, one at a time, from the main session (a subagent cannot ask the owner anything and should be given one repository per run).

## The ledger

`~/.claude/plans/modernize-ledger.md` is the single source of truth, so a loop can resume after a context reset.

```text
# Modernize ledger (oldest first). [ ] todo  [~] in progress  [x] done  [!] blocked or excluded
- [x] repo-a (2020-01-08) -- commit abc1234; one-paragraph note of what changed, what was found, what is not verified
- [~] repo-b (2021-07-27)
- [ ] repo-c (2022-02-06)
- [!] repo-d (EXCLUDED reason)
```

Order: by first-commit date, oldest first, with any re-ordering the owner asked for recorded in a `> USER REQUEST (date): ...` line under the list. Find the date with `git log --reverse --format=%cs | head -1`.

Standing user requests recorded so far in the ledger: a single combined status file with Done, Todo and Skipped columns and numbered rows; skip forks, and skip repositories the owner names; process particular repositories in a particular place in the order; bring skipped repositories back when asked.

## Scripts

Copies are in `../templates/batch/`. On the owner's machine they already live in `~/.claude/plans/modernize-tools/`; on a fresh machine copy them there.

```bash
python3 ~/.claude/plans/modernize-tools/ledger_update.py DONE <repo> <commit> "<note>" [<next-repo>]
python3 ~/.claude/plans/modernize-tools/ledger_update.py --exclude <repo> "<reason>" [<next-repo>]
```

Both update the ledger and regenerate `~/modern-repo-status.md` (a table with Done, Todo and Skipped columns, numbered rows, a line stating how many are done and what is next, and a section explaining each skip). The ledger note should carry the commit, the headline changes, the real defects found, the ROTATE and SET items, and what was not verified, in one paragraph.

## The loop

1. Take the first `[~]` or `[ ]` repository. Run the playbook (the `repo-modernizer` agent, one repository per run).
2. When the run reports COMPLETE or PARTIAL, record it with `ledger_update.py`, naming the next repository.
3. When a repository is BLOCKED (fork, no way to verify, needs a human step), record why with `--exclude` or leave a note and move on. Never stop the loop for something that can be skipped.
4. Continue until nothing is left, then report per-repository outcomes and the outstanding hand-offs.

Use demo values and fakes so the loop never waits on credentials.

## After each repository

The owner has previously asked, per repository, for: merge to the default branch, push, a CI and hosting check, and removing the local checkout. None of those can be run by the agent (push is denied, and deleting a checkout is destructive). Produce them as an ordered list of commands in the hand-off, per repository, and let the owner run them.

## Usage limits and resumes

A usage limit or a resume interrupts the loop. Because the ledger and each repository's progress file live outside the scratchpad, the next session can read them and continue. Before continuing after a resume, run the checks in `mutation-testing.md` for a driver that may have been interrupted.
