---
name: token-efficient-workflow
description: Reduce Claude Code token and context use while preserving correctness. Use for long sessions, large repositories, repetitive work, or when the user asks to save usage or make Claude Code more efficient.
---

# Token-efficient Claude Code workflow

Keep the active context narrowly tied to the task. Do not trade away required verification or accuracy to reduce usage.

## Start and scope

- For a new task, use `/clear` when the prior conversation is unrelated; use `/compact` when its decisions still matter.
- Use `/context` to inspect a large session before adding more material. Use `/usage` for plan/API usage and `/cost` when API billing applies.
- Search filenames and symbols first (`rg --files`, `rg -n`); read only the matching files and relevant sections. Avoid loading whole directories, lockfiles, generated output, vendored code, or large logs.
- Prefer a path and a focused question over pasting file contents. Avoid `@file` unless the whole file is needed.
- Ask for a concise plan before cross-cutting edits; then execute the agreed scope without repeatedly restating repository context.

## Search and tool output

- Use `ast-grep` for structural code searches when text search would return too much; use `rg` for ordinary text searches.
- Bound command output with a path, pattern, line range, or small `head`/`tail`; never dump an entire package tree or generated file into context.
- Prefer `git diff --stat` and targeted diffs, then inspect changed hunks. Use `difft` for syntax-aware comparisons where useful.
- Run the narrowest relevant formatter, type checker, and tests. Report commands and results; do not run unrelated suites.
- For shell scripts, use ShellCheck and `shfmt` on touched files. Use `actionlint` only when GitHub Actions files change.

## Session discipline

- Use Sonnet for routine implementation and Haiku for simple mechanical tasks when available; reserve Opus for genuinely difficult analysis or architecture.
- Keep durable repository facts in concise `CLAUDE.md`; put task-specific procedures in skills or nested instructions so they load only when relevant.
- Prefer one focused subtask per subagent and request short findings; do not parallelize work that shares files or needs the full conversation.
- When a task is complete, summarize decisions and verification briefly, then start a clean session for unrelated work.

## Local usage reports

- Run `ccusage claude daily` or `ccusage claude session` to inspect Claude Code's local usage records. It reads local usage data; it does not reduce usage automatically.
- Use Claude Code's built-in `/context`, `/usage`, `/cost`, `/compact`, and `/clear` commands as the authoritative in-session controls.
