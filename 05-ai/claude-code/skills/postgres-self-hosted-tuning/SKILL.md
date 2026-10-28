---
name: postgres-self-hosted-tuning
description: Diagnose or tune a self-hosted (non-managed) Postgres instance, indexing decisions, reading EXPLAIN ANALYZE output, connection pooling, autovacuum, and gotchas specific to running Postgres yourself instead of on RDS/Supabase/Neon. Trigger on slow-query reports, connection-exhaustion errors, index design questions, or "why is Postgres using so much disk/CPU."
---

Managed Postgres hides a lot of ops work behind defaults. Self-hosted means you own connection limits, autovacuum, WAL, and backups, most "mystery" production incidents trace back to one of these being left at factory settings.

## Indexing
- Composite index column order: put the equality-filtered column(s) first, range/sort columns last. `WHERE tenant_id = ? AND created_at > ?` wants `(tenant_id, created_at)`, not the reverse, equality-first is still the right default. PG18 B-tree skip scan can use a multicolumn index when early columns have no or non-equality restrictions, but it only pays off for low-cardinality leading columns.
- Partial indexes beat a full index when a column is heavily skewed (e.g. `status = 'pending'` is 2% of rows but 90% of queries), `CREATE INDEX ... WHERE status = 'pending'` is smaller, cheaper to maintain, and more likely to stay in cache.
- Don't index reflexively. Every index slows every write on that table and autovacuum has to maintain it too. Low-cardinality columns (booleans, small enums) rarely benefit alone, combine into a composite or use a partial index instead. Check `pg_stat_user_indexes` for `idx_scan = 0` periodically and drop what nothing uses.
- A foreign key column needs an index for the child-side lookups and because without it every parent `DELETE` or key `UPDATE` scans the whole child table, Postgres does not auto-create this the way MySQL/InnoDB does.

## Reading EXPLAIN ANALYZE
- Seq Scan isn't inherently bad: for small tables or queries returning >~15-20% of rows, it's often correct and an index would be slower. The problem is a seq scan on a large table for a selective filter.
- The number that matters: estimated rows vs actual rows in each node. A large mismatch (planner expects 50, actual is 50,000) means stale statistics, run `ANALYZE` on the table, or lower `autovacuum_analyze_scale_factor` if this happens repeatedly on a fast-changing table. A bad row estimate cascades into a bad join plan (nested loop chosen where a hash join was needed).
- Look at the innermost/lowest nodes first: cost accumulates upward, and the actual time gap between a node and its children shows exactly where time is spent.

## Connection pooling
- Each raw Postgres connection is a full OS process (~5-10MB RAM, plus context-switch overhead). A few hundred concurrent app connections direct to Postgres degrades throughput before you hit `max_connections`. This is why app-side pool sizes must be conservative and multiplied across every service/replica hitting the same DB.
- PgBouncer transaction mode is what you want for typical web app workloads (holds the server connection only for the duration of a transaction), but it breaks session-level features: SQL-level `PREPARE`/`EXECUTE`, `SET` session variables (protocol-level prepared statements are tracked since PgBouncer 1.21.0 via `max_prepared_statements`, default 200), advisory locks held across statements, `LISTEN/NOTIFY`. Session mode preserves those but gives you no real pooling benefit. Know which one is configured, and which PgBouncer version, before debugging "prepared statement does not exist" errors.

## Autovacuum
- Default `autovacuum_vacuum_scale_factor` (20%) is tuned for small tables. On a large, high-churn table it means vacuum waits until 20% of a 10M-row table is dead tuples, way too much bloat. Lower the scale factor (or set an absolute threshold) per-table via `ALTER TABLE ... SET (autovacuum_vacuum_scale_factor = ...)`. PG18 adds `autovacuum_vacuum_max_threshold` (default 100,000,000 dead tuples), which caps the 20% trigger only on very large tables, so the 10M-row case above still needs the per-table setting.
- Long-running transactions block vacuum from reclaiming dead tuples it would otherwise clean up, an idle-in-transaction connection left open by a buggy app is a common silent cause of bloat and table growth.

## Self-hosted vs managed gotchas
- No automatic failover, PITR, or connection pooling layer unless you build it, plan backups (`pg_basebackup -D dir -Ft -z -P -X stream -c fast`, WAL archiving with `archive_mode=on` and `archive_command`, PITR with `restore_command` plus `recovery.signal` and `recovery_target_time`; incremental backups via `pg_basebackup --incremental` and `pg_combinebackup` since PG17; pgBackRest for production repositories) and monitoring (`pg_stat_activity`, bloat queries) explicitly; they don't exist by default.
- `shared_buffers`, `work_mem`, `effective_cache_size` default low for compatibility with tiny VMs (PG18: 128MB, 4MB and 4GB), start `shared_buffers` at about 25% of RAM on a dedicated server (above 40% rarely helps) and tune the others to actual instance RAM, or every sort/hash spills to disk. PG18 also adds asynchronous I/O (`io_method`, default `worker`; `io_uring` needs a build with liburing).
