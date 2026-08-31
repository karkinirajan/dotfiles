---
name: docker-multi-stage-optimization
description: Use when writing or reviewing a multi-stage Dockerfile for build speed, final image size, multi-arch targets, or secrets handling during build. Trigger on requests to optimize a Dockerfile, fix slow rebuilds, shrink an image, add multi-arch support, or when a build ARG/secret is at risk of landing in an image layer.
---

Assumes BuildKit is already the default builder (it is on this machine) — these patterns depend on it.

## Layer caching order — the single biggest build-speed win
- Copy dependency manifests (`package.json`+lockfile, `requirements.txt`/`pyproject.toml`+lock, `go.mod`) and run install *before* copying the rest of the source. Docker caches each layer by its inputs; if source code is copied first, any source change invalidates the cache for the install step too, and every build reinstalls the entire dependency tree.
- Order matters within this too: copy the lockfile before the manifest-that-generates-it is irrelevant, but copy files that change least often first, most often last. `.dockerignore` needs `node_modules`, `.git`, `__pycache__`, `.venv` excluded or COPY invalidates cache on files that shouldn't even be in the build context.
- For monorepos, copy only the specific package's manifest first if the build tool supports partial installs — copying the whole repo's lockfile means any unrelated package's dependency bump invalidates every image's cache.

## Final image size and runtime-stage discipline
- The `builder` stage can be as fat as needed (full SDK, compilers, dev headers) — it's discarded. Only the final stage's size matters.
- Alpine trims size but musl libc breaks some compiled Python/Node native deps (silently different behavior, not just missing packages) — verify native deps (bcrypt, sharp, psycopg2 non-binary, etc.) actually work on Alpine before committing to it; `slim` (Debian-based) is often the safer default for Python/Node apps with native extensions.
- Distroless (`gcr.io/distroless/*`) is smaller and reduces attack surface further but has no shell — breaks `docker exec sh` debugging and any entrypoint script that isn't a compiled binary. Use it only when the team is comfortable debugging without a shell, or add a debug variant tag for troubleshooting.
- Final stage should only contain: the runtime (interpreter/JRE/etc.), the installed dependencies copied from the builder (`COPY --from=builder`), and the app code — never build tools, test dependencies, or dev-only packages. Split `requirements.txt` into prod/dev, or use `npm ci --omit=dev`.
- Run as a non-root user in the final stage (`USER app`) — a container running as root that gets compromised has root on anything the container escapes to.

## Multi-arch builds
- Only matters when the build machine's architecture differs from the deploy target — e.g., building on Apple Silicon (arm64) for an x86_64 EC2/Railway target, or explicitly supporting both for a client whose infra you don't control.
- `docker buildx build --platform linux/amd64,linux/arm64` — but any stage using arch-specific binaries (not multi-arch base images) breaks silently on the non-native arch; test the actual target, don't assume `--platform` alone guarantees a working image.
- If deploying to a single known target (most freelance client deploys — a specific EC2 instance type, a specific Railway region), skip multi-arch entirely; it adds build time and complexity for a portability guarantee nobody's using.

## Secrets in build args — never
- `ARG`/`ENV` values are baked into image layer history and readable via `docker history` even if a later layer overwrites or deletes the file — this includes `--build-arg` values passed on the CLI.
- Use BuildKit secret mounts instead: `RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm install`, invoked with `docker build --secret id=npmrc,src=.npmrc`. The secret is available only during that RUN step and never persists in a layer.
- Same applies to SSH keys for private repo access during build: `--mount=type=ssh` with `docker build --ssh default`, not copying a key file into the build context.
