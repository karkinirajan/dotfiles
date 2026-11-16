# 06.2 · pgvector demo

A small database that shows pgvector on the system PostgreSQL 18: a table of 3-dimensional embeddings, an HNSW index and two nearest-neighbour queries. The axes are `[tech, food, sport]`, so the numbers can be read by eye; a real embedding model gives 384 to 3072 dimensions.

```text
06-tools/pgvector-demo/
├── README.md
└── setup.sql        # extension, table, 8 rows, HNSW index, two example queries
```

## Prerequisites

`postgresql` and `pgvector` are both in [`packages/developer.txt`](../../01-system/cachyos/packages/developer.txt). The PostgreSQL service must be running and your role needs `CREATEDB`.

## Set it up

pgvector is not a trusted extension, so enabling it takes a superuser. That is the only step that needs `sudo`.

```sh
createdb pgvector_demo
sudo -u postgres psql -d pgvector_demo -c 'CREATE EXTENSION IF NOT EXISTS vector;'
/usr/bin/psql -X -d pgvector_demo -v ON_ERROR_STOP=1 -f 06-tools/pgvector-demo/setup.sql
```

The script is safe to re-run: it drops and recreates the `documents` table. Use `/usr/bin/psql` when scripting, because the interactive `psql` in this zsh setup opens a kitty window instead of printing to the terminal.

## What to look at

| Operator | Meaning | Used for |
|---|---|---|
| `<=>` | cosine distance | the first example query |
| `<->` | L2 distance | the second example query, filtered to food and mixed topics |
| `<#>` | negative inner product | not in the script; the third distance pgvector offers |

On 8 rows the planner scans the table instead of using the index; the HNSW index matters once the table is large.
