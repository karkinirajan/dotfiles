---
title: "06 Databases"
part: "01"
chapter: "06"
topic: databases
versions: [postgresql, pgvector, mariadb-lts, mongodb, mongosh, valkey, sqlite, dbeaver]
last_verified: 2026-10-29
status: current
sources:
  - https://www.postgresql.org/docs/18/
  - https://mariadb.org/about/
  - https://www.mongodb.com/docs/manual/release-notes/
  - https://valkey.io/download/
---

# 06 Databases

## Purpose

Local development databases. Every service binds to loopback only; none of them needs a public listener. Data directories start empty: no production data or backup lives in this repository.

## Prerequisites

- UFW with deny-incoming ([chapter 19](19-security-privacy.md)). Initializing a database is a deliberate step, not a side effect of installing the package.
- The ordered, host-level procedure (including verification) is in [`../dev-stack.md`](../dev-stack.md).

## 6.1 PostgreSQL

PostgreSQL <!-- v:postgresql -->18.6<!-- /v --> (PG18 GA 2025-09-25, supported until 2030-11-14; PG19 is a release candidate). `initdb` must run before the service starts, and **its default authentication method is `trust`**, so always pass the two auth flags: they give peer authentication on the socket and SCRAM over TCP. In PostgreSQL 18 `--data-checksums` is already the default (use `--no-data-checksums` to opt out); keeping the flag is explicit and avoids a mismatch with an older cluster when you `pg_upgrade`.

Run these as your normal user from the repository root (`cd ~/dotfiles`), not as root: `$USER` becomes the database role. Blank machine only; `initdb` refuses a non-empty data directory, and an existing cluster must not be re-initialized.

```bash
sudo pacman -S --needed postgresql pgvector
sudo install -d -o postgres -g postgres -m 700 /var/lib/postgres/data
sudo -u postgres initdb --locale=C.UTF-8 -E UTF8 \
  -D /var/lib/postgres/data --data-checksums \
  --auth-local=peer --auth-host=scram-sha-256
sudo systemctl enable --now postgresql

# Dev role and database named after your Unix user (peer auth, no password to store):
sudo -u postgres createuser --createdb "$USER"
sudo -u postgres createdb -O "$USER" dev
sudo -u postgres psql -d dev -c 'CREATE EXTENSION vector'
```

Label: the `initdb` flags were run on PostgreSQL 16 in the sandbox (accepted, resulting `pg_hba.conf` has `local all all peer` and `scram-sha-256` for 127.0.0.1 and ::1, `data_checksums = on`, locale `C.UTF-8`); PostgreSQL 18 itself was not available there, so the full sequence is `machine-only`. `listen_addresses` defaults to `localhost`.

Good to know on 18: asynchronous I/O (`io_method` = `worker` by default; `io_uring` and `sync` exist), B-tree skip scan, `uuidv7()`, OAuth authentication, `EXPLAIN ANALYZE` showing buffers by default. Major upgrade on Arch uses `postgresql-old-upgrade` (installs `/opt/pgsql-17/bin`) with the same `initdb` flags; a cluster with the `vector` extension may need `pg_dumpall` instead because that package carries no pgvector. <!-- UNVERIFIED: Arch upgrade procedure and the pgvector caveat; not run -->

**pgvector** <!-- v:pgvector -->0.8.7<!-- /v --> (supports PostgreSQL 13 to 18): run `CREATE EXTENSION vector;` once per database. HNSW defaults `m=16`, `ef_construction=64`, `hnsw.ef_search=40`; IVFFlat `lists` about rows/1000 up to a million rows, `ivfflat.probes=1`; `halfvec` indexes up to 4000 dimensions. The index builds ran against pgvector 0.6.2 in the sandbox; `halfvec` and binary quantization were not run. In Python prefer Psycopg 3: `uv add pgvector 'psycopg[binary]'`.

## 6.2 MariaDB (MySQL-compatible)

Arch `mariadb` is **13.0**, a *rolling* release whose Community support ends in Q4 2026 (13.1 is rolling too). For a stable development server use the long-term series **`mariadb-lts`** (<!-- v:mariadb-lts -->12.3.3<!-- /v -->, supported until 2029-06-12). The two packages conflict. Switching is dump-free on an empty data directory; a 13.0 data directory cannot be downgraded to 12.3.

Blank machine only. The commands are chained so MariaDB never starts without the loopback drop-in; if the data directory already holds a database, do not run `mariadb-install-db`, and never answer `y` to a "`mariadb-lts` and `mariadb` are in conflict, remove?" prompt:

```bash
sudo pacman -S --needed mariadb-lts &&
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql &&
sudo install -Dm644 "$HOME/dotfiles/01-system/cachyos/mariadb-local.cnf" /etc/my.cnf.d/90-local-dev.cnf &&
sudo systemctl enable --now mariadb
```

`mariadb-local.cnf` sets `bind-address = 127.0.0.1`; MariaDB's own default is every interface. Option files must end in `.cnf` and are read in byte order, so `90-local-dev.cnf` loads before `server.cnf` (fine unless that file sets `bind-address`). Create a database and the matching Unix-socket user (root and the install user already use socket authentication):

```bash
sudo mariadb -e "CREATE DATABASE dev; CREATE USER '$USER'@'localhost' IDENTIFIED VIA unix_socket; GRANT ALL ON dev.* TO '$USER'@'localhost';"
mariadb --protocol=socket dev -e 'select database(), current_user()'
```

Binary names: `mariadb`, `mariadbd`, `mariadb-install-db`, `mariadb-admin` are canonical; the `mysql*` names are symlinks. Label: option-file precedence, the bind drop-in, `mariadb-install-db` flags and the socket-auth user were run on MariaDB 10.11.14 in the sandbox (`verified-in-cloud`); MariaDB 12.3 and 13.0 themselves were not.

## 6.3 MongoDB

MongoDB is licensed SSPL, so it is **AUR-only** (`mongodb-bin`, <!-- v:mongodb -->8.3.9<!-- /v -->; building the `mongodb` source package takes hours). The current major is **9.0** (GA 2026-09-28, supported until 2031-10-31); 8.3 is a minor release (supported until 2029-10-31). Versions 8.3.0 to 8.3.12 are inside the critical advisory SERVER-131805 (a cross-database `renameCollection` participant can drop the target after a stepdown; fixed in 8.3.13). The AUR binary is still 8.3.9 and the 8.3.13 source package is a Bazel build, so on this single-node, loopback-only dev instance (no replica set, so no stepdown) the practical exposure is low; move to 8.3.13 or 9.x when an AUR binary exists.

```bash
paru -S --needed mongodb-bin       # depends on mongosh-bin; optional mongodb-tools
systemctl list-unit-files --no-legend | rg 'mongo(d|db)\.service'   # confirm the unit name before enabling
sudo systemctl enable --now mongodb
mongosh --quiet --eval 'db.runCommand({ping:1})'
```

The AUR package uses `mongodb.service` and `/etc/mongodb.conf` (`bindIp: 127.0.0.1`; the default `net.bindIp` is `localhost`); upstream packages use `mongod.service` and `/etc/mongod.conf`. Checked with `pacman -Ql mongodb-bin` on the host: the package ships `/usr/lib/systemd/system/mongodb.service` and `/etc/mongodb.conf`. Authentication is off, which is acceptable only while the instance stays on loopback behind UFW; to turn it on create an admin user in `admin`, set `security.authorization: enabled`, restart, and connect with `mongosh -u USER -p --authenticationDatabase admin`. <!-- UNVERIFIED: exact steps, only the overview page was readable -->

> **CachyOS note:** if MongoDB fails to start with `Permission denied`, the data directory is owned by root. Create a systemd override that fixes it on every start; the `+` prefix runs the command as root regardless of the service user:
>
> ```bash
> sudo mkdir -p /etc/systemd/system/mongodb.service.d/
> sudo tee /etc/systemd/system/mongodb.service.d/fix-permissions.conf <<'EOF2'
> [Service]
> ExecStartPre=+/bin/chown -R mongodb:mongodb /var/lib/mongodb /var/log/mongodb
> EOF2
> sudo systemctl daemon-reload && sudo systemctl restart mongodb
> ```
>
> The drop-in assumes a `mongodb` user and group exist (`id mongodb`). <!-- UNVERIFIED: the permission problem and this fix are recorded from this host only -->

mongosh is <!-- v:mongosh -->2.14.0<!-- /v -->.

## 6.4 Valkey (Redis-compatible)

Arch replaced Redis with Valkey in `extra` (news of 2025-04-17); Redis itself is AUR-only and is no longer BSD licensed (7.4 to 7.8 RSALv2/SSPLv1, 8.x also AGPLv3).

```bash
sudo pacman -S --needed valkey
sudo systemctl enable --now valkey.service
valkey-cli ping   # PONG
```

Valkey <!-- v:valkey -->9.1.2<!-- /v --> (upstream 9.1.3). The package provides the `redis-*` names as well, units `valkey.service` and `redis.service`, and `/etc/valkey/valkey.conf`. Shipped defaults: `bind 127.0.0.1 -::1`, `protected-mode yes`, port 6379, `appendonly no`. It speaks the Redis 7.2 wire protocol; `redis-py` and `valkey-py` both work (checked against `redis-server` 7.0 in the sandbox; no Valkey server was available there).

## 6.5 Elasticsearch (Docker)

Elasticsearch 9.5.5 is current; 8.x is in maintenance until 2027-01-15 and 9.3 is end of life. Security is on by default in the image (a generated `elastic` password, an enrollment token and HTTPS); the command below turns it off for a throwaway local node, so publish on loopback only. Elastic requires `vm.max_map_count` of at least 1048576 on the host (OpenSearch documents 262144).

```bash
sudo sysctl -w vm.max_map_count=1048576
echo 'vm.max_map_count = 1048576' | sudo tee /etc/sysctl.d/99-elasticsearch.conf   # survive a reboot
docker run -d --name elasticsearch \
  -p 127.0.0.1:9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
  docker.elastic.co/elasticsearch/elasticsearch:9.5.5
```

OpenSearch 3.9 (`opensearchproject/opensearch:3.9.0`, needs `OPENSEARCH_INITIAL_ADMIN_PASSWORD`) is the open alternative; Arch `extra` also packages it. Label: `machine-only`. Every `-p HOST:CONTAINER` publish without a host IP binds all interfaces, so use `127.0.0.1:` for any container below as well.

## 6.6 SQLite

```bash
sudo pacman -S --needed sqlite   # CLI; Python's sqlite3 module is built in
```

SQLite <!-- v:sqlite -->3.54.0<!-- /v --> (upstream 3.54.1 fixes a 32-bit heap overflow). 3.54 replaces `sqlite3_analyzer` with `.diskused` in the shell.

## 6.7 Database GUI tools

**DBeaver** (universal client; Arch <!-- v:dbeaver -->26.2.2<!-- /v -->, upstream 26.2.3):

```bash
sudo pacman -S --needed dbeaver
```

**pgAdmin 4** (not in the repos; run the container with the credentials from your environment, never a literal password, and bind to loopback):

```bash
docker run -d --name pgadmin -p 127.0.0.1:5050:80 \
  -e "PGADMIN_DEFAULT_EMAIL=${PGADMIN_EMAIL:?set it}" \
  -e "PGADMIN_DEFAULT_PASSWORD=${PGADMIN_PASSWORD:?set it}" \
  dpage/pgadmin4
```

**Redis Insight** (licensed SSPL):

```bash
docker run -d --name redis-insight -p 127.0.0.1:5540:5540 redis/redisinsight:latest
```

A container reaching a Valkey that listens on host loopback is a networking caveat under rootless Docker. <!-- UNVERIFIED -->

**MongoDB Compass**: use the prebuilt AUR package. The CachyOS repo `mongodb-compass` is 1.49.4, flagged out of date, a source build against Electron 37 and `nodejs>=22.21.1`; `mongodb-compass-bin` is the current 1.53.2.

```bash
paru -S --needed mongodb-compass-bin
```

Other options: `pgcli` and `sqlitebrowser` (extra), DataGrip and Beekeeper Studio (AUR).

## Verify

```bash
systemctl is-active postgresql mariadb mongodb valkey
psql -d dev -c 'select current_user, current_database()'
mariadb --protocol=socket dev -e 'select database()'
mongosh --quiet --eval 'db.runCommand({ping:1})'
valkey-cli ping
```

Expected: each service `active`, the Postgres query returns your user and `dev`, `PONG` from Valkey. Check loopback binding with `ss -ltn | grep -E '5432|3306|27017|6379'` (every listener on `127.0.0.1` or `::1`).

## Sources

- [PostgreSQL 18 `initdb`](https://www.postgresql.org/docs/18/app-initdb.html), [versioning policy](https://www.postgresql.org/support/versioning/)
- [MariaDB releases](https://mariadb.org/about/), [MongoDB release notes](https://www.mongodb.com/docs/manual/release-notes/), [Valkey downloads](https://valkey.io/download/)
- Ledger: cluster C6 in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
