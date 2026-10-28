# DECISIONS

One entry per ambiguous call. Format: id, decision, reason, what would reverse it.

| Id | Decision | Reason | Reverse if |
|---|---|---|---|
| D-01 | Target repo is `karkinirajan/dotfiles` (the only repo in scope) | Contents match "topics, setup and learning reference" | n/a |
| D-02 | The repo's Hyprland + Noctalia desktop overrides the KDE Plasma 6 baseline in the brief | `02-desktop/hyprland/KDE-REMOVAL.md`, `system-summary.md` and `fresh-setup.md` all state Plasma was removed; the instructions say to flag contradictions, not to follow the baseline over the repo | The owner says the repo is outdated and Plasma is back |
| D-03 | Date of record is 2026-10-29 for `last_verified` | Brief says today is 2026-10-29; the repo's newest commit is 2026-10-29 +0545 (Nepal local date). Sandbox UTC clock reads 2026-10-28 | n/a |
| D-04 | Commits carry no AI attribution trailers and the PR description carries no generated-with footer | `05-ai/claude-code/CLAUDE.md` is the owner's explicit permanent rule against any AI attribution in commits, and the session reminder says the owner's CLAUDE.md rules take precedence over its attribution lines. A squash merge could copy a PR footer into a commit, so the PR body omits it too | Owner removes the rule |
| D-05 | Git identity: `karkinirajan <karkinirajan1999@gmail.com>`, repo-local | The brief fixes the author to `karkinirajan` and names this email when no local email is set; none was set. The repo CLAUDE.md names `kneeraazon@gmail.com`; the brief is the current request and wins | Owner prefers the other address |
| D-06 | Work happens on `modernize/2026-10` and is pushed to that branch; the session's default branch `claude/nifty-feynman-n215z4` is left untouched | The brief names the branch and the PR from it explicitly | n/a |
| D-07 | The repo `CLAUDE.md` rule "never run git push or sudo myself" is treated as scoped to the owner's machine sessions, not to this cloud run | The brief requires pushing `modernize/2026-10` and opening a PR. No `sudo` is used in the cloud | n/a |
| D-08 | The owner-checkpoint prose already in `fresh-setup.md` is kept as the owner's content; `HANDOFF.md` is the plain full-auto reference and states it supersedes those checkpoints for the next run | The brief forbids adding new safety scaffolding but also forbids deleting content without a ledger entry | Owner wants `fresh-setup.md` stripped to match |
| D-09 | The numbered-part book layout is kept (curriculum rule). Changes are inside it: split `setup.md` into one-topic-per-file chapters, add a generated index, add `versions.yaml` | The owner's standing instruction and the repo README both require a book curriculum with a table of contents. Re-numbering parts would break more links than it fixes | n/a |
| D-10 | Notion: Agent Operating Guide v0.0.4 read at session start; no Notion Skills are enabled; no Notion writes are made in this session | Guide says skills destination is not approved and memory writes need verified durable facts. This session writes to the repo only | n/a |
| D-11 | Unresolved fact "GitHub account kneeraazon404 or karkinirajan" (Notion guide): the brief says `karkinirajan`, which is used; the remote is `github.com/karkinirajan/dotfiles` | Current request governs | n/a |
