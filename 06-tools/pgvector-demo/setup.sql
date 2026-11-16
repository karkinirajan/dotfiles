-- pgvector demo. Run against the pgvector_demo database:
--   /usr/bin/psql -X -d pgvector_demo -v ON_ERROR_STOP=1 -f 06-tools/pgvector-demo/setup.sql
-- See README.md in this folder for the one sudo step that enables the extension.
-- Safe to re-run: it drops and recreates the demo table.
--
-- Embeddings are 3-dimensional so the numbers are readable by eye. Axes are
-- [tech, food, sport]; a real model would give 384-3072 dimensions.

CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS documents;
CREATE TABLE documents (
    id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title     text         NOT NULL,
    topic     text         NOT NULL,
    embedding vector(3)    NOT NULL
);

INSERT INTO documents (title, topic, embedding) VALUES
    ('Intro to PostgreSQL',          'tech',  '[0.90, 0.10, 0.00]'),
    ('Vector search with pgvector',  'tech',  '[0.95, 0.05, 0.00]'),
    ('Sourdough baking basics',      'food',  '[0.05, 0.90, 0.05]'),
    ('Best pasta recipes',           'food',  '[0.00, 0.95, 0.05]'),
    ('Marathon training plan',       'sport', '[0.10, 0.05, 0.85]'),
    ('Football tactics 101',         'sport', '[0.05, 0.00, 0.95]'),
    ('Cooking for athletes',         'mixed', '[0.00, 0.60, 0.40]'),
    ('Sports analytics with SQL',    'mixed', '[0.50, 0.00, 0.50]');

-- Approximate-nearest-neighbour index (HNSW) for cosine distance. On 8 rows the
-- planner will still pick a seq scan; the index matters once the table is large.
CREATE INDEX documents_embedding_hnsw
    ON documents USING hnsw (embedding vector_cosine_ops);

-- Example queries -------------------------------------------------------------
-- Operators: <=> cosine distance, <-> L2 distance, <#> negative inner product.

\echo '--- 3 nearest to a "tech" query vector (cosine) ---'
SELECT title, topic, round((embedding <=> '[0.9, 0.1, 0.0]')::numeric, 4) AS cosine_distance
FROM documents
ORDER BY embedding <=> '[0.9, 0.1, 0.0]'
LIMIT 3;

\echo '--- 3 nearest to a "food" query vector, food/mixed topics only (filtered) ---'
SELECT title, topic, round((embedding <-> '[0.0, 1.0, 0.0]')::numeric, 4) AS l2_distance
FROM documents
WHERE topic IN ('food', 'mixed')
ORDER BY embedding <-> '[0.0, 1.0, 0.0]'
LIMIT 3;
