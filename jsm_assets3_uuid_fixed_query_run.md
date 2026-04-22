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
- Queries with returned rows = 0: `22`
- Queries with execution errors: `0`

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
| 5. JSON Attribute Queries / Query 1 | `ok` | no | 0 | 5890.228 | no rows |
| 5. JSON Attribute Queries / Query 2 | `ok` | no | 0 | 5610.457 | no rows |
| 5. JSON Attribute Queries / Query 3 | `ok` | no | 0 | 5273.968 | no rows |
| 5. JSON Attribute Queries / Query 4 | `ok` | no | 0 | 6934.63 | no rows |
| 5. JSON Attribute Queries / Query 5 | `ok` | no | 0 | 5974.24 | no rows |
| 5. JSON Attribute Queries / Query 6 | `ok` | no | 0 | 5185.842 | no rows |
| 5. JSON Attribute Queries / Query 7 | `ok` | no | 0 | 5075.727 | no rows |
| 5. JSON Attribute Queries / Query 8 | `ok` | yes | 1000 | 356.05 | matched |
| 6. Range Queries / Query 1 | `ok` | yes | 1000 | 102.799 | matched |

## LIKE vs MATCH AGAINST

| Query | Column(s) | FULLTEXT index | LIKE rows | LIKE DB latency (ms) | MATCH rows | MATCH DB latency (ms) | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Full Text Search / Query 2 | `text_value_1` | idx_obj_new_text_value_1_ngram (NGRAM) | 2 | 54.1 | 2 | 6.27 | contains semantics; MATCH uses quoted phrase |
| Full Text Search / Query 3 | `text_value_4 + text_value_5` | idx_obj_new_text_value_4_ngram (NGRAM); idx_obj_new_text_value_5_ngram (NGRAM) | 3 | 60.7 | 3 | 5.4 | cross-column OR rewritten to UNION DISTINCT |
| Full Text Search / Query 4 | `text_value_4 + text_value_5 + text_value_10` | idx_obj_new_text_value_4_ngram (NGRAM); idx_obj_new_text_value_5_ngram (NGRAM); text_value_10 has no FULLTEXT index | 1000 | 79.0 | 1000 | 104.4 | LIKE branches rewritten to MATCH; equality branch on text_value_10 kept as-is |
| Full Text Search / Query 5 | `text_value_5` | idx_obj_new_text_value_5_ngram (NGRAM) | 1 | 42.6 | 1 | 5.12 | contains semantics; MATCH uses quoted phrase |
| Full Text Search / Query 6 | `text_value_4` | idx_obj_new_text_value_4_ngram (NGRAM) | 4 | 77.0 | 4 | 8.46 | same-column OR rewritten to a single MATCH with multiple quoted phrases |
| Full Text Search / Query 7 | `text_value_5` | idx_obj_new_text_value_5_ngram (NGRAM) | 1 | 61.9 | 1 | 5.76 | contains semantics; MATCH uses quoted phrase |
| 1. Basic Filters / Query 2 | `text_value_22` | idx_obj_new_text_value_22_ngram (NGRAM) | 28 | 93.4 | 28 | 4410.0 | contains semantics; MATCH is executable now but much slower because the FTS candidate set is very wide |
| 1. Basic Filters / Query 7 | `label` | idx_obj_new_label_ngram (NGRAM) | 0 | 13.888 | 0 | 3.78 | contains semantics; MATCH uses quoted phrase |
| 4. Relationship Traversal / Depth 1 / Query 4 | `text_value_1` | idx_obj_new_text_value_1_ngram (NGRAM) | 0 | 905.5 | 0 | 935.9 | recommended rewrite runs with `tidb_enforce_mpp=on` and `tiflash_hash_join_version='optimized'`; the better rewrite pushes `UNION DISTINCT` into the FTS candidate-id subquery so the relationship traversal runs only once |
| 5. JSON Attribute Queries / Query 6 | `text_value_20` | idx_obj_new_text_value_20_ngram (NGRAM) | 0 | 5185.842 | 0 | 2.89 | includes JSON predicates; MATCH branch is executable now and collapses the scan quickly |

## Notes

- `Full Text Search / Query 1` should stay on `LIKE`, not `MATCH`, because the tested prefix rewrite on a hyphenated token is not semantically equivalent and returns many more rows.
- `text_value_10` has no FULLTEXT index, so in `Full Text Search / Query 4` only the `text_value_4` and `text_value_5` branches were rewritten to `MATCH`; the equality branch on `text_value_10` stayed unchanged.
- Outside the explicit `Full Text Search` section, `text_value_22`, `label`, and `text_value_20` also have `NGRAM FULLTEXT` indexes, so their executable `MATCH AGAINST` comparisons are included in the same table.
- Among the newly restored queries, `4. Relationship Traversal / Depth 1 / Query 4` is the only additional `LIKE` case whose target column already has a matching FULLTEXT index. The recommended execution recipe for the rewrite is to enable `tidb_enforce_mpp=on` and `tiflash_hash_join_version='optimized'`, then `UNION DISTINCT` the small FTS candidate-id set first and join/filter once. Under the same settings, the rewritten form is close to the original `LIKE` runtime, but not faster on this dataset.
- `1. Basic Filters / Query 2` is a good example of “can rewrite, but should not blindly rewrite”: after adding `text_value_22` FULLTEXT, the `MATCH` form still returns the same 28 rows, but it is far slower than the original `LIKE` because the token `Requirements` is too unselective on this dataset.

## LIKE vs MATCH QPS Benchmark

This benchmark uses the comparable `LIKE vs MATCH AGAINST` subset from the table above as two separate mixed workloads:

- `LIKE` corpus: `bench/assets3_like_vs_match_like_qps_corpus.json`
- `MATCH` corpus: `bench/assets3_like_vs_match_match_qps_corpus.json`
- Benchmark driver: `bench/go_qps_bench/main.go`
- Client path: workstation -> HAProxy -> TiDB
- Concurrency levels: `2 / 4 / 6 / 8 / 10 / 12`
- Per-level duration: `90s`
- Sleep between levels: `15s`
- `MATCH` session settings:
  - `set tidb_enforce_mpp=on;`
  - `set tiflash_hash_join_version='optimized';`

Result files:

- `LIKE`: `bench/results/assets3_like_qps_benchmark_20260422.json`
- `MATCH`: `bench/results/assets3_match_qps_benchmark_20260422.json`

### Overall Results

| Concurrency | LIKE QPS | LIKE p50 (ms) | LIKE p95 (ms) | MATCH QPS | MATCH p50 (ms) | MATCH p95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 1.907 | 83.599 | 8033.057 | 3.329 | 12.276 | 4209.262 |
| 4 | 2.408 | 167.680 | 14462.511 | 4.485 | 23.605 | 4724.378 |
| 6 | 2.585 | 100.742 | 20853.472 | 5.169 | 34.442 | 6406.438 |
| 8 | 2.952 | 197.810 | 22904.356 | 5.704 | 40.759 | 7223.654 |
| 10 | 4.165 | 593.620 | 14350.547 | 5.511 | 67.221 | 10128.682 |
| 12 | 5.184 | 900.371 | 11455.976 | 5.274 | 76.751 | 11653.893 |

### Warmup Highlights

- `LIKE` warmup slowest queries:
  - `5. JSON Attribute Queries / Query 6`: `5143.350ms`
  - `4. Relationship Traversal / Depth 1 / Query 4`: `1266.233ms`
- `MATCH` warmup slowest queries:
  - `1. Basic Filters / Query 2`: `32298.523ms`
  - `4. Relationship Traversal / Depth 1 / Query 4`: `1717.954ms`

### Dominant Query Costs

For the `LIKE` workload, the main throughput limiter is still:

- `5. JSON Attribute Queries / Query 6`
  - `c=12`: `avg=12385.185ms`, `p95=19364.716ms`
- `4. Relationship Traversal / Depth 1 / Query 4`
  - `c=12`: `avg=3720.053ms`, `p95=5903.377ms`

For the `MATCH` workload, `JSON Query 6` stops being the dominant bottleneck, and the cost shifts to:

- `1. Basic Filters / Query 2`
  - `c=12`: `avg=9016.083ms`, `p95=12773.294ms`
- `4. Relationship Traversal / Depth 1 / Query 4`
  - `c=12`: `avg=10274.851ms`, `p95=26818.131ms`

### Conclusions

- On this 10-query mixed workload, `MATCH` reaches a slightly higher QPS ceiling than `LIKE`.
- `LIKE` peaks at `5.184 QPS` at `c=12`.
- `MATCH` peaks at `5.704 QPS` at `c=8`.
- The main improvement comes from removing the very slow `LIKE` behavior of `JSON Attribute Queries / Query 6`.
- After that shift, the workload is limited mostly by:
  - `1. Basic Filters / Query 2`
  - `4. Relationship Traversal / Depth 1 / Query 4`
- Both workloads completed without execution errors or row-count mismatches.
