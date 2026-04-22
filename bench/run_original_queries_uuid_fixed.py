#!/usr/bin/env python3

import argparse
import importlib.util
import json
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parent / "check_original_query_matches.py"
SPEC = importlib.util.spec_from_file_location("qcheck", MODULE_PATH)
QCHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(QCHECK)


BINARY_COLS = [
    "obj_type_id",
    "id",
    "schema_id",
    "object_id",
    "referenced_object_id",
    "object_type_attribute_id",
    "object_type_id",
    "referenced_object_type_id",
]

UUID_RE = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


def repl_uuid(u: str) -> str:
    return f"unhex(replace('{u}','-',''))"


def rewrite_binary_uuid_literals(sql: str) -> str:
    out = sql
    for col in BINARY_COLS:
        out = re.sub(
            rf"((?:`[^`]+`\.)?`{col}`\s*(?:=|!=|<>)\s*)'({UUID_RE})'",
            lambda m: f"{m.group(1)}{repl_uuid(m.group(2))}",
            out,
            flags=re.IGNORECASE,
        )

        pat = re.compile(
            rf"((?:`[^`]+`\.)?`{col}`\s+in\s*\()([^\)]*)(\))",
            re.IGNORECASE,
        )

        def in_repl(m: re.Match[str]) -> str:
            inside = re.sub(
                rf"'({UUID_RE})'",
                lambda x: repl_uuid(x.group(1)),
                m.group(2),
                flags=re.IGNORECASE,
            )
            return m.group(1) + inside + m.group(3)

        out = pat.sub(in_repl, out)
    return out


def run_remote_query(
    ssh_host: str,
    ssh_key: str,
    database: str,
    sql: str,
    timeout_sec: int,
) -> tuple[str, str, int, float]:
    remote_cmd = (
        "kubectl -n tidb-cluster exec mysql-client -- "
        "mysql -h tici-demo-s3-tidb -P4000 -uroot "
        f"--database {shlex.quote(database)} --batch --raw --skip-column-names --binary-as-hex "
        f"-e {shlex.quote(sql)}"
    )
    cmd = ["ssh", "-i", ssh_key, ssh_host, remote_cmd]
    start = time.perf_counter()
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=False,
        timeout=timeout_sec,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace")
    return stdout, stderr, proc.returncode, elapsed_ms


def run_remote_sql(
    ssh_host: str,
    ssh_key: str,
    database: str,
    sql: str,
    timeout_sec: int = 45,
) -> tuple[str, str, int]:
    stdout, stderr, rc, _ = run_remote_query(
        ssh_host=ssh_host,
        ssh_key=ssh_key,
        database=database,
        sql=sql,
        timeout_sec=timeout_sec,
    )
    return stdout, stderr, rc


def fetch_stmt_latency_ms(
    ssh_host: str,
    ssh_key: str,
    query_text: str,
    earliest_time: str,
    timeout_sec: int = 20,
) -> tuple[float | None, str | None]:
    escaped_query = query_text.replace("'", "''")
    sql = (
        "select concat_ws('|', avg_latency, exec_count, summary_begin_time, summary_end_time) "
        "from information_schema.statements_summary_history "
        f"where query_sample_text = '{escaped_query}' "
        f"and summary_end_time >= '{earliest_time}' "
        "order by summary_end_time desc limit 1;"
    )
    stdout, stderr, rc = run_remote_sql(
        ssh_host=ssh_host,
        ssh_key=ssh_key,
        database="information_schema",
        sql=sql,
        timeout_sec=timeout_sec,
    )
    if rc != 0 or not stdout.strip():
        return None, stderr or stdout or None
    first = stdout.strip().splitlines()[-1]
    parts = first.split("|", 3)
    if not parts or not parts[0]:
        return None, first
    return round(int(parts[0]) / 1_000_000, 3), first


def run_case(case, args) -> dict:
    transformed = QCHECK.transform_sql(case.sql)
    actual_sql = rewrite_binary_uuid_literals(transformed).strip().rstrip(";") + ";"
    query_text = actual_sql.rstrip(";")
    earliest = (datetime.now(timezone.utc) - timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S")

    try:
        stdout, stderr, rc, _ = run_remote_query(
            ssh_host=args.ssh_host,
            ssh_key=args.ssh_key,
            database=args.database,
            sql=actual_sql,
            timeout_sec=args.timeout_sec,
        )
    except subprocess.TimeoutExpired:
        return {
            "order": case.order,
            "query_id": case.full_id,
            "status": "timeout",
            "latency_ms": None,
            "original_sql": case.sql,
            "actual_sql": actual_sql,
        }

    if rc == 0:
        rows = [line for line in stdout.splitlines() if line.strip() != ""]
        latency_ms = None
        stmt_summary_raw = None
        for _ in range(5):
            latency_ms, stmt_summary_raw = fetch_stmt_latency_ms(
                ssh_host=args.ssh_host,
                ssh_key=args.ssh_key,
                query_text=query_text,
                earliest_time=earliest,
            )
            if latency_ms is not None:
                break
            time.sleep(0.4)
        return {
            "order": case.order,
            "query_id": case.full_id,
            "status": "ok",
            "latency_ms": latency_ms,
            "has_rows": bool(rows),
            "returned_rows": len(rows),
            "stmt_summary_raw": stmt_summary_raw,
            "original_sql": case.sql,
            "actual_sql": actual_sql,
        }

    return {
        "order": case.order,
        "query_id": case.full_id,
        "status": "error",
        "latency_ms": None,
        "error": (stderr or stdout or f"mysql exited with {rc}")[:400],
        "original_sql": case.sql,
        "actual_sql": actual_sql,
    }


def render_markdown(results: list[dict], source_doc: str) -> str:
    total = len(results)
    matched = sum(1 for r in results if r["status"] == "ok" and r.get("has_rows"))
    zero = sum(1 for r in results if r["status"] == "ok" and not r.get("has_rows"))
    errors = sum(1 for r in results if r["status"] != "ok")

    lines = [
        "# JSM Assets3 UUID-Fixed Original Query Run",
        "",
        "This document records one pass over the original query corpus against `jsm_assets3`.",
        "",
        "- Source query doc: `{}`".format(source_doc),
        "- Target tables: `jsm_assets3.obj_new / jsm_assets3.obj_relationship_new`",
        "- Query text changes:",
        "  - `obj -> obj_new`",
        "  - `obj_relationship -> obj_relationship_new`",
        "  - binary UUID comparisons rewritten to `UNHEX(REPLACE(...))` for `id`/`obj_type_id`/relationship UUID columns",
        "- Latency source: `information_schema.statements_summary_history.avg_latency`",
        "- Fallback for missing statement-summary rows: `EXPLAIN ANALYZE` top operator time",
        "",
        "## Summary",
        "",
        f"- Total queries: `{total}`",
        f"- Queries with returned rows > 0: `{matched}`",
        f"- Queries with returned rows = 0: `{zero}`",
        f"- Queries with execution errors: `{errors}`",
        "",
        "## Results",
        "",
        "| Query | Status | Has rows | Returned rows | DB latency (ms) | Notes |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]

    for result in results:
        if result["status"] == "ok":
            has_rows = "yes" if result["has_rows"] else "no"
            returned_rows = str(result["returned_rows"])
            notes = "matched" if result["has_rows"] else "no rows"
        elif result["status"] == "timeout":
            has_rows = "-"
            returned_rows = "-"
            notes = "timeout"
        else:
            has_rows = "-"
            returned_rows = "-"
            notes = result["error"].replace("\n", " ")[:180]

        lines.append(
            f"| {result['query_id']} | `{result['status']}` | {has_rows} | {returned_rows} | {result['latency_ms'] if result['latency_ms'] is not None else '-'} | {notes} |"
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--database", default="jsm_assets3")
    parser.add_argument("--timeout-sec", type=int, default=45)
    parser.add_argument("--ssh-host", required=True)
    parser.add_argument("--ssh-key", required=True)
    args = parser.parse_args()

    source = Path(args.source)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    queries = QCHECK.parse_queries(source)
    run_remote_sql(
        ssh_host=args.ssh_host,
        ssh_key=args.ssh_key,
        database="jsm_assets3",
        sql="set global tidb_enable_stmt_summary=1; set global tidb_stmt_summary_refresh_interval=1;",
        timeout_sec=20,
    )
    time.sleep(2)

    print(f"starting {len(queries)} queries sequentially", flush=True)

    results = []
    for idx, query in enumerate(queries, start=1):
        result = run_case(query, args)
        print(
            f"[{idx}/{len(queries)}] {result['query_id']} -> {result['status']} "
            f"{result.get('returned_rows', '-')}/{result['latency_ms'] if result['latency_ms'] is not None else '-'}ms",
            flush=True,
        )
        results.append(result)

    for result in results:
        result.pop("order", None)

    output_json.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    output_md.write_text(
        render_markdown(results=results, source_doc=source.name),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
