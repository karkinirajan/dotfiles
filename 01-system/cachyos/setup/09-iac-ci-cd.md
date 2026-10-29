---
title: "09 Infrastructure as Code and CI/CD"
part: "01"
chapter: "09"
topic: iac-ci-cd
versions: [terraform, opentofu, ansible, pulumi, act, gitlab-runner, gha-checkout, gha-setup-uv]
last_verified: 2026-10-29
status: current
sources:
  - https://developer.hashicorp.com/terraform
  - https://opentofu.org/docs/
  - https://docs.github.com/actions
  - https://docs.gitlab.com/runner/
---

# 09 Infrastructure as Code and CI/CD

## Purpose

Provisioning tools, local CI runners and a CI workflow template that does not depend on end-of-life action runtimes.

## 9.1 Terraform

```bash
sudo pacman -S --needed terraform
# terraform init → plan → apply → destroy
```

Terraform <!-- v:terraform -->1.15.9<!-- /v --> in Arch is licensed under the Business Source License 1.1 (production use is allowed unless you offer a competing hosted or embedded product; each version converts to MPL 2.0 four years after release). Upstream is at 1.17.1, so the packaged build lags. OpenTofu (section 9.2) is the MPL-licensed alternative.

## 9.2 OpenTofu (open-source Terraform fork)

```bash
sudo pacman -S --needed opentofu
tofu -v
```

OpenTofu <!-- v:opentofu -->1.13.2<!-- /v --> (MPL 2.0; supported to 2027-08-01; 1.13 removed the WinRM provisioner connection).

## 9.3 Ansible

```bash
sudo pacman -S --needed ansible
ansible --version
```

Arch `ansible` is the community bundle (<!-- v:ansible -->14.5.0<!-- /v -->, built on ansible-core 2.21; control node needs Python 3.12 to 3.14). `ansible-core` (2.21.5) is the engine alone and `ansible-lint` is in extra. Installing it with `uv tool install ansible` only exposes `ansible-community`; use `uv tool install ansible-core` for the engine.

## 9.4 Pulumi (IaC with real programming languages)

Pulumi <!-- v:pulumi -->3.272.0<!-- /v --> in Arch (upstream 3.273.0).

```bash
sudo pacman -S --needed pulumi
pulumi new python                     # Python projects can set runtime.options.toolchain: uv
```

## 9.5 GitHub Actions local runner: act

act <!-- v:act -->0.2.89<!-- /v --> in Arch (upstream 0.2.92).

```bash
sudo pacman -S --needed act
cd /your/repo && act                  # runs .github/workflows/*.yml locally
```

`act` talks to the Docker Engine API. On rootless Docker export `DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock` first. <!-- UNVERIFIED: act with rootless Docker and node24-based actions --> Label: `machine-only`.

## 9.6 GitLab CI runner

GitLab Runner <!-- v:gitlab-runner -->19.5.1<!-- /v --> in Arch.

```bash
sudo pacman -S --needed gitlab-runner
sudo gitlab-runner register --url https://gitlab.com/ --token "$RUNNER_TOKEN"   # a glrt- runner authentication token
```

Registration tokens (the old `--registration-token` flow) are removed in GitLab 20.0; create the runner in the GitLab UI and use its `glrt-` token. Label: `machine-only`.

## 9.7 Sample GitHub Actions workflow (Python and uv)

The previous sample used `actions/checkout@v4`, `astral-sh/setup-uv@v5` and `docker/build-push-action@v5`, which run on Node 20; **Node 20 was removed from GitHub-hosted runners on 2026-09-23**. Actions are pinned by commit SHA (GitHub's hardening guidance); the comment names the release. `setup-uv` has no floating `v8` to `v10` tag, which is another reason to pin.

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
      - run: uv sync --locked
      - run: uv run ruff check .
      - run: uv run pytest

  docker:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: docker/build-push-action@c3c9e263c25d99ce0380d002d59b67737d91b0dc # v7.4.0
        with:
          push: false
          tags: myapp:latest
```

Versions: checkout <!-- v:gha-checkout -->7.0.1<!-- /v -->, setup-uv <!-- v:gha-setup-uv -->10.3.3<!-- /v -->. SHAs come from `git ls-remote --tags` on each action repository. The workflow passes `actionlint` 1.7.12 (`verified-in-cloud`, syntax only; it was not run on GitHub). Keep the pins current with Dependabot's `github-actions` ecosystem (see this repository's `.github/dependabot.yml`).

## Verify

```bash
terraform version
tofu -v
act --version
```

## Sources

- [Terraform BSL](https://www.hashicorp.com/en/bsl), [OpenTofu](https://opentofu.org/docs/), [GitLab Runner](https://docs.gitlab.com/runner/)
- [GitHub: Node 20 removal](https://github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions)
- Ledger: cluster C5, topics `Terraform`, `IaC and CI runners`, `Workflow` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
