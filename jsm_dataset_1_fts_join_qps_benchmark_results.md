# Dataset 1 FTS vs LIKE + JOIN QPS Benchmark

## 本轮范围

- 客户端：AWS workstation
- 压测程序：Go
- 入口：workstation 本地 HAProxy，后端 `3` 个 TiDB
- 数据库：`jsm_testcase2`
- FTS corpus：[bench/fts_join_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/fts_join_qps_corpus.json)
- LIKE corpus：[bench/fts_join_like_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/fts_join_like_qps_corpus.json)
- FTS 结果 JSON：[bench/results/fts_join_qps_benchmark_go_haproxy_20260421_1908.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_qps_benchmark_go_haproxy_20260421_1908.json)
- LIKE 结果 JSON：[bench/results/fts_join_like_qps_benchmark_go_haproxy_20260421_2250.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/fts_join_like_qps_benchmark_go_haproxy_20260421_2250.json)

两轮 query 都是正式查询，不是 `EXPLAIN ANALYZE`。每条连接初始化时都会设置：

```sql
set tidb_enforce_mpp=on;
set tiflash_hash_join_version='optimized';
```

其中：
- `FTS` 版本使用 `MATCH ... AGAINST`
- `LIKE` 版本把同一组过滤条件改成 `lower(o1.text_value_x) like '%...%'`
- `LIKE` 版本已经抽查过 `EXPLAIN`，`o1` 这一支走的是 `mpp[tiflash]` 下的 `TableRangeScan + Selection like(...)`，不是 FTS 索引

## Query 组成

这轮对比使用同一组 `10` 条 `obj_new + obj_relationship_new + JOIN + ORDER BY + LIMIT` query，只变过滤写法。

- `text_value_7`：`1` 条，`10%`
- `text_value_1`：`3` 条，`30%`
- `text_value_4`：`3` 条，`30%`
- `text_value_5`：`3` 条，`30%`

每条 query 权重相同，单条 query 百分比都是 `10%`。

## 实际 Query 集合

| Query | 列 | Workspace | FTS 条件 | LIKE 条件 | Row Count |
| --- | --- | --- | --- | --- | ---: |
| `q1` | `text_value_7` | `8a6526e6-...` | `match(o1.text_value_7) against('Fagor' in boolean mode)` | `lower(o1.text_value_7) like '%fagor%'` | `1000` |
| `q4` | `text_value_1` | `8a6526e6-...` | `match(o1.text_value_1) against('"admiral-100"' in boolean mode)` | `lower(o1.text_value_1) like '%admiral-100%'` | `1000` |
| `q5` | `text_value_1` | `9963b35f-...` | `match(o1.text_value_1) against('"franke-100"' in boolean mode)` | `lower(o1.text_value_1) like '%franke-100%'` | `1000` |
| `q10` | `text_value_1` | `00eaf117-...` | `match(o1.text_value_1) against('"admiral-10029"' in boolean mode)` | `lower(o1.text_value_1) like '%admiral-10029%'` | `21` |
| `q6` | `text_value_4` | `3b4c201d-...` | `match(o1.text_value_4) against('"morissette.test"' in boolean mode)` | `lower(o1.text_value_4) like '%morissette.test%'` | `1000` |
| `q7` | `text_value_4` | `00eaf117-...` | `match(o1.text_value_4) against('"welch.test"' in boolean mode)` | `lower(o1.text_value_4) like '%welch.test%'` | `1000` |
| `q11` | `text_value_4` | `00eaf117-...` | `match(o1.text_value_4) against('"maren.heller"' in boolean mode)` | `lower(o1.text_value_4) like '%maren.heller%'` | `0` |
| `q8` | `text_value_5` | `3b4c201d-...` | `match(o1.text_value_5) against('"royal-simonis"' in boolean mode)` | `lower(o1.text_value_5) like '%royal-simonis%'` | `12` |
| `q9` | `text_value_5` | `cafd5188-...` | `match(o1.text_value_5) against('"shelby-torp"' in boolean mode)` | `lower(o1.text_value_5) like '%shelby-torp%'` | `31` |
| `q12` | `text_value_5` | `00eaf117-...` | `match(o1.text_value_5) against('"louise-haley"' in boolean mode)` | `lower(o1.text_value_5) like '%louise-haley%'` | `8` |

完整 SQL 见对应的两个 corpus 文件。

## Warmup 对比

| Query | FTS Warmup | LIKE Warmup | Row Count |
| --- | ---: | ---: | ---: |
| `q1` | `443.854ms` | `179.537ms` | `1000` |
| `q4` | `125.635ms` | `125.234ms` | `1000` |
| `q5` | `125.210ms` | `134.382ms` | `1000` |
| `q10` | `63.838ms` | `62.942ms` | `21` |
| `q6` | `117.857ms` | `125.020ms` | `1000` |
| `q7` | `57.352ms` | `62.309ms` | `1000` |
| `q11` | `61.238ms` | `72.055ms` | `0` |
| `q8` | `116.102ms` | `115.234ms` | `12` |
| `q9` | `69.057ms` | `82.678ms` | `31` |
| `q12` | `60.149ms` | `70.774ms` | `8` |

## 总体结果对比

每档并发持续 `60s`。

| Concurrency | FTS QPS | FTS p95 | FTS p99 | LIKE QPS | LIKE p95 | LIKE p99 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2` | `14.417` | `455.005ms` | `505.996ms` | `15.712` | `216.777ms` | `239.001ms` |
| `4` | `20.450` | `569.739ms` | `688.895ms` | `20.247` | `355.226ms` | `419.928ms` |
| `6` | `22.288` | `702.252ms` | `863.458ms` | `21.977` | `510.186ms` | `591.256ms` |
| `8` | `23.403` | `820.737ms` | `992.855ms` | `22.569` | `665.028ms` | `805.396ms` |
| `10` | `23.359` | `906.967ms` | `1136.890ms` | `22.578` | `827.551ms` | `975.472ms` |

## 每条 Query 对比

下面取 `c=10` 这一档看每条 query 的表现。

| Query | FTS QPS | FTS p95 | LIKE QPS | LIKE p95 |
| --- | ---: | ---: | ---: | ---: |
| `q1` `text_value_7 = Fagor` | `2.238` | `1176.772ms` | `2.140` | `980.229ms` |
| `q4` `text_value_1 ~ "admiral-100"` | `2.669` | `752.846ms` | `2.604` | `828.550ms` |
| `q5` `text_value_1 ~ "franke-100"` | `2.619` | `717.662ms` | `2.588` | `764.424ms` |
| `q10` `text_value_1 ~ "admiral-10029"` | `2.255` | `257.778ms` | `2.157` | `273.055ms` |
| `q6` `text_value_4 ~ "morissette.test"` | `2.056` | `802.328ms` | `1.991` | `928.584ms` |
| `q7` `text_value_4 ~ "welch.test"` | `2.437` | `251.611ms` | `2.322` | `264.577ms` |
| `q11` `text_value_4 ~ "maren.heller"` | `2.122` | `276.346ms` | `2.024` | `217.147ms` |
| `q8` `text_value_5 ~ "royal-simonis"` | `2.338` | `776.920ms` | `2.322` | `897.855ms` |
| `q9` `text_value_5 ~ "shelby-torp"` | `2.338` | `662.365ms` | `2.206` | `784.880ms` |
| `q12` `text_value_5 ~ "louise-haley"` | `2.288` | `253.318ms` | `2.223` | `256.614ms` |

## 结论

- 在当前这组 `10` 条 query 上，`FTS + JOIN` 和 `LIKE + JOIN` 的总吞吐已经比较接近。
- `FTS` 的峰值大约在 `23.4 QPS`，`LIKE` 的峰值大约在 `22.6 QPS`。
- 从整体看，`LIKE` 的尾延迟更低一些，尤其在 `c=2/4/6/8/10` 这几档，`p95/p99` 都低于 `FTS`。
- 从单条 query 看，差异并不是完全单边的：
  - `q1` 上 `LIKE` 明显更轻
  - `q4/q6/q8/q9` 上 `FTS` 更有优势
  - `q10/q11/q12` 这种过滤率更高的 query，两边已经非常接近
- 这页现在展示的是同一组 query 在 `FTS` 和 `LIKE` 两种写法下的并排结果，方便直接横向对比。
