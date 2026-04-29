# JSM Assets2 FTS vs LIKE + JOIN QPS Benchmark

## Latest Run

- Date: `2026-04-29`
- Cluster: `10 TiDB / 6 TiKV / 30 TiFlash / 1 TiCDC`
- Database: `jsm_assets2`
- Benchmark client: `workload-bench-client` pod
- TiDB endpoint: `tici-demo-s3-tidb:4000`
- Mode: `shared-pool`
- Concurrency levels: `10`, `30`, `50`
- Duration: `300s` per concurrency level
- Workload: same `10` `obj_new + obj_relationship_new + JOIN + ORDER BY + LIMIT` queries, only text filter differs
- LIKE corpus: [bench/fts_join_like_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/fts_join_like_qps_corpus.json)
- MATCH corpus: [bench/fts_join_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/fts_join_qps_corpus.json)
- LIKE result JSON: [bench/results/fts_join_like_10tidb6tikv30tiflash_rebuilt_c10_30_50_5min_20260429.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_like_10tidb6tikv30tiflash_rebuilt_c10_30_50_5min_20260429.json)
- MATCH result JSON: [bench/results/fts_join_match_10tidb6tikv30tiflash_rebuilt_c10_30_50_5min_20260429.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_match_10tidb6tikv30tiflash_rebuilt_c10_30_50_5min_20260429.json)

Session settings:

```sql
set tidb_enforce_mpp=on;
set tiflash_hash_join_version='optimized';
```

Both LIKE and MATCH runs had `0` warmup row-count mismatches, `0` execution errors, `0` benchmark row-count mismatches, and `0` zero-completed query patterns.

## Overall Result

| Concurrency | LIKE Completed | LIKE QPS | LIKE p50 | LIKE p95 | LIKE p99 | MATCH Completed | MATCH QPS | MATCH p50 | MATCH p95 | MATCH p99 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | `29,401` | `97.984` | `96.353ms` | `146.972ms` | `174.747ms` | `4,669` | `15.512` | `629.210ms` | `1,541.900ms` | `1,922.084ms` |
| 30 | `37,518` | `124.959` | `246.108ms` | `416.838ms` | `486.038ms` | `6,262` | `20.723` | `1,270.073ms` | `3,856.806ms` | `5,387.293ms` |
| 50 | `39,892` | `132.832` | `391.928ms` | `668.572ms` | `777.707ms` | `6,370` | `21.062` | `1,847.721ms` | `6,877.328ms` | `10,776.704ms` |

Latest-run findings:

- `LIKE + JOIN` peaked at `132.832 QPS` at concurrency `50`.
- `MATCH + JOIN` peaked at `21.062 QPS` at concurrency `50`.
- At concurrency `50`, `LIKE + JOIN` was `6.31x` the throughput of `MATCH + JOIN`.
- `MATCH + JOIN` had much higher tail latency in this run. Several MATCH warmup queries took about `8.5s` to `10.6s`, and the benchmark p99 reached `10.777s` at concurrency `50`.

## TiDB mpp-10287 Image Rerun

After the latest run above, TiDB was temporarily changed from:

- Previous TiDB image: `gcr.io/pingcap-public/dbaas/tidb:v8.5.6-20260423-93f2dfb`
- Test TiDB image: `gcr.io/pingcap-public/dbaas/tidb:v8.5.6-20260410-mpp-10287-dev`

Only the `MATCH + JOIN` corpus was rerun. TiKV, TiFlash, FULLTEXT indexes, corpus, session settings, and cluster size stayed the same.

- Result JSON: [bench/results/fts_join_match_tidb_mpp10287_10tidb6tikv30tiflash_c10_30_50_5min_20260429.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_match_tidb_mpp10287_10tidb6tikv30tiflash_c10_30_50_5min_20260429.json)
- Validation: `0` warmup row-count mismatches, `0` execution errors, `0` benchmark row-count mismatches, and `0` zero-completed query patterns.
- Rollback target after validation: `gcr.io/pingcap-public/dbaas/tidb:v8.5.6-20260423-93f2dfb`

| Concurrency | Previous MATCH QPS | mpp-10287 MATCH QPS | Speedup | Previous p95 | mpp-10287 p95 | Previous p99 | mpp-10287 p99 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | `15.512` | `75.025` | `4.84x` | `1,541.900ms` | `693.192ms` | `1,922.084ms` | `777.942ms` |
| 30 | `20.723` | `119.697` | `5.78x` | `3,856.806ms` | `1,099.735ms` | `5,387.293ms` | `1,274.730ms` |
| 50 | `21.062` | `123.316` | `5.85x` | `6,877.328ms` | `1,334.778ms` | `10,776.704ms` | `1,540.078ms` |

At concurrency `50`, the mpp-10287 image brought `MATCH + JOIN` close to the same throughput range as `LIKE + JOIN` from the previous section: `123.316 QPS` vs `132.832 QPS`.

### mpp-10287 Per Query Result At Concurrency 50

| Query | MATCH QPS | MATCH p50 | MATCH p95 | MATCH p99 |
| --- | ---: | ---: | ---: | ---: |
| `q1` `text_value_7 = Fagor` | `12.422` | `1,331.304ms` | `1,613.265ms` | `1,790.365ms` |
| `q4` `text_value_1 ~ "admiral-100"` | `12.223` | `335.138ms` | `542.563ms` | `680.642ms` |
| `q5` `text_value_1 ~ "franke-100"` | `12.266` | `346.741ms` | `553.009ms` | `667.636ms` |
| `q10` `text_value_1 ~ "admiral-10029"` | `12.067` | `196.064ms` | `346.504ms` | `452.545ms` |
| `q6` `text_value_4 ~ "morissette.test"` | `12.402` | `373.758ms` | `621.855ms` | `757.792ms` |
| `q7` `text_value_4 ~ "welch.test"` | `12.073` | `196.988ms` | `355.987ms` | `466.102ms` |
| `q11` `text_value_4 ~ "maren.heller"` | `12.409` | `198.070ms` | `349.475ms` | `464.491ms` |
| `q8` `text_value_5 ~ "royal-simonis"` | `12.535` | `362.473ms` | `586.460ms` | `747.763ms` |
| `q9` `text_value_5 ~ "shelby-torp"` | `12.342` | `340.835ms` | `594.616ms` | `746.558ms` |
| `q12` `text_value_5 ~ "louise-haley"` | `12.578` | `197.362ms` | `352.460ms` | `478.851ms` |

## Per Query Result At Concurrency 50

| Query | LIKE QPS | LIKE p95 | LIKE p99 | MATCH QPS | MATCH p95 | MATCH p99 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `q1` `text_value_7 = Fagor` | `13.319` | `752.479ms` | `861.955ms` | `2.133` | `7,943.578ms` | `11,182.273ms` |
| `q4` `text_value_1 ~ "admiral-100"` | `13.219` | `712.897ms` | `805.609ms` | `2.169` | `7,579.791ms` | `10,931.684ms` |
| `q5` `text_value_1 ~ "franke-100"` | `13.166` | `724.751ms` | `828.698ms` | `2.133` | `8,587.710ms` | `14,379.840ms` |
| `q10` `text_value_1 ~ "admiral-10029"` | `12.983` | `309.850ms` | `375.706ms` | `2.063` | `2,081.786ms` | `3,040.503ms` |
| `q6` `text_value_4 ~ "morissette.test"` | `13.346` | `691.231ms` | `788.111ms` | `2.080` | `8,970.390ms` | `13,193.283ms` |
| `q7` `text_value_4 ~ "welch.test"` | `13.086` | `317.492ms` | `390.016ms` | `2.139` | `2,241.468ms` | `3,084.012ms` |
| `q11` `text_value_4 ~ "maren.heller"` | `13.416` | `307.066ms` | `386.636ms` | `2.053` | `1,103.794ms` | `1,761.701ms` |
| `q8` `text_value_5 ~ "royal-simonis"` | `13.396` | `677.108ms` | `786.373ms` | `2.176` | `8,367.976ms` | `11,452.816ms` |
| `q9` `text_value_5 ~ "shelby-torp"` | `13.239` | `624.364ms` | `700.467ms` | `2.096` | `6,993.549ms` | `9,419.689ms` |
| `q12` `text_value_5 ~ "louise-haley"` | `13.662` | `307.962ms` | `375.098ms` | `2.020` | `2,235.911ms` | `3,423.604ms` |

## Previous Run

Previous `2026-04-28` run shape:

- Cluster: `6 TiDB / 4 TiKV / 6 TiFlash / 1 TiCDC`
- Concurrency: `10`
- Duration: `300s` for LIKE and `300s` for MATCH
- LIKE result JSON: [bench/results/fts_join_like_current_6tidb4tikv6tiflash_c10_5min_20260428.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_like_current_6tidb4tikv6tiflash_c10_5min_20260428.json)
- MATCH result JSON: [bench/results/fts_join_match_current_6tidb4tikv6tiflash_c10_5min_20260428.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_match_current_6tidb4tikv6tiflash_c10_5min_20260428.json)

| Type | Completed | QPS | p50 | p95 | p99 | Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LIKE + JOIN | `14,180` | `47.241` | `208.068ms` | `319.174ms` | `362.158ms` | `211.638ms` |
| MATCH + JOIN | `3,262` | `10.731` | `50.544ms` | `8,249.624ms` | `8,935.846ms` | `926.777ms` |

## Notes

- This run used the rebuilt `jsm_assets2.obj_new` FULLTEXT indexes after the `30` TiFlash scale-out.
- The existing historical `jsm_testcase2` JOIN workload result remains in [jsm_dataset_1_fts_join_qps_benchmark_results.md](/Users/jin/Desktop/jsm-query-latency-tracking/jsm_dataset_1_fts_join_qps_benchmark_results.md).
