# jsm_assets3 LIKE vs MATCH QPS Benchmark Results

This document records the AWS-internal `LIKE` vs `MATCH AGAINST` QPS benchmark for the 10-query corpus derived from `jsm_assets3_uuid_fixed_query_run.md`.

## Workload

- Database: `jsm_assets3`
- TiDB endpoint: `tici-demo-s3-tidb:4000`
- Benchmark mode: `per-query-pool`
- Duration: `300s` per worker point
- Driver: `bench/go_qps_bench/main.go`
- `MATCH` session settings:
  - `set tidb_enforce_mpp=on`
  - `set tiflash_hash_join_version=optimized`

The worker-specific corpus files duplicate the 10 logical queries into independent query slots, so the corpus length equals the requested worker count.

## Latest Run: 10 TiDB / 6 TiKV / 30 TiFlash After FULLTEXT Rebuild

Preparation:

- Scaled the cluster to `10 TiDB / 6 TiKV / 30 TiFlash / 1 TiCDC`.
- Dropped and recreated all `jsm_assets2.obj_new` and `jsm_assets3.obj_new` FULLTEXT indexes after TiFlash scale-out.
- During the rebuild, `tici-worker` hit OOM while building `jsm_assets2.obj_new.idx_fts_22`; the DDL was cancelled, `tici-worker` was moved to a `node-tiflash` node with a `56Gi` memory limit, and the index rebuild was rerun successfully.
- Verified the following FULLTEXT indexes on both `jsm_assets2.obj_new` and `jsm_assets3.obj_new`:
  - `idx_fts_1(text_value_1) WITH PARSER NGRAM`
  - `idx_fts_4(text_value_4) WITH PARSER NGRAM`
  - `idx_fts_5(text_value_5) WITH PARSER NGRAM`
  - `idx_fts_7(text_value_7) WITH PARSER NGRAM`
  - `idx_fts_20(text_value_20) WITH PARSER NGRAM`
  - `idx_fts_22(text_value_22) WITH PARSER NGRAM`
  - `idx_fts_label(label) WITH PARSER NGRAM`

Result files:

- LIKE:
  - `bench/results/assets3_like_vs_match_like_per_query_10tidb6tikv30tiflash_rebuilt_20workers_5min_20260429.json`
  - `bench/results/assets3_like_vs_match_like_per_query_10tidb6tikv30tiflash_rebuilt_30workers_5min_20260429.json`
  - `bench/results/assets3_like_vs_match_like_per_query_10tidb6tikv30tiflash_rebuilt_50workers_5min_20260429.json`
  - `bench/results/assets3_like_vs_match_like_per_query_10tidb6tikv30tiflash_rebuilt_80workers_5min_20260429.json`
  - `bench/results/assets3_like_vs_match_like_per_query_10tidb6tikv30tiflash_rebuilt_100workers_5min_20260429.json`
- MATCH:
  - `bench/results/assets3_like_vs_match_match_per_query_10tidb6tikv30tiflash_rebuilt_20workers_5min_20260429.json`
  - `bench/results/assets3_like_vs_match_match_per_query_10tidb6tikv30tiflash_rebuilt_30workers_5min_20260429.json`
  - `bench/results/assets3_like_vs_match_match_per_query_10tidb6tikv30tiflash_rebuilt_50workers_5min_20260429.json`
  - `bench/results/assets3_like_vs_match_match_per_query_10tidb6tikv30tiflash_rebuilt_80workers_5min_20260429.json`
  - `bench/results/assets3_like_vs_match_match_per_query_10tidb6tikv30tiflash_rebuilt_100workers_5min_20260429.json`

Validation:

- All `10` completed runs had `0` execution errors.
- All `10` completed runs had `0` row-count mismatches.
- All `10` completed runs had `0` warmup row-count mismatches.
- All `10` completed runs had `0` zero-completed query slots.

| Workers | LIKE QPS | LIKE p50 (ms) | LIKE p95 (ms) | LIKE p99 (ms) | MATCH QPS | MATCH p50 (ms) | MATCH p95 (ms) | MATCH p99 (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 187.359 | 17.274 | 292.008 | 804.979 | 1414.651 | 7.391 | 17.815 | 118.850 |
| 30 | 203.684 | 26.575 | 405.962 | 1132.882 | 1508.053 | 8.829 | 36.814 | 191.826 |
| 50 | 218.976 | 38.742 | 670.577 | 1815.367 | 2583.429 | 8.410 | 32.677 | 175.613 |
| 80 | 218.979 | 62.080 | 1093.819 | 2689.260 | 2725.777 | 10.799 | 97.863 | 268.550 |
| 100 | 201.332 | 79.883 | 1440.951 | 3282.266 | 3369.796 | 10.176 | 90.247 | 269.282 |

Latest-run findings:

- `LIKE` peak: `218.979 QPS` at `80` workers. The `50` worker point was effectively the same at `218.976 QPS`, and `100` workers dropped to `201.332 QPS`.
- `MATCH` peak: `3369.796 QPS` at `100` workers.
- Peak-to-peak, `MATCH` reached `15.39x` the `LIKE` throughput after scaling to `30` TiFlash and rebuilding the FULLTEXT indexes.
- `MATCH` scaled strongly from `30` to `100` workers in this run, while `LIKE` flattened after `50` workers and developed a much larger tail.

Latest peak-run completed counts by logical query:

| Query | LIKE completed at 80 workers | MATCH completed at 100 workers |
| --- | ---: | ---: |
| 1. Basic Filters / Query 2 | 2,768 | 421 |
| 1. Basic Filters / Query 7 | 45,530 | 125,920 |
| 2. Full Text Search / Query 2 | 2,867 | 112,318 |
| 2. Full Text Search / Query 3 | 2,807 | 107,958 |
| 2. Full Text Search / Query 4 | 2,739 | 7,762 |
| 2. Full Text Search / Query 5 | 2,862 | 114,109 |
| 2. Full Text Search / Query 6 | 2,749 | 90,135 |
| 2. Full Text Search / Query 7 | 2,855 | 143,400 |
| 4. Relationship Traversal / Depth 1 / Query 4 | 938 | 867 |
| 5. JSON Attribute Queries / Query 6 | 351 | 325,607 |

## Latest Run: 6 TiFlash After FULLTEXT Rebuild

Preparation:

- Scaled TiFlash from `3` to `6` replicas.
- Scaled `node-tiflash` from `3` to `6` nodes.
- Dropped and recreated all `jsm_assets3.obj_new` FULLTEXT indexes after scale-out:
  - `idx_fts_1(text_value_1) WITH PARSER NGRAM`
  - `idx_fts_4(text_value_4) WITH PARSER NGRAM`
  - `idx_fts_5(text_value_5) WITH PARSER NGRAM`
  - `idx_fts_7(text_value_7) WITH PARSER NGRAM`
  - `idx_fts_20(text_value_20) WITH PARSER NGRAM`
  - `idx_fts_22(text_value_22) WITH PARSER NGRAM`
  - `idx_fts_label(label) WITH PARSER NGRAM`

Cluster shape:

- `6 TiDB / 4 TiKV / 6 TiFlash / 1 TiCDC`

Result files:

- LIKE:
  - `bench/results/assets3_like_vs_match_like_per_query_6tiflash_rebuilt_20workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_like_per_query_6tiflash_rebuilt_30workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_like_per_query_6tiflash_rebuilt_50workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_like_per_query_6tiflash_rebuilt_80workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_like_per_query_6tiflash_rebuilt_100workers_5min_20260428.json`
- MATCH:
  - `bench/results/assets3_like_vs_match_match_per_query_6tiflash_rebuilt_20workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_match_per_query_6tiflash_rebuilt_30workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_match_per_query_6tiflash_rebuilt_50workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_match_per_query_6tiflash_rebuilt_80workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_match_per_query_6tiflash_rebuilt_100workers_5min_20260428.json`

Validation:

- All completed runs had `0` execution errors.
- All completed runs had `0` row-count mismatches.
- All completed runs had `0` warmup row-count mismatches.
- All completed runs had `0` zero-completed query slots.

| Workers | LIKE QPS | LIKE p50 (ms) | LIKE p95 (ms) | LIKE p99 (ms) | MATCH QPS | MATCH p50 (ms) | MATCH p95 (ms) | MATCH p99 (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 168.426 | 13.412 | 807.392 | 2069.140 | 1448.716 | 7.400 | 21.638 | 113.287 |
| 30 | 218.335 | 14.177 | 1076.277 | 1696.201 | 1227.267 | 12.693 | 50.411 | 141.713 |
| 50 | 286.084 | 16.503 | 1585.980 | 2760.051 | 1315.689 | 18.344 | 93.049 | 212.377 |
| 80 | 437.923 | 17.654 | 40.502 | 4269.473 | 1013.220 | 34.844 | 226.415 | 522.544 |
| 100 | 280.965 | 37.063 | 4299.665 | 6128.032 | 1073.616 | 39.003 | 273.333 | 589.341 |

Latest-run findings:

- `LIKE` peak: `437.923 QPS` at `80` workers.
- `MATCH` peak: `1448.716 QPS` at `20` workers.
- Peak-to-peak, `MATCH` reached `3.31x` the `LIKE` throughput after TiFlash scale-out and FULLTEXT index rebuild.
- `MATCH` stayed above `1000 QPS` through `100` workers, but its best point was still the lowest tested concurrency.
- `LIKE` remained dominated by one very fast zero-row label query plus a long slow tail; aggregate p95 can look low even when p99 remains multi-second.

Latest peak-run completed counts by logical query:

| Query | LIKE completed at 80 workers | MATCH completed at 20 workers |
| --- | ---: | ---: |
| 1. Basic Filters / Query 2 | 581 | 120 |
| 1. Basic Filters / Query 7 | 127,643 | 71,524 |
| 2. Full Text Search / Query 2 | 659 | 42,238 |
| 2. Full Text Search / Query 3 | 663 | 32,042 |
| 2. Full Text Search / Query 4 | 671 | 4,641 |
| 2. Full Text Search / Query 5 | 653 | 78,528 |
| 2. Full Text Search / Query 6 | 699 | 30,816 |
| 2. Full Text Search / Query 7 | 679 | 61,891 |
| 4. Relationship Traversal / Depth 1 / Query 4 | 287 | 169 |
| 5. JSON Attribute Queries / Query 6 | 341 | 114,680 |

## Previous Run: 3 TiFlash Before Rebuild

Cluster shape:

- `6 TiDB / 4 TiKV / 3 TiFlash / 1 TiCDC`

Result files:

- LIKE:
  - `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_20workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_30workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_50workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_80workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_100workers_5min_20260428.json`
- MATCH:
  - `bench/results/assets3_like_vs_match_match_per_query_6tidb4tikv_20workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_match_per_query_6tidb4tikv_30workers_5min_20260428.json`
  - `bench/results/assets3_like_vs_match_match_per_query_6tidb4tikv_50workers_5min_20260428.json`

| Workers | LIKE QPS | LIKE p50 (ms) | LIKE p95 (ms) | LIKE p99 (ms) | MATCH QPS | MATCH p50 (ms) | MATCH p95 (ms) | MATCH p99 (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 162.955 | 13.034 | 1076.288 | 1763.978 | 592.830 | 18.631 | 69.611 | 214.706 |
| 30 | 193.308 | 16.036 | 1481.551 | 2480.825 | 441.561 | 35.077 | 177.551 | 361.096 |
| 50 | 343.345 | 13.586 | 25.971 | 3801.591 | 363.723 | 69.455 | 350.828 | 563.993 |
| 80 | 263.738 | 30.978 | 47.562 | 7114.949 | not run | - | - | - |
| 100 | 353.829 | 29.743 | 42.234 | 9283.692 | not run | - | - | - |

Previous-run findings:

- `LIKE` peak: `353.829 QPS` at `100` workers.
- `MATCH` peak: `592.830 QPS` at `20` workers.
- `MATCH 50 workers` dropped below `MATCH 30 workers`, so `MATCH 80/100 workers` were intentionally skipped in that run.

## Peak Comparison

| Run | LIKE peak | MATCH peak | MATCH / LIKE |
| --- | ---: | ---: | ---: |
| 3 TiFlash before rebuild | 353.829 QPS | 592.830 QPS | 1.68x |
| 6 TiFlash after FULLTEXT rebuild | 437.923 QPS | 1448.716 QPS | 3.31x |
| 30 TiFlash after FULLTEXT rebuild | 218.979 QPS | 3369.796 QPS | 15.39x |
