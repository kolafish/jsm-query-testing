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

## Compatibility Procedure Rehearsed

Authoritative procedure from the new-version compatibility guidance:

1. Drop FTS indexes.
2. Stop TiCI service.
3. Drop the `tici` database from TiDB.
4. Remove the old changefeed and remove S3 data under the TiCI S3 prefix.
5. Add a new changefeed without date separator.
6. Start TiCI service.
7. Add FTS indexes.

For the new storage changefeed, use `date-separator=none`. In this cluster, putting only `date-separator=none` in the sink URI was not sufficient: TiCDC accepted the URI but `changefeed query` still showed `date_separator: "day"` and S3 files were written under a `YYYY-MM-DD` path. The working procedure was to create the changefeed with both the sink URI and a config file containing:

```toml
[sink]
protocol = "canal-json"
date-separator = "none"
enable-partition-separator = true
```

New sink URI for this cluster:

```text
s3://atlassian-jsm-tici-178851224597-us-east-2/tici_shared_prefix/cdc?force-path-style=false&protocol=canal-json&enable-tidb-extension=true&output-row-key=true&use-table-id-as-path=true&date-separator=none
```

## Executed Steps

1. Saved pre-upgrade evidence under `upgrade_rehearsal_20260520/`.
2. Generated FTS drop/create SQL for all current FTS indexes.
3. Dropped all `138` FTS indexes from `jsm_assets2.obj_new`, `jsm_assets3.obj_new`, and `jsm_assets4.obj_new`.
4. Stopped TiCI meta and worker.
5. Dropped the `tici` database from TiDB.
6. Removed old changefeed `tici-replication-task`.
7. Deleted the whole S3 prefix `s3://atlassian-jsm-tici-178851224597-us-east-2/tici_shared_prefix/`.
8. Patched TiDB, TiKV, TiFlash, TiCI meta, and TiCI worker images to the target images.
9. Waited for all upgraded pods to become ready and confirmed running images.
10. Recreated changefeed `tici-replication-task` with sink config `date-separator = "none"`.
11. Restarted TiCI meta and worker.
12. Recreated all `138` FTS indexes serially. TiDB does not support multi-schema change for `ADD FULLTEXT INDEX`.
13. Validated row counts, TiFlash replica availability, TiCI meta rows, TiCI import jobs, changefeed status, S3 path layout, and FTS smoke queries.

## Execution Results

| Area | Result |
|---|---|
| Image upgrade | Succeeded. TiDB, TiKV, TiFlash, TiCI meta, and TiCI worker are on target images. |
| TiDB Operator | Not upgraded. It remained `pingcap/tidb-operator:v1.7.0-alpha.10-31-ga0cc44aea`. |
| FTS drop | Succeeded for all `138` indexes. |
| `tici` database reset | Succeeded. New TiCI tables were recreated by TiCI v0.3.0. |
| Old changefeed removal | Succeeded. |
| S3 prefix cleanup | Succeeded. Pre-delete prefix had `3425` objects, `195149817075` bytes; post-delete count was `0`. |
| Changefeed recreate | Succeeded. Final state `normal`; final `config.sink.date_separator` is `none`. |
| FTS recreate | Succeeded for all `138` indexes. Timed run: `2026-05-20T02:12:45Z` to `2026-05-20T03:49:11Z`. |
| TiCI import jobs | `138` import jobs all `finished`; `3297` import job tasks all `finish`. |
| Pod health | All TiDB/TiKV/TiFlash/TiCDC/TiCI pods were Running with `0` restarts after the rehearsal. |

Final component images:

| Component | Running image |
|---|---|
| TiDB | `us-docker.pkg.dev/pingcap-testing-account/hotfix/pingcap/tidb/images/tidb-server:v8.5.6-20260519-f7f5d8b-10457` |
| TiKV | `us-docker.pkg.dev/pingcap-testing-account/hotfix/tikv/tikv/image:v8.5.6-20260519-b7d1a0f-10459` |
| TiFlash | `us-docker.pkg.dev/pingcap-testing-account/hub/pingcap/tiflash/image:v8.5.6-20260519-317f5f6` |
| TiCI meta/worker | `us-docker.pkg.dev/pingcap-testing-account/dev/pingcap/tici/image:v0.3.0-496b5a2` |
| TiCDC | `gcr.io/pingcap-public/dbaas/ticdc:v8.5.6-release.3` |
| PD | `gcr.io/pingcap-public/dbaas/pd:v8.5.6-20260423-4b9dde5` |

## Validation Results

| Check | Result |
|---|---|
| Row counts | Unchanged: `jsm_assets2.obj_new=14,000,000`, `jsm_assets2.obj_relationship_new=139,991,715`, `jsm_assets3.obj_new=10,000,000`, `jsm_assets3.obj_relationship_new=100,005,360`, `jsm_assets4.obj_new=14,000,000`, `jsm_assets4.obj_relationship_new=139,988,146`. |
| TiFlash replicas | All six target tables have `replica_count=1`, `available=1`, `progress=1`. |
| SHOW INDEX FTS count | `jsm_assets2.obj_new=7`, `jsm_assets3.obj_new=7`, `jsm_assets4.obj_new=124`. |
| TiCI meta | `tici.tici_index_meta=138`, `tici.tici_shard_meta=426`. |
| Changefeed | `tici-replication-task` state `normal`; `config.sink.date_separator=none`. |
| S3 CDC path | Verified files under `tici_shared_prefix/cdc/<table_id>/<commit_ts>/...`; no date directory for new files. |
| FTS smoke | `jsm_assets2.text_value_1` matched `7` rows, `jsm_assets3.text_value_1` matched `2` rows, `jsm_assets4.text_value_1` matched `44` rows. |
| TiCI logs | No `ERROR`, panic, or `Watch handle is finished` in final worker log tail. Meta log had repeated `topology freeze` split warnings during import, but all import jobs finished successfully. |

Note: `information_schema.statistics.index_type` reports these FTS indexes as `BTREE`, but `SHOW INDEX ... WHERE Index_type='FULLTEXT'` reports them correctly as `FULLTEXT`. The validation count above uses `SHOW INDEX`.

## Post-Upgrade Workload Validation

Executed after the image upgrade, TiCI metadata reset, changefeed recreation, and all `138` FTS indexes finished rebuilding. Full result JSON: `bench/results/upgrade_rehearsal_workload_validation_20260520.json`.

| Workload | Database | Queries | Errors | Row-count mismatches | Zero-row queries | p50 latency | p95 latency | Max latency |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Workload smoke corpus | `jsm_assets3` | 49 | 0 | 0 | 10 | 222.13 ms | 769.46 ms | 9848.02 ms |
| LIKE-to-MATCH rewrite corpus | `jsm_assets3` | 10 | 0 | 0 | 3 | 502.55 ms | 12051.03 ms | 13688.78 ms |
| FTS+JOIN MATCH corpus | `jsm_assets2` | 10 | 0 | 0 | 1 | 1311.65 ms | 10061.48 ms | 10332.92 ms |
| FTS indexed-column sample | `jsm_assets4` | 10 | 0 | n/a | n/a | n/a | n/a | n/a |

`jsm_assets4` FTS sample details:

| Column | Sample term | MATCH count | MATCH latency | Notes |
|---|---|---:|---:|---|
| `label` | `Bosch-10603` | 44 | 221.74 ms | Returned rows. |
| `text_value_1` | `Bosch-39517` | 28 | 223.48 ms | Returned rows. |
| `text_value_4` | `britni.nader@quitzon.test` | 4 | 221.97 ms | Returned rows. |
| `text_value_5` | `www.morgan-prohaska.net` | 4 | 219.85 ms | Returned rows. |
| `text_value_7` | `Bosch` | 599,993 | 243.73 ms | Returned rows. |
| `text_value_20` | `2` | 0 | 221.70 ms | Query executed without error; sampled values are single-token encoded values and do not match current boolean MATCH tokenization. |
| `text_value_22` | `Analysed` | 2,331,753 | 363.40 ms | Returned rows. |
| `text_value_10` | `Fagor` | 598,750 | 239.02 ms | Returned rows. |
| `text_value_50` | n/a | n/a | n/a | No non-empty, non-sentinel sample value found. |
| `text_value_99` | n/a | n/a | n/a | No non-empty, non-sentinel sample value found. |

Slowest queries in this validation:

| Workload | Query | Latency | Rows |
|---|---|---:|---:|
| LIKE-to-MATCH rewrite corpus | `1_basic_filters_|_query_2` | 13688.78 ms | 28 |
| FTS+JOIN MATCH corpus | `fts_join_q1_tv7_fagor_w8` | 10332.92 ms | 1000 |
| LIKE-to-MATCH rewrite corpus | `2_full_text_search_|_query_3` | 10049.34 ms | 3 |
| Workload smoke corpus | `fts_match_q2` | 9848.02 ms | 1 |
| FTS+JOIN MATCH corpus | `fts_join_q6_tv4_morissette_w3b4c` | 9729.73 ms | 1000 |

## Evidence Files

Key evidence files are under `upgrade_rehearsal_20260520/`:

- `pre_tidbcluster.yaml`
- `pre_mysql_evidence.tsv`
- `pre_changefeed_list.json`
- `pre_s3_tici_prefix_summary.json`
- `fts_drop.sql`
- `fts_create.sql`
- `changefeed_date_none.toml`
- `post_upgrade_images.txt`
- `recreate_changefeed_date_none.log`
- `recreate_fts_timed.log`
- `post_upgrade_validation.log`
- `post_upgrade_show_index_fulltext_counts.tsv`
- `post_upgrade_show_index_fulltext.tsv`
- `post_upgrade_final_mysql_summary.log`
- `post_upgrade_fts_smoke_retry.log`
- `bench/results/upgrade_rehearsal_workload_validation_20260520.json`

## Customer-Facing Recommendation

Do not send only a raw script. The destructive parts are DDL, metadata deletion, changefeed removal, and S3 deletion, so the safer package is:

- A runbook that states prerequisites, exact image tags, expected operator deployment shape, backup requirements, commands, validation checks, and rollback boundaries.
- A guarded helper script that supports `--dry-run`, prints every destructive command, validates namespace/cluster/bucket/prefix/current images, requires an explicit confirmation flag for S3 deletion, creates the new changefeed with an explicit config file for `date-separator = "none"`, and logs all output.
- A separate SQL file containing the exact FTS drop/create statements generated from the customer schema, so the customer can review index scope before execution.

## References

- TiCDC storage sink path and `date-separator=none`: https://docs.pingcap.com/tidb/stable/ticdc-sink-to-cloud-storage/
