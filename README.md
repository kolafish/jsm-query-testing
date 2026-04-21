# JSM Query Latency Tracking

这个仓库记录 dataset 1 的单条查询延迟测试、QPS 压测模式和当前压测代码。

主要文件：
- `jsm_dataset_1_single_query_latency_results.md`
  - 单条 query latency、返回行数、实际执行 SQL、改写说明和慢点备注
- `jsm_original_queries.md`
  - 当前覆盖到的原始 query 文本
- `jsm_dataset_1_qps_patterns.md`
  - 从 JQL 视角整理出来的代表性 query pattern，以及压测计划
- `jsm_dataset_1_simple_qps_benchmark_results.md`
  - 当前 mixed workload QPS 压测结果和结论

压测相关代码：
- `bench/dataset_1_qps_corpus.json`
  - 最初的 query corpus
- `bench/dataset_1_qps_corpus_tuned_60s.json`
  - 当前正式压测使用的 tuned corpus
- `bench/run_dataset_1_qps_benchmark.py`
  - 早期 Python benchmark driver
- `bench/go_qps_bench/main.go`
  - 当前正式使用的 Go benchmark driver
- `bench/haproxy_tidb_workstation.cfg`
  - workstation 上用于分流到 3 个 TiDB 的 `HAProxy` 配置

结果数据：
- `bench/results/dataset_1_qps_benchmark_20260421.json`
  - 最初的短时 Python 基线结果
- `bench/results/dataset_1_qps_benchmark_go_20260421_080916.json`
  - workstation + Go，但还没切到正式分流入口时的 baseline
- `bench/results/dataset_1_qps_benchmark_go_haproxy_20260421_082216.json`
  - 当前正式结果：workstation + Go + HAProxy + 3 TiDB

改写约定：
- `obj -> obj_new`
- `obj_relationship -> obj_relationship_new`
- UUID 过滤用 `UNHEX(REPLACE(...))` 适配 `BINARY(16)` 列
- 适合时把 `LIKE` 改写成 `MATCH ... AGAINST`
- 失败、报错和 `0` 行的 case 也保留原 query 和原因

当前状态：
- 单条 query latency 文档已经覆盖 dataset 1 的主要 query 形态
- QPS benchmark 已经从本地 Python 原型，切到 workstation 上的 Go 正式版本
- 当前正式压测入口已经改成 workstation 本地 `HAProxy`，可以把连接均匀打到 `3` 个 TiDB
