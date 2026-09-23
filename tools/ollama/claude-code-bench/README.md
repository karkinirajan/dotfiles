# Claude Code + local Ollama — benchmark & wiring

Wires local Ollama models into Claude Code itself, so a local, free model can
stand in for the paid Anthropic API on request — without ever touching plain
`claude`, which keeps using the Pro plan. Once finished, the intent is
`ccl`/`cclf` shell functions that launch Claude Code against a local model.

**Status: in progress, not finished.** For the honest, current picture of
what's actually been measured vs. only written, read
[`ollama-claude-setup.md`](ollama-claude-setup.md) first — it's the
maintained status doc, updated at every real milestone, not a plan dressed
up as a result. [`STATE.md`](STATE.md) is the more granular working log
behind it (spec decisions, exact commands, every dead end).

## Central finding so far

The GPU (RX 6700 XT, gfx1031) does not officially support ROCm, so both
Vulkan and ROCm were tried. **Vulkan crashes** (`ggml_vulkan: device lost`)
on prompts in the 24k-33k token range — which is exactly the size of Claude
Code's own real first request (66,609 raw tokens, truncated to Ollama's
context budget). A short/simple crash test would have missed this; it only
showed up once tested at realistic size. **ROCm passed the same stress
test** (3/3 clean runs at ~34k prompt tokens) and is the backend now live —
see `../systemd/backend-rocm.conf` (active) vs
`../systemd/backend-vulkan.conf.example` (kept as a documented rollback,
not currently used).

## Layout

- `discovery.md` — Phase 1 environment/config audit.
- `bench.py` — Stage 1 throughput benchmark (httpx, resumable `results.jsonl`,
  VRAM/power sampling). Not yet run for real.
- `run_e2e.py` — Stage 3 agentic end-to-end benchmark against `fixtures/`,
  graded independently of the agent's own claims (pytest rerun, git-diff
  scope check, sha256 identity check on test files). Not yet run.
- `modelfiles/ccb-*.Modelfile` — benchmark aliases (`num_ctx 65536` only,
  zero extra disk — share weight layers with the base tag).
- `model-info/ollama-show.txt` — captured `ollama show` for all 3 candidate
  models (gemma4:12b, qwen3-coder:30b, gpt-oss:20b).
- `fixtures/repo-template/` — the agentic-benchmark fixture: a small
  inventory/checkout Python package with a genuine cross-module bug.
- `root-steps/` — the root-run setup scripts, in order, including the
  `02-backend-switch-helper.sh` script with a known, since-fixed bug (kept
  as-is for the audit trail — see `ollama-claude-setup.md` §7).
- `rocm_crashtest_gemma4-12b.json` — raw output of the ROCm large-prompt
  stress test referenced above.
- `scripts/` — Phase 6/7 support (tuning, report generation, zsh install).
  Written, not yet exercised against real results.

## Why context length isn't set globally

See `../README.md` — this server is shared with Continue.dev, so
`OLLAMA_CONTEXT_LENGTH` is deliberately never set in the systemd drop-ins;
context lives per-model in each `ccb-*` Modelfile's `num_ctx` instead.
