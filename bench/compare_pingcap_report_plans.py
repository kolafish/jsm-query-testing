#!/usr/bin/env python3
"""Compare local TiDB plans with the PingCAP customer report plans.

The customer report stores EXPLAIN ANALYZE output for query #1..#25. This tool
extracts stable plan-shape signatures from that report, optionally captures
current EXPLAIN plans for sampled jsm_assets4 SQL, and writes a markdown
comparison focused on operator/task/index shape rather than runtime numbers.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VIEWER_SCRIPT = REPO_ROOT / "reports/pingcap-query-performance-2026-05-06/create_pingcap_query_viewer.py"
SOURCE_REPORT = REPO_ROOT / "reports/pingcap-query-performance-2026-05-06/full_report_for_pingcap.md"
SAMPLED_RESULTS = REPO_ROOT / "bench/results/pingcap_report_jsm_assets4_query_sample_comparison.json"
OUT_JSON = REPO_ROOT / "bench/results/pingcap_report_plan_comparison.json"
OUT_MD = REPO_ROOT / "pingcap_report_plan_comparison.md"


def load_viewer_module() -> Any:
    spec = importlib.util.spec_from_file_location("pingcap_query_viewer", VIEWER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load parser from {VIEWER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def clean_operator(node: str) -> str:
    node = re.sub(r"^[\s│├└─]+", "", node).strip()
    node = re.sub(r"\([^)]+\)$", "", node)
    node = re.sub(r"_\d+$", "", node)
    return node


def compact(text: str, limit: int = 140) -> str:
    text = re.sub(r"\s+", " ", str(text).strip())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def cell_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        try:
            text = value.decode("utf-8")
        except UnicodeDecodeError:
            text = value.decode("latin1")
    else:
        text = str(value)
    # Keep raw plans parseable and markdown-safe even when EXPLAIN embeds binary handles.
    return text.replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n")


def extract_access(row: Any) -> dict[str, str]:
    info = row.operator_info or ""
    table_match = re.search(r"table:([^,\s]+)", info)
    index_match = re.search(r"index:([^(,\s]+)\(([^)]*)\)", info)
    access = {
        "operator": clean_operator(row.node),
        "task": row.task,
        "table": table_match.group(1) if table_match else "",
        "index": index_match.group(1) if index_match else "",
        "index_columns": index_match.group(2) if index_match else "",
    }
    return access


def signature_from_rows(rows: list[Any]) -> dict[str, Any]:
    operators = [clean_operator(row.node) for row in rows]
    tasks = [row.task for row in rows]
    scan_rows = [row for row in rows if clean_operator(row.node).endswith("Scan")]
    reader_rows = [row for row in rows if clean_operator(row.node).endswith("Reader")]
    join_ops = [op for op in operators if "Join" in op]
    access_paths = [extract_access(row) for row in scan_rows + reader_rows]
    indexes = sorted(
        {
            f"{item['table']}.{item['index']}({item['index_columns']})"
            for item in access_paths
            if item["index"]
        }
    )
    index_columns_paths = sorted(
        {
            f"{item['table']}({item['index_columns']})"
            for item in access_paths
            if item["index_columns"]
        }
    )
    tables = sorted({item["table"] for item in access_paths if item["table"]})
    task_set = sorted({task for task in tasks if task})
    return {
        "operators": operators,
        "tasks": tasks,
        "task_set": task_set,
        "join_ops": join_ops,
        "access_paths": access_paths,
        "indexes": indexes,
        "index_columns_paths": index_columns_paths,
        "tables": tables,
        "topology": " -> ".join(operators),
        "task_topology": " -> ".join(f"{op}[{task}]" for op, task in zip(operators, tasks)),
    }


def parse_simple_explain_rows(raw_plan: str) -> list[Any]:
    rows: list[Any] = []
    lines = [line for line in raw_plan.splitlines() if line.strip()]
    if len(lines) < 2:
        return rows
    header = [part.strip().lower() for part in lines[0].split("\t")]
    if "task" not in header or not any(col in header for col in ["access object", "operator info"]):
        return rows
    for line in lines[1:]:
        parts = [part.strip() for part in line.split("\t")]
        if len(parts) < len(header):
            parts += [""] * (len(header) - len(parts))
        values = dict(zip(header, parts))
        access_object = values.get("access object", "")
        operator_info = values.get("operator info", "")
        rows.append(
            SimpleNamespace(
                node=values.get("id", ""),
                task=values.get("task", ""),
                est_rows=values.get("estrows", ""),
                act_rows=values.get("actrows", ""),
                operator_info=f"{access_object} {operator_info}".strip(),
                access_object=access_object,
                execution_info=values.get("execution info", ""),
                memory=values.get("memory", ""),
                disk=values.get("disk", ""),
            )
        )
    return rows


def parse_plan_text(raw_plan: str) -> dict[str, Any]:
    viewer = load_viewer_module()
    rows = viewer.parse_plan(raw_plan)
    if not rows:
        rows = parse_simple_explain_rows(raw_plan)
    return {
        "raw_plan": raw_plan,
        "signature": signature_from_rows(rows),
    }


def normalize_explain_rows(rows: list[tuple[Any, ...]], columns: list[str]) -> str:
    normalized = []
    normalized.append("\t".join(columns))
    for row in rows:
        normalized.append("\t".join(cell_text(value) for value in row))
    return "\n".join(normalized)


def plan_from_explain_result(rows: list[tuple[Any, ...]], columns: list[str]) -> dict[str, Any]:
    header = [column.strip().lower() for column in columns]
    plan_rows = []
    for row in rows:
        values = dict(zip(header, [cell_text(value) for value in row]))
        access_object = values.get("access object", "")
        operator_info = values.get("operator info", "")
        plan_rows.append(
            SimpleNamespace(
                node=values.get("id", ""),
                task=values.get("task", ""),
                est_rows=values.get("estrows", ""),
                act_rows=values.get("actrows", ""),
                operator_info=f"{access_object} {operator_info}".strip(),
                access_object=access_object,
                execution_info=values.get("execution info", ""),
                memory=values.get("memory", ""),
                disk=values.get("disk", ""),
            )
        )
    return {
        "raw_plan": normalize_explain_rows(rows, columns),
        "signature": signature_from_rows(plan_rows),
    }


def capture_current_plans(args: argparse.Namespace, sampled: dict[str, Any]) -> dict[str, Any]:
    try:
        import pymysql
    except ImportError as exc:
        raise RuntimeError("pymysql is required for --capture-current") from exc

    def connect() -> Any:
        return pymysql.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database,
            charset="utf8mb4",
            use_unicode=False,
            autocommit=True,
            read_timeout=args.read_timeout,
            write_timeout=args.read_timeout,
        )

    captured: dict[str, Any] = {
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "database": args.database,
        "explain_mode": args.explain_mode,
        "samples_per_query": args.samples_per_query,
        "queries": {},
    }
    for qid, query in sorted(sampled.get("queries", {}).items(), key=lambda item: int(item[0])):
        samples = [sample for sample in query.get("samples", []) if sample.get("sql")]
        if not samples:
            captured["queries"][qid] = {"status": "skipped", "reason": "no sampled SQL"}
            continue
        query_samples = []
        for sample in samples[: args.samples_per_query]:
            sql = sample["sql"].rstrip().rstrip(";")
            explain_sql = f"{args.explain_mode} {sql}"
            item = {"sample": sample.get("sample", ""), "params": sample.get("params", ""), "sql": sql}
            conn = None
            try:
                conn = connect()
                with conn.cursor() as cur:
                    for statement in args.set:
                        cur.execute(f"SET {statement}")
                    cur.execute(explain_sql)
                    rows = cur.fetchall()
                    columns = [cell_text(desc[0]) for desc in cur.description]
                    item.update(plan_from_explain_result(rows, columns))
                    item["status"] = "ok"
            except Exception as exc:  # noqa: BLE001 - preserve database error text in the report.
                item["status"] = "error"
                item["error"] = str(exc)
            finally:
                if conn is not None:
                    conn.close()
            query_samples.append(item)
        captured["queries"][qid] = {"status": "ok", "samples": query_samples}
    return captured


def compare_signatures(source: dict[str, Any], current: dict[str, Any] | None) -> dict[str, Any]:
    if not current:
        return {"status": "pending", "reasons": ["current plan not captured"]}
    if current.get("status") == "error":
        return {"status": "error", "reasons": [current.get("error", "current EXPLAIN failed")]}
    if "signature" not in current:
        return {"status": "error", "reasons": ["current EXPLAIN did not produce a parseable signature"]}

    src = source["signature"]
    cur = current["signature"]
    minor: list[str] = []
    major: list[str] = []

    def core_ops(operators: list[str]) -> list[str]:
        # Projection wrappers often differ between EXPLAIN and EXPLAIN ANALYZE
        # while the access path is identical.
        return [op for op in operators if op not in {"Projection", "Selection"}]

    def task_engines(tasks: list[str]) -> list[str]:
        engines = []
        for task in tasks:
            if "tiflash" in task:
                engines.append("tiflash")
            elif "tikv" in task:
                engines.append("tikv")
            elif task:
                engines.append(task)
        return sorted(set(engines))

    if src["operators"] != cur["operators"]:
        if core_ops(src["operators"]) == core_ops(cur["operators"]):
            minor.append("operator topology differs only by Projection wrapper")
        else:
            major.append("operator topology differs")
    if src["task_set"] != cur["task_set"]:
        if task_engines(src["task_set"]) == task_engines(cur["task_set"]):
            minor.append(f"task label differs but storage engines match: source={src['task_set']} current={cur['task_set']}")
        else:
            major.append(f"task set differs: source={src['task_set']} current={cur['task_set']}")
    if src["join_ops"] != cur["join_ops"]:
        major.append(f"join operators differ: source={src['join_ops']} current={cur['join_ops']}")
    if src["indexes"] != cur["indexes"]:
        if src["index_columns_paths"] == cur["index_columns_paths"]:
            minor.append(f"index name differs but indexed columns match: source={src['indexes']} current={cur['indexes']}")
        else:
            major.append(f"index access differs: source={src['indexes']} current={cur['indexes']}")
    if src["tables"] != cur["tables"]:
        major.append(f"scan tables differ: source={src['tables']} current={cur['tables']}")

    return {
        "status": "match" if not major and not minor else ("compatible" if not major else "mismatch"),
        "reasons": major + minor,
        "major_reasons": major,
        "minor_reasons": minor,
    }


def load_source_plans(source_report: Path) -> dict[str, Any]:
    viewer = load_viewer_module()
    markdown = source_report.read_text()
    _, anti_map = viewer.parse_anti_patterns(markdown)
    queries = viewer.parse_queries(markdown, anti_map)
    source: dict[str, Any] = {}
    for query in queries:
        source[str(query.qid)] = {
            "title": query.title,
            "group": query.group,
            "pattern": query.pattern,
            "severity": query.severity,
            "metrics": query.metrics,
            "normalized_sql": query.normalized_sql,
            "sample_sql": query.sample_sql,
            "raw_plan": query.raw_plan,
            "signature": signature_from_rows(query.plan_rows),
        }
    return source


def load_current_plan_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def current_representative(current_query: dict[str, Any] | None) -> dict[str, Any] | None:
    if not current_query or current_query.get("status") == "skipped":
        return None
    samples = current_query.get("samples", [])
    for sample in samples:
        if sample.get("status") == "ok":
            return sample
    return samples[0] if samples else None


def build_comparison(source_report: Path, source: dict[str, Any], current: dict[str, Any] | None) -> dict[str, Any]:
    current_queries = (current or {}).get("queries", {})
    items = []
    for qid in sorted(source, key=lambda x: int(x)):
        current_query = current_queries.get(qid)
        representative = current_representative(current_query)
        comparison = compare_signatures(source[qid], representative)
        items.append(
            {
                "query_id": int(qid),
                "source": source[qid],
                "current": current_query,
                "representative_current": representative,
                "comparison": comparison,
            }
        )
    summary: dict[str, int] = {}
    for item in items:
        status = item["comparison"]["status"]
        summary[status] = summary.get(status, 0) + 1
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_report": str(source_report.relative_to(REPO_ROOT) if source_report.is_relative_to(REPO_ROOT) else source_report),
        "current_plan_file": str((current or {}).get("path", "")),
        "summary": summary,
        "items": items,
    }


def render_markdown(result: dict[str, Any], out: Path) -> None:
    lines = [
        "# PingCAP Report Plan Comparison",
        "",
        f"Generated at: `{result['generated_at']}`",
        "",
        f"Source report: `{result['source_report']}`",
        "",
        "Comparison checks the stable plan shape: operator topology, storage task set, join operators, scanned tables, and index access paths. Runtime row counts and latency are intentionally ignored.",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status in ["match", "compatible", "mismatch", "error", "pending"]:
        lines.append(f"| {status} | {result['summary'].get(status, 0)} |")

    lines += [
        "",
        "## Query Plan Shape",
        "",
        "| Query | Source pattern | Source task set | Source top operators | Source indexes | Current status | Difference |",
        "|---:|---|---|---|---|---|---|",
    ]
    for item in result["items"]:
        source = item["source"]
        sig = source["signature"]
        comparison = item["comparison"]
        reasons = "; ".join(comparison["reasons"]) if comparison["reasons"] else ""
        lines.append(
            f"| {item['query_id']} | {source.get('pattern') or source.get('group') or ''} | "
            f"{', '.join(sig['task_set'])} | {compact(sig['topology'])} | "
            f"{compact(', '.join(sig['indexes']) or 'n/a')} | {comparison['status']} | {compact(reasons or 'n/a', 220)} |"
        )

    lines += ["", "## Details", ""]
    for item in result["items"]:
        qid = item["query_id"]
        source = item["source"]
        current = item.get("representative_current")
        lines += [
            f"### Query {qid}",
            "",
            f"- Source status: `{item['comparison']['status']}`",
            f"- Source topology: `{compact(source['signature']['topology'], 500)}`",
            f"- Source task topology: `{compact(source['signature']['task_topology'], 500)}`",
            f"- Source indexes: `{', '.join(source['signature']['indexes']) or 'n/a'}`",
        ]
        if current:
            if current.get("status") == "ok":
                lines += [
                    f"- Current sample: `{current.get('sample', '')}`",
                    f"- Current topology: `{compact(current['signature']['topology'], 500)}`",
                    f"- Current task topology: `{compact(current['signature']['task_topology'], 500)}`",
                    f"- Current indexes: `{', '.join(current['signature']['indexes']) or 'n/a'}`",
                ]
            else:
                lines.append(f"- Current error: `{current.get('error', '')}`")
        else:
            lines.append("- Current plan: not captured yet.")
        lines.append("")

    out.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-report", type=Path, default=SOURCE_REPORT)
    parser.add_argument("--sampled-results", type=Path, default=SAMPLED_RESULTS)
    parser.add_argument("--current-plan-json", type=Path, default=REPO_ROOT / "bench/results/pingcap_report_current_plans.json")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    parser.add_argument("--capture-current", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default="jsm_assets4")
    parser.add_argument("--read-timeout", type=int, default=180)
    parser.add_argument("--samples-per-query", type=int, default=1)
    parser.add_argument("--explain-mode", choices=["EXPLAIN", "EXPLAIN ANALYZE"], default="EXPLAIN")
    parser.add_argument("--set", action="append", default=[])
    args = parser.parse_args()

    source = load_source_plans(args.source_report)
    current = load_current_plan_file(args.current_plan_json)
    if current is not None:
        current["path"] = str(args.current_plan_json)

    if args.capture_current:
        sampled = json.loads(args.sampled_results.read_text())
        current = capture_current_plans(args, sampled)
        current["path"] = str(args.current_plan_json)
        args.current_plan_json.parent.mkdir(parents=True, exist_ok=True)
        args.current_plan_json.write_text(json.dumps(current, indent=2, default=str) + "\n")

    result = build_comparison(args.source_report, source, current)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, default=str) + "\n")
    render_markdown(result, args.out_md)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()
