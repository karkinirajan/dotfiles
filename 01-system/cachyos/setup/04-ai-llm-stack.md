---
title: "04 AI/ML and LLM Stack"
part: "01"
chapter: "04"
topic: ai-llm-stack
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 04 AI/ML and LLM Stack


## 4.1 PyTorch with ROCm ⭐

Add to `pyproject.toml` before installing:

```toml
[tool.uv.sources]
torch = [{ index = "pytorch-rocm", marker = "sys_platform == 'linux'" }]
torchvision = [{ index = "pytorch-rocm", marker = "sys_platform == 'linux'" }]
pytorch-triton-rocm = [{ index = "pytorch-rocm", marker = "sys_platform == 'linux'" }]

[[tool.uv.index]]
name = "pytorch-rocm"
url = "https://download.pytorch.org/whl/rocm6.4"
explicit = true
```

```bash
uv add torch torchvision "pytorch-triton-rocm>=3.5.1"
```

**Verify:**

```python
import torch
print(torch.cuda.is_available())        # True (ROCm uses CUDA API via HIP)
print(torch.cuda.get_device_name(0))    # AMD Radeon RX 6700 XT
print(torch.cuda.get_device_properties(0).total_mem / 1e9, "GB")
```

## 4.2 TensorFlow with ROCm

Docker is the most reliable method on Arch:

```bash
docker run -it --network=host --device=/dev/kfd --device=/dev/dri \
  --ipc=host --shm-size 16G --group-add video \
  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
  rocm/tensorflow:latest
```

## 4.3 Ollama — Local LLM Inference ⭐

CachyOS ships `ollama`, `ollama-rocm`, and `ollama-vulkan`. See [`../../05-ai/ollama/README.md`](../../../05-ai/ollama/README.md) for the complete benchmarked setup.

```bash
sudo pacman -S --needed ollama ollama-rocm ollama-vulkan
sudo install -Dm644 05-ai/ollama/systemd/backend-rocm.conf \
  /etc/systemd/system/ollama.service.d/backend.conf
sudo install -Dm644 05-ai/ollama/systemd/claude-code.conf \
  /etc/systemd/system/ollama.service.d/claude-code.conf
sudo install -Dm755 05-ai/ollama/bin/ollama-backend \
  /usr/local/sbin/ollama-backend
sudo install -Dm644 05-ai/ollama/systemd/ollama-setcap.hook \
  /etc/pacman.d/hooks/ollama-setcap.hook
sudo setcap cap_perfmon+ep /usr/bin/ollama
sudo systemctl daemon-reload
sudo systemctl enable --now ollama.service
```

```bash
ollama pull llama3.1:8b          # Download 8B model (~4.7GB)
ollama pull qwen3:8b             # Qwen 3 8B
ollama pull codellama:13b        # Code-focused 13B
ollama pull nomic-embed-text     # Embedding model for RAG
ollama run llama3.1:8b           # Interactive chat
ollama list                      # Show downloaded models
```

**With 32GB RAM, you can run:** 7B–13B parameter models (Q4_K_M quantization) fully on GPU.

## 4.4 Open WebUI — Local Chat Interface

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

Access: http://localhost:3000 — create admin account on first visit.

## 4.5 llama.cpp with ROCm/HIP ⭐

High-performance C++ inference for GGUF quantized models with AMD GPU via HIP.

```bash
git clone https://github.com/ggml-org/llama.cpp.git && cd llama.cpp

# Find your GPU arch:
rocminfo | grep gfx | head -1 | awk '{print $2}'   # e.g., gfx1030

# Build with HIP:
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build -DGGML_HIP=ON \
  -DAMDGPU_TARGETS=gfx1030 \
  -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=ON \
  && cmake --build build --config Release -j$(nproc)

./build/bin/llama-cli -m model.gguf -ngl 99 -p "Hello"
./build/bin/llama-server -m model.gguf -ngl 99 --host 0.0.0.0 --port 8080
```

## 4.6 vLLM — Production LLM Serving

```bash
# Docker (recommended for production):
docker run --rm --device /dev/kfd --device /dev/dri \
  --group-add=video --ipc=host --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 vllm/vllm-openai-rocm:latest \
  --model Qwen/Qwen3-0.6B

# pip:
uv add vllm --extra-index-url https://wheels.vllm.ai/rocm/
```

## 4.7 LangChain & LlamaIndex

```bash
# LangChain — LLM application framework:
uv add langchain langchain-core langchain-community langgraph \
       langchain-openai langchain-ollama langchain-huggingface langchain-chroma

# LlamaIndex — RAG data framework:
uv add llama-index \
       llama-index-llms-ollama llama-index-embeddings-huggingface \
       llama-index-vector-stores-chroma
```

## 4.8 Hugging Face Ecosystem

```bash
uv add transformers datasets accelerate tokenizers sentence-transformers huggingface-hub
```

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")   # Auto-uses ROCm GPU
embeddings = model.encode(["Hello world", "AI on Arch Linux"])
```

## 4.9 Vector Databases

**ChromaDB** (local, lightweight — best for prototyping):

```bash
uv add chromadb
```

**Weaviate** (local Docker, production-grade):

```bash
docker run -d -p 8080:8080 -p 50051:50051 \
  -v weaviate_data:/var/lib/weaviate \
  --name weaviate cr.weaviate.io/semitechnologies/weaviate:latest
uv add weaviate-client
```

**pgvector** (PostgreSQL extension — vector search in your existing Postgres):

```bash
sudo pacman -S pgvector
# In psql: CREATE EXTENSION vector;
uv add pgvector psycopg2-binary
```

**FAISS** (Facebook AI Similarity Search):

```bash
uv add faiss-cpu
```

**Pinecone** (cloud managed):

```bash
uv add pinecone
```
