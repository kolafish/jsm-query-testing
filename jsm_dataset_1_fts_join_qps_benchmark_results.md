# Dataset 1 FTS + JOIN QPS Benchmark

## 本轮范围

- 客户端：AWS workstation
- 压测程序：Go
- 入口：workstation 本地 HAProxy，后端 3 个 TiDB
- 数据库：`jsm_testcase2`
- query corpus：[bench/fts_join_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/fts_join_qps_corpus.json)
- 结果 JSON：[bench/results/fts_join_qps_benchmark_go_haproxy_20260421_1740.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_qps_benchmark_go_haproxy_20260421_1740.json)

所有 query 都是正式查询，不是 `EXPLAIN ANALYZE`。每条连接初始化时都会设置：

```sql
set tidb_enforce_mpp=on;
set tiflash_hash_join_version='optimized';
```

## Query 组成

这轮 workload 共 9 条 query，全部是 `obj_new + obj_relationship_new + MATCH AGAINST + JOIN + ORDER BY + LIMIT` 形态。

- `text_value_7` `STANDARD FULLTEXT`：3 条
- `text_value_1` `NGRAM FULLTEXT`：2 条
- `text_value_4` `NGRAM FULLTEXT`：2 条
- `text_value_5` `NGRAM FULLTEXT`：2 条

每条 query 权重相同，query 百分比都是 `11.1%`。

## Warmup

| Query | Warmup Latency | Row Count |
| --- | ---: | ---: |
| `q1` `text_value_7 = Fagor` | `448.788ms` | `1000` |
| `q2` `text_value_7 = Sharp` | `357.486ms` | `1000` |
| `q3` `text_value_7 = Bosch` | `276.007ms` | `1000` |
| `q4` `text_value_1 ~ "admiral-100"` | `112.409ms` | `1000` |
| `q5` `text_value_1 ~ "franke-100"` | `110.091ms` | `1000` |
| `q6` `text_value_4 ~ "morissette.test"` | `104.505ms` | `1000` |
| `q7` `text_value_4 ~ "welch.test"` | `58.127ms` | `1000` |
| `q8` `text_value_5 ~ "royal-simonis"` | `100.333ms` | `12` |
| `q9` `text_value_5 ~ "shelby-torp"` | `64.082ms` | `31` |

## 总体结果

每档并发持续 `60s`。

| Concurrency | QPS | p50 | p95 | p99 | Errors | Mismatches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2` | `9.674` | `145.221ms` | `459.940ms` | `511.945ms` | `0` | `0` |
| `4` | `13.099` | `258.011ms` | `609.273ms` | `719.376ms` | `0` | `0` |
| `6` | `14.500` | `391.631ms` | `782.608ms` | `923.339ms` | `0` | `0` |
| `8` | `14.620` | `553.430ms` | `934.652ms` | `1103.614ms` | `0` | `0` |
| `10` | `14.724` | `692.818ms` | `1128.380ms` | `1301.003ms` | `0` | `0` |

## 每条 Query 观察

下面取 `c=10` 这一档看每条 query 的表现。

| Query | QPS | p95 |
| --- | ---: | ---: |
| `q1` `text_value_7 = Fagor` | `1.770` | `1328.712ms` |
| `q2` `text_value_7 = Sharp` | `1.472` | `1012.970ms` |
| `q3` `text_value_7 = Bosch` | `1.869` | `1130.319ms` |
| `q4` `text_value_1 ~ "admiral-100"` | `1.787` | `837.124ms` |
| `q5` `text_value_1 ~ "franke-100"` | `1.638` | `769.104ms` |
| `q6` `text_value_4 ~ "morissette.test"` | `1.472` | `914.934ms` |
| `q7` `text_value_4 ~ "welch.test"` | `1.737` | `275.111ms` |
| `q8` `text_value_5 ~ "royal-simonis"` | `1.572` | `842.089ms` |
| `q9` `text_value_5 ~ "shelby-torp"` | `1.406` | `773.731ms` |

## 结论

- 这轮 `FTS + JOIN` 专项 workload 在当前 `3 TiDB + 3 TiFlash` 环境下，峰值大约就在 `14.6 ~ 14.7 QPS`。
- 从 `c=6` 往上继续加并发，吞吐基本不再增长，说明当前瓶颈已经固定在数据库侧，不在客户端。
- `text_value_7` 这三条 `STANDARD FULLTEXT + JOIN` 是这轮里最重的一组，`p95` 明显最高。
- `text_value_4 ~ "welch.test"` 这一条最轻，说明 `FTS` 选择性差异会直接放大到 `JOIN` 成本上。
- 当前这轮没有报错，也没有行数漂移，结果是稳定可复现的。
