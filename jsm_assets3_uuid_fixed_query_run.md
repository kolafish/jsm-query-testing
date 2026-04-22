# JSM Assets3 UUID-Fixed Original Query Run

This document records one pass over the original query corpus against `jsm_assets3`.

- Source query doc: `jsm_original_queries.md`
- Target tables: `jsm_assets3.obj_new / jsm_assets3.obj_relationship_new`
- Query text changes:
  - `obj -> obj_new`
  - `obj_relationship -> obj_relationship_new`
  - binary UUID comparisons rewritten to `UNHEX(REPLACE(...))` for `id`/`obj_type_id`/relationship UUID columns
- Latency source: `information_schema.statements_summary_history.avg_latency`
- Fallback for missing statement-summary rows: `EXPLAIN ANALYZE` top operator time

## Summary

- Total queries: `58`
- Queries with returned rows > 0: `36`
- Queries with returned rows = 0: `17`
- Queries with execution errors: `5`

## Results

| Query | Status | Has rows | Returned rows | DB latency (ms) | Notes |
| --- | --- | --- | ---: | ---: | --- |
| 1. Basic Filters / Query 1 | `ok` | yes | 158 | 54.995 | matched |
| 1. Basic Filters / Query 2 | `ok` | yes | 28 | 93.4 | matched |
| 1. Basic Filters / Query 3 | `ok` | no | 0 | 0.99 | no rows |
| 1. Basic Filters / Query 4 | `ok` | no | 0 | 1.011 | no rows |
| 1. Basic Filters / Query 5 | `ok` | no | 0 | 0.988 | no rows |
| 1. Basic Filters / Query 6 | `ok` | yes | 1000 | 11.354 | matched |
| 1. Basic Filters / Query 7 | `ok` | no | 0 | 13.888 | no rows |
| 1. Basic Filters / Query 8 | `ok` | yes | 1000 | 155.708 | matched |
| 1. Basic Filters / Query 9 | `ok` | yes | 1000 | 240.033 | matched |
| 1. Basic Filters / Query 10 | `ok` | no | 0 | 4.296 | no rows |
| 1. Basic Filters / Query 11 | `ok` | no | 0 | 15.075 | no rows |
| 1. Basic Filters / Query 12 | `ok` | no | 0 | 1.536 | no rows |
| 1. Basic Filters / Query 13 | `ok` | yes | 1000 | 170.822 | matched |
| 1. Basic Filters / Query 14 | `ok` | no | 0 | 1.425 | no rows |
| 1. Basic Filters / Query 15 | `ok` | no | 0 | 1.474 | no rows |
| 1. Basic Filters / Query 16 | `ok` | yes | 1000 | 402.593 | matched |
| 1. Basic Filters / Query 17 | `ok` | no | 0 | 1.347 | no rows |
| 1. Basic Filters / Query 18 | `ok` | yes | 1000 | 237.774 | matched |
| 1. Basic Filters / Query 19 | `ok` | no | 0 | 1.422 | no rows |
| 2. Full Text Search / Query 1 | `ok` | yes | 5 | 40.1 | matched |
| 2. Full Text Search / Query 2 | `ok` | yes | 2 | 54.1 | matched |
| 2. Full Text Search / Query 3 | `ok` | yes | 3 | 60.7 | matched |
| 2. Full Text Search / Query 4 | `ok` | yes | 1000 | 79.0 | matched |
| 2. Full Text Search / Query 5 | `ok` | yes | 1 | 42.6 | matched |
| 2. Full Text Search / Query 6 | `ok` | yes | 4 | 77.0 | matched |
| 2. Full Text Search / Query 7 | `ok` | yes | 1 | 61.9 | matched |
| 3. Sorting / Query 1 | `ok` | yes | 1000 | 61.649 | matched |
| 3. Sorting / Query 2 | `ok` | yes | 1000 | 55.001 | matched |
| 3. Sorting / Query 3 | `ok` | yes | 1000 | 61.739 | matched |
| 3. Sorting / Query 4 | `ok` | yes | 1000 | 59.284 | matched |
| 3. Sorting / Query 5 | `ok` | yes | 1000 | 54.782 | matched |
| 3. Sorting / Query 6 | `ok` | yes | 1000 | 69.167 | matched |
| 3. Sorting / Query 7 | `ok` | yes | 1000 | 68.78 | matched |
| 3. Sorting / Query 8 | `ok` | yes | 1000 | 55.179 | matched |
| 3. Sorting / Query 9 | `ok` | yes | 1000 | 57.901 | matched |
| 3. Sorting / Query 10 | `ok` | no | 0 | 0.962 | no rows |
| 3. Sorting / Query 11 | `ok` | yes | 1000 | 552.561 | matched |
| 4. Relationship Traversal / Depth 0 / Query 1 | `ok` | yes | 1000 | 465.85 | matched |
| 4. Relationship Traversal / Depth 0 / Query 2 | `ok` | yes | 10 | 34.049 | matched |
| 4. Relationship Traversal / Depth 1 / Query 1 | `ok` | no | 0 | 298.742 | no rows |
| 4. Relationship Traversal / Depth 1 / Query 2 | `ok` | yes | 1000 | 533.666 | matched |
| 4. Relationship Traversal / Depth 1 / Query 3 | `ok` | yes | 9 | 338.902 | matched |
| 4. Relationship Traversal / Depth 1 / Query 4 | `ok` | no | 0 | 1210.0 | no rows |
| 4. Relationship Traversal / Depth 1 / Query 5 | `ok` | yes | 1000 | 406.641 | matched |
| 4. Relationship Traversal / Depth 1 / Query 6 | `ok` | yes | 1000 | 1324.303 | matched |
| 4. Relationship Traversal / Depth 2 / Query 1 | `ok` | yes | 90 | 1806.715 | matched |
| 4. Relationship Traversal / Depth 2 / Query 2 | `ok` | yes | 1000 | 532.332 | matched |
| 4. Relationship Traversal / Depth 2 / Query 3 | `ok` | yes | 12 | 479.233 | matched |
| 4. Relationship Traversal / Depth 3 / Query 1 | `ok` | no | 0 | 3122.104 | no rows |
| 5. JSON Attribute Queries / Query 1 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 2 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 3 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 4 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 5 | `error` | - | - | - | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 6 | `ok` | no | 0 | 5185.842 | no rows |
| 5. JSON Attribute Queries / Query 7 | `ok` | no | 0 | 5075.727 | no rows |
| 5. JSON Attribute Queries / Query 8 | `ok` | yes | 1000 | 356.05 | matched |
| 6. Range Queries / Query 1 | `ok` | yes | 1000 | 102.799 | matched |
