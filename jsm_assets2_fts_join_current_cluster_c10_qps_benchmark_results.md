# JSM Assets2 FTS vs LIKE + JOIN c=10 QPS Benchmark

## Run Scope

- Date: `2026-04-28`
- Cluster: `6 TiDB / 4 TiKV / 6 TiFlash / 1 TiCDC`
- Database: `jsm_assets2`
- Benchmark client: `workload-bench-client` pod
- TiDB endpoint: `tici-demo-s3-tidb:4000`
- Mode: `shared-pool`
- Concurrency: `10`
- Duration: `300s` for LIKE and `300s` for MATCH
- Workload: same `10` `obj_new + obj_relationship_new + JOIN + ORDER BY + LIMIT` queries, only text filter differs
- LIKE corpus: [bench/fts_join_like_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/fts_join_like_qps_corpus.json)
- MATCH corpus: [bench/fts_join_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/fts_join_qps_corpus.json)
- LIKE result JSON: [bench/results/fts_join_like_current_6tidb4tikv6tiflash_c10_5min_20260428.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_like_current_6tidb4tikv6tiflash_c10_5min_20260428.json)
- MATCH result JSON: [bench/results/fts_join_match_current_6tidb4tikv6tiflash_c10_5min_20260428.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_match_current_6tidb4tikv6tiflash_c10_5min_20260428.json)

Session settings:

```sql
set tidb_enforce_mpp=on;
set tiflash_hash_join_version='optimized';
```

Both runs had warmup row counts matching expected row counts. The benchmark phase also had `errors=0` and `row_count_mismatches=0`.

## Overall Result

| Type | Completed | QPS | p50 | p95 | p99 | Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LIKE + JOIN | `14,180` | `47.241` | `208.068ms` | `319.174ms` | `362.158ms` | `211.638ms` |
| MATCH + JOIN | `3,262` | `10.731` | `50.544ms` | `8,249.624ms` | `8,935.846ms` | `926.777ms` |

`LIKE + JOIN` QPS is `4.40x` of `MATCH + JOIN` in this run. `MATCH + JOIN` has lower median latency, but its tail latency is much higher because a small number of queries are slow, especially `q1 text_value_7 = Fagor`.

## Per Query Result

| Query | LIKE QPS | LIKE p95 | MATCH QPS | MATCH p95 |
| --- | ---: | ---: | ---: | ---: |
| `q1` `text_value_7 = Fagor` | `4.784` | `353.134ms` | `1.118` | `9,019.318ms` |
| `q4` `text_value_1 ~ "admiral-100"` | `4.831` | `333.412ms` | `1.125` | `253.508ms` |
| `q5` `text_value_1 ~ "franke-100"` | `4.667` | `343.069ms` | `1.125` | `287.165ms` |
| `q10` `text_value_1 ~ "admiral-10029"` | `4.484` | `242.959ms` | `1.013` | `91.438ms` |
| `q6` `text_value_4 ~ "morissette.test"` | `4.648` | `321.586ms` | `1.000` | `367.817ms` |
| `q7` `text_value_4 ~ "welch.test"` | `4.861` | `241.424ms` | `1.132` | `261.754ms` |
| `q11` `text_value_4 ~ "maren.heller"` | `4.781` | `240.937ms` | `1.046` | `12.128ms` |
| `q8` `text_value_5 ~ "royal-simonis"` | `4.544` | `321.096ms` | `1.013` | `55.558ms` |
| `q9` `text_value_5 ~ "shelby-torp"` | `4.764` | `305.422ms` | `1.069` | `56.353ms` |
| `q12` `text_value_5 ~ "louise-haley"` | `4.877` | `243.077ms` | `1.089` | `53.895ms` |

## Notes

- This run used the current `jsm_assets2.obj_new` FULLTEXT index state.
- `jsm_assets2.obj_new` FULLTEXT indexes were not rebuilt before this run.
- The existing historical `jsm_testcase2` JOIN workload result remains in [jsm_dataset_1_fts_join_qps_benchmark_results.md](/Users/jin/Desktop/jsm-query-latency-tracking/jsm_dataset_1_fts_join_qps_benchmark_results.md).
