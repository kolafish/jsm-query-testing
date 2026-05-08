#!/usr/bin/env python3
"""Sample and run the PingCAP report top queries against jsm_assets4.

The source report contains normalized statements with placeholders. This script
materializes representative parameter sets from jsm_assets4, runs the matching
query shapes, and writes JSON plus a markdown comparison.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import math
import re
import statistics
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

import pymysql


REPORT = Path("/Users/jin/Downloads/full_report_for_pingcap.md")
OUT_MD = Path("pingcap_report_jsm_assets4_query_sample_comparison.md")
OUT_JSON = Path("bench/results/pingcap_report_jsm_assets4_query_sample_comparison.json")
DB = "jsm_assets4"
DEFAULT_GRAFANA_URL = (
    "http://a2e41aa49d08647d1b55ecd7b146bbf6-38f9eda417a300aa."
    "elb.us-east-2.amazonaws.com:3000"
)

MISSING_TABLES = {
    1: "cdm_type_obj_type_attr is not present in jsm_assets4",
    3: "cdm_type_obj_type, cdm_type_obj_schema, and obj_schema_owner are not present in jsm_assets4",
    12: "cdm_type_ref_type, cdm_type_obj_schema, and obj_schema_owner are not present in jsm_assets4",
}


def sql_quote(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bytes):
        return "0x" + value.hex()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return "NULL"
        return str(value)
    s = str(value)
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


def bin_hex(value: bytes | str) -> str:
    if isinstance(value, bytes):
        return "0x" + value.hex()
    v = str(value)
    if v.startswith("0x"):
        return v
    return "0x" + v.replace("-", "")


def uuid_hex(value: bytes | str) -> str:
    if isinstance(value, bytes):
        h = value.hex()
    else:
        h = str(value).replace("0x", "").replace("-", "")
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def safe_label(value: Any, limit: int = 80) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bytes):
        return uuid_hex(value)
    s = str(value).replace("\n", " ")
    return s if len(s) <= limit else s[: limit - 3] + "..."


def parse_source_metrics(report_text: str) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    pattern = re.compile(r"^(?:#{3,4}) Query #(\d+).*?(?=^(?:#{3,4}) Query #|\Z)", re.S | re.M)
    for m in pattern.finditer(report_text):
        qid = int(m.group(1))
        sec = m.group(0)
        metrics: dict[str, Any] = {}
        table = re.search(r"\| Metric \| Value \|\n\|[-| ]+\|\n(.*?)(?:\n\n|\n\*\*)", sec, re.S)
        if table:
            for line in table.group(1).splitlines():
                if not line.startswith("|"):
                    continue
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) >= 2:
                    metrics[parts[0]] = parts[1]
        rows[qid] = {
            "tables": metrics.get("Tables", ""),
            "indexes_used": metrics.get("Indexes used", ""),
            "exec_count": metrics.get("Exec count", ""),
            "source_avg_latency": metrics.get("Avg latency", ""),
            "source_max_latency": metrics.get("Max latency", ""),
            "source_avg_rows": metrics.get("Avg result rows", ""),
            "source_avg_cop_tasks": metrics.get("Avg cop tasks", ""),
            "digest": metrics.get("Digest", ""),
        }
    return rows


def ms_from_source(s: str) -> float | None:
    if not s:
        return None
    m = re.match(r"([0-9.]+)\s*ms", s)
    return float(m.group(1)) if m else None


def connect(args: argparse.Namespace):
    return pymysql.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        database=DB,
        charset="utf8mb4",
        autocommit=True,
        read_timeout=args.read_timeout,
        write_timeout=args.read_timeout,
    )


def fetchall(cur, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    cur.execute(sql, params)
    return list(cur.fetchall())


def top_workspaces(cur, limit: int) -> list[str]:
    rows = fetchall(
        cur,
        f"""
        SELECT workspace_id, COUNT(*) cnt
        FROM obj_new
        GROUP BY workspace_id
        ORDER BY cnt DESC
        LIMIT {limit}
        """,
    )
    return [r["workspace_id"] for r in rows]


def object_types(cur, workspace: str, where: str = "1=1", limit: int = 5) -> list[bytes]:
    rows = fetchall(
        cur,
        f"""
        SELECT obj_type_id, COUNT(*) cnt
        FROM obj_new
        WHERE workspace_id=%s AND {where}
        GROUP BY obj_type_id
        ORDER BY cnt DESC
        LIMIT {limit}
        """,
        (workspace,),
    )
    return [r["obj_type_id"] for r in rows]


def obj_type_list(types: list[bytes]) -> str:
    return ", ".join(bin_hex(t) for t in types)


def relation_select() -> str:
    return (
        "obj_relationship.workspace_id, obj_relationship.partition_id, obj_relationship.id, "
        "obj_relationship.object_id, obj_relationship.referenced_object_id, "
        "obj_relationship.object_type_attribute_id, obj_relationship.object_type_id, "
        "obj_relationship.referenced_object_type_id"
    )


def metadata_ota_select() -> str:
    return (
        "otae1_0.id, otae1_0.additional_value, otae1_0.aql, otae1_0.created, "
        "otae1_0.default_type_id, otae1_0.deleted_at, otae1_0.description, "
        "otae1_0.external_id, otae1_0.group_id_type_value, otae1_0.hidden, "
        "otae1_0.include_child_object_types, otae1_0.is_deleted, otae1_0.label, "
        "otae1_0.maximum_cardinality, otae1_0.minimum_cardinality, otae1_0.name, "
        "otae1_0.object_type_id, otae1_0.ota_position, otae1_0.options, otae1_0.pending, "
        "otae1_0.reference_object_type_id, otae1_0.reference_type_id, "
        "otae1_0.regex_validation, otae1_0.removable, otae1_0.sequential_id, "
        "otae1_0.suffix, otae1_0.summable, otae1_0.type, otae1_0.type_value, "
        "otae1_0.unique_attribute, otae1_0.updated, otae1_0.workspace_id"
    )


def json_pairs_from_doc(doc: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if not isinstance(doc, dict):
        return pairs
    for key, values in doc.items():
        if isinstance(values, list):
            for value in values:
                pairs.append((str(key), str(value)))
        elif values is not None:
            pairs.append((str(key), str(values)))
    return pairs


def json_condition(alias: str, pairs: list[tuple[str, str]]) -> str:
    terms = []
    for key, value in pairs:
        terms.append(
            f"JSON_CONTAINS({alias}.other_values_indexed, "
            f"JSON_SET(CAST('{{}}' AS JSON), '$.\"{key}\"', JSON_ARRAY({sql_quote(value)})))"
        )
    return "(" + " OR ".join(terms) + ")"


def sample_json_groups(cur, workspaces: list[str]) -> dict[tuple[str, bytes], list[tuple[str, str]]]:
    groups: dict[tuple[str, bytes], list[tuple[str, str]]] = defaultdict(list)
    for ws in workspaces:
        rows = fetchall(
            cur,
            """
            SELECT workspace_id, obj_type_id, other_values_indexed
            FROM obj_new
            WHERE workspace_id=%s
              AND other_values_indexed IS NOT NULL
              AND JSON_LENGTH(other_values_indexed) > 0
            LIMIT 400
            """,
            (ws,),
        )
        for r in rows:
            doc = r["other_values_indexed"]
            if isinstance(doc, str):
                try:
                    doc = json.loads(doc)
                except json.JSONDecodeError:
                    continue
            for pair in json_pairs_from_doc(doc):
                key = (r["workspace_id"], r["obj_type_id"])
                if pair not in groups[key]:
                    groups[key].append(pair)
    return groups


def pick_json_group(groups: dict[tuple[str, bytes], list[tuple[str, str]]], min_pairs: int, offset: int = 0):
    candidates = [(k, v) for k, v in groups.items() if len(v) >= min_pairs]
    candidates.sort(key=lambda kv: (kv[0][0], kv[0][1].hex()))
    if not candidates:
        return None
    return candidates[offset % len(candidates)]


def build_queries(cur, sample_limit: int = 10) -> dict[int, list[dict[str, Any]]]:
    workspaces = top_workspaces(cur, max(sample_limit * 3, 10))
    variants: dict[int, list[dict[str, Any]]] = defaultdict(list)

    # Query #2: relationship object_id IN (...)
    for i, ws in enumerate(workspaces[:sample_limit], 1):
        rows = fetchall(
            cur,
            """
            SELECT object_id, COUNT(*) cnt
            FROM obj_relationship_new
            WHERE workspace_id=%s
            GROUP BY object_id
            ORDER BY cnt DESC
            LIMIT 25
            """,
            (ws,),
        )
        ids = [r["object_id"] for r in rows]
        if ids:
            variants[2].append(
                {
                    "sample": f"s{i}",
                    "params": f"workspace={ws}, object_ids={len(ids)}",
                    "sql": f"SELECT {relation_select()} FROM obj_relationship_new obj_relationship "
                    f"WHERE obj_relationship.object_id IN ({', '.join(bin_hex(x) for x in ids)})",
                }
            )

    # Query #9: relationship object_id point lookup.
    rows = fetchall(
        cur,
        f"""
        SELECT object_id, workspace_id, COUNT(*) cnt
        FROM obj_relationship_new
        GROUP BY object_id, workspace_id
        ORDER BY cnt DESC
        LIMIT {sample_limit}
        """,
    )
    for i, r in enumerate(rows, 1):
        variants[9].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, object_id={uuid_hex(r['object_id'])}",
                "sql": f"SELECT {relation_select()} FROM obj_relationship_new obj_relationship "
                f"WHERE obj_relationship.object_id = {bin_hex(r['object_id'])}",
            }
        )

    # Query #4: label-ordered numeric_value_5 IS NOT NULL with five obj types.
    for i, ws in enumerate(workspaces[:sample_limit], 1):
        types = object_types(cur, ws, "numeric_value_5 IS NOT NULL", 5)
        if len(types) >= 2:
            ors = " OR ".join(
                f"(o.numeric_value_5 IS NOT NULL AND o.obj_type_id = {bin_hex(t)})" for t in types
            )
            variants[4].append(
                {
                    "sample": f"s{i}",
                    "params": f"workspace={ws}, obj_types={len(types)}",
                    "sql": f"SELECT o.sequential_id, o.label FROM obj_new o "
                    f"WHERE o.workspace_id={sql_quote(ws)} AND "
                    f"(o.obj_type_id IN ({obj_type_list(types)}) AND ({ors})) "
                    f"ORDER BY o.label ASC LIMIT 1000 OFFSET 0",
                }
            )

    # JSON queries #5/#10/#17/#23.
    json_groups = sample_json_groups(cur, workspaces)
    for i in range(sample_limit):
        group = pick_json_group(json_groups, 4, i)
        if not group:
            break
        (ws, obj_type), pairs = group
        cond4 = json_condition("o", pairs[:4])
        cond8 = json_condition("o", pairs[:8] if len(pairs) >= 8 else pairs[:4])
        variants[10].append(
            {
                "sample": f"s{i+1}",
                "params": f"workspace={ws}, obj_type={uuid_hex(obj_type)}, json_terms=4",
                "sql": f"SELECT o.* FROM obj_new o WHERE o.workspace_id={sql_quote(ws)} "
                f"AND (o.obj_type_id={bin_hex(obj_type)} AND {cond4} AND o.obj_type_id={bin_hex(obj_type)}) "
                f"ORDER BY o.label ASC LIMIT 1000 OFFSET 0",
            }
        )
        variants[23].append(
            {
                "sample": f"s{i+1}",
                "params": f"workspace={ws}, obj_type={uuid_hex(obj_type)}, json_terms=4",
                "sql": f"SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id={sql_quote(ws)} "
                f"AND (o.obj_type_id={bin_hex(obj_type)} AND {cond4} AND o.obj_type_id={bin_hex(obj_type)}) "
                f"ORDER BY o.label ASC LIMIT 1000 OFFSET 0",
            }
        )
        variants[17].append(
            {
                "sample": f"s{i+1}",
                "params": f"workspace={ws}, obj_type={uuid_hex(obj_type)}, json_terms={len(pairs[:8])}",
                "sql": f"SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id={sql_quote(ws)} "
                f"AND (o.obj_type_id={bin_hex(obj_type)} AND {cond8} AND o.obj_type_id={bin_hex(obj_type)}) "
                f"ORDER BY o.label ASC LIMIT 1000 OFFSET 0",
            }
        )
    # Query #5 uses five obj_type branches, when enough JSON groups exist for a workspace.
    by_ws: dict[str, list[tuple[bytes, list[tuple[str, str]]]]] = defaultdict(list)
    for (ws, obj_type), pairs in json_groups.items():
        if len(pairs) >= 1:
            by_ws[ws].append((obj_type, pairs))
    eligible_json_workspaces = [w for w in workspaces if len(by_ws[w]) >= 2]
    for i in range(sample_limit):
        if not eligible_json_workspaces:
            break
        ws = eligible_json_workspaces[i % len(eligible_json_workspaces)]
        branch_groups = by_ws[ws]
        rotate = (i // len(eligible_json_workspaces)) % len(branch_groups)
        rotated_groups = branch_groups[rotate:] + branch_groups[:rotate]
        branches = []
        for obj_type, pairs in rotated_groups[:5]:
            branches.append(
                f"({json_condition('o', pairs[:4])} AND o.obj_type_id={bin_hex(obj_type)})"
            )
        types = [x[0] for x in rotated_groups[:5]]
        variants[5].append(
            {
                "sample": f"s{i+1}",
                "params": f"workspace={ws}, obj_type_branches={len(branches)}",
                "sql": f"SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id={sql_quote(ws)} "
                f"AND (o.obj_type_id IN ({obj_type_list(types)}) AND ({' OR '.join(branches)})) "
                f"ORDER BY o.label ASC LIMIT 1000 OFFSET 0",
            }
        )

    # Query #8: FTS + selective post filters.
    for i, ws in enumerate(workspaces[:sample_limit], 1):
        rows = fetchall(
            cur,
            """
            SELECT workspace_id, obj_type_id, text_value_23, text_value_22, text_value_9,
                   numeric_value_3, numeric_value_1
            FROM obj_new
            WHERE workspace_id=%s
              AND text_value_23 IS NOT NULL AND text_value_23 != ''
              AND text_value_22 IS NOT NULL AND text_value_22 != ''
              AND text_value_9 IS NOT NULL AND text_value_9 != ''
              AND numeric_value_3 IS NOT NULL
              AND numeric_value_1 IS NOT NULL
            LIMIT 1
            """,
            (ws,),
        )
        if rows:
            r = rows[0]
            types = object_types(cur, ws, "1=1", 5)
            phrase = f'"{str(r["text_value_22"]).replace(chr(34), "")}"'
            variants[8].append(
                {
                    "sample": f"s{i}",
                    "params": f"workspace={ws}, obj_type={uuid_hex(r['obj_type_id'])}, text_value_22={safe_label(r['text_value_22'])}",
                    "sql": f"SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id={sql_quote(ws)} "
                    f"AND (o.obj_type_id IN ({obj_type_list(types)}) "
                    f"AND (o.obj_type_id = {bin_hex(r['obj_type_id'])}) "
                    f"AND (o.text_value_23 = {sql_quote(r['text_value_23'])} "
                    f"AND MATCH(o.text_value_22) AGAINST ({sql_quote(phrase)} IN BOOLEAN MODE) "
                    f"AND o.text_value_22 LIKE {sql_quote('%' + str(r['text_value_22']) + '%')} "
                    f"AND o.text_value_22 != '' "
                    f"AND o.text_value_9 = {sql_quote(r['text_value_9'])} "
                    f"AND (o.numeric_value_3 = {sql_quote(r['numeric_value_3'])} "
                    f"OR o.numeric_value_1 = {sql_quote(r['numeric_value_1'])}))) "
                    f"ORDER BY o.label ASC LIMIT 1000 OFFSET 0",
                }
            )

    # Query #6: wide fetch by id IN (...).
    for i, ws in enumerate(workspaces[:sample_limit], 1):
        rows = fetchall(cur, "SELECT id FROM obj_new WHERE workspace_id=%s LIMIT 50", (ws,))
        ids = [r["id"] for r in rows]
        if ids:
            variants[6].append(
                {
                    "sample": f"s{i}",
                    "params": f"workspace={ws}, ids={len(ids)}",
                    "sql": f"SELECT obj.* FROM obj_new obj WHERE obj.id IN ({', '.join(bin_hex(x) for x in ids)})",
                }
            )

    # Query #11: wide fetch by workspace + sequential_id.
    rows = fetchall(
        cur,
        f"""
        SELECT workspace_id, sequential_id
        FROM obj_new
        WHERE sequential_id IS NOT NULL
        ORDER BY workspace_id, sequential_id
        LIMIT {sample_limit}
        """,
    )
    for i, r in enumerate(rows, 1):
        variants[11].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, sequential_id={r['sequential_id']}",
                "sql": f"SELECT obj.* FROM obj_new obj WHERE obj.workspace_id={sql_quote(r['workspace_id'])} "
                f"AND obj.sequential_id = {sql_quote(r['sequential_id'])}",
            }
        )

    # Query #22: wide fetch by workspace + partition + sequential_id IN (...).
    for i, ws in enumerate(workspaces[:sample_limit], 1):
        rows = fetchall(
            cur,
            """
            SELECT partition_id, sequential_id
            FROM obj_new
            WHERE workspace_id=%s AND sequential_id IS NOT NULL
            ORDER BY sequential_id
            LIMIT 20
            """,
            (ws,),
        )
        if rows:
            part = rows[0]["partition_id"]
            seqs = [r["sequential_id"] for r in rows]
            variants[22].append(
                {
                    "sample": f"s{i}",
                    "params": f"workspace={ws}, partition_id={part}, sequential_ids={len(seqs)}",
                    "sql": f"SELECT obj.* FROM obj_new obj WHERE obj.workspace_id={sql_quote(ws)} "
                    f"AND obj.partition_id={sql_quote(part)} "
                    f"AND obj.sequential_id IN ({', '.join(sql_quote(s) for s in seqs)})",
                }
            )

    # Metadata queries #7/#13/#18/#20.
    rows = fetchall(
        cur,
        f"""
        SELECT workspace_id, object_type_id, COUNT(*) cnt
        FROM obj_type_attr
        WHERE is_deleted=0
        GROUP BY workspace_id, object_type_id
        ORDER BY cnt DESC
        LIMIT {sample_limit}
        """,
    )
    for i, r in enumerate(rows, 1):
        variants[7].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, obj_type={uuid_hex(r['object_type_id'])}",
                "sql": f"SELECT {metadata_ota_select()} FROM obj_type_attr otae1_0 "
                f"LEFT JOIN obj_type ot1_0 ON ot1_0.id = otae1_0.object_type_id "
                f"AND ot1_0.workspace_id = {sql_quote(r['workspace_id'])} "
                f"AND ot1_0.is_deleted = 0 AND ot1_0.is_deleted = 0 "
                f"WHERE otae1_0.workspace_id = {sql_quote(r['workspace_id'])} "
                f"AND otae1_0.is_deleted = 0 AND ot1_0.id IN ({bin_hex(r['object_type_id'])})",
            }
        )
    for i, ws in enumerate(workspaces[:sample_limit], 1):
        rows = fetchall(
            cur,
            """
            SELECT id
            FROM obj_type
            WHERE workspace_id=%s AND is_deleted=0
            LIMIT 5
            """,
            (ws,),
        )
        ids = [r["id"] for r in rows]
        if ids:
            variants[13].append(
                {
                    "sample": f"s{i}",
                    "params": f"workspace={ws}, obj_types={len(ids)}",
                    "sql": f"SELECT {metadata_ota_select()} FROM obj_type_attr otae1_0 "
                    f"LEFT JOIN obj_type ot1_0 ON ot1_0.id = otae1_0.object_type_id "
                    f"AND ot1_0.workspace_id = {sql_quote(ws)} "
                    f"AND ot1_0.is_deleted = 0 AND ot1_0.is_deleted = 0 "
                    f"WHERE otae1_0.workspace_id = {sql_quote(ws)} "
                    f"AND otae1_0.is_deleted = 0 AND ot1_0.id IN ({', '.join(bin_hex(x) for x in ids)})",
                }
            )
            variants[18].append(
                {
                    "sample": f"s{i}",
                    "params": f"workspace={ws}, obj_types={len(ids)}",
                    "sql": f"SELECT ote1_0.* FROM obj_type ote1_0 WHERE ote1_0.workspace_id={sql_quote(ws)} "
                    f"AND ote1_0.is_deleted = 0 AND ote1_0.id IN ({', '.join(bin_hex(x) for x in ids)})",
                }
            )
    rows = fetchall(
        cur,
        f"""
        SELECT workspace_id, sequential_id
        FROM obj_type_attr
        WHERE is_deleted=0 AND sequential_id IS NOT NULL
        ORDER BY workspace_id, sequential_id
        LIMIT {sample_limit}
        """,
    )
    for i, r in enumerate(rows, 1):
        variants[20].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, sequential_id={r['sequential_id']}",
                "sql": f"SELECT {metadata_ota_select()} FROM obj_type_attr otae1_0 "
                f"WHERE otae1_0.workspace_id = {sql_quote(r['workspace_id'])} "
                f"AND otae1_0.is_deleted = 0 AND otae1_0.sequential_id = {sql_quote(r['sequential_id'])}",
            }
        )

    # text_value_7 lower-index fanout queries #14/#15/#16/#19/#25.
    text_rows = fetchall(
        cur,
        f"""
        SELECT workspace_id, obj_type_id, text_value_7, text_value_8, text_value_16
        FROM obj_new
        WHERE text_value_7 IS NOT NULL AND text_value_7 != ''
          AND text_value_8 IS NOT NULL AND text_value_8 != ''
          AND text_value_16 IS NOT NULL AND text_value_16 != ''
        LIMIT {sample_limit}
        """,
    )
    for i, r in enumerate(text_rows, 1):
        exclude = "__not_" + str(r["text_value_7"]).lower() + "__"
        common = (
            f"o.workspace_id={sql_quote(r['workspace_id'])} "
            f"AND (o.obj_type_id={bin_hex(r['obj_type_id'])} "
            f"AND ((NOT o.text_value_7_lower = {sql_quote(exclude)} OR LOWER(o.text_value_7) = '􏿿') "
            f"AND o.text_value_7 IS NOT NULL AND o.obj_type_id={bin_hex(r['obj_type_id'])}) "
        )
        variants[14].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, obj_type={uuid_hex(r['obj_type_id'])}, text_value_8={safe_label(r['text_value_8'])}",
                "sql": f"SELECT o.sequential_id, o.text_value_8 FROM obj_new o WHERE {common} "
                f"AND (o.text_value_8={sql_quote(r['text_value_8'])} AND o.obj_type_id={bin_hex(r['obj_type_id'])})) "
                f"ORDER BY o.text_value_8 ASC LIMIT 1000 OFFSET 0",
            }
        )
        variants[15].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, obj_type={uuid_hex(r['obj_type_id'])}, text_value_8={safe_label(r['text_value_8'])}",
                "sql": f"SELECT o.sequential_id, o.text_value_1 FROM obj_new o WHERE {common} "
                f"AND (o.text_value_8={sql_quote(r['text_value_8'])} AND o.obj_type_id={bin_hex(r['obj_type_id'])})) "
                f"ORDER BY o.text_value_1 ASC LIMIT 1000 OFFSET 0",
            }
        )
        variants[25].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, obj_type={uuid_hex(r['obj_type_id'])}, text_value_8={safe_label(r['text_value_8'])}",
                "sql": f"SELECT o.* FROM obj_new o WHERE {common} "
                f"AND (o.text_value_8={sql_quote(r['text_value_8'])} AND o.obj_type_id={bin_hex(r['obj_type_id'])})) "
                f"ORDER BY o.text_value_1 ASC LIMIT 1000 OFFSET 0",
            }
        )
        variants[19].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, obj_type={uuid_hex(r['obj_type_id'])}, text_value_16={safe_label(r['text_value_16'])}",
                "sql": f"SELECT o.sequential_id, o.numeric_value_4 FROM obj_new o WHERE {common} "
                f"AND (o.text_value_16={sql_quote(r['text_value_16'])} AND o.obj_type_id={bin_hex(r['obj_type_id'])})) "
                f"ORDER BY o.numeric_value_4 ASC LIMIT 1000 OFFSET 0",
            }
        )
        variants[16].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, obj_type={uuid_hex(r['obj_type_id'])}, text_value_16={safe_label(r['text_value_16'])}",
                "sql": f"SELECT o.* FROM obj_new o WHERE {common} "
                f"AND (o.text_value_16={sql_quote(r['text_value_16'])} AND o.obj_type_id={bin_hex(r['obj_type_id'])})) "
                f"ORDER BY o.numeric_value_4 ASC LIMIT 1000 OFFSET 0",
            }
        )

    # Query #21 relationship exists depth 1.
    rel_rows = fetchall(
        cur,
        f"""
        SELECT r.workspace_id, r.object_id, r.referenced_object_id
        FROM obj_relationship_new r
        LIMIT {sample_limit * 10}
        """,
    )
    count = 0
    for r in rel_rows:
        pair = fetchall(
            cur,
            """
            SELECT o.workspace_id, o.obj_type_id, o.text_value_24, subo1.text_value_8
            FROM obj_new o
            JOIN obj_new subo1
              ON subo1.id=%s AND subo1.workspace_id=%s
            WHERE o.id=%s AND o.workspace_id=%s
              AND o.text_value_24 IS NOT NULL AND o.text_value_24 != ''
              AND subo1.text_value_8 IS NOT NULL AND subo1.text_value_8 != ''
            LIMIT 1
            """,
            (r["object_id"], r["workspace_id"], r["referenced_object_id"], r["workspace_id"]),
        )
        if not pair:
            continue
        p = pair[0]
        types = object_types(cur, p["workspace_id"], "1=1", 5)
        count += 1
        variants[21].append(
            {
                "sample": f"s{count}",
                "params": f"workspace={p['workspace_id']}, text_value_24={safe_label(p['text_value_24'])}, sub_text_value_8={safe_label(p['text_value_8'])}",
                "sql": f"SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id={sql_quote(p['workspace_id'])} "
                f"AND (o.obj_type_id IN ({obj_type_list(types)}) "
                f"AND (o.text_value_24={sql_quote(p['text_value_24'])} AND o.obj_type_id IN ({obj_type_list(types)})) "
                f"AND EXISTS (SELECT 1 FROM obj_relationship_new subr "
                f"INNER JOIN obj_new subo1 ON subr.object_id=subo1.id AND subo1.obj_type_id IN ({obj_type_list(types)}) "
                f"WHERE o.id=subr.referenced_object_id AND subo1.workspace_id={sql_quote(p['workspace_id'])} "
                f"AND subo1.text_value_8={sql_quote(p['text_value_8'])})) "
                f"ORDER BY o.label ASC LIMIT 1000 OFFSET 0",
            }
        )
        if count >= sample_limit:
            break

    # Query #24 relationship exists depth 3.
    chain_rows = fetchall(
        cur,
        f"""
        SELECT r0.workspace_id, r0.object_id AS start_id, o3.label AS label3
        FROM obj_relationship_new r0
        JOIN obj_relationship_new r1 ON r1.object_id = r0.referenced_object_id AND r1.workspace_id = r0.workspace_id
        JOIN obj_relationship_new r2 ON r2.object_id = r1.referenced_object_id AND r2.workspace_id = r0.workspace_id
        JOIN obj_new o3 ON o3.id = r2.referenced_object_id AND o3.workspace_id = r0.workspace_id
        WHERE o3.label IS NOT NULL
        LIMIT {sample_limit}
        """,
    )
    for i, r in enumerate(chain_rows, 1):
        types = object_types(cur, r["workspace_id"], "1=1", 5)
        variants[24].append(
            {
                "sample": f"s{i}",
                "params": f"workspace={r['workspace_id']}, depth3_label={safe_label(r['label3'])}",
                "sql": f"SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id={sql_quote(r['workspace_id'])} "
                f"AND (o.obj_type_id IN ({obj_type_list(types)}) AND EXISTS ("
                f"SELECT 1 FROM obj_relationship_new subr INNER JOIN obj_new subo1 "
                f"ON subr.referenced_object_id=subo1.id WHERE o.id=subr.object_id "
                f"AND subo1.workspace_id={sql_quote(r['workspace_id'])} AND EXISTS ("
                f"SELECT 1 FROM obj_relationship_new subr1 INNER JOIN obj_new subo2 "
                f"ON subr1.referenced_object_id=subo2.id WHERE subo1.id=subr1.object_id "
                f"AND subo2.workspace_id={sql_quote(r['workspace_id'])} AND EXISTS ("
                f"SELECT 1 FROM obj_relationship_new subr2 INNER JOIN obj_new subo3 "
                f"ON subr2.referenced_object_id=subo3.id WHERE subo2.id=subr2.object_id "
                f"AND subo3.workspace_id={sql_quote(r['workspace_id'])} AND subo3.label={sql_quote(r['label3'])})))) "
                f"ORDER BY o.label ASC LIMIT 1000 OFFSET 0",
            }
        )

    return variants


def run_sql(conn, sql: str) -> tuple[str, int | None, float | None, str | None]:
    cur = conn.cursor()
    try:
        start = time.perf_counter()
        cur.execute(sql)
        rows = cur.fetchall()
        elapsed = (time.perf_counter() - start) * 1000
        return "ok", len(rows), elapsed, None
    except Exception as exc:  # noqa: BLE001
        return "error", None, None, f"{type(exc).__name__}: {exc}"
    finally:
        cur.close()


def summarize(samples: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [s for s in samples if s["status"] == "ok"]
    lat = [s["latency_ms"] for s in ok if s.get("latency_ms") is not None]
    rows = [s["rows"] for s in ok if s.get("rows") is not None]
    return {
        "runs": len(samples),
        "ok": len(ok),
        "errors": len(samples) - len(ok),
        "avg_ms": round(statistics.mean(lat), 1) if lat else None,
        "p50_ms": round(statistics.median(lat), 1) if lat else None,
        "min_ms": round(min(lat), 1) if lat else None,
        "max_ms": round(max(lat), 1) if lat else None,
        "avg_rows": round(statistics.mean(rows), 1) if rows else None,
    }


def ratio_text(measured: float | None, source: float | None) -> str:
    if measured is None or source is None or source == 0:
        return "n/a"
    ratio = measured / source
    if ratio >= 1:
        return f"{ratio:.2f}x source"
    return f"{1 / ratio:.2f}x faster"


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    idx = min(len(values) - 1, max(0, math.ceil(len(values) * p) - 1))
    return values[idx]


def fmt_num(value: Any, digits: int = 1) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return str(value)


def summarize_latencies(latencies: list[float], rows: list[int]) -> dict[str, Any]:
    return {
        "avg_ms": round(statistics.mean(latencies), 1) if latencies else None,
        "p50_ms": round(statistics.median(latencies), 1) if latencies else None,
        "p95_ms": round(percentile(latencies, 0.95), 1) if latencies else None,
        "max_ms": round(max(latencies), 1) if latencies else None,
        "avg_rows": round(statistics.mean(rows), 1) if rows else None,
    }


def run_worker(worker_id: int, qid: int, samples: list[dict[str, Any]], deadline: float, args: argparse.Namespace):
    conn = connect(args)
    ops: list[dict[str, Any]] = []
    sample_idx = 0
    try:
        while time.time() < deadline:
            sample = samples[sample_idx % len(samples)]
            sample_idx += 1
            status, rows, elapsed, error = run_sql(conn, sample["sql"])
            ops.append(
                {
                    "worker_id": worker_id,
                    "query_id": qid,
                    "sample": sample["sample"],
                    "status": status,
                    "rows": rows,
                    "latency_ms": round(elapsed, 1) if elapsed is not None else None,
                    "error": error,
                }
            )
    finally:
        conn.close()
    return ops


def run_concurrency_level(
    level: int,
    variants: dict[int, list[dict[str, Any]]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    runnable = sorted(qid for qid, samples in variants.items() if qid not in MISSING_TABLES and samples)
    assignments = [runnable[i % len(runnable)] for i in range(level)]
    start_wall = dt.datetime.now(dt.timezone.utc)
    start_epoch = time.time()
    deadline = start_epoch + args.concurrency_duration
    print(f"concurrency={level} start runnable_query_classes={len(runnable)} duration_s={args.concurrency_duration}")
    all_ops: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=level) as pool:
        futures = [
            pool.submit(run_worker, i + 1, qid, variants[qid][: args.samples], deadline, args)
            for i, qid in enumerate(assignments)
        ]
        for fut in concurrent.futures.as_completed(futures):
            all_ops.extend(fut.result())
    end_epoch = time.time()
    end_wall = dt.datetime.now(dt.timezone.utc)
    ok = [op for op in all_ops if op["status"] == "ok"]
    latencies = [op["latency_ms"] for op in ok if op.get("latency_ms") is not None]
    rows = [op["rows"] for op in ok if op.get("rows") is not None]
    by_query: dict[str, dict[str, Any]] = {}
    for qid in runnable:
        qops = [op for op in all_ops if op["query_id"] == qid]
        qok = [op for op in qops if op["status"] == "ok"]
        qlat = [op["latency_ms"] for op in qok if op.get("latency_ms") is not None]
        qrows = [op["rows"] for op in qok if op.get("rows") is not None]
        qsummary = summarize_latencies(qlat, qrows)
        qsummary.update(
            {
                "ops": len(qops),
                "ok": len(qok),
                "errors": len(qops) - len(qok),
                "workers": assignments.count(qid),
            }
        )
        by_query[str(qid)] = qsummary
    summary = summarize_latencies(latencies, rows)
    summary.update(
        {
            "concurrency": level,
            "query_classes": len(runnable),
            "ops": len(all_ops),
            "ok": len(ok),
            "errors": len(all_ops) - len(ok),
            "elapsed_s": round(end_epoch - start_epoch, 1),
            "qps": round(len(ok) / (end_epoch - start_epoch), 2) if end_epoch > start_epoch else None,
        }
    )
    print(
        f"concurrency={level} done ops={summary['ops']} ok={summary['ok']} "
        f"errors={summary['errors']} qps={summary['qps']} avg_ms={summary['avg_ms']}"
    )
    return {
        "concurrency": level,
        "duration_s": args.concurrency_duration,
        "start_time": start_wall.isoformat(),
        "end_time": end_wall.isoformat(),
        "start_epoch": start_epoch,
        "end_epoch": end_epoch,
        "worker_assignment": {str(qid): assignments.count(qid) for qid in runnable},
        "summary": summary,
        "by_query": by_query,
    }


def prometheus_query_range(url: str, query: str, start: float, end: float, step: int = 15) -> list[float]:
    params = urllib.parse.urlencode({"query": query, "start": start, "end": end, "step": step})
    with urllib.request.urlopen(f"{url.rstrip('/')}/api/v1/query_range?{params}", timeout=30) as resp:
        payload = json.loads(resp.read())
    if payload.get("status") != "success":
        raise RuntimeError(payload)
    values: list[float] = []
    for series in payload["data"]["result"]:
        for _, value in series.get("values", []):
            try:
                values.append(float(value))
            except (TypeError, ValueError):
                continue
    return values


def collect_prometheus_metrics(url: str, start: float, end: float) -> dict[str, dict[str, Any]]:
    queries = {
        "tidb": {
            "cpu_query": 'sum(rate(process_cpu_seconds_total{component="tidb"}[1m]))',
            "mem_query": 'sum(process_resident_memory_bytes{component="tidb"})',
            "capacity_cores": 48,
            "replicas": 3,
        },
        "tikv": {
            "cpu_query": 'sum(rate(process_cpu_seconds_total{component="tikv"}[1m]))',
            "mem_query": 'sum(process_resident_memory_bytes{component="tikv"})',
            "capacity_cores": 64,
            "replicas": 4,
        },
        "tiflash": {
            "cpu_query": "sum(rate(tiflash_proxy_process_cpu_seconds_total[1m]))",
            "mem_query": 'sum(tiflash_process_rss_by_type_bytes{component="tiflash"})',
            "capacity_cores": 96,
            "replicas": 6,
            "cpu_note": "TiFlash proxy process CPU metric",
        },
    }
    out: dict[str, dict[str, Any]] = {}
    for component, spec in queries.items():
        cpu_values = prometheus_query_range(url, spec["cpu_query"], start, end)
        mem_values = prometheus_query_range(url, spec["mem_query"], start, end)
        cpu_avg = statistics.mean(cpu_values) if cpu_values else None
        cpu_max = max(cpu_values) if cpu_values else None
        mem_avg = statistics.mean(mem_values) / (1024**3) if mem_values else None
        mem_max = max(mem_values) / (1024**3) if mem_values else None
        capacity = spec["capacity_cores"]
        out[component] = {
            "replicas": spec["replicas"],
            "cpu_avg_cores": round(cpu_avg, 2) if cpu_avg is not None else None,
            "cpu_max_cores": round(cpu_max, 2) if cpu_max is not None else None,
            "cpu_max_pct": round(cpu_max / capacity * 100, 1) if cpu_max is not None else None,
            "mem_avg_gib": round(mem_avg, 2) if mem_avg is not None else None,
            "mem_max_gib": round(mem_max, 2) if mem_max is not None else None,
            "note": spec.get("cpu_note", ""),
        }
    return out


def run_concurrency_suite(variants: dict[int, list[dict[str, Any]]], args: argparse.Namespace) -> list[dict[str, Any]]:
    runs = []
    for level in args.concurrency_levels:
        run = run_concurrency_level(level, variants, args)
        if args.prometheus_url:
            try:
                run["metrics"] = collect_prometheus_metrics(args.prometheus_url, run["start_epoch"], run["end_epoch"])
            except Exception as exc:  # noqa: BLE001
                run["metrics_error"] = f"{type(exc).__name__}: {exc}"
        runs.append(run)
        if args.concurrency_pause > 0:
            time.sleep(args.concurrency_pause)
    return runs


def write_markdown(results: dict[str, Any], out: Path) -> None:
    metrics = results["source_metrics"]
    lines = [
        "# jsm_assets4 Query Sample Run vs PingCAP Report",
        "",
        f"Run time: {results['run_time']}",
        "",
        "Source report: `/Users/jin/Downloads/full_report_for_pingcap.md`.",
        "",
        "Notes:",
        "- The source report contains normalized SQL with placeholders, so this run materialized representative parameter sets from `jsm_assets4`.",
        f"- Each runnable query uses up to {results['sample_limit']} sampled parameter sets. Rows are fetched to the client; latency is client-observed SQL execution plus fetch time.",
        "- Wide object queries are represented as `SELECT o.*` / `SELECT obj.*`; predicate, ordering, and limit shape are preserved.",
        "- Queries whose referenced tables are absent from `jsm_assets4` are marked skipped.",
        f"- Grafana: [{results['grafana_url']}]({results['grafana_url']})",
        "",
        "## Summary",
        "",
        "| Query | Source avg | Source max | Source rows avg | Samples | OK | Run rows avg | jsm_assets4 avg | jsm_assets4 p50 | jsm_assets4 max | Comparison | Status |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for qid in range(1, 26):
        q = results["queries"].get(str(qid), {})
        src = metrics.get(qid) or metrics.get(str(qid), {})
        summary = q.get("summary", {})
        source_avg_ms = ms_from_source(src.get("source_avg_latency", ""))
        comp = ratio_text(summary.get("avg_ms"), source_avg_ms)
        status = q.get("status", "")
        lines.append(
            f"| {qid} | {src.get('source_avg_latency','')} | "
            f"{src.get('source_max_latency','')} | {src.get('source_avg_rows','')} | "
            f"{summary.get('runs',0)} | {summary.get('ok',0)} | "
            f"{summary.get('avg_rows','')} | {summary.get('avg_ms','')} | {summary.get('p50_ms','')} | "
            f"{summary.get('max_ms','')} | {comp} | {status} |"
        )
    lines += ["", "## Skipped Queries", ""]
    skipped = [q for q in results["queries"].values() if q["status"] == "skipped"]
    if skipped:
        for q in skipped:
            lines.append(f"- Query #{q['query_id']}: {q['reason']}.")
    else:
        lines.append("- None.")
    if results.get("concurrency_runs"):
        lines += [
            "",
            "## Concurrent Runs",
            "",
            "Worker assignment is per query class. When concurrency equals the runnable query class count, each query class gets one worker. When concurrency is higher, workers are assigned round-robin across the runnable query classes.",
            "",
            "| Concurrency | Query classes | Duration s | Ops | OK | Errors | QPS | Avg ms | P95 ms | Max ms |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for run in results["concurrency_runs"]:
            s = run["summary"]
            lines.append(
                f"| {s['concurrency']} | {s['query_classes']} | {run['duration_s']} | {s['ops']} | {s['ok']} | "
                f"{s['errors']} | {s['qps']} | {s['avg_ms']} | {s['p95_ms']} | {s['max_ms']} |"
            )
        lines += ["", "### Grafana / Prometheus Resource Metrics", ""]
        lines.append(
            "CPU and memory values below are pulled from the Grafana Prometheus datasource for each run window. CPU capacity percentage assumes the current scale: TiDB 3 x 16 cores, TiKV 4 x 16 cores, TiFlash 6 x 16 cores."
        )
        lines.append("")
        for run in results["concurrency_runs"]:
            start_ms = int(run["start_epoch"] * 1000)
            end_ms = int(run["end_epoch"] * 1000)
            grafana_link = f"{results['grafana_url']}?from={start_ms}&to={end_ms}"
            lines += [
                f"#### Concurrency {run['concurrency']}",
                "",
                f"- Window: `{run['start_time']}` to `{run['end_time']}`",
                f"- Grafana time range: [{grafana_link}]({grafana_link})",
            ]
            if run.get("metrics_error"):
                lines.append(f"- Metrics error: `{run['metrics_error']}`")
                lines.append("")
                continue
            lines += [
                "",
                "| Component | Replicas | CPU avg cores | CPU max cores | CPU max % capacity | Mem avg GiB | Mem max GiB | Note |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
            ]
            for component in ["tidb", "tikv", "tiflash"]:
                m = run.get("metrics", {}).get(component, {})
                lines.append(
                    f"| {component} | {m.get('replicas','')} | {fmt_num(m.get('cpu_avg_cores'), 2)} | "
                    f"{fmt_num(m.get('cpu_max_cores'), 2)} | {fmt_num(m.get('cpu_max_pct'), 1)}% | "
                    f"{fmt_num(m.get('mem_avg_gib'), 2)} | {fmt_num(m.get('mem_max_gib'), 2)} | {m.get('note','')} |"
                )
            lines += [
                "",
                "Grafana panel screenshots:",
                "",
                "<table>",
                "<tr>",
                f"<td width=\"50%\"><strong>TiDB CPU/Memory</strong><br><img src=\"images/jsm_assets4_concurrency{run['concurrency']}_tidb_cpu_memory.png\" alt=\"TiDB CPU/Memory - concurrency {run['concurrency']}\" /></td>",
                f"<td width=\"50%\"><strong>TiKV CPU/Memory</strong><br><img src=\"images/jsm_assets4_concurrency{run['concurrency']}_tikv_cpu_memory.png\" alt=\"TiKV CPU/Memory - concurrency {run['concurrency']}\" /></td>",
                "</tr>",
                "<tr>",
                f"<td width=\"50%\"><strong>TiFlash CPU</strong><br><img src=\"images/jsm_assets4_concurrency{run['concurrency']}_tiflash_cpu.png\" alt=\"TiFlash CPU - concurrency {run['concurrency']}\" /></td>",
                f"<td width=\"50%\"><strong>TiFlash Memory</strong><br><img src=\"images/jsm_assets4_concurrency{run['concurrency']}_tiflash_memory.png\" alt=\"TiFlash Memory - concurrency {run['concurrency']}\" /></td>",
                "</tr>",
                "</table>",
                "",
                "| Query | Ops | OK | Errors | Source avg | Source max | Source rows avg | Run avg ms | vs source avg | P95 ms | Max ms | Run rows avg |",
                "|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|",
            ]
            for qid in sorted(run["by_query"], key=lambda x: int(x)):
                q = run["by_query"][qid]
                src = metrics.get(int(qid)) or metrics.get(str(qid), {})
                source_avg = src.get("source_avg_latency", "")
                source_max = src.get("source_max_latency", "")
                source_rows = src.get("source_avg_rows", "")
                comp = ratio_text(q.get("avg_ms"), ms_from_source(source_avg))
                lines.append(
                    f"| {qid} | {q['ops']} | {q['ok']} | {q['errors']} | "
                    f"{source_avg} | {source_max} | {source_rows} | {q['avg_ms']} | {comp} | "
                    f"{q['p95_ms']} | {q['max_ms']} | {q['avg_rows']} |"
                )
            lines.append("")
    lines += ["", "## Per-Query Details", ""]
    for qid in range(1, 26):
        q = results["queries"].get(str(qid))
        if not q:
            continue
        src = metrics.get(qid) or metrics.get(str(qid), {})
        lines += [
            f"### Query #{qid}",
            "",
            f"- Source tables: `{src.get('tables','')}`",
            f"- Source avg/max latency: `{src.get('source_avg_latency','')}` / `{src.get('source_max_latency','')}`",
            f"- Source avg rows/cop tasks: `{src.get('source_avg_rows','')}` / `{src.get('source_avg_cop_tasks','')}`",
            f"- Status: `{q['status']}`",
        ]
        if q["status"] == "skipped":
            lines.append(f"- Reason: {q['reason']}")
            lines.append("")
            continue
        lines += [
            "",
            "| Sample | Params | Rows | Latency ms | Status | Error |",
            "|---|---|---:|---:|---|---|",
        ]
        for s in q["samples"]:
            lines.append(
                f"| {s['sample']} | {s.get('params','')} | {s.get('rows','')} | "
                f"{s.get('latency_ms','')} | {s['status']} | {s.get('error') or ''} |"
            )
        if q["samples"]:
            lines += [
                "",
                "<details>",
                "<summary>Representative SQL</summary>",
                "",
                "```sql",
                q["samples"][0]["sql"].strip().rstrip(";") + ";",
                "```",
                "",
                "</details>",
                "",
            ]
    out.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=14000)
    parser.add_argument("--user", default="root")
    parser.add_argument("--read-timeout", type=int, default=120)
    parser.add_argument("--limit-query", type=int, default=0)
    parser.add_argument("--samples", type=int, default=10)
    parser.add_argument("--concurrency-levels", type=int, nargs="*", default=[])
    parser.add_argument("--concurrency-duration", type=int, default=120)
    parser.add_argument("--concurrency-pause", type=int, default=30)
    parser.add_argument("--prometheus-url", default="http://127.0.0.1:19090")
    parser.add_argument("--grafana-url", default=DEFAULT_GRAFANA_URL)
    args = parser.parse_args()

    report_text = REPORT.read_text()
    source_metrics = parse_source_metrics(report_text)

    conn = connect(args)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        variants = build_queries(cur, args.samples)
    finally:
        cur.close()

    run_conn = connect(args)
    queries: dict[str, Any] = {}
    try:
        for qid in range(1, 26):
            if qid in MISSING_TABLES:
                queries[str(qid)] = {
                    "query_id": qid,
                    "status": "skipped",
                    "reason": MISSING_TABLES[qid],
                    "samples": [],
                    "summary": summarize([]),
                }
                continue
            samples = variants.get(qid, [])
            if args.limit_query and qid != args.limit_query:
                continue
            if not samples:
                queries[str(qid)] = {
                    "query_id": qid,
                    "status": "skipped",
                    "reason": "no sample parameters could be materialized from jsm_assets4",
                    "samples": [],
                    "summary": summarize([]),
                }
                continue
            executed = []
            for sample in samples[: args.samples]:
                status, rows, elapsed, error = run_sql(run_conn, sample["sql"])
                item = dict(sample)
                item.update(
                    {
                        "status": status,
                        "rows": rows,
                        "latency_ms": round(elapsed, 1) if elapsed is not None else None,
                        "error": error,
                    }
                )
                executed.append(item)
                print(f"query={qid} sample={sample['sample']} status={status} rows={rows} latency_ms={item['latency_ms']} error={error}")
            queries[str(qid)] = {
                "query_id": qid,
                "status": "ok" if all(s["status"] == "ok" for s in executed) else "partial",
                "samples": executed,
                "summary": summarize(executed),
            }
    finally:
        run_conn.close()
        conn.close()

    concurrency_runs = []
    if args.concurrency_levels and not args.limit_query:
        concurrency_runs = run_concurrency_suite(variants, args)

    results = {
        "run_time": dt.datetime.now(dt.timezone.utc).isoformat(),
        "database": DB,
        "source_report": str(REPORT),
        "sample_limit": args.samples,
        "grafana_url": args.grafana_url,
        "source_metrics": source_metrics,
        "queries": queries,
        "concurrency_runs": concurrency_runs,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(results, indent=2, default=str))
    write_markdown(results, OUT_MD)
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
