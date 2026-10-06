---
name: mysql-patterns
description: Handle MySQL/InnoDB-specific design and debugging that differs meaningfully from Postgres — indexing on a clustered-index engine, the REPEATABLE READ isolation default, replication lag in application logic, and Postgres-to-MySQL migration gotchas. Trigger when working in a MySQL/MariaDB codebase, migrating between MySQL and Postgres, or debugging inconsistent reads/locking that don't match Postgres intuition.
---

Engineers who default to Postgres carry assumptions into MySQL that are quietly wrong. InnoDB's storage model and default isolation level are the two biggest sources of surprise bugs.

## Indexing — the clustered index difference
- InnoDB stores the table itself ordered by the primary key (clustered index) — every secondary index stores the PK value, not a row pointer, and every secondary-index lookup does a second lookup back into the clustered index to fetch the row ("bookmark lookup"). This makes PK choice a performance decision, not just an identity decision.
- A large or random PK (UUID v4) causes constant page splits and fragmentation as inserts land all over the B-tree, and it bloats every secondary index since they all carry a copy of the PK. Prefer an auto-increment PK, or a sequential/sortable ID (UUIDv7, ULID) if you need global uniqueness without a central sequence.
- Covering indexes matter more here than in Postgres: a secondary index that includes every column the query needs avoids the clustered-index lookup entirely. Check `EXPLAIN` for `Using index` (covered) vs `Using where` plus a row lookup.

## The isolation-level trap
- MySQL/InnoDB defaults to `REPEATABLE READ`; Postgres defaults to `READ COMMITTED`. Code written and tested against Postgres, then pointed at MySQL, can behave differently under concurrent writes — a transaction's snapshot is fixed at first read/write, not per-statement, so a value read early in a long transaction won't reflect a concurrent commit the way it would under Postgres's default.
- `REPEATABLE READ` in InnoDB uses gap locks on range scans (e.g., `WHERE id BETWEEN`), which can produce deadlocks or blocking that would never happen under Postgres MVCC for the equivalent query. If you're seeing deadlocks on what looks like non-conflicting rows, check for gap-lock contention, not just row-lock contention.
- Don't "fix" this by dropping to `READ COMMITTED` without checking what relies on repeatable-read semantics elsewhere (report generation, multi-step batch jobs) — verify, don't just match Postgres by habit.

## Replication lag
- MySQL async/semi-sync replication means a read against a replica right after a write on the primary can return stale data — this is an application-level problem, not a database bug. Common fixes: read-your-writes by routing the immediate post-write read to the primary, or sticky sessions to primary for a short window after a write, or checking replica lag (`SHOW REPLICA STATUS`, `Seconds_Behind_Source`) before trusting a replica read in a critical path.
- Don't assume Postgres streaming replication is meaningfully different in this regard — the same read-after-write hazard applies there too if you're reading from a replica.

## Migrating between MySQL and Postgres
- Implicit type coercion: MySQL is forgiving about comparing strings to numbers, truncating on overflow (in non-strict mode), and silently converting invalid dates to zero-dates. Postgres errors on all of this. Audit for code that relied on MySQL's leniency before cutting over.
- `AUTO_INCREMENT` → `SERIAL`/`IDENTITY`, `ENUM` columns → Postgres enum types or check constraints (MySQL enums are ordinal and reorderable in ways Postgres enums aren't), `UNSIGNED` integers have no Postgres equivalent — plan the column width up front.
- Case-insensitive comparison and default collation behavior differ; string equality that worked accidentally on MySQL's default collation can break on Postgres's C/UTF8 default.

## When MySQL is genuinely the better call
Simple read-heavy web/CMS workloads with well-understood replication topology, teams already deep in the MySQL/InnoDB operational playbook, or hosting environments (shared/cheap managed hosting) where MySQL tooling is more mature — don't rewrite a working MySQL system into Postgres on aesthetic grounds alone.
