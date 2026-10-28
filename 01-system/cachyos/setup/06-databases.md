---
title: "06 Databases"
part: "01"
chapter: "06"
topic: databases
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 06 Databases


## 6.1 PostgreSQL ⭐

```bash
sudo pacman -S postgresql
sudo -iu postgres initdb --locale=C.UTF-8 -E UTF8 -D /var/lib/postgres/data --data-checksums
sudo systemctl enable --now postgresql

# Create dev user and database:
sudo -iu postgres psql -c "CREATE USER devuser WITH ENCRYPTED PASSWORD 'devpass' CREATEDB;"
sudo -iu postgres psql -c "CREATE DATABASE devdb OWNER devuser;"

# Enable pgvector:
sudo pacman -S pgvector
sudo -iu postgres psql devdb -c "CREATE EXTENSION vector;"
```

## 6.2 MariaDB (MySQL-compatible)

```bash
sudo pacman -S mariadb
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo install -Dm644 01-system/cachyos/mariadb-local.cnf /etc/my.cnf.d/90-local-dev.cnf
sudo systemctl enable --now mariadb
```

## 6.3 MongoDB

```bash
paru -S mongodb-bin   # Pre-built binary (building from source takes hours)
sudo systemctl enable --now mongodb
mongosh   # Verify
```

> **CachyOS note:** If MongoDB fails to start with `Permission denied`, the data directory is owned by root. Create a systemd override to auto-fix on every start:
> ```bash
> sudo mkdir -p /etc/systemd/system/mongodb.service.d/
> sudo tee /etc/systemd/system/mongodb.service.d/fix-permissions.conf << 'EOF'
> [Service]
> ExecStartPre=+/bin/chown -R mongodb:mongodb /var/lib/mongodb /var/log/mongodb
> EOF
> sudo systemctl daemon-reload && sudo systemctl restart mongodb
> ```
> The `+` prefix runs the command as root regardless of the service user.

## 6.4 Redis (Valkey)

CachyOS/Arch ships `valkey` (the Redis open-source fork):

```bash
sudo pacman -S valkey
sudo systemctl enable --now valkey.service
valkey-cli ping   # → PONG
```

## 6.5 Elasticsearch (Docker)

```bash
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.0
```

## 6.6 SQLite

```bash
sudo pacman -S sqlite   # CLI tool (Python's sqlite3 module is always available)
```

## 6.7 Database GUI Tools

**DBeaver ⭐** (universal — Postgres, MySQL, SQLite, MongoDB, 80+ databases):

```bash
sudo pacman -S dbeaver
```

**pgAdmin 4** (Docker):

```bash
docker run -d --name pgadmin -p 5050:80 \
  -e "PGADMIN_DEFAULT_EMAIL=admin@local.dev" \
  -e "PGADMIN_DEFAULT_PASSWORD=admin" \
  dpage/pgadmin4
```

**Redis Insight**:

```bash
docker run -d --name redis-insight -p 5540:5540 redis/redisinsight:latest
```

**MongoDB Compass** (official GUI for MongoDB):

```bash
# CachyOS repo version requires nodejs-25 which conflicts with nodejs-lts-iron.
# Use the pre-built binary from AUR instead:
paru -S mongodb-compass-bin
```
