#!/usr/bin/env python3

import argparse
import concurrent.futures
import importlib.util
import json
import re
import shlex
import subprocess
import sys
import time
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


def run_case(case, args) -> dict:
    transformed = QCHECK.transform_sql(case.sql)
    actual_sql = rewrite_binary_uuid_literals(transformed).strip().rstrip(";") + ";"

    try:
        stdout, stderr, rc, elapsed_ms = run_remote_query(
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
            "latency_ms": args.timeout_sec * 1000,
            "original_sql": case.sql,
            "actual_sql": actual_sql,
        }

    if rc == 0:
        rows = [line for line in stdout.splitlines() if line.strip() != ""]
        return {
            "order": case.order,
            "query_id": case.full_id,
            "status": "ok",
            "latency_ms": round(elapsed_ms, 1),
            "has_rows": bool(rows),
            "returned_rows": len(rows),
            "original_sql": case.sql,
            "actual_sql": actual_sql,
        }

    return {
        "order": case.order,
        "query_id": case.full_id,
        "status": "error",
        "latency_ms": round(elapsed_ms, 1),
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
        "| Query | Status | Has rows | Returned rows | Latency (ms) | Notes |",
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
            f"| {result['query_id']} | `{result['status']}` | {has_rows} | {returned_rows} | {result['latency_ms']} | {notes} |"
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--database", default="jsm_assets3")
    parser.add_argument("--timeout-sec", type=int, default=45)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--ssh-host", required=True)
    parser.add_argument("--ssh-key", required=True)
    args = parser.parse_args()

    source = Path(args.source)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    queries = QCHECK.parse_queries(source)
    print(f"starting {len(queries)} queries with {args.workers} workers", flush=True)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run_case, q, args) for q in queries]
        for idx, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            result = future.result()
            print(
                f"[{idx}/{len(queries)}] {result['query_id']} -> {result['status']} "
                f"{result.get('returned_rows', '-')}/{result['latency_ms']}ms",
                flush=True,
            )
            results.append(result)

    results.sort(key=lambda item: item["order"])
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
