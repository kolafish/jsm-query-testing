# TiCI Compatibility Upgrade Helper

This package is the minimal customer-facing helper for upgrading a TiDB Operator
cluster with existing TiCI FULLTEXT indexes to a TiCI version whose metadata and
S3 layout are incompatible with the previous release.

The package contains two files:

- `README.md`: this runbook.
- `tici_upgrade_compat.sh`: the guarded helper script.

## What The Script Does

The script follows the compatibility procedure:

1. Save pre-upgrade evidence.
2. Generate `fts_drop.sql` and `fts_create.sql` from the current schema.
3. Drop existing FULLTEXT indexes.
4. Stop TiCI meta and TiCI worker through the `TidbCluster` CR.
5. Drop the `tici` database from TiDB.
6. Remove the old TiCDC changefeed.
7. Delete the old TiCI S3 prefix.
8. Optionally patch target component images if target image variables are set.
9. Create a new changefeed with `date-separator = "none"`.
10. Start TiCI meta and TiCI worker.
11. Recreate FULLTEXT indexes.
12. Wait for TiCI import jobs to finish.
13. Run validation checks.

The script embeds the required changefeed config and writes it to the working
directory at runtime:

```toml
[sink]
protocol = "canal-json"
date-separator = "none"
enable-partition-separator = true
```

Do not create the new changefeed using only a sink URI parameter. In rehearsal,
putting `date-separator=none` only in the URI was accepted by TiCDC, but
`changefeed query` still showed `date_separator: "day"`.

## Prerequisites

- The cluster is managed by TiDB Operator and has a `TidbCluster` CR.
- `kubectl` can access the Kubernetes cluster.
- `mysql` can connect to TiDB.
- `aws` can list and delete objects under the TiCI S3 prefix.
- TiCDC CLI is available either inside the TiCDC pod at `/cdc`, or locally.
- TiDB data and the TiCI S3 prefix have been backed up before execution.

## Prepare Environment File

Create `customer.env`:

```bash
NAMESPACE=tidb-cluster
CLUSTER=tici-demo-s3

TIDB_HOST=127.0.0.1
TIDB_PORT=4000
TIDB_USER=root
TIDB_PASSWORD=

S3_BUCKET=your-tici-bucket
S3_PREFIX=tici_default_prefix
AWS_REGION=us-east-2
CHANGEFEED_ID=tici-replication-task

# Default is to run cdc cli inside the TiCDC pod.
CDC_MODE=pod
CDC_SERVER=http://127.0.0.1:8300

# Optional: restrict FULLTEXT DDL generation to specific databases.
# Comma separated. Leave empty to scan all non-system schemas.
DATABASES=

# Optional image patching. Leave empty if images are upgraded separately.
TARGET_TIDB_BASE_IMAGE=
TARGET_TIDB_VERSION=
TARGET_TIKV_BASE_IMAGE=
TARGET_TIKV_VERSION=
TARGET_TIFLASH_BASE_IMAGE=
TARGET_TIFLASH_VERSION=
TARGET_TICI_BASE_IMAGE=
TARGET_TICI_VERSION=

# Optional smoke SQL file. Each statement should be read-only.
SMOKE_SQL_FILE=
```

If `TIDB_HOST=127.0.0.1`, start a port-forward in another terminal before
running the script:

```bash
kubectl -n tidb-cluster port-forward svc/tici-demo-s3-tidb 4000:4000
```

## Dry Run

Always run dry-run first:

```bash
./tici_upgrade_compat.sh --env ./customer.env --dry-run
```

Review generated files under the working directory:

- `fts_drop.sql`
- `fts_create.sql`
- `changefeed-date-none.toml`
- `pre_tidbcluster.yaml`
- `pre_fulltext_indexes.tsv`
- `pre_s3_prefix_summary.txt`

## Execute

Only execute after reviewing generated SQL and confirming backup completion:

```bash
./tici_upgrade_compat.sh \
  --env ./customer.env \
  --execute \
  --confirm-delete-s3-prefix tici_default_prefix
```

`--confirm-delete-s3-prefix` must exactly match `S3_PREFIX`. The script refuses
to delete S3 objects if the prefix is empty, `/`, `.`, `*`, or the confirmation
does not match.

## Resume

If a stage fails after partial completion, fix the issue and resume from a
specific stage:

```bash
./tici_upgrade_compat.sh \
  --env ./customer.env \
  --execute \
  --workdir ./tici-upgrade-work-20260520-120000 \
  --resume-from create-changefeed \
  --confirm-delete-s3-prefix tici_default_prefix
```

Supported stages:

```text
precheck
generate-fts-ddl
drop-fts
stop-tici
drop-tici-db
reset-changefeed
patch-images
create-changefeed
start-tici
recreate-fts
wait-import
validate
```

## Validate Only

Run read-only validation after the upgrade:

```bash
./tici_upgrade_compat.sh --env ./customer.env --validate-only
```

Validation checks include:

- `TidbCluster` and pod status.
- FULLTEXT index count.
- TiCI metadata and import job status.
- Changefeed state and `date_separator`.
- S3 path shape under the TiCI prefix.
- Optional read-only smoke SQL.

## Safety Notes

This process is destructive:

- It drops and recreates FULLTEXT indexes.
- It drops the `tici` metadata database.
- It removes the old TiCDC changefeed.
- It deletes the configured TiCI S3 prefix.

The base table data is not dropped by this script, but the operation should
still be treated as an upgrade maintenance procedure that requires a confirmed
backup and an approved maintenance window.

