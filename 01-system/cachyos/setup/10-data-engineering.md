---
title: "10 Data Engineering"
part: "01"
chapter: "10"
topic: data-engineering
versions: []
last_verified: 2026-10-06
status: draft
sources: []
---

# 10 Data Engineering


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

## 10.2 Apache Kafka — Local Setup (Redpanda)

Redpanda is Kafka-API-compatible, no JVM, ~512MB RAM:

```yaml
# docker-compose.kafka.yml
services:
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:latest
    command:
      - redpanda start --smp 1 --memory 512M --overprovisioned
      - --kafka-addr internal://0.0.0.0:9092,external://0.0.0.0:19092
      - --advertise-kafka-addr internal://redpanda:9092,external://localhost:19092
    ports: ["19092:19092", "9644:9644"]

  console:
    image: docker.redpanda.com/redpandadata/console:latest
    ports: ["8080:8080"]
    environment:
      KAFKA_BROKERS: redpanda:9092
    depends_on: [redpanda]
```

## 10.3 Workflow Orchestration

```bash
uv add prefect            # Modern Python-native orchestration
uv add apache-airflow     # Industry standard (heavier)
uv add "dask[complete]"   # Parallel computing — scales Pandas to larger-than-memory
```
