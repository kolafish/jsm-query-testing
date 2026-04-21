# Dataset 1 简单 QPS 压测结果

这页只记录当前最新这一轮 mixed workload benchmark 的方法和结果。

## 当前压测代码

相关文件：
- Query pattern 页面：[jsm_dataset_1_qps_patterns.md](/Users/jin/Desktop/jsm-query-latency-tracking/jsm_dataset_1_qps_patterns.md)
- 当前 corpus：[bench/dataset_1_qps_corpus_tuned_60s.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/dataset_1_qps_corpus_tuned_60s.json)
- Go benchmark driver：
  - [bench/go_qps_bench/main.go](/Users/jin/Desktop/jsm-query-latency-tracking/bench/go_qps_bench/main.go)
  - [bench/go_qps_bench/go.mod](/Users/jin/Desktop/jsm-query-latency-tracking/bench/go_qps_bench/go.mod)
- workstation 上的 `HAProxy` 配置：
  - [bench/haproxy_tidb_workstation.cfg](/Users/jin/Desktop/jsm-query-latency-tracking/bench/haproxy_tidb_workstation.cfg)
- 当前最新结果 JSON：
  - [bench/results/dataset_1_qps_benchmark_go_haproxy_pattern7tight_20260421_084835.json](/Users/jin/Desktop/jsm-query-latency-tracking/bench/results/dataset_1_qps_benchmark_go_haproxy_pattern7tight_20260421_084835.json)

## 当前正式压测方法

### 客户端

- benchmark 进程运行在 `workstation`
- 压测程序是 `Go`
- 每个 worker goroutine 复用一个持久数据库连接
- 每条 query 都完整取回结果并校验 `row_count`
- 正式 run 前会先串行 warmup 一次

### 数据库入口

当前正式入口是：
- workstation 本地 `127.0.0.1:34008`
- 由 workstation 本地 `HAProxy` 做 TCP 负载均衡
- 后端直连 `3` 个 `TiDB pod IP:4000`

当前 3 个后端：
- `192.168.27.181:4000`
- `192.168.23.56:4000`
- `192.168.7.250:4000`

分流验证：
- 连续 `12` 次新建连接
- 落到 `3` 个 `TiDB` 的分布是 `4 / 4 / 4`

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
  --output /home/ec2-user/jsm-query-bench/results/dataset_1_qps_benchmark_go_haproxy_pattern7tight_20260421_084835.json \
  2 4 6 8 10
```

说明：
- 每档并发跑 `60s`
- 并发档位：`2 / 4 / 6 / 8 / 10`

## 当前 Pattern 百分比

| Pattern | 描述 | 百分比 |
|---|---|---:|
| `Pattern 1` | 标量过滤 + 按标题排序 | `25%` |
| `Pattern 2` | 由原始 `LIKE '%...%'` 改写来的短语搜索 | `25%` |
| `Pattern 3` | 多列短语搜索，用 `UNION DISTINCT` 拼接 | `15%` |
| `Pattern 4` | 按自定义字段排序 | `20%` |
| `Pattern 6` | 直接查关系表 | `5%` |
| `Pattern 7` | 单跳关系遍历 | `5%` |
| `Pattern 9` | 数值范围过滤 | `5%` |

## Pattern 7 当前写法

这轮 benchmark 里，`Pattern 7` 已经换成更高过滤率的单跳关系遍历版本：
- 不再用宽过滤条件如品牌值 `Sharp / Samsung`
- 改成内层精确对象过滤：
  - `subO1.label = 'LG-259837'`
- 这条 query 当前预期返回：
  - `45` 行

## Warmup 结果

所有 query 都通过了 warmup，且返回行数和预期一致。

| Query | Pattern | Warmup Latency | Row Count |
|---|---|---:|---:|
| `pattern_1_scalar_filters` | Pattern 1 | `22.553ms` | `51` |
| `pattern_2_phrase_match` | Pattern 2 | `12.278ms` | `1` |
| `pattern_3_multi_column_union` | Pattern 3 | `10.699ms` | `1` |
| `pattern_4_sort_custom_field` | Pattern 4 | `23.322ms` | `1000` |
| `pattern_6_direct_relationship` | Pattern 6 | `7.538ms` | `56` |
| `pattern_7_single_hop_reference` | Pattern 7 | `27.224ms` | `45` |
| `pattern_9_numeric_range` | Pattern 9 | `52.838ms` | `1000` |

## 当前最新结果

| Concurrency | QPS | Avg | p50 | p95 | p99 | Errors | Row Count Mismatch |
|---|---:|---:|---:|---:|---:|---:|---:|
| `2` | `124.914` | `16.008ms` | `15.320ms` | `39.627ms` | `44.649ms` | `0` | `0` |
| `4` | `237.065` | `16.869ms` | `15.659ms` | `39.295ms` | `50.334ms` | `0` | `0` |
| `6` | `333.853` | `17.965ms` | `16.875ms` | `38.773ms` | `54.992ms` | `0` | `0` |
| `8` | `383.054` | `20.878ms` | `19.013ms` | `45.004ms` | `61.785ms` | `0` | `0` |
| `10` | `336.536` | `29.709ms` | `24.182ms` | `69.939ms` | `89.506ms` | `0` | `0` |

## 分 Pattern 观察

这里只列当前更有代表性的 `c=8` 和 `c=10`。

### Concurrency = 8

| Pattern | Completed | QPS | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| `pattern_1_scalar_filters` | `5917` | `98.575` | `22.831ms` | `45.968ms` | `61.451ms` |
| `pattern_2_phrase_match` | `5707` | `95.076` | `10.622ms` | `18.446ms` | `23.295ms` |
| `pattern_3_multi_column_union` | `3359` | `55.960` | `9.575ms` | `18.852ms` | `23.457ms` |
| `pattern_4_sort_custom_field` | `4579` | `76.284` | `26.216ms` | `38.810ms` | `50.146ms` |
| `pattern_6_direct_relationship` | `1196` | `19.925` | `4.688ms` | `21.263ms` | `30.068ms` |
| `pattern_7_single_hop_reference` | `1069` | `17.809` | `26.495ms` | `49.286ms` | `68.463ms` |
| `pattern_9_numeric_range` | `1166` | `19.425` | `47.263ms` | `70.398ms` | `90.170ms` |

### Concurrency = 10

| Pattern | Completed | QPS | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| `pattern_1_scalar_filters` | `5145` | `85.729` | `40.765ms` | `81.404ms` | `98.154ms` |
| `pattern_2_phrase_match` | `5038` | `83.947` | `11.109ms` | `19.427ms` | `25.482ms` |
| `pattern_3_multi_column_union` | `2964` | `49.388` | `9.754ms` | `19.519ms` | `24.904ms` |
| `pattern_4_sort_custom_field` | `4001` | `66.667` | `35.358ms` | `64.545ms` | `74.423ms` |
| `pattern_6_direct_relationship` | `1030` | `17.163` | `15.508ms` | `43.317ms` | `50.515ms` |
| `pattern_7_single_hop_reference` | `970` | `16.163` | `41.153ms` | `95.708ms` | `116.402ms` |
| `pattern_9_numeric_range` | `1049` | `17.479` | `47.366ms` | `74.380ms` | `87.035ms` |

## 结论

当前这轮 benchmark 的结论可以直接概括成 5 条：

1. 当前 mixed workload 已经稳定超过 `100 QPS`
   - `c=2` 就已经到 `124.914 QPS`

2. 当前峰值在 `c=8`
   - `383.054 QPS`

3. `c=10` 时吞吐开始回落
   - `336.536 QPS`
   - 说明这一轮的最佳并发点更接近 `8`

4. 这轮结果已经可以基本排除“压测程序本身是瓶颈”
   - 客户端在 `workstation`
   - 压测程序是 `Go`
   - 本地入口是 `HAProxy`
   - 后端能均匀打到 `3` 个 `TiDB`
   - `errors = 0`
   - `row_count_mismatches = 0`

5. 在当前这个更高过滤率的 workload 里，`Pattern 7` 已经不再是压倒性的尾延迟来源
   - 它仍然比纯点查/短语查更重
   - 但已经从秒级下降到几十毫秒量级
   - 当前 mixed workload 的整体尾延迟已经明显改善
