# Claude Code + Local Ollama — Setup Status

*Last updated: 2026-09-23 14:54 · Status: **in progress, not finished** — infrastructure is live and verified including the ROCm large-prompt stress test, the model benchmark suite has not run yet*

This document reflects exactly what has been measured so far. Nothing below is estimated — every number has a command or a log line behind it, and every "pending" is labeled as such rather than implied to be done.

---

## 1. Hardware & environment (verified, not assumed)

| | |
|---|---|
| CPU | AMD Ryzen 5 5600 |
| GPU | Radeon RX 6700 XT, 12 GB (gfx1031, RDNA2 — not on ROCm's official support list) |
| RAM | 32 GB DDR4-3600 |
| OS | CachyOS (Arch, rolling), kernel `7.2.6-1-cachyos` |
| Compositor | **Hyprland** — confirmed via `$XDG_CURRENT_DESKTOP`, `$XDG_SESSION_DESKTOP`, and the running process; no Plasma/`kwin` process found despite conflicting notes |
| Shell | zsh 5.9.2 |
| Ollama | `0.34.3` (clears the `gemma4:12b` ≥ 0.30.5 requirement) |
| Claude Code | `2.1.280` |
| GPU power sensor | `/sys/class/drm/card1/device/hwmon/hwmon2/power1_average` — confirmed readable, used for the Wh energy metric in benchmarking |
| Continue.dev | shares this same Ollama server — this is why context length is **not** set globally (see §3) |

---

## 2. GPU backend — the central finding so far

The spec called for Vulkan first (preferred), with ROCm deferred as a challenger only tested later. **That plan changed, for cause:**

### Vulkan — tried, found to crash under realistic load, currently disabled

- Installed cleanly, `setcap cap_perfmon+ep` applied, discovery confirmed (`library=Vulkan`).
- A short/simple crash test (200 tokens, 3 cold-load runs) passed 3/3 with no issue.
- **But** the real Claude Code request — full system prompt + built-in tool schemas, **66,609 tokens** before truncation — reproduced a hard crash **twice in a row**:
  ```
  ggml_vulkan: device lost on Vulkan0
  decode() failed: vk::Queue::submit: ErrorDeviceLost
  llama-server terminated, signal: aborted (core dumped)
  ```
  Both failures landed at 24,576–32,771 tokens into the prompt. The daemon itself survived (the crash is in the per-model runner subprocess), but the request always failed.
- **Conclusion:** the short crash test gave a false pass — it never stressed a large enough prompt to hit this. At the prompt sizes Claude Code actually sends, Vulkan does not currently pass the "no crash" gate on this card. Not discarding it permanently — a driver/Mesa update could change this — but it is not viable today.

### ROCm — now live, verified, initial checks pass

Switched to via a small helper installed for exactly this purpose:
```bash
sudo ollama-backend rocm   # or: sudo ollama-backend vulkan, to switch back
```
- Live config: `OLLAMA_VULKAN=0`, `HSA_OVERRIDE_GFX_VERSION=10.3.0` (this card's gfx1031 reports as its supported sibling gfx1030 — without this, ROCm does not initialize on this GPU at all).
- Verified: `ollama ps` shows **100% GPU**, clean load, no error. First real generation: 33.6 tok/s decode, 135 tok/s prefill, on a trivial prompt.
- **Large-prompt stress test — passed.** The same test that reproduced the Vulkan crash (a ~30k-token prompt built from the Python stdlib, 3 cold-load runs, `ccb-gemma4-12b`, `num_ctx=65536`) was run against ROCm: **3/3 runs succeeded**, `prompt_eval_count: 33849` each time (squarely inside the 24,576–32,771 range that crashed Vulkan twice), `eval_count: 200`, no errors, `ollama.service` still active afterward. Raw results: `~/ollama-setup/rocm_crashtest_gemma4-12b.json`.
- The spec's own known risk (`HSA_OVERRIDE_GFX_VERSION` + ROCm ≥ 6.4.3 reported to SIGSEGV on gfx1031) has **not** reproduced on this box's ROCm 7.2.4, now including at realistic Claude-Code-sized prompts. ROCm clears gate G4 where Vulkan did not — this is the backend going forward.

---

## 3. Server configuration (live now)

`/etc/systemd/system/ollama.service.d/`:

| File | Contents |
|---|---|
| `claude-code.conf` | `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KV_CACHE_TYPE=q8_0`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_KEEP_ALIVE=30m` |
| `backend.conf` | Backend selection only — currently ROCm (see §2). Written/swapped by `ollama-backend`. |

**Deliberately absent: `OLLAMA_CONTEXT_LENGTH`.** This was live on the box *before* this task started (inherited from an unrelated earlier session) and has been removed — setting it globally would force a fixed KV cache size onto every model on this server, including whatever Continue.dev requests. Context is set per-model instead, via Modelfile `num_ctx` (see §4).

Verified on the ROCm switch: flash attention active (`warmup: flash attention is enabled` in the load log) and q8_0 KV cache genuinely applied — confirmed directly from the model's own load line (`K (q8_0): 272.00 MiB, V (q8_0): 272.00 MiB`), not a silent fallback to f16.

**Continue.dev interaction, not yet resolved:** with `OLLAMA_MAX_LOADED_MODELS=1`, any request from Continue.dev while a `ccl`/`cclf` session is active will evict that model and force a reload on the next Claude Code turn (and vice versa). Options (raise to 2 if VRAM allows, or pause Continue during benchmark/`ccl` sessions) are noted but **not applied** — this needs a decision, not a default.

**Setcap caveat:** `cap_perfmon+ep` is applied to `/usr/bin/ollama`, with a pacman hook (`/etc/pacman.d/hooks/ollama-setcap.hook`) to reapply it after every `ollama`/`ollama-vulkan`/`ollama-rocm` package upgrade — otherwise a routine update silently drops it and Vulkan's VRAM reporting degrades with no error message.

---

## 4. Models — ready, held to 3 candidates by request

| Model | Size | Architecture | Native context | Capabilities |
|---|---|---|---|---|
| `gemma4:12b` | 7.6 GB | dense, 11.9B | 262,144 | tools, vision, audio, **thinking (default on)** |
| `qwen3-coder:30b` | 18.6 GB | MoE, 30.5B | 262,144 | tools |
| `gpt-oss:20b` | 13.8 GB | MoE, 20.9B | 131,072 | tools, **thinking (default medium)** |

**Total: 39.9 GB** — well under the 60 GB cap. Two further candidates from the original shortlist (`gemma4:26b`, `devstral-small-2:24b`) were **not** pulled, at your explicit instruction to hold at 3 for now.

Each has a benchmark alias — `ccb-<slug>`, with only `PARAMETER num_ctx 65536` set, so every measurement uses a known, explicit context rather than silently the server default. These share the underlying weight layers with the base tags, so they cost no extra disk.

Worth knowing before comparing raw decode speed later: both `gemma4:12b` and `gpt-oss:20b` have "thinking" enabled by default (on / medium respectively) — their decode token counts will include hidden reasoning tokens, not just visible output. `qwen3-coder:30b` has no thinking mode.

---

## 5. Fixture (for the eventual end-to-end test)

A small, real inventory/checkout Python package was built for the agentic benchmark stage: 241 lines across 6 modules (catalog, pricing, checkout, receipt, stock, cli), with one genuine cross-module bug — an off-by-one discount threshold in `pricing.py` that only surfaces through a test in `checkout.py`'s domain, so fixing it requires actually navigating the code rather than pattern-matching a traceback. 5 tests, 2 failing. Verified: the real one-line fix makes all 5 pass; the buggy baseline is what's committed. Git author is `kneeraazon404` as required.

Grading, when the end-to-end stage runs, will be independent of the agent's own claims: an isolated `pytest` rerun, a `git diff` scope check restricted to `src/`, and a sha256 identity check on every file under `tests/` — an agent "fixing" the test's expected value instead of the real bug will be caught, not credited.

---

## 6. What is written and ready, vs. what has actually run

| Script | Status |
|---|---|
| `discovery.md` | done — full Phase 1 |
| `root-steps.sh`, `root-steps-backend-switch.sh`, `root-steps-fix-helper.sh` | all run successfully (the third fixes a real bug in the second — see §7) |
| `bench.py` (Stage 1 throughput) | written, dependency-checked, **not yet run for real** |
| `run_e2e.py` (Stage 3 agentic) | written, **not yet run** |
| `results.jsonl`, `e2e_results.jsonl` | **do not exist yet** — this is why there's no results table below |
| `REPORT.md` | **does not exist yet** — it gets written from real Stage 1/2/3 data, once that exists |

---

## 7. A mistake made and corrected, in the interest of an honest record

The first version of the `ollama-backend` helper script had a real bug: its usage message used `${1:?usage: ollama-backend {vulkan|rocm}}`, and the literal `{`/`}` characters inside that message confused bash's own brace-matching for the `${...}` expansion — the argument arrived mangled as `rocm}` instead of `rocm`, and the switch failed. The fix (`root-steps-fix-helper.sh`) was tested standalone (all four cases — `rocm`, `vulkan`, no-arg, invalid-arg — verified to behave correctly) before being handed over, and it worked cleanly on the first real run.

---

## 8. Immediate next steps

1. ~~Run the same large-prompt crash test on ROCm that caught Vulkan's failure~~ — **done, passed** (see §2).
2. Proceed to the full Stage 1 throughput sweep (S/M/L prompt sizes, cold load / cold prefill / warm turn, on all 3 models) → `results.jsonl`.
3. Stage 2 (tool-calling accuracy, 10 trials/model) and Stage 3 (3 real end-to-end agentic runs/model against the fixture) follow.
4. Only once all of that is real, measured data: score against the gates, pick a winner and a FAST pick, tune (Phase 6), wire `ccl`/`cclf` into zsh (Phase 7), do final verification (Phase 8), and write the real `REPORT.md`.

This file will be updated again as each of those actually completes — not before.
