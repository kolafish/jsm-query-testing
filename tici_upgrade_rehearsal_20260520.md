# TiCI Upgrade Rehearsal - 2026-05-20

This document tracks the upgrade rehearsal for the AWS `Atlassian-jsm-tici` test cluster. The old Google Doc is used only as background for TiDB Operator, IRSA, and S3 deployment shape. The authoritative target images and compatibility procedure are the new values provided in this rehearsal request.

## Current Environment

| Item | Value |
|---|---|
| AWS account | `178851224597` |
| Region | `us-east-2` |
| EKS cluster | `Atlassian-jsm-tici` |
| Namespace | `tidb-cluster` |
| TidbCluster | `tici-demo-s3` |
| Current scale | `3 TiDB / 3 TiKV / 6 TiFlash / 1 TiCDC / 1 TiCI meta / 1 TiCI worker` |
| Grafana | `http://a2e41aa49d08647d1b55ecd7b146bbf6-14b9d142fd22522c.elb.us-east-2.amazonaws.com:3000/` |

## Current Baseline Images

Captured from `tidb-cluster/tici-demo-s3` before starting the upgrade rehearsal.

| Component | Current image |
|---|---|
| TiDB | `gcr.io/pingcap-public/dbaas/tidb:v8.5.6-20260423-93f2dfb` |
| TiKV | `gcr.io/pingcap-public/dbaas/tikv:v8.5.6-20260424-74347d1` |
| TiFlash | `gcr.io/pingcap-public/dbaas/tiflash:v8.5.6-20260423-cbe33d1` |
| TiCDC | `gcr.io/pingcap-public/dbaas/ticdc:v8.5.6-release.3` |
| TiCI meta | `gcr.io/pingcap-public/dbaas/tici:v0.2.0` |
| TiCI worker | `gcr.io/pingcap-public/dbaas/tici:v0.2.0` |
| PD | `gcr.io/pingcap-public/dbaas/pd:v8.5.6-20260423-4b9dde5` |
| TiDB Operator | `pingcap/tidb-operator:v1.7.0-alpha.10-31-ga0cc44aea` |

Current TiCI configuration:

| Item | Value |
|---|---|
| Changefeed ID | `tici-replication-task` |
| Changefeed state before upgrade | `failed`, `CDC:ErrSnapshotLostByGC` |
| S3 bucket | `atlassian-jsm-tici-178851224597-us-east-2` |
| TiCI S3 prefix | `tici_shared_prefix` |
| Sink URI | `s3://atlassian-jsm-tici-178851224597-us-east-2/tici_shared_prefix/cdc?force-path-style=false&protocol=canal-json&enable-tidb-extension=true&output-row-key=true&use-table-id-as-path=true` |
| `tidb_enable_dist_task` | `ON` |
| `tidb_cloud_storage_uri` | `s3://atlassian-jsm-tici-178851224597-us-east-2/tidb-global-sort?region=us-east-2` |

## Current Data And FTS Indexes

| Database | Table | Rows | TiFlash replica | FTS indexes in TiCI meta |
|---|---:|---:|---|---:|
| `jsm_assets2` | `obj_new` | 14,000,000 | available, progress `1.0` | 7 |
| `jsm_assets2` | `obj_relationship_new` | 139,991,715 | available, progress `1.0` | 0 |
| `jsm_assets3` | `obj_new` | 10,000,000 | available, progress `1.0` | 7 |
| `jsm_assets3` | `obj_relationship_new` | 100,005,360 | available, progress `1.0` | 0 |
| `jsm_assets4` | `obj_new` | 14,000,000 | available, progress `1.0` | 124 |
| `jsm_assets4` | `obj_relationship_new` | 139,988,146 | available, progress `1.0` | 0 |

FTS parser: all current TiCI FTS metadata entries use `ngram`.

## Target Images

These are the authoritative upgrade target images for this rehearsal.

| Component | Target image | Target version |
|---|---|---|
| TiCI | `us-docker.pkg.dev/pingcap-testing-account/dev/pingcap/tici/image:v0.3.0-496b5a2` | `v0.3.0` |
| TiDB | `us-docker.pkg.dev/pingcap-testing-account/hotfix/pingcap/tidb/images/tidb-server:v8.5.6-20260519-f7f5d8b-10457` | `v8.5.6-20260519-f7f5d8b` |
| TiFlash | `us-docker.pkg.dev/pingcap-testing-account/hub/pingcap/tiflash/image:v8.5.6-20260519-317f5f6` | `v8.5.6-20260519-317f5f6` |
| TiKV | `us-docker.pkg.dev/pingcap-testing-account/hotfix/tikv/tikv/image:v8.5.6-20260519-b7d1a0f-10459` | `v8.5.6-20260519-b7d1a0f` |

Image pull preflight: all four target images were successfully pulled by pods in the current EKS cluster.

## Compatibility Procedure To Rehearse

Authoritative procedure from the new-version compatibility guidance:

1. Drop FTS indexes.
2. Stop TiCI service.
3. Drop the `tici` database from TiDB.
4. Remove the old changefeed and remove S3 data under the TiCI S3 prefix.
5. Add a new changefeed without date separator.
6. Start TiCI service.
7. Add FTS indexes.

For the new storage changefeed, use `date-separator=none`. TiCDC storage sink documentation defines `none` as no date separator in the path.

Proposed new sink URI for this cluster:

```text
s3://atlassian-jsm-tici-178851224597-us-east-2/tici_shared_prefix/cdc?force-path-style=false&protocol=canal-json&enable-tidb-extension=true&output-row-key=true&use-table-id-as-path=true&date-separator=none
```

## Proposed Execution Plan

1. Save pre-upgrade evidence: TidbCluster YAML, row counts, TiFlash replica status, current FTS DDL, current `tici` meta table row counts, current changefeed status, and S3 prefix inventory.
2. Generate and review the exact `ALTER TABLE ... DROP INDEX ...` and `ALTER TABLE ... ADD FULLTEXT INDEX ... WITH PARSER NGRAM` statements for all target FTS indexes.
3. Drop FTS indexes on the selected target tables.
4. Stop TiCI service by scaling `tici-demo-s3-tici-meta` and `tici-demo-s3-tici-worker` to `0`.
5. Drop the `tici` database from TiDB.
6. Remove the old TiCDC changefeed `tici-replication-task`.
7. Delete S3 objects under `s3://atlassian-jsm-tici-178851224597-us-east-2/tici_shared_prefix/` after recording the object count and size.
8. Patch TiDB, TiKV, TiFlash, TiCI meta, and TiCI worker images in the TidbCluster CR to the target images.
9. Wait for all upgraded pods to become ready and confirm their running images.
10. Recreate changefeed `tici-replication-task` with `date-separator=none`.
11. Start TiCI service.
12. Recreate FTS indexes.
13. Wait for TiCI metadata and import jobs to settle.
14. Validate row counts, TiFlash replica availability, TiCI meta rows, FTS smoke queries, and TiKV/TiFlash control queries.

## Decisions Needed Before Destructive Steps

| Decision | Default I will use if approved |
|---|---|
| Whether to upgrade TiDB Operator too | Do not upgrade operator unless the new images or CR fields require it. The target image list does not include operator. |
| FTS rebuild scope | Rebuild all current FTS indexes in `jsm_assets2.obj_new`, `jsm_assets3.obj_new`, and `jsm_assets4.obj_new` (`138` total). |
| S3 delete scope | Delete the whole TiCI prefix `s3://atlassian-jsm-tici-178851224597-us-east-2/tici_shared_prefix/`, not just `cdc/`, because the guidance says TiCI S3 prefix. |
| Changefeed start position | Create the replacement changefeed from current time unless compatibility guidance requires replaying from an earlier TSO. Since FTS indexes are rebuilt after TiCI restart, current-time CDC is usually sufficient for new writes after rebuild. |
| Customer deliverable | Provide both a human-reviewed runbook and a guarded script with dry-run mode. |

## Customer-Facing Recommendation

Do not send only a raw script. The destructive parts are DDL, metadata deletion, changefeed removal, and S3 deletion, so the safer package is:

- A runbook that states prerequisites, exact image tags, expected operator deployment shape, backup requirements, commands, validation checks, and rollback boundaries.
- A guarded helper script that supports `--dry-run`, prints every destructive command, validates namespace/cluster/bucket/prefix/current images, requires an explicit confirmation flag for S3 deletion, and logs all output.
- A separate SQL file containing the exact FTS drop/create statements generated from the customer schema, so the customer can review index scope before execution.

## References

- TiCDC storage sink path and `date-separator=none`: https://docs.pingcap.com/tidb/stable/ticdc-sink-to-cloud-storage/
