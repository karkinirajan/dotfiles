---
title: "08 Docker and Kubernetes"
part: "01"
chapter: "08"
topic: docker-kubernetes
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 08 Docker and Kubernetes


## 8.1 Docker + Docker Compose (Rootless)

This workstation runs rootless Docker via `docker-rootless-extras` so the user
account does not need the root-equivalent `docker` group:

```bash
sudo pacman -S docker docker-compose docker-buildx rootlesskit slirp4netns
paru -S docker-rootless-extras
systemctl --user enable --now docker.service
docker context use rootless
docker run --rm hello-world   # Verify
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

## 8.2 Docker Compose — Local Dev Stack

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

## 8.3 Kubernetes Tools

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

## 8.4 Multi-Stage Dockerfile Template

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

## 8.5 Container Registry Auth

```bash
docker login   # Docker Hub

# AWS ECR:
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com

# GitHub Container Registry:
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```
