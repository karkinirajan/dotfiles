---
title: "10 Data Engineering"
part: "01"
chapter: "10"
topic: data-engineering
versions: [python, uv]
last_verified: 2026-10-29
status: current
sources:
  - https://redpanda.com/docs
  - https://kafka.apache.org/documentation/
  - https://airflow.apache.org/docs/
---

# 10 Data Engineering

Current releases on 2026-10-28: pandas 3.1.0, polars 2.1.0, numpy 2.5.4, pyarrow 26.0.0, prefect 3.9.0, apache-airflow 3.3.2, dask 2026.8.0. pandas 3 and polars 2 are major bumps whose breaking changes were not reviewed here; every group below resolves as binary wheels on Python 3.14 (`verified-in-cloud`).

## 10.1 Core Libraries

```bash
uv add pandas numpy scipy matplotlib seaborn plotly kaleido
uv add scikit-learn polars pyarrow
```

| Library | Purpose |
|---|---|
| **Pandas** | DataFrames for tabular data |
| **Polars** | Blazing-fast Rust-based DataFrames (10-100× faster) |
| **NumPy** | Numerical computing |
| **SciPy** | Scientific computing |
| **Matplotlib/Seaborn** | Static plotting |
| **Plotly** | Interactive charts |
| **scikit-learn** | ML preprocessing, models, pipelines |
| **PyArrow** | Apache Arrow — columnar data & Parquet I/O |

## 10.2 Apache Kafka: local setup

Two options. **Apache Kafka 4.4.0** (KRaft mode, no ZooKeeper) runs from the official image and is the reference implementation:

```bash
docker run -d --name kafka -p 127.0.0.1:9092:9092 apache/kafka:4.4.0
```

**Redpanda** is Kafka-API-compatible and written in C++ (no JVM); its licence is BSL 1.1. Pin the images instead of `latest` (images below were current on 2026-10-28). The Kafka listeners are published on loopback only. The `command` form and the `--smp`/`--memory` flags follow the previous version of this guide and were not re-verified against Redpanda's current docs; Redpanda's own compose example adds `--mode dev-container`. <!-- UNVERIFIED: Redpanda command syntax and the "~512MB RAM, no JVM" claim -->

```yaml
# docker-compose.kafka.yml
services:
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:v26.2.6
    command:
      - redpanda start --smp 1 --memory 512M --overprovisioned
      - --kafka-addr internal://0.0.0.0:9092,external://0.0.0.0:19092
      - --advertise-kafka-addr internal://redpanda:9092,external://localhost:19092
    ports: ["127.0.0.1:19092:19092", "127.0.0.1:9644:9644"]

  console:
    image: docker.redpanda.com/redpandadata/console:v3.13.1
    ports: ["127.0.0.1:8080:8080"]
    environment:
      KAFKA_BROKERS: redpanda:9092
    depends_on: [redpanda]
```

## 10.3 Workflow Orchestration

```bash
uv add prefect            # Python-native orchestration (3.9)
uvx apache-airflow standalone   # Airflow 3.3: an unconstrained `uv add apache-airflow` is not supported; use the official constraints file for a project install
uv add dagster            # asset-based orchestration (1.13)
uv add "dask[complete]"   # Parallel computing — scales Pandas to larger-than-memory
```
