---
name: mongodb-schema-design
description: Design or review a MongoDB schema — embed vs reference decisions, aggregation pipeline structure, schema validation, and recognizing when the data is actually relational and shouldn't be in Mongo at all. Trigger on requests to add a collection, model a document relationship, write an aggregation pipeline, or debug slow/unbounded document growth.
---

"Schemaless" is a storage-layer property, not a design license. Most Mongo schema problems are relational modeling mistakes made worse by the lack of a query planner that forces the issue upfront.

## Embed vs reference — the real tradeoff
- The decision axis is read pattern vs document growth, not "is it related data." Embed when the sub-data is always read/written together with the parent, has a bounded size, and doesn't need to be queried independently (e.g., an address on a user, line items on an order at time of purchase).
- Reference when the sub-data grows unboundedly (comments on a post, events on a user), is queried/updated independently of the parent, or is shared across multiple parents (a product referenced by many orders — embedding it duplicates data that then drifts when the product changes).
- The 16MB document size cap is a hard ceiling, but the real failure shows up long before that: an embedded array that grows without bound (activity log, comments) causes document moves on disk as it outgrows its allocated space, degrading write performance well before the size limit is hit. If an array's growth isn't bounded by the domain (max N items, or time-windowed), reference it instead.
- A common middle ground: embed a bounded recent/preview subset (last 5 comments) and reference the full collection for the rest — avoids a query for the common case while keeping growth unbounded-safe.

## Aggregation pipelines
- The `$lookup`-in-a-loop trap: don't run a query per document in application code to fetch related data — that's N+1 applied to Mongo. Use a single `$lookup` stage (or `$lookup` + `$unwind` for a 1:1 join) to pull related documents in one round trip.
- Put `$match` and `$sort` as early as possible in the pipeline, before `$lookup`/`$unwind`/`$group` — this lets Mongo use an index for the match/sort and shrinks the working set before the expensive stages run. A `$match` placed after a `$group` gets none of the index benefit.
- `$lookup` without a `pipeline` sub-filter pulls the entire matching foreign collection's documents before any projection — for a large foreign collection, use `$lookup` with a `let`/`pipeline` form to filter and project on the foreign side before the join.
- Aggregations returning large result sets need `allowDiskUse: true` or they fail past the in-memory stage limit (100MB per stage) — but treat that as a signal to add an earlier `$match`/`$limit`, not just a flag to silence the error.

## Schema validation
- Use `$jsonSchema` validation on every collection that isn't genuinely free-form. "Flexible schema" without validation means a typo'd field name or wrong type silently creates a new shape that every downstream reader has to defensively handle forever. Validation with `validationLevel: moderate` catches new/modified documents without breaking existing ones during a migration.
- ODM-level validation (Mongoose, Pydantic + Motor/Beanie) is necessary but not sufficient — anything that writes via a script, migration, or a different service bypasses it. Database-level `$jsonSchema` is the actual backstop.

## When it should have been relational
If the data has a fixed, well-known shape, needs multi-document ACID transactions across many entities routinely (not the occasional one), needs joins across more than one or two collections regularly, or the access pattern is fundamentally "give me arbitrary slices filtered by several unrelated fields" — that's a relational workload wearing a document-store costume. Watch for: a "denormalized for performance" schema that requires writing the same fact to five collections to keep them in sync, or aggregation pipelines that have grown to look like hand-rolled SQL joins. Both are signals the domain wanted Postgres.
