# CachyOS AI Development Workstation: Complete Setup Guide

**A comprehensive, step-by-step setup guide for a CachyOS (Arch Linux) workstation optimized for AI/ML development, Python backend engineering, and freelance productivity.** This guide covers every tool in the stack — from AMD ROCm GPU acceleration and local LLM inference to Django/FastAPI backends, Docker orchestration, and daily productivity apps. Hardware context: 32GB RAM, AMD GPU, KDE Plasma desktop.

---

## Section 1: System foundation and AMD GPU

### CachyOS post-install optimization
**What:** CachyOS ships `cachyos-settings` with sysctl tweaks, I/O scheduler rules, ZRAM config, and audio power management.
```bash
sudo pacman -S cachyos-settings ananicy-cpp cachyos-ananicy-rules
# Settings auto-applied via udev/sysctl. Override in /etc/sysctl.d/99-custom.conf
sudo systemctl enable --now ananicy-cpp.service
```
📎 https://wiki.cachyos.org/features/cachyos_settings/

### AMD GPU drivers (AMDGPU + Mesa + Vulkan)
**What:** Open-source AMD GPU stack — kernel module, Mesa OpenGL/Vulkan, and RADV Vulkan driver.
```bash
sudo pacman -S mesa lib32-mesa vulkan-radeon lib32-vulkan-radeon \
  vulkan-icd-loader lib32-vulkan-icd-loader libva-mesa-driver lib32-libva-mesa-driver
# Verify: lspci -k | grep -A3 VGA  (should show "Kernel driver in use: amdgpu")
```
📎 https://wiki.archlinux.org/title/AMDGPU

### ROCm installation for AI/ML
**What:** AMD's open-source GPU compute platform. The `rocm-hip-sdk` meta-package pulls in HIP runtime, rocBLAS, MIOpen, and all core ROCm libraries.
```bash
sudo pacman -S rocm-hip-sdk rocm-opencl-sdk
sudo usermod -aG render,video $USER   # Required for GPU access
# Log out/in, then verify:
rocminfo && hipcc --version
```
📎 https://rocm.docs.amd.com/projects/install-on-linux/en/latest/

### ROCm compatibility layers — HIP, rocBLAS, MIOpen
**What:** HIP is AMD's CUDA-compatible programming interface; rocBLAS provides GPU-accelerated BLAS; MIOpen is AMD's deep learning primitives library.
```bash
# Already pulled in by rocm-hip-sdk. Individual packages if needed:
sudo pacman -S hip-runtime-amd hipblas rocblas miopen-hip
# HIP programs compile with hipcc. For CUDA porting: hipify-perl or hipify-clang
```
📎 https://rocm.docs.amd.com/projects/HIP/en/latest/

### GPU monitoring tools
**What:** `radeontop` shows real-time GPU utilization; `rocm-smi` provides detailed ROCm GPU stats, temps, and power.
```bash
sudo pacman -S radeontop rocm-smi-lib
# Usage: radeontop (live utilization), rocm-smi (detailed info)
# Optional modern TUI: paru -S amdgpu_top
```
📎 https://github.com/clbr/radeontop · https://rocm.docs.amd.com/projects/rocm_smi_lib/en/latest/

### 32GB RAM optimization — ZRAM and swappiness
**What:** CachyOS enables ZRAM by default with `vm.swappiness=150`, aggressively moving cold pages to compressed ZRAM to free RAM.
```bash
# Verify: swapon --show (should show /dev/zram0)
# Customize ZRAM — create /etc/systemd/zram-generator.conf:
[zram0]
zram-size = min(ram, 8192)
compression-algorithm = zstd

# Optional swap file fallback for heavy AI/ML workloads:
sudo btrfs filesystem mkswapfile --size 8G /swap/swapfile && sudo swapon /swap/swapfile
```
📎 https://wiki.archlinux.org/title/Zram

---

## Section 2: Python development environment

### Python version management — pyenv (recommended)
**What:** CLI tool to install and manage multiple Python versions without touching system Python.
```bash
sudo pacman -S pyenv
sudo pacman -S --needed base-devel openssl zlib xz tk zstd
```
Add to `~/.zshrc`:
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
# Usage: pyenv install 3.12.8 && pyenv global 3.12.8
```
📎 https://github.com/pyenv/pyenv

**Alternative — asdf** (universal version manager for Python, Node, Ruby, etc.):
```bash
yay -S asdf-vm
# Add to shell: source /opt/asdf-vm/asdf.sh
# Then: asdf plugin add python && asdf install python 3.12.8
```
📎 https://asdf-vm.com/

### Virtual environments — venv, virtualenv, Poetry, Pipenv

**venv (built-in):** No install needed — `python -m venv .venv && source .venv/bin/activate`
📎 https://docs.python.org/3/library/venv.html

**virtualenv:** Enhanced venv with faster creation — `pipx install virtualenv`
📎 https://virtualenv.pypa.io/

**Poetry ⭐ (recommended):** Modern dependency manager with lockfiles, resolution, and publishing.
```bash
pipx install poetry
poetry config virtualenvs.in-project true  # Store .venv in project dir
# Usage: poetry init / poetry add requests / poetry install / poetry shell
```
📎 https://python-poetry.org/docs/

**Pipenv:** Combines pip + virtualenv with Pipfile.lock — `pipx install pipenv`
📎 https://pipenv.pypa.io/

### pip and pipx
**What:** `pip` is Python's standard installer; `pipx` installs CLI tools in isolated environments.
```bash
sudo pacman -S python-pip python-pipx
pipx ensurepath
# pip install <library>   (inside a venv)
# pipx install ruff       (global CLI tool, isolated)
```
📎 https://pip.pypa.io/ · https://pipx.pypa.io/

### Python debugging — pdb, ipdb, pudb
**What:** `pdb` — built-in debugger; `ipdb` — IPython-enhanced; `pudb` — full-screen TUI debugger.
```bash
pip install ipdb pudb
# Usage: import ipdb; ipdb.set_trace()
# Or: PYTHONBREAKPOINT=pudb.set_trace python script.py
```
📎 https://github.com/gotcha/ipdb · https://github.com/inducer/pudb

### Linting and formatting — ruff ⭐ (recommended all-in-one)
**What:** Extremely fast Rust-based linter + formatter replacing flake8, isort, and partially black.
```bash
sudo pacman -S ruff
# Or: pipx install ruff
```
Add to `pyproject.toml`:
```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "UP", "B", "SIM"]
# ruff check . && ruff format .
```
📎 https://docs.astral.sh/ruff/

**Additional linters/formatters:**
```bash
pipx install black    # Opinionated formatter — https://black.readthedocs.io/
pipx install isort    # Import sorter — https://pycqa.github.io/isort/
pipx install mypy     # Static type checker — https://mypy.readthedocs.io/
pipx install pylint   # Comprehensive analyzer — https://pylint.readthedocs.io/
```

### Pre-commit hooks
**What:** Framework for running linters/formatters automatically before each commit.
```bash
pipx install pre-commit
```
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
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
```
```bash
pre-commit install && pre-commit run --all-files
```
📎 https://pre-commit.com/

### Jupyter Notebook/Lab
**What:** Interactive notebook environment for data exploration, prototyping, and ML experimentation.
```bash
pip install jupyterlab notebook ipykernel
python -m ipykernel install --user --name=myproject --display-name "Python (myproject)"
jupyter lab   # Opens at http://localhost:8888
```
📎 https://jupyterlab.readthedocs.io/

---

## Section 3: AI/ML and LLM stack (primary focus)

### PyTorch with ROCm support ⭐
**What:** Leading deep learning framework. AMD provides official ROCm-accelerated wheels.
```bash
# Stable (PyTorch 2.7 + ROCm 6.3) — inside your venv:
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.3

# Nightly (ROCm 7.x):
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm7.0
```
Verify:
```python
import torch
print(torch.cuda.is_available())      # True (ROCm uses CUDA API via HIP)
print(torch.cuda.get_device_name(0))  # Shows your AMD GPU
```
📎 https://pytorch.org/get-started/locally/

### TensorFlow with ROCm
**What:** Google's deep learning framework. ROCm support via `tensorflow-rocm` — **Docker recommended** on Arch.
```bash
# Docker (recommended for reliability):
docker run -it --network=host --device=/dev/kfd --device=/dev/dri \
  --ipc=host --shm-size 16G --group-add video \
  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
  rocm/tensorflow:latest

# pip (may work if glibc is compatible):
pip3 install tensorflow-rocm --extra-index-url https://repo.radeon.com/rocm/manylinux/rocm-rel-7.2/
```
📎 https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/3rd-party/tensorflow-install.html

### LangChain
**What:** Framework for building LLM-powered applications — chains, agents, RAG pipelines.
```bash
pip install langchain langchain-community langchain-core langgraph
pip install langchain-openai langchain-ollama langchain-huggingface langchain-chroma
```
📎 https://python.langchain.com/docs/

### LlamaIndex
**What:** Data framework for connecting LLMs to structured/unstructured data with RAG pipelines.
```bash
pip install llama-index
pip install llama-index-llms-ollama llama-index-embeddings-huggingface llama-index-vector-stores-chroma
```
📎 https://docs.llamaindex.ai/

### Ollama for local LLM inference with AMD ROCm ⭐
**What:** Simple tool for running LLMs locally. Arch ships `ollama-rocm` pre-built with AMD GPU acceleration.
```bash
sudo pacman -S ollama-rocm
sudo usermod -aG render,video $USER
sudo systemctl enable --now ollama.service

# For unsupported GPUs, create override:
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="HSA_OVERRIDE_GFX_VERSION=11.0.0"
EOF
sudo systemctl daemon-reload && sudo systemctl restart ollama

# Pull and run a model:
ollama pull llama3.1:8b && ollama run llama3.1:8b
```
📎 https://ollama.com/ · https://wiki.archlinux.org/title/Ollama

### Open WebUI
**What:** Self-hosted web chat interface for LLMs — connects to Ollama and OpenAI-compatible APIs.
```bash
# Docker (recommended):
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main

# Or pip: pipx install open-webui && open-webui serve
# Access: http://localhost:3000 — create admin account on first visit
```
📎 https://docs.openwebui.com/

### Vector databases

**Pinecone (cloud):** Fully managed cloud vector database.
```bash
pip install pinecone
# from pinecone import Pinecone; pc = Pinecone(api_key="YOUR_KEY")
```
📎 https://docs.pinecone.io/

**Weaviate (local Docker):** Open-source vector DB with built-in vectorization and hybrid search.
```bash
docker run -d -p 8080:8080 -p 50051:50051 \
  -v weaviate_data:/var/lib/weaviate \
  --name weaviate cr.weaviate.io/semitechnologies/weaviate:latest
pip install weaviate-client
```
📎 https://weaviate.io/developers/weaviate

**ChromaDB (local):** Lightweight embeddable vector database — perfect for prototyping.
```bash
pip install chromadb
# import chromadb; client = chromadb.PersistentClient(path="./chroma_db")
```
📎 https://docs.trychroma.com/

**pgvector (PostgreSQL extension):** Vector similarity search in your existing Postgres.
```bash
git clone --branch v0.8.1 https://github.com/pgvector/pgvector.git /tmp/pgvector
cd /tmp/pgvector && make && sudo make install
# In psql: CREATE EXTENSION vector;
pip install pgvector psycopg2-binary
```
📎 https://github.com/pgvector/pgvector

### Hugging Face Transformers and sentence-transformers
**What:** Industry-standard pretrained model library and specialized text embedding generation.
```bash
pip install transformers datasets accelerate tokenizers sentence-transformers
```
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")  # Runs on ROCm GPU automatically
embeddings = model.encode(["Hello world", "AI is amazing"])
```
📎 https://huggingface.co/docs/transformers · https://www.sbert.net/

### vLLM for production LLM serving ⭐
**What:** High-throughput LLM serving engine with PagedAttention. ROCm is a first-class platform.
```bash
# pip (ROCm wheel):
uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/

# Docker (recommended for production):
docker run --rm --device /dev/kfd --device /dev/dri \
  --group-add=video --ipc=host --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 vllm/vllm-openai-rocm:latest \
  --model Qwen/Qwen3-0.6B
```
📎 https://docs.vllm.ai/en/latest/getting_started/installation/gpu/

**Text Generation Inference (TGI) — alternative:**
```bash
docker run --device=/dev/kfd --device=/dev/dri --group-add video \
  --ipc=host --shm-size 1g -p 8080:80 -v $PWD/data:/data \
  ghcr.io/huggingface/text-generation-inference:latest-rocm \
  --model-id meta-llama/Meta-Llama-3-8B
```
📎 https://huggingface.co/docs/text-generation-inference

### llama.cpp with ROCm/HIP support (GGUF models) ⭐
**What:** High-performance C/C++ inference engine for GGUF quantized models with AMD GPU acceleration via HIP.
```bash
sudo pacman -S rocm-hip-sdk rocm-opencl-sdk
git clone https://github.com/ggml-org/llama.cpp.git && cd llama.cpp

# Find your GPU arch: rocminfo | grep gfx | head -1 | awk '{print $2}'
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build -DGGML_HIP=ON \
  -DAMDGPU_TARGETS=gfx1100 \
  -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=ON \
  && cmake --build build --config Release -j$(nproc)

# Run: ./build/bin/llama-cli -m model.gguf -ngl 99 -p "Hello"
# Server: ./build/bin/llama-server -m model.gguf -ngl 99 --host 0.0.0.0 --port 8080
```
📎 https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md

### Semantic search tools and embeddings
**What:** Complete stack for semantic search — embeddings + vector storage + similarity queries.
```bash
pip install sentence-transformers chromadb langchain-chroma faiss-cpu
ollama pull nomic-embed-text   # Local embedding model via Ollama
```
Recommended embedding models: `all-MiniLM-L6-v2` (fast, 384d), `bge-large-en-v1.5` (high quality, 1024d), `nomic-embed-text` (local via Ollama).

📎 https://www.sbert.net/ · https://docs.trychroma.com/

---

## Section 4: Backend frameworks and tools

### Django + Django REST Framework
**What:** Full-featured Python web framework with a powerful REST API toolkit.
```bash
pip install django djangorestframework
django-admin startproject myproject && cd myproject
python manage.py startapp myapp
# Add 'rest_framework' to INSTALLED_APPS in settings.py
```
📎 https://www.djangoproject.com/ · https://www.django-rest-framework.org/

### FastAPI + Uvicorn + Gunicorn
**What:** Modern async web framework with auto-generated OpenAPI docs, served by Uvicorn (ASGI) and Gunicorn (process manager).
```bash
pip install fastapi uvicorn[standard] gunicorn
# Dev: uvicorn main:app --reload
# Prod: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
📎 https://fastapi.tiangolo.com/ · https://www.uvicorn.org/

### Flask
**What:** Lightweight Python micro-framework for web applications and APIs.
```bash
pip install flask
# Run: flask run --debug
```
📎 https://flask.palletsprojects.com/

### Celery + Redis (message broker)
**What:** Distributed task queue for async/scheduled jobs; Redis serves as the message broker.
```bash
pip install celery redis
```
```python
# celery_app.py
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
@app.task
def add(x, y): return x + y
# Run worker: celery -A celery_app worker --loglevel=info
```
📎 https://docs.celeryq.dev/

### WebSockets support
**What:** Real-time bidirectional communication for Django (Channels) and FastAPI (built-in).
```bash
pip install channels channels-redis   # Django Channels
pip install websockets                # Standalone / FastAPI uses Starlette's built-in WebSocket support
```
📎 https://channels.readthedocs.io/ · https://websockets.readthedocs.io/

### AsyncIO tooling
**What:** Essential async libraries for HTTP clients, web servers, and database access.
```bash
pip install aiohttp httpx asyncpg
# aiohttp — async HTTP client/server
# httpx — modern async/sync HTTP client with HTTP/2
# asyncpg — fast async PostgreSQL driver
```
📎 https://docs.aiohttp.org/ · https://www.python-httpx.org/ · https://magicstack.github.io/asyncpg/

---

## Section 5: Databases

### PostgreSQL
**What:** Advanced open-source relational database — the gold standard for Python backend work.
```bash
sudo pacman -S postgresql
sudo -iu postgres initdb --locale=C.UTF-8 -E UTF8 -D /var/lib/postgres/data --data-checksums
sudo systemctl enable --now postgresql
sudo -iu postgres psql -c "CREATE USER devuser WITH ENCRYPTED PASSWORD 'devpass';"
sudo -iu postgres psql -c "CREATE DATABASE devdb OWNER devuser;"
```
**pgvector extension:**
```bash
yay -S pgvector   # Or build from source (see Section 3)
# In psql: CREATE EXTENSION vector;
```
📎 https://www.postgresql.org/ · https://wiki.archlinux.org/title/PostgreSQL

### MySQL / MariaDB
**What:** MariaDB is Arch's default MySQL-compatible drop-in replacement.
```bash
sudo pacman -S mariadb
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo systemctl enable --now mariadb
sudo mariadb-secure-installation
```
📎 https://mariadb.org/ · https://wiki.archlinux.org/title/MariaDB

### MongoDB
**What:** NoSQL document database — install prebuilt binary from AUR.
```bash
yay -S mongodb-bin   # Use -bin (prebuilt); building from source takes hours
sudo systemctl enable --now mongodb
# Verify: mongosh
```
📎 https://www.mongodb.com/ · https://wiki.archlinux.org/title/MongoDB

### Redis
**What:** In-memory key-value store for caching, message brokering, and sessions.
```bash
sudo pacman -S redis
sudo systemctl enable --now redis
redis-cli ping   # → PONG
```
📎 https://redis.io/ · https://wiki.archlinux.org/title/Redis

### Elasticsearch
**What:** Distributed full-text search engine. **Docker recommended** on Arch.
```bash
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.0
# Verify: curl http://localhost:9200
```
📎 https://www.elastic.co/elasticsearch

### SQLite
**What:** Lightweight serverless file-based database — ships with Python's `sqlite3` module.
```bash
sudo pacman -S sqlite   # CLI tool (likely already installed as Python dependency)
# Python: import sqlite3; conn = sqlite3.connect('mydb.db')
```
📎 https://www.sqlite.org/

### Database GUI tools

**DBeaver ⭐ (recommended — universal):** Supports PostgreSQL, MySQL, SQLite, MongoDB, and 80+ databases.
```bash
sudo pacman -S dbeaver
```
📎 https://dbeaver.io/

**pgAdmin 4 (Docker recommended):**
```bash
docker run -d --name pgadmin -p 5050:80 \
  -e "PGADMIN_DEFAULT_EMAIL=admin@local.dev" \
  -e "PGADMIN_DEFAULT_PASSWORD=admin" \
  dpage/pgadmin4
```
📎 https://www.pgadmin.org/

---

## Section 6: DevOps and cloud tools

### Docker + Docker Compose
**What:** Container platform + multi-container orchestration.
```bash
sudo pacman -S docker docker-compose docker-buildx
sudo systemctl enable --now docker.service
sudo usermod -aG docker $USER
newgrp docker   # Or log out/in
```
For rootless Docker, see https://wiki.archlinux.org/title/Docker#Rootless_Docker_daemon.

📎 https://docs.docker.com/ · https://wiki.archlinux.org/title/Docker

### Kubernetes tools — kubectl, minikube, Helm
```bash
sudo pacman -S kubectl minikube helm
minikube start --driver=docker
```
**k3s alternative:** `curl -sfL https://get.k3s.io | sh -`

📎 https://kubernetes.io/docs/reference/kubectl/ · https://minikube.sigs.k8s.io/ · https://helm.sh/

### AWS CLI v2
```bash
sudo pacman -S aws-cli-v2
aws configure   # Set Access Key, Secret Key, region, output format
```
📎 https://docs.aws.amazon.com/cli/latest/userguide/

### Azure CLI
```bash
sudo pacman -S azure-cli
az login   # Opens browser for interactive auth
```
📎 https://learn.microsoft.com/en-us/cli/azure/

### Google Cloud SDK
```bash
yay -S google-cloud-cli
gcloud init   # Authenticate and set default project/region
```
📎 https://cloud.google.com/sdk/docs/

### Terraform
```bash
sudo pacman -S terraform
terraform -v
```
📎 https://www.terraform.io/

### Nginx
```bash
sudo pacman -S nginx
sudo systemctl enable --now nginx
# Config: /etc/nginx/nginx.conf
```
📎 https://nginx.org/en/docs/ · https://wiki.archlinux.org/title/Nginx

### CI/CD local tools — act and GitLab Runner
```bash
sudo pacman -S act           # Run GitHub Actions locally
sudo pacman -S gitlab-runner  # GitLab CI runner
# Usage: cd /your/repo && act
```
📎 https://github.com/nektos/act · https://docs.gitlab.com/runner/

---

## Section 7: Containerization and deployment

### Docker best practices for Python apps

- **Multi-stage builds:** Builder stage for dependencies → slim final image
- **Slim base images:** Use `python:3.12-slim` (~150MB vs ~900MB)
- **`.dockerignore`:** Exclude `.git`, `__pycache__`, `.venv`, `.env`, `node_modules`
- **Non-root user:** `RUN useradd -m appuser && USER appuser`
- **Pin versions:** Pin base image tag and pip package versions

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

### Docker Compose for multi-service local dev

```yaml
# docker-compose.yml — Django + Postgres + Redis + Celery
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp_db
      POSTGRES_USER: myapp_user
      POSTGRES_PASSWORD: changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes: [".:/app"]
    ports: ["8000:8000"]
    env_file: [.env]
    environment:
      DATABASE_URL: postgres://myapp_user:changeme@db:5432/myapp_db
      REDIS_URL: redis://redis:6379/0
    depends_on: [db, redis]

  celery_worker:
    build: .
    command: celery -A myproject worker -l info
    volumes: [".:/app"]
    env_file: [.env]
    environment:
      DATABASE_URL: postgres://myapp_user:changeme@db:5432/myapp_db
      REDIS_URL: redis://redis:6379/0
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
Run: `docker compose up -d` — Tear down: `docker compose down -v`

### Container registry authentication
```bash
# Docker Hub:
docker login

# AWS ECR:
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com

# Google Artifact Registry:
gcloud auth configure-docker us-central1-docker.pkg.dev
```

---

## Section 8: Data engineering

### Apache Kafka (local Docker — Redpanda recommended)
**What:** Distributed event streaming. Redpanda is a lighter, Kafka-API-compatible alternative (no JVM, ~512MB RAM).
```yaml
# docker-compose.yml
services:
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:latest
    command:
      - redpanda start
      - --smp 1
      - --memory 512M
      - --overprovisioned
      - --node-id 0
      - --kafka-addr internal://0.0.0.0:9092,external://0.0.0.0:19092
      - --advertise-kafka-addr internal://redpanda:9092,external://localhost:19092
    ports: ["19092:19092", "18081:18081", "9644:9644"]
  console:
    image: docker.redpanda.com/redpandadata/console:latest
    ports: ["8080:8080"]
    environment:
      KAFKA_BROKERS: redpanda:9092
    depends_on: [redpanda]
```
📎 https://docs.redpanda.com/current/get-started/quick-start/ · https://kafka.apache.org/

### Pandas, NumPy, Plotly
```bash
pip install pandas numpy plotly kaleido
```
📎 https://pandas.pydata.org/ · https://numpy.org/ · https://plotly.com/python/

### ETL pipeline tools
```bash
pip install apache-airflow   # Industry-standard workflow orchestrator
pip install prefect           # Modern Python-native orchestration
pip install luigi             # Lightweight pipeline framework (Spotify)
```
📎 https://airflow.apache.org/ · https://docs.prefect.io/ · https://luigi.readthedocs.io/

### Data preprocessing libraries
```bash
pip install scikit-learn polars dask[complete] pyarrow
```

| Library | Purpose |
|---|---|
| **scikit-learn** | ML preprocessing, feature engineering, model pipelines |
| **Polars** | Blazing-fast Rust-based DataFrame library for large datasets |
| **Dask** | Parallel computing that scales Pandas/NumPy to larger-than-memory |
| **PyArrow** | Apache Arrow bindings for columnar data and Parquet I/O |

📎 https://scikit-learn.org/ · https://pola.rs/ · https://www.dask.org/ · https://arrow.apache.org/docs/python/

---

## Section 9: Frontend (when needed)

### Node.js via nvm
```bash
sudo pacman -S nvm
# Add to ~/.zshrc:
source /usr/share/nvm/init-nvm.sh
# Install LTS:
nvm install --lts && nvm use --lts
```
📎 https://github.com/nvm-sh/nvm

### Package managers — npm, yarn, pnpm
```bash
# npm comes with Node.js
corepack enable                           # Enables yarn and pnpm via corepack
corepack prepare yarn@stable --activate   # Yarn 4+
corepack prepare pnpm@latest --activate   # pnpm
```
📎 https://yarnpkg.com/ · https://pnpm.io/

### React + Next.js
```bash
npm create vite@latest my-react-app -- --template react-ts   # React with Vite
npx create-next-app@latest my-next-app                        # Next.js (follow prompts)
```
📎 https://react.dev/ · https://nextjs.org/docs

### TypeScript
```bash
npm install -D typescript
npx tsc --init   # Generates tsconfig.json
```
📎 https://www.typescriptlang.org/

### Tailwind CSS
```bash
npm install -D tailwindcss @tailwindcss/postcss postcss
npx tailwindcss init
# Add to CSS entry: @import "tailwindcss";
```
📎 https://tailwindcss.com/docs/installation

---

## Section 10: Code editors and IDEs

### VS Code
```bash
# Open-source build (Open VSX marketplace):
sudo pacman -S code

# Microsoft build (full marketplace + Remote Dev):
yay -S visual-studio-code-bin
```
📎 https://code.visualstudio.com/

### VS Codium
**What:** Telemetry-free, MIT-licensed VS Code binary.
```bash
yay -S vscodium-bin
```
📎 https://vscodium.com/

### Essential VS Code extensions
```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-azuretools.vscode-docker
code --install-extension eamodio.gitlens
code --install-extension ms-vscode-remote.remote-ssh
code --install-extension ms-toolsai.jupyter
code --install-extension GitHub.copilot
code --install-extension Continue.continue
```

| Extension | ID | Purpose |
|---|---|---|
| Python | `ms-python.python` | Language support, debugging, venvs |
| Pylance | `ms-python.vscode-pylance` | Fast IntelliSense and type checking |
| Ruff | `charliermarsh.ruff` | Blazing-fast linter and formatter |
| Docker | `ms-azuretools.vscode-docker` | Dockerfile/Compose support |
| GitLens | `eamodio.gitlens` | Git blame, history, authorship |
| Remote SSH | `ms-vscode-remote.remote-ssh` | Edit files on remote machines |
| Jupyter | `ms-toolsai.jupyter` | Notebook support in VS Code |
| GitHub Copilot | `GitHub.copilot` | AI pair programmer (subscription) |
| Continue | `Continue.continue` | Open-source AI assistant (any model) |

📎 https://marketplace.visualstudio.com/ · https://docs.continue.dev/

### Neovim + LazyVim
```bash
sudo pacman -S neovim git lazygit ripgrep fd
mv ~/.config/nvim{,.bak}     # Backup existing config
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
nvim                          # Plugins auto-install on first run
```
**AstroNvim alternative:** `git clone --depth 1 https://github.com/AstroNvim/template ~/.config/nvim`

📎 https://www.lazyvim.org/ · https://astronvim.com/

### PyCharm
```bash
sudo pacman -S pycharm-community-edition   # Free
yay -S pycharm-professional                # Paid
```
📎 https://www.jetbrains.com/pycharm/

---

## Section 11: Terminal and shell

### Zsh + Oh My Zsh
```bash
sudo pacman -S zsh
chsh -s $(which zsh)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
Add to `~/.zshrc`:
```bash
plugins=(git zsh-autosuggestions zsh-syntax-highlighting docker kubectl)
```
📎 https://ohmyz.sh/

### Fish shell (alternative)
```bash
sudo pacman -S fish
# Try without switching: fish
# Set as default: chsh -s $(which fish)
```
📎 https://fishshell.com/

### Terminal emulators — Kitty ⭐, Alacritty, WezTerm
```bash
sudo pacman -S kitty       # GPU-accelerated, feature-rich (recommended)
sudo pacman -S alacritty   # Minimalist, blazing-fast (pair with tmux)
sudo pacman -S wezterm     # GPU-accelerated, Lua config, built-in multiplexer
```
📎 https://sw.kovidgoyal.net/kitty/ · https://alacritty.org/ · https://wezfurlong.org/wezterm/

### Starship prompt
```bash
sudo pacman -S starship
# Add to ~/.zshrc: eval "$(starship init zsh)"
```
📎 https://starship.rs/

### tmux and Zellij
```bash
sudo pacman -S tmux     # Classic multiplexer — Ctrl-b c (new window), Ctrl-b % (split)
sudo pacman -S zellij   # Modern Rust multiplexer — beginner-friendly help bar
```
📎 https://github.com/tmux/tmux · https://zellij.dev/

### Modern CLI tools
```bash
sudo pacman -S fzf ripgrep fd bat eza zoxide
```

| Tool | Replaces | Purpose |
|---|---|---|
| **fzf** | — | Fuzzy finder for files, history |
| **ripgrep** (`rg`) | `grep` | 10x faster recursive search |
| **fd** | `find` | Fast file finder with intuitive syntax |
| **bat** | `cat` | Syntax highlighting, Git integration |
| **eza** | `ls` | Icons, Git status, tree view |
| **zoxide** | `cd` | Smart directory jumping |

Add to `~/.zshrc`:
```bash
eval "$(zoxide init zsh)"
source /usr/share/fzf/key-bindings.zsh
source /usr/share/fzf/completion.zsh
alias ls='eza --icons --group-directories-first'
alias ll='eza -la --icons --group-directories-first --git'
alias cat='bat --style=plain --paging=never'
```

### TUI tools — lazygit and lazydocker
```bash
sudo pacman -S lazygit   # Terminal UI for Git
yay -S lazydocker        # Terminal UI for Docker
```
📎 https://github.com/jesseduffield/lazygit · https://github.com/jesseduffield/lazydocker

---

## Section 12: Git and version control

### Git configuration
```bash
sudo pacman -S git

# Identity
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# GPG signing
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# Aliases
git config --global alias.st "status -sb"
git config --global alias.co "checkout"
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.amend "commit --amend --no-edit"

# Global .gitignore
cat >> ~/.gitignore_global << 'EOF'
.DS_Store
*.swp
.idea/
.vscode/
__pycache__/
*.pyc
.env
.env.local
node_modules/
EOF
git config --global core.excludesfile ~/.gitignore_global

# Recommended defaults
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global fetch.prune true
git config --global diff.colorMoved zebra
```
📎 https://git-scm.com/doc

### GitHub CLI (gh)
```bash
sudo pacman -S github-cli
gh auth login       # Interactive auth via browser
gh auth status      # Verify
```
📎 https://cli.github.com/manual/

### Git workflow best practices
**Conventional Commits:** `type(scope): description` — e.g., `feat(auth): add OAuth2 login`, `fix(api): handle null response`. Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`. See https://www.conventionalcommits.org/

**Branch naming:** `feature/add-user-auth`, `bugfix/fix-login-crash`, `hotfix/patch-security`, `release/v1.2.0`. Include ticket numbers: `feature/PROJ-123-add-search`.

---

## Section 13: Browsers

### Firefox Developer Edition
**What:** Mozilla's dev-focused browser with advanced DevTools and CSS Grid inspector.
```bash
sudo pacman -S firefox-developer-edition
```
📎 https://www.mozilla.org/en-US/firefox/developer/

### Brave Browser
**What:** Privacy-focused Chromium with built-in ad/tracker blocking.
```bash
yay -S brave-bin
```
📎 https://brave.com/

### LibreWolf
**What:** Privacy-hardened Firefox fork with telemetry removed and uBlock Origin included.
```bash
yay -S librewolf-bin
```
📎 https://librewolf.net/

### Mullvad Browser
**What:** Anti-fingerprinting browser co-developed with the Tor Project.
```bash
yay -S mullvad-browser-bin
```
📎 https://mullvad.net/en/browser

### Ungoogled Chromium
**What:** Chromium with all Google tracking removed.
```bash
yay -S ungoogled-chromium-bin
```
📎 https://github.com/ungoogled-software/ungoogled-chromium

### Essential browser extensions

| Extension | Purpose |
|---|---|
| **uBlock Origin** | Best-in-class ad/tracker blocker |
| **Dark Reader** | Dark mode for all websites |
| **JSON Viewer** | Pretty-prints JSON responses in-browser |
| **React DevTools** | Inspect React component tree and state |
| **Wappalyzer** | Identify technologies on any website |
| **Bitwarden** | Password manager auto-fill |
| **Privacy Badger** | EFF's adaptive tracker blocker |
| **Refined GitHub** | Enhanced GitHub UI |

---

## Section 14: Note-taking and knowledge management

### Obsidian ⭐ (recommended for personal knowledge)
**What:** Markdown-based knowledge base with graph view, backlinks, and plugins.
```bash
sudo pacman -S obsidian
```
📎 https://obsidian.md/

### Notion
**What:** All-in-one workspace for collaboration, wikis, and databases.
```bash
yay -S notion-app-electron   # Or use https://notion.so in browser
```
📎 https://www.notion.so/

### Logseq
**What:** Open-source outliner with block-based editing and daily journals.
```bash
yay -S logseq-desktop-bin
```
📎 https://logseq.com/

### When to use which

| Tool | Best for |
|---|---|
| **Obsidian** | Personal knowledge base, local-first Markdown, Git-friendly, works offline |
| **Notion** | Team collaboration, project wikis, databases — requires internet |
| **Logseq** | Outliner-style daily journaling, block-level referencing |

**Recommendation:** Obsidian as primary personal tool. Notion for client collaboration. Logseq if you prefer outliner-style.

---

## Section 15: Productivity and workflow

### Screenshots — Flameshot and Spectacle
```bash
sudo pacman -S flameshot spectacle
# flameshot gui (annotation tools) / spectacle (KDE default, PrintScreen key)
```
📎 https://flameshot.org/ · https://apps.kde.org/spectacle/

### KDE Connect
**What:** Phone-to-desktop integration — file transfer, notifications, clipboard sync.
```bash
sudo pacman -S kdeconnect
# Firewall: sudo ufw allow 1714:1764/udp && sudo ufw allow 1714:1764/tcp
```
📎 https://kdeconnect.kde.org/

### Thunderbird
**What:** Full-featured email client with calendar, contacts, and extension support.
```bash
sudo pacman -S thunderbird
```
📎 https://www.thunderbird.net/

### Calendar — KOrganizer and Thunderbird
```bash
sudo pacman -S korganizer   # Standalone KDE calendar
# Thunderbird's calendar is built-in — no extra install needed
```
📎 https://kontact.kde.org/components/korganizer/

### Password managers — Bitwarden and KeePassXC
```bash
sudo pacman -S bitwarden keepassxc
# Bitwarden: cloud-synced, cross-device
# KeePassXC: local/offline, sync .kdbx via Syncthing
```
📎 https://bitwarden.com/ · https://keepassxc.org/

### File sync — Syncthing
```bash
sudo pacman -S syncthing
systemctl --user enable --now syncthing.service
# Web UI: http://127.0.0.1:8384
```
📎 https://syncthing.net/

### Clipboard manager — CopyQ and Klipper
```bash
sudo pacman -S copyq   # Feature-rich clipboard manager
# Klipper is pre-installed with KDE Plasma (system tray)
```
📎 https://hluk.github.io/CopyQ/

### PDF viewer — Okular
```bash
sudo pacman -S okular   # Pre-installed on CachyOS KDE
```
📎 https://okular.kde.org/

### Video calls — Zoom and Discord
```bash
yay -S zoom
sudo pacman -S discord
# Wayland screen sharing fix:
sudo pacman -S xdg-desktop-portal xdg-desktop-portal-kde
```
📎 https://zoom.us/ · https://discord.com/

### Communication — Slack and Discord
```bash
yay -S slack-desktop
sudo pacman -S discord
```
📎 https://slack.com/ · https://discord.com/

### Time tracking — Toggl Track and Clockify
**What:** Both are **web-based** — Linux desktop apps are deprecated or unreliable. Use the web apps or install as browser PWAs.
- **Toggl Track:** https://track.toggl.com/
- **Clockify:** https://app.clockify.me/

📎 https://toggl.com/track/ · https://clockify.me/

---

## Section 16: Security hardening

### Firewall — UFW
**What:** CachyOS ships and enables UFW by default.
```bash
sudo pacman -S ufw
sudo ufw enable && sudo systemctl enable --now ufw.service
sudo ufw allow ssh
sudo ufw allow 1714:1764/udp   # KDE Connect
sudo ufw allow 1714:1764/tcp
sudo ufw status verbose
```
📎 https://wiki.archlinux.org/title/Uncomplicated_Firewall

### Fail2ban
**What:** Intrusion prevention — bans IPs with too many failed auth attempts.
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

### SSH hardening
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
ssh-keygen -t ed25519 -a 100
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host
sudo systemctl restart sshd
```
📎 https://wiki.archlinux.org/title/OpenSSH#Protection

### Disk encryption (LUKS)
**What:** Full-disk encryption — **must be configured at install time**. CachyOS installer offers a LUKS checkbox during partitioning.
```bash
# Verify: lsblk -f (look for crypto_LUKS)
# For SSD TRIM: add allow-discards to /etc/crypttab
# Backup headers: sudo cryptsetup luksHeaderBackup /dev/sdXn --header-backup-file /safe/header.img
```
📎 https://wiki.archlinux.org/title/Dm-crypt/Encrypting_an_entire_system

### Encrypted DNS (DNS over HTTPS)
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
```bash
# Set DNS to 127.0.0.1 in NetworkManager
sudo systemctl enable --now dnscrypt-proxy.service
```
📎 https://wiki.archlinux.org/title/Dnscrypt-proxy

### VPN — Mullvad and ProtonVPN
```bash
# Mullvad:
paru -S mullvad-vpn-bin
sudo systemctl enable --now mullvad-daemon.service
mullvad account login <ACCOUNT_NUMBER> && mullvad connect

# ProtonVPN:
sudo pacman -S proton-vpn-gtk-app
# Launch from app menu and log in
```
📎 https://mullvad.net/ · https://wiki.archlinux.org/title/ProtonVPN

### AppArmor on CachyOS
**What:** Mandatory Access Control system. CachyOS kernels include AppArmor but it's **not enabled by default**.
```bash
sudo pacman -S apparmor apparmor.d
```
Add kernel parameter (systemd-boot: edit `/boot/loader/entries/*.conf`):
```
lsm=landlock,lockdown,yama,integrity,apparmor,bpf
```
```bash
sudo systemctl enable --now apparmor.service
# Reboot required. Verify: sudo aa-status
```
📎 https://wiki.archlinux.org/title/AppArmor

---

## Section 17: System maintenance

### Automatic updates strategy
**What:** Full auto-updates are risky on Arch. CachyOS provides `cachy-update` — a systray notifier for reviewing and applying updates interactively.
```bash
sudo pacman -S cachy-update   # Pre-installed; checks hourly
# Best practice: review updates, keep Snapper snapshots, reboot after kernel updates
```
📎 https://wiki.cachyos.org/configuration/post_install_setup/

### Snapper for btrfs snapshots
**What:** CachyOS defaults to Btrfs with Snapper + `snap-pac` (auto-creates snapshots on pacman transactions).
```bash
sudo pacman -S snapper snap-pac btrfs-assistant
# Verify: snapper list
# Restore: boot from GRUB snapshot entry or use snapper rollback
```
📎 https://wiki.cachyos.org/configuration/btrfs_snapshots/ · https://wiki.archlinux.org/title/Snapper

### Reflector for mirror optimization
```bash
sudo pacman -S reflector
sudo reflector --country 'United States' --age 12 --protocol https --sort rate --save /etc/pacman.d/mirrorlist
sudo systemctl enable --now reflector.timer

# CachyOS mirrors:
sudo pacman -S cachyos-rate-mirrors && sudo cachyos-rate-mirrors
```
📎 https://wiki.archlinux.org/title/Reflector

### System monitoring — btop, nvtop, Mission Center
```bash
sudo pacman -S btop nvtop mission-center
# btop — full system TUI monitor (auto-detects AMD GPUs)
# nvtop — GPU process monitor (supports AMD despite the name)
# mission-center — GTK4 GUI system monitor
```
📎 https://github.com/aristocratos/btop · https://github.com/Syllo/nvtop · https://gitlab.com/mission-center-devs/mission-center

### Disk usage — ncdu and dust
```bash
sudo pacman -S ncdu dust
# ncdu / — interactive disk usage (arrow keys to navigate, d to delete)
# dust — visual proportional disk usage overview
```
📎 https://dev.yorhel.nl/ncdu · https://github.com/bootandy/dust

### Package cache cleanup — paccache
```bash
sudo pacman -S pacman-contrib
sudo paccache -r          # Keep last 3 versions
sudo paccache -ruk0       # Remove all uninstalled package cache
sudo systemctl enable --now paccache.timer   # Automate weekly cleanup
```
📎 https://wiki.archlinux.org/title/Pacman#Cleaning_the_package_cache

---

## Section 18: Media and personal

### Media players — VLC and mpv
```bash
sudo pacman -S vlc mpv
```
Optional mpv config (`~/.config/mpv/mpv.conf`):
```ini
hwdec=auto
vo=gpu-next
profile=gpu-hq
```
📎 https://www.videolan.org/vlc/ · https://mpv.io/

### Image editing — GIMP and Inkscape
```bash
sudo pacman -S gimp inkscape
# GIMP — raster/photo editing (Photoshop alternative)
# Inkscape — vector graphics (Illustrator alternative)
```
📎 https://www.gimp.org/ · https://inkscape.org/

### Office suite — LibreOffice and OnlyOffice
```bash
sudo pacman -S libreoffice-fresh    # Latest features (or libreoffice-still for stable)
yay -S onlyoffice-bin               # Better MS Office compatibility
```
📎 https://www.libreoffice.org/ · https://www.onlyoffice.com/

### Music — Spotify and Strawberry
```bash
yay -S spotify                     # Streaming (AUR, proprietary)
sudo pacman -S strawberry          # Local music player (FLAC, MP3, gapless)
```
📎 https://open.spotify.com/ · https://www.strawberrymusicplayer.org/

---

## Quick-start bulk install commands

Run these to install most system packages in one shot:

```bash
# Section 1: System & GPU
sudo pacman -S cachyos-settings ananicy-cpp cachyos-ananicy-rules \
  mesa lib32-mesa vulkan-radeon lib32-vulkan-radeon vulkan-icd-loader lib32-vulkan-icd-loader \
  libva-mesa-driver lib32-libva-mesa-driver rocm-hip-sdk rocm-opencl-sdk radeontop rocm-smi-lib

# Section 2: Python base
sudo pacman -S pyenv python-pip python-pipx ruff

# Section 5: Databases
sudo pacman -S postgresql mariadb redis sqlite dbeaver

# Section 6: DevOps
sudo pacman -S docker docker-compose docker-buildx kubectl minikube helm \
  aws-cli-v2 azure-cli terraform nginx act gitlab-runner

# Section 9: Frontend
sudo pacman -S nvm

# Section 10: Editors
sudo pacman -S code neovim pycharm-community-edition

# Section 11: Terminal & Shell
sudo pacman -S zsh kitty alacritty wezterm starship tmux zellij \
  fzf ripgrep fd bat eza zoxide lazygit

# Section 12: Git
sudo pacman -S git github-cli

# Section 13-18: Apps & Productivity
sudo pacman -S firefox-developer-edition obsidian flameshot spectacle kdeconnect \
  thunderbird korganizer bitwarden keepassxc syncthing copyq okular discord \
  vlc mpv gimp inkscape libreoffice-fresh strawberry btop nvtop mission-center \
  ncdu dust pacman-contrib reflector snapper snap-pac btrfs-assistant

# AUR packages (yay/paru)
yay -S visual-studio-code-bin vscodium-bin mongodb-bin google-cloud-cli \
  brave-bin librewolf-bin mullvad-browser-bin ungoogled-chromium-bin \
  notion-app-electron logseq-desktop-bin zoom slack-desktop spotify \
  onlyoffice-bin lazydocker mullvad-vpn-bin

# Security
sudo pacman -S ufw fail2ban dnscrypt-proxy apparmor apparmor.d openssh proton-vpn-gtk-app
```

**Post-install essentials:**
```bash
sudo usermod -aG render,video,docker $USER
sudo systemctl enable --now docker.service postgresql redis ollama.service ufw fail2ban
chsh -s $(which zsh)
pipx ensurepath
```

This guide covers **every tool** in the specified stack. Prioritize Sections 1–3 first (GPU, Python, AI/ML), then build outward. With 32GB RAM and an AMD GPU running ROCm, this workstation handles local **7B–13B parameter LLMs** comfortably via Ollama or llama.cpp with quantized GGUF models, while serving as a complete backend engineering and freelance productivity environment.