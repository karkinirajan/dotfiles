# A List of Commonly Used Git Commands

This list provides a structured overview of frequently used Git commands, categorized by their typical use in a Git workflow.

## 1. Configuration

*Commands to set up your Git identity and preferences.*

| Command                                     | Description                                         |
| ------------------------------------------- | --------------------------------------------------- |
| **`git config --global user.name "[name]"`** | Set the name that will be attached to your commits  |
| **`git config --global user.email "[email]"`**| Set the email address for your commits              |
| **`git config --global init.defaultBranch main`** | Set the default branch name for new repositories    |
| **`git config --list`** | List all Git configuration settings                 |

## 2. Getting & Creating Projects

*Commands to start a new repository or obtain an existing one.*

| Command                                     | Description                                            |
| ------------------------------------------- | ------------------------------------------------------ |
| **`git init`** | Initialize a new, local Git repository in the current directory |
| **`git clone [repository-url]`** | Create a local copy of a remote repository             |

## 3. Basic Workflow (Staging & Committing)

*Core commands for tracking changes and saving snapshots of your project.*

| Command                                     | Description                                                      |
| ------------------------------------------- | ---------------------------------------------------------------- |
| **`git status`** | Show the status of changes (tracked, untracked, staged)        |
| **`git add [file-name.txt]`** | Add a specific file to the staging area                          |
| **`git add .`** | Add all new and changed files in the current directory to staging |
| **`git add -A`** | Add all new and changed files in the entire working tree to staging |
| **`git commit -m "[commit message]"`** | Record staged changes to the repository with a descriptive message |
| **`git commit -am "[commit message]"`** | Stage all modified tracked files and commit them in one step     |

## 4. Branching

*Commands for managing different lines of development.*

| Command                                     | Description                                                          |
| ------------------------------------------- | -------------------------------------------------------------------- |
| **`git branch`** | List all local branches (the asterisk * denotes the current branch)    |
| **`git branch -a`** | List all branches (local and remote)                                 |
| **`git branch [branch-name]`** | Create a new local branch                                            |
| **`git checkout [branch-name]`** | Switch to an existing branch                                         |
| **`git checkout -b [branch-name]`** | Create a new local branch and switch to it                           |
| **`git checkout -b [new-branch-name] origin/[remote-branch-name]`** | Create a new local branch based on a remote branch and switch to it |
| **`git branch -m [old-branch-name] [new-branch-name]`** | Rename a local branch                                                |
| **`git branch -d [branch-name]`** | Delete a local branch (if it has been merged)                      |
| **`git branch -D [branch-name]`** | Force delete a local branch (even if not merged)                   |
| **`git checkout -`** | Switch to the previously checked out branch                          |

## 5. Merging & Rebasing

*Commands to integrate changes from different branches.*

| Command                                     | Description                                                                   |
| ------------------------------------------- | ----------------------------------------------------------------------------- |
| **`git merge [branch-to-merge-in]`** | Merge the specified branch's history into the current branch                  |
| **`git rebase [base-branch]`** | Re-apply commits from the current branch onto the tip of `[base-branch]`      |
| **`git rebase -i [base-branch]`** | Interactively rebase commits from the current branch onto `[base-branch]`     |
| **`git merge --abort`** | Abort a merge operation that resulted in conflicts                            |
| **`git rebase --abort`** | Abort a rebase operation                                                      |
| **`git rebase --continue`** | Continue a rebase after resolving conflicts                                   |

## 6. Remote Repositories (Sharing & Updating)

*Commands for interacting with remote repositories.*

| Command                                     | Description                                                                |
| ------------------------------------------- | -------------------------------------------------------------------------- |
| **`git remote -v`** | List all configured remote repositories with their URLs                    |
| **`git remote add [name] [url]`** | Add a new remote repository (e.g., `git remote add origin [url]`)          |
| **`git remote show [name]`** | Show detailed information about a remote repository                        |
| **`git remote rename [old-name] [new-name]`**| Rename a remote repository                                                 |
| **`git remote remove [name]`** | Remove a remote repository connection                                      |
| **`git remote set-url [name] [new-url]`** | Change the URL of a remote repository (e.g., to switch between SSH/HTTPS) |
| **`git fetch [remote-name]`** | Download objects and refs from a remote repository (does not merge)        |
| **`git fetch --all`** | Fetch from all configured remotes                                          |
| **`git pull [remote-name] [branch-name]`** | Fetch from the specified remote and merge changes into the current branch   |
| **`git pull`** | Fetch from and integrate with another repository or a local branch (usually the tracked upstream branch) |
| **`git push [remote-name] [branch-name]`** | Upload local branch commits to the remote repository branch                  |
| **`git push -u [remote-name] [branch-name]`**| Push local branch and set it to track the remote branch                   |
| **`git push`** | Push commits from the current local branch to its configured remote upstream |
| **`git push [remote-name] --delete [branch-name]`** | Delete a branch on the remote repository                             |
| **`git push [remote-name] :[branch-name]`** | Alternative syntax to delete a remote branch                               |

## 7. Inspecting History & Changes

*Commands to view project history, changes, and differences.*

| Command                                     | Description                                                                 |
| ------------------------------------------- | --------------------------------------------------------------------------- |
| **`git log`** | Show the commit history for the current branch                              |
| **`git log --oneline`** | Show commit history in a condensed, one-line format                         |
| **`git log --graph --oneline --decorate --all`** | Show a visual representation of the commit history across all branches      |
| **`git log --summary`** | Show commit history with a summary of changes (files created/deleted/mode changed) |
| **`git log -p [file-name.txt]`** | Show changes over time for a specific file (patch view)                     |
| **`git show [commit-hash]`** | Show metadata and content changes of a specific commit                      |
| **`git diff`** | Show changes between the working directory and the staging area (unstaged changes) |
| **`git diff --staged`** (or **`--cached`**) | Show changes between the staging area and the last commit (staged changes) |
| **`git diff [branch1]..[branch2]`** | Show changes between the tips of two branches                               |
| **`git diff [commit1]..[commit2]`** | Show changes between two arbitrary commits                                  |
| **`git blame [file-name.txt]`** | Show who last modified each line of a file and in which commit             |

## 8. Undoing Changes & Stashing

*Commands for reverting changes, fixing mistakes, and temporarily saving work.*

| Command                                     | Description                                                                 |
| ------------------------------------------- | --------------------------------------------------------------------------- |
| **`git checkout -- [file-name.txt]`** | Discard changes in the working directory for a specific file (restores last committed version) |
| **`git reset HEAD [file-name.txt]`** | Unstage a file, but keep its changes in the working directory               |
| **`git reset [commit-hash]`** | Reset current HEAD to the specified commit, discarding commits after it. Staging and working directory are also reset. (**Use with caution**) |
| **`git reset --soft [commit-hash]`** | Reset current HEAD to specified commit, but leave staging area and working directory unchanged. |
| **`git reset --hard [commit-hash]`** | Reset current HEAD, staging area, and working directory to specified commit. **All changes after this commit are lost. (Very Dangerous)** |
| **`git commit --amend -m "[new message]"`** | Replace the last commit with the current staged changes and a new message    |
| **`git commit --amend --no-edit`** | Add current staged changes to the previous commit without changing its message |
| **`git revert [commit-hash]`** | Create a new commit that undoes the changes made in a previous commit      |
| **`git clean -n`** | Show which untracked files would be removed by `git clean` (dry run)       |
| **`git clean -fd`** | Remove untracked files and directories from the working directory. (**Use with caution**) |
| **`git stash`** | Temporarily store modified, tracked files and staged changes                |
| **`git stash save "[message]"`** | Stash changes with a descriptive message                                    |
| **`git stash list`** | List all stashed changesets                                                 |
| **`git stash pop`** | Apply the latest stash and remove it from the stash list                     |
| **`git stash apply [stash@{n}]`** | Apply a specific stash (e.g., `stash@{0}`) but keep it in the stash list |
| **`git stash drop [stash@{n}]`** | Delete a specific stash from the stash list                                 |
| **`git stash clear`** | Remove all stashed entries                                                  |

## 9. File Management (Tracked by Git)

*Commands for managing files within the Git tracking system.*

| Command                                     | Description                                                                 |
| ------------------------------------------- | --------------------------------------------------------------------------- |
| **`git rm [file-name.txt]`** | Remove a file from the working directory and the staging area               |
| **`git rm -r [directory-name]`** | Remove a directory and its contents from the working directory and staging area |
| **`git rm --cached [file-name.txt]`** | Remove a file from the staging area (Git tracking) but keep it in the working directory |
| **`git mv [old-name] [new-name]`** | Rename a file or directory and stage the change                             |

## 10. Tagging

*Commands for creating and managing release points or important commits.*

| Command                                     | Description                                                              |
| ------------------------------------------- | ------------------------------------------------------------------------ |
| **`git tag`** | List all tags in the repository                                          |
| **`git tag [tag-name]`** | Create a lightweight tag at the current commit                           |
| **`git tag -a [tag-name] -m "[message]"`** | Create an annotated tag with a message                                   |
| **`git show [tag-name]`** | Show information about a specific tag                                    |
| **`git tag -d [tag-name]`** | Delete a local tag                                                       |
| **`git push [remote-name] [tag-name]`** | Push a specific tag to a remote repository                               |
| **`git push [remote-name] --tags`** | Push all local tags to a remote repository                               |
| **`git push [remote-name] --delete [tag-name]`** | Delete a tag from a remote repository                                  |

---
*Remember that many commands have additional options and variations. Use `git help [command]` for more details.*
