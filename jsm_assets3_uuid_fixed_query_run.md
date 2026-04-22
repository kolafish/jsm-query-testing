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

These two workloads use the same 10-query corpus from the table above:

- `LIKE` corpus: `bench/assets3_like_vs_match_like_qps_corpus.json`
- `MATCH` corpus: `bench/assets3_like_vs_match_match_qps_corpus.json`
- driver: `bench/go_qps_bench/main.go`
- concurrency levels: `2 / 4 / 6 / 8 / 10 / 12`
- per-level duration: `90s`
- sleep between levels: `15s`
- `MATCH` runs with:
  - `set tidb_enforce_mpp=on;`
  - `set tiflash_hash_join_version='optimized';`

There are two execution modes:

- `shared-pool`: all workers share one mixed request pool
- `per-query-pool`: each query has its own worker loop, with a global concurrency gate

Result files:

- shared-pool:
  - `bench/results/assets3_like_qps_benchmark_20260422.json`
  - `bench/results/assets3_match_qps_benchmark_20260422.json`
- per-query-pool:
  - `bench/results/assets3_like_per_query_qps_benchmark_20260422.json`
  - `bench/results/assets3_match_per_query_qps_benchmark_20260422.json`

### shared-pool

| Concurrency | LIKE QPS | LIKE p95 (ms) | MATCH QPS | MATCH p95 (ms) |
| --- | ---: | ---: | ---: | ---: |
| 2 | 1.907 | 8033.057 | 3.329 | 4209.262 |
| 4 | 2.408 | 14462.511 | 4.485 | 4724.378 |
| 6 | 2.585 | 20853.472 | 5.169 | 6406.438 |
| 8 | 2.952 | 22904.356 | 5.704 | 7223.654 |
| 10 | 4.165 | 14350.547 | 5.511 | 10128.682 |
| 12 | 5.184 | 11455.976 | 5.274 | 11653.893 |

Peak:

- `LIKE`: `5.184 QPS` at `c=12`
- `MATCH`: `5.704 QPS` at `c=8`

### per-query-pool

| Concurrency | LIKE QPS | LIKE p95 (ms) | MATCH QPS | MATCH p95 (ms) |
| --- | ---: | ---: | ---: | ---: |
| 2 | 6.309 | 1401.386 | 6.438 | 1797.253 |
| 4 | 9.893 | 1525.000 | 74.586 | 162.587 |
| 6 | 12.260 | 1678.086 | 183.912 | 50.910 |
| 8 | 14.761 | 1826.737 | 296.827 | 37.950 |
| 10 | 73.902 | 870.369 | 401.557 | 38.600 |
| 12 | 73.166 | 889.796 | 405.337 | 37.138 |

Peak:

- `LIKE`: `73.902 QPS` at `c=10`
- `MATCH`: `405.337 QPS` at `c=12`

### per-query-pool peak-run completed counts

The table below shows how many times each query actually completed in the peak `per-query-pool` run:

- `LIKE`: peak run is `c=10`
- `MATCH`: peak run is `c=12`

| Query | LIKE completed | MATCH completed |
| --- | ---: | ---: |
| 1. Basic Filters / Query 2 | 110 | 20 |
| 1. Basic Filters / Query 7 | 5583 | 4850 |
| 2. Full Text Search / Query 2 | 145 | 4811 |
| 2. Full Text Search / Query 3 | 145 | 3880 |
| 2. Full Text Search / Query 4 | 143 | 406 |
| 2. Full Text Search / Query 5 | 145 | 5876 |
| 2. Full Text Search / Query 6 | 150 | 4255 |
| 2. Full Text Search / Query 7 | 151 | 5637 |
| 4. Relationship Traversal / Depth 1 / Query 4 | 46 | 37 |
| 5. JSON Attribute Queries / Query 6 | 44 | 7288 |

### Conclusions

- `shared-pool` measures a mixed request stream sharing the same worker pool.
- `per-query-pool` measures independent per-query traffic sources with a shared concurrency cap.
- Under `shared-pool`, `MATCH` is only slightly better than `LIKE`:
  - `LIKE`: `5.184 QPS`
  - `MATCH`: `5.704 QPS`
- Under `per-query-pool`, the difference becomes much larger:
  - `LIKE`: `73.902 QPS`
  - `MATCH`: `405.337 QPS`
- The big gap comes from preventing a few slow queries from monopolizing the whole mixed worker pool.

### per-query-pool high-concurrency rerun on 2 TiDB

After scaling TiDB from `1` to `2`, the `per-query-pool` benchmark was rerun only on the higher concurrency levels: `8 / 10 / 12 / 16`.

Result files:

- `bench/results/assets3_like_per_query_qps_benchmark_2tidb_20260422.json`
- `bench/results/assets3_match_per_query_qps_benchmark_2tidb_20260422.json`

| Concurrency | LIKE QPS | LIKE p95 (ms) | MATCH QPS | MATCH p95 (ms) |
| --- | ---: | ---: | ---: | ---: |
| 8 | 14.246 | 1822.749 | 334.702 | 35.288 |
| 10 | 72.774 | 896.049 | 473.016 | 32.004 |
| 12 | 73.570 | 852.058 | 472.085 | 32.985 |
| 16 | 73.160 | 864.650 | 483.032 | 36.222 |

Takeaway:

- Adding the second TiDB barely changed `LIKE per-query-pool`; it still saturates around `73 QPS`.
- `MATCH per-query-pool` benefits more from the extra TiDB front-end capacity:
  - previous peak on 1 TiDB: `405.337 QPS`
  - new peak on 2 TiDB: `483.032 QPS`
