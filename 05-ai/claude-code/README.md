# 05.1 · Claude Code

The global Claude Code setup: instructions, subagents, skills and settings that
apply to every project. Project-specific `.claude/` config stays in each
project's own repo.

```
claude-code/
├── CLAUDE.md          → ~/.claude/CLAUDE.md     always-loaded engineering profile
├── settings.json      → ~/.claude/settings.json permissions, hooks, plugins, model defaults
├── agents/            → ~/.claude/agents/       focused subagents, one file each
│   ├── ai-agent-engineer.md
│   ├── backend-engineer.md
│   ├── data-ml-engineer.md
│   ├── database-engineer.md
│   ├── frontend-engineer.md
│   ├── qa-engineer.md
│   └── release-engineer.md
└── skills/            → ~/.claude/skills/       one folder per skill, each with SKILL.md
    ├── claude-brain/          second-brain vault integration
    ├── discover/              map an unfamiliar project before changing it
    ├── shipcheck/             run real build/lint/test gates before "done"
    ├── visual-qa/             check rendered UI, not just the source
    └── …                      stack patterns: FastAPI, Django/DRF, Flask,
                               SQLAlchemy, Pydantic v2, Postgres/MySQL/Mongo/Redis,
                               JWT, OAuth, CORS/CSRF, secrets, Docker, Nginx
```

## How each piece is loaded

| Piece | Loaded when | Format |
|-------|-------------|--------|
| `CLAUDE.md` | every session, at start | plain Markdown |
| `agents/*.md` | a task matches the agent's `description`, or you name it | YAML frontmatter + system prompt. Fields are checked against the [subagent schema](https://code.claude.com/docs/en/sub-agents) |
| `skills/*/SKILL.md` | a task matches the skill's `description` | YAML frontmatter (`name`, `description`) + instructions. Supporting files sit beside it |
| `settings.json` | every session, at start | JSON. Hooks run the commands listed under each event |

Claude Code loads skills only from **direct children** of `~/.claude/skills/`.
Do not nest skills in category folders, or they will not load. Keep the flat
layout and sort skills by name prefix instead.

## Deliberately not tracked

Everything else under `~/.claude/` is a credential, machine state, or private
conversation data:

| Excluded | Why |
|----------|-----|
| `.credentials.json` | OAuth tokens |
| `settings.local.json` | per-machine permission grants with absolute paths |
| `projects/`, `history.jsonl`, `sessions/` | conversation transcripts, private and large |
| `skills/synced/` | written by the desktop app's sync; ignored in `.gitignore` |
| `plugins/`, `usage.db`, `stats-cache.json`, `daemon*`, `*-cache/`, `backups/`, `*.bak-*` | runtime state, regenerable |

`settings.json`'s `enabledPlugins` still records which plugins are on. Only the
installed plugin code is left out.

## Enforcing rules

`CLAUDE.md` is advisory: the model follows it most of the time. Anything that
must hold every time goes in `settings.json` instead, which is enforced by the
harness:

- `permissions.deny` blocks `sudo`, every form of `git push`/`pull`/`fetch`,
  and reads of `.env` and the credentials file. Deny rules are checked before
  allow rules, so an allow can't override them.
- Bash rules match the command text as written. `git push *` does not catch
  `git -C . push`, so the `-C` and `-c` forms are listed separately.
- `maxTurns: 40` on each agent caps a runaway subagent.

Check the file with `claude plugin validate agents` and
`claude plugin validate skills` after editing either.

## Maintaining it

- Check each agent and skill against the current docs when Claude Code
  updates. Unknown frontmatter fields are ignored without error, so a typo
  fails silently.
- Keep `CLAUDE.md` short. Anything that only applies to one stack belongs in a
  skill, which loads on demand.
- Sources for the schemas and the wider reading list are in
  [`../RESOURCES.md`](../RESOURCES.md).

## Install

`install.sh` links these from the manifest. To do it by hand:

```sh
ln -sfn "$PWD/05-ai/claude-code/CLAUDE.md"   ~/.claude/CLAUDE.md
ln -sfn "$PWD/05-ai/claude-code/settings.json" ~/.claude/settings.json
ln -sfn "$PWD/05-ai/claude-code/agents"      ~/.claude/agents
ln -sfn "$PWD/05-ai/claude-code/skills"      ~/.claude/skills
```

`settings.local.json` and `.credentials.json` are per-machine. Set them up
separately; Claude Code prompts for sign-in on first run.
