# AI resources

Sources behind the choices in this chapter, checked on 2026-10-29. Each entry
says what it is for. Where a project changes quickly, the version seen is
noted so you can tell when to look again.

## Primary documentation

| Resource | Use it for |
|----------|------------|
| [Claude Code: subagents](https://code.claude.com/docs/en/sub-agents) | The frontmatter schema for `05-ai/claude-code/agents/*.md`: `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory` (`user`, `project` or `local`), `effort`, `isolation` (`worktree` only), `background`, `color` and newer fields such as `initialPrompt` and `omitClaudeMd`. Unknown fields are ignored silently (`claude --debug` logs the ones it does not recognize), so check here when an agent misbehaves |
| [Agent Skills specification](https://agentskills.io/specification) | The `SKILL.md` format for `05-ai/claude-code/skills/`: a folder with YAML `name` (64 characters at most, `a-z0-9-`, no leading, trailing or double hyphen, equal to the directory name) and `description` (1024 characters at most) plus instructions. The format is open and shared by several agent products |
| [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | When to use a plain workflow and when to use an autonomous agent: prompt chaining, routing, parallelisation, orchestrator-workers, evaluator-optimizer. Start with the simplest pattern that works. The page (2024-12-19) now warns that much of its tooling description has changed since and points to Managed Agents; the pattern names still hold |
| [Anthropic: Effective context engineering for AI agents](https://anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Keeping `CLAUDE.md` and skills short and relevant, so the model's context holds only what the current task needs |
| [Model Context Protocol](https://modelcontextprotocol.io) | How MCP servers expose tools and resources to Claude Code. The configured plugin servers use this |

## Reference projects

| Project | Use it for |
|---------|------------|
| [affaan-m/ECC](https://github.com/affaan-m/ECC) (v2.2.3, MIT) | The most complete open catalogue of Claude Code content: 311 skills, 71 agents, 97 legacy command shims, and tiered rules (`rules/common/` plus one folder per language). Use it to find a pattern, then adapt it to a local skill rather than copying it whole |
| [Anthropic skills](https://github.com/anthropics/skills) | Official reference skills, including `skill-creator`, which is the template for writing one |

ECC's structure is the model for this chapter: one folder per skill with a
`SKILL.md`, one file per agent, commands kept separate, and rules split into a
shared base with per-language overrides. The repo does not yet have a rules
layer; Claude Code now supports `.claude/rules/*.md` natively (with `paths` frontmatter, see the [`.claude` directory docs](https://code.claude.com/docs/en/claude-directory)), so add one there before copying any ECC rules.

## Local models

| Resource | Use it for |
|----------|------------|
| [Ollama GPU support](https://docs.ollama.com/gpu) | Vulkan GPU backend: enabled by default when the Vulkan backend is installed; disable with `OLLAMA_VULKAN=0` or `GGML_VK_VISIBLE_DEVICES=-1`. `OLLAMA_VULKAN=1` is redundant. The reason the Vulkan backend exists alongside ROCm on this card |
| [`ollama-vulkan` on Arch](https://archlinux.org/packages/extra/x86_64/ollama-vulkan) | The packaged Vulkan build. Prefer it over the upstream installer, as `01-system/cachyos/packages/ai.txt` notes |

## Rules for keeping this list honest

- Add a resource only if it changes a decision in this repo. A link without a
  use is clutter.
- Record the version or date seen, and recheck entries that name a version.
- Do not copy content from a reference project into the repo without reading
  its licence first.
