# jsm_assets3 LIKE vs MATCH QPS Benchmark Results

This document records the AWS-internal `LIKE` vs `MATCH AGAINST` QPS benchmark for the 10-query corpus derived from `jsm_assets3_uuid_fixed_query_run.md`.

## Scope

- Cluster shape: `6 TiDB / 4 TiKV / 3 TiFlash / 1 TiCDC`
- Database: `jsm_assets3`
- TiDB endpoint: `tici-demo-s3-tidb:4000`
- Benchmark mode: `per-query-pool`
- Duration: `300s` per worker point
- Driver: `bench/go_qps_bench/main.go`
- `MATCH` session settings:
  - `set tidb_enforce_mpp=on`
  - `set tiflash_hash_join_version=optimized`

The worker-specific corpus files duplicate the 10 logical queries into independent query slots, so the corpus length equals the requested worker count.

## Result Files

LIKE corpus and results:

- `bench/assets3_like_vs_match_like_qps_corpus_20workers.json`
- `bench/assets3_like_vs_match_like_qps_corpus_30workers.json`
- `bench/assets3_like_vs_match_like_qps_corpus_50workers.json`
- `bench/assets3_like_vs_match_like_qps_corpus_80workers.json`
- `bench/assets3_like_vs_match_like_qps_corpus_100workers.json`
- `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_20workers_5min_20260428.json`
- `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_30workers_5min_20260428.json`
- `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_50workers_5min_20260428.json`
- `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_80workers_5min_20260428.json`
- `bench/results/assets3_like_vs_match_like_per_query_6tidb4tikv_100workers_5min_20260428.json`

MATCH corpus and results:

- `bench/assets3_like_vs_match_match_qps_corpus_20workers.json`
- `bench/assets3_like_vs_match_match_qps_corpus_30workers.json`
- `bench/assets3_like_vs_match_match_qps_corpus_50workers.json`
- `bench/results/assets3_like_vs_match_match_per_query_6tidb4tikv_20workers_5min_20260428.json`
- `bench/results/assets3_like_vs_match_match_per_query_6tidb4tikv_30workers_5min_20260428.json`
- `bench/results/assets3_like_vs_match_match_per_query_6tidb4tikv_50workers_5min_20260428.json`

## Validation

All completed runs had:

- `0` execution errors
- `0` row-count mismatches
- `0` warmup row-count mismatches
- `0` zero-completed query slots

## QPS Summary

| Workers | LIKE QPS | LIKE p50 (ms) | LIKE p95 (ms) | LIKE p99 (ms) | MATCH QPS | MATCH p50 (ms) | MATCH p95 (ms) | MATCH p99 (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 162.955 | 13.034 | 1076.288 | 1763.978 | 592.830 | 18.631 | 69.611 | 214.706 |
| 30 | 193.308 | 16.036 | 1481.551 | 2480.825 | 441.561 | 35.077 | 177.551 | 361.096 |
| 50 | 343.345 | 13.586 | 25.971 | 3801.591 | 363.723 | 69.455 | 350.828 | 563.993 |
| 80 | 263.738 | 30.978 | 47.562 | 7114.949 | not run | - | - | - |
| 100 | 353.829 | 29.743 | 42.234 | 9283.692 | not run | - | - | - |

## Findings

- `LIKE` peak: `353.829 QPS` at `100` workers.
- `MATCH` peak: `592.830 QPS` at `20` workers.
- Peak-to-peak, `MATCH` reached `1.68x` the `LIKE` throughput on this cluster.
- `MATCH 30 workers` dropped to `441.561 QPS`; `MATCH 50 workers` dropped further to `363.723 QPS`, so `MATCH 80/100 workers` were intentionally skipped.
- `LIKE` kept improving through `100` workers, but the p99 tail latency remained very high because a few slow queries still complete infrequently.

## Peak-Run Completed Counts

The table below aggregates duplicated worker slots back to the original 10 logical queries.

| Query | LIKE completed at 100 workers | MATCH completed at 20 workers |
| --- | ---: | ---: |
| 1. Basic Filters / Query 2 | 324 | 99 |
| 1. Basic Filters / Query 7 | 106,778 | 27,818 |
| 2. Full Text Search / Query 2 | 365 | 18,675 |
| 2. Full Text Search / Query 3 | 366 | 18,549 |
| 2. Full Text Search / Query 4 | 371 | 2,751 |
| 2. Full Text Search / Query 5 | 365 | 31,417 |
| 2. Full Text Search / Query 6 | 385 | 16,643 |
| 2. Full Text Search / Query 7 | 380 | 25,624 |
| 4. Relationship Traversal / Depth 1 / Query 4 | 175 | 277 |
| 5. JSON Attribute Queries / Query 6 | 354 | 37,940 |

