---
title: "04 AI/ML and LLM Stack"
part: "01"
chapter: "04"
topic: ai-llm-stack
versions: [ollama, rocm, torch, triton-rocm, pytorch-rocm-index, llama-cpp, pgvector, python]
last_verified: 2026-10-29
status: current
sources:
  - https://docs.ollama.com/gpu
  - https://pytorch.org/get-started/locally/
  - https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
  - https://docs.openwebui.com/
---

# 04 AI/ML and LLM Stack

## Purpose

Local inference and the Python ML libraries on the RX 6700 XT (12 GiB VRAM, gfx1031). The binding constraint for model choice is **VRAM**, not system RAM.

## Prerequisites

- [Chapter 02](02-amd-gpu-rocm.md): drivers, ROCm <!-- v:rocm -->7.2.4<!-- /v -->, and the gfx1031 notes.
- [Chapter 03](03-python-uv.md): uv and a project.

## 4.1 PyTorch with ROCm

Match the wheel index to the ROCm train: <!-- v:pytorch-rocm-index -->7.2<!-- /v --> goes with Arch's ROCm 7.2.4 (the `rocm6.4` index is frozen and resolves torch 2.9.1). The index tops out at torch <!-- v:torch -->2.14.1<!-- /v -->. `pytorch-triton-rocm` is the old Triton package name and no longer resolves; torch needs `triton-rocm` (<!-- v:triton-rocm -->3.8.0<!-- /v -->) as a **direct** dependency with its own source entry, because uv applies `[tool.uv.sources]` to direct dependencies only.

`pyproject.toml`:

```toml
[project]
name = "my-ai-project"
version = "0.1.0"
requires-python = ">=3.12,<3.15"
dependencies = ["torch", "torchvision", "triton-rocm; sys_platform == 'linux'"]

[tool.uv]
environments = ["sys_platform == 'linux' and platform_machine == 'x86_64'"]

[tool.uv.sources]
torch = [{ index = "pytorch-rocm" }]
torchvision = [{ index = "pytorch-rocm" }]
triton-rocm = [{ index = "pytorch-rocm" }]

[[tool.uv.index]]
name = "pytorch-rocm"
url = "https://download.pytorch.org/whl/rocm7.2"
explicit = true
```

```bash
uv lock       # torch 2.14.1+rocm7.2, torchvision 0.29.1+rocm7.2, triton-rocm 3.8.0
uv sync
```

Label: the lock step is `verified-in-cloud` (resolution only, with uv 0.11.32 on 2026-10-28; no wheel was installed and there is no GPU in the sandbox). The runtime check is `machine-only`:

```bash
HSA_OVERRIDE_GFX_VERSION=10.3.0 uv run python -c "
import torch
print(torch.version.hip, torch.cuda.is_available())
p = torch.cuda.get_device_properties(0)
print(p.name, p.gcnArchName, round(p.total_memory / 1e9, 1), 'GB')
"
```

Expected: a HIP version string, `True`, the GPU name, and about 12.0 GB. `total_memory` is the correct attribute (`total_mem` raises `AttributeError`). The override is required for the pip wheels (chapter 02, section 2.3). Python 3.12 to 3.14 work; torch 2.15.0 exists on PyPI but not on the `rocm7.2` index.

## 4.2 TensorFlow with ROCm

Not supported on this GPU. AMD's TensorFlow support table for ROCm 10.1.0 lists TF 2.21 and 2.20 and no RDNA2 card; `tensorflow-rocm` on PyPI ended at 2.14.0.600 (2024); the `rocm/tensorflow:latest` tag is about five months old and current images are ROCm-versioned (for example `rocm10.1-ubuntu24.04-py3.12-tf2.22`). Practical behavior on gfx1031 is untested. <!-- UNVERIFIED: TensorFlow on gfx1031 --> Use PyTorch, or JAX/ONNX Runtime if you need another framework. A container, if you try anyway:

```bash
docker run -it --network=host --device=/dev/kfd --device=/dev/dri \
  --ipc=host --shm-size 16G --group-add video \
  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
  rocm/tensorflow:rocm7.14.1-ubuntu24.04-py3.12-tf2.21
```

## 4.3 Ollama: local LLM inference

Ollama <!-- v:ollama -->0.40.11<!-- /v --> (Arch and CachyOS; upstream is at <!-- v:ollama:upstream -->0.40.13<!-- /v -->). The packages are `ollama` (CPU), `ollama-rocm` and `ollama-vulkan`; the full benchmarked setup is in [`05-ai/ollama/README.md`](../../../05-ai/ollama/README.md).

```bash
sudo pacman -S --needed ollama ollama-rocm
sudo install -Dm644 05-ai/ollama/systemd/backend-rocm.conf \
  /etc/systemd/system/ollama.service.d/backend.conf
sudo install -Dm644 05-ai/ollama/systemd/claude-code.conf \
  /etc/systemd/system/ollama.service.d/claude-code.conf
sudo install -Dm755 05-ai/ollama/bin/ollama-backend /usr/local/sbin/ollama-backend
sudo systemctl daemon-reload
sudo systemctl enable --now ollama.service
```

The ROCm backend is the one live on the primary host. Install `ollama-vulkan` only if you plan to use the Vulkan backend, and then also apply the `cap_perfmon` step from the Ollama README: Ollama's docs say Vulkan needs extra capabilities to read VRAM data, while the ROCm backend does not, and upstream issue 15321 reports that `setcap cap_perfmon+ep` can break GPU discovery. Do not run `setcap` or install the pacman hook on a ROCm-only setup.

Vulkan is enabled by default when its backend is installed (`OLLAMA_VULKAN=0` turns it off). Pull a small model first and confirm GPU residency before pulling large ones:

```bash
ollama pull qwen3:4b
ollama run qwen3:4b hi
ollama ps                          # PROCESSOR column: 100% GPU
```

Model fit on 12 GiB of VRAM (library sizes of 2026-10-28; sizes change when a tag is re-pushed, so check `ollama show`):

| Model | Size | Fit on 12 GiB |
|---|---|---|
| `llama3.1:8b` | 4.9 GB | fits |
| `qwen3:8b` | 5.2 GB | fits |
| `gemma4:12b` | 7.7 to 8.0 GB | fits: 8.38 GB VRAM at 65536 context with q8_0 KV cache, 100 percent GPU (measured on Ollama 0.34.3) |
| `gpt-oss:20b` | 14 GB | does not fit: 29 percent CPU / 71 percent GPU (measured) |
| `qwen3-coder:30b` | 19 GB | does not fit; partial offload, not measured |
| `codellama:13b` | 7.4 GB | fits, but it is a 16K-context model last updated long ago |
| `nomic-embed-text` | 274 MB | embeddings for RAG |

A 7B to 13B model at Q4 fits entirely in VRAM; the 32 GiB of system RAM only matters for partial offload. For coding agents set the context to 64000 or more per model with `PARAMETER num_ctx` in a Modelfile (the repo deliberately sets no global `OLLAMA_CONTEXT_LENGTH`). Default context is 4k below 24 GiB of VRAM.

Claude Code can talk to Ollama through its Anthropic-compatible `/v1/messages` endpoint: `ollama launch claude --model <model>`, or `ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL=http://localhost:11434 claude --model <model>`. Tool use, streaming and thinking work; prompt caching, `tool_choice` and token counting do not. See `05-ai/ollama/claude-code-bench/` for the measured setup. Label for all of 4.3: `machine-only`.

## 4.4 Open WebUI

Bind to loopback and set a secret key. Docker route:

```bash
docker run -d -p 127.0.0.1:3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  -e WEBUI_SECRET_KEY="$(openssl rand -hex 32)" \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

Without Docker: `uvx --python 3.12 open-webui@latest serve` (the PyPI package requires Python 3.11 or 3.12). Image tags: `:main`, `:slim`, `:cuda`, `:ollama`, `:vX.Y.Z`; there is no ROCm tag, so GPU work stays in Ollama. Reaching an Ollama that listens on 127.0.0.1 from a rootless Docker container through `host.docker.internal` is not verified. <!-- UNVERIFIED --> Open `http://localhost:3000` and create the admin account on first visit. Label: `machine-only`.

## 4.5 llama.cpp with ROCm/HIP or Vulkan

Arch `extra` (and CachyOS) package llama.cpp: `llama-cpp` 0.6.0 with the backend packages `ggml-hip` and `ggml-vulkan`. Use the package first; build from source only for features newer than the package (upstream is at release build b11969).

```bash
sudo pacman -S --needed llama-cpp ggml-hip     # or ggml-vulkan
llama-cli -m model.gguf -ngl 99 -p "Hello"
```

Whether Arch's `ggml-hip` is built for gfx1031 is not established. <!-- UNVERIFIED --> Source build for HIP (current flags: `GPU_TARGETS`, not `AMDGPU_TARGETS`; ROCm 6.1 or newer; `-DLLAMA_CURL` no longer exists):

```bash
git clone https://github.com/ggml-org/llama.cpp.git && cd llama.cpp
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build -DGGML_HIP=ON -DGPU_TARGETS=gfx1031 -DCMAKE_BUILD_TYPE=Release \
  && cmake --build build --config Release -j"$(nproc)"
./build/bin/llama-server -m model.gguf -ngl 99 --host 127.0.0.1 --port 8080
```

`rocminfo | grep gfx` prints `gfx1030` when the override is exported, so read your real architecture with the variable unset. A Vulkan build is `cmake -B build -DGGML_VULKAN=1` and needs the Vulkan headers and loader, `glslc` and `spirv-headers`. Bind the server to loopback unless you mean to expose it. Label: `machine-only`.

## 4.6 vLLM

Not supported on this GPU. vLLM's ROCm builds list RX 7900 (gfx1100/1101) and RX 9000 cards; gfx1031 is not listed. The documented routes are the `vllm/vllm-openai-rocm` image (the `rocm/vllm` images are deprecated) and `uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/` (ROCm wheels are Python 3.12 only and can silently fall back to the CUDA wheel on any other version). Use Ollama or llama.cpp locally and keep vLLM for a server GPU. <!-- UNVERIFIED: runtime on gfx1031 --> Label: `unverified`.

## 4.7 LangChain and LlamaIndex

LangChain is on 1.x (langchain 1.4, langgraph 1.2, `langchain-ollama` 1.1). Legacy chains, retrievers and indexing moved to `langchain-classic`; `create_react_agent` is now `langchain.agents.create_agent`. LlamaIndex package names are unchanged (`llama-index-<type>-<provider>`).

```bash
uv add langchain langchain-core langgraph langchain-ollama langchain-chroma
uv add langchain-openai langchain-huggingface      # only if you use those providers
uv add llama-index llama-index-llms-ollama llama-index-embeddings-huggingface llama-index-vector-stores-chroma
```

Add `langchain-community` only for integrations that have no dedicated package, and `langchain-classic` only for old code. Label: `unverified` for the exact set (versions resolved on 2026-10-28; the sandbox did not install them).

## 4.8 Hugging Face ecosystem

transformers is on v5. The CLI is `hf` (`huggingface-cli` was removed in huggingface_hub 1.0): `hf auth login`, `hf download`, `hf upload`, `hf cache ls`.

```bash
uv add transformers datasets accelerate tokenizers sentence-transformers huggingface-hub
uv tool install hf        # PyPI package `hf` 2.3.0 is the extracted CLI; or: curl -LsSf https://hf.co/cli/install.sh | bash
```

`SentenceTransformer("all-MiniLM-L6-v2")` runs on the GPU only if the torch in the environment is the ROCm build, so configure the ROCm index (4.1) **before** adding `sentence-transformers`; otherwise PyPI's default torch may be pulled. Which default PyPI resolves to on Linux was not checked. <!-- UNVERIFIED -->

## 4.9 Vector databases

pgvector is the default (it lives in the PostgreSQL you already run; see [chapter 06](06-databases.md)). Alternatives for specific needs:

| Store | Use | Notes |
|---|---|---|
| pgvector <!-- v:pgvector -->0.8.7<!-- /v --> | default, one datastore | `sudo pacman -S pgvector`, then `CREATE EXTENSION vector;`; HNSW and IVFFlat, halfvec, sparsevec |
| Qdrant | dedicated server, scale | `docker run -p 127.0.0.1:6333:6333 -p 127.0.0.1:6334:6334 qdrant/qdrant`; `uv add qdrant-client` |
| ChromaDB 1.5 | prototyping | `uv add chromadb`; production docs lean on Chroma Cloud |
| Weaviate | production-grade local | pin the tag (docs use `cr.weaviate.io/semitechnologies/weaviate:1.40.2`), publish to `127.0.0.1` only; `uv add weaviate-client` |
| Milvus Lite | embedded | `uv add "pymilvus[milvus-lite]"`; FLAT index only; Ubuntu and macOS are the listed platforms |
| FAISS | in-process library | `uv add faiss-cpu` |
| Pinecone | managed cloud | `uv add pinecone` |

Publishing a container port as `-p 8080:8080` binds every interface; prefix `127.0.0.1:` to match the loopback policy of this machine.

## Verify

```bash
ollama --version
uv lock --check
```

Expected: `ollama version is` <!-- v:ollama -->0.40.11<!-- /v -->; the lock check passes in a project using the 4.1 recipe.

## Sources

- [Ollama GPU support](https://docs.ollama.com/gpu), [context length](https://docs.ollama.com/context-length), [Claude Code integration](https://docs.ollama.com/integrations/claude-code)
- [PyTorch install selector](https://pytorch.org/get-started/locally/)
- [llama.cpp build docs](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)
- Ledger: cluster C3 in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
