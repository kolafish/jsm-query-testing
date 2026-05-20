#!/usr/bin/env bash
set -Eeuo pipefail

MODE=""
ENV_FILE=""
WORKDIR=""
RESUME_FROM="precheck"
CONFIRM_DELETE_S3_PREFIX=""

STAGES=(
  precheck
  generate-fts-ddl
  drop-fts
  stop-tici
  drop-tici-db
  reset-changefeed
  create-changefeed
  start-tici
  recreate-fts
  wait-import
  validate
)

usage() {
  cat <<'EOF'
Usage:
  tici_upgrade_compat.sh --env customer.env --dry-run
  tici_upgrade_compat.sh --env customer.env --execute --confirm-delete-s3-prefix <prefix>
  tici_upgrade_compat.sh --env customer.env --validate-only

Options:
  --env FILE                         Environment file with cluster parameters.
  --dry-run                          Generate evidence and print destructive actions without executing them.
  --execute                          Execute the TiCI compatibility reset.
  --validate-only                    Run read-only validation only.
  --workdir DIR                      Working directory. Default: ./tici-compat-reset-work-<timestamp>.
  --resume-from STAGE                Resume from an internal stage name.
  --confirm-delete-s3-prefix PREFIX  Required for --execute before deleting S3 objects.
  --help                             Show this help.

The script is intentionally guarded. Destructive steps run only in --execute mode.
EOF
}

log() {
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >&2
}

key_step() {
  log "================================================================"
  log "Step $1: $2"
  log "================================================================"
}

die() {
  log "ERROR: $*"
  exit 1
}

print_cmd() {
  printf '  '
  printf '%q ' "$@"
  printf '\n'
}

run_cmd() {
  log "command:"
  print_cmd "$@"
  if [[ "$MODE" == "execute" ]]; then
    "$@"
  else
    log "dry-run: command not executed"
  fi
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --env)
        ENV_FILE="${2:-}"
        shift 2
        ;;
      --dry-run)
        MODE="dry-run"
        shift
        ;;
      --execute)
        MODE="execute"
        shift
        ;;
      --validate-only)
        MODE="validate-only"
        RESUME_FROM="validate"
        shift
        ;;
      --workdir)
        WORKDIR="${2:-}"
        shift 2
        ;;
      --resume-from)
        RESUME_FROM="${2:-}"
        shift 2
        ;;
      --confirm-delete-s3-prefix)
        CONFIRM_DELETE_S3_PREFIX="${2:-}"
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        die "unknown argument: $1"
        ;;
    esac
  done

  [[ -n "$MODE" ]] || die "one of --dry-run, --execute, or --validate-only is required"
  [[ -n "$ENV_FILE" ]] || die "--env FILE is required"
  [[ -f "$ENV_FILE" ]] || die "env file not found: $ENV_FILE"
}

load_env() {
  # The env file is customer-controlled input. Do not source untrusted files.
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a

  KUBECTL_BIN="${KUBECTL_BIN:-kubectl}"
  MYSQL_BIN="${MYSQL_BIN:-mysql}"
  AWS_BIN="${AWS_BIN:-aws}"
  PYTHON_BIN="${PYTHON_BIN:-python3}"

  NAMESPACE="${NAMESPACE:-}"
  CLUSTER="${CLUSTER:-}"
  TIDB_HOST="${TIDB_HOST:-127.0.0.1}"
  TIDB_PORT="${TIDB_PORT:-4000}"
  TIDB_USER="${TIDB_USER:-root}"
  TIDB_PASSWORD="${TIDB_PASSWORD:-}"
  MYSQL_EXTRA_ARGS="${MYSQL_EXTRA_ARGS:-}"

  S3_BUCKET="${S3_BUCKET:-}"
  S3_PREFIX="${S3_PREFIX:-}"
  AWS_REGION="${AWS_REGION:-}"
  CHANGEFEED_ID="${CHANGEFEED_ID:-tici-replication-task}"

  CDC_MODE="${CDC_MODE:-pod}"
  CDC_SERVER="${CDC_SERVER:-http://127.0.0.1:8301}"
  CDC_CLI_CMD="${CDC_CLI_CMD:-cdc cli}"
  CDC_POD_CLI="${CDC_POD_CLI:-/cdc}"

  TICI_META_REPLICAS="${TICI_META_REPLICAS:-1}"
  TICI_WORKER_REPLICAS="${TICI_WORKER_REPLICAS:-1}"
  DATABASES="${DATABASES:-}"
  SMOKE_SQL_FILE="${SMOKE_SQL_FILE:-}"

  [[ -n "$NAMESPACE" ]] || die "NAMESPACE is required"
  [[ -n "$CLUSTER" ]] || die "CLUSTER is required"
  [[ -n "$S3_BUCKET" ]] || die "S3_BUCKET is required"
  [[ -n "$S3_PREFIX" ]] || die "S3_PREFIX is required"
  [[ -n "$AWS_REGION" ]] || die "AWS_REGION is required"
}

init_workdir() {
  if [[ -z "$WORKDIR" ]]; then
    WORKDIR="./tici-compat-reset-work-$(date -u '+%Y%m%d-%H%M%S')"
  fi
  mkdir -p "$WORKDIR"
  CHANGEFEED_CONFIG="$WORKDIR/changefeed-date-none.toml"
  FTS_DROP_SQL="$WORKDIR/fts_drop.sql"
  FTS_CREATE_SQL="$WORKDIR/fts_create.sql"
  LOG_FILE="$WORKDIR/tici_upgrade_compat.log"
  exec > >(tee -a "$LOG_FILE") 2>&1
}

validate_stage_name() {
  local s
  for s in "${STAGES[@]}"; do
    [[ "$s" == "$RESUME_FROM" ]] && return 0
  done
  die "unknown --resume-from stage: $RESUME_FROM"
}

should_run_stage() {
  local stage="$1"
  local seen=0
  local s
  for s in "${STAGES[@]}"; do
    [[ "$s" == "$RESUME_FROM" ]] && seen=1
    [[ "$s" == "$stage" && "$seen" == 1 ]] && return 0
  done
  return 1
}

mysql_base_args() {
  local args=(
    "$MYSQL_BIN"
    -h "$TIDB_HOST"
    -P "$TIDB_PORT"
    -u "$TIDB_USER"
    --batch
    --raw
    --skip-column-names
  )
  if [[ -n "$TIDB_PASSWORD" ]]; then
    args+=("--password=$TIDB_PASSWORD")
  fi
  if [[ -n "$MYSQL_EXTRA_ARGS" ]]; then
    # shellcheck disable=SC2206
    local extra=( $MYSQL_EXTRA_ARGS )
    args+=("${extra[@]}")
  fi
  printf '%s\0' "${args[@]}"
}

mysql_sql() {
  local sql="$1"
  local args=()
  while IFS= read -r -d '' item; do
    args+=("$item")
  done < <(mysql_base_args)
  "${args[@]}" -e "$sql"
}

mysql_file_execute() {
  local file="$1"
  [[ -f "$file" ]] || die "SQL file not found: $file"
  log "SQL file: $file"
  if [[ "$MODE" == "execute" ]]; then
    local args=()
    while IFS= read -r -d '' item; do
      args+=("$item")
    done < <(mysql_base_args)
    "${args[@]}" < "$file"
  else
    log "dry-run: SQL file not executed"
  fi
}

get_ticdc_pod() {
  "$KUBECTL_BIN" -n "$NAMESPACE" get pod \
    -l "app.kubernetes.io/instance=$CLUSTER,app.kubernetes.io/component=ticdc" \
    -o jsonpath='{.items[0].metadata.name}'
}

cdc_exec() {
  if [[ "$CDC_MODE" == "pod" ]]; then
    local pod
    pod="$(get_ticdc_pod)"
    [[ -n "$pod" ]] || die "could not find TiCDC pod"
    "$KUBECTL_BIN" -n "$NAMESPACE" exec "$pod" -- "$CDC_POD_CLI" cli "$@"
  elif [[ "$CDC_MODE" == "local" ]]; then
    # shellcheck disable=SC2206
    local cdc_cmd=( $CDC_CLI_CMD )
    "${cdc_cmd[@]}" "$@"
  else
    die "unsupported CDC_MODE: $CDC_MODE"
  fi
}

run_cdc_cmd() {
  log "cdc command:"
  if [[ "$CDC_MODE" == "pod" ]]; then
    local pod
    pod="$(get_ticdc_pod)"
    printf '  kubectl -n %q exec %q -- %q cli ' "$NAMESPACE" "$pod" "$CDC_POD_CLI"
    printf '%q ' "$@"
    printf '\n'
    if [[ "$MODE" == "execute" ]]; then
      "$KUBECTL_BIN" -n "$NAMESPACE" exec "$pod" -- "$CDC_POD_CLI" cli "$@"
    else
      log "dry-run: cdc command not executed"
    fi
  else
    # shellcheck disable=SC2206
    local cdc_cmd=( $CDC_CLI_CMD )
    print_cmd "${cdc_cmd[@]}" "$@"
    if [[ "$MODE" == "execute" ]]; then
      "${cdc_cmd[@]}" "$@"
    else
      log "dry-run: cdc command not executed"
    fi
  fi
}

write_changefeed_config() {
  cat > "$CHANGEFEED_CONFIG" <<'EOF'
[sink]
protocol = "canal-json"
date-separator = "none"
enable-partition-separator = true
EOF
  log "wrote $CHANGEFEED_CONFIG"
}

sink_uri() {
  printf 's3://%s/%s/cdc?force-path-style=false&protocol=canal-json&enable-tidb-extension=true&output-row-key=true&use-table-id-as-path=true&date-separator=none' \
    "$S3_BUCKET" "$S3_PREFIX"
}

precheck() {
  log "Preparation: precheck and evidence capture"
  need_cmd "$KUBECTL_BIN"
  need_cmd "$MYSQL_BIN"
  need_cmd "$AWS_BIN"
  need_cmd "$PYTHON_BIN"

  "$KUBECTL_BIN" -n "$NAMESPACE" get tidbcluster "$CLUSTER" -o yaml > "$WORKDIR/pre_tidbcluster.yaml"
  "$KUBECTL_BIN" -n "$NAMESPACE" get pods -o wide > "$WORKDIR/pre_pods.txt"

  mysql_sql "SELECT VERSION();" > "$WORKDIR/pre_tidb_version.txt"

  log "saving S3 prefix summary"
  "$AWS_BIN" s3 ls "s3://$S3_BUCKET/$S3_PREFIX/" \
    --recursive \
    --summarize \
    --region "$AWS_REGION" > "$WORKDIR/pre_s3_prefix_summary.txt" || true

  log "saving current changefeed query if present"
  cdc_exec changefeed query "--server=$CDC_SERVER" "--changefeed-id=$CHANGEFEED_ID" \
    > "$WORKDIR/pre_changefeed_query.json" 2>&1 || true
}

generate_fts_ddl() {
  log "Preparation: generate FTS drop/create SQL"
  export MYSQL_BIN TIDB_HOST TIDB_PORT TIDB_USER TIDB_PASSWORD MYSQL_EXTRA_ARGS DATABASES
  export FTS_DROP_SQL FTS_CREATE_SQL
  "$PYTHON_BIN" - <<'PY'
import os
import shlex
import subprocess
import sys

mysql_bin = os.environ["MYSQL_BIN"]
host = os.environ["TIDB_HOST"]
port = os.environ["TIDB_PORT"]
user = os.environ["TIDB_USER"]
password = os.environ.get("TIDB_PASSWORD", "")
extra = os.environ.get("MYSQL_EXTRA_ARGS", "")
databases = [x.strip() for x in os.environ.get("DATABASES", "").split(",") if x.strip()]
drop_path = os.environ["FTS_DROP_SQL"]
create_path = os.environ["FTS_CREATE_SQL"]

def qident(value):
    return "`" + value.replace("`", "``") + "`"

def mysql(sql):
    cmd = [
        mysql_bin,
        "-h", host,
        "-P", str(port),
        "-u", user,
        "--batch",
        "--raw",
        "--skip-column-names",
        "-e", sql,
    ]
    if password:
        cmd.append("--password=" + password)
    if extra:
        cmd[1:1] = shlex.split(extra)
    return subprocess.check_output(cmd, text=True)

if databases:
    db_list = ",".join("'" + db.replace("'", "''") + "'" for db in databases)
    table_sql = f"""
      SELECT table_schema, table_name
      FROM information_schema.tables
      WHERE table_type='BASE TABLE' AND table_schema IN ({db_list})
      ORDER BY table_schema, table_name
    """
else:
    table_sql = """
      SELECT table_schema, table_name
      FROM information_schema.tables
      WHERE table_type='BASE TABLE'
        AND table_schema NOT IN (
          'INFORMATION_SCHEMA','PERFORMANCE_SCHEMA','METRICS_SCHEMA',
          'INSPECTION_SCHEMA','mysql','sys','tici'
        )
      ORDER BY table_schema, table_name
    """

tables = []
for line in mysql(table_sql).splitlines():
    if not line.strip():
        continue
    parts = line.split("\t")
    if len(parts) >= 2:
        tables.append((parts[0], parts[1]))

drops = []
creates = []
index_rows = []

for db, table in tables:
    full_table = f"{qident(db)}.{qident(table)}"
    try:
        show_index = mysql(f"SHOW INDEX FROM {full_table}")
    except subprocess.CalledProcessError as exc:
        print(f"warn: SHOW INDEX failed for {db}.{table}: {exc}", file=sys.stderr)
        continue

    fts_names = []
    for line in show_index.splitlines():
        parts = line.split("\t")
        if len(parts) > 10 and parts[10].upper() == "FULLTEXT":
            name = parts[2]
            col = parts[4] if len(parts) > 4 else ""
            index_rows.append((db, table, name, col))
            if name not in fts_names:
                fts_names.append(name)

    if not fts_names:
        continue

    for name in fts_names:
        drops.append(f"ALTER TABLE {full_table} DROP INDEX {qident(name)};")

    try:
        show_create = mysql(f"SHOW CREATE TABLE {full_table}")
    except subprocess.CalledProcessError as exc:
        print(f"warn: SHOW CREATE TABLE failed for {db}.{table}: {exc}", file=sys.stderr)
        continue

    create_stmt = show_create.split("\t", 1)[1] if "\t" in show_create else show_create
    for raw_line in create_stmt.splitlines():
        line = raw_line.strip()
        upper = line.upper()
        if not (upper.startswith("FULLTEXT KEY ") or upper.startswith("FULLTEXT INDEX ")):
            continue
        if line.endswith(","):
            line = line[:-1]
        creates.append(f"ALTER TABLE {full_table} ADD {line};")

with open(drop_path, "w", encoding="utf-8") as f:
    f.write("\n".join(drops))
    if drops:
        f.write("\n")

with open(create_path, "w", encoding="utf-8") as f:
    f.write("\n".join(creates))
    if creates:
        f.write("\n")

with open(os.path.join(os.path.dirname(drop_path), "pre_fulltext_indexes.tsv"), "w", encoding="utf-8") as f:
    for row in index_rows:
        f.write("\t".join(row) + "\n")

print(f"tables_scanned={len(tables)}")
print(f"fulltext_indexes={len(set((db, table, name) for db, table, name, _ in index_rows))}")
print(f"drop_sql={drop_path}")
print(f"create_sql={create_path}")
PY
}

drop_fts() {
  key_step "1/7" "Drop FTS indexes."
  [[ -s "$FTS_DROP_SQL" ]] || die "empty or missing $FTS_DROP_SQL; run generate-fts-ddl first"
  mysql_file_execute "$FTS_DROP_SQL"
}

wait_sts_replicas() {
  local sts="$1"
  local desired="$2"
  local timeout="${3:-600}"
  [[ "$MODE" == "execute" ]] || return 0
  local start now replicas ready
  start="$(date +%s)"
  while true; do
    replicas="$("$KUBECTL_BIN" -n "$NAMESPACE" get sts "$sts" -o jsonpath='{.status.replicas}' 2>/dev/null || true)"
    ready="$("$KUBECTL_BIN" -n "$NAMESPACE" get sts "$sts" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || true)"
    replicas="${replicas:-0}"
    ready="${ready:-0}"
    log "$sts replicas=$replicas ready=$ready target=$desired"
    if [[ "$replicas" == "$desired" && "$ready" == "$desired" ]]; then
      return 0
    fi
    now="$(date +%s)"
    (( now - start < timeout )) || die "timeout waiting for $sts replicas=$desired"
    sleep 10
  done
}

stop_tici() {
  key_step "2/7" "Stop TiCI service."
  run_cmd "$KUBECTL_BIN" -n "$NAMESPACE" patch tidbcluster "$CLUSTER" --type merge \
    -p '{"spec":{"tici":{"changefeed":{"enable":false},"meta":{"replicas":0},"worker":{"replicas":0}}}}'
  wait_sts_replicas "$CLUSTER-tici-meta" 0 600
  wait_sts_replicas "$CLUSTER-tici-worker" 0 600
}

drop_tici_db() {
  key_step "3/7" "Drop the tici database from TiDB."
  if [[ "$MODE" == "execute" ]]; then
    mysql_sql "DROP DATABASE IF EXISTS tici;"
  else
    log "dry-run SQL: DROP DATABASE IF EXISTS tici;"
  fi
}

guard_s3_prefix_delete() {
  [[ -n "$S3_PREFIX" ]] || die "S3_PREFIX cannot be empty"
  case "$S3_PREFIX" in
    "/"|"."|"*"|"/*"|".*" )
      die "unsafe S3_PREFIX: $S3_PREFIX"
      ;;
  esac
  if [[ "$MODE" == "execute" && "$CONFIRM_DELETE_S3_PREFIX" != "$S3_PREFIX" ]]; then
    die "--confirm-delete-s3-prefix must exactly match S3_PREFIX ($S3_PREFIX)"
  fi
}

reset_changefeed() {
  key_step "4/7" "Remove old changefeed and remove S3 data under the TiCI S3 prefix."
  log "querying existing changefeed"
  local changefeed_exists=0
  if cdc_exec changefeed query "--server=$CDC_SERVER" "--changefeed-id=$CHANGEFEED_ID" \
    > "$WORKDIR/changefeed_before_reset.json" 2>&1; then
    changefeed_exists=1
  else
    log "changefeed $CHANGEFEED_ID was not queryable; remove step will be skipped"
  fi

  if [[ "$changefeed_exists" == "1" ]]; then
    run_cdc_cmd changefeed remove "--server=$CDC_SERVER" "--changefeed-id=$CHANGEFEED_ID" --force
  else
    log "skip changefeed remove because the changefeed was not found"
  fi

  guard_s3_prefix_delete
  log "S3 prefix to delete: s3://$S3_BUCKET/$S3_PREFIX/"
  run_cmd "$AWS_BIN" s3 rm "s3://$S3_BUCKET/$S3_PREFIX/" \
    --recursive \
    --region "$AWS_REGION"
}

create_changefeed() {
  key_step "5/7" "Add a new changefeed without date separator."
  write_changefeed_config
  local uri
  uri="$(sink_uri)"
  if [[ "$CDC_MODE" == "pod" ]]; then
    local pod remote_config
    pod="$(get_ticdc_pod)"
    remote_config="/tmp/changefeed-date-none.toml"
    run_cmd "$KUBECTL_BIN" -n "$NAMESPACE" cp "$CHANGEFEED_CONFIG" "$pod:$remote_config"
    run_cdc_cmd changefeed create "--server=$CDC_SERVER" "--changefeed-id=$CHANGEFEED_ID" "--sink-uri=$uri" "--config=$remote_config"
  else
    run_cdc_cmd changefeed create "--server=$CDC_SERVER" "--changefeed-id=$CHANGEFEED_ID" "--sink-uri=$uri" "--config=$CHANGEFEED_CONFIG"
  fi
}

start_tici() {
  key_step "6/7" "Start TiCI service."
  local uri
  uri="$(sink_uri)"
  export TICI_META_REPLICAS TICI_WORKER_REPLICAS CHANGEFEED_ID uri
  local patch_file="$WORKDIR/start_tici_patch.json"
  "$PYTHON_BIN" - <<'PY' > "$patch_file"
import json
import os

print(json.dumps({
  "spec": {
    "tici": {
      "changefeed": {
        "enable": True,
        "changefeedID": os.environ["CHANGEFEED_ID"],
        "sinkURI": os.environ["uri"],
      },
      "meta": {"replicas": int(os.environ["TICI_META_REPLICAS"])},
      "worker": {"replicas": int(os.environ["TICI_WORKER_REPLICAS"])},
    }
  }
}))
PY
  run_cmd "$KUBECTL_BIN" -n "$NAMESPACE" patch tidbcluster "$CLUSTER" --type merge --patch-file "$patch_file"
  wait_sts_replicas "$CLUSTER-tici-meta" "$TICI_META_REPLICAS" 900
  wait_sts_replicas "$CLUSTER-tici-worker" "$TICI_WORKER_REPLICAS" 900
}

recreate_fts() {
  key_step "7/7" "Add FTS indexes."
  [[ -s "$FTS_CREATE_SQL" ]] || die "empty or missing $FTS_CREATE_SQL; run generate-fts-ddl first"
  mysql_file_execute "$FTS_CREATE_SQL"
}

wait_import() {
  log "Post-step check: wait for TiCI import jobs"
  [[ "$MODE" == "execute" ]] || {
    log "dry-run: import wait skipped"
    return 0
  }
  local timeout="${IMPORT_WAIT_TIMEOUT_SECONDS:-21600}"
  local start now line unfinished
  start="$(date +%s)"
  while true; do
    line="$(mysql_sql "SELECT CONCAT(SUM(status='finished'), '/', COUNT(*), ' jobs, ', (SELECT CONCAT(SUM(status='finish'), '/', COUNT(*)) FROM tici.tici_import_jobs_task), ' tasks') FROM tici.tici_import_jobs;" 2>/dev/null || true)"
    log "import progress: ${line:-not available yet}"
    unfinished="$(mysql_sql "SELECT (SELECT COUNT(*) FROM tici.tici_import_jobs WHERE status <> 'finished') + (SELECT COUNT(*) FROM tici.tici_import_jobs_task WHERE status <> 'finish');" 2>/dev/null || echo 1)"
    if [[ "$unfinished" == "0" ]]; then
      return 0
    fi
    now="$(date +%s)"
    (( now - start < timeout )) || die "timeout waiting for TiCI import jobs"
    sleep 30
  done
}

validate_fulltext_count() {
  export MYSQL_BIN TIDB_HOST TIDB_PORT TIDB_USER TIDB_PASSWORD MYSQL_EXTRA_ARGS DATABASES WORKDIR
  "$PYTHON_BIN" - <<'PY'
import os
import shlex
import subprocess

mysql_bin = os.environ["MYSQL_BIN"]
host = os.environ["TIDB_HOST"]
port = os.environ["TIDB_PORT"]
user = os.environ["TIDB_USER"]
password = os.environ.get("TIDB_PASSWORD", "")
extra = os.environ.get("MYSQL_EXTRA_ARGS", "")
databases = [x.strip() for x in os.environ.get("DATABASES", "").split(",") if x.strip()]

def qident(value):
    return "`" + value.replace("`", "``") + "`"

def mysql(sql):
    cmd = [
        mysql_bin, "-h", host, "-P", str(port), "-u", user,
        "--batch", "--raw", "--skip-column-names", "-e", sql,
    ]
    if password:
        cmd.append("--password=" + password)
    if extra:
        cmd[1:1] = shlex.split(extra)
    return subprocess.check_output(cmd, text=True)

if databases:
    db_list = ",".join("'" + db.replace("'", "''") + "'" for db in databases)
    table_sql = f"SELECT table_schema, table_name FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema IN ({db_list}) ORDER BY table_schema, table_name"
else:
    table_sql = """
      SELECT table_schema, table_name
      FROM information_schema.tables
      WHERE table_type='BASE TABLE'
        AND table_schema NOT IN (
          'INFORMATION_SCHEMA','PERFORMANCE_SCHEMA','METRICS_SCHEMA',
          'INSPECTION_SCHEMA','mysql','sys','tici'
        )
      ORDER BY table_schema, table_name
    """

count = 0
lines = []
for row in mysql(table_sql).splitlines():
    if not row.strip():
        continue
    db, table = row.split("\t")[:2]
    try:
        show_index = mysql(f"SHOW INDEX FROM {qident(db)}.{qident(table)}")
    except subprocess.CalledProcessError:
        continue
    names = set()
    for line in show_index.splitlines():
        parts = line.split("\t")
        if len(parts) > 10 and parts[10].upper() == "FULLTEXT":
            names.add(parts[2])
    if names:
        count += len(names)
        lines.append(f"{db}\t{table}\t{len(names)}")

print(f"fulltext_index_count={count}")
for line in lines:
    print(line)
PY
}

validate() {
  log "Post-step check: validate TiCI compatibility reset"
  "$KUBECTL_BIN" -n "$NAMESPACE" get tidbcluster "$CLUSTER" -o yaml > "$WORKDIR/post_tidbcluster.yaml"
  "$KUBECTL_BIN" -n "$NAMESPACE" get pods -o wide > "$WORKDIR/post_pods.txt"

  log "FULLTEXT indexes:"
  validate_fulltext_count | tee "$WORKDIR/post_fulltext_counts.tsv"

  log "TiCI metadata:"
  mysql_sql "SELECT (SELECT COUNT(*) FROM tici.tici_index_meta) AS indexes, (SELECT COUNT(*) FROM tici.tici_shard_meta) AS shards, (SELECT COUNT(*) FROM tici.tici_import_jobs WHERE status='finished') AS finished_jobs, (SELECT COUNT(*) FROM tici.tici_import_jobs_task WHERE status='finish') AS finished_tasks;" \
    | tee "$WORKDIR/post_tici_meta_summary.tsv" || true

  log "changefeed query:"
  if cdc_exec changefeed query "--server=$CDC_SERVER" "--changefeed-id=$CHANGEFEED_ID" \
    | tee "$WORKDIR/post_changefeed_query.json"; then
    "$PYTHON_BIN" - "$WORKDIR/post_changefeed_query.json" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

try:
    data = json.loads(text)
except json.JSONDecodeError:
    # Some cdc cli builds wrap the JSON with log text. Keep validation readable
    # instead of silently accepting an unknown result.
    raise SystemExit(f"changefeed query output is not JSON: {path}")

state = data.get("state")
date_separator = data.get("config", {}).get("sink", {}).get("date_separator")
if state not in ("normal", "stopped"):
    raise SystemExit(f"unexpected changefeed state: {state}")
if date_separator != "none":
    raise SystemExit(f"unexpected changefeed date_separator: {date_separator}")
print(f"changefeed_validation=ok state={state} date_separator={date_separator}")
PY
  else
    die "changefeed query failed during validation"
  fi

  log "S3 path sample:"
  "$AWS_BIN" s3api list-objects-v2 \
    --bucket "$S3_BUCKET" \
    --prefix "$S3_PREFIX/cdc/" \
    --max-items 20 \
    --region "$AWS_REGION" \
    --query 'Contents[].{Key:Key,Size:Size}' \
    --output table \
    | tee "$WORKDIR/post_s3_path_sample.txt" || true

  if [[ -n "$SMOKE_SQL_FILE" ]]; then
    [[ -f "$SMOKE_SQL_FILE" ]] || die "SMOKE_SQL_FILE not found: $SMOKE_SQL_FILE"
    log "running smoke SQL: $SMOKE_SQL_FILE"
    local args=()
    while IFS= read -r -d '' item; do
      args+=("$item")
    done < <(mysql_base_args)
    "${args[@]}" < "$SMOKE_SQL_FILE" | tee "$WORKDIR/post_smoke_sql.out"
  else
    log "SMOKE_SQL_FILE not set; skipping query smoke"
  fi
}

main() {
  parse_args "$@"
  load_env
  init_workdir
  validate_stage_name

  log "mode=$MODE workdir=$WORKDIR resume_from=$RESUME_FROM"

  if [[ "$MODE" == "validate-only" ]]; then
    validate
    exit 0
  fi

  local stage
  for stage in "${STAGES[@]}"; do
    if should_run_stage "$stage"; then
      case "$stage" in
        precheck) precheck ;;
        generate-fts-ddl) generate_fts_ddl ;;
        drop-fts) drop_fts ;;
        stop-tici) stop_tici ;;
        drop-tici-db) drop_tici_db ;;
        reset-changefeed) reset_changefeed ;;
        create-changefeed) create_changefeed ;;
        start-tici) start_tici ;;
        recreate-fts) recreate_fts ;;
        wait-import) wait_import ;;
        validate) validate ;;
        *) die "internal error: unknown stage $stage" ;;
      esac
    else
      log "skip stage before resume point: $stage"
    fi
  done

  log "finished"
}

main "$@"
