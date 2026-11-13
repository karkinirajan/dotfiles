# 05.1 · Claude Code

The global Claude Code setup: instructions, subagents, skills and settings that
apply to every project. Project-specific `.claude/` config stays in each
project's own repo.

```text
claude-code/
├── CLAUDE.md          → ~/.claude/CLAUDE.md     always-loaded engineering profile
├── agent-dev.md       how to build a production-grade agent, step by step
├── settings.json      → ~/.claude/settings.json permissions, hooks, plugins, model defaults
├── commands/          → ~/.claude/commands/     custom slash commands (/discover, /shipcheck)
│   ├── discover.md
│   └── shipcheck.md
├── agents/            → ~/.claude/agents/       focused subagents, one file each
│   ├── ai-agent-engineer.md
│   ├── backend-engineer.md
│   ├── data-ml-engineer.md
│   ├── database-engineer.md
│   ├── frontend-auditor.md
│   ├── frontend-engineer.md
│   ├── frontend-engineer-kit.md
│   ├── frontend-verifier.md
│   ├── qa-engineer.md
│   ├── release-engineer.md
│   └── repo-modernizer.md     the whole-repository modernization pass (see below)
└── skills/            → ~/.claude/skills/       one folder per skill, each with SKILL.md
    ├── discover/              map an unfamiliar project before changing it
    ├── shipcheck/             run real build/lint/test gates before "done"
    ├── modernize-repo/        the modernization playbook, references and templates
    ├── visual-qa/             check rendered UI, not just the source
    ├── token-efficient-workflow/ keep context focused and inspect usage
    ├── frontend-master/       Next.js/React/TS/Tailwind/Supabase/Prisma rulebook (rev 3)
    ├── frontend-audit/        automated + multi-agent FRONTEND-MASTER auditor
    ├── frontend-development-standards/ UI, CWV, WCAG 2.2 AA, and motion checklist
    └── …                      stack patterns: FastAPI, Django/DRF, Flask,
                               SQLAlchemy, Pydantic v2, Postgres/MySQL/Mongo/Redis,
                               JWT, OAuth, CORS/CSRF, secrets, Docker, Nginx
```

## How each piece is loaded

| Piece | Loaded when | Format |
|-------|-------------|--------|
| `CLAUDE.md` | every session, at start | plain Markdown |
| `commands/*.md` | you run `/command-name` explicitly | Markdown prompt. `discover.md` and `shipcheck.md` are shadowed by the same-named skills (a skill wins over a command), so the skill copy is the one that runs; keep the two bodies identical or delete the command copy |
| `agents/*.md` | a task matches the agent's `description`, or you name it | YAML frontmatter + system prompt. Fields are checked against the [subagent schema](https://code.claude.com/docs/en/sub-agents) |
| `skills/*/SKILL.md` | a task matches the skill's `description` | YAML frontmatter (`name`, `description`; optional `when_to_use`, `allowed-tools`, `disable-model-invocation`, `paths`, `model`, `effort`, `context` and others, unknown fields are ignored) + instructions. Supporting files sit beside it |
| `settings.json` | every session, at start | JSON. Hooks run the commands listed under each event |

Claude Code loads skills only from **direct children** of `~/.claude/skills/`.
Do not nest skills in category folders, or they will not load. Keep the flat
layout in `skills/`.

The global skills directory is a symlink to this tracked directory, so skills
are available to new Claude Code sessions without a separate enable step. The
`token-efficient-workflow` skill is invoked as `/token-efficient-workflow` or
selected automatically when relevant; its full instructions load only when
used. Edits to a skill in an existing directory are picked up live; a new top-level skills directory needs `/reload-skills`.

## Token-efficient setup

`ccusage` is installed per-user with pnpm and reads local Claude Code usage
records. Run `ccusage claude daily` or `ccusage claude session` to inspect
historical usage; it reports usage but does not itself reduce it. In a Claude
Code session, use `/context`, `/usage`, `/cost`, `/compact`, and `/clear` to
inspect or manage the active context. Use `/token-efficient-workflow` for the
focused search, output, and session practices in the skill.

The optional supporting packages are listed in
[`../../01-system/cachyos/packages/claude-code-tools.txt`](../../01-system/cachyos/packages/claude-code-tools.txt).
They add structural search (`ast-grep`), syntax-aware diffs (`difftastic`),
shell and workflow validation (`shellcheck`, `shfmt`, `actionlint`), and focused
diff, watch, and benchmark tools. Install them with pacman after reviewing the
dependency plan; they are not Claude runtime dependencies.

Install the eight optional packages with:

```sh
sudo pacman -S --needed ast-grep actionlint difftastic git-delta hyperfine shellcheck shfmt watchexec
```

`ccusage` is already installed for the current user. The eight pacman packages
are documented but remain uninstalled until an administrator authenticates.

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

## Repository modernization

`agents/repo-modernizer.md` runs the whole pass on one repository: current verified
versions, secrets out of the tree, security and correctness defects found and fixed
with tests, mutation checks, CI, docs, and commits on a local `chore/modernize`
branch that it never pushes. Its playbook is the `modernize-repo` skill, preloaded
into the agent. The phases are in `SKILL.md`. The details are in `references/`
(defect catalogue, stack playbooks, verification recipes, mutation testing, docs and
hand-off, operating pitfalls, batch mode). Copies of the mutation drivers, CI files
and doc skeletons are in `templates/`. The content was distilled from the 67
repositories modernized in October and November 2026.

Run it by naming the agent and giving an absolute path:
`Use the repo-modernizer agent on ~/<repo>`. A subagent cannot ask questions, so it
decides with the defaults in the skill and lists them for you. A run that reaches its
turn limit returns a partial result, and the progress file at
`~/.cache/<repo>-qa/progress.md` lets it be resumed.

It has `memory: user`, so lessons it adds land in
`~/.claude/agent-memory/repo-modernizer/`. Fold the good ones into
`skills/modernize-repo/references/`, which stays the tracked source of truth.

To build another agent to the same standard, follow [`agent-dev.md`](agent-dev.md):
fifteen ordered steps from the decision to build, through evals, hardening and
packaging, to a launch checklist. Its last appendix scores `repo-modernizer`
against that checklist.

## Enforcing rules

`CLAUDE.md` is advisory: the model follows it most of the time. Anything that
must hold every time goes in `settings.json` instead, which is enforced by the
harness:

- `permissions.deny` blocks `sudo`, every form of `git push`/`pull`/`fetch`/`remote`,
  `git config --global`, and reads of `.env` and the credentials file. Deny rules
  are checked before allow rules, so an allow can't override them.
- Bash rules match the command text as written. `git push *` does not catch
  `git -C . push`, so the `-C` and `-c` forms are listed separately.
- `maxTurns: 40` on each focused agent caps a runaway subagent. `repo-modernizer` is
  the exception (400): a whole-repository pass is hundreds of tool calls.

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
ln -sfn "$PWD/05-ai/claude-code/CLAUDE.md"     ~/.claude/CLAUDE.md
ln -sfn "$PWD/05-ai/claude-code/settings.json" ~/.claude/settings.json
ln -sfn "$PWD/05-ai/claude-code/agents"        ~/.claude/agents
ln -sfn "$PWD/05-ai/claude-code/skills"        ~/.claude/skills
ln -sfn "$PWD/05-ai/claude-code/commands"      ~/.claude/commands
```

`settings.local.json` and `.credentials.json` are per-machine. Set them up
separately; Claude Code prompts for sign-in on first run.
