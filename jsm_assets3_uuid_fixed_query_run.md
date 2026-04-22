# JSM Assets3 UUID-Fixed Original Query Run

This document records one pass over the original query corpus against `jsm_assets3`.

- Source query doc: `jsm_original_queries.md`
- Target tables: `jsm_assets3.obj_new / jsm_assets3.obj_relationship_new`
- Query text changes:
  - `obj -> obj_new`
  - `obj_relationship -> obj_relationship_new`
  - binary UUID comparisons rewritten to `UNHEX(REPLACE(...))` for `id`/`obj_type_id`/relationship UUID columns

## Summary

- Total queries: `52`
- Queries with returned rows > 0: `32`
- Queries with returned rows = 0: `15`
- Queries with execution errors: `5`

## Results

| Query | Status | Has rows | Returned rows | Latency (ms) | Notes |
| --- | --- | --- | ---: | ---: | --- |
| 1. Basic Filters / Query 1 | `ok` | yes | 158 | 6074.1 | matched |
| 1. Basic Filters / Query 2 | `ok` | yes | 28 | 6286.7 | matched |
| 1. Basic Filters / Query 3 | `ok` | no | 0 | 6030.3 | no rows |
| 1. Basic Filters / Query 4 | `ok` | no | 0 | 6147.4 | no rows |
| 1. Basic Filters / Query 5 | `ok` | no | 0 | 5660.0 | no rows |
| 1. Basic Filters / Query 6 | `ok` | yes | 1000 | 5861.3 | matched |
| 1. Basic Filters / Query 7 | `ok` | no | 0 | 6860.2 | no rows |
| 1. Basic Filters / Query 8 | `ok` | yes | 1000 | 6176.6 | matched |
| 1. Basic Filters / Query 9 | `ok` | yes | 1000 | 7488.9 | matched |
| 1. Basic Filters / Query 10 | `ok` | no | 0 | 6734.0 | no rows |
| 1. Basic Filters / Query 11 | `ok` | no | 0 | 6719.1 | no rows |
| 1. Basic Filters / Query 12 | `ok` | no | 0 | 6498.6 | no rows |
| 1. Basic Filters / Query 13 | `ok` | yes | 1000 | 6148.8 | matched |
| 1. Basic Filters / Query 14 | `ok` | no | 0 | 6153.1 | no rows |
| 1. Basic Filters / Query 15 | `ok` | no | 0 | 6142.3 | no rows |
| 1. Basic Filters / Query 16 | `ok` | yes | 1000 | 6932.9 | matched |
| 1. Basic Filters / Query 17 | `ok` | no | 0 | 4676.8 | no rows |
| 1. Basic Filters / Query 18 | `ok` | yes | 1000 | 7076.6 | matched |
| 1. Basic Filters / Query 19 | `ok` | no | 0 | 5786.9 | no rows |
| 2. Full Text Search / Query 1 | `ok` | yes | 5 | 5165.8 | matched |
| 2. Full Text Search / Query 2 | `ok` | yes | 2 | 3875.5 | matched |
| 2. Full Text Search / Query 3 | `ok` | yes | 3 | 4352.1 | matched |
| 2. Full Text Search / Query 4 | `ok` | yes | 1000 | 4927.0 | matched |
| 2. Full Text Search / Query 5 | `ok` | yes | 1 | 4931.3 | matched |
| 2. Full Text Search / Query 6 | `ok` | yes | 4 | 4440.6 | matched |
| 2. Full Text Search / Query 7 | `ok` | yes | 1 | 4603.0 | matched |
| 3. Sorting / Query 1 | `ok` | yes | 1000 | 4643.0 | matched |
| 3. Sorting / Query 2 | `ok` | yes | 1000 | 5099.7 | matched |
| 3. Sorting / Query 3 | `ok` | yes | 1000 | 5109.0 | matched |
| 3. Sorting / Query 4 | `ok` | yes | 1000 | 4621.8 | matched |
| 3. Sorting / Query 5 | `ok` | yes | 1000 | 4341.7 | matched |
| 3. Sorting / Query 6 | `ok` | yes | 1000 | 5152.6 | matched |
| 3. Sorting / Query 7 | `ok` | yes | 1000 | 4794.3 | matched |
| 3. Sorting / Query 8 | `ok` | yes | 1000 | 5030.4 | matched |
| 3. Sorting / Query 9 | `ok` | yes | 1000 | 4575.1 | matched |
| 3. Sorting / Query 10 | `ok` | no | 0 | 4776.4 | no rows |
| 3. Sorting / Query 11 | `ok` | yes | 1000 | 5294.7 | matched |
| 4. Relationship Traversal / Depth 0 / Query 1 | `ok` | yes | 1000 | 4916.5 | matched |
| 4. Relationship Traversal / Depth 0 / Query 2 | `ok` | yes | 10 | 4349.5 | matched |
| 4. Relationship Traversal / Depth 1 / Query 1 | `ok` | no | 0 | 4401.4 | no rows |
| 4. Relationship Traversal / Depth 1 / Query 2 | `ok` | yes | 1000 | 5487.0 | matched |
| 4. Relationship Traversal / Depth 1 / Query 3 | `ok` | yes | 9 | 6382.0 | matched |
| 4. Relationship Traversal / Depth 1 / Query 6 | `ok` | yes | 1000 | 6320.7 | matched |
| 5. JSON Attribute Queries / Query 1 | `error` | - | - | 4557.0 | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 2 | `error` | - | - | 3969.0 | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 3 | `error` | - | - | 4788.1 | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 4 | `error` | - | - | 6008.8 | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 5 | `error` | - | - | 5461.1 | ERROR 1105 (HY000) at line 1: [components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs:293]: Invalid JSON path expression. The error is around character position 1. comman |
| 5. JSON Attribute Queries / Query 6 | `ok` | no | 0 | 11569.5 | no rows |
| 5. JSON Attribute Queries / Query 7 | `ok` | no | 0 | 10893.5 | no rows |
| 5. JSON Attribute Queries / Query 8 | `ok` | yes | 1000 | 6903.9 | matched |
| 6. Range Queries / Query 1 | `ok` | yes | 1000 | 4827.8 | matched |
