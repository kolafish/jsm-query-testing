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

TIDB_HOST=tici-demo-s3-tidb
TIDB_PORT=4000
TIDB_USER=root
TIDB_PASSWORD=

# For long DDL, prefer running mysql inside the Kubernetes cluster.
# Use `local` if you already have a stable local TiDB connection.
MYSQL_MODE=pod
MYSQL_CLIENT_POD=tici-compat-mysql-client
MYSQL_CLIENT_IMAGE=mysql:8.0
MYSQL_CLIENT_CREATE=true

S3_BUCKET=your-tici-bucket
S3_PREFIX=tici_default_prefix
AWS_REGION=us-east-2
CHANGEFEED_ID=tici-replication-task

# Use the TiCDC CLI inside the TiCDC pod by default.
CDC_MODE=pod
CDC_SERVER=http://127.0.0.1:8301

# TiDB Operator deployment. Defaults shown here match standard TiDB Operator installs.
TIDB_OPERATOR_NAMESPACE=tidb-admin
TIDB_OPERATOR_DEPLOYMENT=tidb-controller-manager

# Optional: comma-separated database list. Empty means all non-system schemas.
DATABASES=
```

If `MYSQL_MODE=local` and `TIDB_HOST=127.0.0.1`, start TiDB port-forward separately:

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

## Manual Commands

The script is the recommended path. If the same compatibility reset must be
performed manually, use the commands below. They mirror the script behavior.

Prepare shell variables and generate the FTS drop/create SQL first:

```bash
source ./customer.env
WORKDIR=./tici-compat-manual
mkdir -p "$WORKDIR"

MYSQL_PASSWORD_ARG=()
if [ -n "${TIDB_PASSWORD:-}" ]; then
  MYSQL_PASSWORD_ARG=("--password=${TIDB_PASSWORD}")
fi

SINK_URI="s3://${S3_BUCKET}/${S3_PREFIX}/cdc?force-path-style=false&protocol=canal-json&enable-tidb-extension=true&output-row-key=true&use-table-id-as-path=true&date-separator=none"

# Use the script dry-run to generate $WORKDIR/fts_drop.sql and
# $WORKDIR/fts_create.sql without executing destructive steps.
./tici_upgrade_compat.sh --env ./customer.env --dry-run --workdir "$WORKDIR"

# If using MYSQL_MODE=pod, prepare the in-cluster mysql client.
kubectl -n "$NAMESPACE" run "$MYSQL_CLIENT_POD" \
  --image="$MYSQL_CLIENT_IMAGE" \
  --restart=Never \
  --command -- sleep 86400
kubectl -n "$NAMESPACE" wait --for=condition=Ready "pod/$MYSQL_CLIENT_POD" --timeout=180s
```

1. Drop FTS indexes.

```bash
kubectl -n "$NAMESPACE" exec -i "$MYSQL_CLIENT_POD" -- \
  mysql -h "$TIDB_HOST" -P "$TIDB_PORT" -u "$TIDB_USER" "${MYSQL_PASSWORD_ARG[@]}" \
  < "$WORKDIR/fts_drop.sql"
```

2. Stop TiCI service.

```bash
kubectl -n "$NAMESPACE" patch tidbcluster "$CLUSTER" --type merge \
  -p '{"spec":{"tici":{"changefeed":{"enable":false}}}}'

# Stop the operator first so it does not reconcile TiCI meta/worker back up.
kubectl -n "$TIDB_OPERATOR_NAMESPACE" scale deployment "$TIDB_OPERATOR_DEPLOYMENT" --replicas=0
kubectl -n "$TIDB_OPERATOR_NAMESPACE" get deployment "$TIDB_OPERATOR_DEPLOYMENT"

kubectl -n "$NAMESPACE" scale statefulset "$CLUSTER-tici-meta" --replicas=0
kubectl -n "$NAMESPACE" scale statefulset "$CLUSTER-tici-worker" --replicas=0
kubectl -n "$NAMESPACE" wait --for=delete "pod/$CLUSTER-tici-meta-0" --timeout=600s
kubectl -n "$NAMESPACE" wait --for=delete "pod/$CLUSTER-tici-worker-0" --timeout=600s
kubectl -n "$NAMESPACE" get statefulset "$CLUSTER-tici-meta" "$CLUSTER-tici-worker"
```

3. Drop the `tici` database from TiDB.

```bash
kubectl -n "$NAMESPACE" exec "$MYSQL_CLIENT_POD" -- \
  mysql -h "$TIDB_HOST" -P "$TIDB_PORT" -u "$TIDB_USER" "${MYSQL_PASSWORD_ARG[@]}" \
  -e "DROP DATABASE IF EXISTS tici;"
```

4. Remove old changefeed and remove S3 data under the TiCI S3 prefix.

```bash
CDC_POD="$(kubectl -n "$NAMESPACE" get pod \
  -l "app.kubernetes.io/instance=$CLUSTER,app.kubernetes.io/component=ticdc" \
  -o jsonpath='{.items[0].metadata.name}')"

kubectl -n "$NAMESPACE" exec "$CDC_POD" -- \
  /cdc cli changefeed query \
  --server="$CDC_SERVER" \
  --changefeed-id="$CHANGEFEED_ID"

kubectl -n "$NAMESPACE" exec "$CDC_POD" -- \
  /cdc cli changefeed remove \
  --server="$CDC_SERVER" \
  --changefeed-id="$CHANGEFEED_ID"

aws s3 rm "s3://${S3_BUCKET}/${S3_PREFIX}/" \
  --recursive \
  --region "$AWS_REGION"
```

5. Add a new changefeed without date separator.

```bash
cat > "$WORKDIR/changefeed-date-none.toml" <<'EOF'
[sink]
protocol = "canal-json"
date-separator = "none"
enable-partition-separator = true
EOF

kubectl -n "$NAMESPACE" cp "$WORKDIR/changefeed-date-none.toml" \
  "$CDC_POD:/tmp/changefeed-date-none.toml"

kubectl -n "$NAMESPACE" exec "$CDC_POD" -- \
  /cdc cli changefeed create \
  --server="$CDC_SERVER" \
  --changefeed-id="$CHANGEFEED_ID" \
  --sink-uri="$SINK_URI" \
  --config=/tmp/changefeed-date-none.toml
```

6. Start TiCI service.

```bash
cat > "$WORKDIR/start-tici-patch.json" <<EOF
{
  "spec": {
    "tici": {
      "changefeed": {
        "enable": true,
        "changefeedID": "${CHANGEFEED_ID}",
        "sinkURI": "${SINK_URI}"
      },
      "meta": {"replicas": ${TICI_META_REPLICAS:-1}},
      "worker": {"replicas": ${TICI_WORKER_REPLICAS:-1}}
    }
  }
}
EOF

kubectl -n "$NAMESPACE" patch tidbcluster "$CLUSTER" \
  --type merge \
  --patch-file "$WORKDIR/start-tici-patch.json"

kubectl -n "$NAMESPACE" scale statefulset "$CLUSTER-tici-meta" \
  --replicas="${TICI_META_REPLICAS:-1}"
kubectl -n "$NAMESPACE" scale statefulset "$CLUSTER-tici-worker" \
  --replicas="${TICI_WORKER_REPLICAS:-1}"
kubectl -n "$NAMESPACE" wait --for=condition=Ready "pod/$CLUSTER-tici-meta-0" --timeout=900s
kubectl -n "$NAMESPACE" wait --for=condition=Ready "pod/$CLUSTER-tici-worker-0" --timeout=900s

kubectl -n "$TIDB_OPERATOR_NAMESPACE" scale deployment "$TIDB_OPERATOR_DEPLOYMENT" --replicas=1
kubectl -n "$TIDB_OPERATOR_NAMESPACE" rollout status deployment/"$TIDB_OPERATOR_DEPLOYMENT" --timeout=300s
```

7. Add FTS indexes.

```bash
kubectl -n "$NAMESPACE" exec -i "$MYSQL_CLIENT_POD" -- \
  mysql -h "$TIDB_HOST" -P "$TIDB_PORT" -u "$TIDB_USER" "${MYSQL_PASSWORD_ARG[@]}" \
  < "$WORKDIR/fts_create.sql"
```

Post-check:

```bash
kubectl -n "$NAMESPACE" exec "$MYSQL_CLIENT_POD" -- \
  mysql -h "$TIDB_HOST" -P "$TIDB_PORT" -u "$TIDB_USER" "${MYSQL_PASSWORD_ARG[@]}" \
  -e "SELECT (SELECT COUNT(*) FROM tici.tici_index_meta) AS indexes, (SELECT COUNT(*) FROM tici.tici_shard_meta) AS shards, (SELECT COUNT(*) FROM tici.tici_import_jobs WHERE status='finished') AS finished_jobs, (SELECT COUNT(*) FROM tici.tici_import_jobs_task WHERE status='finish') AS finished_tasks;"

kubectl -n "$NAMESPACE" exec "$CDC_POD" -- \
  /cdc cli changefeed query \
  --server="$CDC_SERVER" \
  --changefeed-id="$CHANGEFEED_ID"
```

## Important Notes

- This script is destructive: it drops FTS indexes, drops the `tici` database,
  removes the old changefeed, and deletes the configured TiCI S3 prefix.
- The script prints each compatibility action as `Step N/7` in the execution log.
- To stop TiCI, the script temporarily scales the TiDB Operator deployment to
  `0`, scales TiCI meta/worker StatefulSets to `0`, then scales the operator
  back after TiCI is started again.
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
