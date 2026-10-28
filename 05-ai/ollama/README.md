---
title: Ollama on the RX 6700 XT
part: "05"
chapter: "02"
topic: ollama
versions: [ollama, rocm, mesa]
last_verified: 2026-10-29
status: current
sources:
  - https://docs.ollama.com/gpu
  - https://docs.ollama.com/faq
  - https://docs.ollama.com/context-length
---

# 05.2 · Ollama: local LLM inference on an RX 6700 XT

Package version: Ollama <!-- v:ollama -->0.40.11<!-- /v --> (Arch and CachyOS; upstream <!-- v:ollama:upstream -->0.40.13<!-- /v -->). The benchmark numbers in this chapter and in `claude-code-bench/` are dated measurements on older versions; each one says what it was measured with.

GPU-accelerated Ollama on hardware AMD does not officially support, tuned by
measurement rather than guesswork. Two layers here: the base server setup
(this file), and a separate, more involved effort to wire local models into
Claude Code itself as `ccl`/`cclf` (`claude-code-bench/`, see its own
README; **that effort is in progress, not finished** as of the last commit
touching it).

```text
05-ai/ollama/
├── systemd/
│   ├── claude-code.conf         → /etc/systemd/system/ollama.service.d/
│   │                               flash attention, q8_0 KV, parallelism/
│   │                               eviction limits. Deliberately does NOT
│   │                               set context length globally, see below.
│   ├── backend-rocm.conf        → /etc/systemd/system/ollama.service.d/backend.conf
│   │                               the currently-ACTIVE backend selection
│   ├── backend-vulkan.conf.example   the alternate, not currently active,
│   │                               kept for reference/rollback (see
│   │                               claude-code-bench/ for why)
│   └── ollama-setcap.hook       → /etc/pacman.d/hooks/   (Vulkan backend only)
│                                   re-applies cap_perfmon on every
│                                   ollama/-vulkan/-rocm package upgrade
├── bin/
│   └── ollama-backend           → /usr/local/sbin/ollama-backend
│                                   `ollama-backend {vulkan|rocm}`, swaps
│                                   backend.conf and restarts the service
├── bench.py                     quick standalone HTTP benchmark & GPU placement check
├── claude-code-bench/           local models wired into Claude Code itself
│                                   (ccl/cclf), see its own README
└── README.md
```

## Hardware

| | |
|---|---|
| GPU | Radeon RX 6700 XT, 12 GB, **gfx1031** (not officially ROCm-supported) |
| CPU | Ryzen 5 5600, 6C/12T |
| RAM | 32 GB DDR4 @ **3600 MT/s**, system RAM bandwidth ~30-40 GB/s |
| Packages | `ollama`, `ollama-rocm`, `ollama-vulkan`, all three installed side by side; which one is *live* is whatever `backend.conf` currently says |

## Install

```sh
sudo pacman -S --needed ollama-rocm ollama-vulkan   # NOT plain `ollama` alone
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo cp systemd/claude-code.conf systemd/backend-rocm.conf \
       /etc/systemd/system/ollama.service.d/
sudo mv /etc/systemd/system/ollama.service.d/backend-rocm.conf \
        /etc/systemd/system/ollama.service.d/backend.conf
sudo cp bin/ollama-backend /usr/local/sbin/ollama-backend
sudo chmod 755 /usr/local/sbin/ollama-backend
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

The `cap_perfmon` capability and its pacman hook are **not** part of the ROCm install. Ollama's documentation says Vulkan needs extra capabilities (or root) to read the available VRAM, and upstream issue 15321 reports that `setcap cap_perfmon+ep` can break GPU discovery. Apply them only if you switch to the Vulkan backend:

```sh
sudo cp systemd/ollama-setcap.hook /etc/pacman.d/hooks/
sudo setcap cap_perfmon+ep /usr/bin/ollama
getcap /usr/bin/ollama        # cap_perfmon=ep; re-check after each ollama package upgrade
```

Do not use the upstream `install.sh`: it installs under `/usr/local` or `/usr` without checking for a packaged install, deletes `$OLLAMA_INSTALL_DIR/lib/ollama`, and creates its own user and unit.

Confirm the GPU is actually in use, startup detection is not proof, so load
a model and check the layer count:

```sh
journalctl -u ollama | grep 'inference compute'   # expect library=ROCm compute=gfx1030
ollama run qwen:latest hi --verbose               # then: ollama ps -> should show 100% GPU
```

## Switching backend

```sh
sudo ollama-backend vulkan
sudo ollama-backend rocm
```

**ROCm is the one currently live**, not because it was preferred going in  - 
Vulkan was tried first and found to crash on large prompts. Full story,
with the exact journalctl evidence, in
[`claude-code-bench/ollama-claude-setup.md`](claude-code-bench/ollama-claude-setup.md).

`HSA_OVERRIDE_GFX_VERSION=10.3.0` (this card's gfx1031 reporting as its
supported sibling gfx1030) is what `backend.conf` sets for ROCm. It is a
fallback, not a requirement on this packaging: Arch's `ollama-rocm` bundles
ROCm 7.2 libraries with kernels for gfx1030 and gfx1031, and the harness
journal shows a native `compute=gfx1031` run at 32.85 tok/s against 32.79
spoofed (Ollama 0.34.3, 2026-09-23). gfx1031 is not on AMD's or Ollama's
supported list, so keep the override as a fallback and retest native
discovery on the current version. <!-- UNVERIFIED: native gfx1031 on Ollama 0.40.11 and kernel 7.3 -->

## Server config: what `claude-code.conf` deliberately does NOT set

`OLLAMA_CONTEXT_LENGTH` is absent on purpose. This server is shared with
Continue.dev, setting a global context length would force a fixed KV cache
size onto every model on the server, Continue's requests included. Context
belongs per-model, in a Modelfile's `PARAMETER num_ctx`, not here. (An
earlier, unrelated session had set this globally by mistake; removed.)

## Caveats

- **`cap_perfmon` matters only for the Vulkan backend.** If you applied it, the
  pacman hook re-applies it on upgrade; verify with `getcap /usr/bin/ollama`
  after any `ollama`/`ollama-vulkan`/`ollama-rocm` update (expect
  `cap_perfmon=ep`). On the ROCm backend leave it unset.
- **ROCm regression risk on upgrade.** `HSA_OVERRIDE_GFX_VERSION` on an
  unsupported gfx target is exactly the kind of thing a ROCm point release
  can break. Re-run the crash test in `claude-code-bench/` after any ROCm
  package update before trusting it again.
- **Continue.dev eviction.** `OLLAMA_MAX_LOADED_MODELS=1` means a Continue.dev
  request and a `ccl`/`cclf` session will evict each other's loaded model.
  Not resolved, see `claude-code-bench/ollama-claude-setup.md` §3.
