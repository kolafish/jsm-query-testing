# JSM Workload QPS Benchmark Results

This document records the AWS-internal QPS benchmark for the materialized `/Users/jin/Downloads/workload_queries.sql` read-only corpus.

- Target database: `jsm_assets3`
- Corpus: `bench/workload_smoke_corpus.json`
- Benchmark client: Kubernetes pod `workload-bench-client` in the same EKS cluster
- TiDB endpoint: `tici-demo-s3-tidb:4000`
- Benchmark mode: `shared-pool`, weighted by the materialized query weights
- Run duration: `600s` per concurrency level, with `15s` pause between levels
- Current cluster shape: `3 TiDB`, `3 TiKV`, `3 TiFlash`, `1 TiCDC`
- Current result JSON files: `bench/results/workload_qps_shared_3tidb_c*_600s_20260428.json`

## Run Configurations

| Run | Cluster shape | Default nodegroup | Duration | Result files |
| --- | --- | --- | --- | --- |
| Previous 1 TiDB run | `1 TiDB / 3 TiKV / 3 TiFlash / 1 TiCDC` | `node16c32=3` | `600s` per concurrency | `bench/results/workload_qps_shared_c*_600s_20260428.json` |
| Current 3 TiDB run | `3 TiDB / 3 TiKV / 3 TiFlash / 1 TiCDC` | `node16c32=4` | `600s` per concurrency | `bench/results/workload_qps_shared_3tidb_c*_600s_20260428.json` |

## Result Validation

All checked result files met the expected benchmark correctness criteria:

| Run set | Files checked | Query patterns per file | Errors | Row-count mismatches | Zero-completed query patterns |
| --- | ---: | ---: | ---: | ---: | ---: |
| 3 TiDB 600s | 5 | 49 | 0 | 0 | 0 |
| 1 TiDB 600s | 5 | 49 | 0 | 0 | 0 |
| 1 TiDB 60s smoke ramp | 5 | 49 | 0 | 0 | 0 |

## 3 TiDB 10-Minute Run

| Concurrency | Completed | QPS | Avg ms | P50 ms | P95 ms | P99 ms | Errors | Mismatches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 7,297,994 | 12163.00 | 4.11 | 2.69 | 9.30 | 22.97 | 0 | 0 |
| 100 | 8,968,568 | 14943.23 | 6.69 | 4.13 | 18.83 | 40.78 | 0 | 0 |
| 200 | 9,225,998 | 15373.72 | 13.00 | 8.54 | 35.41 | 72.93 | 0 | 0 |
| 350 | 9,084,878 | 15139.13 | 23.11 | 15.47 | 63.16 | 126.77 | 0 | 0 |
| 500 | 8,831,063 | 14710.67 | 33.95 | 23.60 | 90.83 | 172.11 | 0 | 0 |

## Findings

- Peak throughput in the 3 TiDB run was at `200` clients: `15373.72 QPS`.
- `100`, `200`, and `350` clients all stayed near `15k QPS`; `500` clients dropped slightly to `14710.67 QPS` while tail latency continued to increase.
- Compared with the 1 TiDB run, QPS improved by `2.15x` to `3.71x` depending on concurrency, and p95 latency dropped materially at every concurrency level.
- The Kubernetes service distributes new TiDB connections across all three TiDB pods. A 300-connection sample returned `tidb-0:102`, `tidb-1:109`, `tidb-2:89`; during benchmark, `cluster_processlist` at `200` clients showed `80 / 70 / 56` root sessions across the three TiDB pods.
- During the `200` client run, a point-in-time `kubectl top pod` snapshot showed TiDB around `12.8 / 11.7 / 10.4` CPU cores, TiFlash around `7.6 / 7.2 / 6.3` CPU cores, the hottest TiKV pods around `8.5` CPU cores, and the benchmark pod around `0.72` CPU core. The benchmark client was not CPU-bound.

## 1 TiDB vs 3 TiDB

| Concurrency | 1 TiDB QPS | 3 TiDB QPS | QPS ratio | 1 TiDB P95 ms | 3 TiDB P95 ms |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 5661.59 | 12163.00 | 2.15x | 24.75 | 9.30 |
| 100 | 5525.04 | 14943.23 | 2.70x | 46.56 | 18.83 |
| 200 | 5001.71 | 15373.72 | 3.07x | 101.44 | 35.41 |
| 350 | 4362.19 | 15139.13 | 3.47x | 193.28 | 63.16 |
| 500 | 3959.89 | 14710.67 | 3.71x | 297.36 | 90.83 |

## Query Mix At 500 Clients

| Pattern | Queries | Weight | Completed | QPS |
| --- | ---: | ---: | ---: | ---: |
| Schema/metadata queries | 27 | 2,322,110 | 8,496,554 | 14153.44 |
| obj_new queries | 15 | 50,297 | 183,750 | 306.09 |
| obj_relationship (original) queries | 2 | 20,803 | 75,933 | 126.49 |
| obj_relationship_new queries | 3 | 19,553 | 71,614 | 119.29 |
| FTS (MATCH) | 2 | 863 | 3,212 | 5.35 |

## Slowest Queries At 500 Clients

| Query | Pattern | Completed | QPS | P50 ms | P95 ms | P99 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| obj_new_queries_q11 | obj_new queries | 2,064 | 3.44 | 623.06 | 1067.94 | 1279.82 |
| obj_new_queries_q12 | obj_new queries | 1,933 | 3.22 | 608.33 | 1023.02 | 1210.78 |
| obj_new_queries_q14 | obj_new queries | 1,577 | 2.63 | 604.49 | 1004.27 | 1243.04 |
| obj_new_queries_q10 | obj_new queries | 3,224 | 5.37 | 191.38 | 485.25 | 701.40 |
| obj_new_queries_q15 | obj_new queries | 1,557 | 2.59 | 201.19 | 477.23 | 791.25 |
| schema_metadata_queries_q3 | Schema/metadata queries | 229,502 | 382.30 | 88.33 | 293.98 | 459.10 |
| fts_match_q2 | FTS (MATCH) | 1,594 | 2.65 | 44.89 | 162.38 | 246.86 |
| schema_metadata_queries_q17 | Schema/metadata queries | 12,192 | 20.31 | 47.16 | 158.09 | 268.55 |
| obj_new_queries_q5 | obj_new queries | 6,156 | 10.26 | 50.26 | 153.03 | 245.34 |
| obj_new_queries_q13 | obj_new queries | 1,651 | 2.75 | 45.36 | 149.92 | 232.78 |

## Previous 1 TiDB 10-Minute Run

| Concurrency | Completed | QPS | Avg ms | P50 ms | P95 ms | P99 ms | Errors | Mismatches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 3,397,512 | 5661.59 | 8.83 | 5.68 | 24.75 | 50.64 | 0 | 0 |
| 100 | 3,315,474 | 5525.04 | 18.09 | 12.83 | 46.56 | 90.87 | 0 | 0 |
| 200 | 3,001,856 | 5001.71 | 39.97 | 29.17 | 101.44 | 185.64 | 0 | 0 |
| 350 | 2,618,434 | 4362.19 | 80.18 | 62.30 | 193.28 | 357.35 | 0 | 0 |
| 500 | 2,376,587 | 3959.89 | 126.19 | 100.50 | 297.36 | 561.11 | 0 | 0 |

## Previous 1 TiDB 60-Second Run

| Concurrency | Completed | QPS | Avg ms | P50 ms | P95 ms | P99 ms | Errors | Mismatches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 340,405 | 5669.74 | 8.81 | 5.80 | 23.58 | 50.11 | 0 | 0 |
| 100 | 308,450 | 5131.29 | 19.44 | 12.90 | 52.68 | 108.10 | 0 | 0 |
| 200 | 304,560 | 5063.07 | 39.32 | 29.64 | 97.96 | 178.35 | 0 | 0 |
| 350 | 255,956 | 4242.44 | 81.87 | 62.78 | 198.65 | 384.26 | 0 | 0 |
| 500 | 238,078 | 3954.28 | 125.78 | 100.80 | 287.45 | 559.22 | 0 | 0 |

## Notes

- The shared-pool query mix is weight-driven, so the workload is dominated by schema/metadata queries. Use `per-query-pool` mode if each query should have independent worker pressure.
- The 3 TiDB run shifts the saturation point upward: QPS stays near `15k` through `350` clients, while the 1 TiDB run started degrading after `50-100` clients.
