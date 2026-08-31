---
name: redis-patterns
description: Design or debug Redis usage — cache invalidation strategy, Redis as a queue vs a real message broker, pub/sub delivery guarantees, rate limiting implementation, and whether a given piece of data is being treated as cache or as source of truth. Trigger when adding caching, building a queue/job system on Redis, implementing rate limits, or debugging stale/missing cached data.
---

Redis's biggest failure mode isn't the tool — it's ambiguity about what a given key actually is. Before writing to Redis, decide: is this disposable (cache, safe to lose, needs a TTL and a real source of truth elsewhere) or is this the record (needs the durability thinking of a real database)? Most production Redis bugs come from that line being blurry.

## Cache invalidation
- TTL-only is the default because it's simple and self-healing, but it means every cache miss window serves stale data for up to the TTL — fine for tolerant data (a public profile), wrong for anything correctness-sensitive right after a write (a user's own just-updated settings).
- Explicit invalidation (delete/update the key on write) gives correctness but couples every write path to cache-key knowledge, and it's easy to miss an invalidation site when a value is written from more than one code path. Prefer writing through a single service-layer function that owns both the DB write and the cache invalidation, not scattering `redis.delete()` calls at call sites.
- The stale-cache-vs-thundering-herd tradeoff: when a hot key expires, many concurrent requests can all miss simultaneously and hammer the DB at once. Mitigate with a short jittered TTL (avoid every key expiring in lockstep), a lock/single-flight pattern so only one request repopulates while others wait or serve stale, or serve-stale-while-revalidate (return the expired value immediately, refresh in the background).

## Redis as a queue vs a real broker
- Redis (`LPUSH`/`BRPOP`, or Streams) works for simple job queues but lacks what a real broker (SQS, RabbitMQ, Kafka) gives you by default: durable delivery guarantees on broker restart without persistence tuned correctly, per-message dead-lettering, and consumer-group semantics that survive a crashed worker without careful `XCLAIM`/`XPENDING` handling in Streams.
- A `BRPOP`-based queue loses in-flight jobs if a worker crashes after popping but before finishing — there's no ack/nack without building it yourself (move to a processing list, ack by removing, requeue on timeout). Streams with consumer groups fix this properly; a plain list does not. If jobs must never be silently dropped, don't hand-roll it on plain lists — use Streams with explicit ack, or use a real queue.

## Pub/sub — no delivery guarantee
- Redis pub/sub is fire-and-forget: a subscriber that isn't connected when a message publishes never sees it, and there's no replay, no persistence, no ack. Design around this explicitly — pub/sub is for ephemeral signals (invalidate this cache key, a live update nice-to-have), never for anything that must be delivered (use Streams, a queue, or a DB-backed outbox instead).

## Rate limiting
- Fixed window (`INCR` + `EXPIRE` per time bucket) is simple but allows up to 2x the limit at window boundaries (burst at the end of one window plus the start of the next). Sliding window (sorted set of timestamps, trim outside the window, `ZCARD` to count) is accurate but costs more memory and ops per check. Sliding window log is exact; sliding window counter (weighted average of current + previous fixed window) is the usual production compromise — cheap like fixed window, close to sliding-window accuracy.
- Always make the increment+check atomic (Lua script or `MULTI`/`EXEC`) — a check-then-increment done as two round trips race under concurrent requests and let the limit be exceeded.

## Cache vs source of truth
If losing the Redis instance (crash, eviction under memory pressure, `maxmemory-policy` reclaiming keys) would lose data the app can't reconstruct from elsewhere, it's not a cache — it needs `appendonly`/RDB persistence tuned deliberately, or it shouldn't be in Redis at all. Session data, feature flags cached from a config service, and computed aggregates are cache. Distributed locks, counters that gate real actions (e.g., inventory decrements), and anything with no other copy of the data are source-of-truth and need to be treated accordingly.
