# JSM Workload QPS Benchmark Results

This document records the AWS-internal QPS benchmark for the materialized `/Users/jin/Downloads/workload_queries.sql` read-only corpus.

- Target database: `jsm_assets3`
- Corpus: `bench/workload_smoke_corpus.json`
- Benchmark client: Kubernetes pod `workload-bench-client` in the same EKS cluster
- TiDB endpoint: `tici-demo-s3-tidb:4000`
- Benchmark mode: `shared-pool`, weighted by the materialized query weights
- Run duration: `600s` per concurrency level, with `15s` pause between levels
- Current cluster shape: `10 TiDB`, `6 TiKV`, `30 TiFlash`, `1 TiCDC`
- Current result JSON files: `bench/results/workload_qps_shared_10tidb6tikv30tiflash_c*_600s_20260429.json`

## Run Configurations

| Run | Cluster shape | Nodegroups | Duration | Result files |
| --- | --- | --- | --- | --- |
| 1 TiDB run | `1 TiDB / 3 TiKV / 3 TiFlash / 1 TiCDC` | `node16c32=3`, `node-tikv=3`, `node-tiflash=3` | `600s` per concurrency | `bench/results/workload_qps_shared_c*_600s_20260428.json` |
| 3 TiDB run | `3 TiDB / 3 TiKV / 3 TiFlash / 1 TiCDC` | `node16c32=4`, `node-tikv=3`, `node-tiflash=3` | `600s` per concurrency | `bench/results/workload_qps_shared_3tidb_c*_600s_20260428.json` |
| 6 TiDB / 4 TiKV run | `6 TiDB / 4 TiKV / 3 TiFlash / 1 TiCDC` | `node16c32=7`, `node-tikv=4`, `node-tiflash=3` | `600s` per concurrency | `bench/results/workload_qps_shared_6tidb4tikv_c*_600s_20260428.json` |
| 10 TiDB / 6 TiKV / 30 TiFlash run | `10 TiDB / 6 TiKV / 30 TiFlash / 1 TiCDC` | `node16c32=16`, `node-tikv=6`, `node-tiflash=30` | `600s` per concurrency | `bench/results/workload_qps_shared_10tidb6tikv30tiflash_c*_600s_20260429.json` |

## Result Validation

All checked result files met the expected benchmark correctness criteria:

| Run set | Files checked | Query patterns per file | Errors | Row-count mismatches | Zero-completed query patterns |
| --- | ---: | ---: | ---: | ---: | ---: |
| 10 TiDB / 6 TiKV / 30 TiFlash 600s | 5 | 49 | 0 | 0 | 0 |
| 6 TiDB / 4 TiKV 600s | 5 | 49 | 0 | 0 | 0 |
| 3 TiDB 600s | 5 | 49 | 0 | 0 | 0 |
| 1 TiDB 600s | 5 | 49 | 0 | 0 | 0 |

## 10 TiDB / 6 TiKV / 30 TiFlash 10-Minute Run

| Concurrency | Completed | QPS | Avg ms | P50 ms | P95 ms | P99 ms | Errors | Mismatches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 9,509,290 | 15800.72 | 3.15 | 1.51 | 6.46 | 15.43 | 0 | 0 |
| 100 | 13,077,131 | 21443.15 | 4.59 | 1.75 | 17.80 | 32.07 | 0 | 0 |
| 200 | 15,453,099 | 25454.47 | 7.76 | 2.21 | 36.83 | 55.74 | 0 | 0 |
| 350 | 18,354,624 | 30525.40 | 11.44 | 2.32 | 51.20 | 94.59 | 0 | 0 |
| 500 | 17,737,586 | 29430.01 | 16.92 | 3.50 | 33.19 | 237.59 | 0 | 0 |

## 6 TiDB / 4 TiKV 10-Minute Run

| Concurrency | Completed | QPS | Avg ms | P50 ms | P95 ms | P99 ms | Errors | Mismatches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 9,533,013 | 15884.60 | 3.15 | 1.56 | 8.26 | 19.55 | 0 | 0 |
| 100 | 11,528,809 | 19209.75 | 5.20 | 1.76 | 15.07 | 54.23 | 0 | 0 |
| 200 | 13,863,110 | 23090.57 | 8.65 | 3.65 | 28.27 | 91.28 | 0 | 0 |
| 350 | 14,568,397 | 24262.40 | 14.41 | 6.49 | 50.34 | 129.64 | 0 | 0 |
| 500 | 14,613,995 | 24322.82 | 20.52 | 11.21 | 65.53 | 146.83 | 0 | 0 |

## Findings

- Peak throughput in the current run was at `350` clients: `30525.40 QPS`. The `500` client point was slightly lower at `29430.01 QPS` and had a higher `p99` tail.
- Compared with the 6 TiDB / 4 TiKV run, QPS improved by `0.99x` to `1.33x` depending on concurrency; the largest gain was at `350` clients.
- Compared with the 3 TiDB run, the current run improved QPS by `1.30x` to `2.02x` depending on concurrency.
- All current-run result files had `0` execution errors, `0` row-count mismatches, `0` warmup mismatches, and `0` zero-completed query patterns.
- This run followed the TiFlash scale-out to `30` replicas and FULLTEXT index rebuild. The shared-pool workload is still dominated by schema/metadata queries, so this document should not be used alone to judge FTS scalability.

## QPS Comparison

| Concurrency | 1 TiDB / 3 TiKV QPS | 3 TiDB / 3 TiKV QPS | 6 TiDB / 4 TiKV QPS | 10 TiDB / 6 TiKV / 30 TiFlash QPS | vs 6 TiDB | Current P95 ms |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 5661.59 | 12163.00 | 15884.60 | 15800.72 | 0.99x | 6.46 |
| 100 | 5525.04 | 14943.23 | 19209.75 | 21443.15 | 1.12x | 17.80 |
| 200 | 5001.71 | 15373.72 | 23090.57 | 25454.47 | 1.10x | 36.83 |
| 350 | 4362.19 | 15139.13 | 24262.40 | 30525.40 | 1.26x | 51.20 |
| 500 | 3959.89 | 14710.67 | 24322.82 | 29430.01 | 1.21x | 33.19 |

## Query Mix At 500 Clients

| Pattern | Queries | Weight | Completed | QPS |
| --- | ---: | ---: | ---: | ---: |
| Schema/metadata queries | 27 | 2,322,110 | 17,065,716 | 28315.25 |
| obj_new queries | 15 | 50,297 | 369,146 | 612.48 |
| obj_relationship (original) queries | 2 | 20,803 | 152,676 | 253.32 |
| obj_relationship_new queries | 3 | 19,553 | 143,618 | 238.29 |
| FTS (MATCH) | 2 | 863 | 6,430 | 10.67 |

## Slowest Queries At 500 Clients

| Query | Pattern | Completed | QPS | P50 ms | P95 ms | P99 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| obj_new_queries_q12 | obj_new queries | 3,929 | 6.52 | 3935.28 | 50491.70 | 95481.75 |
| obj_new_queries_q14 | obj_new queries | 3,176 | 5.27 | 3965.14 | 47779.25 | 93808.42 |
| obj_new_queries_q11 | obj_new queries | 4,177 | 6.93 | 3941.86 | 49828.81 | 92510.14 |
| obj_relationship_original_queries_q2 | obj_relationship (original) queries | 59,480 | 98.69 | 270.38 | 428.55 | 510.76 |
| obj_relationship_original_queries_q1 | obj_relationship (original) queries | 93,196 | 154.63 | 270.19 | 427.61 | 510.25 |
| obj_relationship_new_queries_q3 | obj_relationship_new queries | 65,260 | 108.28 | 253.25 | 408.69 | 481.30 |
| obj_relationship_new_queries_q2 | obj_relationship_new queries | 68,282 | 113.29 | 254.97 | 408.44 | 479.94 |
| obj_relationship_new_queries_q4 | obj_relationship_new queries | 10,076 | 16.72 | 253.76 | 406.87 | 478.89 |
| obj_new_queries_q10 | obj_new queries | 6,455 | 10.71 | 103.87 | 202.84 | 263.16 |
| obj_new_queries_q7 | obj_new queries | 9,447 | 15.67 | 18.24 | 91.08 | 163.34 |

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
- Scaling TiDB/TiKV/TiFlash moved the peak to about `30.5k QPS` for this workload. At `500` clients, the long tail became worse even though median latency stayed low.
