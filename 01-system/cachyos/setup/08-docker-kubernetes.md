---
title: "08 Docker and Kubernetes"
part: "01"
chapter: "08"
topic: docker-kubernetes
versions: [docker, docker-compose, docker-buildx, docker-rootless-extras, kubectl, minikube, helm, k9s, postgresql, valkey]
last_verified: 2026-10-29
status: current
sources:
  - https://docs.docker.com/engine/security/rootless/
  - https://docs.docker.com/compose/
  - https://kubernetes.io/releases/version-skew-policy/
  - https://minikube.sigs.k8s.io/docs/
---

# 08 Docker and Kubernetes

## Purpose

Rootless Docker for local development, a Compose template for a typical Django stack, Kubernetes tooling, and a multi-stage Dockerfile.

## Prerequisites

- cgroup v2 and kernel 5.11 or newer (rootless `overlay2`); kernel <!-- v:cachyos-kernel -->7.3.0<!-- /v --> qualifies.
- At least 65536 subordinate IDs for your user: `grep "^$USER:" /etc/subuid /etc/subgid`; if there is no line, add the range with `sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 "$USER"`.

## 8.1 Docker and Compose, rootless

Docker Engine <!-- v:docker -->29.9.2<!-- /v -->, Compose <!-- v:docker-compose -->5.6.1<!-- /v -->, Buildx <!-- v:docker-buildx -->0.38.1<!-- /v -->. This workstation runs the daemon as a **user** service so the account does not need the root-equivalent `docker` group. `docker-rootless-extras` is an **AUR** package (it is in neither Arch extra nor the CachyOS repos); it depends on `docker` and `rootlesskit`.

```bash
sudo pacman -S --needed docker docker-compose docker-buildx rootlesskit
paru -S --needed docker-rootless-extras
sudo systemctl disable --now docker.service docker.socket    # make sure no rootful daemon runs
dockerd-rootless-setuptool.sh install                        # writes ~/.config/systemd/user/docker.service, creates and selects the `rootless` context
systemctl --user enable --now docker.service
sudo loginctl enable-linger "$USER"                          # optional: start at boot instead of at login
docker info | grep -E 'Context|rootless|Storage Driver|Server Version'
docker run --rm hello-world
```

Notes:

- `dockerd-rootless-setuptool.sh` selects the `rootless` context; tools that ignore contexts need `export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock`.
- Rootless networking: since Docker 29.5 the default driver is `gvisor-tap-vsock` and `slirp4netns` is no longer installed by the Docker packaging; `slirp4netns` is an optional dependency, `passt` (`pasta`) is experimental. Source-IP propagation needs RootlessKit 3.0 or newer (the repo has 3.3.0) with the userland proxy disabled.
- Ports below 1024 need `sudo setcap cap_net_bind_service=ep "$(which rootlesskit)"` and a daemon restart, or `net.ipv4.ip_unprivileged_port_start=0`. `ping` needs `net.ipv4.ping_group_range = 0 2147483647`. `--cpus` and `--memory` limits need cgroup v2 with systemd and only `memory pids` are delegated by default (extend through `/etc/systemd/system/user@.service.d/delegate.conf`).
- Fresh Docker 29 installs use the containerd image store, so check `Storage Driver` or the driver type rather than an overlay2-only field such as `Native Overlay Diff`.
- Do **not** enable the system `docker.socket`. Socket activation of the system unit starts a rootful daemon, the opposite of this setup. Restart the rootless daemon with `systemctl --user restart docker`.
- A kernel-module tweak (`options overlay metacopy=off redirect_dir=off`) appeared in an earlier version of this guide; it could not be sourced, is host-specific and is not recommended. <!-- UNVERIFIED -->
- `docker-machine` is archived upstream (2025-07-18) and is no longer in the package lists. `lazydocker` is in the repos: `sudo pacman -S lazydocker`. Podman is an alternative (`sudo pacman -S podman`); `act` does not officially support it.

Label: all of 8.1 is `machine-only`. Proof: `docker info` shows `Context: rootless` and Server Version <!-- v:docker -->29.9.2<!-- /v -->, and `hello-world` prints its greeting.

## 8.2 Docker Compose: local dev stack

The Compose file format needs no `version:` key (it is obsolete and warns). Host ports are published on loopback and shifted so they do not collide with the host's PostgreSQL (5432) and Valkey (6379). The compose blocks in this chapter parse and validate against the Compose specification schema (`verified-in-cloud`, schema only); `docker compose config` itself needs the host.

```yaml
# docker-compose.yml: Django + PostgreSQL + Valkey + Celery
services:
  db:
    image: postgres:18-alpine
    environment:
      POSTGRES_DB: myapp_db
      POSTGRES_USER: myapp_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set it in .env}
    volumes: [postgres_data:/var/lib/postgresql]   # PostgreSQL 18 images mount the parent directory
    ports: ["127.0.0.1:5433:5432"]

  valkey:
    image: valkey/valkey:9.1-alpine
    ports: ["127.0.0.1:6380:6379"]

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:9.5.5
    environment:
      discovery.type: single-node
      xpack.security.enabled: "false"       # dev only; the image enables security by default
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
    ports: ["127.0.0.1:9201:9200"]   # 9200 is the chapter 06 standalone node

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes: [".:/app"]
    ports: ["127.0.0.1:8000:8000"]
    env_file: [.env]
    depends_on: [db, valkey]

  celery_worker:
    build: .
    command: celery -A myproject worker -l info
    volumes: [".:/app"]
    env_file: [.env]
    depends_on: [db, valkey]

  celery_beat:
    build: .
    command: celery -A myproject beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes: [".:/app"]
    env_file: [.env]
    depends_on: [db, valkey]

volumes:
  postgres_data:
```

Why these choices:

- An omitted host IP in `ports:` binds **all interfaces**; `127.0.0.1:` keeps services off the LAN, matching the loopback policy of this machine.
- `postgres:18-alpine` and `valkey/valkey:9.1-alpine` are the tags used here; the Docker Hub tag list was not re-read in this research pass. <!-- UNVERIFIED: both image tags --> `redis:7` is no longer BSD licensed; Valkey is the drop-in the host already runs, and `redis-py` and Celery's Redis transport work with it.
- Elasticsearch 9.5.5 is current (8.x is in maintenance until 2027-01-15; 9.3 is end of life). It requires `vm.max_map_count` of 1048576 or more on the host (`sudo sysctl -w vm.max_map_count=1048576`, persisted with a file in `/etc/sysctl.d/`; chapter 06 shows the command). OpenSearch 3.9 is the alternative (`DISABLE_SECURITY_PLUGIN=true` for dev, `vm.max_map_count=262144`). <!-- UNVERIFIED: the exact map count Elasticsearch needs for one node -->

Label: `machine-only` except the schema validation.

## 8.3 Kubernetes tools

```bash
sudo pacman -S --needed kubectl minikube helm k9s
minikube start --driver=docker --container-runtime=containerd --memory=4096   # add --cpus=2 only after delegating the cpu controller (below)
```

- kubectl <!-- v:kubectl -->1.37.1<!-- /v --> (1.37 is supported until 2027-10-28; stay within one minor of the API server). minikube <!-- v:minikube -->1.38.1<!-- /v --> in Arch (upstream 1.39.0, default Kubernetes 1.37 and containerd runtime, a breaking change); Helm <!-- v:helm -->4.3.0<!-- /v --> (server-side apply by default, post-renderers are plugins, `--atomic` is `--rollback-on-failure`, `--force` is `--force-replace`); k9s <!-- v:k9s -->0.51.0<!-- /v -->.
- On rootless Docker, minikube also needs cgroup v2 delegation; `--cpus` only works if the cpu controller is delegated: create `/etc/systemd/system/user@.service.d/delegate.conf` with `[Service]` and `Delegate=cpu cpuset io memory pids`, run `sudo systemctl daemon-reload`, and log out and back in. `kind` (in extra) works the same way with `DOCKER_HOST` exported.
- **k3s** (`curl -sfL https://get.k3s.io | sh -`; read the script first) is still the documented install, but it listens on 6443, 10250 and 8472/udp and its docs recommend turning UFW off. That conflicts with this machine's deny-incoming policy, so prefer minikube or kind locally; the AUR `k3s` is 1.35 and flagged out of date.

| Tool | Purpose |
|---|---|
| `kubectl` | CLI for Kubernetes clusters |
| `minikube` | Local single-node cluster |
| `kind` | Clusters in containers, good for CI |
| `helm` | Kubernetes package manager |
| `k9s` | Terminal UI for cluster navigation |

Label: `machine-only`.

## 8.4 Multi-stage Dockerfile template

The uv pattern from the [uv Docker guide](https://docs.astral.sh/uv/guides/integration/docker/): dependencies are installed in a separate layer, the project is installed after, and the runtime image carries only the virtualenv. `python:3.12-slim` is valid (3.12 is security-only until 2028-10); use a 3.13 or 3.14 image for new projects.

```dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
RUN useradd -m appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Both `uv sync` flag combinations ran in a temporary project in the sandbox (`verified-in-cloud`); the Dockerfile itself needs a container runtime. `hadolint` 2.15.1 reports only the DL3066 info.

## 8.5 Container registry auth

```bash
docker login                                   # Docker Hub

# AWS ECR (the token is valid for 12 hours)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com

# GitHub Container Registry: needs a classic personal access token with
# write:packages (read:packages to pull); $GITHUB_TOKEN exists only inside Actions
echo "$CR_PAT" | docker login ghcr.io -u USERNAME --password-stdin
```

Docker stores credentials base64-encoded in `~/.docker/config.json` unless a credential helper (`pass`, `secretservice`) is configured; set one.

## Verify

```bash
docker context show
docker run --rm hello-world
kubectl version --client
```

Expected: `rootless`; the hello-world greeting; kubectl <!-- v:kubectl -->1.37.1<!-- /v -->.

## Sources

- [Docker rootless mode](https://docs.docker.com/engine/security/rootless/), [Engine 29 release notes](https://docs.docker.com/engine/release-notes/29/)
- [Kubernetes version skew policy](https://kubernetes.io/releases/version-skew-policy/), [minikube](https://minikube.sigs.k8s.io/docs/)
- Ledger: cluster C5 and C6 in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
