# Dataset 1 FTS + JOIN QPS Benchmark

## 本轮范围

- 客户端：AWS workstation
- 压测程序：Go
- 入口：workstation 本地 HAProxy，后端 `3` 个 TiDB
- 数据库：`jsm_testcase2`
- query corpus：[bench/fts_join_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/fts_join_qps_corpus.json)
- 结果 JSON：[bench/results/fts_join_qps_benchmark_go_haproxy_20260421_1908.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_qps_benchmark_go_haproxy_20260421_1908.json)

所有 query 都是正式查询，不是 `EXPLAIN ANALYZE`。每条连接初始化时都会设置：

```sql
set tidb_enforce_mpp=on;
set tiflash_hash_join_version='optimized';
```

## Query 组成

这轮 workload 共 `10` 条 query，全部是 `obj_new + obj_relationship_new + MATCH AGAINST + JOIN + ORDER BY + LIMIT` 形态。

- `text_value_7` `STANDARD FULLTEXT`：`1` 条，`10%`
- `text_value_1` `NGRAM FULLTEXT`：`3` 条，`30%`
- `text_value_4` `NGRAM FULLTEXT`：`3` 条，`30%`
- `text_value_5` `NGRAM FULLTEXT`：`3` 条，`30%`

每条 query 权重相同，单条 query 百分比都是 `10%`。

## 实际 Query 集合

| Query | 列 | Workspace | FTS 过滤条件 | Warmup Row Count |
| --- | --- | --- | --- | ---: |
| `q1` | `text_value_7` | `8a6526e6-...` | `match(o1.text_value_7) against('Fagor' in boolean mode)` | `1000` |
| `q4` | `text_value_1` | `8a6526e6-...` | `match(o1.text_value_1) against('"admiral-100"' in boolean mode)` | `1000` |
| `q5` | `text_value_1` | `9963b35f-...` | `match(o1.text_value_1) against('"franke-100"' in boolean mode)` | `1000` |
| `q10` | `text_value_1` | `00eaf117-...` | `match(o1.text_value_1) against('"admiral-10029"' in boolean mode)` | `21` |
| `q6` | `text_value_4` | `3b4c201d-...` | `match(o1.text_value_4) against('"morissette.test"' in boolean mode)` | `1000` |
| `q7` | `text_value_4` | `00eaf117-...` | `match(o1.text_value_4) against('"welch.test"' in boolean mode)` | `1000` |
| `q11` | `text_value_4` | `00eaf117-...` | `match(o1.text_value_4) against('"maren.heller"' in boolean mode)` | `0` |
| `q8` | `text_value_5` | `3b4c201d-...` | `match(o1.text_value_5) against('"royal-simonis"' in boolean mode)` | `12` |
| `q9` | `text_value_5` | `cafd5188-...` | `match(o1.text_value_5) against('"shelby-torp"' in boolean mode)` | `31` |
| `q12` | `text_value_5` | `00eaf117-...` | `match(o1.text_value_5) against('"louise-haley"' in boolean mode)` | `8` |

完整 SQL 见 [bench/fts_join_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/fts_join_qps_corpus.json)。

## Warmup

| Query | Warmup Latency | Row Count |
| --- | ---: | ---: |
| `q1` `text_value_7 = Fagor` | `443.854ms` | `1000` |
| `q4` `text_value_1 ~ "admiral-100"` | `125.635ms` | `1000` |
| `q5` `text_value_1 ~ "franke-100"` | `125.210ms` | `1000` |
| `q10` `text_value_1 ~ "admiral-10029"` | `63.838ms` | `21` |
| `q6` `text_value_4 ~ "morissette.test"` | `117.857ms` | `1000` |
| `q7` `text_value_4 ~ "welch.test"` | `57.352ms` | `1000` |
| `q11` `text_value_4 ~ "maren.heller"` | `61.238ms` | `0` |
| `q8` `text_value_5 ~ "royal-simonis"` | `116.102ms` | `12` |
| `q9` `text_value_5 ~ "shelby-torp"` | `69.057ms` | `31` |
| `q12` `text_value_5 ~ "louise-haley"` | `60.149ms` | `8` |

## 总体结果

每档并发持续 `60s`。

| Concurrency | QPS | p50 | p95 | p99 |
| ---: | ---: | ---: | ---: | ---: |
| `2` | `14.417` | `104.863ms` | `455.005ms` | `505.996ms` |
| `4` | `20.450` | `152.775ms` | `569.739ms` | `688.895ms` |
| `6` | `22.288` | `232.011ms` | `702.252ms` | `863.458ms` |
| `8` | `23.403` | `309.721ms` | `820.737ms` | `992.855ms` |
| `10` | `23.359` | `436.561ms` | `906.967ms` | `1136.890ms` |

## 每条 Query 观察

下面取 `c=10` 这一档看每条 query 的表现。

| Query | QPS | p95 |
| --- | ---: | ---: |
| `q1` `text_value_7 = Fagor` | `2.238` | `1176.772ms` |
| `q4` `text_value_1 ~ "admiral-100"` | `2.669` | `752.846ms` |
| `q5` `text_value_1 ~ "franke-100"` | `2.619` | `717.662ms` |
| `q10` `text_value_1 ~ "admiral-10029"` | `2.255` | `257.778ms` |
| `q6` `text_value_4 ~ "morissette.test"` | `2.056` | `802.328ms` |
| `q7` `text_value_4 ~ "welch.test"` | `2.437` | `251.611ms` |
| `q11` `text_value_4 ~ "maren.heller"` | `2.122` | `276.346ms` |
| `q8` `text_value_5 ~ "royal-simonis"` | `2.338` | `776.920ms` |
| `q9` `text_value_5 ~ "shelby-torp"` | `2.338` | `662.365ms` |
| `q12` `text_value_5 ~ "louise-haley"` | `2.288` | `253.318ms` |

## 结论

- 当前这组 `FTS + JOIN` workload 在 `workstation + Go + HAProxy + 3 TiDB` 这套跑法下，峰值大约在 `23.3 ~ 23.4 QPS`。
- 从 `c=8` 往上继续加并发，吞吐基本不再增长，当前瓶颈已经固定在数据库侧。
- `text_value_7 = Fagor` 仍然是这组里最重的一条，`p95` 最高。
- 过滤率更高的几条 query，例如 `admiral-10029`、`maren.heller`、`louise-haley`，明显更轻，`p95` 在 `250ms` 左右。
- 这轮结果反映的是当前最新的 query 集合和当前最新的专项 benchmark 数字。
