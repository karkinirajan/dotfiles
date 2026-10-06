---
name: nginx-reverse-proxy-patterns
description: Use when writing or debugging an Nginx reverse proxy config — SSE/WebSocket streaming that hangs or buffers, rate limiting, TLS termination, or cache headers for a proxied app. Trigger on requests to configure a `server`/`location` block, diagnose "streaming works locally but not behind Nginx," or add rate limiting/TLS in front of an app server.
---

Nginx defaults are tuned for static-file serving and quietly sabotage anything that streams or holds a long-lived connection. When a client reports "SSE works in dev, hangs/buffers in prod," check the proxy config before touching app code — this is almost always the cause.

## SSE proxying — the exact settings that break it silently
- `proxy_buffering off;` on the SSE `location` block. Without it, Nginx buffers the upstream response and the client gets nothing until the buffer fills or the connection closes — looks like the stream "isn't streaming" even though the app is emitting chunks correctly.
- `proxy_http_version 1.1;` — HTTP/1.0 (Nginx's default upstream version) doesn't support chunked transfer the same way; without this, keepalive to upstream breaks and connections get recycled mid-stream.
- `proxy_set_header Connection '';` — clear the `Connection` header when proxying to HTTP/1.1 upstream, otherwise Nginx forwards `close` from the client and upstream may terminate the stream early.
- `chunked_transfer_encoding on;` and set `X-Accel-Buffering: no` as a response header from the app itself — some Nginx versions/setups need the app to explicitly opt out of buffering, config alone isn't always enough.
- `proxy_read_timeout` — bump well past default 60s for anything long-lived (LLM streaming responses, SSE that idles between events), or Nginx kills the connection mid-response with no error surfaced to the app.

## WebSocket proxying
- `proxy_set_header Upgrade $http_upgrade;` and `proxy_set_header Connection "upgrade";` — both required, and the second one CANNOT be a static string if you also proxy non-upgrade requests on the same location; use the `map $http_upgrade $connection_upgrade` idiom (maps to `upgrade` or `close`) so non-WS requests on a shared location don't break.
- `proxy_http_version 1.1;` is required here too — WebSocket upgrade doesn't work over 1.0.

## Rate limiting
- Define the zone (`limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;`) in the `http` block, apply with `limit_req zone=api burst=20 nodelay;` at the location. `binary_remote_addr` not `$remote_addr` — smaller memory footprint per tracked IP.
- Behind a load balancer/CDN, `$remote_addr` is the LB's IP, not the client's — every request lands in the same bucket. Use `$http_x_forwarded_for` (first IP) or the real-IP module, and confirm the upstream (Cloudflare, ALB) is actually setting that header before trusting it.
- `nodelay` vs default: without it, requests over the rate but within `burst` get queued/delayed rather than serviced immediately — fine for background jobs, wrong for interactive API traffic.

## TLS termination
- Terminate at Nginx, proxy plaintext to upstream on localhost/private network only — never expose the app's own HTTP port externally.
- Redirect HTTP→HTTPS in a separate `server` block on port 80, don't try to branch on scheme inside one block.
- Set `proxy_set_header X-Forwarded-Proto $scheme;` — apps behind TLS-terminating proxies need this to generate correct redirect URLs and know the original request was HTTPS (Django/FastAPI secure-cookie logic depends on it).

## Cache headers
- Static assets (hashed filenames from a build): `expires 1y; add_header Cache-Control "public, immutable";` — safe because the filename changes on content change.
- API responses: explicit `Cache-Control: no-store` (or app-set headers passed through, don't override with `proxy_hide_header` unless intentional) — Nginx won't cache dynamic responses by default, but a misconfigured `proxy_cache` block or an overly broad `expires` directive at the server level can leak stale API data to a CDN in front of it.
