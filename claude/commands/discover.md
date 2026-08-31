---
description: Map an unfamiliar project's stack and architecture before making changes
---

Do a discovery pass on the current project before any implementation work. This is read-only — do not modify anything during this command.

Inspect what's actually present (skip sections that don't apply to this project rather than forcing a fit):

**Repository**: directory structure, README, package/dependency files, `.env.example`, Docker config, CI/CD config, recent `git log` and current branch state.

**Frontend** (if present): framework and version, routing approach, how state is managed, API client pattern, auth flow, styling/theme system, existing design tokens.

**Backend** (if present): framework, route/controller/service/repository layering (or however this project actually organizes it — don't assume a layer exists), auth/authz approach, background jobs, streaming/WebSocket usage, error-handling convention.

**Database** (if present): schema/models, migration tool and history, key relationships and indexes, which ORM/query patterns are actually used in practice (not just how models are declared).

**Infrastructure**: Docker setup, deployment target (Vercel/Railway/AWS/other), reverse proxy config, how secrets/env vars are managed, CI/CD pipeline steps.

**Tests**: what test types exist, how to run them, current coverage posture, any tests that are skipped/xfailed and why if discoverable.

Report back concisely: the stack, the conventions Claude should follow (naming, layering, where new code of each kind belongs), and anything that looks broken, duplicated, or inconsistent worth flagging before touching it. Don't create `/docs` files unless the project is substantial enough that a persistent architecture note would materially help future work — ask first if unsure.
