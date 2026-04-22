# JSM Assets3 UUID-Fixed Original Query Run

This document records one pass over the original query corpus against `jsm_assets3`.

- Source query doc: `jsm_original_queries.md`
- Target tables: `jsm_assets3.obj_new / jsm_assets3.obj_relationship_new`
- Query text changes:
  - `obj -> obj_new`
  - `obj_relationship -> obj_relationship_new`
  - binary UUID comparisons rewritten to `UNHEX(REPLACE(...))` for `id`/`obj_type_id`/relationship UUID columns
- Latency source: `information_schema.statements_summary_history.avg_latency`

## Summary

- Total queries: `52`
- Queries with returned rows > 0: `32`
- Queries with returned rows = 0: `15`
- Queries with execution errors: `5`

## Results

| Query | Status | Has rows | Returned rows | DB latency (ms) | Notes |
| --- | --- | --- | ---: | ---: | --- |
| 1. Basic Filters / Query 1 | `ok` | yes | 158 | 38.455 | matched |
| 1. Basic Filters / Query 2 | `ok` | yes | 28 | 81.2 | matched |
| 1. Basic Filters / Query 3 | `ok` | no | 0 | 1.02 | no rows |
| 1. Basic Filters / Query 4 | `ok` | no | 0 | 1.025 | no rows |
| 1. Basic Filters / Query 5 | `ok` | no | 0 | 0.986 | no rows |
| 1. Basic Filters / Query 6 | `ok` | yes | 1000 | 8.628 | matched |
| 1. Basic Filters / Query 7 | `ok` | no | 0 | 978.13 | no rows |
| 1. Basic Filters / Query 8 | `ok` | yes | 1000 | 145.392 | matched |
| 1. Basic Filters / Query 9 | `ok` | yes | 1000 | 193.352 | matched |
| 1. Basic Filters / Query 10 | `ok` | no | 0 | 3.38 | no rows |
| 1. Basic Filters / Query 11 | `ok` | no | 0 | 8.702 | no rows |
| 1. Basic Filters / Query 12 | `ok` | no | 0 | 0.919 | no rows |
| 1. Basic Filters / Query 13 | `ok` | yes | 1000 | 136.919 | matched |
| 1. Basic Filters / Query 14 | `ok` | no | 0 | 1.044 | no rows |
| 1. Basic Filters / Query 15 | `ok` | no | 0 | 0.873 | no rows |
| 1. Basic Filters / Query 16 | `ok` | yes | 1000 | 252.309 | matched |
| 1. Basic Filters / Query 17 | `ok` | no | 0 | 1.432 | no rows |
| 1. Basic Filters / Query 18 | `ok` | yes | 1000 | 216.442 | matched |
| 1. Basic Filters / Query 19 | `ok` | no | 0 | 1.365 | no rows |
| 2. Full Text Search / Query 1 | `ok` | yes | 5 | 45.0 | matched |
| 2. Full Text Search / Query 2 | `ok` | yes | 2 | 43.9 | matched |
| 2. Full Text Search / Query 3 | `ok` | yes | 3 | 63.3 | matched |
| 2. Full Text Search / Query 4 | `ok` | yes | 1000 | 82.2 | matched |
| 2. Full Text Search / Query 5 | `ok` | yes | 1 | 45.6 | matched |
| 2. Full Text Search / Query 6 | `ok` | yes | 4 | 77.1 | matched |
| 2. Full Text Search / Query 7 | `ok` | yes | 1 | 63.6 | matched |
| 3. Sorting / Query 1 | `ok` | yes | 1000 | 48.894 | matched |
| 3. Sorting / Query 2 | `ok` | yes | 1000 | 50.291 | matched |
| 3. Sorting / Query 3 | `ok` | yes | 1000 | 58.346 | matched |
| 3. Sorting / Query 4 | `ok` | yes | 1000 | 54.224 | matched |
| 3. Sorting / Query 5 | `ok` | yes | 1000 | 54.349 | matched |
| 3. Sorting / Query 6 | `ok` | yes | 1000 | 61.505 | matched |
| 3. Sorting / Query 7 | `ok` | yes | 1000 | 64.031 | matched |
| 3. Sorting / Query 8 | `ok` | yes | 1000 | 54.198 | matched |
| 3. Sorting / Query 9 | `ok` | yes | 1000 | 49.225 | matched |
| 3. Sorting / Query 10 | `ok` | no | 0 | 1.015 | no rows |
| 3. Sorting / Query 11 | `ok` | yes | 1000 | 551.812 | matched |
| 4. Relationship Traversal / Depth 0 / Query 1 | `ok` | yes | 1000 | 442.556 | matched |
| 4. Relationship Traversal / Depth 0 / Query 2 | `ok` | yes | 10 | 23.576 | matched |
| 4. Relationship Traversal / Depth 1 / Query 1 | `ok` | no | 0 | 284.764 | no rows |
| 4. Relationship Traversal / Depth 1 / Query 2 | `ok` | yes | 1000 | 520.924 | matched |
| 4. Relationship Traversal / Depth 1 / Query 3 | `ok` | yes | 9 | 337.176 | matched |
| 4. Relationship Traversal / Depth 1 / Query 6 | `ok` | yes | 1000 | 1326.885 | matched |
| 5. JSON Attribute Queries / Query 1 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 2 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 3 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 4 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 5 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 6 | `ok` | no | 0 | 4603.523 | no rows |
| 5. JSON Attribute Queries / Query 7 | `ok` | no | 0 | 4631.261 | no rows |
| 5. JSON Attribute Queries / Query 8 | `ok` | yes | 1000 | 362.883 | matched |
| 6. Range Queries / Query 1 | `ok` | yes | 1000 | 102.28 | matched |
