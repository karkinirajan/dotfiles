---
title: "07 DevOps and Cloud Tools"
part: "01"
chapter: "07"
topic: devops-cloud-tools
versions: [aws-cli, azure-cli, nginx]
last_verified: 2026-10-29
status: current
sources:
  - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
  - https://learn.microsoft.com/cli/azure/
  - https://nginx.org/en/docs/
---

# 07 DevOps and Cloud Tools

## Purpose

Cloud CLIs and the web server used for local reverse-proxy work. Credentials never go into dotfiles; each CLI keeps them in its own store.

## 7.1 AWS CLI v2

The package is `aws-cli-v2` (<!-- v:aws-cli -->2.37.9<!-- /v --> in Arch; upstream is at 2.39.1).

```bash
sudo pacman -S --needed aws-cli-v2
aws login                      # CLI 2.32.0 or newer: browser flow, auto-refreshing credentials (up to 12 h); `aws login --remote` on a headless host
aws sts get-caller-identity
aws logout
uv tool install aws-sam-cli    # Serverless Application Model
```

Prefer `aws login` or `aws configure sso` over `aws configure` with a long-term IAM access key: AWS ranks long-term keys as "not recommended". Label: `machine-only`.

## 7.2 Azure CLI

Azure CLI <!-- v:azure-cli -->2.90.0<!-- /v --> in Arch (2.91.0 is in extra-testing).

```bash
sudo pacman -S --needed azure-cli
az login                              # opens a browser; `az login --use-device-code` on a headless host
```

Microsoft requires MFA for user identities since September 2025; use service principals or managed identities for automation. Label: `machine-only`.

## 7.3 nginx

The Arch package `nginx` is the **stable** branch (<!-- v:nginx -->1.30.6<!-- /v -->, five CVE fixes); `nginx-mainline` is 1.31.8 and Arch's dynamic modules are built against the stable package. The package installs upstream's `nginx.conf` with only `user http`, `root` and `include modules.d/*.conf` changes, has **no** `conf.d` include, and gets `mime.types` from `mailcap`.

```bash
sudo pacman -S --needed nginx
# Config: /etc/nginx/nginx.conf     Test: sudo nginx -t
# This host's MIME table needs a larger type hash. Install the tracked drop-in
# and ensure /etc/nginx/nginx.conf includes conf.d/*.conf inside http {}:
sudo install -Dm644 07-networking/nginx/conf.d/00-types-hash.conf /etc/nginx/conf.d/00-types-hash.conf
if ! sudo grep -q 'conf\.d/\*\.conf' /etc/nginx/nginx.conf; then
  sudo sed -i '/include[[:space:]]\+mime\.types;/a\    include       conf.d/*.conf;' /etc/nginx/nginx.conf
fi
sudo nginx -t
# Enable only when needed: sudo systemctl enable --now nginx
```

`types_hash_max_size` defaults to 1024 and `types_hash_bucket_size` to 64; the drop-in raises the maximum to 4096, which is what the Arch wiki's sample config uses. Label: `machine-only`. Proof: `nginx -t` reports "syntax is ok" with no `types_hash` warning. Checked on the host: the stock `/etc/nginx/nginx.conf` includes `modules.d/*.conf` and `mime.types` but not `conf.d/*.conf`, and after the drop-in `nginx -t` prints no `types_hash` warning.

Reverse-proxy hardening that applies to nginx 1.30 (the `nginx-reverse-proxy-patterns` skill carries the detail):

- `proxy_http_version` defaults to 1.1 since nginx 1.29.7 (it was 1.0); set `Connection ""` for keepalive to an upstream.
- `limit_req_status 429` (the default status is 503); behind a proxy derive the client address with `set_real_ip_from`, `real_ip_header X-Forwarded-For` and `real_ip_recursive on` instead of keying on the raw header.
- `server_tokens off`; `add_header ... always`; `add_header` is not inherited into a `location` that defines its own (`add_header_inherit merge` from 1.29.3); `http2 on;` replaces `listen ... http2`.

## Verify

```bash
aws --version
az version
nginx -v
```

Expected: aws-cli <!-- v:aws-cli -->2.37.9<!-- /v -->, azure-cli <!-- v:azure-cli -->2.90.0<!-- /v -->, nginx <!-- v:nginx -->1.30.6<!-- /v -->.

## Sources

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/), [Azure CLI](https://learn.microsoft.com/cli/azure/), [nginx documentation](https://nginx.org/en/docs/)
- Ledger: cluster C5, topics `AWS CLI`, `Nginx`, `credentials` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
