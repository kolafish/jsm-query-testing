#!/usr/bin/env python3

import argparse
import concurrent.futures
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class QueryCase:
    order: int
    section: str
    subsection: str
    query_label: str
    sql: str

    @property
    def full_id(self) -> str:
        parts = [self.section]
        if self.subsection:
            parts.append(self.subsection)
        if self.query_label:
            parts.append(self.query_label)
        return " / ".join(parts)


def parse_queries(markdown_path: Path) -> list[QueryCase]:
    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    section = ""
    subsection = ""
    query_label = ""
    in_sql = False
    sql_lines: list[str] = []
    queries: list[QueryCase] = []

    order = 0
    for line in lines:
        if line.startswith("## "):
            section = line[3:].strip()
            subsection = ""
            query_label = ""
            continue
        if line.startswith("### "):
            title = line[4:].strip()
            if title.startswith("Query "):
                query_label = title
            else:
                subsection = title
                query_label = ""
            continue
        if line.startswith("#### "):
            query_label = line[5:].strip()
            continue
        if line.startswith("```sql"):
            in_sql = True
            sql_lines = []
            continue
        if line.startswith("```") and in_sql:
            in_sql = False
            queries.append(
                QueryCase(
                    order=order,
                    section=section,
                    subsection=subsection,
                    query_label=query_label,
                    sql="\n".join(sql_lines).strip(),
                )
            )
            order += 1
            sql_lines = []
            continue
        if in_sql:
            sql_lines.append(line)

    return queries


def transform_sql(sql: str) -> str:
    transformed = sql
    transformed = re.sub(r"`obj_relationship`", "`obj_relationship_new`", transformed)
    transformed = re.sub(r"`obj`", "`obj_new`", transformed)
    return transformed


def wrap_exists_sql(sql: str) -> str:
    stripped = sql.strip().rstrip(";")
    return f"select 1 as has_row from (\n{stripped}\n) as q limit 1;"


def run_query(
    mysql_bin: str,
    host: str,
    port: int,
    database: str,
    sql: str,
    timeout_sec: int,
    ssh_host: str | None = None,
    ssh_key: str | None = None,
) -> tuple[str, str, int]:
    if ssh_host:
        remote_cmd = (
            "kubectl -n tidb-cluster exec mysql-client -- "
            "mysql -h tici-demo-s3-tidb -P4000 -uroot "
            f"--database {shlex.quote(database)} --batch --raw --skip-column-names "
            f"-e {shlex.quote(sql)}"
        )
        cmd = ["ssh"]
        if ssh_key:
            cmd.extend(["-i", ssh_key])
        cmd.extend([ssh_host, remote_cmd])
    else:
        cmd = [
            mysql_bin,
            "-h",
            host,
            "-P",
            str(port),
            "-uroot",
            "--database",
            database,
            "--batch",
            "--raw",
            "--skip-column-names",
            "-e",
            sql,
        ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    return proc.stdout.strip(), proc.stderr.strip(), proc.returncode


def render_markdown(
    results: list[dict],
    source_doc: str,
    target_tables: str,
) -> str:
    total = len(results)
    positive = sum(1 for r in results if r["status"] == "ok" and r["has_rows"])
    zero = sum(1 for r in results if r["status"] == "ok" and not r["has_rows"])
    error = sum(1 for r in results if r["status"] != "ok")

    lines = [
        "# JSM Assets3 Original Query Match Check",
        "",
        "This document records one pass over the original query corpus with the original predicate values left unchanged.",
        "",
        f"- Source query doc: `{source_doc}`",
        f"- Target tables: `{target_tables}`",
        "- Query text changes: only `obj -> obj_new` and `obj_relationship -> obj_relationship_new`",
        "",
        "## Summary",
        "",
        f"- Total queries: `{total}`",
        f"- Queries with returned rows > 0: `{positive}`",
        f"- Queries with returned rows = 0: `{zero}`",
        f"- Queries with execution errors: `{error}`",
        "",
        "## Results",
        "",
        "| Query | Status | Has rows | Notes |",
        "| --- | --- | --- | --- |",
    ]

    for result in results:
        if result["status"] == "ok":
            notes = "matched" if result["has_rows"] else "no rows"
            has_rows = "yes" if result["has_rows"] else "no"
        elif result["status"] == "timeout":
            notes = f"timeout after {result['timeout_sec']}s"
            has_rows = "-"
        else:
            notes = result["error"].replace("\n", " ")[:200]
            has_rows = "-"

        lines.append(
            f"| {result['query_id']} | `{result['status']}` | {has_rows} | {notes} |"
        )

    return "\n".join(lines) + "\n"


def run_case(case: QueryCase, args: argparse.Namespace) -> dict:
    transformed = transform_sql(case.sql)
    wrapped = wrap_exists_sql(transformed)
    try:
        stdout, stderr, rc = run_query(
            mysql_bin=args.mysql_bin,
            host=args.host,
            port=args.port,
            database=args.database,
            sql=wrapped,
            timeout_sec=args.timeout_sec,
            ssh_host=args.ssh_host,
            ssh_key=args.ssh_key,
        )
    except subprocess.TimeoutExpired:
        return {
            "order": case.order,
            "query_id": case.full_id,
            "status": "timeout",
            "timeout_sec": args.timeout_sec,
            "original_sql": case.sql,
            "actual_sql": transformed,
        }

    if rc == 0:
        return {
            "order": case.order,
            "query_id": case.full_id,
            "status": "ok",
            "has_rows": bool(stdout.strip()),
            "original_sql": case.sql,
            "actual_sql": transformed,
        }

    return {
        "order": case.order,
        "query_id": case.full_id,
        "status": "error",
        "error": stderr or stdout or f"mysql exited with {rc}",
        "original_sql": case.sql,
        "actual_sql": transformed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--mysql-bin", default="mysql")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=34009)
    parser.add_argument("--database", default="jsm_assets3")
    parser.add_argument("--timeout-sec", type=int, default=60)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--ssh-host")
    parser.add_argument("--ssh-key")
    args = parser.parse_args()

    source = Path(args.source)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    queries = parse_queries(source)
    results: list[dict] = []

    print(f"starting {len(queries)} queries with {args.workers} workers", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {
            executor.submit(run_case, case, args): case for case in queries
        }
        completed = 0
        for future in concurrent.futures.as_completed(future_map):
            result = future.result()
            completed += 1
            print(
                f"[{completed}/{len(queries)}] {result['query_id']} -> {result['status']}",
                flush=True,
            )
            results.append(result)

    results.sort(key=lambda item: item["order"])
    for result in results:
        result.pop("order", None)

    output_json.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(
        render_markdown(
            results=results,
            source_doc=source.name,
            target_tables="jsm_assets3.obj_new / jsm_assets3.obj_relationship_new",
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
