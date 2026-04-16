# CachyOS Developer Workstation — Complete Setup Guide

**Hardware:** AMD Ryzen 5 5600 · AMD RX 6700 XT (RDNA2, gfx1030) · 32GB RAM · KDE Plasma  
**Profile:** Senior Python Backend & AI Engineer · Freelancer · Full-Stack when needed  
**OS:** CachyOS (Arch Linux) · Kernel 6.19 · ROCm 7.2 · uv 0.10.4 · Node v20 LTS  
**Last updated:** April 2026

> This guide merges both setup files into one authoritative reference. Every section lists what to install, why, and how — including post-install configuration and service enablement. Follow top to bottom for a clean machine; skip sections already done.

---

## Table of Contents

1. [System Foundation & Optimization](#1-system-foundation--optimization)
2. [AMD GPU Drivers & ROCm](#2-amd-gpu-drivers--rocm)
3. [Python Environment with uv](#3-python-environment-with-uv)
4. [AI/ML & LLM Stack](#4-aiml--llm-stack)
5. [Backend Frameworks & Tools](#5-backend-frameworks--tools)
6. [Databases](#6-databases)
7. [DevOps & Cloud Tools](#7-devops--cloud-tools)
8. [Docker & Kubernetes](#8-docker--kubernetes)
9. [Infrastructure as Code & CI/CD](#9-infrastructure-as-code--cicd)
10. [Data Engineering](#10-data-engineering)
11. [Frontend Development](#11-frontend-development)
12. [Code Editors & IDEs](#12-code-editors--ides)
13. [Terminal, Shell & CLI Tools](#13-terminal-shell--cli-tools)
14. [Git & Version Control](#14-git--version-control)
15. [Browsers](#15-browsers)
16. [Knowledge Management & Productivity](#16-knowledge-management--productivity)
17. [Project Management & Freelance](#17-project-management--freelance)
18. [Communication & Collaboration](#18-communication--collaboration)
19. [Security & Privacy](#19-security--privacy)
20. [System Maintenance & Monitoring](#20-system-maintenance--monitoring)
21. [Media, Office & Personal](#21-media-office--personal)
22. [Bulk Install Commands](#22-bulk-install-commands)
23. [~/.zshrc Configuration](#23-zshrc-configuration)
24. [AI/ML Project Quickstart](#24-aiml-project-quickstart)

---

## 1. System Foundation & Optimization

### 1.1 CachyOS Post-Install Settings

CachyOS ships `cachyos-settings` with sysctl tweaks, I/O scheduler rules, ZRAM config, and audio power management. `ananicy-cpp` auto-adjusts process priorities for desktop responsiveness.

```bash
sudo pacman -S cachyos-settings ananicy-cpp cachyos-ananicy-rules
sudo systemctl enable --now ananicy-cpp.service
```

### 1.2 Developer sysctl Tweaks

Create `/etc/sysctl.d/99-developer.conf`:

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
sudo sysctl --system   # Apply without reboot
```

### 1.3 ZRAM Configuration (32GB RAM)

CachyOS enables ZRAM by default. Tune `/etc/systemd/zram-generator.conf`:

```ini
[zram0]
zram-size = min(ram, 8192)
compression-algorithm = zstd
```

**Why:** Creates an 8GB compressed swap device in RAM using zstd. When RAM fills under heavy AI workloads (Ollama + Docker + VS Code + browser), cold pages compress in RAM (~37ns) instead of hitting SSD (~100µs). Effectively gives you ~36-40GB usable memory.

**Optional SSD swap fallback** for extremely heavy workloads (Btrfs):

```bash
sudo btrfs filesystem mkswapfile --size 8G /swap/swapfile
sudo swapon /swap/swapfile
echo '/swap/swapfile none swap defaults 0 0' | sudo tee -a /etc/fstab
```

### 1.4 Mirror Optimization

```bash
sudo pacman -S reflector cachyos-rate-mirrors
sudo reflector --country 'NP,IN,SG' --age 12 --protocol https --sort rate \
  --save /etc/pacman.d/mirrorlist
sudo cachyos-rate-mirrors
sudo systemctl enable --now reflector.timer
```

---

## 2. AMD GPU Drivers & ROCm

### 2.1 GPU Drivers (AMDGPU + Mesa + Vulkan)

CachyOS ships mesa from its own repo (includes VA-API and VDPAU built in). Install Vulkan and lib32 layers:

```bash
sudo pacman -S vulkan-radeon lib32-vulkan-radeon \
  vulkan-icd-loader lib32-vulkan-icd-loader lib32-mesa
```

**Verify:**

```bash
lspci -k | grep -A3 VGA     # Should show "Kernel driver in use: amdgpu"
vulkaninfo --summary         # Should list your AMD GPU
```

### 2.2 ROCm Installation

AMD's open-source GPU compute platform. `rocm-hip-sdk` pulls in HIP runtime, rocBLAS, MIOpen, and all core ROCm libraries needed for PyTorch and llama.cpp.

```bash
sudo pacman -S rocm-hip-sdk rocm-opencl-sdk
sudo usermod -aG render,video $USER
# Log out and back in, then verify:
rocminfo      # Lists your GPU agent
hipcc --version
rocm-smi
```

### 2.3 RDNA2 GPU Override (RX 6700 XT / RX 6000 series)

The RX 6700 XT (gfx1030/gfx1031) needs a compatibility override for ROCm. Add to `~/.zshrc`:

```bash
export HSA_OVERRIDE_GFX_VERSION=10.3.0   # RDNA2 (RX 6700/6800/6900 series)
# export HSA_OVERRIDE_GFX_VERSION=11.0.0  # RDNA3 (RX 7000 series)
```

**For Ollama service override** (required for GPU acceleration):

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="HSA_OVERRIDE_GFX_VERSION=10.3.0"
EOF
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

### 2.4 GPU Monitoring Tools

```bash
sudo pacman -S radeontop rocm-smi-lib
paru -S amdgpu_top   # Modern TUI with per-process GPU usage
```

| Tool | Command | Purpose |
|---|---|---|
| `radeontop` | `radeontop` | Real-time GPU utilization bars |
| `rocm-smi` | `rocm-smi` | Detailed stats: temp, power, VRAM |
| `amdgpu_top` | `amdgpu_top` | Modern TUI with per-process GPU usage |

---

## 3. Python Environment with uv

### 3.1 Why uv

On Arch/CachyOS, `pip install` globally throws `error: externally-managed-environment` (PEP 668). **uv solves this permanently:**

- Always operates inside virtual environments
- 10-100× faster than pip (Rust implementation + global cache)
- Replaces pyenv (version management), pipx (tool isolation), pip-tools (lockfiles)
- Generates `uv.lock` for reproducible builds

```bash
# Recommended — enables self-update:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or from pacman (disables uv self update):
sudo pacman -S uv
```

Add to `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"
```

### 3.2 Python Version Management

```bash
uv python install 3.12 3.13    # Install versions
uv python list                  # List all available/installed
uv python pin 3.12              # Pin project (creates .python-version)
uv python find                  # Show active Python path
```

### 3.3 Project Workflow

```bash
uv init my-project --python 3.12   # Create project
cd my-project

uv add django fastapi uvicorn[standard]   # Add dependencies
uv add --dev pytest ruff ipykernel        # Dev dependencies
uv run python manage.py runserver         # Run in project venv
uv run pytest                             # Run tests
uv sync                                   # Sync from lockfile (CI/teammates)
uv export --format requirements-txt > requirements.txt   # Docker/legacy
uv tree                                   # Dependency tree
```

### 3.4 Global CLI Tools (replaces pipx)

```bash
uv tool install ruff         # Linter + formatter (replaces black, flake8, isort)
uv tool install jupyterlab   # Jupyter notebook server
uv tool install httpie       # Modern HTTP client
uv tool install pre-commit   # Git hook manager
uv tool install mypy         # Static type checker
uv tool install ipython      # Enhanced Python REPL
uv tool install ansible      # Configuration management

uv tool list                 # Show installed tools
uv tool upgrade --all        # Upgrade everything
```

**Run tools ephemerally without installing:**

```bash
uvx ruff check .      # Run ruff once
uvx black --check .   # Run black once
```

### 3.5 Ruff — All-in-One Linter & Formatter

Replaces black, flake8, isort, pyflakes, and more — 30-100× faster.

```bash
uv tool install ruff
```

`pyproject.toml`:

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
ruff check . --fix   # Lint and auto-fix
ruff format .        # Format (Black-compatible)
```

### 3.6 Pre-commit Hooks

`.pre-commit-config.yaml`:

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
pre-commit install            # Install hooks
pre-commit run --all-files    # Run on all files now
```

### 3.7 Jupyter Notebook/Lab

```bash
# Option A — Within project (recommended):
uv add --dev ipykernel
uv run --with jupyter jupyter lab

# Option B — Global tool:
uv tool install jupyterlab
uv run ipython kernel install --user --name=my-project
jupyter lab
```

---

## 4. AI/ML & LLM Stack

### 4.1 PyTorch with ROCm ⭐

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

### 4.2 TensorFlow with ROCm

Docker is the most reliable method on Arch:

```bash
docker run -it --network=host --device=/dev/kfd --device=/dev/dri \
  --ipc=host --shm-size 16G --group-add video \
  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
  rocm/tensorflow:latest
```

### 4.3 Ollama — Local LLM Inference ⭐

CachyOS ships `ollama-rocm` — pre-built with AMD GPU acceleration.

```bash
sudo pacman -S ollama-rocm
sudo usermod -aG render,video $USER

# Create GPU override for RX 6700 XT:
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="HSA_OVERRIDE_GFX_VERSION=10.3.0"
EOF
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

### 4.4 Open WebUI — Local Chat Interface

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

Access: http://localhost:3000 — create admin account on first visit.

### 4.5 llama.cpp with ROCm/HIP ⭐

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

### 4.6 vLLM — Production LLM Serving

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

### 4.7 LangChain & LlamaIndex

```bash
# LangChain — LLM application framework:
uv add langchain langchain-core langchain-community langgraph \
       langchain-openai langchain-ollama langchain-huggingface langchain-chroma

# LlamaIndex — RAG data framework:
uv add llama-index \
       llama-index-llms-ollama llama-index-embeddings-huggingface \
       llama-index-vector-stores-chroma
```

### 4.8 Hugging Face Ecosystem

```bash
uv add transformers datasets accelerate tokenizers sentence-transformers huggingface-hub
```

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")   # Auto-uses ROCm GPU
embeddings = model.encode(["Hello world", "AI on Arch Linux"])
```

### 4.9 Vector Databases

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
paru -S pgvector
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

---

## 5. Backend Frameworks & Tools

### 5.1 Django + Django REST Framework

```bash
uv add django djangorestframework django-cors-headers django-filter \
       django-celery-beat django-celery-results whitenoise
uv add --dev django-debug-toolbar factory-boy

uv run django-admin startproject myproject && cd myproject
uv run python manage.py startapp api
```

### 5.2 FastAPI + Uvicorn + Gunicorn

```bash
uv add fastapi "uvicorn[standard]" gunicorn python-multipart
uv add --dev httpx   # For testing

# Dev:  uv run uvicorn main:app --reload
# Prod: uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5.3 Flask

```bash
uv add flask flask-sqlalchemy flask-migrate flask-cors
```

### 5.4 Celery + Redis

```bash
uv add celery redis
```

```python
# celery_app.py
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def process_document(doc_id):
    pass

# Run: uv run celery -A celery_app worker --loglevel=info
# Beat: uv run celery -A celery_app beat -l info
```

### 5.5 WebSockets & Async

```bash
uv add channels channels-redis websockets   # WebSockets
uv add aiohttp httpx asyncpg aiofiles       # Async HTTP/DB/IO
```

| Library | Purpose |
|---|---|
| `httpx` | Modern async/sync HTTP client with HTTP/2 |
| `aiohttp` | Async HTTP client/server |
| `asyncpg` | Fast async PostgreSQL driver |
| `aiofiles` | Async file I/O |

---

## 6. Databases

### 6.1 PostgreSQL ⭐

```bash
sudo pacman -S postgresql
sudo -iu postgres initdb --locale=C.UTF-8 -E UTF8 -D /var/lib/postgres/data --data-checksums
sudo systemctl enable --now postgresql

# Create dev user and database:
sudo -iu postgres psql -c "CREATE USER devuser WITH ENCRYPTED PASSWORD 'devpass' CREATEDB;"
sudo -iu postgres psql -c "CREATE DATABASE devdb OWNER devuser;"

# Enable pgvector:
paru -S pgvector
sudo -iu postgres psql devdb -c "CREATE EXTENSION vector;"
```

### 6.2 MariaDB (MySQL-compatible)

```bash
sudo pacman -S mariadb
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo systemctl enable --now mariadb
sudo mariadb-secure-installation
```

### 6.3 MongoDB

```bash
paru -S mongodb-bin   # Pre-built binary (building from source takes hours)
sudo systemctl enable --now mongodb
mongosh   # Verify
```

> **CachyOS note:** If MongoDB fails to start with `Permission denied`, the data directory is owned by root. Create a systemd override to auto-fix on every start:
> ```bash
> sudo mkdir -p /etc/systemd/system/mongodb.service.d/
> sudo tee /etc/systemd/system/mongodb.service.d/fix-permissions.conf << 'EOF'
> [Service]
> ExecStartPre=+/bin/chown -R mongodb:mongodb /var/lib/mongodb /var/log/mongodb
> EOF
> sudo systemctl daemon-reload && sudo systemctl restart mongodb
> ```
> The `+` prefix runs the command as root regardless of the service user.

### 6.4 Redis (Valkey)

CachyOS/Arch ships `valkey` (the Redis open-source fork) as the `redis` package:

```bash
sudo pacman -S redis   # Installs valkey, creates redis.service alias
sudo systemctl enable --now valkey.service
valkey-cli ping   # → PONG
```

### 6.5 Elasticsearch (Docker)

```bash
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.0
```

### 6.6 SQLite

```bash
sudo pacman -S sqlite   # CLI tool (Python's sqlite3 module is always available)
```

### 6.7 Database GUI Tools

**DBeaver ⭐** (universal — Postgres, MySQL, SQLite, MongoDB, 80+ databases):

```bash
sudo pacman -S dbeaver
```

**pgAdmin 4** (Docker):

```bash
docker run -d --name pgadmin -p 5050:80 \
  -e "PGADMIN_DEFAULT_EMAIL=admin@local.dev" \
  -e "PGADMIN_DEFAULT_PASSWORD=admin" \
  dpage/pgadmin4
```

**Redis Insight**:

```bash
docker run -d --name redis-insight -p 5540:5540 redis/redisinsight:latest
```

**MongoDB Compass** (official GUI for MongoDB):

```bash
# CachyOS repo version requires nodejs-25 which conflicts with nodejs-lts-iron.
# Use the pre-built binary from AUR instead:
paru -S mongodb-compass-bin
```

---

## 7. DevOps & Cloud Tools

### 7.1 AWS CLI v2

```bash
sudo pacman -S aws-cli-v2
aws configure   # Enter: Access Key, Secret Key, region, output format

uv tool install aws-sam-cli   # Serverless Application Model
```

### 7.2 Azure CLI

```bash
sudo pacman -S azure-cli
az login   # Opens browser for interactive auth
```

### 7.3 Google Cloud SDK

```bash
paru -S google-cloud-cli
gcloud init   # Authenticate and set default project/region
```

### 7.4 Nginx

```bash
sudo pacman -S nginx
sudo systemctl enable --now nginx
# Config:    /etc/nginx/nginx.conf
# Test:      sudo nginx -t
# Reload:    sudo nginx -s reload
```

---

## 8. Docker & Kubernetes

### 8.1 Docker + Docker Compose

```bash
sudo pacman -S docker docker-compose docker-buildx
sudo systemctl enable --now docker.service
sudo usermod -aG docker $USER
newgrp docker   # Apply immediately (or reboot)
docker run hello-world   # Verify
```

**Enable native overlay diff** (performance fix for Arch):

```bash
echo "options overlay metacopy=off redirect_dir=off" | \
  sudo tee /etc/modprobe.d/disable-overlay-redirect-dir.conf
sudo modprobe -r overlay && sudo modprobe overlay
sudo systemctl restart docker.service
docker info | grep "Native Overlay"   # Should show: true
```

**Socket activation** (Docker starts only when first used — faster boot):

```bash
sudo systemctl disable docker.service
sudo systemctl enable docker.socket
```

### 8.2 Docker Compose — Local Dev Stack

```yaml
# docker-compose.yml — Django + PostgreSQL + Redis + Celery
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

  celery_beat:
    build: .
    command: celery -A myproject beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes: [".:/app"]
    env_file: [.env]
    depends_on: [db, redis]

volumes:
  postgres_data:
```

### 8.3 Kubernetes Tools

```bash
sudo pacman -S kubectl minikube helm k9s

minikube start --driver=docker --memory=4096 --cpus=2

# k3s (lightweight, production-grade):
curl -sfL https://get.k3s.io | sh -
```

| Tool | Purpose |
|---|---|
| `kubectl` | CLI for Kubernetes cluster management |
| `minikube` | Local single-node K8s cluster |
| `k3s` | Lightweight production K8s |
| `helm` | Kubernetes package manager (charts) |
| `k9s` | Terminal UI for K8s cluster navigation |

### 8.4 Multi-Stage Dockerfile Template

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN useradd -m appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 8.5 Container Registry Auth

```bash
docker login   # Docker Hub

# AWS ECR:
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com

# GCP Artifact Registry:
gcloud auth configure-docker us-central1-docker.pkg.dev

# GitHub Container Registry:
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

---

## 9. Infrastructure as Code & CI/CD

### 9.1 Terraform

```bash
sudo pacman -S terraform
# terraform init → terraform plan → terraform apply → terraform destroy
```

### 9.2 OpenTofu (Open-source Terraform fork)

```bash
sudo pacman -S opentofu
tofu -v
```

### 9.3 Ansible

```bash
uv tool install ansible
ansible --version
```

### 9.4 Pulumi (IaC with real programming languages)

```bash
paru -S pulumi-bin
pulumi new python   # Create Python IaC project
```

### 9.5 GitHub Actions Local Runner — act

```bash
sudo pacman -S act
cd /your/repo && act   # Runs .github/workflows/*.yml locally
```

### 9.6 GitLab CI Runner

```bash
sudo pacman -S gitlab-runner
sudo gitlab-runner register   # Follow prompts with your GitLab token
```

### 9.7 Sample GitHub Actions (Python + uv)

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

## 10. Data Engineering

### 10.1 Core Libraries

```bash
uv add pandas numpy scipy matplotlib seaborn plotly kaleido
uv add scikit-learn polars pyarrow
```

| Library | Purpose |
|---|---|
| **Pandas** | DataFrames for tabular data |
| **Polars** | Blazing-fast Rust-based DataFrames (10-100× faster) |
| **NumPy** | Numerical computing |
| **SciPy** | Scientific computing |
| **Matplotlib/Seaborn** | Static plotting |
| **Plotly** | Interactive charts |
| **scikit-learn** | ML preprocessing, models, pipelines |
| **PyArrow** | Apache Arrow — columnar data & Parquet I/O |

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

### 10.3 Workflow Orchestration

```bash
uv add prefect            # Modern Python-native orchestration
uv add apache-airflow     # Industry standard (heavier)
uv add "dask[complete]"   # Parallel computing — scales Pandas to larger-than-memory
```

---

## 11. Frontend Development

### 11.1 Node.js via NVM

```bash
# Install NVM (if not via pacman):
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# Or via pacman:
sudo pacman -S nvm
```

Add to `~/.zshrc`:

```bash
export NVM_DIR="$HOME/.nvm"
[[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"
```

```bash
nvm install --lts && nvm use --lts
node -v && npm -v
```

### 11.2 Package Managers

```bash
corepack enable
corepack prepare pnpm@latest --activate    # pnpm (recommended — fastest, disk-efficient)
corepack prepare yarn@stable --activate    # Yarn 4+
```

### 11.3 React + Vite

```bash
pnpm create vite@latest my-react-app -- --template react-ts
cd my-react-app && pnpm install && pnpm dev
```

### 11.4 Next.js

```bash
pnpm create next-app@latest my-next-app
cd my-next-app && pnpm dev
```

### 11.5 TypeScript

```bash
pnpm add -D typescript
npx tsc --init   # Creates tsconfig.json
```

### 11.6 Tailwind CSS

```bash
pnpm add -D tailwindcss @tailwindcss/postcss postcss
npx tailwindcss init
```

---

## 12. Code Editors & IDEs

### 12.1 VS Code ⭐

```bash
paru -S visual-studio-code-bin   # Microsoft build (full marketplace, Copilot, Remote Dev)
sudo pacman -S code               # Open-source build (Open VSX marketplace)
```

**Install all essential extensions:**

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

**`settings.json`:**

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
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

### 12.2 Cursor (AI-First Editor)

```bash
paru -S cursor-bin
```

VS Code fork with deep Claude/GPT-4 integration for code generation, editing, and chat.

### 12.3 Zed (Modern GPU-Accelerated Editor)

```bash
paru -S zed
```

Built in Rust, extremely fast, built-in AI assistant, multiplayer editing.

### 12.4 Neovim + LazyVim

```bash
sudo pacman -S neovim
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
nvim   # Plugins auto-install on first launch
# Type :LazyExtras and enable lang.python
```

### 12.5 PyCharm

```bash
sudo pacman -S pycharm-community-edition   # Free — Python + Django
paru -S pycharm-professional               # Paid — FastAPI, Docker, DB tools, Remote Dev
```

### 12.6 VS Codium (Telemetry-Free)

```bash
paru -S vscodium-bin
```

---

## 13. Terminal, Shell & CLI Tools

### 13.1 Zsh + Oh My Zsh

```bash
sudo pacman -S zsh
chsh -s $(which zsh)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

git clone https://github.com/zsh-users/zsh-autosuggestions \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

`~/.zshrc`:

```bash
plugins=(git sudo fzf history zsh-autosuggestions zsh-syntax-highlighting docker kubectl)
```

### 13.2 Terminal Emulators

| Terminal | Install | Highlights |
|---|---|---|
| **Kitty** ⭐ | `sudo pacman -S kitty` | GPU-accelerated, splits, tabs, ligatures, image display |
| **Alacritty** | `sudo pacman -S alacritty` | Fastest, minimalist (pair with tmux) |
| **WezTerm** | `sudo pacman -S wezterm` | GPU-accel, Lua config, built-in multiplexer |
| **Ghostty** | `paru -S ghostty` | Zig-based, extremely fast, native GPU rendering |

### 13.3 Starship Prompt

```bash
sudo pacman -S starship
# Add to ~/.zshrc: eval "$(starship init zsh)"
```

Customize via `~/.config/starship.toml`. Shows git branch, Python version, Docker context, K8s namespace.

### 13.4 Terminal Multiplexers

```bash
sudo pacman -S tmux     # Classic — Ctrl-b c (new window), Ctrl-b % (split vertical)
sudo pacman -S zellij   # Modern Rust alternative — beginner-friendly bottom help bar
```

### 13.5 Modern CLI Replacements

```bash
sudo pacman -S fzf ripgrep fd bat eza zoxide procs dust duf tokei hyperfine lazygit
```

| Tool | Replaces | Purpose |
|---|---|---|
| `fzf` | — | Fuzzy finder for files, history, everything |
| `ripgrep` (`rg`) | `grep` | 10× faster recursive search |
| `fd` | `find` | Fast, intuitive file finder |
| `bat` | `cat` | Syntax highlighting, Git integration |
| `eza` | `ls` | Icons, Git status, tree view |
| `zoxide` | `cd` | Smart directory jumping (learns habits) |
| `procs` | `ps` | Modern process viewer |
| `dust` | `du` | Visual proportional disk usage |
| `duf` | `df` | Colorful disk free output |
| `tokei` | `cloc` | Fast code line counter |
| `hyperfine` | `time` | Command benchmarking with statistics |
| `lazygit` | — | Full Git TUI — staging, commits, branches, rebasing |

**Shell aliases** (add to `~/.zshrc`):

```bash
eval "$(zoxide init zsh)"
source /usr/share/fzf/key-bindings.zsh
source /usr/share/fzf/completion.zsh
alias ls='eza --icons --group-directories-first'
alias ll='eza -la --icons --group-directories-first --git'
alias lt='eza --tree --icons --level=2'
alias cat='bat --style=plain --paging=never'
alias grep='rg'
alias find='fd'
alias du='dust'
alias df='duf'
alias ps='procs'
alias lg='lazygit'
```

### 13.6 lazydocker

```bash
paru -S lazydocker   # TUI for Docker containers, images, volumes
alias ld='lazydocker'
```

---

## 14. Git & Version Control

### 14.1 Git Configuration

```bash
sudo pacman -S git

git config --global user.name "Your Name"
git config --global user.email "you@email.com"

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

### 14.2 Global .gitignore

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

### 14.3 GitHub CLI

```bash
sudo pacman -S github-cli
gh auth login       # Interactive browser auth
gh auth status      # Verify

gh repo create my-project --public --clone
gh pr create --title "feat: add search" --body "Adds semantic search"
gh pr list
gh issue create --title "Bug: API timeout"
gh release create v1.0.0
```

### 14.4 Conventional Commits

Format: `type(scope): description`

| Type | Use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change, no feature/fix |
| `test` | Adding tests |
| `chore` | Build/tools/dependencies |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

Branch naming: `feature/PROJ-123-add-search`, `bugfix/fix-login-crash`, `hotfix/patch-security`

---

## 15. Browsers

### 15.1 Browser Strategy

| Browser | Install | Use Case |
|---|---|---|
| **Firefox Dev Edition** ⭐ | `sudo pacman -S firefox-developer-edition` | Primary dev — CSS Grid inspector, network analysis |
| **Brave** | `paru -S brave-bin` | Secondary dev testing (Chromium), casual browsing |
| **LibreWolf** ⭐ | `paru -S librewolf-bin` | Personal browsing, banking, private accounts |
| **Mullvad Browser** | `paru -S mullvad-browser-bin` | Maximum anonymity |
| **Ungoogled Chromium** | `paru -S ungoogled-chromium-bin` | Chrome compatibility testing |

### 15.2 Essential Browser Extensions

**Development:**

| Extension | Purpose |
|---|---|
| uBlock Origin | Best-in-class ad/tracker blocker |
| React DevTools | Inspect React component tree and state |
| JSON Viewer | Pretty-prints JSON responses |
| Wappalyzer | Identify tech stack on any website |
| Refined GitHub | Enhanced GitHub UI |
| ColorZilla | Color picker and eyedropper |

**Privacy/Personal:**

| Extension | Purpose |
|---|---|
| Bitwarden | Password manager |
| Dark Reader | Dark mode for all sites |
| Privacy Badger | EFF's adaptive tracker blocker |
| ClearURLs | Remove tracking parameters |
| SponsorBlock | Skip YouTube sponsors |

---

## 16. Knowledge Management & Productivity

### 16.1 Notes & Knowledge Bases

| Tool | Install | Best For |
|---|---|---|
| **Obsidian** ⭐ | `sudo pacman -S obsidian` | Personal KB, local Markdown, Git-friendly, works offline |
| **Notion** | `paru -S notion-app-enhanced` | Client wikis, team databases, shared project docs |
| **Logseq** | `paru -S logseq-desktop-bin` | Outliner-style daily journaling, block-level referencing |
| **AnyType** | `paru -S anytype-bin` | Open-source local-first Notion alternative |

**Recommended:** Obsidian as primary. Notion for client-facing work.

**Obsidian recommended plugins:** Templater, Dataview, Calendar, Kanban, Git, Advanced Tables, Excalidraw

### 16.2 Task Management

| Tool | Use |
|---|---|
| **Todoist** | `paru -S todoist-appimage` — Personal task manager |
| **Linear** | https://linear.app — Developer-focused, GitHub integration |
| **ClickUp** | https://clickup.com — All-in-one project management |
| **Plane** | Self-hosted Linear alternative (Docker) |

### 16.3 Screenshots & Screen Recording

```bash
sudo pacman -S flameshot spectacle obs-studio
# flameshot gui    — annotation tools, arrows, blur
# spectacle        — KDE default (PrintScreen key)
# obs-studio       — recording and streaming (Wayland via PipeWire)
```

### 16.4 Time Tracking (Essential for Freelancing)

- **Toggl Track** ⭐ — https://track.toggl.com/ (free tier, project/client categorization)
- **Clockify** — https://app.clockify.me/ (unlimited users free, timesheets, invoicing)
- **WakaTime** — VS Code extension `WakaTime.vscode-wakatime` (automatic coding time tracking)

### 16.5 Clipboard Manager

```bash
sudo pacman -S copyq   # Feature-rich clipboard manager
# Klipper is pre-installed with KDE Plasma (system tray)
```

---

## 17. Project Management & Freelance

### 17.1 Invoicing & Finance

- **Invoice Ninja** — `docker run -d -p 8080:80 invoiceninja/invoiceninja` (self-hosted)
- **Wave Accounting** — https://www.waveapps.com/ (free cloud accounting)
- **AND.CO** — https://www.and.co/ (free proposals, contracts, invoicing — by Fiverr)

### 17.2 Upwork App

```bash
paru -S upwork   # Required for hourly contracts (screenshots + activity tracking)
```

### 17.3 PDF Viewer

```bash
sudo pacman -S okular   # KDE PDF viewer (pre-installed on CachyOS KDE)
```

### 17.4 Calendar

```bash
sudo pacman -S korganizer   # Standalone KDE calendar
# Or use Thunderbird's built-in calendar
```

---

## 18. Communication & Collaboration

### 18.1 Communication Apps

```bash
sudo pacman -S discord telegram-desktop thunderbird
paru -S slack-desktop zoom
```

**Wayland screen sharing fix for Zoom:**

```bash
sudo pacman -S xdg-desktop-portal xdg-desktop-portal-kde pipewire-v4l2
```

### 18.2 Email — Thunderbird

```bash
sudo pacman -S thunderbird
```

Built-in calendar, contacts, and RSS reader. Supports Gmail, Outlook, and any IMAP/SMTP.

### 18.3 Phone Integration — KDE Connect

```bash
sudo pacman -S kdeconnect
sudo ufw allow 1714:1764/udp
sudo ufw allow 1714:1764/tcp
```

Syncs clipboard, notifications, files, and SMS between phone and desktop.

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
sudo ufw --force enable
sudo systemctl enable --now ufw.service
```

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

### 19.3 SSH Hardening

```bash
ssh-keygen -t ed25519 -a 100 -C "you@email.com"
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host
```

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
sudo systemctl restart sshd
```

### 19.4 Password Managers

```bash
sudo pacman -S bitwarden keepassxc
```

| Tool | Use Case |
|---|---|
| **Bitwarden** | Cloud-synced across all devices, browser extension, team sharing |
| **KeePassXC** | Local/offline, sync `.kdbx` file via Syncthing, maximum control |

### 19.5 Encrypted DNS

```bash
sudo pacman -S dnscrypt-proxy
```

Edit `/etc/dnscrypt-proxy/dnscrypt-proxy.toml`:

```toml
server_names = ['cloudflare', 'quad9-dnscrypt-ip4-nofilter-pri']
listen_addresses = ['127.0.0.1:5300', '[::1]:5300']
require_dnssec = true
require_nolog = true
```

> **Note on CachyOS:** `dnsmasq` occupies port 53 by default. Configure dnscrypt-proxy on port 5300 and point dnsmasq to forward to it.

```bash
sudo systemctl enable --now dnscrypt-proxy.service
```

### 19.6 VPN

```bash
# Mullvad VPN (no email, no account, anonymous payment):
paru -S mullvad-vpn-bin
sudo systemctl enable --now mullvad-daemon.service
mullvad account login <ACCOUNT_NUMBER>
mullvad connect

# ProtonVPN (free tier available):
sudo pacman -S proton-vpn-gtk-app
```

### 19.7 AppArmor

```bash
sudo pacman -S apparmor
sudo pacman -S apparmor.d   # Community profiles (complain mode — safe, logs violations)
```

Add kernel parameter to `/etc/default/grub`:

```
GRUB_CMDLINE_LINUX_DEFAULT="... lsm=landlock,lockdown,yama,integrity,apparmor,bpf"
```

```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
sudo systemctl enable apparmor.service
# Reboot required. Verify: sudo aa-status
```

> **CachyOS note:** After reboot, AppArmor loads profiles in complain mode (logs but doesn't block). Switch individual profiles to enforce mode with `sudo aa-enforce /etc/apparmor.d/<profile>`.

### 19.8 Disk Encryption (LUKS)

Must be configured at install time. CachyOS installer has a LUKS checkbox.

```bash
# Verify:  lsblk -f   (look for crypto_LUKS)
# Backup:  sudo cryptsetup luksHeaderBackup /dev/sdXn --header-backup-file /safe/header.img
```

### 19.9 File Sync — Syncthing

```bash
sudo pacman -S syncthing
systemctl --user enable --now syncthing.service
# Or:
sudo systemctl enable --now syncthing@$USER.service
# Web UI: http://127.0.0.1:8384
```

---

## 20. System Maintenance & Monitoring

### 20.1 Btrfs Snapshots — Snapper + grub-btrfs

CachyOS defaults to Btrfs. `snap-pac` auto-creates snapshots on every pacman transaction. `grub-btrfs` adds a recovery submenu to GRUB so you can boot into any snapshot.

```bash
sudo pacman -S snapper snap-pac btrfs-assistant grub-btrfs
sudo snapper -c root create-config /
sudo systemctl enable --now snapper-timeline.timer snapper-cleanup.timer
snapper list   # View snapshots
# Restore: boot from GRUB "CachyOS Snapshots (Recovery)" submenu or snapper rollback
```

**Limit snapshot display in GRUB** — edit `/etc/default/grub-btrfs/config`:

```bash
GRUB_BTRFS_LIMIT="10"
GRUB_BTRFS_SUBMENUNAME="CachyOS Snapshots (Recovery)"
GRUB_BTRFS_IGNORE_PREFIX_PATH=("var/lib/docker" "@var/lib/docker" "var/lib/containers")
```

**Auto-update GRUB after kernel upgrades** — create `/etc/pacman.d/hooks/95-grub-btrfs-update.hook`:

```ini
[Trigger]
Operation = Upgrade
Operation = Install
Operation = Remove
Type = Package
Target = linux-cachyos
Target = linux-cachyos-lts
Target = grub
Target = grub-btrfs
Target = snapper

[Action]
Description = Updating GRUB config after kernel/grub/snapshot change...
When = PostTransaction
Exec = /usr/bin/grub-mkconfig -o /boot/grub/grub.cfg
Depends = grub
Depends = grub-btrfs
```

> **Secure Boot note:** grub-btrfs snapshot entries appear as a single submenu in GRUB — they do NOT break Secure Boot. The GRUB EFI binary is signed by a custom DB key; snapshot kernels boot through the same GRUB loader without requiring individual signing (lockdown LSM stays in `[none]` mode when no shim is installed).

### 20.2 System Monitoring

```bash
sudo pacman -S btop nvtop mission-center ncdu
```

| Tool | Purpose |
|---|---|
| `btop` | Full system TUI monitor (CPU, RAM, disk, network) |
| `nvtop` | GPU process monitor (supports AMD despite the name) |
| `mission-center` | GTK4 GUI system monitor (like Windows Task Manager) |
| `ncdu` | Interactive disk usage browser |
| `dust` | Visual proportional disk usage (already in CLI tools) |
| `amdgpu_top` | Modern TUI with per-process GPU usage |

### 20.3 Package Cache Cleanup

```bash
sudo pacman -S pacman-contrib
sudo paccache -r             # Keep last 3 versions
sudo paccache -ruk0          # Remove all uninstalled package cache
sudo systemctl enable --now paccache.timer   # Weekly auto-cleanup
```

### 20.4 Mirror Optimization

```bash
sudo pacman -S reflector
sudo reflector --country 'NP,IN,SG' --age 12 --protocol https --sort rate \
  --save /etc/pacman.d/mirrorlist
sudo pacman -S cachyos-rate-mirrors && sudo cachyos-rate-mirrors
sudo systemctl enable --now reflector.timer
```

### 20.5 Update Strategy

Full auto-updates are risky on Arch. CachyOS provides `cachy-update` for interactive reviews:

```bash
# Best practice: review updates → verify snapper has recent snapshot → apply → reboot after kernel updates
paru -Syu   # or use the cachy-update systray notifier
```

---

## 21. Media, Office & Personal

### 21.1 Media Players

```bash
sudo pacman -S vlc mpv
```

`~/.config/mpv/mpv.conf`:

```ini
hwdec=auto
vo=gpu-next
profile=gpu-hq
```

### 21.2 Image Editing

```bash
sudo pacman -S gimp inkscape
```

### 21.3 Office Suite

```bash
sudo pacman -S libreoffice-fresh      # Latest features
paru -S onlyoffice-bin                 # Better MS Office compatibility
```

### 21.4 Music

```bash
yay -S spotify                  # Streaming
sudo pacman -S strawberry       # Local music (FLAC, MP3, gapless playback)
```

### 21.5 File Manager Enhancements

```bash
sudo pacman -S dolphin kdegraphics-thumbnailers ffmpegthumbs
# Thumbnail packages add image/video previews in Dolphin
```

### 21.6 Archive Manager

```bash
sudo pacman -S ark p7zip unrar
```

---

## 22. Bulk Install Commands

Run these on a fresh machine to install everything in one pass:

```bash
# === 1. SYSTEM & GPU ===
sudo pacman -S --noconfirm cachyos-settings ananicy-cpp cachyos-ananicy-rules \
  vulkan-radeon lib32-vulkan-radeon vulkan-icd-loader lib32-vulkan-icd-loader lib32-mesa \
  rocm-hip-sdk rocm-opencl-sdk radeontop rocm-smi-lib

# === 2. DATABASES ===
sudo pacman -S --noconfirm postgresql mariadb redis sqlite dbeaver

# === 3. DEVOPS & CLOUD ===
sudo pacman -S --noconfirm docker docker-compose docker-buildx \
  kubectl minikube helm k9s \
  aws-cli-v2 azure-cli terraform opentofu nginx act gitlab-runner

# === 4. TERMINAL & SHELL TOOLS ===
sudo pacman -S --noconfirm neovim zsh kitty alacritty wezterm starship tmux zellij \
  fzf ripgrep fd bat eza zoxide procs dust duf tokei hyperfine lazygit \
  git github-cli nvm

# === 5. EDITORS ===
sudo pacman -S --noconfirm pycharm-community-edition

# === 6. PRODUCTIVITY & SECURITY ===
sudo pacman -S --noconfirm bitwarden keepassxc syncthing copyq okular korganizer \
  thunderbird flameshot spectacle kdeconnect \
  ufw fail2ban dnscrypt-proxy apparmor apparmor.d \
  snapper snap-pac btrfs-assistant grub-btrfs pacman-contrib reflector

# === 7. APPS & MEDIA ===
sudo pacman -S --noconfirm firefox-developer-edition obsidian \
  discord telegram-desktop vlc mpv \
  gimp inkscape obs-studio libreoffice-fresh strawberry \
  btop nvtop mission-center ncdu \
  ark p7zip unrar dolphin kdegraphics-thumbnailers ffmpegthumbs sqlite

# === 8. AUR PACKAGES ===
paru -S --noconfirm visual-studio-code-bin cursor-bin zed vscodium-bin \
  brave-bin librewolf-bin mullvad-browser-bin ungoogled-chromium-bin \
  notion-app-enhanced logseq-desktop-bin anytype-bin \
  zoom slack-desktop spotify upwork \
  mullvad-vpn-bin proton-vpn-gtk-app \
  lazydocker onlyoffice-bin \
  ghostty amdgpu_top todoist-appimage \
  google-cloud-cli mongodb-bin mongodb-compass-bin pgvector

# === 9. POST-INSTALL ESSENTIALS ===
# GPU & Docker groups
sudo usermod -aG render,video,docker $USER

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Global Python CLI tools (uv tool install takes ONE package at a time)
uv tool install ruff
uv tool install jupyterlab
uv tool install httpie
uv tool install pre-commit
uv tool install mypy
uv tool install ipython
uv tool install ansible

# Initialize databases
sudo -iu postgres initdb --locale=C.UTF-8 -E UTF8 -D /var/lib/postgres/data --data-checksums
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql

# Enable all services
sudo systemctl enable --now \
  ananicy-cpp docker postgresql mariadb valkey mongodb nginx \
  ollama fail2ban dnscrypt-proxy apparmor syncthing@$USER \
  mullvad-daemon ufw paccache.timer reflector.timer \
  snapper-timeline.timer snapper-cleanup.timer

# Ollama RDNA2 override (RX 6700 XT / RX 6000 series)
sudo mkdir -p /etc/systemd/system/ollama.service.d/
echo -e '[Service]\nEnvironment="HSA_OVERRIDE_GFX_VERSION=10.3.0"' | \
  sudo tee /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama

# Default shell
chsh -s $(which zsh)
```

---

## 23. ~/.zshrc Configuration

Full recommended `~/.zshrc` for this setup:

```bash
# =========================================================
#  Oh My Zsh
# =========================================================
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"   # or "robbyrussell" if not using p10k

plugins=(git sudo fzf history zsh-autosuggestions zsh-syntax-highlighting docker kubectl)
source "$ZSH/oh-my-zsh.sh"

# =========================================================
#  PATH
# =========================================================
export PATH="$HOME/.local/bin:$HOME/.focus/scripts:$PATH"

# =========================================================
#  uv — Python package manager
# =========================================================
eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"

# =========================================================
#  Node.js — NVM (lazy-loaded for fast startup)
# =========================================================
export NVM_DIR="$HOME/.nvm"
nvm() { unset -f nvm; [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"; nvm "$@"; }
node() { unset -f node; [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"; node "$@"; }

# pnpm
export PNPM_HOME="$HOME/.local/share/pnpm"
[[ ":$PATH:" != *":$PNPM_HOME:"* ]] && export PATH="$PNPM_HOME:$PATH"

# =========================================================
#  Prompt — Starship (alternative to p10k)
# =========================================================
# eval "$(starship init zsh)"   # Uncomment to use Starship

# =========================================================
#  ROCm / AMD GPU — RDNA2 (RX 6700 XT)
# =========================================================
export HSA_OVERRIDE_GFX_VERSION=10.3.0
# export HSA_OVERRIDE_GFX_VERSION=11.0.0   # RDNA3 (RX 7000 series)

# =========================================================
#  Ollama
# =========================================================
export OLLAMA_HOST="0.0.0.0:11434"

# =========================================================
#  zoxide — smart cd
# =========================================================
eval "$(zoxide init zsh)"

# =========================================================
#  fzf
# =========================================================
source /usr/share/fzf/key-bindings.zsh
source /usr/share/fzf/completion.zsh

# =========================================================
#  File listing
# =========================================================
alias ls='eza --icons --group-directories-first'
alias l='eza -lbF --icons --git --group-directories-first'
alias ll='eza -lahig --time-style=long-iso --color-scale --icons --group-directories-first'
alias lt='eza --tree --icons --level=2'
alias cat='bat --style=plain --paging=never'

# =========================================================
#  Modern CLI replacements
# =========================================================
alias grep='rg'
alias find='fd'
alias du='dust'
alias df='duf'
alias ps='procs'

# =========================================================
#  TUI tools
# =========================================================
alias lg='lazygit'
alias ld='lazydocker'
alias gpumon='amdgpu_top'
alias top='btop'

# =========================================================
#  Docker / Kubernetes
# =========================================================
alias d='docker'
alias dco='docker compose'
alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dclogs='docker compose logs -f'
alias dps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
alias k='kubectl'
alias kgp='kubectl get pods'
alias kl='kubectl logs'

# =========================================================
#  Python / uv
# =========================================================
alias py='python3'
alias pyt='uv run pytest'
alias lint='uv run ruff check . --fix && uv run ruff format .'

# Django
alias djrun='python manage.py runserver'
alias djmm='python manage.py makemigrations'
alias djm='python manage.py migrate'

# =========================================================
#  Git
# =========================================================
alias gs='git status -sb'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias glog='git log --oneline --graph --decorate --all'
alias gacm='git add . && git commit -m'

# =========================================================
#  System
# =========================================================
alias ports='ss -tulnp'
alias myip='curl -s ifconfig.me && echo'
alias c='code .'
alias vim='nvim'
```

---

## 24. AI/ML Project Quickstart

Create a new AI/ML project with PyTorch ROCm, LangChain, and JupyterLab:

```bash
# 1. Create project
uv init my-ai-project --python 3.12
cd my-ai-project

# 2. Configure PyTorch ROCm index
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
uv add llama-index llama-index-llms-ollama llama-index-embeddings-huggingface
uv add transformers sentence-transformers huggingface-hub
uv add chromadb numpy pandas matplotlib
uv add --dev ipykernel pytest ruff

# 4. Verify GPU
uv run python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'ROCm available: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
print(f'VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB')
"

# 5. Launch Jupyter
uv run --with jupyter jupyter lab

# 6. Initialize git
git init && echo -e '.venv/\n__pycache__/' > .gitignore
git add . && git commit -m "feat: initial AI project setup"
```

**Recommended project structure:**

```
my-ai-project/
├── .python-version        # "3.12"
├── .venv/                 # Auto-created by uv (gitignored)
├── .gitignore
├── pyproject.toml         # Single source of truth for deps
├── uv.lock                # Reproducible builds (commit this)
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
| Install Python packages | `uv add <pkg>` | Inside project |
| Install CLI tools globally | `uv tool install <tool>` | Isolated env |
| Run scripts | `uv run python script.py` | Project venv |
| Run LLMs locally | `ollama run llama3.1:8b` | Uses AMD GPU |
| Chat UI for LLMs | Open WebUI | http://localhost:3000 |
| GPU monitoring | `amdgpu_top` / `rocm-smi` | Real-time |
| Docker management | `lazydocker` | TUI |
| Git management | `lazygit` | TUI |
| API testing | Thunder Client | VS Code extension |
| Smart directory jump | `z <partial-path>` | zoxide |
| Fuzzy file search | `Ctrl+T` | fzf |
| System snapshot | `snapper list` | Btrfs snapshots |
| Password manager | `bitwarden` / `keepassxc` | Desktop + browser |
| VPN | `mullvad connect` | Mullvad VPN |
| Time tracking | Toggl Track | https://track.toggl.com |
| Note-taking | Obsidian | Desktop app |
| Project management | Linear / ClickUp | Browser |

---

## Services Enabled at Boot

```bash
# Verify all critical services are running:
systemctl is-active docker postgresql mariadb valkey mongodb nginx \
  ollama fail2ban dnscrypt-proxy syncthing@$USER ananicy-cpp ufw mullvad-daemon
```

| Service | Purpose |
|---|---|
| `docker` | Container runtime |
| `postgresql` | Primary database |
| `mariadb` | MySQL-compatible database |
| `valkey` | Redis-compatible key-value store |
| `mongodb` | NoSQL document database |
| `nginx` | Reverse proxy / web server |
| `ollama` | Local LLM inference (ROCm GPU) |
| `fail2ban` | Intrusion prevention |
| `dnscrypt-proxy` | Encrypted DNS over HTTPS |
| `syncthing` | Peer-to-peer file sync |
| `ananicy-cpp` | Process priority management |
| `ufw` | Firewall |
| `mullvad-daemon` | VPN daemon |
| `apparmor` | Mandatory access control (after reboot) |
| `paccache.timer` | Weekly package cache cleanup |
| `reflector.timer` | Mirror list refresh |
| `snapper-*.timer` | Automated Btrfs snapshots |

---

*Built for CachyOS · AMD RX 6700 XT (RDNA2) · ROCm 7.2 · KDE Plasma · 32GB RAM*  
*Last updated: April 2026*
