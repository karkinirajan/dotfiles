# Ollama — local LLM inference on an RX 6700 XT

GPU-accelerated Ollama on hardware AMD does not officially support, tuned by
measurement rather than guesswork. Everything below was benchmarked on this
machine on 2026-09-09; the numbers are real, not vendor claims.

```
tools/ollama/
├── systemd/
│   ├── override.conf   → /etc/systemd/system/ollama.service.d/
│   │                     the gfx1031→gfx1030 lie that makes ROCm work at all
│   └── context.conf    → /etc/systemd/system/ollama.service.d/
│                         64K context + flash attention + q8_0 KV cache
├── bench.py            measure generation speed AND GPU placement
└── README.md
```

## Hardware

| | |
|---|---|
| GPU | Radeon RX 6700 XT, 12 GB, **gfx1031** (not officially ROCm-supported) |
| CPU | Ryzen 5 5600, 6C/12T |
| RAM | 32 GB DDR4 @ **2666 MT/s** — the weak axis, ~30-40 GB/s |
| Packages | `ollama` + `ollama-rocm` (system ROCm 7.2) |

## Install

```sh
sudo pacman -S --needed ollama-rocm          # NOT plain `ollama` — that is CPU-only
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo cp systemd/*.conf /etc/systemd/system/ollama.service.d/
sudo systemctl daemon-reload && sudo systemctl enable --now ollama
```

Confirm the GPU is actually in use — startup detection is not proof, so load a
model and check the layer count:

```sh
journalctl -u ollama | grep 'inference compute'   # expect library=ROCm compute=gfx1030
./bench.py qwen3.5:9b                             # expect gpu=34/34, ~47 tok/s
```

**Do not install via the upstream `install.sh` script.** It puts a binary in
`/usr/local/bin`, which shadows the packaged one in `/usr/bin`, and pins the
service to it. This machine silently ran a five-month-old 0.21.0 server that
way while `pacman` reported 0.33.3 installed. It also ships 7.4 GB of bundled
CUDA/MLX libraries that are dead weight on an AMD card.

## Tuning — measured, not assumed

Sweep of `glm-4.7-flash`, generation tokens/sec:

| Flash attn | KV cache | Context | GPU layers | tok/s | |
|---|---|---|---|---|---|
| off | f16 | 64K | 48/48 | 19.7 | baseline |
| **on** | f16 | 64K | 48/48 | 23.5 | **+19%** |
| **on** | **q8_0** | 64K | 48/48 | **25.1** | **+27% — chosen** |
| on | q8_0 | 128K | 48/48 | 17.9 | −29%, no benefit |
| off | f16 | 128K | **27/48** | 10.4 | spills to CPU, halves speed |

- **Flash attention works on gfx1031** despite the card being unofficial. It is
  the single biggest win and costs nothing.
- **`q8_0` KV cache** adds another 7%, near-lossless.
- **128K context is never worth it.** It costs throughput even when it fits,
  and without flash attention it forces a genuine partial offload — the only
  configuration tested where layers left the GPU.

Context below 128K is effectively free: 4K→64K held 48/48 layers with VRAM flat
at ~11.7-11.9 GB. Ollama sizes the allocation to fit the card rather than
spilling.

## Models

| Model | Size | Arch | Generation | Prompt eval | VRAM |
|---|---|---|---|---|---|
| `glm-4.7-flash` | 19 GB | 30B-**A3B** MoE | 25.9 tok/s | 65 tok/s | 11.8 GB |
| `qwen3.5:9b` | 6.6 GB | 9B dense | 46.7 tok/s | 241 tok/s | 9.2 GB |

**A 19 GB model runs fully on a 12 GB card.** That is the MoE payoff: only ~3B
of 30B parameters are active per token, so expert tensors stream instead of
sitting resident. All 48 layers report as GPU-offloaded.

The corollary matters when choosing models: a *dense* 19 GB model would be
crippled here, because every token would drag the full weight set across
2666 MT/s system RAM. Judge a model by bytes-read-per-token, not file size —
`a3b`/`a4b` in a tag name means MoE with that many active parameters, even
where the model page does not say so.

Which to use:
- **`glm-4.7-flash`** for coding and agentic work (SWE-bench Verified 59.2).
- **`qwen3.5:9b`** for quick queries and anything with a large prompt — its
  241 tok/s ingestion is 3.7× faster, which dominates on big inputs.

Ollama unloads after 5 minutes idle, so both can live on disk without
competing for VRAM. Switching is just the model name.

**The real ceiling is prompt ingestion, not VRAM.** At ~65 tok/s, filling
GLM's 64K context takes roughly 17 minutes before the first output token.

## Cloud

`ollama signin` then `ollama run <model>:cloud` — free tier, 1 concurrent
request. Useful for models that cannot run here at all: GLM-5.x is cloud-only
(744B/40B active, ~370 GB quantized), as are DeepSeek V4 and Kimi K3.
