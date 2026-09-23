# STATE

**Spec version:** v2 (pasted 2026-09-23 13:45, supersedes the v1 spec started ~13:28 same day)

## Key differences from v1 that change already-completed work
- v1 set `OLLAMA_CONTEXT_LENGTH=65536` globally (inherited from a PRE-EXISTING
  drop-in from an earlier, unrelated session — confirmed via `systemctl show
  ollama -p Environment` during v1 Phase 1). v2 explicitly forbids this
  (breaks Continue.dev, which shares this server). MUST be removed via
  root-steps.sh (Phase 3), replaced with per-Modelfile `num_ctx`. Not fixed
  yet — the live server still has it as of this note.
- v1 compared ROCm-spoofed / ROCm-native / Vulkan simultaneously. v2: Vulkan
  is tried FIRST and is the default expectation; ROCm is a "challenger,
  deferred" only tested in Phase 5 Stage 1 after Vulkan has real numbers, and
  only kept if it clears specific win margins (>=15% faster on one of
  prefill/decode at size M, neither >5% worse).
- v1 used system Python + `requests`, ad-hoc results.json (per-model
  overwrite). v2 requires a dedicated venv, httpx/jsonschema, and
  results.jsonl (append-only, resumable, one line per measured cell).
- v1's Phase 5C fixture was a single-file, single-bug, 6-test package. v2
  wants 4+ modules (~300 LOC), a bug that spans two modules, 5 tests (2
  failing), and a deliberate "wrong fix" trap. Needs to be rebuilt.
- v1 candidate list: gemma4:12b, qwen3-coder:30b, devstral:24b, gpt-oss:20b.
  v2 candidate list: gemma4:12b, qwen3-coder:30b, gemma4:26b, gpt-oss:20b,
  devstral-small-2. Different — devstral:24b vs devstral-small-2 need
  re-verifying, gemma4:26b is new.

## Background work still running from v1, being kept (data still useful)
- `ollama pull qwen3-coder:30b` into the REAL store (/var/lib/ollama):
  COMPLETE, 18.5GB, capabilities=[completion, tools] confirmed via API.
- `ollama pull gemma4:12b / devstral:24b / gpt-oss:20b` into the REAL store:
  in progress in background (task bf6j60i0m).
- `scripts/phase2_backend_compare.py` (ROCm-spoof / ROCm-native / Vulkan,
  simultaneous 3-way): in progress in background (task bj51y9ht3). Useful as
  extra evidence even though v2's procedure is staged, not simultaneous —
  will fold its Vulkan and ROCm-native numbers in as a cross-check, not as
  the primary decision mechanism.
- Isolated test-model store at ~/ollama-setup/test-models has gemma4:12b
  (7.6GB) — reusable for any further non-root backend testing.

## Current phase
Phase 1 discovery (v2), in progress.

## v1 3-way backend smoke test result (gemma4:12b, single short prompt, decode only)
All three started cleanly, no crash, decode tok/s within noise of each other:
  rocm_spoof_gfx1030   compute=gfx1030   32.79 tok/s
  rocm_native_gfx1031  compute=gfx1031   32.85 tok/s
  vulkan               compute=0.0       32.40 tok/s
Treating this as G4 (no-crash) evidence only, not as the v2 decision — v2's
staged Stage-1 procedure (cold load, cold prefill w/ nonce, warm turn, size
S/M/L, energy, VRAM sampling) still needs to run properly per the new spec.

## Phase 2 Step 1 (Vulkan) — STOPPED, waiting on root-steps.sh

Phase 1 (v2) complete: ~/ollama-setup/discovery.md (523 lines).

root-steps.sh is written and ready at ~/ollama-setup/root-steps.sh. It:
1. Replaces the two existing broken drop-ins with one consolidated
   claude-code.conf: FLASH_ATTENTION=1, KV_CACHE_TYPE=q8_0, NUM_PARALLEL=1,
   MAX_LOADED_MODELS=1, KEEP_ALIVE=30m, OLLAMA_LLM_LIBRARY=vulkan.
   Deliberately does NOT set OLLAMA_CONTEXT_LENGTH (see discovery.md
   diagnosis — that was a hard-rule violation inherited from an earlier,
   unrelated session).
2. setcap cap_perfmon+ep on /usr/bin/ollama.
3. A pacman hook to re-apply that setcap after every ollama/ollama-vulkan/
   ollama-rocm upgrade.
4. daemon-reload + restart + verifies Vulkan discovery.

No package installs needed — ollama-vulkan, vulkan-radeon, ollama-rocm are
all already present (confirmed in discovery.md).

**Waiting for the user to run this and confirm** before continuing to Phase
2 Step 1's own crash/discovery verification and into Phase 3/4/5.

Background pulls (v1, still valuable, unaffected by any of this):
qwen3-coder:30b DONE (18.6GB in real store). gemma4:12b / devstral:24b /
gpt-oss:20b still pulling into the real store (task bf6j60i0m). Will
re-verify tags against v2's actual candidate list (gemma4:12b,
qwen3-coder:30b, gemma4:26b, gpt-oss:20b, devstral-small-2 — NOTE:
devstral:24b, currently pulling, is NOT on the v2 list; devstral-small-2 is.
Needs checking once background pulls are dealt with — may need to swap.)

## User decision: hold candidates to 3 for now
Confirmed: gemma4:12b, qwen3-coder:30b, gpt-oss:20b only. NOT pulling
gemma4:26b or devstral-small-2:24b at this time (would exceed 60GB cap).
Revisit after Stage-1 results if the 3-model set doesn't produce a clear
winner.

root-steps.sh: NOT YET RUN by the user as of this check (OLLAMA_CONTEXT_LENGTH
still live, no OLLAMA_LLM_LIBRARY=vulkan, no setcap, no pacman hook). Still
waiting.

## Prep completed while waiting on root-steps.sh + gpt-oss:20b pull
- ccb-gemma4-12b, ccb-qwen3-coder-30b Modelfile aliases created (num_ctx
  65536 only, per spec). Zero extra disk cost — Ollama shares weight layers.
- `ollama show` captured for both into model-info/ollama-show.txt.
  gemma4:12b: dense 11.9B, context 262144, capabilities incl. thinking
  (default true) — thinking tokens will count in eval_count/decode timing,
  worth remembering when comparing raw decode tok/s across models.
  qwen3-coder:30b: qwen3moe, 30.5B, context 262144, default temp=0.7 —
  bench.py explicitly overrides to temperature=0/seed=42 for Stage 1
  determinism (not baked into the Modelfile, which per spec holds only
  num_ctx).
- Fixture rebuilt per v2 spec: ~/ollama-setup/fixtures/repo-template.
  241 LOC across 6 modules (catalog/pricing/checkout/receipt/stock/cli),
  bug in pricing.py (off-by-one, `>` vs `>=`), surfaces via checkout.py's
  test — genuine cross-module navigation required. 5 tests, 2 failing.
  Verified: applying the real 1-char fix (>= instead of >) makes all 5 pass.
  git author kneeraazon404 as required. NOTE: an incidental `rm -rf` while
  rebuilding this also deleted a stray, duplicate `.remember/` plugin-state
  directory that had gotten created inside the OLD fixture dir (not the
  real ~/.remember/, which is untouched — verified). Harmless (logs/temp
  markers only), flagging for transparency.
- bench.py rewritten to spec: httpx (not requests), results.jsonl
  (append-only, resumable via a `(model,stage,size,run_kind,run_index)`
  key), Sampler class integrating VRAM (always) and power->Wh (sensor
  confirmed present: /sys/class/drm/card1/device/hwmon/hwmon2/power1_average)
  every 250ms during each call, MIN_EVAL_COUNT=128 discard-and-rerun logic,
  builds prompts from real files under sysconfig stdlib path (not lorem
  ipsum). Stage 0 calibration not yet run (needs a real Claude Code turn
  against ccb-gemma4-12b with stream-json — blocked on root-steps.sh since
  I want the FINAL backend live before spending a real calibration call).
- run_e2e.py rewritten to spec: independent pytest rerun (exact "5 passed",
  no skip/xfail) + git-diff src/-only scope check + sha256 identity check
  on tests/ + conftest.py/pytest.ini/pyproject.toml, 3 runs with
  auto-extend-to-5 on an exact 2/3 result, stream-json parsing for
  turns/tokens/truncation-risk, --max-turns correctly OMITTED (does not
  exist in this CLI version, confirmed Phase 1), --allowedTools passed as
  separate args (confirmed empirically, not comma-joined).

## Still blocked
- root-steps.sh not yet run by the user (systemctl show still shows the OLD
  OLLAMA_CONTEXT_LENGTH=65536, no OLLAMA_LLM_LIBRARY=vulkan).
- gpt-oss:20b pull: 68% as of this note (~3min left per its own ETA).

## All 3 held-to candidates fully ready
gemma4:12b (7.6GB, dense, ctx 262144, thinking default=true) /
qwen3-coder:30b (18.6GB, MoE, ctx 262144) / gpt-oss:20b (13.8GB, MoE, ctx
131072, thinking default=medium). Real store total: 39.9GB. All three have
ccb-<slug> Modelfile aliases (num_ctx 65536, zero extra disk — shared
layers). ollama show output for all 3 captured in model-info/ollama-show.txt.

Genuinely idle now on anything non-root. Waiting purely on root-steps.sh.

## Phase 2 Step 1 (Vulkan) — VERIFIED, root-steps.sh run successfully
User ran root-steps.sh at 14:12:17. Independently re-verified (not just
trusting the script's own echo):
  getcap: cap_perfmon=ep on /usr/bin/ollama — confirmed
  pacman hook: present at /etc/pacman.d/hooks/ollama-setcap.hook
  systemctl show: OLLAMA_CONTEXT_LENGTH is GONE (the hard-rule violation is
    fixed); OLLAMA_LLM_LIBRARY=vulkan present
  Real generate call against ccb-gemma4-12b: "OK" returned correctly,
    eval_count=49/prompt_eval_count=26, no crash
  journalctl: "warmup: flash attention is enabled", and the KV cache line
    directly states K (q8_0): 272.00 MiB, V (q8_0): 272.00 MiB — q8_0
    confirmed genuinely active, not a silent f16 fallback
  ollama ps: ccb-gemma4-12b 100% GPU, context=65536, 8.38GB VRAM used
  No-crash check on all 3 candidates: qwen3-coder:30b responded correctly;
    gpt-oss:20b loaded and responded (empty text because its default
    thinking=medium ate a small num_predict budget, NOT a crash) at
    29%/71% CPU/GPU split — real, measured partial offload, no crash.

Phase 2 Step 1 goal met: GPU confirmed doing inference, via journalctl AND
ollama ps, on all 3 candidates, on Vulkan. ROCm stays deferred per spec —
not tested yet, only revisited in Phase 5 Stage 1 if Vulkan's numbers
warrant a challenge.

Moving to Stage 0 calibration now.

## Real Vulkan crash observed — recorded honestly, not silently retried away
During the FIRST Stage 0 calibration attempt, a direct streaming call to
ccb-gemma4-12b hit a genuine Vulkan crash:
  `vk::Queue::submit: ErrorDeviceLost` -> journalctl confirmed
  `llama-server terminated" error="signal: aborted (core dumped)"`.
The parent ollama daemon survived (Restart=on-failure at the unit level;
the crashed process was the per-model runner subprocess, not `ollama serve`
itself). This happened right after several back-to-back model
loads/unloads during the no-crash sanity checks (gemma4:12b ->
qwen3-coder:30b -> gpt-oss:20b in quick succession).

Two follow-up tests, both clean:
  - 3 immediate streaming retries: 3/3 succeeded normally.
  - A properly structured test matching the brief's own ROCm crash-test
    rigor (cold `ollama stop`, then generate 200 tokens, 3 times): 3/3
    succeeded, eval_count=200 every time, no error.

Read: this looks like a transient driver hiccup specifically under rapid
model-swap load, not a steady-state Vulkan reliability problem — Stage 1's
actual procedure (sequential per-model cold-load-then-generate, the exact
pattern just tested clean) does not reproduce it. Proceeding with Vulkan
Stage 1 benchmarking on that basis, but recording this transient crash
plainly as an observed caveat in REPORT.md rather than pretending it never
happened. If it recurs during the real Stage 1 run, that changes this
assessment and Vulkan would need to be reconsidered.

## VULKAN FAILS G4 (no crash) at realistic context depth — real, reproduced
Stage 0 calibration against ccb-gemma4-12b, using the REAL Claude Code
request (full system prompt + built-in tool schemas), failed twice
identically: `ggml_vulkan: device lost on Vulkan0` ->
`decode() failed: vk::Queue::submit: ErrorDeviceLost`, both times at
n_tokens in the 24576-32771 range (Claude Code's raw first-request prompt
is 66,609 tokens; Ollama's log shows it truncating to the 65536-4=32771
budget). The daemon survives (runner subprocess crash, not the service),
but every retry at this size fails the same way.

This is NOT the same thing as the earlier one-off crash (which happened
mid rapid-model-swap and did not reproduce on 3 clean retries) — this one
is 2/2 reproduced, specifically triggered by LARGE prompts. My initial
crash test (200 tokens generated, short prompt) never stressed a large
context and so passed cleanly while missing this. Correcting course:
Vulkan does not pass G4 at realistic Claude-Code-sized prompts on this
card, as measured right now.

This legitimately brings ROCm testing forward from "deferred until Stage 1
has Vulkan numbers" — that deferral was premised on Vulkan being usable at
all at the sizes that matter, which it is not. Not lowering gate G4;
refusing to credit Vulkan with a pass it did not earn under realistic load.

Building the /usr/local/sbin/ollama-backend {vulkan|rocm} helper the spec
itself calls for (needed for switching now, and any future switch, in one
root ask rather than a fresh script each time).

## ollama-backend helper bug, fix, and ROCm switch — VERIFIED
root-steps-backend-switch.sh (installs the helper, cleans
OLLAMA_LLM_LIBRARY=vulkan out of claude-code.conf, invokes `ollama-backend
rocm`) FAILED on its final step: `${1:?usage: ollama-backend
{vulkan|rocm}}` has literal unescaped `{`/`}` inside the `${...}` expansion's
error message, confusing bash's brace-matching — the arg arrived as `rocm}`
instead of `rocm`, so `case` fell to `*)` and exited 2, aborting the outer
script under `set -e` right before writing backend.conf or restarting.
Steps 1-2 (helper installed, claude-code.conf cleaned) had succeeded; the
service was left running on stale cached environment.

Fix: root-steps-fix-helper.sh, using `if [ -z "$BACKEND" ]; then ...; fi`
instead of the `${1:?...}` construct. Tested standalone in
/tmp/test-ollama-backend.sh first (all 4 cases: rocm, vulkan, no-arg,
bogus-arg — all correct) before handing over. User ran it; independently
re-verified via `systemctl show ollama -p Environment`:
OLLAMA_VULKAN=0 HSA_OVERRIDE_GFX_VERSION=10.3.0 — ROCm is live.

Quick ROCm sanity check (small prompt): `ollama ps` 100% GPU, 33.6 tok/s
decode, 135 tok/s prefill, no crash.

## ROCm large-prompt stress test — PASSED, ROCm clears G4 where Vulkan didn't
Ran the same class of test that broke Vulkan: ~30k-token prompt (built via
bench.py's build_prompt_from_python_stdlib, same generator used for the real
Stage 1 harness), 3 cold-load runs against ccb-gemma4-12b, num_ctx=65536,
num_predict=200, temperature=0, seed=42 (script: /tmp/rocm_crashtest.py,
background task bldb42mzb, output:
~/ollama-setup/rocm_crashtest_gemma4-12b.json).

Result: 3/3 runs ok=true, prompt_eval_count=33849 every time (inside the
24576-32771 range that crashed Vulkan 2/2), eval_count=200, no errors.
`systemctl is-active ollama` confirmed active afterward — no daemon or
runner-subprocess crash.

Decision: ROCm is the backend going forward. Vulkan's `backend-vulkan.conf`
is kept only as a documented rollback option, not as a live candidate,
pending a future Mesa/driver update that might warrant re-testing it.

ollama-claude-setup.md updated with this result (§2, §8) — next steps now
point straight at the full Stage 1 throughput sweep.
