# Dataset 1 简单 QPS 压测结果

这页记录目前这套 dataset 1 mixed workload 的正式压测方法和最新结果。

当前这版结果，和前面“本地 Python + port-forward”的短压测不一样。现在这版已经切到：
- 客户端跑在 `workstation`
- 压测程序改成 `Go`
- 入口改成 workstation 本地 `HAProxy`
- 后端均匀分发到 `3` 个 `TiDB`

所以这页里的结论，优先以这一版为准。

## 当前压测代码

相关文件：
- Query pattern 页面：[jsm_dataset_1_qps_patterns.md](/Users/jin/Desktop/jsm-query-latency-tracking/jsm_dataset_1_qps_patterns.md)
- 当前 corpus：[bench/dataset_1_qps_corpus_tuned_60s.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/dataset_1_qps_corpus_tuned_60s.json)
- Go benchmark driver：
  - [bench/go_qps_bench/main.go](/Users/jin/Desktop/jsm-query-latency-tracking/bench/go_qps_bench/main.go)
  - [bench/go_qps_bench/go.mod](/Users/jin/Desktop/jsm-query-latency-tracking/bench/go_qps_bench/go.mod)
- workstation 上的 `HAProxy` 配置：
  - [bench/haproxy_tidb_workstation.cfg](/Users/jin/Desktop/jsm-query-latency-tracking/bench/haproxy_tidb_workstation.cfg)
- 当前正式结果 JSON：
  - [bench/results/dataset_1_qps_benchmark_go_haproxy_20260421_082216.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/dataset_1_qps_benchmark_go_haproxy_20260421_082216.json)
- 扩容到 `3 TiDB` 但还没换正式分流入口时的 baseline：
  - [bench/results/dataset_1_qps_benchmark_go_20260421_080916.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/dataset_1_qps_benchmark_go_20260421_080916.json)

## 当前正式压测方法

### 客户端

- benchmark 进程运行在 `workstation`
- 压测程序是 `Go`，不是 Python
- 每个 worker goroutine 复用一个持久数据库连接
- 每条 query 都完整取回结果并校验 `row_count`
- 正式 run 前会先串行 warmup 一次

### 数据库入口

当前正式入口不是 `kubectl port-forward`，而是：
- workstation 本地 `127.0.0.1:34008`
- 由 workstation 本地 `HAProxy` 做 TCP 负载均衡
- 后端直连 3 个 `TiDB pod IP:4000`

当前 3 个后端是：
- `192.168.27.181:4000`
- `192.168.23.56:4000`
- `192.168.7.250:4000`

我做过分流验证：
- 连续 `12` 次新建连接
- 落到 `3` 个 `TiDB` 的分布是 `4 / 4 / 4`

这意味着这轮压测已经不是“单 TiDB + 单 port-forward”的假分流结果。

### 集群规格

当前与这轮压测直接相关的前端规格：
- `TiDB replicas = 3`
- `TiDB pods`：
  - `tici-demo-s3-tidb-0`
  - `tici-demo-s3-tidb-1`
  - `tici-demo-s3-tidb-2`

### 正式执行命令

```bash
cd /home/ec2-user/jsm-query-bench
./dataset_1_qps_bench_go \
  --host 127.0.0.1 \
  --port 34008 \
  --user root \
  --database jsm_testcase2 \
  --corpus /home/ec2-user/jsm-query-bench/dataset_1_qps_corpus_tuned_60s.json \
  --duration 60 \
  --output /home/ec2-user/jsm-query-bench/results/dataset_1_qps_benchmark_go_haproxy_20260421_082216.json \
  1 4 8 16
```

说明：
- 每档并发跑 `60s`
- 并发档位：`1 / 4 / 8 / 16`

## Warmup 结果

所有 query 都通过了 warmup，且返回行数和预期一致。

| Query | Pattern | Warmup Latency | Row Count |
|---|---|---:|---:|
| `pattern_1_scalar_filters` | Pattern 1 | `51.307ms` | `51` |
| `pattern_2_phrase_match` | Pattern 2 | `94.130ms` | `1` |
| `pattern_3_multi_column_union` | Pattern 3 | `19.873ms` | `1` |
| `pattern_4_sort_custom_field` | Pattern 4 | `33.304ms` | `1000` |
| `pattern_6_direct_relationship` | Pattern 6 | `14.158ms` | `56` |
| `pattern_7_single_hop_reference` | Pattern 7 | `858.774ms` | `1000` |
| `pattern_9_numeric_range` | Pattern 9 | `51.034ms` | `1000` |

## 当前正式结果

| Concurrency | QPS | Avg | p50 | p95 | p99 | Errors | Row Count Mismatch |
|---|---:|---:|---:|---:|---:|---:|---:|
| `1` | `16.447` | `60.798ms` | `16.309ms` | `712.967ms` | `922.071ms` | `0` | `0` |
| `4` | `59.598` | `66.802ms` | `17.272ms` | `708.485ms` | `1105.378ms` | `0` | `0` |
| `8` | `79.780` | `99.554ms` | `22.217ms` | `894.486ms` | `1685.730ms` | `0` | `0` |
| `16` | `79.156` | `198.288ms` | `48.840ms` | `1607.103ms` | `3087.987ms` | `0` | `0` |

## 和前一轮的对比

前一轮 baseline 是：
- 客户端已经在 `workstation`
- 压测程序已经是 `Go`
- 但入口还不是 `HAProxy`
- 没有真正把流量均匀铺到 `3` 个 `TiDB`

对比结果：

| Concurrency | Baseline QPS | 当前正式 QPS |
|---|---:|---:|
| `1` | `15.807` | `16.447` |
| `4` | `30.315` | `59.598` |
| `8` | `27.714` | `79.780` |
| `16` | `22.526` | `79.156` |

最值得关注的是：
- `c=4`：`30.3 -> 59.6`
- `c=8`：`27.7 -> 79.8`

这说明：
- 之前确实不是数据库后端极限，而是前端 `TiDB` 和入口链路先卡住了
- 把 `TiDB` 扩到 `3`，再换成真正分流的入口后，吞吐提升很明显

## 分 Pattern 观察

这里只列当前更有代表性的 `c=8` 和 `c=16`。

### Concurrency = 8

| Pattern | Completed | QPS | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| `pattern_1_scalar_filters` | `1218` | `19.892` | `25.148ms` | `60.509ms` | `146.068ms` |
| `pattern_2_phrase_match` | `1212` | `19.794` | `12.655ms` | `39.079ms` | `138.207ms` |
| `pattern_3_multi_column_union` | `726` | `11.857` | `12.264ms` | `35.535ms` | `131.490ms` |
| `pattern_4_sort_custom_field` | `965` | `15.760` | `29.283ms` | `74.828ms` | `120.315ms` |
| `pattern_6_direct_relationship` | `263` | `4.295` | `5.270ms` | `41.397ms` | `74.393ms` |
| `pattern_7_single_hop_reference` | `251` | `4.099` | `1424.605ms` | `1865.524ms` | `2089.748ms` |
| `pattern_9_numeric_range` | `250` | `4.083` | `51.158ms` | `87.158ms` | `262.698ms` |

### Concurrency = 16

| Pattern | Completed | QPS | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| `pattern_1_scalar_filters` | `1275` | `20.463` | `60.083ms` | `203.308ms` | `347.566ms` |
| `pattern_2_phrase_match` | `1226` | `19.677` | `23.417ms` | `156.897ms` | `281.475ms` |
| `pattern_3_multi_column_union` | `718` | `11.524` | `25.528ms` | `181.739ms` | `295.830ms` |
| `pattern_4_sort_custom_field` | `967` | `15.520` | `62.390ms` | `256.111ms` | `386.206ms` |
| `pattern_6_direct_relationship` | `260` | `4.173` | `27.740ms` | `183.124ms` | `422.652ms` |
| `pattern_7_single_hop_reference` | `258` | `4.141` | `2511.083ms` | `3544.618ms` | `4003.067ms` |
| `pattern_9_numeric_range` | `228` | `3.659` | `63.932ms` | `393.733ms` | `1127.193ms` |

## 结论

当前这轮更像正式 benchmark 的结论有 5 条：

1. 当前 mixed workload 在这套集群上的真实吞吐已经接近 `80 QPS`
   - `c=8`：`79.780 QPS`
   - `c=16`：`79.156 QPS`

2. 这轮结果已经可以基本排除“压测程序本身是瓶颈”
   - 客户端在 `workstation`
   - 压测程序是 `Go`
   - 每个 worker 复用持久连接
   - 所有 query 都做结果读取和行数校验
   - `errors = 0`
   - `row_count_mismatches = 0`

3. 之前的主要瓶颈确实是 `TiDB` 前端和入口链路
   - 把 `TiDB` 从 `1` 扩到 `3`
   - 再把入口换成真正分流的 `HAProxy`
   - `c=4` 和 `c=8` 的 QPS 都接近翻倍甚至更多

4. 当前新的瓶颈已经偏数据库侧，不是客户端侧
   - `c=8 -> c=16` 时，QPS 没继续涨
   - 但 `p95/p99` 明显恶化
   - 说明现在是重查询开始互相堆积，不是 benchmark driver 发不动

5. 最主要的尾延迟来源仍然是 `Pattern 7`
   - `c=8` 时 `p95 = 1865ms`
   - `c=16` 时 `p95 = 3545ms`
   - 它仍然是这组 mixed workload 里最该继续优化的 query 形态

## 对 100+ QPS 的判断

基于当前这轮结果，`100+ QPS` 已经不是遥远目标，但还没到。

当前状态：
- 峰值大约 `80 QPS`
- 离 `100 QPS` 还差大约 `20-25%`

更务实的下一步不是继续换客户端程序，而是继续做数据库侧优化：
- 优先看 `Pattern 7` 的执行计划和关系遍历路径
- 再决定是继续扩 `TiDB/TiFlash/TiKV`，还是先改 query/plan

一句话说就是：
- benchmark 客户端这边已经基本到位
- 后面要追 `100+ QPS`，主要该动数据库和 query pattern，而不是 benchmark 程序
