# The Ultimate CachyOS Developer Workstation: Complete Setup Guide

**Hardware:** 32GB RAM · AMD GPU (ROCm) · KDE Plasma · CachyOS (Arch Linux)
**Profile:** Senior Python Backend & AI Engineer · Freelancer · Full-Stack when needed
**Updated:** February 2026

> This guide covers EVERY tool you need — from kernel optimization and GPU drivers to local LLM inference, backend frameworks, DevOps pipelines, browsers, note-taking, project management, and daily productivity. Each item includes: what it is, install command, quick config, and official link. Nothing is skipped.

---

## Table of Contents

1. [System Foundation & AMD GPU](#1-system-foundation--amd-gpu)
2. [Python Environment with uv](#2-python-environment-with-uv)
3. [AI/ML & LLM Stack](#3-aiml--llm-stack)
4. [Backend Frameworks & Tools](#4-backend-frameworks--tools)
5. [Databases](#5-databases)
6. [DevOps & Cloud Tools](#6-devops--cloud-tools)
7. [Docker & Kubernetes](#7-docker--kubernetes)
8. [Infrastructure as Code](#8-infrastructure-as-code)
9. [CI/CD Pipelines](#9-cicd-pipelines)
10. [Data Engineering & Science](#10-data-engineering--science)
11. [Frontend Development](#11-frontend-development)
12. [Code Editors & IDEs](#12-code-editors--ides)
13. [Terminal, Shell & CLI Tools](#13-terminal-shell--cli-tools)
14. [Git & Version Control](#14-git--version-control)
15. [Browsers](#15-browsers)
16. [Note-Taking & Knowledge Management](#16-note-taking--knowledge-management)
17. [Project Management & Freelance Tools](#17-project-management--freelance-tools)
18. [Communication & Collaboration](#18-communication--collaboration)
19. [Security & Privacy](#19-security--privacy)
20. [System Maintenance & Monitoring](#20-system-maintenance--monitoring)
21. [Media, Office & Personal](#21-media-office--personal)
22. [Bulk Install Commands](#22-bulk-install-commands)
23. [Complete ~/.zshrc Configuration](#23-complete-zshrc-configuration)
24. [AI/ML Project Quickstart Template](#24-aiml-project-quickstart-template)

---

## 1. System Foundation & AMD GPU

### 1.1 CachyOS Post-Install Optimization

CachyOS ships `cachyos-settings` with sysctl tweaks, I/O scheduler rules, ZRAM config, and audio power management. `ananicy-cpp` auto-adjusts process priorities for desktop responsiveness.

```bash
sudo pacman -S cachyos-settings ananicy-cpp cachyos-ananicy-rules
sudo systemctl enable --now ananicy-cpp.service
```

**Custom sysctl tweaks** (create `/etc/sysctl.d/99-developer.conf`):
```ini
# Network performance for API development
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_fastopen = 3

# File watchers for VS Code, webpack, etc.
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 512
```
```bash
sudo sysctl --system  # Apply without reboot
```

- 📎 https://wiki.cachyos.org/features/cachyos_settings/
- 📎 https://github.com/CachyOS/CachyOS-Settings

### 1.2 AMD GPU Drivers (AMDGPU + Mesa + Vulkan)

Open-source AMD GPU stack — kernel driver, Mesa OpenGL/Vulkan, and RADV Vulkan driver.

```bash
sudo pacman -S mesa lib32-mesa vulkan-radeon lib32-vulkan-radeon \
  vulkan-icd-loader lib32-vulkan-icd-loader \
  libva-mesa-driver lib32-libva-mesa-driver mesa-vdpau lib32-mesa-vdpau
```

**Verify:**
```bash
lspci -k | grep -A3 VGA          # Should show "Kernel driver in use: amdgpu"
vulkaninfo --summary              # Should list your AMD GPU
vainfo                            # Hardware video decode info
```

- 📎 https://wiki.archlinux.org/title/AMDGPU

### 1.3 ROCm Installation for AI/ML

AMD's open-source GPU compute platform. The `rocm-hip-sdk` meta-package pulls in HIP runtime, rocBLAS, MIOpen, and all core ROCm libraries needed for PyTorch, TensorFlow, and llama.cpp.

```bash
sudo pacman -S rocm-hip-sdk rocm-opencl-sdk
sudo usermod -aG render,video $USER
```

**Log out and back in**, then verify:
```bash
rocminfo                   # Should list your GPU agent
hipcc --version            # HIP compiler
rocm-smi                   # GPU stats, temperature, power
```

**For consumer GPUs (RX 7000/6000 series)** — if `rocminfo` doesn't list your GPU, set the override. Add to `~/.zshrc`:
```bash
# RDNA3 (RX 7900 XTX/XT/GRE, RX 7800 XT, RX 7700 XT)
export HSA_OVERRIDE_GFX_VERSION=11.0.0

# RDNA2 (RX 6900/6800/6700/6600 series)
# export HSA_OVERRIDE_GFX_VERSION=10.3.0
```

- 📎 https://rocm.docs.amd.com/projects/install-on-linux/en/latest/
- 📎 https://linux-packages.com/arch-linux/package/rocm-hip-sdk

### 1.4 ROCm Components — HIP, rocBLAS, MIOpen

- **HIP:** AMD's CUDA-compatible programming interface. Programs compile with `hipcc`.
- **rocBLAS:** GPU-accelerated BLAS (Basic Linear Algebra Subprograms).
- **MIOpen:** AMD's deep learning primitives library (convolutions, pooling, batch norm, etc.).

```bash
# Already installed via rocm-hip-sdk. Individual packages if needed:
sudo pacman -S hip-runtime-amd hipblas rocblas miopen-hip rocm-cmake
```

- 📎 https://rocm.docs.amd.com/projects/HIP/en/latest/

### 1.5 GPU Monitoring Tools

```bash
sudo pacman -S radeontop rocm-smi-lib
yay -S amdgpu_top-bin   # Modern TUI GPU monitor
```

| Tool | Purpose | Command |
|---|---|---|
| `radeontop` | Real-time GPU utilization bars | `radeontop` |
| `rocm-smi` | Detailed ROCm stats, temp, power, VRAM | `rocm-smi` |
| `amdgpu_top` | Modern TUI with per-process GPU usage | `amdgpu_top` |

- 📎 https://github.com/clbr/radeontop
- 📎 https://github.com/Umio-Yasuno/amdgpu_top

### 1.6 32GB RAM Optimization — ZRAM and Swappiness

CachyOS enables ZRAM by default. For 32GB RAM, configure `/etc/systemd/zram-generator.conf`:

```ini
[zram0]
zram-size = min(ram, 8192)
compression-algorithm = zstd
```

**What this does:** Creates an 8GB compressed swap device in RAM using zstd compression (2:1 to 3:1 ratio). When RAM fills during heavy AI workloads (Ollama + Docker + VS Code + browser), cold pages compress in RAM (~37ns) instead of hitting SSD (~100μs). Effectively gives you 36-40GB usable memory.

**Optional SSD swap fallback** for extremely heavy workloads:
```bash
# Btrfs:
sudo btrfs filesystem mkswapfile --size 8G /swap/swapfile
sudo swapon /swap/swapfile
echo '/swap/swapfile none swap defaults 0 0' | sudo tee -a /etc/fstab
```

- 📎 https://wiki.archlinux.org/title/Zram

---

## 2. Python Environment with uv

### 2.1 Why uv, Not pip

On Arch/CachyOS, running `pip install` globally throws `error: externally-managed-environment` (PEP 668). Arch's system Python is managed by pacman — pip can break it.

**`uv` by Astral solves this permanently:**
- `uv add` and `uv run` always operate inside virtual environments
- `uv pip install` refuses to touch system Python unless you explicitly pass `--system`
- `uv tool install` creates isolated per-tool envs (replaces pipx)
- `uv python install` manages Python versions (replaces pyenv)
- 10-100× faster than pip thanks to Rust implementation and global cache
- Generates `uv.lock` for reproducible builds

**You never need `--break-system-packages`.** PEP 668 becomes irrelevant.

### 2.2 Installing uv

**Option A — Standalone installer (recommended, enables self-update):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Option B — From pacman:**
```bash
sudo pacman -S uv
# Note: pacman version disables `uv self update` — upgrade via pacman -Syu
```

- 📎 https://docs.astral.sh/uv/getting-started/installation/

### 2.3 uv Shell Configuration

Add to `~/.zshrc`:
```bash
# uv — Python package manager
export PATH="$HOME/.local/bin:$PATH"
eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"
```

### 2.4 Managing Python Versions (Replaces pyenv)

```bash
uv python install 3.12 3.13        # Install versions
uv python list                      # List all available/installed
uv python pin 3.12                  # Pin project to 3.12 (creates .python-version)
uv python find                      # Show active Python path
uv python uninstall 3.13            # Remove a version
```

### 2.5 Project Workflow (Replaces pip + venv + pip-tools)

```bash
# Create a new project
uv init my-project --python 3.12
cd my-project

# Add dependencies (auto-updates pyproject.toml + uv.lock + .venv)
uv add django djangorestframework
uv add fastapi uvicorn[standard]
uv add --dev pytest ruff ipykernel

# Run commands in the project's venv
uv run python manage.py runserver
uv run pytest
uv run ruff check .

# Sync environment from lockfile (for CI/teammates)
uv sync

# Export for Docker/legacy systems
uv export --format requirements-txt > requirements.txt

# Lock without installing
uv lock
uv lock --locked  # Verify lockfile is current

# Dependency tree
uv tree
```

### 2.6 Installing CLI Tools (Replaces pipx)

Each tool gets an isolated virtual environment. Only executables go in `~/.local/bin/`:

```bash
uv tool install ruff              # Linter + formatter (replaces black, flake8, isort)
uv tool install jupyterlab        # Jupyter notebook server
uv tool install httpie             # Modern HTTP client
uv tool install pre-commit         # Git hook manager
uv tool install mypy               # Static type checker
uv tool install ipython            # Enhanced Python REPL

uv tool list                       # Show installed tools
uv tool upgrade ruff               # Upgrade a tool
uv tool upgrade --all              # Upgrade everything
```

**`uvx` runs tools ephemerally** (no permanent install):
```bash
uvx ruff check .                   # Run ruff without installing
uvx black --check .                # Run black once
uvx cowsay 'hello from arch'       # Just for fun
```

### 2.7 The pip-Compatible Interface (Fallback)

When you need classic pip behavior inside a venv:

```bash
uv venv                            # Create standalone .venv
source .venv/bin/activate           # Activate it
uv pip install requests flask       # Install (into venv only)
uv pip install -r requirements.txt  # From requirements file
uv pip freeze                       # Freeze
uv pip list                         # List packages
uv pip compile requirements.in -o requirements.txt  # Compile (like pip-tools)
```

- 📎 https://docs.astral.sh/uv/
- 📎 https://docs.astral.sh/uv/guides/projects/
- 📎 https://docs.astral.sh/uv/concepts/tools/

### 2.8 Linting & Formatting — ruff (All-in-One)

Ruff replaces black, flake8, isort, pyflakes, pycodestyle, and dozens more — in one tool, 30-100× faster.

```bash
uv tool install ruff
```

Add to `pyproject.toml`:
```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "W"]

[tool.ruff.format]
quote-style = "double"
```

```bash
ruff check .          # Lint
ruff check . --fix    # Auto-fix
ruff format .         # Format (Black-compatible)
```

- 📎 https://docs.astral.sh/ruff/

### 2.9 Pre-commit Hooks

```bash
uv tool install pre-commit
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

```bash
pre-commit install              # Set up hooks
pre-commit run --all-files      # Run on all files now
```

- 📎 https://pre-commit.com/

### 2.10 Python Debugging — ipdb, pudb

```bash
# Inside a project:
uv add --dev ipdb pudb
```

| Debugger | Style | Usage |
|---|---|---|
| `pdb` | Built-in CLI | `import pdb; pdb.set_trace()` |
| `ipdb` | IPython-enhanced | `import ipdb; ipdb.set_trace()` |
| `pudb` | Full-screen TUI | `PYTHONBREAKPOINT=pudb.set_trace python script.py` |

- 📎 https://github.com/gotcha/ipdb
- 📎 https://github.com/inducer/pudb

### 2.11 Jupyter Notebook/Lab

**Option A — Run within project (recommended):**
```bash
uv add --dev ipykernel
uv run --with jupyter jupyter lab
```

**Option B — Global tool:**
```bash
uv tool install jupyterlab
# Register project kernel:
uv run ipython kernel install --user --name=my-project
jupyter lab  # Select kernel from dropdown
```

- 📎 https://jupyterlab.readthedocs.io/

---

## 3. AI/ML & LLM Stack

### 3.1 PyTorch with ROCm Support ⭐

```bash
# In your project, configure pyproject.toml first:
```

Add to `pyproject.toml`:
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

Then install:
```bash
uv add torch torchvision "pytorch-triton-rocm>=3.5.1"
```

**Verify:**
```bash
uv run python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'ROCm available: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
print(f'VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB')
"
```

- 📎 https://pytorch.org/get-started/locally/
- 📎 https://rocm.docs.amd.com/projects/install-on-linux/en/docs-6.4.3/install/3rd-party/pytorch-install.html

### 3.2 TensorFlow with ROCm

Docker is the most reliable method on Arch:

```bash
docker run -it --network=host --device=/dev/kfd --device=/dev/dri \
  --ipc=host --shm-size 16G --group-add video \
  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
  rocm/tensorflow:latest
```

**pip alternative** (may work depending on glibc version):
```bash
uv add tensorflow-rocm --extra-index-url https://repo.radeon.com/rocm/manylinux/rocm-rel-7.2/
```

- 📎 https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/3rd-party/tensorflow-install.html

### 3.3 Ollama — Local LLM Inference with AMD GPU ⭐

The easiest way to run LLMs locally. CachyOS provides a ROCm-accelerated package.

```bash
sudo pacman -S ollama-rocm
sudo usermod -aG render,video $USER
sudo systemctl enable --now ollama.service
```

**For unsupported GPUs**, create an override:
```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="HSA_OVERRIDE_GFX_VERSION=11.0.0"
EOF
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

**Usage:**
```bash
ollama pull llama3.1:8b         # Download 8B model (~4.7GB)
ollama pull qwen3:8b            # Qwen 3 8B
ollama pull codellama:13b       # Code-focused 13B
ollama pull nomic-embed-text    # Embedding model for RAG
ollama run llama3.1:8b          # Interactive chat
ollama list                     # Show downloaded models
ollama ps                       # Show running models
```

**With 32GB RAM, you can comfortably run:** 7B-13B parameter models (Q4_K_M quantization). 30B+ models require offloading to CPU.

- 📎 https://ollama.com/
- 📎 https://wiki.archlinux.org/title/Ollama

### 3.4 Open WebUI — Local Chat Interface

Self-hosted web UI for Ollama and OpenAI-compatible APIs.

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

Access: http://localhost:3000 — create admin account on first visit.

- 📎 https://docs.openwebui.com/

### 3.5 llama.cpp with ROCm/HIP (GGUF Models) ⭐

High-performance C++ inference for quantized GGUF models with AMD GPU acceleration.

```bash
git clone https://github.com/ggml-org/llama.cpp.git && cd llama.cpp

# Find your GPU architecture:
rocminfo | grep gfx | head -1 | awk '{print $2}'

# Build with HIP:
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build -DGGML_HIP=ON \
  -DAMDGPU_TARGETS=gfx1100 \
  -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=ON \
  && cmake --build build --config Release -j$(nproc)

# Run:
./build/bin/llama-cli -m model.gguf -ngl 99 -p "Hello"

# Server (OpenAI-compatible API):
./build/bin/llama-server -m model.gguf -ngl 99 --host 0.0.0.0 --port 8080
```

- 📎 https://github.com/ggml-org/llama.cpp
- 📎 https://rocm.blogs.amd.com/ecosystems-and-partners/llama-cpp/README.html

### 3.6 vLLM — Production LLM Serving

High-throughput LLM serving engine with PagedAttention. ROCm is first-class.

```bash
# Docker (recommended):
docker run --rm --device /dev/kfd --device /dev/dri \
  --group-add=video --ipc=host --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 vllm/vllm-openai-rocm:latest \
  --model Qwen/Qwen3-0.6B

# pip (in a project):
uv add vllm --extra-index-url https://wheels.vllm.ai/rocm/
```

- 📎 https://docs.vllm.ai/en/latest/getting_started/installation/gpu/

### 3.7 LangChain

Framework for building LLM applications — chains, agents, RAG pipelines.

```bash
uv add langchain langchain-core langchain-community langgraph
uv add langchain-openai langchain-ollama langchain-huggingface langchain-chroma
```

- 📎 https://python.langchain.com/docs/

### 3.8 LlamaIndex

Data framework for connecting LLMs to your own data via RAG.

```bash
uv add llama-index
uv add llama-index-llms-ollama llama-index-embeddings-huggingface llama-index-vector-stores-chroma
```

- 📎 https://docs.llamaindex.ai/

### 3.9 Hugging Face Ecosystem

```bash
uv add transformers datasets accelerate tokenizers sentence-transformers huggingface-hub
```

**Quick embedding example:**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")  # Auto-uses ROCm GPU
embeddings = model.encode(["Hello world", "AI development on Arch Linux"])
```

- 📎 https://huggingface.co/docs/transformers
- 📎 https://www.sbert.net/

### 3.10 Vector Databases

**ChromaDB (local, lightweight, great for prototyping):**
```bash
uv add chromadb
# import chromadb; client = chromadb.PersistentClient(path="./chroma_db")
```
📎 https://docs.trychroma.com/

**Weaviate (local Docker, production-grade):**
```bash
docker run -d -p 8080:8080 -p 50051:50051 \
  -v weaviate_data:/var/lib/weaviate \
  --name weaviate cr.weaviate.io/semitechnologies/weaviate:latest
uv add weaviate-client
```
📎 https://weaviate.io/developers/weaviate

**pgvector (PostgreSQL extension):**
```bash
yay -S pgvector
# In psql: CREATE EXTENSION vector;
uv add pgvector psycopg2-binary
```
📎 https://github.com/pgvector/pgvector

**Pinecone (cloud, managed):**
```bash
uv add pinecone
```
📎 https://docs.pinecone.io/

**FAISS (Facebook AI Similarity Search):**
```bash
uv add faiss-cpu   # or faiss-gpu for CUDA (ROCm support limited)
```
📎 https://github.com/facebookresearch/faiss

---

## 4. Backend Frameworks & Tools

### 4.1 Django + Django REST Framework

```bash
uv add django djangorestframework django-cors-headers django-filter
uv add django-celery-beat django-celery-results whitenoise
uv add --dev django-debug-toolbar factory-boy
```

```bash
uv run django-admin startproject myproject && cd myproject
uv run python manage.py startapp api
# Add 'rest_framework', 'corsheaders' to INSTALLED_APPS
```

- 📎 https://www.djangoproject.com/
- 📎 https://www.django-rest-framework.org/

### 4.2 FastAPI + Uvicorn + Gunicorn

```bash
uv add fastapi "uvicorn[standard]" gunicorn python-multipart
uv add --dev httpx  # For testing
```

```bash
# Dev: uv run uvicorn main:app --reload
# Prod: uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

- 📎 https://fastapi.tiangolo.com/
- 📎 https://www.uvicorn.org/

### 4.3 Flask

```bash
uv add flask flask-sqlalchemy flask-migrate flask-cors
```

- 📎 https://flask.palletsprojects.com/

### 4.4 Celery + Redis

```bash
uv add celery redis
```

```python
# celery_app.py
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def process_document(doc_id):
    # Heavy AI processing here
    pass

# Run: uv run celery -A celery_app worker --loglevel=info
# Beat: uv run celery -A celery_app beat -l info
```

- 📎 https://docs.celeryq.dev/

### 4.5 WebSockets

```bash
uv add channels channels-redis     # Django Channels
uv add websockets                   # Standalone / FastAPI built-in
```

- 📎 https://channels.readthedocs.io/

### 4.6 AsyncIO Essentials

```bash
uv add aiohttp httpx asyncpg aiofiles
```

| Library | Purpose |
|---|---|
| `httpx` | Modern async/sync HTTP client with HTTP/2 |
| `aiohttp` | Async HTTP client/server |
| `asyncpg` | Fast async PostgreSQL driver |
| `aiofiles` | Async file I/O |

- 📎 https://www.python-httpx.org/
- 📎 https://magicstack.github.io/asyncpg/

---

## 5. Databases

### 5.1 PostgreSQL ⭐

```bash
sudo pacman -S postgresql
sudo -iu postgres initdb --locale=C.UTF-8 -E UTF8 -D /var/lib/postgres/data --data-checksums
sudo systemctl enable --now postgresql

# Create dev user and database:
sudo -iu postgres psql -c "CREATE USER devuser WITH ENCRYPTED PASSWORD 'devpass' CREATEDB;"
sudo -iu postgres psql -c "CREATE DATABASE devdb OWNER devuser;"

# Enable pgvector:
yay -S pgvector
sudo -iu postgres psql devdb -c "CREATE EXTENSION vector;"
```

- 📎 https://www.postgresql.org/
- 📎 https://wiki.archlinux.org/title/PostgreSQL

### 5.2 MariaDB (MySQL-compatible)

```bash
sudo pacman -S mariadb
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo systemctl enable --now mariadb
sudo mariadb-secure-installation
```

- 📎 https://mariadb.org/

### 5.3 MongoDB

```bash
yay -S mongodb-bin   # Pre-built binary (building from source takes hours)
sudo systemctl enable --now mongodb
mongosh              # Verify
```

- 📎 https://www.mongodb.com/

### 5.4 Redis

```bash
sudo pacman -S redis
sudo systemctl enable --now redis
redis-cli ping   # → PONG
```

- 📎 https://redis.io/

### 5.5 Elasticsearch (Docker)

```bash
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.0
```

- 📎 https://www.elastic.co/elasticsearch

### 5.6 SQLite

Ships with Python. System CLI:
```bash
sudo pacman -S sqlite
```

- 📎 https://www.sqlite.org/

### 5.7 Database GUI Tools

**DBeaver ⭐ (universal — Postgres, MySQL, SQLite, MongoDB, 80+ databases):**
```bash
sudo pacman -S dbeaver
```
📎 https://dbeaver.io/

**pgAdmin 4 (PostgreSQL-specific, Docker):**
```bash
docker run -d --name pgadmin -p 5050:80 \
  -e "PGADMIN_DEFAULT_EMAIL=admin@local.dev" \
  -e "PGADMIN_DEFAULT_PASSWORD=admin" \
  dpage/pgadmin4
```
📎 https://www.pgadmin.org/

**Redis Insight (Redis GUI):**
```bash
docker run -d --name redis-insight -p 5540:5540 redis/redisinsight:latest
```
📎 https://redis.io/insight/

**MongoDB Compass:**
```bash
yay -S mongodb-compass
```
📎 https://www.mongodb.com/products/tools/compass

---

## 6. DevOps & Cloud Tools

### 6.1 AWS CLI v2

```bash
sudo pacman -S aws-cli-v2
aws configure
# Enter: Access Key, Secret Key, region (e.g., us-east-1), output format (json)
```

**Essential AWS tools:**
```bash
uv tool install aws-sam-cli        # Serverless Application Model
sudo pacman -S aws-vault           # Secure credential management (if available)
```

- 📎 https://docs.aws.amazon.com/cli/latest/userguide/

### 6.2 Azure CLI

```bash
sudo pacman -S azure-cli
az login   # Opens browser for auth
```

- 📎 https://learn.microsoft.com/en-us/cli/azure/

### 6.3 Google Cloud SDK

```bash
yay -S google-cloud-cli
gcloud init   # Authenticate, set project/region
```

- 📎 https://cloud.google.com/sdk/docs/

### 6.4 Nginx

```bash
sudo pacman -S nginx
sudo systemctl enable --now nginx
# Config: /etc/nginx/nginx.conf
# Test config: sudo nginx -t
# Reload: sudo nginx -s reload
```

- 📎 https://nginx.org/en/docs/

---

## 7. Docker & Kubernetes

### 7.1 Docker + Docker Compose

```bash
sudo pacman -S docker docker-compose docker-buildx
sudo systemctl enable --now docker.service
sudo usermod -aG docker $USER
newgrp docker   # Apply immediately (or reboot)
docker run hello-world   # Test
```

**Performance fix for Arch (enable native overlay diff):**
```bash
echo "options overlay metacopy=off redirect_dir=off" | sudo tee /etc/modprobe.d/disable-overlay-redirect-dir.conf
sudo modprobe -r overlay && sudo modprobe overlay
sudo systemctl restart docker.service
docker info | grep "Native Overlay"  # Should show "true"
```

**Socket activation (faster boot — Docker starts only when first used):**
```bash
sudo systemctl disable docker.service
sudo systemctl enable docker.socket
```

- 📎 https://docs.docker.com/
- 📎 https://wiki.archlinux.org/title/Docker

### 7.2 Docker Compose for Local Dev Stack

```yaml
# docker-compose.yml — Django + Postgres + Redis + Celery + Elasticsearch
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp_db
      POSTGRES_USER: myapp_user
      POSTGRES_PASSWORD: changeme
    volumes: [postgres_data:/var/lib/postgresql/data]
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.17.0
    environment:
      discovery.type: single-node
      xpack.security.enabled: "false"
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
    ports: ["9200:9200"]

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes: [".:/app"]
    ports: ["8000:8000"]
    env_file: [.env]
    depends_on: [db, redis]

  celery_worker:
    build: .
    command: celery -A myproject worker -l info
    volumes: [".:/app"]
    env_file: [.env]
    depends_on: [db, redis]

volumes:
  postgres_data:
```

### 7.3 Kubernetes Tools

```bash
sudo pacman -S kubectl minikube helm

# Start local cluster:
minikube start --driver=docker --memory=4096 --cpus=2

# k3s alternative (lightweight, production-grade):
curl -sfL https://get.k3s.io | sh -

# k9s — terminal UI for Kubernetes:
sudo pacman -S k9s
```

| Tool | Purpose |
|---|---|
| `kubectl` | CLI for Kubernetes cluster management |
| `minikube` | Local single-node K8s cluster |
| `k3s` | Lightweight production K8s (Rancher) |
| `helm` | Kubernetes package manager (charts) |
| `k9s` | Terminal UI for K8s cluster navigation |
| `lens` | Desktop GUI for K8s (`yay -S lens-bin`) |

- 📎 https://kubernetes.io/docs/reference/kubectl/
- 📎 https://minikube.sigs.k8s.io/
- 📎 https://helm.sh/
- 📎 https://k9scli.io/

### 7.4 Container Registry Auth

```bash
# Docker Hub:
docker login

# AWS ECR:
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com

# Google Artifact Registry:
gcloud auth configure-docker us-central1-docker.pkg.dev

# GitHub Container Registry:
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

---

## 8. Infrastructure as Code

### 8.1 Terraform

```bash
sudo pacman -S terraform
terraform -v

# Workflow:
# terraform init      # Initialize provider plugins
# terraform plan      # Preview changes
# terraform apply     # Apply changes
# terraform destroy   # Tear down infrastructure
```

- 📎 https://www.terraform.io/

### 8.2 OpenTofu (Open-source Terraform fork)

```bash
sudo pacman -S opentofu
tofu -v
```

- 📎 https://opentofu.org/

### 8.3 Ansible (Configuration Management)

```bash
uv tool install ansible
ansible --version
```

- 📎 https://docs.ansible.com/

### 8.4 Pulumi (IaC with real programming languages)

```bash
yay -S pulumi-bin
pulumi new python   # Create Python IaC project
```

- 📎 https://www.pulumi.com/

---

## 9. CI/CD Pipelines

### 9.1 GitHub Actions Local Runner — act

Run GitHub Actions workflows locally before pushing:

```bash
sudo pacman -S act
cd /your/repo && act   # Runs .github/workflows/*.yml locally
```

- 📎 https://github.com/nektos/act

### 9.2 GitLab CI Runner

```bash
sudo pacman -S gitlab-runner
sudo gitlab-runner register  # Follow prompts with your GitLab token
```

- 📎 https://docs.gitlab.com/runner/

### 9.3 Sample GitHub Actions for Python + Docker

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - run: uv run ruff check .
      - run: uv run pytest

  docker:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: false
          tags: myapp:latest
```

---

## 10. Data Engineering & Science

### 10.1 Core Libraries

```bash
uv add pandas numpy scipy matplotlib seaborn plotly kaleido
uv add scikit-learn polars pyarrow
```

| Library | Purpose |
|---|---|
| **Pandas** | DataFrames for tabular data |
| **Polars** | Blazing-fast Rust-based DataFrames (10-100× faster than Pandas) |
| **NumPy** | Numerical computing |
| **SciPy** | Scientific computing |
| **Matplotlib** | Static plotting |
| **Seaborn** | Statistical visualization |
| **Plotly** | Interactive plots |
| **scikit-learn** | ML preprocessing, models, pipelines |
| **PyArrow** | Apache Arrow for columnar data & Parquet I/O |

- 📎 https://pandas.pydata.org/ · https://pola.rs/ · https://numpy.org/
- 📎 https://scikit-learn.org/ · https://plotly.com/python/

### 10.2 Apache Kafka — Local Setup (Redpanda)

Redpanda is Kafka-API-compatible, no JVM, ~512MB RAM:

```yaml
# docker-compose.kafka.yml
services:
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:latest
    command:
      - redpanda start --smp 1 --memory 512M --overprovisioned
      - --kafka-addr internal://0.0.0.0:9092,external://0.0.0.0:19092
      - --advertise-kafka-addr internal://redpanda:9092,external://localhost:19092
    ports: ["19092:19092", "9644:9644"]

  console:
    image: docker.redpanda.com/redpandadata/console:latest
    ports: ["8080:8080"]
    environment:
      KAFKA_BROKERS: redpanda:9092
    depends_on: [redpanda]
```

- 📎 https://docs.redpanda.com/current/get-started/quick-start/

### 10.3 ETL & Workflow Orchestration

```bash
uv add prefect           # Modern Python-native orchestration
# or: uv add apache-airflow  # Industry standard (heavier)
# or: uv add luigi           # Lightweight (Spotify)
```

- 📎 https://docs.prefect.io/ · https://airflow.apache.org/ · https://luigi.readthedocs.io/

### 10.4 Dask (Parallel Computing)

```bash
uv add "dask[complete]"
```

Scales Pandas/NumPy to larger-than-memory datasets using parallel workers.

- 📎 https://www.dask.org/

---

## 11. Frontend Development

### 11.1 Node.js via nvm

```bash
sudo pacman -S nvm
```

Add to `~/.zshrc`:
```bash
source /usr/share/nvm/init-nvm.sh
```

```bash
nvm install --lts && nvm use --lts
node -v && npm -v
```

- 📎 https://github.com/nvm-sh/nvm

### 11.2 Package Managers — npm, yarn, pnpm

```bash
corepack enable
corepack prepare pnpm@latest --activate    # pnpm (recommended — fastest, disk-efficient)
corepack prepare yarn@stable --activate    # Yarn 4+
```

- 📎 https://pnpm.io/ · https://yarnpkg.com/

### 11.3 React + Vite

```bash
pnpm create vite@latest my-react-app -- --template react-ts
cd my-react-app && pnpm install && pnpm dev
```

- 📎 https://react.dev/ · https://vite.dev/

### 11.4 Next.js

```bash
pnpm create next-app@latest my-next-app
cd my-next-app && pnpm dev
```

- 📎 https://nextjs.org/docs

### 11.5 TypeScript

```bash
pnpm add -D typescript
npx tsc --init   # Creates tsconfig.json
```

- 📎 https://www.typescriptlang.org/

### 11.6 Tailwind CSS

```bash
pnpm add -D tailwindcss @tailwindcss/postcss postcss
npx tailwindcss init
```

- 📎 https://tailwindcss.com/docs/installation

---

## 12. Code Editors & IDEs

### 12.1 VS Code ⭐ (Primary Recommendation)

```bash
# Microsoft build (full marketplace, Remote Dev, Copilot):
yay -S visual-studio-code-bin

# Open-source build (Open VSX marketplace):
sudo pacman -S code
```

**Essential Extensions:**

| Extension | ID | Purpose |
|---|---|---|
| Python | `ms-python.python` | Language support, debugging, venvs |
| Pylance | `ms-python.vscode-pylance` | Fast IntelliSense, type checking |
| Ruff | `charliermarsh.ruff` | Linter + formatter |
| Docker | `ms-azuretools.vscode-docker` | Dockerfile/Compose support |
| GitLens | `eamodio.gitlens` | Git blame, history, authorship |
| Remote SSH | `ms-vscode-remote.remote-ssh` | Edit files on remote machines |
| Remote Containers | `ms-vscode-remote.remote-containers` | Develop inside Docker |
| Jupyter | `ms-toolsai.jupyter` | Notebook support |
| GitHub Copilot | `GitHub.copilot` | AI pair programmer ($10/mo) |
| Continue | `Continue.continue` | Open-source AI assistant (local Ollama or any API) |
| Thunder Client | `rangav.vscode-thunder-client` | REST API testing (Postman alternative) |
| Tailwind CSS IntelliSense | `bradlc.vscode-tailwindcss` | Tailwind class autocompletion |
| ESLint | `dbaeumer.vscode-eslint` | JavaScript/TypeScript linting |
| Prettier | `esbenp.prettier-vscode` | Code formatter for JS/TS/CSS/HTML |
| Error Lens | `usernamehw.errorlens` | Inline error/warning display |
| Todo Tree | `Gruntfuggly.todo-tree` | Find TODO/FIXME comments |
| Material Icon Theme | `PKief.material-icon-theme` | Better file icons |

**Bulk install:**
```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-azuretools.vscode-docker
code --install-extension eamodio.gitlens
code --install-extension ms-vscode-remote.remote-ssh
code --install-extension ms-vscode-remote.remote-containers
code --install-extension ms-toolsai.jupyter
code --install-extension Continue.continue
code --install-extension rangav.vscode-thunder-client
code --install-extension bradlc.vscode-tailwindcss
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension usernamehw.errorlens
code --install-extension Gruntfuggly.todo-tree
code --install-extension PKief.material-icon-theme
```

**Recommended `settings.json`:**
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": { "source.fixAll": "explicit", "source.organizeImports": "explicit" }
  },
  "[javascript][typescript][typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "python.analysis.typeCheckingMode": "basic",
  "files.autoSave": "onFocusChange",
  "terminal.integrated.defaultProfile.linux": "zsh",
  "git.autofetch": true,
  "workbench.iconTheme": "material-icon-theme"
}
```

- 📎 https://code.visualstudio.com/

### 12.2 VS Codium (Telemetry-Free VS Code)

```bash
yay -S vscodium-bin
```

MIT-licensed, no telemetry, uses Open VSX marketplace. Same extensions work (install manually if not on Open VSX).

- 📎 https://vscodium.com/

### 12.3 Neovim + LazyVim

```bash
sudo pacman -S neovim
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
nvim   # Plugins auto-install on first launch
```

LazyVim comes pre-configured with LSP, Treesitter, Telescope, and sane defaults. Add Python support: type `:LazyExtras` and enable `lang.python`.

**AstroNvim alternative:**
```bash
git clone --depth 1 https://github.com/AstroNvim/template ~/.config/nvim
```

- 📎 https://www.lazyvim.org/ · https://astronvim.com/

### 12.4 PyCharm

```bash
sudo pacman -S pycharm-community-edition   # Free — Python + Django support
yay -S pycharm-professional                # Paid — adds FastAPI, Docker, DB tools, Remote Dev
```

- 📎 https://www.jetbrains.com/pycharm/

### 12.5 Zed (Modern, GPU-Accelerated Editor)

```bash
yay -S zed-editor
```

Built in Rust, extremely fast, built-in AI assistant, multiplayer editing.

- 📎 https://zed.dev/

### 12.6 Cursor (AI-First Code Editor)

```bash
yay -S cursor-bin
```

VS Code fork with deep AI integration (Claude, GPT-4, etc.) for code generation, editing, and chat.

- 📎 https://cursor.com/

---

## 13. Terminal, Shell & CLI Tools

### 13.1 Zsh + Oh My Zsh

```bash
sudo pacman -S zsh
chsh -s $(which zsh)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Essential plugins:
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

In `~/.zshrc`:
```bash
plugins=(git zsh-autosuggestions zsh-syntax-highlighting docker kubectl)
```

- 📎 https://ohmyz.sh/

### 13.2 Fish Shell (Alternative)

```bash
sudo pacman -S fish
# Try: fish (without switching default)
# Switch: chsh -s $(which fish)
```

- 📎 https://fishshell.com/

### 13.3 Terminal Emulators

| Terminal | Install | Highlights |
|---|---|---|
| **Kitty** ⭐ | `sudo pacman -S kitty` | GPU-accelerated, splits, tabs, ligatures, image display |
| **Alacritty** | `sudo pacman -S alacritty` | Fastest, minimalist (pair with tmux) |
| **WezTerm** | `sudo pacman -S wezterm` | GPU-accel, Lua config, built-in multiplexer |
| **Ghostty** | `yay -S ghostty` | New, Zig-based, extremely fast, native GPU rendering |

- 📎 https://sw.kovidgoyal.net/kitty/ · https://alacritty.org/
- 📎 https://wezfurlong.org/wezterm/ · https://ghostty.org/

### 13.4 Starship Prompt

```bash
sudo pacman -S starship
# Add to ~/.zshrc: eval "$(starship init zsh)"
```

Customizable via `~/.config/starship.toml`. Shows git branch, Python version, Docker context, K8s namespace, Node version, and more.

- 📎 https://starship.rs/

### 13.5 Terminal Multiplexers

```bash
sudo pacman -S tmux     # Classic — Ctrl-b c (new window), Ctrl-b % (split vertical)
sudo pacman -S zellij   # Modern Rust alternative — beginner-friendly bottom help bar
```

- 📎 https://github.com/tmux/tmux · https://zellij.dev/

### 13.6 Modern CLI Replacements

```bash
sudo pacman -S fzf ripgrep fd bat eza zoxide procs dust duf tokei hyperfine
```

| Tool | Replaces | Purpose |
|---|---|---|
| `fzf` | — | Fuzzy finder for files, history, everything |
| `ripgrep` (`rg`) | `grep` | 10× faster recursive search |
| `fd` | `find` | Fast, intuitive file finder |
| `bat` | `cat` | Syntax highlighting, Git integration |
| `eza` | `ls` | Icons, Git status, tree view |
| `zoxide` | `cd` | Smart directory jumping (learns your habits) |
| `procs` | `ps` | Modern process viewer |
| `dust` | `du` | Visual proportional disk usage |
| `duf` | `df` | Colorful disk free output |
| `tokei` | `cloc` | Fast code line counter |
| `hyperfine` | `time` | Command benchmarking with statistical analysis |

**Shell aliases** (add to `~/.zshrc`):
```bash
eval "$(zoxide init zsh)"
source /usr/share/fzf/key-bindings.zsh
source /usr/share/fzf/completion.zsh
alias ls='eza --icons --group-directories-first'
alias ll='eza -la --icons --group-directories-first --git'
alias lt='eza -la --icons --tree --level=2'
alias cat='bat --style=plain --paging=never'
alias grep='rg'
alias find='fd'
alias du='dust'
alias df='duf'
alias ps='procs'
```

### 13.7 TUI Tools

```bash
sudo pacman -S lazygit
yay -S lazydocker
```

| Tool | Purpose |
|---|---|
| `lazygit` | Full Git UI in terminal — staging, commits, branches, rebasing |
| `lazydocker` | Docker container/image/volume management TUI |

- 📎 https://github.com/jesseduffield/lazygit
- 📎 https://github.com/jesseduffield/lazydocker

---

## 14. Git & Version Control

### 14.1 Git Configuration

```bash
sudo pacman -S git

git config --global user.name "Nirajan Karki"
git config --global user.email "your@email.com"

# GPG signing
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# Aliases
git config --global alias.st "status -sb"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.ci "commit"
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.last "log -1 HEAD --stat"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.unstage "reset HEAD --"

# Defaults
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global fetch.prune true
git config --global diff.colorMoved zebra
git config --global merge.conflictstyle zdiff3
git config --global rerere.enabled true
```

**Global `.gitignore`:**
```bash
cat > ~/.gitignore_global << 'EOF'
# OS
.DS_Store
Thumbs.db

# Editors
.idea/
.vscode/
*.swp
*.swo
*~

# Python
__pycache__/
*.pyc
*.pyo
.venv/
*.egg-info/
dist/
build/

# Node
node_modules/

# Environment
.env
.env.local
.env.*.local

# Docker
docker-compose.override.yml
EOF

git config --global core.excludesfile ~/.gitignore_global
```

- 📎 https://git-scm.com/doc

### 14.2 GitHub CLI (gh)

```bash
sudo pacman -S github-cli
gh auth login       # Interactive browser auth
gh auth status      # Verify

# Common usage:
gh repo create my-project --public --clone
gh pr create --title "feat: add search" --body "Adds semantic search"
gh pr list
gh issue create --title "Bug: API timeout"
gh release create v1.0.0
```

- 📎 https://cli.github.com/manual/

### 14.3 Conventional Commits

Format: `type(scope): description`

| Type | Use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change without feature/fix |
| `test` | Adding tests |
| `chore` | Build/tools/dependencies |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

Branch naming: `feature/PROJ-123-add-search`, `bugfix/fix-login-crash`, `hotfix/patch-security`

- 📎 https://www.conventionalcommits.org/

---

## 15. Browsers

### 15.1 Development Browser — Firefox Developer Edition ⭐

Best browser for web development with advanced CSS Grid inspector, Flexbox tools, network analysis, and responsive design mode.

```bash
sudo pacman -S firefox-developer-edition
```

📎 https://www.mozilla.org/en-US/firefox/developer/

### 15.2 Secondary Dev Browser — Brave

Chromium-based for testing, with built-in ad/tracker blocking and DevTools identical to Chrome.

```bash
yay -S brave-bin
```

📎 https://brave.com/

### 15.3 Personal/Privacy Browser — LibreWolf ⭐

Privacy-hardened Firefox fork. Telemetry removed, uBlock Origin pre-installed, anti-fingerprinting enabled by default.

```bash
yay -S librewolf-bin
```

📎 https://librewolf.net/

### 15.4 Maximum Privacy — Mullvad Browser

Co-developed with the Tor Project. Anti-fingerprinting focus. All users look identical.

```bash
yay -S mullvad-browser-bin
```

📎 https://mullvad.net/en/browser

### 15.5 Chromium Testing — Ungoogled Chromium

Chromium with all Google tracking removed. Use for testing Chrome compatibility.

```bash
yay -S ungoogled-chromium-bin
```

📎 https://github.com/nickel-browser/nickel  (previously ungoogled-chromium)

### 15.6 Browser Strategy

| Browser | Use Case |
|---|---|
| **Firefox Developer Edition** | Primary development (DevTools, CSS Grid inspector, network analysis) |
| **Brave** | Secondary dev testing (Chromium engine), casual browsing |
| **LibreWolf** | Personal browsing, banking, private accounts |
| **Mullvad Browser** | Maximum anonymity when needed |

### 15.7 Essential Browser Extensions

**For Development:**
| Extension | Purpose |
|---|---|
| uBlock Origin | Ad/tracker blocker (essential everywhere) |
| React DevTools | Inspect React component tree and state |
| Vue.js DevTools | Vue component inspector |
| JSON Viewer | Pretty-prints JSON responses |
| Wappalyzer | Identify tech stack on any website |
| Refined GitHub | Enhanced GitHub UI |
| Octotree | GitHub code tree sidebar |
| ColorZilla | Color picker and eyedropper |
| Responsive Viewer | Test multiple screen sizes simultaneously |

**For Privacy/Personal:**
| Extension | Purpose |
|---|---|
| uBlock Origin | Best-in-class content blocker |
| Bitwarden | Password manager |
| Dark Reader | Dark mode for all sites |
| Privacy Badger | EFF's adaptive tracker blocker |
| ClearURLs | Remove tracking parameters from URLs |
| SponsorBlock | Skip YouTube sponsors |

---

## 16. Note-Taking & Knowledge Management

### 16.1 Obsidian ⭐ (Primary Personal Knowledge Base)

Local-first, Markdown-based, works offline, Git-friendly. Graph view shows connections between notes. 1000+ community plugins.

```bash
sudo pacman -S obsidian
```

**Why Obsidian for developers:**
- Notes are plain `.md` files — version-control with Git
- Dataview plugin turns notes into a queryable database
- Templater plugin for note templates
- Canvas for visual brainstorming
- Mermaid diagram support built-in
- Free for personal use

**Recommended plugins:** Templater, Dataview, Calendar, Kanban, Git (auto-commit/push), Advanced Tables, Excalidraw.

📎 https://obsidian.md/

### 16.2 Notion (Client Collaboration & Project Wikis)

Web-based workspace with databases, wikis, and team collaboration. Best for sharing with clients who need a GUI.

```bash
yay -S notion-app-electron
# Or just use https://notion.so in browser
```

📎 https://www.notion.so/

### 16.3 Logseq (Open-Source Outliner Alternative)

Block-based outliner with daily journals. Open-source (AGPL). Graph view like Obsidian.

```bash
yay -S logseq-desktop-bin
```

📎 https://logseq.com/

### 16.4 AnyType (Notion Alternative, Local-First)

Open-source, local-first knowledge base with blocks, relations, and databases. E2E encrypted sync.

```bash
yay -S anytype-bin
```

📎 https://anytype.io/

### 16.5 When to Use Which

| Tool | Best For | Offline? | Open Source? |
|---|---|---|---|
| **Obsidian** | Personal knowledge base, dev notes, learning | Yes | Partial |
| **Notion** | Client wikis, team databases, project docs | No | No |
| **Logseq** | Daily journaling, block-level referencing | Yes | Yes |
| **AnyType** | Private knowledge base, Notion replacement | Yes | Yes |

**Recommendation:** Obsidian as primary. Notion for client-facing work.

---

## 17. Project Management & Freelance Tools

### 17.1 Task & Project Management

**Trello (Kanban boards — simple, visual):**
- Web: https://trello.com/
- 📎 Free tier: unlimited personal boards

**ClickUp (All-in-one project management):**
- Web: https://clickup.com/
- 📎 Free tier: unlimited tasks, 100MB storage

**Linear (Modern, fast, developer-focused):**
- Web: https://linear.app/
- 📎 Free for small teams, GitHub integration

**Plane (Open-source Linear/Jira alternative):**
```bash
# Self-hosted via Docker:
git clone https://github.com/makeplane/plane.git
cd plane && docker compose up -d
```
📎 https://plane.so/

**Todoist (Personal task manager):**
```bash
yay -S todoist-electron
# Or: https://todoist.com/ in browser
```
📎 https://todoist.com/

### 17.2 Time Tracking (Essential for Freelancing)

**Toggl Track ⭐ (Recommended — simple, integrates with everything):**
- Web: https://track.toggl.com/
- One-click timer, detailed reports, project/client categorization
- Free tier: unlimited tracking

**Clockify (Free alternative with more features):**
- Web: https://app.clockify.me/
- Unlimited users on free tier, timesheets, invoicing

**Wakatime (Automatic coding time tracking):**
- VS Code extension: `WakaTime.vscode-wakatime`
- Tracks time per project, language, and file automatically
- 📎 https://wakatime.com/

### 17.3 Invoicing & Finance

**Invoice Ninja (Open-source invoicing):**
```bash
# Self-hosted Docker or use cloud at https://invoiceninja.com/
docker run -d -p 8080:80 invoiceninja/invoiceninja
```
📎 https://invoiceninja.com/

**Wave Accounting (Free cloud accounting):**
📎 https://www.waveapps.com/

### 17.4 Client Contracts & Proposals

**AND.CO (by Fiverr — free proposals, contracts, invoicing):**
📎 https://www.and.co/

**HelloSign / Dropbox Sign (e-signatures):**
📎 https://sign.dropbox.com/

### 17.5 Upwork-Specific Tools

**Upwork Desktop App:**
```bash
yay -S upwork
# Required for hourly contracts — takes screenshots + tracks activity
```
📎 https://www.upwork.com/ab/downloads/

---

## 18. Communication & Collaboration

### 18.1 Slack

```bash
yay -S slack-desktop
```
📎 https://slack.com/

### 18.2 Discord

```bash
sudo pacman -S discord
```
📎 https://discord.com/

### 18.3 Zoom

```bash
yay -S zoom
```

**Wayland screen sharing fix:**
```bash
sudo pacman -S xdg-desktop-portal xdg-desktop-portal-kde pipewire-v4l2
```
📎 https://zoom.us/

### 18.4 Telegram

```bash
sudo pacman -S telegram-desktop
```
📎 https://telegram.org/

### 18.5 Email — Thunderbird

```bash
sudo pacman -S thunderbird
```

Built-in calendar, contacts, and RSS reader. Supports Gmail, Outlook, and any IMAP/SMTP.

📎 https://www.thunderbird.net/

### 18.6 KDE Connect (Phone Integration)

```bash
sudo pacman -S kdeconnect
sudo ufw allow 1714:1764/udp && sudo ufw allow 1714:1764/tcp
```

Syncs clipboard, notifications, files, and SMS between phone and desktop.

📎 https://kdeconnect.kde.org/

---

## 19. Security & Privacy

### 19.1 Firewall — UFW

```bash
sudo pacman -S ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 1714:1764/udp   # KDE Connect
sudo ufw allow 1714:1764/tcp
sudo ufw enable
sudo systemctl enable --now ufw.service
```
📎 https://wiki.archlinux.org/title/Uncomplicated_Firewall

### 19.2 Fail2ban

```bash
sudo pacman -S fail2ban
```

Create `/etc/fail2ban/jail.local`:
```ini
[DEFAULT]
bantime = 1d
findtime = 10m
maxretry = 5

[sshd]
enabled = true
backend = systemd
maxretry = 3
bantime = 2w
```

```bash
sudo systemctl enable --now fail2ban.service
```
📎 https://wiki.archlinux.org/title/Fail2ban

### 19.3 SSH Hardening

Edit `/etc/ssh/sshd_config`:
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
AllowUsers yourusername
```

```bash
ssh-keygen -t ed25519 -a 100 -C "your@email.com"
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host
sudo systemctl restart sshd
```
📎 https://wiki.archlinux.org/title/OpenSSH

### 19.4 Password Manager — Bitwarden + KeePassXC

```bash
sudo pacman -S bitwarden keepassxc
```

| Tool | Use Case |
|---|---|
| **Bitwarden** | Cloud-synced across all devices, browser extension, team sharing |
| **KeePassXC** | Local/offline, sync .kdbx file via Syncthing, maximum control |

📎 https://bitwarden.com/ · https://keepassxc.org/

### 19.5 Encrypted DNS (DNS over HTTPS)

```bash
sudo pacman -S dnscrypt-proxy
```

Edit `/etc/dnscrypt-proxy/dnscrypt-proxy.toml`:
```toml
server_names = ['cloudflare', 'quad9-dnscrypt-ip4-nofilter-pri']
listen_addresses = ['127.0.0.1:53', '[::1]:53']
require_dnssec = true
require_nolog = true
```

Set DNS to `127.0.0.1` in NetworkManager, then:
```bash
sudo systemctl enable --now dnscrypt-proxy.service
```
📎 https://wiki.archlinux.org/title/Dnscrypt-proxy

### 19.6 VPN

**Mullvad VPN ⭐ (no email, no account, anonymous payment):**
```bash
yay -S mullvad-vpn-bin
sudo systemctl enable --now mullvad-daemon.service
mullvad account login <ACCOUNT_NUMBER>
mullvad connect
```
📎 https://mullvad.net/

**ProtonVPN (free tier available):**
```bash
sudo pacman -S proton-vpn-gtk-app
```
📎 https://protonvpn.com/

### 19.7 Disk Encryption (LUKS)

Must be configured at install time. CachyOS installer has a LUKS checkbox.

```bash
# Verify: lsblk -f (look for crypto_LUKS)
# Backup headers: sudo cryptsetup luksHeaderBackup /dev/sdXn --header-backup-file /safe/header.img
```
📎 https://wiki.archlinux.org/title/Dm-crypt

### 19.8 AppArmor

```bash
sudo pacman -S apparmor apparmor.d
```

Add kernel parameter (edit `/boot/loader/entries/*.conf`):
```
lsm=landlock,lockdown,yama,integrity,apparmor,bpf
```

```bash
sudo systemctl enable --now apparmor.service
# Reboot. Verify: sudo aa-status
```
📎 https://wiki.archlinux.org/title/AppArmor

### 19.9 File Sync — Syncthing

```bash
sudo pacman -S syncthing
systemctl --user enable --now syncthing.service
# Web UI: http://127.0.0.1:8384
```

Continuous file sync between devices. No cloud — direct peer-to-peer. Encrypted.

📎 https://syncthing.net/

---

## 20. System Maintenance & Monitoring

### 20.1 Btrfs Snapshots — Snapper

CachyOS defaults to Btrfs. `snap-pac` auto-creates snapshots on every pacman transaction.

```bash
sudo pacman -S snapper snap-pac btrfs-assistant
snapper list         # View snapshots
# Restore: boot from GRUB snapshot entry or snapper rollback
```
📎 https://wiki.cachyos.org/configuration/btrfs_snapshots/

### 20.2 Mirror Optimization

```bash
sudo pacman -S reflector
sudo reflector --country 'Nepal' --age 12 --protocol https --sort rate --save /etc/pacman.d/mirrorlist
sudo systemctl enable --now reflector.timer

# CachyOS-specific mirrors:
sudo pacman -S cachyos-rate-mirrors && sudo cachyos-rate-mirrors
```
📎 https://wiki.archlinux.org/title/Reflector

### 20.3 System Monitoring

```bash
sudo pacman -S btop nvtop mission-center
```

| Tool | Purpose |
|---|---|
| `btop` | Full system TUI monitor (CPU, RAM, disk, network, GPU) |
| `nvtop` | GPU process monitor (supports AMD despite the name) |
| `mission-center` | GTK4 GUI system monitor (like Windows Task Manager) |

📎 https://github.com/aristocratos/btop · https://github.com/Syllo/nvtop

### 20.4 Disk Usage

```bash
sudo pacman -S ncdu dust
# ncdu /       — interactive disk usage browser
# dust         — visual proportional disk usage
```

### 20.5 Package Cache Cleanup

```bash
sudo pacman -S pacman-contrib
sudo paccache -r             # Keep last 3 versions
sudo paccache -ruk0          # Remove all uninstalled cache
sudo systemctl enable --now paccache.timer   # Weekly auto-cleanup
```

### 20.6 Update Strategy

Full auto-updates are risky on Arch. CachyOS provides `cachy-update` for interactive reviews:
```bash
sudo pacman -S cachy-update   # Checks hourly, notifies in systray
# Best practice: review updates, ensure Snapper has recent snapshot, reboot after kernel updates
```

---

## 21. Media, Office & Personal

### 21.1 Media Players

```bash
sudo pacman -S vlc mpv
```

**mpv config** (`~/.config/mpv/mpv.conf`):
```ini
hwdec=auto
vo=gpu-next
profile=gpu-hq
```

📎 https://www.videolan.org/vlc/ · https://mpv.io/

### 21.2 Music — Spotify + Strawberry

```bash
yay -S spotify                     # Streaming
sudo pacman -S strawberry          # Local music (FLAC, MP3, gapless)
```
📎 https://open.spotify.com/ · https://www.strawberrymusicplayer.org/

### 21.3 Image Editing

```bash
sudo pacman -S gimp inkscape
# GIMP — raster/photo editing (Photoshop alternative)
# Inkscape — vector graphics (Illustrator alternative)
```
📎 https://www.gimp.org/ · https://inkscape.org/

### 21.4 Screenshots

```bash
sudo pacman -S flameshot spectacle
# flameshot gui — annotation tools, arrows, blur
# spectacle — KDE default (PrintScreen key)
```
📎 https://flameshot.org/ · https://apps.kde.org/spectacle/

### 21.5 Screen Recording / Streaming

```bash
sudo pacman -S obs-studio
```

OBS Studio — open-source recording and streaming. Supports Wayland via PipeWire.

📎 https://obsproject.com/

### 21.6 Office Suite

```bash
sudo pacman -S libreoffice-fresh    # Latest features
yay -S onlyoffice-bin               # Better MS Office compatibility
```
📎 https://www.libreoffice.org/ · https://www.onlyoffice.com/

### 21.7 PDF Viewer — Okular

```bash
sudo pacman -S okular   # Pre-installed on CachyOS KDE
```
📎 https://okular.kde.org/

### 21.8 Clipboard Manager — CopyQ

```bash
sudo pacman -S copyq
# Klipper also pre-installed with KDE Plasma (system tray)
```
📎 https://hluk.github.io/CopyQ/

### 21.9 Calendar — KOrganizer

```bash
sudo pacman -S korganizer
# Or use Thunderbird's built-in calendar
```
📎 https://kontact.kde.org/components/korganizer/

### 21.10 File Manager Enhancements

```bash
sudo pacman -S dolphin kdegraphics-thumbnailers ffmpegthumbs
# Dolphin is KDE's file manager (pre-installed). Thumbnail packages add image/video previews.
```

### 21.11 Archive Manager

```bash
sudo pacman -S ark p7zip unrar
# ark is KDE's archive manager. p7zip/unrar add format support.
```

---

## 22. Bulk Install Commands

Run these to install most system packages in one shot:

```bash
# ===== SECTION 1: System & GPU =====
sudo pacman -S cachyos-settings ananicy-cpp cachyos-ananicy-rules \
  mesa lib32-mesa vulkan-radeon lib32-vulkan-radeon vulkan-icd-loader lib32-vulkan-icd-loader \
  libva-mesa-driver lib32-libva-mesa-driver mesa-vdpau lib32-mesa-vdpau \
  rocm-hip-sdk rocm-opencl-sdk radeontop rocm-smi-lib

# ===== SECTION 5: Databases =====
sudo pacman -S postgresql mariadb redis sqlite dbeaver

# ===== SECTION 6-8: DevOps & Cloud =====
sudo pacman -S docker docker-compose docker-buildx \
  kubectl minikube helm k9s \
  aws-cli-v2 azure-cli terraform \
  nginx act gitlab-runner

# ===== SECTION 10-11: Editors & Terminal =====
sudo pacman -S neovim zsh kitty alacritty wezterm starship tmux zellij \
  fzf ripgrep fd bat eza zoxide procs dust duf tokei hyperfine lazygit \
  git github-cli nvm

# ===== SECTION 13+: Apps & Productivity =====
sudo pacman -S firefox-developer-edition obsidian \
  flameshot spectacle kdeconnect thunderbird korganizer \
  bitwarden keepassxc syncthing copyq okular \
  discord telegram-desktop \
  vlc mpv gimp inkscape obs-studio libreoffice-fresh strawberry \
  btop nvtop mission-center ncdu pacman-contrib reflector \
  snapper snap-pac btrfs-assistant \
  ufw fail2ban dnscrypt-proxy apparmor apparmor.d openssh \
  ark p7zip unrar dolphin kdegraphics-thumbnailers ffmpegthumbs \
  pycharm-community-edition

# ===== AUR PACKAGES (yay/paru) =====
yay -S visual-studio-code-bin vscodium-bin \
  brave-bin librewolf-bin mullvad-browser-bin ungoogled-chromium-bin \
  notion-app-electron logseq-desktop-bin anytype-bin \
  zoom slack-desktop spotify upwork \
  mongodb-bin mongodb-compass google-cloud-cli \
  mullvad-vpn-bin lazydocker onlyoffice-bin \
  zed-editor cursor-bin ghostty \
  amdgpu_top-bin todoist-electron

# ===== POST-INSTALL ESSENTIALS =====
sudo usermod -aG render,video,docker $USER
sudo systemctl enable --now docker.service postgresql redis ollama.service ufw fail2ban syncthing@$USER.service
chsh -s $(which zsh)

# Install uv:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install global Python CLI tools via uv:
uv tool install ruff jupyterlab httpie pre-commit mypy ipython
```

---

## 23. Complete ~/.zshrc Configuration

```bash
# ======================================
# CachyOS Developer Workstation — .zshrc
# ======================================

# Oh My Zsh
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"   # Or leave empty if using Starship
plugins=(git zsh-autosuggestions zsh-syntax-highlighting docker kubectl)
source $ZSH/oh-my-zsh.sh

# ---- PATH ----
export PATH="$HOME/.local/bin:$PATH"

# ---- uv (Python package manager) ----
eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"

# ---- Node.js (nvm) ----
source /usr/share/nvm/init-nvm.sh

# ---- Starship prompt ----
eval "$(starship init zsh)"

# ---- zoxide (smart cd) ----
eval "$(zoxide init zsh)"

# ---- fzf ----
source /usr/share/fzf/key-bindings.zsh
source /usr/share/fzf/completion.zsh

# ---- ROCm (AMD GPU) ----
# Uncomment for your GPU:
# export HSA_OVERRIDE_GFX_VERSION=11.0.0  # RDNA3 (RX 7900/7800/7700)
# export HSA_OVERRIDE_GFX_VERSION=10.3.0  # RDNA2 (RX 6000 series)

# ---- Modern CLI aliases ----
alias ls='eza --icons --group-directories-first'
alias ll='eza -la --icons --group-directories-first --git'
alias lt='eza -la --icons --tree --level=2'
alias cat='bat --style=plain --paging=never'
alias grep='rg'
alias find='fd'
alias du='dust'
alias df='duf'
alias ps='procs'
alias lg='lazygit'
alias ld='lazydocker'

# ---- Docker ----
alias dcu='docker compose up -d'
alias dcd='docker compose down'
alias dcl='docker compose logs -f'
alias dps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# ---- Python / uv shortcuts ----
alias py='uv run python'
alias pyt='uv run pytest'
alias lint='uv run ruff check . --fix && uv run ruff format .'

# ---- Git shortcuts ----
alias gs='git status -sb'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias glog='git log --oneline --graph --decorate --all'
```

---

## 24. AI/ML Project Quickstart Template

Create a new AI/ML project with PyTorch ROCm, LangChain, and JupyterLab in under 2 minutes:

```bash
# 1. Create project
uv init my-ai-project --python 3.12
cd my-ai-project

# 2. Add PyTorch ROCm index to pyproject.toml
cat >> pyproject.toml << 'EOF'

[tool.uv.sources]
torch = [{ index = "pytorch-rocm", marker = "sys_platform == 'linux'" }]
torchvision = [{ index = "pytorch-rocm", marker = "sys_platform == 'linux'" }]
pytorch-triton-rocm = [{ index = "pytorch-rocm", marker = "sys_platform == 'linux'" }]

[[tool.uv.index]]
name = "pytorch-rocm"
url = "https://download.pytorch.org/whl/rocm6.4"
explicit = true

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "W"]
EOF

# 3. Install everything
uv add torch torchvision "pytorch-triton-rocm>=3.5.1"
uv add langchain langchain-core langchain-community langchain-ollama langchain-chroma
uv add llama-index
uv add transformers sentence-transformers
uv add chromadb
uv add numpy pandas matplotlib
uv add --dev ipykernel pytest ruff

# 4. Verify GPU
uv run python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"

# 5. Launch Jupyter
uv run --with jupyter jupyter lab

# 6. Initialize git
git init && echo -e '.venv/\n__pycache__/' > .gitignore
git add . && git commit -m "feat: initial project setup"
```

**Project structure:**
```
my-ai-project/
├── .python-version       # "3.12"
├── .venv/                # Auto-created by uv (gitignored)
├── .gitignore
├── README.md
├── main.py
├── pyproject.toml        # Single source of truth for deps
├── uv.lock               # Reproducible builds (commit this)
├── notebooks/
│   └── exploration.ipynb
├── src/
│   ├── agents/
│   ├── chains/
│   ├── data/
│   └── models/
└── tests/
    └── test_pipeline.py
```

---

## Quick Reference Card

| Need | Tool | Command |
|---|---|---|
| Install Python packages | `uv add <pkg>` | In project |
| Install CLI tools globally | `uv tool install <tool>` | Isolated env |
| Run scripts | `uv run python script.py` | In project venv |
| Run LLMs locally | `ollama run llama3.1:8b` | Uses AMD GPU |
| Chat with LLMs (web) | Open WebUI | `http://localhost:3000` |
| GPU monitoring | `amdgpu_top` or `rocm-smi` | Real-time |
| Docker management | `lazydocker` | TUI |
| Git management | `lazygit` | TUI |
| API testing | Thunder Client (VS Code) | Extension |
| Time tracking | Toggl Track | Browser |
| Note-taking | Obsidian | Desktop app |
| Project management | ClickUp or Linear | Browser |
| Password manager | Bitwarden | Desktop + browser |
| VPN | Mullvad | `mullvad connect` |
| System snapshots | Snapper | `snapper list` |

---

*Built for CachyOS (Arch Linux) · AMD GPU · KDE Plasma · 32GB RAM*
*Last updated: February 2026*
