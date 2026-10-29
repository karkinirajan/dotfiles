### A.15 Logger and rate limiter

The logger writes JSON lines to stdout and stderr, so no `console.*` call exists in application code (OBS-01). `requestLogger()` binds the request id that `proxy.ts` sets (DAL-06); the plain `logger` is for code that runs outside a request, such as the Redis client's error event. The limiter is a fixed window on Redis. It fails open on Redis errors, and when Redis does not answer within 300 ms, so an outage neither locks users out nor slows sign-in (a Redis client left to its own retry timers delayed sign-in by several seconds during an outage). It logs every failure; for brute-force-sensitive endpoints (sign-in, OTP) switch the `catch` branch to `ok: false`.

`src/lib/logger.ts`

```ts
import 'server-only';
import { headers } from 'next/headers';

type Level = 'debug' | 'info' | 'warn' | 'error';
type Fields = Record<string, unknown>;

export interface Logger {
  debug: (fields: Fields, message: string) => void;
  info: (fields: Fields, message: string) => void;
  warn: (fields: Fields, message: string) => void;
  error: (fields: Fields, message: string) => void;
}

const LEVEL_RANK: Record<Level, number> = { debug: 10, info: 20, warn: 30, error: 40 };
const MIN_LEVEL: Level = process.env.NODE_ENV === 'production' ? 'info' : 'debug';

function write(level: Level, bound: Fields, fields: Fields, message: string): void {
  if (LEVEL_RANK[level] < LEVEL_RANK[MIN_LEVEL]) return;
  const line = JSON.stringify({
    level,
    time: new Date().toISOString(),
    message,
    ...bound,
    ...fields,
  });
  // stdout/stderr directly: structured, no console.* in application code.
  (level === 'error' || level === 'warn' ? process.stderr : process.stdout).write(`${line}\n`);
}

function create(bound: Fields): Logger {
  return {
    debug: (fields, message) => {
      write('debug', bound, fields, message);
    },
    info: (fields, message) => {
      write('info', bound, fields, message);
    },
    warn: (fields, message) => {
      write('warn', bound, fields, message);
    },
    error: (fields, message) => {
      write('error', bound, fields, message);
    },
  };
}

/** For code that runs outside a request (startup, the Redis client's error event). */
export const logger: Logger = create({});

/**
 * A logger that stamps every line with the request id the proxy set (DAL-06).
 * Call it inside a request: a Server Action, a route handler, or a DAL function.
 */
export async function requestLogger(): Promise<Logger> {
  const requestId = (await headers()).get('x-request-id');
  return create(requestId ? { requestId } : {});
}
```

`src/lib/rate-limit.ts`

```ts
import 'server-only';
import Redis from 'ioredis';
import { serverEnv } from '@/lib/env/server';
import { logger, requestLogger } from '@/lib/logger';

export type RateLimitInput = Readonly<{ key: string; limit: number; windowSeconds: number }>;
export type RateLimitResult = Readonly<{
  ok: boolean;
  remaining: number;
  retryAfterSeconds: number;
}>;

/** Longest a request waits on the limiter before it fails open. Keeps sign-in fast during a Redis outage. */
const LIMITER_TIMEOUT_MS = 300;

function createRedis(): Redis {
  const client = new Redis(serverEnv.REDIS_URL, { maxRetriesPerRequest: 1, lazyConnect: true });
  client.on('error', (error: Error) => {
    logger.error({ err: error.message }, 'redis connection error');
  });
  return client;
}

const globalForRedis = globalThis as unknown as { redis?: Redis };
const redis = globalForRedis.redis ?? createRedis();
if (serverEnv.NODE_ENV !== 'production') globalForRedis.redis = redis;

function withTimeout<T>(work: Promise<T>, ms: number): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`rate limiter timed out after ${String(ms)} ms`));
    }, ms);
    work.then(resolve, reject).finally(() => {
      clearTimeout(timer);
    });
  });
}

/** Fixed-window limiter. Fails open on Redis errors and timeouts for availability; the failure is logged. */
export async function rateLimit({
  key,
  limit,
  windowSeconds,
}: RateLimitInput): Promise<RateLimitResult> {
  const consume = async (): Promise<RateLimitResult> => {
    const bucket = `rl:${key}`;
    const count = await redis.incr(bucket);
    if (count === 1) await redis.expire(bucket, windowSeconds);
    const ttl = await redis.ttl(bucket);
    return {
      ok: count <= limit,
      remaining: Math.max(0, limit - count),
      retryAfterSeconds: Math.max(ttl, 1),
    };
  };
  try {
    return await withTimeout(consume(), LIMITER_TIMEOUT_MS);
  } catch (error) {
    (await requestLogger()).error(
      { err: error instanceof Error ? error.message : 'unknown', key },
      'rate limiter unavailable',
    );
    return { ok: true, remaining: limit, retryAfterSeconds: 0 };
  }
}
```

`src/lib/rate-limit.test.ts`

```ts
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { incr, expire, ttl, on, error } = vi.hoisted(() => ({
  incr: vi.fn(),
  expire: vi.fn(),
  ttl: vi.fn(),
  on: vi.fn(),
  error: vi.fn(),
}));

vi.mock('ioredis', () => ({
  default: class {
    incr = incr;
    expire = expire;
    ttl = ttl;
    on = on;
  },
}));
vi.mock('@/lib/logger', () => {
  const log = { info: vi.fn(), warn: vi.fn(), error };
  return { logger: log, requestLogger: () => Promise.resolve(log) };
});

import { rateLimit } from '@/lib/rate-limit';

// Recorded at import time; beforeEach clears the mocks.
const registeredErrorHandler = on.mock.calls.some(([event]) => event === 'error');

const input = { key: 'sign-in:ip:203.0.113.9', limit: 3, windowSeconds: 60 };

describe('rateLimit', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    expire.mockResolvedValue(1);
    ttl.mockResolvedValue(42);
  });

  it('starts the window on the first hit and allows it', async () => {
    incr.mockResolvedValue(1);
    await expect(rateLimit(input)).resolves.toEqual({
      ok: true,
      remaining: 2,
      retryAfterSeconds: 42,
    });
    expect(expire).toHaveBeenCalledWith('rl:sign-in:ip:203.0.113.9', 60);
  });

  it('allows the last hit in the window and rejects the next one', async () => {
    incr.mockResolvedValueOnce(3).mockResolvedValueOnce(4);
    await expect(rateLimit(input)).resolves.toMatchObject({ ok: true, remaining: 0 });
    await expect(rateLimit(input)).resolves.toMatchObject({
      ok: false,
      remaining: 0,
      retryAfterSeconds: 42,
    });
    expect(expire).not.toHaveBeenCalled();
  });

  it('fails open and logs when Redis errors', async () => {
    incr.mockRejectedValue(new Error('ECONNREFUSED'));
    await expect(rateLimit(input)).resolves.toEqual({
      ok: true,
      remaining: 3,
      retryAfterSeconds: 0,
    });
    expect(error).toHaveBeenCalledWith(
      expect.objectContaining({ err: 'ECONNREFUSED' }),
      'rate limiter unavailable',
    );
  });

  it('fails open quickly when Redis hangs', async () => {
    vi.useFakeTimers();
    try {
      incr.mockReturnValue(new Promise(() => undefined));
      const pending = rateLimit(input);
      await vi.advanceTimersByTimeAsync(300);
      await expect(pending).resolves.toMatchObject({ ok: true, retryAfterSeconds: 0 });
      expect(error).toHaveBeenCalledWith(
        expect.objectContaining({ err: expect.stringContaining('timed out') as string }),
        'rate limiter unavailable',
      );
    } finally {
      vi.useRealTimers();
    }
  });

  it('logs connection errors instead of leaving them unhandled', () => {
    expect(registeredErrorHandler).toBe(true);
  });
});
```
