# JSM Workload QPS Benchmark Results

This document records the AWS-internal QPS benchmark for the materialized `/Users/jin/Downloads/workload_queries.sql` read-only corpus.

- Target database: `jsm_assets3`
- Corpus: `bench/workload_smoke_corpus.json`
- Benchmark client: Kubernetes pod `workload-bench-client` in the same EKS cluster
- TiDB endpoint: `tici-demo-s3-tidb:4000`
- Benchmark mode: `shared-pool`, weighted by the materialized query weights
- Run duration: `600s` per concurrency level, with `15s` pause between levels
- Current cluster shape: `6 TiDB`, `4 TiKV`, `3 TiFlash`, `1 TiCDC`
- Current result JSON files: `bench/results/workload_qps_shared_6tidb4tikv_c*_600s_20260428.json`

## Run Configurations

| Run | Cluster shape | Nodegroups | Duration | Result files |
| --- | --- | --- | --- | --- |
| 1 TiDB run | `1 TiDB / 3 TiKV / 3 TiFlash / 1 TiCDC` | `node16c32=3`, `node-tikv=3`, `node-tiflash=3` | `600s` per concurrency | `bench/results/workload_qps_shared_c*_600s_20260428.json` |
| 3 TiDB run | `3 TiDB / 3 TiKV / 3 TiFlash / 1 TiCDC` | `node16c32=4`, `node-tikv=3`, `node-tiflash=3` | `600s` per concurrency | `bench/results/workload_qps_shared_3tidb_c*_600s_20260428.json` |
| 6 TiDB / 4 TiKV run | `6 TiDB / 4 TiKV / 3 TiFlash / 1 TiCDC` | `node16c32=7`, `node-tikv=4`, `node-tiflash=3` | `600s` per concurrency | `bench/results/workload_qps_shared_6tidb4tikv_c*_600s_20260428.json` |

## Result Validation

All checked result files met the expected benchmark correctness criteria:

| Run set | Files checked | Query patterns per file | Errors | Row-count mismatches | Zero-completed query patterns |
| --- | ---: | ---: | ---: | ---: | ---: |
| 6 TiDB / 4 TiKV 600s | 5 | 49 | 0 | 0 | 0 |
| 3 TiDB 600s | 5 | 49 | 0 | 0 | 0 |
| 1 TiDB 600s | 5 | 49 | 0 | 0 | 0 |

## 6 TiDB / 4 TiKV 10-Minute Run

| Concurrency | Completed | QPS | Avg ms | P50 ms | P95 ms | P99 ms | Errors | Mismatches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 9,533,013 | 15884.60 | 3.15 | 1.56 | 8.26 | 19.55 | 0 | 0 |
| 100 | 11,528,809 | 19209.75 | 5.20 | 1.76 | 15.07 | 54.23 | 0 | 0 |
| 200 | 13,863,110 | 23090.57 | 8.65 | 3.65 | 28.27 | 91.28 | 0 | 0 |
| 350 | 14,568,397 | 24262.40 | 14.41 | 6.49 | 50.34 | 129.64 | 0 | 0 |
| 500 | 14,613,995 | 24322.82 | 20.52 | 11.21 | 65.53 | 146.83 | 0 | 0 |

## Findings

- Peak throughput in the current run was at `500` clients: `24322.82 QPS`; `350` clients was effectively the same at `24262.40 QPS`.
- Compared with the 3 TiDB run, QPS improved by `1.31x` to `1.65x` depending on concurrency.
- Compared with the 1 TiDB run, the current run improved QPS by `2.81x` to `6.14x` depending on concurrency.
- New TiDB connections were evenly distributed across six TiDB pods before the run: `103 / 94 / 98 / 102 / 91 / 112` over 600 connection attempts.
- This run started soon after adding the fourth TiKV. At the `100` client check, the new TiKV had begun receiving regions and leaders but was not yet balanced with the older TiKV nodes. Treat this run as "scale-out immediately followed by benchmark", not a post-rebalance steady-state TiKV result.
- During the `100` client check, TiDB CPU was spread across all six TiDB pods, TiFlash CPU was active on all three TiFlash pods, and the benchmark pod was around `1.1` CPU core. The benchmark client was not CPU-bound.

## QPS Comparison

| Concurrency | 1 TiDB / 3 TiKV QPS | 3 TiDB / 3 TiKV QPS | 6 TiDB / 4 TiKV QPS | vs 3 TiDB | 6 TiDB P95 ms |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 5661.59 | 12163.00 | 15884.60 | 1.31x | 8.26 |
| 100 | 5525.04 | 14943.23 | 19209.75 | 1.29x | 15.07 |
| 200 | 5001.71 | 15373.72 | 23090.57 | 1.50x | 28.27 |
| 350 | 4362.19 | 15139.13 | 24262.40 | 1.60x | 50.34 |
| 500 | 3959.89 | 14710.67 | 24322.82 | 1.65x | 65.53 |

## Query Mix At 500 Clients

| Pattern | Queries | Weight | Completed | QPS |
| --- | ---: | ---: | ---: | ---: |
| Schema/metadata queries | 27 | 2,322,110 | 14,060,967 | 23402.38 |
| obj_new queries | 15 | 50,297 | 303,926 | 505.84 |
| obj_relationship (original) queries | 2 | 20,803 | 125,760 | 209.31 |
| obj_relationship_new queries | 3 | 19,553 | 117,994 | 196.38 |
| FTS (MATCH) | 2 | 863 | 5,348 | 8.90 |

## Slowest Queries At 500 Clients

| Query | Pattern | Completed | QPS | P50 ms | P95 ms | P99 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| obj_new_queries_q14 | obj_new queries | 2,672 | 4.45 | 1212.02 | 1744.03 | 1919.91 |
| obj_new_queries_q11 | obj_new queries | 3,437 | 5.72 | 1216.34 | 1734.39 | 1953.89 |
| obj_new_queries_q12 | obj_new queries | 3,229 | 5.37 | 1212.85 | 1734.03 | 1930.50 |
| obj_new_queries_q15 | obj_new queries | 2,518 | 4.19 | 268.47 | 1077.34 | 1668.82 |
| obj_new_queries_q10 | obj_new queries | 5,297 | 8.82 | 225.22 | 899.34 | 1619.81 |
| fts_match_q2 | FTS (MATCH) | 2,659 | 4.43 | 87.36 | 290.01 | 480.09 |
| obj_new_queries_q13 | obj_new queries | 2,712 | 4.51 | 87.40 | 280.12 | 463.30 |
| obj_new_queries_q5 | obj_new queries | 10,133 | 16.86 | 150.81 | 259.84 | 308.77 |
| fts_match_q1 | FTS (MATCH) | 2,689 | 4.47 | 42.19 | 255.56 | 419.14 |
| obj_relationship_new_queries_q4 | obj_relationship_new queries | 8,223 | 13.69 | 135.42 | 238.84 | 285.12 |

## Previous 3 TiDB 10-Minute Run

| Concurrency | Completed | QPS | Avg ms | P50 ms | P95 ms | P99 ms | Errors | Mismatches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 7,297,994 | 12163.00 | 4.11 | 2.69 | 9.30 | 22.97 | 0 | 0 |
| 100 | 8,968,568 | 14943.23 | 6.69 | 4.13 | 18.83 | 40.78 | 0 | 0 |
| 200 | 9,225,998 | 15373.72 | 13.00 | 8.54 | 35.41 | 72.93 | 0 | 0 |
| 350 | 9,084,878 | 15139.13 | 23.11 | 15.47 | 63.16 | 126.77 | 0 | 0 |
| 500 | 8,831,063 | 14710.67 | 33.95 | 23.60 | 90.83 | 172.11 | 0 | 0 |

## Previous 1 TiDB 10-Minute Run

| Concurrency | Completed | QPS | Avg ms | P50 ms | P95 ms | P99 ms | Errors | Mismatches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 3,397,512 | 5661.59 | 8.83 | 5.68 | 24.75 | 50.64 | 0 | 0 |
| 100 | 3,315,474 | 5525.04 | 18.09 | 12.83 | 46.56 | 90.87 | 0 | 0 |
| 200 | 3,001,856 | 5001.71 | 39.97 | 29.17 | 101.44 | 185.64 | 0 | 0 |
| 350 | 2,618,434 | 4362.19 | 80.18 | 62.30 | 193.28 | 357.35 | 0 | 0 |
| 500 | 2,376,587 | 3959.89 | 126.19 | 100.50 | 297.36 | 561.11 | 0 | 0 |

## Notes

- The shared-pool query mix is weight-driven, so the workload is dominated by schema/metadata queries. Use `per-query-pool` mode if each query should have independent worker pressure.
- Scaling TiDB continues to move the saturation point upward for this workload. The 6 TiDB run stayed near or above `23k QPS` from `200` through `500` clients.
