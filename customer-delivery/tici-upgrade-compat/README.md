# TiCI Compatibility Reset Helper

This helper does not upgrade TiDB, TiKV, TiFlash, or TiCI images. It only handles
the TiCI compatibility reset required when an upgraded TiCI version cannot reuse
the old FULLTEXT metadata, old changefeed, or old TiCI S3 layout.

## Procedure

The script performs these steps:

1. Drop FTS indexes.
2. Stop TiCI service.
3. Drop the `tici` database from TiDB.
4. Remove old changefeed and remove S3 data under the TiCI S3 prefix.
5. Add a new changefeed without date separator.
6. Start TiCI service.
7. Add FTS indexes.

Before dropping FTS indexes, the script generates these files from the current
schema:

- `fts_drop.sql`
- `fts_create.sql`

Review both files after `--dry-run` and before `--execute`.

## Required Inputs

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

# Use the TiCDC CLI inside the TiCDC pod by default.
CDC_MODE=pod
CDC_SERVER=http://127.0.0.1:8300

# Optional: comma-separated database list. Empty means all non-system schemas.
DATABASES=
```

If `TIDB_HOST=127.0.0.1`, start TiDB port-forward separately:

```bash
kubectl -n tidb-cluster port-forward svc/tici-demo-s3-tidb 4000:4000
```

## Run

Dry-run first:

```bash
./tici_upgrade_compat.sh --env ./customer.env --dry-run
```

Execute only after backup and SQL review:

```bash
./tici_upgrade_compat.sh \
  --env ./customer.env \
  --execute \
  --confirm-delete-s3-prefix tici_default_prefix
```

Validate only:

```bash
./tici_upgrade_compat.sh --env ./customer.env --validate-only
```

## Important Notes

- This script is destructive: it drops FTS indexes, drops the `tici` database,
  removes the old changefeed, and deletes the configured TiCI S3 prefix.
- The script prints each compatibility action as `Step N/7` in the execution log.
- `--confirm-delete-s3-prefix` must exactly match `S3_PREFIX`; otherwise S3
  deletion is refused.
- The new changefeed is created with an embedded config equivalent to:

```toml
[sink]
protocol = "canal-json"
date-separator = "none"
enable-partition-separator = true
```

- Do not rely on only adding `date-separator=none` to the sink URI. The script
  also validates that the created changefeed reports `date_separator = none`.
