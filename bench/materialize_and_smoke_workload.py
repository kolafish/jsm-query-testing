#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import mysql.connector


@dataclass
class QueryTemplate:
    order: int
    group: str
    query_no: int
    exec_count: int
    source_avg_latency_ms: float
    digest: str
    sql: str

    @property
    def query_id(self) -> str:
        safe_group = re.sub(r"[^a-zA-Z0-9]+", "_", self.group.lower()).strip("_")
        return f"{safe_group}_q{self.query_no}"


def parse_workload(path: Path) -> list[QueryTemplate]:
    group = ""
    current: dict | None = None
    queries: list[QueryTemplate] = []
    digest = ""

    for line in path.read_text(errors="replace").splitlines():
        group_match = re.match(r"-- (.+)$", line)
        if group_match:
            text = group_match.group(1).strip()
            if text and set(text) != {"="} and not text.startswith(("Query ", "Digest:", "Cluster:", "Extracted")):
                group = text

        query_match = re.match(
            r"-- Query (\d+): exec_count=([0-9,]+), avg_latency=([0-9.]+)ms",
            line,
        )
        if query_match:
            current = {
                "group": group,
                "query_no": int(query_match.group(1)),
                "exec_count": int(query_match.group(2).replace(",", "")),
                "source_avg_latency_ms": float(query_match.group(3)),
                "sql": "",
            }
            digest = ""
            continue

        digest_match = re.match(r"-- Digest: ([0-9a-f]+)", line)
        if digest_match and current is not None:
            digest = digest_match.group(1)
            continue

        if current is not None and line.strip() and not line.startswith("--"):
            current["sql"] += line.strip() + " "
            queries.append(
                QueryTemplate(
                    order=len(queries),
                    group=current["group"],
                    query_no=current["query_no"],
                    exec_count=current["exec_count"],
                    source_avg_latency_ms=current["source_avg_latency_ms"],
                    digest=digest,
                    sql=" ".join(current["sql"].split()),
                )
            )
            current = None

    return queries


def sql_quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def hex_lit(value: str | None) -> str:
    if not value:
        return "0x00000000000000000000000000000000"
    return "0x" + value.lower()


def first(row: dict, key: str, default=None):
    value = row.get(key)
    return default if value is None else value


def clean_fts_phrase(value: str) -> str:
    return value.replace("\u2063", "").replace("\U0010ffff", "").strip()


def fetch_one(cursor, sql: str) -> dict:
    cursor.execute(sql)
    row = cursor.fetchone()
    return row or {}


def fetch_list(cursor, sql: str, column: str) -> list:
    cursor.execute(sql)
    return [row[column] for row in cursor.fetchall() if row.get(column) is not None]


def build_context(conn, database: str) -> dict:
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"USE `{database}`")

    obj = fetch_one(
        cursor,
        """
        SELECT
          workspace_id,
          partition_id,
          LOWER(HEX(id)) AS id_hex,
          sequential_id,
          LOWER(HEX(obj_type_id)) AS obj_type_id_hex,
          LOWER(HEX(schema_id)) AS schema_id_hex,
          label,
          label_lower,
          numeric_value_1,
          numeric_value_2,
          numeric_value_3,
          numeric_value_5
        FROM obj_new
        WHERE label IS NOT NULL
        LIMIT 1
        """,
    )
    if not obj:
        raise RuntimeError("cannot sample obj_new")

    workspace = obj["workspace_id"]
    fts_text_value_5 = fetch_one(
        cursor,
        f"""
        SELECT text_value_5, LOWER(HEX(obj_type_id)) AS obj_type_id_hex
        FROM obj_new
        WHERE workspace_id = {sql_quote(workspace)}
          AND text_value_5 IS NOT NULL
          AND text_value_5 != ''
          AND text_value_5 LIKE '%www.%'
        LIMIT 1
        """,
    )
    obj_type_ids = fetch_list(
        cursor,
        f"""
        SELECT DISTINCT LOWER(HEX(obj_type_id)) AS value
        FROM obj_new
        WHERE workspace_id = {sql_quote(workspace)}
        LIMIT 5
        """,
        "value",
    )
    if not obj_type_ids:
        obj_type_ids = [obj["obj_type_id_hex"]]
    obj_type_ids = list(dict.fromkeys([obj["obj_type_id_hex"], first(fts_text_value_5, "obj_type_id_hex", None), *obj_type_ids]))
    obj_type_ids = [value for value in obj_type_ids if value]

    rel_new = fetch_one(
        cursor,
        """
        SELECT
          LOWER(HEX(id)) AS id_hex,
          workspace_id,
          partition_id,
          LOWER(HEX(object_id)) AS object_id_hex,
          LOWER(HEX(referenced_object_id)) AS referenced_object_id_hex,
          LOWER(HEX(object_type_attribute_id)) AS object_type_attribute_id_hex,
          LOWER(HEX(object_type_id)) AS object_type_id_hex,
          LOWER(HEX(referenced_object_type_id)) AS referenced_object_type_id_hex
        FROM obj_relationship_new
        LIMIT 1
        """,
    )
    rel_orig = fetch_one(
        cursor,
        """
        SELECT
          LOWER(HEX(id)) AS id_hex,
          LOWER(HEX(object_id)) AS object_id_hex
        FROM obj_relationship
        LIMIT 1
        """,
    )
    obj_type = fetch_one(
        cursor,
        f"""
        SELECT
          LOWER(HEX(id)) AS id_hex,
          sequential_id,
          LOWER(HEX(icon_id)) AS icon_id_hex,
          LOWER(HEX(object_schema_id)) AS object_schema_id_hex
        FROM obj_type
        WHERE workspace_id = {sql_quote(workspace)}
        LIMIT 1
        """,
    )
    obj_type_attr = fetch_one(
        cursor,
        f"""
        SELECT
          LOWER(HEX(id)) AS id_hex,
          sequential_id,
          LOWER(HEX(object_type_id)) AS object_type_id_hex,
          LOWER(HEX(reference_type_id)) AS reference_type_id_hex
        FROM obj_type_attr
        WHERE workspace_id = {sql_quote(workspace)}
        LIMIT 1
        """,
    )
    obj_schema = fetch_one(
        cursor,
        f"""
        SELECT LOWER(HEX(id)) AS id_hex, sequential_id
        FROM obj_schema
        WHERE workspace_id = {sql_quote(workspace)}
        LIMIT 1
        """,
    )
    icon = fetch_one(
        cursor,
        f"""
        SELECT LOWER(HEX(id)) AS id_hex
        FROM icon
        WHERE workspace_id = {sql_quote(workspace)}
        LIMIT 1
        """,
    )
    ref_type = fetch_one(
        cursor,
        f"""
        SELECT LOWER(HEX(id)) AS id_hex
        FROM ref_type
        WHERE workspace_id = {sql_quote(workspace)}
        LIMIT 1
        """,
    )
    mapping = fetch_one(
        cursor,
        f"""
        SELECT
          LOWER(HEX(object_type_attribute_id)) AS object_type_attribute_id_hex,
          LOWER(HEX(object_type_id)) AS object_type_id_hex
        FROM ota_obj_column_mapping
        WHERE workspace_id = {sql_quote(workspace)}
        LIMIT 1
        """,
    )
    issue_conn = fetch_one(
        cursor,
        """
        SELECT LOWER(HEX(object_id)) AS object_id_hex
        FROM object_issue_connection
        LIMIT 1
        """,
    )
    history = fetch_one(
        cursor,
        f"""
        SELECT LOWER(HEX(object_id)) AS object_id_hex
        FROM obj_history
        WHERE workspace_id = {sql_quote(workspace)}
        LIMIT 1
        """,
    )
    attachment = fetch_one(
        cursor,
        f"""
        SELECT LOWER(HEX(object_id)) AS object_id_hex
        FROM obj_attachment
        WHERE workspace_id = {sql_quote(workspace)}
        LIMIT 1
        """,
    )

    label = str(obj["label"])
    label_lower = str(obj.get("label_lower") or label.lower())
    label_like_token = label_lower[: max(3, min(12, len(label_lower)))]

    return {
        "workspace_id": workspace,
        "partition_id": int(obj["partition_id"]),
        "obj_id": obj["id_hex"],
        "obj_sequential_id": int(obj["sequential_id"]),
        "obj_type_id": first(obj_type, "id_hex", obj["obj_type_id_hex"]),
        "obj_type_ids": obj_type_ids,
        "schema_id": first(obj_schema, "id_hex", obj.get("schema_id_hex")),
        "schema_seq": int(first(obj_schema, "sequential_id", 1)),
        "obj_type_seq": int(first(obj_type, "sequential_id", 1)),
        "obj_type_attr_id": first(obj_type_attr, "id_hex", first(mapping, "object_type_attribute_id_hex", None)),
        "obj_type_attr_seq": int(first(obj_type_attr, "sequential_id", 1)),
        "icon_id": first(icon, "id_hex", first(obj_type, "icon_id_hex", None)),
        "ref_type_id": first(ref_type, "id_hex", first(obj_type_attr, "reference_type_id_hex", None)),
        "rel_new_id": first(rel_new, "id_hex", None),
        "rel_orig_id": first(rel_orig, "id_hex", first(rel_new, "id_hex", None)),
        "rel_object_id": first(rel_new, "object_id_hex", first(rel_orig, "object_id_hex", obj["id_hex"])),
        "rel_ref_id": first(rel_new, "referenced_object_id_hex", obj["id_hex"]),
        "rel_ota_id": first(rel_new, "object_type_attribute_id_hex", first(obj_type_attr, "id_hex", None)),
        "issue_object_id": first(issue_conn, "object_id_hex", obj["id_hex"]),
        "history_object_id": first(history, "object_id_hex", obj["id_hex"]),
        "attachment_object_id": first(attachment, "object_id_hex", obj["id_hex"]),
        "label": label,
        "label_lower": label_lower,
        "label_like": f"%{label_like_token}%",
        "text_value_5": clean_fts_phrase(str(first(fts_text_value_5, "text_value_5", ""))),
        "numeric_value_1": int(float(obj.get("numeric_value_1") or 1)),
        "numeric_value_2": int(float(obj.get("numeric_value_2") or 1)),
        "numeric_value_3": int(float(obj.get("numeric_value_3") or 1)),
        "numeric_value_5": int(float(obj.get("numeric_value_5") or 1)),
    }


def alias_map(sql: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(
        r"(?i)\b(?:from|join)\s+(?:`?[a-zA-Z0-9_]+`?\s*\.\s*)?`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?",
        sql,
    ):
        table, alias = match.groups()
        # Avoid treating SQL keywords as aliases when a table has no alias.
        if alias.lower() not in {"where", "on", "left", "inner", "right", "join"}:
            result[alias] = table
    return result


def column_context(sql: str, pos: int) -> tuple[str | None, str | None, str | None]:
    before = sql[max(0, pos - 240) : pos]
    patterns = [
        r"`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s*\.\s*`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s*(=|!=|<>|<=|>=|<|>|like|in\s*\(|between)\s*$",
        r"`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s*(=|!=|<>|<=|>=|<|>|like|in\s*\(|between)\s*$",
    ]
    match = re.search(patterns[0], before, flags=re.IGNORECASE)
    if match:
        return match.group(1), match.group(2), match.group(3).lower()
    match = re.search(patterns[1], before, flags=re.IGNORECASE)
    if match:
        return None, match.group(1), match.group(2).lower()
    return None, None, None


def main_table(sql: str) -> str | None:
    match = re.search(
        r"(?i)\bfrom\s+(?:`?[a-zA-Z0-9_]+`?\s*\.\s*)?`?([a-zA-Z_][a-zA-Z0-9_]*)`?",
        sql,
    )
    return match.group(1) if match else None


def binary_for(table: str | None, column: str, ctx: dict, as_list: bool = False) -> str:
    col = column.lower()
    table_name = (table or "").lower()

    if col in {"obj_type_id", "object_type_id", "referenced_object_type_id"}:
        if as_list:
            return ", ".join(hex_lit(v) for v in ctx["obj_type_ids"])
        if table_name in {"obj_type", "cdm_type_obj_type", "ota_obj_column_mapping", "obj_type_attr"}:
            return hex_lit(ctx["obj_type_id"])
        return hex_lit(ctx["obj_type_ids"][0])

    if col in {"id"}:
        if table_name == "obj_new":
            return hex_lit(ctx["obj_id"])
        if table_name == "obj_relationship":
            return hex_lit(ctx["rel_orig_id"])
        if table_name == "obj_relationship_new":
            return hex_lit(ctx["rel_new_id"])
        if table_name == "obj_type":
            return hex_lit(ctx["obj_type_id"])
        if table_name == "obj_type_attr":
            return hex_lit(ctx["obj_type_attr_id"])
        if table_name == "obj_schema":
            return hex_lit(ctx["schema_id"])
        if table_name == "icon":
            return hex_lit(ctx["icon_id"])
        if table_name == "ref_type":
            return hex_lit(ctx["ref_type_id"])
        return hex_lit(ctx["obj_id"])

    if col == "object_id":
        if table_name == "obj_history":
            return hex_lit(ctx["history_object_id"])
        if table_name == "obj_attachment":
            return hex_lit(ctx["attachment_object_id"])
        if table_name in {"object_issue_connection", "issue_custom_field_connection"}:
            return hex_lit(ctx["issue_object_id"])
        return hex_lit(ctx["rel_object_id"])

    if col == "referenced_object_id":
        return hex_lit(ctx["rel_ref_id"])

    if col in {"object_type_attribute_id", "obj_type_attr_id"}:
        return hex_lit(ctx["obj_type_attr_id"])

    if col in {"object_schema_id", "obj_schema_id"}:
        return hex_lit(ctx["schema_id"])

    if col in {"icon_id"}:
        return hex_lit(ctx["icon_id"])

    if col in {"ref_type_id", "reference_type_id"}:
        return hex_lit(ctx["ref_type_id"])

    if col in {"issue_custom_field_connection_id"}:
        return hex_lit(ctx["obj_id"])

    return hex_lit(ctx["obj_id"])


def numeric_for(column: str, ctx: dict, op: str | None) -> str:
    col = column.lower()
    if op in {"!=", "<>"}:
        return "-1"
    if col == "numeric_value_1":
        return str(ctx["numeric_value_1"])
    if col == "numeric_value_2":
        return str(ctx["numeric_value_2"])
    if col == "numeric_value_3":
        if op in {"<=", "<"}:
            return str(max(ctx["numeric_value_3"], 100))
        return str(ctx["numeric_value_3"])
    if col == "numeric_value_5":
        return str(ctx["numeric_value_5"])
    return "1"


def replacement_for(sql: str, pos: int, ctx: dict, aliases: dict[str, str]) -> str:
    prefix = sql[:pos]
    suffix = sql[pos:]
    around = sql[max(0, pos - 160) : min(len(sql), pos + 160)].lower()
    prefix_lower = prefix.lower()

    if re.search(r"\bagainst\s*\(\s*$", prefix_lower):
        match_col = re.search(
            r"match\s*\(\s*(?:`?[a-zA-Z_][a-zA-Z0-9_]*`?\s*\.\s*)?`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s*\)\s*against\s*\(\s*$",
            prefix,
            flags=re.IGNORECASE,
        )
        if match_col and match_col.group(1).lower() == "label":
            return sql_quote(f'"{ctx["label"]}"')
        return sql_quote(f'"{ctx["text_value_5"]}"')

    if re.search(r"\blimit\s*$", prefix_lower):
        return "1000"
    if re.search(r"\boffset\s*$", prefix_lower):
        return "0"

    if re.search(r"\bis\s+(?:not\s+)?$", prefix_lower):
        return "NULL"

    if re.match(r"\?\s*!=\s*\?", suffix):
        return "1"
    if re.search(r"\?\s*!=\s*$", prefix_lower):
        return "2"

    if re.search(r"\band\s*$", prefix_lower):
        return "1=1"

    alias, column, op = column_context(sql, pos)
    table = aliases.get(alias or "", alias or main_table(sql))
    as_list = bool(op and op.startswith("in"))

    if not column:
        return "0"

    col = column.lower()
    if col == "workspace_id":
        return sql_quote(ctx["workspace_id"])
    if col == "partition_id":
        return str(ctx["partition_id"])
    if col == "is_deleted":
        return "0"
    if col == "issue_deleted":
        return "0"
    if col == "sequential_id":
        table_l = (table or "").lower()
        if table_l == "obj_schema":
            return str(ctx["schema_seq"])
        if table_l == "obj_type":
            return str(ctx["obj_type_seq"])
        if table_l == "obj_type_attr":
            return str(ctx["obj_type_attr_seq"])
        return str(ctx["obj_sequential_id"])
    if col == "label_lower":
        return sql_quote(ctx["label_like"])
    if col.startswith("text_value_"):
        if op in {"!=", "<>"}:
            return sql_quote("")
        return sql_quote(ctx["text_value_5"])
    if col.startswith("numeric_value_"):
        return numeric_for(col, ctx, op)

    binary_cols = {
        "id",
        "obj_type_id",
        "object_type_id",
        "referenced_object_type_id",
        "object_id",
        "referenced_object_id",
        "object_type_attribute_id",
        "obj_type_attr_id",
        "object_schema_id",
        "obj_schema_id",
        "icon_id",
        "ref_type_id",
        "reference_type_id",
        "issue_custom_field_connection_id",
    }
    if col in binary_cols:
        return binary_for(table, col, ctx, as_list=as_list)

    return "0"


def materialize(template: QueryTemplate, ctx: dict) -> str:
    sql = template.sql
    aliases = alias_map(sql)
    parts: list[str] = []
    last = 0
    for match in re.finditer(r"\?", sql):
        parts.append(sql[last : match.start()])
        parts.append(replacement_for(sql, match.start(), ctx, aliases))
        last = match.end()
    parts.append(sql[last:])
    concrete = "".join(parts)
    concrete = re.sub(r"\s+", " ", concrete).strip()
    concrete = rewrite_label_lower_like_to_match(concrete)
    return concrete.rstrip(";") + ";"


def rewrite_label_lower_like_to_match(sql: str) -> str:
    def replace(match: re.Match) -> str:
        alias_prefix = match.group("alias") or ""
        phrase = match.group("phrase").strip("%")
        phrase = phrase.replace("''", "'").replace('"', '\\"')
        if alias_prefix:
            label_expr = f"{alias_prefix}`label`"
        else:
            label_expr = "`label`"
        return f"match({label_expr}) against('\"{phrase}\"' in boolean mode)"

    return re.sub(
        r"(?i)(?P<alias>`?[a-zA-Z_][a-zA-Z0-9_]*`?\s*\.\s*)?`?label_lower`?\s+like\s+'(?P<phrase>[^']*)'",
        replace,
        sql,
    )


def is_write_sql(sql: str) -> bool:
    return bool(re.match(r"^\s*(insert|update|delete|replace|create|alter|drop|truncate)\b", sql, re.IGNORECASE))


def connect_db(host: str, port: int, user: str, database: str, timeout_sec: int):
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        database=database,
        connection_timeout=10,
        read_timeout=timeout_sec,
        write_timeout=30,
        use_pure=True,
    )


def run_query(conn, sql: str, timeout_sec: int) -> dict:
    start = time.perf_counter()
    try:
        cursor = conn.cursor(buffered=False)
        cursor.execute(sql)
        rows = 0
        if cursor.with_rows:
            for _ in cursor:
                rows += 1
        elapsed_ms = (time.perf_counter() - start) * 1000
        cursor.close()
        return {
            "status": "ok",
            "elapsed_ms": round(elapsed_ms, 3),
            "returned_rows": rows,
            "error": "",
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "elapsed_ms": round(timeout_sec * 1000, 3),
            "returned_rows": None,
            "error": f"timeout after {timeout_sec}s",
        }
    except mysql.connector.errors.ReadTimeoutError:
        return {
            "status": "timeout",
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
            "returned_rows": None,
            "error": f"read timeout after {timeout_sec}s",
        }
    except Exception as exc:
        return {
            "status": "error",
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
            "returned_rows": None,
            "error": str(exc)[:1000],
        }


def render_markdown(results: list[dict], output_corpus: Path) -> str:
    total = len(results)
    ok = sum(1 for r in results if r["status"] == "ok")
    timeout = sum(1 for r in results if r["status"] == "timeout")
    error = sum(1 for r in results if r["status"] == "error")
    zero = sum(1 for r in results if r["status"] == "ok" and r["returned_rows"] == 0)

    lines = [
        "# JSM Workload Smoke Run",
        "",
        "This document records the materialized smoke run for `/Users/jin/Downloads/workload_queries.sql`.",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- Target database: `jsm_assets3`",
        f"- Materialized Go corpus: `{output_corpus}`",
        "- Latency source: client-side elapsed time through the local SSH tunnel to TiDB; use this for correctness and outlier detection only, not final QPS reporting.",
        "- Workload note: write templates are excluded from the generated read-only corpus by default.",
        "",
        "## Summary",
        "",
        f"- Total queries: `{total}`",
        f"- OK: `{ok}`",
        f"- Returned 0 rows: `{zero}`",
        f"- Errors: `{error}`",
        f"- Timeouts: `{timeout}`",
        "",
        "## Results",
        "",
        "| Query | Source avg ms | Status | Rows | Smoke elapsed ms | Notes |",
        "| --- | ---: | --- | ---: | ---: | --- |",
    ]
    for r in results:
        rows = "-" if r["returned_rows"] is None else str(r["returned_rows"])
        notes = r.get("error", "").replace("\n", " ")[:180]
        lines.append(
            f"| {r['query_id']} | {r['source_avg_latency_ms']} | `{r['status']}` | {rows} | {r['elapsed_ms']} | {notes} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("/Users/jin/Downloads/workload_queries.sql"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=45001)
    parser.add_argument("--user", default="root")
    parser.add_argument("--database", default="jsm_assets3")
    parser.add_argument("--mysql-bin", default="/usr/local/mysql-9.0.1-macos14-arm64/bin/mysql")
    parser.add_argument("--timeout-sec", type=int, default=90)
    parser.add_argument("--output-corpus", type=Path, default=Path("bench/workload_smoke_corpus.json"))
    parser.add_argument("--output-json", type=Path, default=Path("bench/results/workload_smoke_run.json"))
    parser.add_argument("--output-md", type=Path, default=Path("jsm_workload_smoke_run.md"))
    parser.add_argument("--materialize-only", action="store_true")
    parser.add_argument("--include-writes", action="store_true")
    args = parser.parse_args()

    templates = parse_workload(args.source)
    if not templates:
        raise RuntimeError(f"no queries parsed from {args.source}")

    conn = connect_db(args.host, args.port, args.user, args.database, args.timeout_sec)
    try:
        ctx = build_context(conn, args.database)
    finally:
        conn.close()

    corpus = []
    for template in templates:
        sql = materialize(template, ctx)
        if is_write_sql(sql) and not args.include_writes:
            continue
        corpus.append(
            {
                "id": template.query_id,
                "pattern": template.group,
                "description": f"{template.group} / Query {template.query_no}",
                "weight": max(1, template.exec_count),
                "expected_row_count": 0,
                "sql": sql,
                "source_exec_count": template.exec_count,
                "source_avg_latency_ms": template.source_avg_latency_ms,
                "digest": template.digest,
                "original_sql": template.sql,
            }
        )

    args.output_corpus.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_corpus.write_text(json.dumps(corpus, ensure_ascii=False, indent=2) + "\n")
    if args.materialize_only:
        print(f"wrote materialized corpus: {args.output_corpus}")
        return 0

    results = []
    smoke_conn = connect_db(args.host, args.port, args.user, args.database, args.timeout_sec)
    for idx, spec in enumerate(corpus, start=1):
        result = run_query(
            conn=smoke_conn,
            sql=spec["sql"],
            timeout_sec=args.timeout_sec,
        )
        item = {
            "query_id": spec["id"],
            "pattern": spec["pattern"],
            "description": spec["description"],
            "source_exec_count": spec["source_exec_count"],
            "source_avg_latency_ms": spec["source_avg_latency_ms"],
            "status": result["status"],
            "returned_rows": result["returned_rows"],
            "elapsed_ms": result["elapsed_ms"],
            "error": result["error"],
            "sql": spec["sql"],
        }
        results.append(item)
        if result["status"] == "ok":
            spec["expected_row_count"] = result["returned_rows"]
        print(
            f"[{idx}/{len(corpus)}] {spec['id']}: {result['status']} "
            f"rows={result['returned_rows']} elapsed={result['elapsed_ms']}ms",
            flush=True,
        )
    smoke_conn.close()

    args.output_corpus.write_text(json.dumps(corpus, ensure_ascii=False, indent=2) + "\n")
    args.output_json.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    args.output_md.write_text(render_markdown(results, args.output_corpus))
    print(f"wrote smoke json: {args.output_json}")
    print(f"wrote smoke doc: {args.output_md}")
    print(f"wrote materialized corpus: {args.output_corpus}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
