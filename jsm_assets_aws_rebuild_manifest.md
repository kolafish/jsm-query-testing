# JSM Assets AWS Rebuild Manifest

Generated on 2026-04-27 from source cluster `michael-eks-v2-test` in `us-east-2`, namespace `tidb-cluster`.

This manifest is for rebuilding a fresh AWS TiDB/TiCI cluster that reproduces the four benchmark tables:

- `jsm_assets2.obj_new`
- `jsm_assets2.obj_relationship_new`
- `jsm_assets3.obj_new`
- `jsm_assets3.obj_relationship_new`

## Source Cluster Baseline

The `TidbCluster.spec.version` still reports `v8.5.5`, but the actual running component images are custom `v8.5.6-202604xx` builds. Rebuilds should pin the actual pod images below, not only the CR version.

| Component | Replicas now | Image | Request |
|---|---:|---|---|
| PD | 1 | `gcr.io/pingcap-public/dbaas/pd:v8.5.6-20260423-4b9dde5` | not set in pod output |
| TiDB | 1 | `gcr.io/pingcap-public/dbaas/tidb:v8.5.6-20260423-93f2dfb` | `15 CPU / 25Gi` |
| TiKV | 3 | `gcr.io/pingcap-public/dbaas/tikv:v8.5.6-20260424-74347d1` | `15 CPU / 56Gi` |
| TiFlash | 3 | `gcr.io/pingcap-public/dbaas/tiflash:v8.5.6-20260423-cbe33d1` | `15 CPU / 100Gi` |
| TiCDC | 1 | `gcr.io/pingcap-public/dbaas/ticdc:v8.5.6-release.3` | not set in pod output |
| TiCI meta | 1 | `gcr.io/pingcap-public/dbaas/tici:v0.2.0` | not set in pod output |
| TiCI worker | 1 | `gcr.io/pingcap-public/dbaas/tici:v0.2.0` | not set in pod output |

TiDB version string:

```text
Release Version: v8.5.6-20260423-93f2dfb
Edition: Community
Git Commit Hash: 93f2dfbacbe6029802bcbfac5a6ff456c7d03d87
Git Branch: heads/refs/tags/v8.5.6-20260423-93f2dfb
UTC Build Time: 2026-04-23 10:59:24
GoVersion: go1.25.6
Store: tikv
Kernel Type: Classic
```

## AWS Node Groups

| Node group | Instance type | Desired now | Max |
|---|---|---:|---:|
| `node16c32` | `c8i.4xlarge` | 3 | 20 |
| `node-tikv` | `m8i.4xlarge` | 3 | 20 |
| `node-tiflash` | `r8i.4xlarge` | 3 | 20 |

PVCs to reproduce for the current shape:

| Component | PVC size | Storage class |
|---|---:|---|
| PD | `1Gi` | `gp3` |
| TiKV | `500Gi` per pod | `gp3` |
| TiFlash | `500Gi` per pod | `gp3` |
| monitor | `100Gi` | `gp3` |

If rebuilding with index creation from scratch, leave extra TiKV and TiFlash headroom. Index backfill and TiCI fulltext ingestion can temporarily use more disk and CPU than steady-state query serving.

## Table Size Snapshot

These values come from `information_schema.tables` on the source cluster.

| Table | Rows | data_length | index_length | Total |
|---|---:|---:|---:|---:|
| `jsm_assets2.obj_new` | 14,000,000 | 68.87 GiB | 690.80 GiB | 759.67 GiB |
| `jsm_assets2.obj_relationship_new` | 139,991,715 | 20.47 GiB | 45.37 GiB | 65.84 GiB |
| `jsm_assets3.obj_new` | 10,000,000 | 49.14 GiB | 529.57 GiB | 578.72 GiB |
| `jsm_assets3.obj_relationship_new` | 100,005,360 | 14.62 GiB | 32.41 GiB | 47.03 GiB |

Aggregate logical size:

| Category | Size |
|---|---:|
| Data | 153.10 GiB |
| Indexes | 1,298.15 GiB |
| Total | 1,451.26 GiB |

## Index Snapshot

| Table | Index count | Unique index count | FULLTEXT count |
|---|---:|---:|---:|
| `jsm_assets2.obj_new` | 128 | 1 | 7 |
| `jsm_assets2.obj_relationship_new` | 5 | 1 | 0 |
| `jsm_assets3.obj_new` | 135 | 12 | 7 |
| `jsm_assets3.obj_relationship_new` | 5 | 1 | 0 |

FULLTEXT indexes on both `obj_new` tables:

| Index | Column | Parser |
|---|---|---|
| `idx_fts_1` | `text_value_1` | `NGRAM` |
| `idx_fts_4` | `text_value_4` | `NGRAM` |
| `idx_fts_5` | `text_value_5` | `NGRAM` |
| `idx_fts_7` | `text_value_7` | `NGRAM` |
| `idx_fts_20` | `text_value_20` | `NGRAM` |
| `idx_fts_22` | `text_value_22` | `NGRAM` |
| `idx_fts_label` | `label` | `NGRAM` |

`obj_relationship_new` indexes on both databases:

| Index | Columns |
|---|---|
| `PRIMARY` | `workspace_id,id` |
| `idx_obj_relationship_new_object_ws_ota_ref` | `object_id,workspace_id,object_type_attribute_id,referenced_object_id` |
| `idx_obj_relationship_new_ref_ws_ota_obj` | `referenced_object_id,workspace_id,object_type_attribute_id,object_id` |
| `idx_obj_relationship_new_ws_object` | `workspace_id,object_id` |
| `idx_obj_relationship_new_ws_referenced` | `workspace_id,referenced_object_id` |

## TiFlash Replica Snapshot

All four tables currently have one available TiFlash replica:

| Table | replica_count | available | progress |
|---|---:|---:|---:|
| `jsm_assets2.obj_new` | 1 | 1 | 1 |
| `jsm_assets2.obj_relationship_new` | 1 | 1 | 1 |
| `jsm_assets3.obj_new` | 1 | 1 | 1 |
| `jsm_assets3.obj_relationship_new` | 1 | 1 | 1 |

Rebuild command after table restore or import:

```sql
ALTER TABLE jsm_assets2.obj_new SET TIFLASH REPLICA 1;
ALTER TABLE jsm_assets2.obj_relationship_new SET TIFLASH REPLICA 1;
ALTER TABLE jsm_assets3.obj_new SET TIFLASH REPLICA 1;
ALTER TABLE jsm_assets3.obj_relationship_new SET TIFLASH REPLICA 1;
```

Then wait for:

```sql
SELECT table_schema, table_name, replica_count, available, progress
FROM information_schema.tiflash_replica
WHERE table_schema IN ('jsm_assets2', 'jsm_assets3')
  AND table_name IN ('obj_new', 'obj_relationship_new')
ORDER BY table_schema, table_name;
```

## Recommended Rebuild Flow

The most deterministic flow is:

1. Create a fresh AWS EKS/TiDB/TiCI cluster using the exact component images above.
2. Use a new TiCI S3 prefix and clean TiCI meta tables. Do not reuse old TiCI metadata or old shard-cache paths.
3. Create `jsm_assets2` and `jsm_assets3`.
4. Create the four tables from source DDL, preferably without FULLTEXT indexes for the initial data import.
5. Import data for the four tables.
6. Add normal secondary indexes if the import path did not restore them.
7. Add FULLTEXT indexes one by one or in controlled batches to force clean TiCI ingestion.
8. Add TiFlash replicas and wait for `progress=1`.
9. Run `ANALYZE TABLE` on all four tables.
10. Run validation queries and benchmark smoke tests before large QPS runs.

The faster but less controlled path is TiDB BR `BACKUP TABLE` / `RESTORE TABLE`. If using BR, verify that FULLTEXT/TiCI index data is usable on the new cluster. If FTS queries fail or TiCI reader metadata looks stale, drop and recreate the FULLTEXT indexes in the target cluster.

## DDL Capture Commands

Run from the console host against the source cluster:

```bash
kubectl -n tidb-cluster run mysql-client-ddl --image=mysql:8.0 --restart=Never --rm -i -- \
  mysqldump -h tici-demo-s3-tidb -P 4000 -uroot --no-data jsm_assets2 obj_new obj_relationship_new \
  > jsm_assets2_rebuild_schema.sql

kubectl -n tidb-cluster run mysql-client-ddl --image=mysql:8.0 --restart=Never --rm -i -- \
  mysqldump -h tici-demo-s3-tidb -P 4000 -uroot --no-data jsm_assets3 obj_new obj_relationship_new \
  > jsm_assets3_rebuild_schema.sql
```

Confirm the FULLTEXT lines in the captured DDL:

```sql
FULLTEXT INDEX `idx_fts_1`(`text_value_1`) WITH PARSER NGRAM
FULLTEXT INDEX `idx_fts_4`(`text_value_4`) WITH PARSER NGRAM
FULLTEXT INDEX `idx_fts_5`(`text_value_5`) WITH PARSER NGRAM
FULLTEXT INDEX `idx_fts_7`(`text_value_7`) WITH PARSER NGRAM
FULLTEXT INDEX `idx_fts_20`(`text_value_20`) WITH PARSER NGRAM
FULLTEXT INDEX `idx_fts_22`(`text_value_22`) WITH PARSER NGRAM
FULLTEXT INDEX `idx_fts_label`(`label`) WITH PARSER NGRAM
```

## Backup And Restore Options

## New Cluster Run

The new EKS/TiDB/TiCI cluster was created and validated on 2026-04-27.

| Field | Value |
|---|---|
| AWS account | `178851224597` |
| Region | `us-east-2` |
| EKS cluster | `Atlassian-jsm-tici` |
| Kubernetes namespace | `tidb-cluster` |
| TidbCluster | `tici-demo-s3` |
| New S3 bucket | `s3://atlassian-jsm-tici-178851224597-us-east-2` |
| Shared EC2 key pair name | `atlassian-jsm-tici-shared-key` |
| Initial TiDB/TiKV/TiFlash replicas | `1 / 3 / 3` |

New cluster node groups:

| Node group | Instance type | Desired | Max |
|---|---|---:|---:|
| `node16c32` | `c8i.4xlarge` | 3 | 20 |
| `node-tikv` | `c8i.4xlarge` | 3 | 20 |
| `node-tiflash` | `m8i.4xlarge` | 3 | 20 |

Live component status after restore:

| Component | Replicas | Status |
|---|---:|---|
| PD | 1 | Running |
| TiDB | 1 | Running |
| TiKV | 3 | Running |
| TiFlash | 3 | Running |
| TiCDC | 1 | Running |
| TiCI meta | 1 | Running |
| TiCI worker | 1 | Running |

TiKV pods use `24Gi` memory request on `c8i.4xlarge` because EKS allocatable memory is about `26.2Gi`; the original `28Gi` request could not schedule.

The source BR backup was copied to the new bucket:

```text
s3://atlassian-jsm-tici-178851224597-us-east-2/br-backups/jsm-assets2-assets3-20260427T042546Z
```

Restore command used on the new cluster:

```sql
RESTORE TABLE
  jsm_assets2.obj_new,
  jsm_assets2.obj_relationship_new,
  jsm_assets3.obj_new,
  jsm_assets3.obj_relationship_new
FROM 's3://atlassian-jsm-tici-178851224597-us-east-2/br-backups/jsm-assets2-assets3-20260427T042546Z?region=us-east-2';
```

Restore result:

| Field | Value |
|---|---|
| Start | `2026-04-27 08:41:55 UTC` |
| End | `2026-04-27 08:58:58 UTC` |
| Elapsed | `17m02s` |
| Restored size reported by TiDB | `127,600,242,452 bytes` |

Post-restore table stats on the new cluster:

| Table | Rows | data_length | index_length |
|---|---:|---:|---:|
| `jsm_assets2.obj_new` | 14,000,000 | 62.53 GiB | 638.72 GiB |
| `jsm_assets2.obj_relationship_new` | 139,991,715 | 20.47 GiB | 45.37 GiB |
| `jsm_assets3.obj_new` | 10,000,000 | 44.59 GiB | 489.27 GiB |
| `jsm_assets3.obj_relationship_new` | 100,005,360 | 14.62 GiB | 32.41 GiB |

TiFlash replicas after restore:

| Table | replica_count | available | progress |
|---|---:|---:|---:|
| `jsm_assets2.obj_new` | 1 | 1 | 1 |
| `jsm_assets2.obj_relationship_new` | 1 | 1 | 1 |
| `jsm_assets3.obj_new` | 1 | 1 | 1 |
| `jsm_assets3.obj_relationship_new` | 1 | 1 | 1 |

BR restored FULLTEXT definitions but not usable TiCI index contents in the new TiCI S3 prefix. Initial smoke test showed `MATCH(text_value_7) AGAINST('Fagor') = 0` while `LIKE '%Fagor%'` returned rows. The FULLTEXT indexes were rebuilt on both `obj_new` tables by dropping stale FTS indexes and adding them one by one.

Before rebuilding FULLTEXT indexes, TiDB global sort storage was configured:

```sql
SET GLOBAL tidb_cloud_storage_uri =
  's3://atlassian-jsm-tici-178851224597-us-east-2/tidb-global-sort?region=us-east-2';
```

FULLTEXT rebuild result:

| Field | Value |
|---|---|
| Start | `2026-04-27 09:03:39 UTC` |
| End | `2026-04-27 09:18:15 UTC` |
| Elapsed | `14m36s` |
| Rebuilt indexes | `idx_fts_1`, `idx_fts_4`, `idx_fts_5`, `idx_fts_7`, `idx_fts_20`, `idx_fts_22`, `idx_fts_label` on both `obj_new` tables |

FULLTEXT smoke check after rebuild:

| Query | MATCH rows | LIKE rows |
|---|---:|---:|
| `jsm_assets2.obj_new text_value_7 Fagor` | 601,589 | 601,589 |
| `jsm_assets3.obj_new text_value_7 Fagor` | 429,911 | 429,911 |

## Current Backup Run

The four-table backup was completed successfully on 2026-04-27.

| Field | Value |
|---|---|
| Kubernetes Job | `tidb-cluster/jsm-assets-br-backup-20260427t042546z` |
| Status | `Complete` |
| Source tables | `jsm_assets2.obj_new`, `jsm_assets2.obj_relationship_new`, `jsm_assets3.obj_new`, `jsm_assets3.obj_relationship_new` |
| Destination | `s3://michael-s3-us-east-2/br-backups/jsm-assets2-assets3-20260427T042546Z` |
| BackupTS | `465899080366948362` |
| SQL start time | `2026-04-27 04:25:47 UTC` |
| SQL end time | `2026-04-27 04:30:19 UTC` |
| SQL reported size | `127,600,242,452 bytes` |
| S3 final size | `127,603,146,073 bytes` |
| S3 object count | `4,812` |

Restore from this backup:

```sql
RESTORE TABLE
  jsm_assets2.obj_new,
  jsm_assets2.obj_relationship_new,
  jsm_assets3.obj_new,
  jsm_assets3.obj_relationship_new
FROM 's3://michael-s3-us-east-2/br-backups/jsm-assets2-assets3-20260427T042546Z?region=us-east-2';
```

### Option A: BR Table Backup

Use this if the goal is fastest table copy and then verify/rebuild FULLTEXT if needed.

```sql
BACKUP TABLE
  jsm_assets2.obj_new,
  jsm_assets2.obj_relationship_new,
  jsm_assets3.obj_new,
  jsm_assets3.obj_relationship_new
TO 's3://<bucket>/<prefix>/jsm-assets-rebuild?region=us-east-2';
```

On the new cluster:

```sql
RESTORE TABLE
  jsm_assets2.obj_new,
  jsm_assets2.obj_relationship_new,
  jsm_assets3.obj_new,
  jsm_assets3.obj_relationship_new
FROM 's3://<bucket>/<prefix>/jsm-assets-rebuild?region=us-east-2';
```

### Option B: Data Import Then Index Build

Use this if the goal is the cleanest TiCI/FULLTEXT rebuild.

1. Capture source DDL.
2. Remove secondary and FULLTEXT indexes from initial DDL, keeping primary keys and required generated columns.
3. Export table data with Dumpling or another table-level export path.
4. Import into the target with Lightning or batched load.
5. Add secondary indexes.
6. Add FULLTEXT indexes with `WITH PARSER NGRAM`.

For the current benchmark workload, this path is safer than copying TiCI metadata because TiCI fulltext index data should be generated by the new cluster.

## Validation SQL

Run after restore/import and index creation:

```sql
SELECT table_schema, table_name, table_rows,
       ROUND(data_length/1024/1024/1024, 2) AS data_gib,
       ROUND(index_length/1024/1024/1024, 2) AS index_gib,
       ROUND((data_length + index_length)/1024/1024/1024, 2) AS total_gib
FROM information_schema.tables
WHERE table_schema IN ('jsm_assets2', 'jsm_assets3')
  AND table_name IN ('obj_new', 'obj_relationship_new')
ORDER BY table_schema, table_name;

SELECT table_schema, table_name, COUNT(DISTINCT index_name) AS index_count,
       COUNT(DISTINCT CASE WHEN index_name LIKE 'idx_fts%' THEN index_name END) AS fts_index_count,
       COUNT(DISTINCT CASE WHEN non_unique = 0 THEN index_name END) AS unique_index_count
FROM information_schema.statistics
WHERE table_schema IN ('jsm_assets2', 'jsm_assets3')
  AND table_name IN ('obj_new', 'obj_relationship_new')
GROUP BY table_schema, table_name
ORDER BY table_schema, table_name;

SELECT table_schema, table_name, replica_count, available, progress
FROM information_schema.tiflash_replica
WHERE table_schema IN ('jsm_assets2', 'jsm_assets3')
  AND table_name IN ('obj_new', 'obj_relationship_new')
ORDER BY table_schema, table_name;
```

FTS smoke test pattern:

```sql
SELECT COUNT(*)
FROM jsm_assets2.obj_new
WHERE MATCH(text_value_4) AGAINST ('"mr.willodean.schiller@von.test"' IN BOOLEAN MODE);
```

MPP/TiFlash smoke test pattern:

```sql
SET tidb_enforce_mpp = ON;
SET tiflash_hash_join_version = 'optimized';

EXPLAIN ANALYZE
SELECT o.sequential_id, o.label
FROM jsm_assets3.obj_new o
JOIN jsm_assets3.obj_relationship_new r
  ON o.id = r.object_id
WHERE o.workspace_id = '<known-workspace-id>'
  AND r.workspace_id = '<known-workspace-id>'
LIMIT 1000;
```

## Operational Notes

- Use a fresh S3 prefix for TiCI on the new cluster.
- Do not copy `tici` database meta tables from the old cluster.
- Do not copy TiCI worker local cache.
- Build FULLTEXT indexes after the base data is present if the goal is a clean benchmark environment.
- Avoid creating all seven FULLTEXT indexes in parallel unless the target cluster has enough TiDB/TiKV/TiCI headroom; previous index builds have hit OOM pressure.
- After large restore/import, run `ANALYZE TABLE` before recording latency or QPS.
- Keep the first validation benchmark small. Verify `EXPLAIN` paths before running the full QPS workload.
