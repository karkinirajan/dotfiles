# 05 · AI

Local and hosted language models as used on this workstation: the Claude Code
harness that drives agent work, the Ollama stack that runs models on the
AMD GPU, and the reading that informs both.

| Chapter | Path | Purpose |
|---------|------|---------|
| Claude Code | [`claude-code/`](claude-code/README.md) | Global instructions, subagents, skills, and settings for every project |
| Ollama | [`ollama/`](ollama/README.md) | ROCm and Vulkan backends, systemd drop-ins, and the benchmark harness |
| Resources | [`RESOURCES.md`](RESOURCES.md) | Primary docs and reference projects, with what each is for |

## How the chapters connect

- `claude-code/` is what runs. Its `settings.json` and `CLAUDE.md` are linked
  into `~/.claude/`.
- `ollama/` is what serves local models. The `claude-code-bench/` area wires a
  local model into Claude Code as a second endpoint, and is kept for reference
  rather than linked.
- `RESOURCES.md` is the reading behind both. Check it before adding a new
  agent, skill or pattern, so the repo does not drift from the sources.
