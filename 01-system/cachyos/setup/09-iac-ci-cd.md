---
title: "09 Infrastructure as Code and CI/CD"
part: "01"
chapter: "09"
topic: iac-ci-cd
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 09 Infrastructure as Code and CI/CD


## 9.1 Terraform

```bash
sudo pacman -S terraform
# terraform init → terraform plan → terraform apply → terraform destroy
```

## 9.2 OpenTofu (Open-source Terraform fork)

```bash
sudo pacman -S opentofu
tofu -v
```

## 9.3 Ansible

```bash
sudo pacman -S ansible
ansible --version
```

## 9.4 Pulumi (IaC with real programming languages)

```bash
sudo pacman -S pulumi
pulumi new python   # Create Python IaC project
```

## 9.5 GitHub Actions Local Runner — act

```bash
sudo pacman -S act
cd /your/repo && act   # Runs .github/workflows/*.yml locally
```

## 9.6 GitLab CI Runner

```bash
sudo pacman -S gitlab-runner
sudo gitlab-runner register   # Follow prompts with your GitLab token
```

## 9.7 Sample GitHub Actions (Python + uv)

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
