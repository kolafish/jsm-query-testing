# Dataset 1 简单 QPS 压测结果

这页记录基于 dataset 1 的一版短时混合 QPS 压测结果。它不是长时间 soak test，也不是最终容量结论，目标是先验证：
- 当前 query pattern 混合后，大致能跑到什么 QPS
- 哪类 query 最先拉高 p95 / p99
- rewrite 后的 `MATCH ... AGAINST` 查询在并发下是否稳定

## 压测输入

相关文件：
- Query pattern 页面：[jsm_dataset_1_qps_patterns.md](/Users/jin/Desktop/jsm-query-latency-tracking/jsm_dataset_1_qps_patterns.md)
- Query corpus：[bench/dataset_1_qps_corpus.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/dataset_1_qps_corpus.json)
- Benchmark driver：[bench/run_dataset_1_qps_benchmark.py](/Users/jin/Desktop/jsm-query-latency-tracking/bench/run_dataset_1_qps_benchmark.py)
- 原始结果 JSON：[bench/results/dataset_1_qps_benchmark_20260421.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/dataset_1_qps_benchmark_20260421.json)

本次纳入的 pattern：
- Pattern 1：标量过滤 + 按标题排序
- Pattern 2：由原始 `LIKE '%...%'` 改写来的短语搜索
- Pattern 3：多列短语搜索，用 `UNION DISTINCT` 拼接
- Pattern 4：按自定义字段排序
- Pattern 6：直接查关系表
- Pattern 7：单跳关系遍历
- Pattern 9：数值范围过滤

权重：
- Pattern 1: `25%`
- Pattern 2: `20%`
- Pattern 3: `15%`
- Pattern 4: `15%`
- Pattern 6: `10%`
- Pattern 7: `10%`
- Pattern 9: `5%`

## 程序并发模型

这次 benchmark driver 特意按“不要让压测程序本身成为瓶颈”的思路写：
- 使用固定 worker 线程，而不是单线程串行发 SQL
- 每个 worker 在整个 run 生命周期里复用一个持久 MySQL 连接，不在循环里反复建连
- 由每个 worker 独立按权重随机抽 query 执行，避免中心调度线程串行阻塞
- 每条 query 都会 `fetchall()` 并校验返回行数，确保不是只测到“发请求”而没测到结果读取
- 在正式 run 前，先对 corpus 中每条 query 做 1 次串行 warmup

这次实际执行命令：

```bash
python3 bench/run_dataset_1_qps_benchmark.py \
  --duration 20 \
  --concurrency 1 4 8 \
  --output bench/results/dataset_1_qps_benchmark_20260421.json
```

说明：
- 每档并发跑 `20s`
- 并发档位：`1`、`4`、`8`
- 数据库连接走本地 `127.0.0.1:34006`，由 SSH + `kubectl port-forward` 转到当前 TiDB service

## Warmup 结果

所有 query 都通过了 warmup，且返回行数和预期一致。

| Query | Pattern | Warmup Latency | Row Count |
|---|---|---:|---:|
| `pattern_1_scalar_filters` | Pattern 1 | `264.768ms` | `51` |
| `pattern_2_phrase_match` | Pattern 2 | `256.606ms` | `1` |
| `pattern_3_multi_column_union` | Pattern 3 | `256.260ms` | `1` |
| `pattern_4_sort_custom_field` | Pattern 4 | `783.447ms` | `1000` |
| `pattern_6_direct_relationship` | Pattern 6 | `368.805ms` | `56` |
| `pattern_7_single_hop_reference` | Pattern 7 | `876.124ms` | `1000` |
| `pattern_9_numeric_range` | Pattern 9 | `297.287ms` | `1000` |

## 总体结果

| Concurrency | QPS | Avg | p50 | p95 | p99 | Errors | Row Count Mismatch |
|---|---:|---:|---:|---:|---:|---:|---:|
| `1` | `2.781` | `335.999ms` | `265.322ms` | `875.105ms` | `881.253ms` | `0` | `0` |
| `4` | `8.345` | `442.768ms` | `282.275ms` | `1399.619ms` | `1785.165ms` | `0` | `0` |
| `8` | `11.905` | `611.984ms` | `343.610ms` | `2549.609ms` | `3633.751ms` | `0` | `0` |

## 分 Pattern 观察

### Concurrency = 1

| Pattern | Completed | QPS | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| `pattern_7_single_hop_reference` | `5` | `0.248` | `878.257ms` | `882.712ms` | `883.380ms` |
| `pattern_6_direct_relationship` | `9` | `0.447` | `362.477ms` | `370.990ms` | `371.559ms` |
| `pattern_9_numeric_range` | `1` | `0.050` | `301.183ms` | `301.183ms` | `301.183ms` |
| `pattern_4_sort_custom_field` | `7` | `0.348` | `290.099ms` | `292.946ms` | `293.255ms` |
| `pattern_1_scalar_filters` | `14` | `0.695` | `264.887ms` | `275.230ms` | `278.467ms` |
| `pattern_3_multi_column_union` | `14` | `0.695` | `255.321ms` | `261.990ms` | `263.567ms` |
| `pattern_2_phrase_match` | `6` | `0.298` | `254.730ms` | `255.778ms` | `256.030ms` |

### Concurrency = 4

| Pattern | Completed | QPS | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| `pattern_7_single_hop_reference` | `20` | `0.965` | `1345.771ms` | `1802.625ms` | `1862.676ms` |
| `pattern_9_numeric_range` | `8` | `0.386` | `323.579ms` | `694.662ms` | `755.728ms` |
| `pattern_6_direct_relationship` | `17` | `0.820` | `381.913ms` | `660.006ms` | `668.890ms` |
| `pattern_4_sort_custom_field` | `29` | `1.399` | `305.964ms` | `615.995ms` | `671.494ms` |
| `pattern_2_phrase_match` | `30` | `1.447` | `258.023ms` | `524.410ms` | `557.388ms` |
| `pattern_3_multi_column_union` | `26` | `1.254` | `259.670ms` | `397.809ms` | `403.328ms` |
| `pattern_1_scalar_filters` | `43` | `2.074` | `264.365ms` | `271.132ms` | `299.114ms` |

### Concurrency = 8

| Pattern | Completed | QPS | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| `pattern_7_single_hop_reference` | `29` | `1.365` | `2514.449ms` | `3759.954ms` | `4006.513ms` |
| `pattern_4_sort_custom_field` | `45` | `2.117` | `463.483ms` | `864.440ms` | `946.088ms` |
| `pattern_9_numeric_range` | `13` | `0.612` | `386.573ms` | `754.470ms` | `759.724ms` |
| `pattern_6_direct_relationship` | `23` | `1.082` | `535.828ms` | `659.295ms` | `724.895ms` |
| `pattern_2_phrase_match` | `47` | `2.212` | `313.762ms` | `533.545ms` | `710.890ms` |
| `pattern_3_multi_column_union` | `39` | `1.835` | `310.466ms` | `501.778ms` | `749.223ms` |
| `pattern_1_scalar_filters` | `57` | `2.682` | `264.812ms` | `284.235ms` | `353.809ms` |

## 结论

这轮短压测里，最重要的结论有 4 个：

1. 当前这组混合 workload 的短时吞吐大致在：
   - `c=1`: `2.8 QPS`
   - `c=4`: `8.3 QPS`
   - `c=8`: `11.9 QPS`

2. 最稳定的 pattern 是：
   - Pattern 1：标量过滤 + 按标题排序
   - 即使在 `c=8`，它的 `p95` 也仍然只有 `284ms`

3. 最明显的尾延迟来源是：
   - Pattern 7：单跳关系遍历
   - 在 `c=8` 时，`p50` 已经到 `2514ms`，`p95` 到 `3759ms`
   - 也就是说，整体 p95 / p99 基本是被关系遍历类 query 拉高的

4. rewritten `MATCH ... AGAINST` 查询本身是稳定的：
   - Pattern 2 和 Pattern 3 在 `c=8` 下的 `p95` 都还在 `500ms` 左右
   - 没有报错，也没有行数漂移

## 如果目标是 100+ 混合 QPS

先说结论：如果 mixed workload 仍然保持这页的 pattern 和大致权重，尤其继续包含 `10%` 左右的单跳关系遍历（Pattern 7），当前这套集群规格很难直接冲到 `100+ QPS`。更现实的做法是：
- 先把当前 `1 TiDB / 3 TiKV / 3 TiFlash` 扩到一版更偏读查询的规格；
- 同时接受一个前提：只扩机器、不改关系遍历类 SQL 的执行形态，`100+ QPS` 只能作为起步目标，不能当成保证值。

### 当前规格

- `PD`: `1` 副本
- `TiDB`: `1` 副本，每个 `15 CPU / 25Gi`
- `TiKV`: `3` 副本，每个 `15 CPU / 56Gi / 500Gi`
- `TiFlash`: `3` 副本，每个 `15 CPU / 100Gi / 500Gi`
- 节点组：
  - `node16c32`: `11 x c8i.4xlarge`
  - `node-tikv`: `3 x m8i.4xlarge`
  - `node-tiflash`: `3 x r8i.4xlarge`

### 建议的起步规格

如果目标是把这套 mixed workload 往 `100+ QPS` 推，建议先从下面这版开始压：
- `PD`: `3` 副本
- `TiDB`: `3` 副本，每个 `12-16 CPU / 32Gi`
- `TiKV`: `6` 副本，每个 `15-16 CPU / 56-64Gi / 500Gi`
- `TiFlash`: `8` 副本，每个 `15-16 CPU / 100-128Gi / 500Gi`
- 对应节点组大致扩成：
  - `node16c32`: `13-15 x c8i.4xlarge`
  - `node-tikv`: `6 x m8i.4xlarge`
  - `node-tiflash`: `8 x r8i.4xlarge`

如果目标不只是吞吐到 `100+ QPS`，还希望把 mixed workload 的 `p95` 压在 `1s` 附近，那么更激进但更稳的建议是：
- `TiFlash` 直接到 `10-12` 副本，或者改成更大的 `r8i.8xlarge`
- `TiKV` 提到 `6-8` 副本
- `TiDB` 维持 `3` 副本即可

### 为什么重点要扩 TiFlash

原因很直接，当前瓶颈主要不在 TiDB 前端，而在扫描和 join：
- 当前短压测在 `c=8` 只有 `11.9 QPS`
- 尾延迟几乎被 `Pattern 7` 拉高：
  - `p50 = 2514ms`
  - `p95 = 3759ms`
  - `p99 = 4006ms`
- 这类关系遍历 query 在当前 plan 下主要是 `TiFlash MPP + relationship table scan`
- 之前单独看执行计划时，`obj_relationship_new` 经常要扫当前 workspace 的大段数据，量级在 `29996619` 行

所以这套 workload 要提吞吐，第一优先级是补 `TiFlash` 的并行扫描和 hash join 能力，而不是先盯着 TiDB。

### 为什么还要补 TiDB 和 TiKV

- `TiDB` 现在只有 `1` 个副本，`100+ QPS` mixed workload 下会承担更多 session、编排、MPP task 协调；扩到 `3` 个副本主要是避免前端和单点瓶颈。
- `TiKV` 虽然不是当前第一瓶颈，但 `MATCH ... AGAINST` 的 rowid probe、`IndexLookUp`、直接关系查找这些都还会吃到 TiKV；当 TiFlash 扩完后，TiKV 很容易变成第二瓶颈，所以建议至少翻倍到 `6` 副本。
- `PD` 从 `1` 到 `3` 更多是为了稳定性和测试时的可用性，不是主吞吐瓶颈。

### 一个重要边界

这组规格是“朝 `100+ mixed QPS` 靠近的一版起步配置”，不是承诺值。原因是当前结果已经说明：
- `MATCH ... AGAINST` 类 query 本身是稳定的，不是主问题；
- 真正拖吞吐的是关系遍历类 query，尤其 Pattern 7；
- 如果这些 query 继续保持现在的 plan 形态，只靠加机器，收益不会完全线性。

因此更务实的顺序是：
1. 先把 `TiFlash / TiKV / TiDB` 扩到上面的起步规格；
2. 再在 `c=16 / 32 / 64` 下做第二轮 mixed benchmark；
3. 如果那时吞吐还明显卡在关系遍历上，再继续做 SQL / plan 级优化，而不是只继续堆机器。

## 限制

这轮结果需要结合下面几点理解：
- 每档只跑了 `20s`，属于短时基线，不是长时间容量测试
- 每个 pattern 现在只放了 1 条具体 query，语义上有代表性，但覆盖度还不够广
- 这次只记录了 query 侧结果，没有同步抓 TiDB / TiKV / TiFlash 的系统指标时间线
- 因为 Pattern 7 很重，它在混合 workload 中对 p95 / p99 的影响会比权重本身看起来更大

## 下一步建议

如果要把这套 benchmark 往更可信的方向推进，优先顺序建议是：
- 每个 pattern 扩成 `5` 到 `20` 条具体 query，减少单条样本偏差
- 保留当前 driver，不改并发模型，只把运行时长拉到 `3` 到 `5` 分钟
- 在压测时同步记录 TiDB / TiKV / TiFlash 指标
- 对关系遍历类 query 单独做一轮 profile，确认是单跳 join 还是关系表扫描主导了尾延迟
