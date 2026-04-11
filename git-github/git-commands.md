# Git Commands Reference

A structured reference of Git commands covering everyday workflow through advanced topics.

---

## 1. Configuration

_Set up your Git identity and global preferences._

| Command | Description |
|---------|-------------|
| `git config --global user.name "[name]"` | Set commit author name |
| `git config --global user.email "[email]"` | Set commit author email |
| `git config --global init.defaultBranch main` | Set default branch name for new repos |
| `git config --global core.editor "nvim"` | Set default editor |
| `git config --global pull.rebase true` | Rebase instead of merge on pull |
| `git config --global push.autoSetupRemote true` | Auto-create remote tracking on first push |
| `git config --global rerere.enabled true` | Remember conflict resolutions |
| `git config --global diff.algorithm histogram` | Better diff algorithm |
| `git config --list --show-origin` | List all settings and their source file |
| `git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"` | Pretty log alias |

---

## 2. Getting & Creating Projects

| Command | Description |
|---------|-------------|
| `git init` | Initialize a new local repository |
| `git init --bare` | Initialize a bare repository (for remotes) |
| `git clone [url]` | Clone a remote repository |
| `git clone [url] --depth 1` | Shallow clone (latest commit only) |
| `git clone [url] --branch [branch]` | Clone a specific branch |
| `git clone [url] --filter=blob:none` | Partial clone (no file content until needed) |

---

## 3. Basic Workflow (Staging & Committing)

| Command | Description |
|---------|-------------|
| `git status` | Show status of working tree |
| `git status -s` | Short format status |
| `git add [file]` | Stage a specific file |
| `git add .` | Stage all changes in current directory |
| `git add -A` | Stage all changes in entire working tree |
| `git add -p` | Interactively stage hunks (patch mode) |
| `git commit -m "[message]"` | Commit staged changes |
| `git commit -am "[message]"` | Stage modified tracked files and commit |
| `git commit --amend -m "[message]"` | Replace last commit message |
| `git commit --amend --no-edit` | Add staged changes to last commit |

---

## 4. Branching

| Command | Description |
|---------|-------------|
| `git branch` | List local branches |
| `git branch -a` | List all branches (local + remote) |
| `git branch -v` | List branches with last commit |
| `git branch [name]` | Create new branch |
| `git checkout [name]` | Switch to branch |
| `git checkout -b [name]` | Create and switch to new branch |
| `git switch [name]` | Switch to branch (modern syntax) |
| `git switch -c [name]` | Create and switch (modern syntax) |
| `git checkout -b [new] origin/[remote]` | Create local branch from remote |
| `git branch -m [old] [new]` | Rename branch |
| `git branch -d [name]` | Delete merged branch |
| `git branch -D [name]` | Force-delete branch |
| `git checkout -` | Switch to previous branch |

---

## 5. Merging & Rebasing

| Command | Description |
|---------|-------------|
| `git merge [branch]` | Merge branch into current |
| `git merge --no-ff [branch]` | Merge with a merge commit (no fast-forward) |
| `git merge --squash [branch]` | Squash all commits into staged changes |
| `git rebase [base]` | Re-apply commits on top of base |
| `git rebase -i HEAD~[n]` | Interactive rebase for last n commits |
| `git rebase -i [base]` | Interactively rebase onto base branch |
| `git merge --abort` | Abort an in-progress merge |
| `git rebase --abort` | Abort an in-progress rebase |
| `git rebase --continue` | Continue rebase after resolving conflicts |
| `git rebase --skip` | Skip conflicting commit during rebase |
| `git cherry-pick [commit]` | Apply a specific commit to current branch |
| `git cherry-pick [from]..[to]` | Apply a range of commits |

---

## 6. Remote Repositories

| Command | Description |
|---------|-------------|
| `git remote -v` | List remotes with URLs |
| `git remote add [name] [url]` | Add a new remote |
| `git remote rename [old] [new]` | Rename remote |
| `git remote remove [name]` | Remove remote connection |
| `git remote set-url [name] [url]` | Change remote URL |
| `git remote show [name]` | Inspect a remote |
| `git fetch [remote]` | Download from remote (no merge) |
| `git fetch --all` | Fetch from all remotes |
| `git fetch --prune` | Fetch and remove deleted remote branches |
| `git pull [remote] [branch]` | Fetch and merge |
| `git pull --rebase` | Fetch and rebase (cleaner history) |
| `git push [remote] [branch]` | Push to remote |
| `git push -u [remote] [branch]` | Push and set upstream tracking |
| `git push --force-with-lease` | Force push (safe — fails if remote changed) |
| `git push [remote] --delete [branch]` | Delete remote branch |
| `git push [remote] --tags` | Push all tags |

---

## 7. Inspecting History & Changes

| Command | Description |
|---------|-------------|
| `git log` | Show commit history |
| `git log --oneline` | Compact one-line format |
| `git log --graph --oneline --decorate --all` | Visual branch graph |
| `git log -p [file]` | Show changes for a file over time |
| `git log --follow [file]` | Follow file through renames |
| `git log --since="2 weeks ago"` | Commits since date |
| `git log --author="[name]"` | Commits by author |
| `git log --grep="[pattern]"` | Commits matching message pattern |
| `git log -S "[string]"` | Commits that added/removed a string (pickaxe) |
| `git show [commit]` | Show commit metadata and diff |
| `git show [commit]:[file]` | Show file contents at a commit |
| `git diff` | Unstaged changes |
| `git diff --staged` | Staged changes (vs last commit) |
| `git diff [branch1]..[branch2]` | Diff between branch tips |
| `git diff [commit1]..[commit2]` | Diff between commits |
| `git blame [file]` | Show who last changed each line |
| `git blame -L [start],[end] [file]` | Blame for a line range |
| `git shortlog -sn` | Commit count per author |

---

## 8. Undoing Changes & Stashing

| Command | Description |
|---------|-------------|
| `git restore [file]` | Discard working directory changes |
| `git restore --staged [file]` | Unstage a file |
| `git checkout -- [file]` | Discard changes (legacy syntax) |
| `git reset HEAD [file]` | Unstage a file (legacy syntax) |
| `git reset --soft [commit]` | Move HEAD, keep staging area and working dir |
| `git reset --mixed [commit]` | Move HEAD, clear staging, keep working dir |
| `git reset --hard [commit]` | Move HEAD, discard all changes (destructive) |
| `git revert [commit]` | Create a new commit undoing changes |
| `git revert -n [commit]` | Revert without committing (stage only) |
| `git clean -n` | Dry run — show what would be removed |
| `git clean -fd` | Remove untracked files and directories |
| `git commit --amend -m "[msg]"` | Reword last commit |
| `git stash` | Stash current changes |
| `git stash push -m "[message]"` | Stash with a description |
| `git stash push -u` | Stash including untracked files |
| `git stash list` | List all stashes |
| `git stash pop` | Apply latest stash and remove it |
| `git stash apply [stash@{n}]` | Apply a specific stash (keep it) |
| `git stash drop [stash@{n}]` | Delete a stash |
| `git stash clear` | Remove all stashes |
| `git stash branch [name]` | Create branch from stash |

---

## 9. File Management

| Command | Description |
|---------|-------------|
| `git rm [file]` | Remove file from working dir and staging |
| `git rm --cached [file]` | Untrack file (keep on disk) |
| `git rm -r [dir]` | Remove directory recursively |
| `git mv [old] [new]` | Rename/move file |

---

## 10. Tagging

| Command | Description |
|---------|-------------|
| `git tag` | List all tags |
| `git tag [name]` | Create lightweight tag |
| `git tag -a [name] -m "[message]"` | Create annotated tag |
| `git tag -d [name]` | Delete local tag |
| `git push [remote] [name]` | Push specific tag |
| `git push [remote] --tags` | Push all tags |
| `git push [remote] --delete [name]` | Delete remote tag |

---

## 11. Advanced: Reflog & Recovery

The reflog records every HEAD movement — your safety net for lost commits.

| Command | Description |
|---------|-------------|
| `git reflog` | Show all HEAD movements |
| `git reflog [branch]` | Show movements for a specific branch |
| `git checkout [reflog-hash]` | Recover a detached state |
| `git branch [name] [reflog-hash]` | Recover a lost branch |

**Example: recover after `reset --hard`**
```bash
git reflog                        # find hash before the reset
git reset --hard HEAD@{2}         # go back to that state
```

---

## 12. Advanced: Bisect (Bug Hunting)

Binary search through commits to find the one that introduced a bug.

```bash
git bisect start
git bisect bad                    # current commit is broken
git bisect good [last-good-hash]  # last known good commit
# Git checks out a commit in the middle — test it, then:
git bisect good   # or: git bisect bad
# Repeat until Git identifies the bad commit
git bisect reset  # return to original branch
```

**Automate with a test script:**
```bash
git bisect start
git bisect bad HEAD
git bisect good v1.2.0
git bisect run npm test           # runs automatically until it finds the culprit
git bisect reset
```

---

## 13. Advanced: Worktrees

Check out multiple branches simultaneously in separate directories:

```bash
git worktree add [path] [branch]          # new worktree for existing branch
git worktree add -b [branch] [path]       # new worktree with new branch
git worktree list                          # list all worktrees
git worktree remove [path]                 # remove a worktree
git worktree prune                         # clean up stale worktree entries
```

**Example: fix a hotfix while working on a feature**
```bash
git worktree add ../hotfix hotfix/critical-bug
cd ../hotfix
# fix the bug, commit, push
git worktree remove ../hotfix
```

---

## 14. Advanced: Sparse Checkout

Work with large repos by only checking out a subset of files:

```bash
git clone --filter=blob:none --sparse [url]
git sparse-checkout init --cone
git sparse-checkout set [dir1] [dir2]       # only check out these directories
git sparse-checkout add [dir]               # add another directory
git sparse-checkout list                    # show active patterns
git sparse-checkout disable                 # revert to full checkout
```

---

## 15. Advanced: Submodules

Embed other Git repositories within your project:

```bash
git submodule add [url] [path]                  # add submodule
git submodule init                              # initialize after clone
git submodule update --init --recursive         # fetch all submodule content
git submodule update --remote                   # update to latest remote commit
git submodule foreach 'git pull origin main'    # run command in each submodule
git submodule status                            # show submodule states
# Remove a submodule:
git submodule deinit [path]
git rm [path]
rm -rf .git/modules/[path]
```

---

## 16. Advanced: Git Hooks

Hooks are scripts in `.git/hooks/` that run at lifecycle events.

| Hook | Runs When |
|------|-----------|
| `pre-commit` | Before creating a commit |
| `commit-msg` | After writing commit message |
| `pre-push` | Before pushing |
| `post-checkout` | After checkout |
| `pre-rebase` | Before rebase starts |

**Example `pre-commit` hook (run tests):**
```bash
#!/bin/bash
# .git/hooks/pre-commit
npm test
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
```

**Manage hooks with Husky (JS projects):**
```bash
npm install --save-dev husky
npx husky init
echo "npm test" > .husky/pre-commit
```

---

## 17. Advanced: Interactive Staging

Stage specific lines or hunks interactively:

```bash
git add -p [file]     # patch mode — stage individual hunks
git add -i            # interactive staging menu
```

Inside patch mode:
- `y` — stage this hunk
- `n` — skip this hunk
- `s` — split hunk into smaller parts
- `e` — manually edit the hunk
- `q` — quit

---

## 18. Useful Aliases

Add to `~/.gitconfig` under `[alias]`:

```ini
[alias]
  lg     = log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
  undo   = reset --soft HEAD~1
  wip    = !git add -A && git commit -m "WIP"
  unwip  = reset HEAD~1
  aliases= config --get-regexp '^alias\.'
  who    = shortlog -sn --no-merges
  recent = branch --sort=-committerdate
  root   = rev-parse --show-toplevel
```

---

_Use `git help [command]` or `git [command] --help` for full documentation on any command._
