# JSM Query Latency Tracking

## AWS Test Cluster Quick Access

This repo uses the shared AWS/EKS test cluster below for `jsm_assets2`, `jsm_assets3`, and `jsm_assets4` validation and benchmarks.

| Item | Value |
|---|---|
| AWS account | `178851224597` |
| Region | `us-east-2` |
| EKS cluster | `Atlassian-jsm-tici` |
| Namespace | `tidb-cluster` |
| TidbCluster | `tici-demo-s3` |
| Console host | `ec2-user@ec2-3-14-170-197.us-east-2.compute.amazonaws.com` |
| Grafana | [http://a2e41aa49d08647d1b55ecd7b146bbf6-2611d84fa96ba26a.elb.us-east-2.amazonaws.com:3000](http://a2e41aa49d08647d1b55ecd7b146bbf6-2611d84fa96ba26a.elb.us-east-2.amazonaws.com:3000) |

### Login

Use the console-host pem file provided out of band. The pem file is not stored in this repo. The current console host accepts the key named `michael-eks-us-east-2.pem`; put it anywhere on your local machine and use that local path in the `ssh -i` command.

```bash
ssh -i /path/to/michael-eks-us-east-2.pem ec2-user@ec2-3-14-170-197.us-east-2.compute.amazonaws.com

# Run the following commands after you have logged in to the console host.
export AWS_PROFILE=atlassian-jsm-tici
export AWS_REGION=us-east-2
export KUBECONFIG=/home/ec2-user/.kube/atlassian-jsm-tici

# Run this if kubectl says the SSO token expired.
aws sso login --profile atlassian-jsm-tici
```

### Start The Cluster

This starts compute only. Existing EBS/PVC data, S3 backups, and Kubernetes objects are reused.

```bash
aws eks update-nodegroup-config --cluster-name Atlassian-jsm-tici --nodegroup-name node16c64 --scaling-config minSize=1,maxSize=4,desiredSize=4
aws eks update-nodegroup-config --cluster-name Atlassian-jsm-tici --nodegroup-name node-tikv-16c64 --scaling-config minSize=0,maxSize=20,desiredSize=3
aws eks update-nodegroup-config --cluster-name Atlassian-jsm-tici --nodegroup-name node-tiflash --scaling-config minSize=0,maxSize=6,desiredSize=6

kubectl patch tc -n tidb-cluster tici-demo-s3 --type merge -p '{"spec":{"tidb":{"replicas":3},"tiflash":{"replicas":6},"ticdc":{"replicas":1},"tici":{"meta":{"replicas":1},"worker":{"replicas":1}}}}'
kubectl -n tidb-cluster scale sts tici-demo-s3-tici-meta --replicas=1
kubectl -n tidb-cluster get pods -w
```

Expected test scale for the 220-worker weighted-cop benchmark: `3 TiDB / 3 TiKV / 6 TiFlash`, plus `1 PD`, `1 TiCDC`, `1 TiCI meta`, and `1 TiCI worker`. All node groups use `m8i.4xlarge` (`16 vCPU / 64 GiB`).

If TiFlash or TiCI worker reports `election: no leader`, first confirm `tici-demo-s3-tici-meta` is `1/1 Running`, then restart the TiFlash pods:

```bash
kubectl -n tidb-cluster get sts tici-demo-s3-tici-meta tici-demo-s3-tici-worker tici-demo-s3-tiflash
kubectl -n tidb-cluster delete pod -l app.kubernetes.io/component=tiflash --force --grace-period=0
```

### Access TiDB

Preferred access from the console host is through `kubectl port-forward`:

```bash
kubectl -n tidb-cluster port-forward svc/tici-demo-s3-tidb 4000:4000
mysql -h 127.0.0.1 -P4000 -uroot -Djsm_assets4
```

From a pod inside the cluster, use the service name directly:

```bash
mysql -h tici-demo-s3-tidb -P4000 -uroot -Djsm_assets4
```

Useful checks:

```sql
SHOW DATABASES;
USE jsm_assets4;
SHOW TABLES;
SELECT COUNT(*) FROM obj_new;
SELECT COUNT(*) FROM obj_relationship_new;
```

### Data Overview

| Database | Main tables | Purpose |
|---|---|---|
| `jsm_assets2` | `obj_new`, `obj_relationship_new` | 14M-object dataset restored from the old cluster, used by original JSM query and FTS/JOIN tests. |
| `jsm_assets3` | `obj_new`, `obj_relationship_new` | 10M-object dataset used by LIKE vs MATCH and dataset-specific tests. |
| `jsm_assets4` | `obj_new`, `obj_relationship_new`, `obj_type`, `obj_type_attr`, `status_type`, JSON metadata tables | Dataset used for the PingCAP customer-report query reproduction and weighted TiKV cop-wait stress tests. |

Approximate key table sizes:

| Table | Rows |
|---|---:|
| `jsm_assets2.obj_new` | 14,000,000 |
| `jsm_assets2.obj_relationship_new` | 139,991,715 |
| `jsm_assets3.obj_new` | 10,000,000 |
| `jsm_assets3.obj_relationship_new` | 100,005,360 |
| `jsm_assets4.obj_new` | 14,000,000 |
| `jsm_assets4.obj_relationship_new` | 139,988,146 |
| `jsm_assets4.obj_type` | 50 |
| `jsm_assets4.obj_type_attr` | 1,750 |

Detailed rebuild records, image versions, BR commands, and FULLTEXT rebuild steps are in [`jsm_assets_aws_rebuild_manifest.md`](jsm_assets_aws_rebuild_manifest.md).

### Stop The Cluster

To stop database compute but keep Grafana reachable, scale TiDB/TiFlash/TiCDC/TiCI to zero and keep one default node for `basic-monitor`:

```bash
kubectl patch tc -n tidb-cluster tici-demo-s3 --type merge -p '{"spec":{"tidb":{"replicas":0},"tiflash":{"replicas":0},"ticdc":{"replicas":0},"tici":{"meta":{"replicas":0},"worker":{"replicas":0}}}}'
aws eks update-nodegroup-config --cluster-name Atlassian-jsm-tici --nodegroup-name node-tiflash --scaling-config minSize=0,maxSize=6,desiredSize=0
aws eks update-nodegroup-config --cluster-name Atlassian-jsm-tici --nodegroup-name node-tikv-16c64 --scaling-config minSize=0,maxSize=20,desiredSize=0
aws eks update-nodegroup-config --cluster-name Atlassian-jsm-tici --nodegroup-name node16c64 --scaling-config minSize=1,maxSize=4,desiredSize=1
```

To fully stop all worker EC2 instances, also set `node16c64` to `desiredSize=0`; Grafana will be unavailable until it is started again.

### Current Benchmark

The TiKV cop-wait reproduction workload is `bench/run_pingcap_report_query_samples.py` against `jsm_assets4`, with `220` workers and weighted slow-query classes. Recent fixed-duration results are summarized in [`pingcap_report_weighted_cop_c220_c330_10min_20260511_16c64.md`](pingcap_report_weighted_cop_c220_c330_10min_20260511_16c64.md).

Current continuous run:

| Item | Value |
|---|---|
| Runner pod | `tidb-cluster/jsm-bench-runner` |
| Started at | `2026-05-12T05:38:46Z` |
| PID in pod | `55` |
| Concurrency | `220` workers |
| Duration setting | `604800s`; stop it manually when the test is done |

Useful benchmark commands:

```bash
# Check the runner process and startup log.
kubectl -n tidb-cluster exec jsm-bench-runner -- bash -lc 'PID=$(cat /tmp/c220-continuous.pid); kill -0 $PID && echo running; tail -20 /tmp/c220-continuous.log'

# Stop the continuous run without stopping the cluster.
kubectl -n tidb-cluster exec jsm-bench-runner -- bash -lc 'kill $(cat /tmp/c220-continuous.pid)'
```

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
- `jsm_dataset_1_fts_join_qps_benchmark_results.md`
  - 当前 `FTS + JOIN` 与 `LIKE + JOIN` 专项 QPS 对比结果和结论
- `pingcap_report_query_comparison.html`
  - 客户报告与当前 `jsm_assets4` 测试结果的 query latency、rows、plan shape 对比页面
- `pingcap_report_plan_comparison.md`
  - 客户报告与当前 `jsm_assets4` 的执行计划差异摘要
- `pingcap_report_weighted_cop_c220_10min_20260511.md`
  - 保留全部 runnable query、提高慢 query worker 权重后的 TiKV cop wait 复现实验结果

压测相关代码：
- `bench/dataset_1_qps_corpus.json`
  - 最初的 query corpus
- `bench/dataset_1_qps_corpus_tuned_60s.json`
  - 当前正式压测使用的 tuned corpus
- `bench/fts_join_qps_corpus.json`
  - 当前 `FTS + JOIN` 专项压测使用的 corpus
- `bench/fts_join_like_qps_corpus.json`
  - 当前 `LIKE + JOIN` 专项压测使用的 corpus
- `bench/run_dataset_1_qps_benchmark.py`
  - 早期 Python benchmark driver
- `bench/go_qps_bench/main.go`
  - 当前正式使用的 Go benchmark driver，支持每条连接初始化 session SQL
- `bench/haproxy_tidb_workstation.cfg`
  - workstation 上用于分流到 3 个 TiDB 的 `HAProxy` 配置

结果数据：
- `bench/results/dataset_1_qps_benchmark_go_haproxy_pattern7tight_20260421_084835.json`
  - 当前最新结果：workstation + Go + HAProxy + 3 TiDB + 更高过滤率的 `Pattern 7`
- `bench/results/fts_join_qps_benchmark_go_haproxy_20260421_1908.json`
  - 当前最新 `FTS + JOIN` 专项结果：10 条 query，`text_value_7:1 / text_value_1:3 / text_value_4:3 / text_value_5:3`
- `bench/results/fts_join_like_qps_benchmark_go_haproxy_20260421_2250.json`
  - 当前最新 `LIKE + JOIN` 专项结果：与 `FTS + JOIN` 使用同一组 query，只把过滤写法改成 `LIKE`

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
