# Claude Code

Global Claude Code configuration — instructions, custom subagents, custom
slash commands, and custom skills that apply across every project, not
project-specific `.claude/` config (those stay in each project's own repo).

```
claude/
├── CLAUDE.md              → ~/.claude/CLAUDE.md
│       Global engineering profile/preferences, applied to every session
│       regardless of project.
├── settings.json          → ~/.claude/settings.json
│       Permissions, hooks (claude-brain session/prompt/end hooks), enabled
│       plugins, model/effort defaults, auto-mode trust context.
├── agents/                → ~/.claude/agents/
│       Custom subagents (backend/frontend/database/ai-agent/release/qa/
│       data-ml engineer) — reach for one when a task is squarely in its
│       lane instead of doing it inline.
├── commands/               → ~/.claude/commands/
│       Custom slash commands (/discover, /shipcheck).
└── skills/                 → ~/.claude/skills/
        Custom skills — stack-specific architecture/security patterns
        (FastAPI, Django/DRF, Flask, SQLAlchemy, Postgres/MySQL/MongoDB/
        Redis, JWT/OAuth/CORS/secrets, Docker, Nginx) plus claude-brain
        (second-brain vault integration) and visual-qa.
```

## Deliberately NOT included

Everything else under `~/.claude/` is either a credential, machine/session
state, or private conversation data — none of it belongs in a shared repo:

| Excluded | Why |
|---|---|
| `.credentials.json` | OAuth tokens for Claude Code itself |
| `settings.local.json` | Machine-specific permission grants (hardcoded paths like `/home/kneeraazon/Workspace/...`) — the whole point of the `.local` suffix is that it doesn't travel |
| `projects/` | Full conversation transcripts across every session — private by nature, and huge (~700MB) |
| `plugins/`, `usage.db`, `telemetry/`, `jobs/`, `backups/`, `history.jsonl`, `stats-cache.json`, `daemon*`, `sessions/`, `tasks/`, `*-cache/`, `session-env/`, `shell-snapshots/`, `file-history/`, `security/`, `chrome/`, `ide/`, `downloads/` | Runtime/cache state, regenerable or session-specific — not configuration |

Plugin *enablement* is still captured in `settings.json`'s `enabledPlugins`
list — only the installed plugin code/cache itself is excluded.

## Install

```sh
cp claude/CLAUDE.md claude/settings.json ~/.claude/
cp -r claude/agents claude/commands claude/skills ~/.claude/
```

`settings.local.json` and `.credentials.json` are per-machine — set those up
independently (Claude Code prompts for auth on first run; permissions grow
naturally as you approve prompts).
