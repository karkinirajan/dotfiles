# 07.1 · Nginx

Local reverse-proxy tuning for CachyOS/Arch Linux (`nginx`).

```
07-networking/nginx/
├── README.md
└── conf.d/
    └── 00-types-hash.conf    → /etc/nginx/conf.d/00-types-hash.conf (copied via sudo)
```

## Why `00-types-hash.conf` exists

The MIME table shipped by the Arch/CachyOS `mailcap`/`nginx` packages exceeds
Nginx's default `types_hash_max_size` (`1024`), causing `nginx -t` and service
reloads to emit:

```text
nginx: [warn] could not build optimal types_hash, you should increase either types_hash_max_size: 1024 or types_hash_bucket_size: 64; ignoring types_hash_bucket_size
```

Setting `types_hash_max_size 4096;` inside the `http` block resolves the
warning.

## Install

Stock Arch/CachyOS `/etc/nginx/nginx.conf` does **not** include `conf.d/*.conf`
by default. Install the drop-in and ensure `/etc/nginx/nginx.conf` includes
`conf.d/*.conf` inside its `http { ... }` block:

```bash
sudo install -Dm644 07-networking/nginx/conf.d/00-types-hash.conf \
  /etc/nginx/conf.d/00-types-hash.conf

# Ensure `include conf.d/*.conf;` is present inside the `http {` block of /etc/nginx/nginx.conf:
if ! sudo grep -q 'conf\.d/\*\.conf' /etc/nginx/nginx.conf; then
  sudo sed -i '/include[[:space:]]\+mime\.types;/a\    include       conf.d/*.conf;' /etc/nginx/nginx.conf
fi

sudo nginx -t
```

On this workstation `nginx.service` is installed for local reverse-proxy testing
but left disabled by default (`sudo systemctl enable --now nginx` only when
needed).
