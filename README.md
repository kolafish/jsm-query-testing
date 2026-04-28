# JSM Query Latency Tracking

## 当前 AWS 测试环境

新 AWS/EKS TiDB + TiCI 测试集群已创建并完成数据恢复，当前可用于 `jsm_assets2` / `jsm_assets3` 查询验证和压测。

### 登录入口

```bash
ssh -i /Users/jin/Downloads/michael-eks-us-east-2.pem ec2-user@ec2-3-14-170-197.us-east-2.compute.amazonaws.com

export AWS_PROFILE=atlassian-jsm-tici
export AWS_REGION=us-east-2
export KUBECONFIG=/home/ec2-user/.kube/atlassian-jsm-tici
```

### 启动集群

下面命令只启动新集群的 EC2 nodegroup，不会重新建表或恢复数据。当前压测规模需要 `4` 台 default 节点来承载 `3` 个 TiDB pod。

```bash
eksctl scale nodegroup --cluster Atlassian-jsm-tici --name node16c32 --nodes 4 --nodes-min 0 --nodes-max 20 --region us-east-2
eksctl scale nodegroup --cluster Atlassian-jsm-tici --name node-tikv --nodes 3 --nodes-min 0 --nodes-max 20 --region us-east-2
eksctl scale nodegroup --cluster Atlassian-jsm-tici --name node-tiflash --nodes 3 --nodes-min 0 --nodes-max 20 --region us-east-2

kubectl -n tidb-cluster get pods
```

### 停止集群

下面命令是停止 compute，不是彻底销毁集群。EKS control plane、EBS/PVC、S3 数据和 Kubernetes 对象会保留；停止后数据库不可访问，重新执行上面的启动命令后 pod 会重新调度。

```bash
eksctl scale nodegroup --cluster Atlassian-jsm-tici --name node-tiflash --nodes 0 --nodes-min 0 --nodes-max 20 --region us-east-2
eksctl scale nodegroup --cluster Atlassian-jsm-tici --name node-tikv --nodes 0 --nodes-min 0 --nodes-max 20 --region us-east-2
eksctl scale nodegroup --cluster Atlassian-jsm-tici --name node16c32 --nodes 0 --nodes-min 0 --nodes-max 20 --region us-east-2
```

### 访问 TiDB

从 EKS 内部访问：

```bash
mysql -h tici-demo-s3-tidb -P4000 -uroot -Djsm_assets3
```

从 console host 访问可以先做 port-forward：

```bash
kubectl -n tidb-cluster port-forward svc/tici-demo-s3-tidb 4000:4000
mysql -h 127.0.0.1 -P4000 -uroot -Djsm_assets3
```

### Grafana

Grafana LoadBalancer:

[http://a2e41aa49d08647d1b55ecd7b146bbf6-38f9eda417a300aa.elb.us-east-2.amazonaws.com:3000](http://a2e41aa49d08647d1b55ecd7b146bbf6-38f9eda417a300aa.elb.us-east-2.amazonaws.com:3000)

### 集群信息

| 项目 | 当前值 |
|---|---|
| AWS account | `178851224597` |
| Region | `us-east-2` |
| EKS cluster | `Atlassian-jsm-tici` |
| Namespace | `tidb-cluster` |
| TidbCluster | `tici-demo-s3` |
| S3 bucket | `s3://atlassian-jsm-tici-178851224597-us-east-2` |
| 数据库 | `jsm_assets2`, `jsm_assets3` |

当前组件规模：

| Component | Replicas | Status |
|---|---:|---|
| PD | 1 | Running |
| TiDB | 3 | Running |
| TiKV | 3 | Running |
| TiFlash | 3 | Running |
| TiCDC | 1 | Running |
| TiCI meta | 1 | Running |
| TiCI worker | 1 | Running |

节点规格：

| Node group | Instance type | 当前数量 | 用途 |
|---|---|---:|---|
| `node16c32` | `c8i.4xlarge` | 4 | TiDB / PD / TiCI / TiCDC / monitor / benchmark client |
| `node-tikv` | `c8i.4xlarge` | 3 | TiKV |
| `node-tiflash` | `m8i.4xlarge` | 3 | TiFlash |

TiDB service 连接分布验证：

| Method | Result |
|---|---|
| 300 次新连接访问 `tici-demo-s3-tidb:4000` 并查询 `@@hostname` | `tidb-0:102`, `tidb-1:109`, `tidb-2:89` |

数据恢复和索引状态：

| 项目 | 结果 |
|---|---|
| BR restore | 已完成，`2026-04-27 08:41:55 UTC` 到 `08:58:58 UTC`，耗时 `17m02s` |
| Restore source | `s3://atlassian-jsm-tici-178851224597-us-east-2/br-backups/jsm-assets2-assets3-20260427T042546Z` |
| TiFlash replica | 四张表均 `available=1`, `progress=1` |
| FULLTEXT indexes | 两个 `obj_new` 表均已重建 `idx_fts_1/4/5/7/20/22/label`，parser 为 `NGRAM` |
| FTS smoke check | `text_value_7 = Fagor` 的 `MATCH` 和 `LIKE` 命中数一致 |

当前表规模：

| Table | Rows | data_length | index_length |
|---|---:|---:|---:|
| `jsm_assets2.obj_new` | 14,000,000 | 62.53 GiB | 638.72 GiB |
| `jsm_assets2.obj_relationship_new` | 139,991,715 | 20.47 GiB | 45.37 GiB |
| `jsm_assets3.obj_new` | 10,000,000 | 44.59 GiB | 489.27 GiB |
| `jsm_assets3.obj_relationship_new` | 100,005,360 | 14.62 GiB | 32.41 GiB |

详细重建记录、镜像版本、BR 命令和 FULLTEXT 重建步骤见 [`jsm_assets_aws_rebuild_manifest.md`](jsm_assets_aws_rebuild_manifest.md)。

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
