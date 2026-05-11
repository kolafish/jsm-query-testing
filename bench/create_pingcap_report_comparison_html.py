#!/usr/bin/env python3
"""Build a self-contained HTML report comparing customer and current query runs."""

from __future__ import annotations

import datetime as dt
import html
import json
import math
import re
from pathlib import Path
from typing import Any

from compare_pingcap_report_plans import main_difference, plan_one_liner, status_label


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_JSON = REPO_ROOT / "bench/results/pingcap_report_jsm_assets4_query_sample_comparison.json"
PLAN_JSON = REPO_ROOT / "bench/results/pingcap_report_plan_comparison.json"
OUT_HTML = REPO_ROOT / "pingcap_report_query_comparison.html"
OVERVIEW_CONCURRENCY = 66


def current_grafana_url(sampled: dict[str, Any]) -> str:
    readme = REPO_ROOT / "README.md"
    if readme.exists():
        match = re.search(r"https?://[^\s)\]]+:3000", readme.read_text())
        if match:
            return match.group(0)
    return sampled.get("grafana_url", "-")


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def compact(value: Any, limit: int = 180) -> str:
    text = re.sub(r"\s+", " ", "" if value is None else str(value)).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def parse_ms(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "")
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*ms", text)
    if match:
        return float(match.group(1))
    match = re.search(r"^-?\d+(?:\.\d+)?$", text.strip())
    return float(match.group(0)) if match else None


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip().strip("`")
    match = re.search(r"^-?\d+(?:\.\d+)?$", text)
    return float(match.group(0)) if match else None


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * pct) - 1)
    return ordered[min(index, len(ordered) - 1)]


def fmt_ms(value: float | None) -> str:
    if value is None:
        return "-"
    if value >= 1000:
        return f"{value / 1000:.2f}s"
    return f"{value:.1f}ms"


def fmt_num(value: float | int | None, digits: int = 1) -> str:
    if value is None:
        return "-"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.{digits}f}"
    return f"{int(value):,}"


def status_class(status: str) -> str:
    return {
        "match": "ok",
        "compatible": "warn",
        "mismatch": "bad",
        "pending": "muted",
        "error": "bad",
    }.get(status, "muted")


def speed_summary(benchmark_avg: float | None, source_avg: float | None) -> tuple[str, str]:
    if benchmark_avg is None or source_avg in (None, 0):
        return "-", "muted"
    ratio = benchmark_avg / source_avg
    if ratio < 0.8:
        return f"压测快 {1 / ratio:.2f}x", "fast"
    if ratio > 1.25:
        return f"客户快 {ratio:.2f}x", "slow"
    return f"接近 {ratio:.2f}x", "even"


def display_difference(text: str) -> str:
    replacements = {
        "当前没有 sampled SQL": "压测环境没有 sampled SQL",
        "current EXPLAIN": "EXPLAIN",
        "当前 optimizer": "压测环境 optimizer",
        "当前主要生成": "压测环境主要生成",
        "当前选择": "压测环境选择",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def format_sql(sql: str) -> str:
    text = re.sub(r"\s+", " ", str(sql or "").strip())
    if not text:
        return ""
    keyword_patterns = [
        (r"\bUNION\s+DISTINCT\b", "\nUNION DISTINCT\n"),
        (r"\bUNION\s+ALL\b", "\nUNION ALL\n"),
        (r"\bUNION\b", "\nUNION\n"),
        (r"\bSELECT\b", "SELECT"),
        (r"\bFROM\b", "\nFROM"),
        (r"\bLEFT\s+JOIN\b", "\nLEFT JOIN"),
        (r"\bRIGHT\s+JOIN\b", "\nRIGHT JOIN"),
        (r"\bINNER\s+JOIN\b", "\nINNER JOIN"),
        (r"\bJOIN\b", "\nJOIN"),
        (r"\bON\b", "\n  ON"),
        (r"\bWHERE\b", "\nWHERE"),
        (r"\bGROUP\s+BY\b", "\nGROUP BY"),
        (r"\bORDER\s+BY\b", "\nORDER BY"),
        (r"\bLIMIT\b", "\nLIMIT"),
        (r"\bOFFSET\b", "\nOFFSET"),
    ]
    for pattern, replacement in keyword_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\s*,\s*", ",\n  ", text)
    text = re.sub(r"\s+\bAND\b\s+", "\n  AND ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+\bOR\b\s+", "\n  OR ", text, flags=re.IGNORECASE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def source_metric(item: dict[str, Any], sampled: dict[str, Any], key: str) -> Any:
    qid = str(item["query_id"])
    return (
        sampled.get("source_metrics", {}).get(qid, {}).get(key)
        or item.get("source", {}).get("metrics", {}).get(key)
    )


def sample_latencies(query: dict[str, Any]) -> list[float]:
    values = []
    for sample in query.get("samples", []):
        if sample.get("status") == "ok" and sample.get("latency_ms") is not None:
            values.append(float(sample["latency_ms"]))
    return values


def concurrency_rows(qid: str, runs: list[dict[str, Any]]) -> str:
    rows = []
    for run in runs:
        by_query = run.get("by_query", {}).get(qid)
        if not by_query:
            continue
        rows.append(
            "<tr>"
            f"<td>{esc(run.get('concurrency'))}</td>"
            f"<td>{fmt_num(by_query.get('ops'))}</td>"
            f"<td>{fmt_ms(parse_ms(by_query.get('avg_ms')))}</td>"
            f"<td>{fmt_ms(parse_ms(by_query.get('p95_ms')))}</td>"
            f"<td>{fmt_ms(parse_ms(by_query.get('max_ms')))}</td>"
            f"<td>{fmt_num(parse_number(by_query.get('avg_rows')))}</td>"
            f"<td>{fmt_num(by_query.get('errors'))}</td>"
            "</tr>"
        )
    if not rows:
        return "<p class=\"muted-text\">这条 query 没有并发压测数据。</p>"
    return (
        "<table class=\"mini\"><thead><tr>"
        "<th>并发</th><th>Ops</th><th>Avg</th><th>P95</th><th>Max</th><th>Avg rows</th><th>Errors</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def sample_rows(query: dict[str, Any]) -> str:
    rows = []
    for sample in query.get("samples", []):
        status = sample.get("status", "-")
        rows.append(
            "<tr>"
            f"<td>{esc(sample.get('sample'))}</td>"
            f"<td>{esc(compact(sample.get('params'), 120))}</td>"
            f"<td><span class=\"badge {status_class('match' if status == 'ok' else 'error')}\">{esc(status)}</span></td>"
            f"<td>{fmt_num(sample.get('rows'))}</td>"
            f"<td>{fmt_ms(parse_ms(sample.get('latency_ms')))}</td>"
            f"<td>{esc(compact(sample.get('error'), 120))}</td>"
            "</tr>"
        )
    if not rows:
        return "<p class=\"muted-text\">没有可用样本。</p>"
    return (
        "<table class=\"mini\"><thead><tr>"
        "<th>Sample</th><th>Params</th><th>Status</th><th>Rows</th><th>Latency</th><th>Error</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def render_metric_cards(sampled: dict[str, Any], plan: dict[str, Any]) -> str:
    plan_summary = plan.get("summary", {})
    cards = [
        ("数据库", sampled.get("database", "jsm_assets4")),
        ("样本数", sampled.get("sample_limit", "-")),
        (
            "Plan 结论",
            ", ".join(
                f"{status_label(status)} {plan_summary.get(status, 0)}"
                for status in ["match", "compatible", "mismatch", "error", "pending"]
            ),
        ),
        ("Grafana", current_grafana_url(sampled)),
    ]
    for run in sampled.get("concurrency_runs", []):
        summary = run.get("summary", {})
        cards.append(
            (
                f"并发 {run.get('concurrency')}",
                f"QPS {summary.get('qps', '-')}, avg {fmt_ms(parse_ms(summary.get('avg_ms')))}, "
                f"p95 {fmt_ms(parse_ms(summary.get('p95_ms')))}, errors {summary.get('errors', '-')}",
            )
        )
    rendered = []
    for title, value in cards:
        if title == "Grafana" and str(value).startswith("http"):
            value_html = f"<a href=\"{esc(value)}\">{esc(value)}</a>"
        else:
            value_html = esc(value)
        rendered.append(f"<section class=\"card\"><div>{esc(title)}</div><strong>{value_html}</strong></section>")
    return "".join(rendered)


def render(sampled: dict[str, Any], plan: dict[str, Any]) -> str:
    rows_html: list[str] = []
    detail_html: list[str] = []
    concurrency_runs = sampled.get("concurrency_runs", [])
    overview_run = next(
        (run for run in concurrency_runs if run.get("concurrency") == OVERVIEW_CONCURRENCY),
        {},
    )
    overview_by_query = overview_run.get("by_query", {})

    for item in plan.get("items", []):
        qid = str(item["query_id"])
        query = sampled.get("queries", {}).get(qid, {})
        summary = query.get("summary") or {}
        latencies = sample_latencies(query)
        source_avg = parse_ms(source_metric(item, sampled, "source_avg_latency") or source_metric(item, sampled, "Avg latency"))
        source_max = parse_ms(source_metric(item, sampled, "source_max_latency") or source_metric(item, sampled, "Max latency"))
        source_rows = parse_number(source_metric(item, sampled, "source_avg_rows") or source_metric(item, sampled, "Avg result rows"))
        sample_avg = parse_ms(summary.get("avg_ms"))
        sample_p95 = percentile(latencies, 0.95)
        sample_max = parse_ms(summary.get("max_ms"))
        sample_rows_avg = parse_number(summary.get("avg_rows"))
        benchmark = overview_by_query.get(qid, {})
        benchmark_avg = parse_ms(benchmark.get("avg_ms"))
        benchmark_p95 = parse_ms(benchmark.get("p95_ms"))
        benchmark_max = parse_ms(benchmark.get("max_ms"))
        benchmark_rows = parse_number(benchmark.get("avg_rows"))
        speed_text, speed_class = speed_summary(benchmark_avg, source_avg)
        comparison = item.get("comparison", {})
        plan_status = comparison.get("status", "pending")
        diff = display_difference(main_difference(item))
        current_rep = item.get("representative_current") or {}
        source = item.get("source", {})
        source_plan_line = plan_one_liner(source.get("signature"))
        current_plan_line = (
            plan_one_liner(current_rep.get("signature"))
            if current_rep.get("status") == "ok"
            else compact(current_rep.get("error") or query.get("reason") or "current plan not captured", 220)
        )
        open_detail = plan_status in {"mismatch", "error"} or speed_class in {"fast", "slow"}

        rows_html.append(
            "<tr>"
            f"<td><a href=\"#q{qid}\">Q{qid}</a></td>"
            f"<td><span class=\"speed {speed_class}\">{esc(speed_text)}</span></td>"
            f"<td><span class=\"badge {status_class(plan_status)}\">{esc(status_label(plan_status))}</span></td>"
            f"<td>{fmt_ms(source_avg)}</td>"
            f"<td>{fmt_ms(source_max)}</td>"
            f"<td>{fmt_num(source_rows)}</td>"
            f"<td>{fmt_ms(benchmark_avg)}</td>"
            f"<td>{fmt_ms(benchmark_max)}</td>"
            f"<td>{fmt_num(benchmark_rows)}</td>"
            f"<td class=\"diff-cell\">{esc(compact(diff, 180))}</td>"
            "</tr>"
        )

        source_sql = source.get("sample_sql") or source.get("normalized_sql") or ""
        current_sql = current_rep.get("sql") or next(
            (sample.get("sql", "") for sample in query.get("samples", []) if sample.get("sql")),
            "",
        )
        source_raw_plan = source.get("raw_plan") or ""
        current_raw_plan = current_rep.get("raw_plan") or current_rep.get("error") or query.get("reason") or ""

        detail_html.append(
            f"<details class=\"query-detail\" id=\"q{qid}\" {'open' if open_detail else ''}>"
            f"<summary><span>Q{qid}: {esc(source.get('pattern') or source.get('group') or '-')}</span>"
            f"<span class=\"badge {status_class(plan_status)}\">{esc(status_label(plan_status))}</span>"
            f"<span class=\"speed {speed_class}\">{esc(speed_text)}</span></summary>"
            "<div class=\"detail-grid\">"
            "<section><h3>指标</h3>"
            "<table class=\"mini\"><tbody>"
            f"<tr><th>客户 avg / max / avg rows</th><td>{fmt_ms(source_avg)} / {fmt_ms(source_max)} / {fmt_num(source_rows)}</td></tr>"
            f"<tr><th>压测 {OVERVIEW_CONCURRENCY} 并发 avg / p95 / max / avg rows</th><td>{fmt_ms(benchmark_avg)} / {fmt_ms(benchmark_p95)} / {fmt_ms(benchmark_max)} / {fmt_num(benchmark_rows)}</td></tr>"
            f"<tr><th>单 query 样本 avg / p95 / max / avg rows</th><td>{fmt_ms(sample_avg)} / {fmt_ms(sample_p95)} / {fmt_ms(sample_max)} / {fmt_num(sample_rows_avg)}</td></tr>"
            f"<tr><th>快慢判断</th><td>{esc(speed_text)}（压测 {OVERVIEW_CONCURRENCY} 并发 vs 客户 avg）</td></tr>"
            f"<tr><th>Plan 结论</th><td>{esc(status_label(plan_status))}: {esc(diff)}</td></tr>"
            "</tbody></table>"
            "</section>"
            "<section><h3>并发压测</h3>"
            f"{concurrency_rows(qid, concurrency_runs)}"
            "</section>"
            "</div>"
            "<section><h3>样本执行</h3>"
            f"{sample_rows(query)}"
            "</section>"
            "<section><h3>SQL</h3>"
            "<div class=\"split\">"
            f"<div><h4>客户报告 SQL</h4><pre class=\"sql\">{esc(format_sql(source_sql))}</pre></div>"
            f"<div><h4>压测环境 SQL</h4><pre class=\"sql\">{esc(format_sql(current_sql))}</pre></div>"
            "</div>"
            "</section>"
            "<section><h3>Plan 摘要</h3>"
            "<div class=\"split\">"
            f"<div><h4>客户报告</h4><p>{esc(source_plan_line)}</p></div>"
            f"<div><h4>压测环境</h4><p>{esc(current_plan_line)}</p></div>"
            "</div>"
            "</section>"
            "<section><h3>完整执行计划（客户文档 vs 压测环境）</h3>"
            "<div class=\"split plans\">"
            f"<div><h4>客户文档执行计划</h4><pre>{esc(source_raw_plan)}</pre></div>"
            f"<div><h4>压测环境执行计划</h4><pre>{esc(current_raw_plan)}</pre></div>"
            "</div>"
            "</section>"
            "</details>"
        )

    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    source_report = plan.get("source_report") or sampled.get("source_report") or "-"
    css = """
body { margin: 0; font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #17202a; background: #f6f4ef; }
header { padding: 28px 34px 18px; background: #1b2a2f; color: #f8f4ea; }
h1 { margin: 0 0 8px; font-size: 28px; letter-spacing: -0.02em; }
h2 { margin: 28px 0 12px; font-size: 20px; }
h3 { margin: 18px 0 8px; font-size: 15px; }
h4 { margin: 0 0 8px; font-size: 13px; color: #40545a; }
a { color: #0b6b72; text-decoration: none; }
main { padding: 22px 34px 42px; }
.note { max-width: 1180px; color: #5c6b70; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; margin: 18px 0 22px; }
.card { background: #fffaf0; border: 1px solid #dccfb7; border-radius: 12px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(30, 40, 45, 0.08); }
.card div { color: #68787d; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
.card strong { display: block; margin-top: 5px; overflow-wrap: anywhere; }
.table-wrap { overflow: auto; max-height: 76vh; border: 1px solid #d4c8b2; border-radius: 12px; background: white; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px 10px; border-bottom: 1px solid #eadfcd; vertical-align: top; }
th { position: sticky; top: 0; z-index: 1; background: #efe4d0; text-align: left; white-space: nowrap; }
td { white-space: nowrap; }
td:last-child { white-space: normal; min-width: 280px; }
td.diff-cell { white-space: normal; min-width: 360px; max-width: 560px; overflow-wrap: anywhere; word-break: break-word; }
.mini th { position: static; background: #f1eadf; }
.mini td, .mini th { white-space: normal; font-size: 13px; }
.badge, .speed { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 650; white-space: nowrap; }
.ok { background: #dff1df; color: #22612c; }
.warn { background: #fff0c2; color: #7b5510; }
.bad { background: #ffd9d4; color: #8c2c21; }
.muted { background: #e5e7e8; color: #5f676b; }
.fast { background: #d8f2ed; color: #10665b; }
.slow { background: #ffe0d5; color: #8a321f; }
.even { background: #e7e4ff; color: #4d477c; }
.muted-text { color: #68787d; }
.query-detail { margin: 14px 0; background: #fffefa; border: 1px solid #d6cbb8; border-radius: 12px; }
.query-detail summary { cursor: pointer; padding: 12px 14px; display: flex; align-items: center; gap: 10px; border-radius: 12px; }
.query-detail summary span:first-child { font-weight: 700; margin-right: auto; }
.query-detail[open] summary { border-bottom: 1px solid #eadfcd; border-radius: 12px 12px 0 0; background: #f7efe1; }
.query-detail section, .detail-grid { padding: 0 14px 14px; }
.detail-grid { display: grid; grid-template-columns: minmax(360px, 1fr) minmax(360px, 1fr); gap: 16px; }
.split { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
pre { margin: 0; padding: 12px; max-height: 520px; overflow: auto; background: #10242a; color: #ecf6f2; border-radius: 10px; font: 12px/1.45 "SFMono-Regular", Consolas, monospace; white-space: pre; }
pre.sql { white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word; }
.plans pre { max-height: 680px; }
@media (max-width: 980px) { .split, .detail-grid { grid-template-columns: 1fr; } main, header { padding-left: 16px; padding-right: 16px; } }
"""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PingCAP Report vs jsm_assets4 Query Comparison</title>
<style>{css}</style>
</head>
<body>
<header>
<h1>PingCAP Report vs jsm_assets4 Query Comparison</h1>
<p>Generated at {esc(generated_at)}. Source report: <code>{esc(source_report)}</code>.</p>
</header>
<main>
<p class="note">这个页面把客户报告里的 25 条 query 与 `jsm_assets4` 的压测结果放在一起。主表的“压测”列使用 {OVERVIEW_CONCURRENCY} 并发那组 per-query-pool 结果；单 query 样本和 p95 放在逐条详情里。</p>
<div class="cards">{render_metric_cards(sampled, plan)}</div>
<h2>总览表</h2>
<div class="table-wrap">
<table>
<thead><tr>
<th>Query</th><th>谁快谁慢</th><th>Plan 是否一致</th>
<th>客户 Avg</th><th>客户 Max</th><th>客户 Avg rows</th>
<th>压测 Avg</th><th>压测 Max</th><th>压测 Avg rows</th>
<th>主要差异</th>
</tr></thead>
<tbody>{''.join(rows_html)}</tbody>
</table>
</div>
<h2>逐条详情</h2>
{''.join(detail_html)}
</main>
</body>
</html>
"""


def main() -> None:
    sampled = json.loads(SAMPLE_JSON.read_text())
    plan = json.loads(PLAN_JSON.read_text())
    OUT_HTML.write_text(render(sampled, plan))
    print(f"wrote {OUT_HTML}")


if __name__ == "__main__":
    main()
