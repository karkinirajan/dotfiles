---
name: database-migration-discipline
description: Plan or review a schema migration on a live production database — zero-downtime patterns, NOT NULL additions on populated tables, testing against production-scale data, rollback planning, and migration ordering when multiple services share a database. Trigger before running any migration against a production or production-like database, or when reviewing a migration file for safety.
---

A migration that runs without erroring is not the same as a migration that's safe. The failure modes that matter show up under production load and production data volume, not on an empty local dev DB.

## Zero-downtime pattern: expand-contract
For any breaking column/table change, split into phases deployed separately so old and new code can both run against the schema mid-rollout:
1. **Expand** — add the new column/table alongside the old one, nullable, no constraint yet.
2. **Backfill** — populate the new column in batches (not one giant `UPDATE` — locks the table and blows up WAL/binlog/replication lag). Dual-write from application code so new rows land in both old and new during the transition.
3. **Migrate reads** — cut application code over to the new column, deployed and verified before touching the old one.
4. **Contract** — drop the old column/constraint only after confirming nothing reads it (check application code, other services, reporting queries, ORM-generated SQL — not just the obvious call sites).
This applies across Postgres, MySQL, and Mongo alike; Mongo's version of "expand" is simply writing the new field while tolerating its absence in older documents, since there's no schema to alter, but the same backfill/cutover/cleanup discipline still applies or you end up with three document shapes in production forever.

## The NOT NULL-on-populated-table trap
Adding `NOT NULL` directly on a populated table fails immediately if any existing row is null, and even when it doesn't fail, older Postgres versions take an `ACCESS EXCLUSIVE` lock for the full table scan validating the constraint (Postgres 12+ can skip the scan if a valid `CHECK (col IS NOT NULL)` already exists — add that first, validate it separately with `NOT VALID` + `VALIDATE CONSTRAINT`, then the `NOT NULL` add is instant). MySQL's `ALTER TABLE` behavior varies by version/engine on whether it's an instant, in-place, or full-copy operation — check `ALGORITHM=INSTANT` support before assuming it's cheap. Never add `NOT NULL` without a default or a backfill step confirmed complete first.

## Test against production-scale data before running for real
A migration that takes 200ms on a 500-row dev table can take 40 minutes and hold a lock the whole time on a 50M-row production table. Before running for real: check the row count and table size in production, estimate lock duration (a full table rewrite — adding a column with a non-null default pre-PG11, adding certain constraints, most MySQL `ALGORITHM=COPY` operations — locks for the duration), and if it's non-trivial, test against a production-scale copy (a recent snapshot/replica, not a synthetic dataset that misses real skew) or use an online schema-change tool (`pt-online-schema-change`/`gh-ost` for MySQL, `pg_repack` for Postgres bloat-heavy rewrites).

## Rollback planning
Every migration needs an explicit answer to "how do we undo this," not an assumed one. Additive changes (new nullable column, new table, new index) are cheaply reversible. Some migrations genuinely cannot roll back without data loss — a dropped column, a destructive data transformation, a `NOT NULL`/type-narrowing change applied to already-transformed data. For those: say so explicitly before running, take a backup or snapshot immediately before, and treat "roll forward with a fix" as the real recovery plan rather than pretending a `down` migration script makes it safe.

## Migration ordering across services sharing a database
When multiple services/deployables read the same database, a migration and the code that depends on it can't deploy atomically together — there's always a window where old code, new code, or both run against the schema simultaneously. Order changes so every intermediate state is valid for whichever code version might be running: additive changes before the code that uses them, removal only after every consumer is confirmed off the old shape. Coordinate migration order explicitly across services rather than assuming one team's deploy schedule matches another's.
