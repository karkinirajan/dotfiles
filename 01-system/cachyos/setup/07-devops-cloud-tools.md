---
title: "07 DevOps and Cloud Tools"
part: "01"
chapter: "07"
topic: devops-cloud-tools
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 07 DevOps and Cloud Tools


## 7.1 AWS CLI v2

```bash
sudo pacman -S aws-cli-v2
aws configure   # Enter: Access Key, Secret Key, region, output format

uv tool install aws-sam-cli   # Serverless Application Model
```

## 7.2 Azure CLI

```bash
sudo pacman -S azure-cli
az login   # Opens browser for interactive auth
```

## 7.3 Nginx

```bash
sudo pacman -S nginx
# Config:    /etc/nginx/nginx.conf
# Test:      sudo nginx -t
# This host's MIME table needs a larger type hash. Install the tracked drop-in
# and ensure /etc/nginx/nginx.conf includes conf.d/*.conf inside http {}:
sudo install -Dm644 07-networking/nginx/conf.d/00-types-hash.conf /etc/nginx/conf.d/00-types-hash.conf
if ! sudo grep -q 'conf\.d/\*\.conf' /etc/nginx/nginx.conf; then
  sudo sed -i '/include[[:space:]]\+mime\.types;/a\    include       conf.d/*.conf;' /etc/nginx/nginx.conf
fi
sudo nginx -t
# Enable only when needed: sudo systemctl enable --now nginx
```
