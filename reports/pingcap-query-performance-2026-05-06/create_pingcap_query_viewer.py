#!/usr/bin/env python3
"""Generate a readable HTML viewer for a TiDB query performance markdown report."""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


METRIC_ORDER = [
    "Digest",
    "Tables",
    "Indexes used",
    "Exec count",
    "Avg latency",
    "Max latency",
    "Max cop wait",
    "Avg cop tasks",
    "Avg TiKV CPU",
    "Avg result rows",
    "Avg memory",
    "Max memory",
    "Plan in binding",
    "First seen",
    "Last seen",
]


GROUP_NAMES = {
    "A": "JSON_CONTAINS post-filter on obj_new",
    "B": "IndexLookUp fanout on obj_new",
    "C": "obj_relationship_new IN()/point lookups",
    "D": "7-table schema metadata join",
    "E": "FTS cross-storage post-filter",
}


@dataclass
class AntiPattern:
    pattern: str
    group: str
    queries: list[int]
    combined_load: str
    severity: str


@dataclass
class PlanRow:
    node: str
    raw_node: str
    depth: int
    task: str
    est_rows: str
    act_rows: str
    operator_info: str
    execution_info: str
    memory: str
    disk: str
    time: str = ""
    cop_tasks: str = ""
    process_keys: str = ""
    wait: str = ""


@dataclass
class QueryBlock:
    qid: int
    title: str
    group: str = ""
    load: str = ""
    metrics: dict[str, str] = field(default_factory=dict)
    normalized_sql: str = ""
    sample_sql: str = ""
    raw_plan: str = ""
    plan_rows: list[PlanRow] = field(default_factory=list)
    pattern: str = ""
    severity: str = ""
    slow: bool = False
    avg_latency_ms: float = 0
    max_latency_ms: float = 0
    load_pct: float = 0


def parse_duration_to_ms(value: str) -> float:
    value = value.strip()
    if not value:
        return 0
    total = 0.0
    for number, unit in re.findall(r"([0-9]+(?:\.[0-9]+)?)(us|µs|ms|s|m|h)", value):
        n = float(number)
        if unit in {"us", "µs"}:
            total += n / 1000
        elif unit == "ms":
            total += n
        elif unit == "s":
            total += n * 1000
        elif unit == "m":
            total += n * 60 * 1000
        elif unit == "h":
            total += n * 60 * 60 * 1000
    if total:
        return total
    try:
        return float(value)
    except ValueError:
        return 0


def parse_count(value: str) -> float:
    value = value.replace(",", "").strip()
    match = re.search(r"-?[0-9]+(?:\.[0-9]+)?", value)
    return float(match.group(0)) if match else 0


def format_duration(value: str) -> str:
    ms = parse_duration_to_ms(value)
    if not value or ms <= 0:
        return value or "n/a"
    if ms >= 60 * 1000:
        return f"{ms / 60000:.1f}m"
    if ms >= 1000:
        return f"{ms / 1000:.1f}s"
    if ms >= 1:
        return f"{ms:.1f}ms"
    return value


def compact(text: str, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def read_fenced_after(section: str, marker: str) -> str:
    idx = section.find(marker)
    if idx < 0:
        return ""
    after = section[idx + len(marker) :]
    match = re.search(r"```(?:\w+)?\n(.*?)\n```", after, flags=re.S)
    return match.group(1).strip("\n") if match else ""


def parse_metrics(section: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|$", line)
        if not match:
            continue
        key = match.group(1).strip()
        value = match.group(2).strip()
        if key in {"Metric", "--------"}:
            continue
        metrics[key] = re.sub(r"`", "", value)
    return metrics


def clean_plan_node(raw: str) -> tuple[str, int]:
    raw = raw.rstrip()
    prefix = re.match(r"^([\s│├└─]*)", raw).group(1)
    depth = prefix.count("  ") + prefix.count("│ ") + prefix.count("├") + prefix.count("└")
    node = re.sub(r"^[\s│├└─]+", "", raw).strip()
    return node or raw.strip(), max(depth, 0)


def first_match(text: str, patterns: Iterable[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            for group in match.groups():
                if group:
                    return group.strip()
    return ""


def parse_plan(raw_plan: str) -> list[PlanRow]:
    rows: list[PlanRow] = []
    for line in raw_plan.splitlines():
        if not line.strip() or line.lstrip().startswith("id"):
            continue
        parts = line.split("\t")
        while parts and parts[0].strip() == "":
            parts.pop(0)
        parts = [part.strip() for part in parts]
        if len(parts) < 8:
            # Fallback for plans copied with spaces instead of tabs.
            parts = re.split(r"\s{2,}", line.strip(), maxsplit=7)
        if len(parts) < 8:
            continue
        node, depth = clean_plan_node(parts[0])
        execution_info = parts[5]
        row = PlanRow(
            node=node,
            raw_node=parts[0],
            depth=depth,
            task=parts[1],
            est_rows=parts[2],
            operator_info=parts[3],
            act_rows=parts[4],
            execution_info=execution_info,
            memory=parts[6],
            disk=parts[7],
            time=first_match(execution_info, [r"(?:^|[, ])time:([^,}]+)", r"(?:^|[, ])total_time:([^,}]+)"]),
            cop_tasks=first_match(execution_info, [r"cop_task:\s*\{num:\s*([^,}]+)", r"VersionedCop:\{num_rpc:([^,}]+)", r"Cop:\{num_rpc:([^,}]+)"]),
            process_keys=first_match(execution_info, [r"total_process_keys:\s*([^,}]+)", r"proc_keys:\s*([^,}]+)"]),
            wait=first_match(execution_info, [r"tot_wait:\s*([^,}]+)", r"total_wait_time:\s*([^,}]+)", r"wait_table_lookup_resp:\s*([^,}]+)"]),
        )
        rows.append(row)
    return rows


def parse_anti_patterns(markdown: str) -> tuple[list[AntiPattern], dict[int, AntiPattern]]:
    patterns: list[AntiPattern] = []
    query_map: dict[int, AntiPattern] = {}
    capture = False
    for line in markdown.splitlines():
        if line.startswith("## Anti-Pattern Summary"):
            capture = True
            continue
        if capture and line.startswith("---"):
            break
        if not capture or not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 5 or cells[0] in {"Pattern", "---------"}:
            continue
        query_ids = [int(n) for n in re.findall(r"#(\d+)", cells[2])]
        pattern = AntiPattern(
            pattern=cells[0],
            group=cells[1],
            queries=query_ids,
            combined_load=cells[3],
            severity=cells[4],
        )
        patterns.append(pattern)
        for qid in query_ids:
            query_map[qid] = pattern
    return patterns, query_map


def parse_queries(markdown: str, anti_map: dict[int, AntiPattern]) -> list[QueryBlock]:
    matches = list(re.finditer(r"^(?:####|###)\s+Query #(\d+).*?$", markdown, flags=re.M))
    queries: list[QueryBlock] = []
    for index, match in enumerate(matches):
        qid = int(match.group(1))
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        section = markdown[start:end]
        title = match.group(0).lstrip("# ").strip()
        group_match = re.search(r"\(Group ([A-Z])\)", title)
        load_match = re.search(r"([0-9.]+)%\s+cluster load", title)
        anti = anti_map.get(qid)
        group = group_match.group(1) if group_match else (anti.group if anti else "")
        query = QueryBlock(
            qid=qid,
            title=title,
            group=group,
            load=load_match.group(1) + "%" if load_match else "",
            metrics=parse_metrics(section),
            normalized_sql=read_fenced_after(section, "**Normalized Query"),
            sample_sql=read_fenced_after(section, "**Sample Query"),
            raw_plan=read_fenced_after(section, "**Execution Plan**"),
            pattern=anti.pattern if anti else "",
            severity=anti.severity if anti else "",
        )
        query.plan_rows = parse_plan(query.raw_plan)
        query.avg_latency_ms = parse_duration_to_ms(query.metrics.get("Avg latency", ""))
        query.max_latency_ms = parse_duration_to_ms(query.metrics.get("Max latency", ""))
        query.load_pct = parse_count(query.load)
        query.slow = (
            query.avg_latency_ms >= 1000
            or query.max_latency_ms >= 5000
            or parse_duration_to_ms(query.metrics.get("Max cop wait", "")) >= 5000
            or query.severity in {"CRITICAL", "HIGH"}
        )
        queries.append(query)
    return queries


def extract_report_meta(markdown: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in markdown.splitlines()[:25]:
        match = re.match(r"^\*\*([^:]+):\*\*\s*(.*?)(?:\s{2,})?$", line)
        if match:
            meta[match.group(1)] = match.group(2)
    return meta


def render_metric_grid(query: QueryBlock) -> str:
    rows = []
    for key in METRIC_ORDER:
        if key not in query.metrics:
            continue
        value = query.metrics[key]
        rows.append(
            f"""
            <div class="metric">
              <div class="metric-label">{html.escape(key)}</div>
              <div class="metric-value" title="{html.escape(value)}">{html.escape(value)}</div>
            </div>
            """
        )
    return "\n".join(rows)


def task_class(task: str) -> str:
    task = task.lower()
    if "tiflash" in task:
        return "task-tiflash"
    if "tikv" in task:
        return "task-tikv"
    if "tici" in task:
        return "task-tici"
    return "task-root"


def heat_class(row: PlanRow) -> str:
    time_ms = parse_duration_to_ms(row.time)
    wait_ms = parse_duration_to_ms(row.wait)
    keys = parse_count(row.process_keys)
    if wait_ms >= 5000 or time_ms >= 10000 or keys >= 100000:
        return "hot"
    if wait_ms >= 1000 or time_ms >= 1000 or keys >= 10000:
        return "warm"
    return ""


def render_plan_table(query: QueryBlock) -> str:
    if not query.plan_rows:
        return '<div class="empty">No parsed plan rows found. Use raw plan below.</div>'
    body = []
    for index, row in enumerate(query.plan_rows):
        indent = max(row.depth, 0) * 18
        detail_id = f"q{query.qid}-row{index}"
        summary = compact(row.operator_info, 220)
        row_json = html.escape(
            json.dumps(
                {
                    "operatorInfo": row.operator_info,
                    "executionInfo": row.execution_info,
                    "memory": row.memory,
                    "disk": row.disk,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        body.append(
            f"""
            <tr class="{heat_class(row)}">
              <td class="op-cell">
                <button class="row-toggle" data-target="{detail_id}" title="展开完整 execution info">+</button>
                <span class="tree-spacer" style="width:{indent}px"></span>
                <span class="op-name">{html.escape(row.node)}</span>
              </td>
              <td><span class="task-badge {task_class(row.task)}">{html.escape(row.task)}</span></td>
              <td class="num">{html.escape(row.est_rows)}</td>
              <td class="num">{html.escape(row.act_rows)}</td>
              <td class="num strong">{html.escape(row.time or "-")}</td>
              <td class="num">{html.escape(row.cop_tasks or "-")}</td>
              <td class="num">{html.escape(row.process_keys or "-")}</td>
              <td class="num strong">{html.escape(row.wait or "-")}</td>
              <td class="operator-info" title="{html.escape(row.operator_info)}">{html.escape(summary)}</td>
            </tr>
            <tr id="{detail_id}" class="plan-detail-row hidden">
              <td colspan="9"><pre>{row_json}</pre></td>
            </tr>
            """
        )
    return f"""
      <div class="plan-wrap">
        <table class="plan-table">
          <thead>
            <tr>
              <th>Operator</th>
              <th>Task</th>
              <th>Est</th>
              <th>Act</th>
              <th>Time</th>
              <th>Cop</th>
              <th>Keys</th>
              <th>Wait</th>
              <th>Operator info</th>
            </tr>
          </thead>
          <tbody>
            {''.join(body)}
          </tbody>
        </table>
      </div>
    """


def render_query_card(query: QueryBlock) -> str:
    severity = query.severity or ("SLOW" if query.slow else "NORMAL")
    group_label = f"Group {query.group}: {GROUP_NAMES.get(query.group, '')}" if query.group else "Other top query"
    normalized_sql = html.escape(query.normalized_sql)
    sample_sql = html.escape(query.sample_sql)
    raw_plan = html.escape(query.raw_plan)
    pattern = (
        f'<div class="pattern"><span>Pattern</span>{html.escape(query.pattern)}</div>'
        if query.pattern
        else ""
    )
    return f"""
    <article class="query-card" id="query-{query.qid}" data-slow="{str(query.slow).lower()}" data-group="{html.escape(query.group or 'other')}" data-qid="{query.qid}">
      <header class="query-header">
        <div>
          <div class="eyebrow">{html.escape(group_label)}</div>
          <h2>Query #{query.qid}</h2>
        </div>
        <div class="badges">
          <span class="badge severity-{html.escape(severity.lower())}">{html.escape(severity)}</span>
          <span class="badge">{html.escape(query.load or 'load n/a')}</span>
          <span class="badge">avg {html.escape(format_duration(query.metrics.get('Avg latency', '')))}</span>
          <span class="badge">max {html.escape(format_duration(query.metrics.get('Max latency', '')))}</span>
          <span class="badge">cop wait {html.escape(format_duration(query.metrics.get('Max cop wait', '')))}</span>
        </div>
      </header>
      {pattern}
      <section class="metrics-grid">{render_metric_grid(query)}</section>
      <section class="block">
        <div class="block-title">Readable Execution Plan</div>
        {render_plan_table(query)}
      </section>
      <details class="block">
        <summary>Normalized SQL</summary>
        <pre class="sql sql-wrap">{normalized_sql}</pre>
      </details>
      <details class="block">
        <summary>Sample SQL</summary>
        <pre class="sql">{sample_sql}</pre>
      </details>
      <details class="block">
        <summary>Raw Execution Plan</summary>
        <pre class="raw-plan">{raw_plan}</pre>
      </details>
    </article>
    """


def render_group_summary(patterns: list[AntiPattern]) -> str:
    cards = []
    for pattern in patterns:
        query_links = " ".join(
            f'<a href="#query-{qid}">#{qid}</a>' for qid in pattern.queries
        )
        cards.append(
            f"""
            <div class="summary-card severity-{html.escape(pattern.severity.lower())}">
              <div class="summary-top">
                <span>{html.escape(pattern.severity)}</span>
                <strong>Group {html.escape(pattern.group)}</strong>
              </div>
              <div class="summary-pattern">{html.escape(pattern.pattern)}</div>
              <div class="summary-bottom">
                <span>{query_links}</span>
                <span>{html.escape(pattern.combined_load)}</span>
              </div>
            </div>
            """
        )
    return "\n".join(cards)


def render_sidebar(queries: list[QueryBlock]) -> str:
    items = []
    for query in sorted(queries, key=lambda q: (not q.slow, -q.avg_latency_ms, q.qid)):
        status = query.severity or ("SLOW" if query.slow else "OK")
        label = f"#{query.qid} {format_duration(query.metrics.get('Avg latency', ''))}"
        items.append(
            f"""
            <a class="nav-item" href="#query-{query.qid}" data-slow="{str(query.slow).lower()}" data-group="{html.escape(query.group or 'other')}">
              <span>{html.escape(label)}</span>
              <small>{html.escape(status)}</small>
            </a>
            """
        )
    return "\n".join(items)


def build_html(markdown: str, source: Path) -> str:
    patterns, anti_map = parse_anti_patterns(markdown)
    queries = parse_queries(markdown, anti_map)
    meta = extract_report_meta(markdown)
    slow_count = sum(1 for query in queries if query.slow)
    top25_load = sum(query.load_pct for query in queries)
    max_avg = max((query.avg_latency_ms for query in queries), default=0)
    max_avg_query = max(queries, key=lambda q: q.avg_latency_ms, default=None)
    source_label = html.escape(source.name)
    generated_note = "Generated from the markdown report. Raw SQL and raw plans are preserved in collapsible sections."

    query_cards = "\n".join(
        render_query_card(query)
        for query in sorted(queries, key=lambda q: (not q.slow, -q.avg_latency_ms, -q.load_pct, q.qid))
    )

    meta_rows = "\n".join(
        f"<div><span>{html.escape(key)}</span><strong>{html.escape(value)}</strong></div>"
        for key, value in meta.items()
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PingCAP Query Plan Viewer</title>
  <style>
    :root {{
      --bg: #f7f8fb;
      --panel: #ffffff;
      --panel-soft: #f1f5f9;
      --text: #17202a;
      --muted: #64748b;
      --line: #d9e0ea;
      --line-strong: #bdc8d7;
      --blue: #2563eb;
      --green: #087f5b;
      --orange: #b45309;
      --red: #b42318;
      --violet: #6d28d9;
      --shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-size: 14px;
      line-height: 1.45;
    }}
    a {{ color: inherit; text-decoration: none; }}
    .layout {{
      display: grid;
      grid-template-columns: 300px minmax(0, 1fr);
      min-height: 100vh;
    }}
    .sidebar {{
      position: sticky;
      top: 0;
      height: 100vh;
      padding: 18px;
      border-right: 1px solid var(--line);
      background: #eef2f7;
      overflow: auto;
    }}
    .brand h1 {{
      margin: 0 0 4px;
      font-size: 20px;
      letter-spacing: 0;
    }}
    .brand p {{
      margin: 0 0 16px;
      color: var(--muted);
      font-size: 12px;
    }}
    .filters {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin: 12px 0;
    }}
    .filters button, .search {{
      border: 1px solid var(--line-strong);
      background: #fff;
      color: var(--text);
      border-radius: 7px;
      min-height: 36px;
      padding: 7px 10px;
      font: inherit;
    }}
    .filters button.active {{
      border-color: var(--blue);
      color: var(--blue);
      box-shadow: inset 0 0 0 1px var(--blue);
    }}
    .search {{
      width: 100%;
      margin: 4px 0 10px;
    }}
    .nav-list {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .nav-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 9px 10px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: rgba(255,255,255,0.72);
    }}
    .nav-item:hover {{ border-color: var(--blue); background: #fff; }}
    .nav-item small {{ color: var(--muted); }}
    .main {{
      padding: 28px;
      max-width: 1500px;
      width: 100%;
    }}
    .hero {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      padding: 22px;
      margin-bottom: 18px;
    }}
    .hero h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      letter-spacing: 0;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
    }}
    .source {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 12px;
      word-break: break-all;
    }}
    .kpi-grid, .meta-grid, .summary-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-top: 16px;
    }}
    .kpi, .meta-grid div, .summary-card {{
      border: 1px solid var(--line);
      background: var(--panel-soft);
      border-radius: 8px;
      padding: 12px;
    }}
    .kpi span, .meta-grid span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }}
    .kpi strong, .meta-grid strong {{
      display: block;
      font-size: 20px;
      font-weight: 700;
      overflow-wrap: anywhere;
    }}
    .meta-grid {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .summary-grid {{
      grid-template-columns: repeat(5, minmax(0, 1fr));
      margin-bottom: 18px;
    }}
    .summary-card {{
      background: #fff;
    }}
    .summary-top, .summary-bottom {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}
    .summary-top span {{
      color: var(--red);
      font-size: 11px;
      font-weight: 700;
    }}
    .summary-pattern {{
      color: var(--text);
      min-height: 58px;
      margin: 10px 0;
      font-weight: 600;
    }}
    .summary-bottom {{
      color: var(--muted);
      font-size: 12px;
    }}
    .summary-bottom a {{
      color: var(--blue);
      margin-right: 6px;
      font-weight: 700;
    }}
    .query-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      padding: 18px;
      margin: 0 0 18px;
      scroll-margin-top: 16px;
    }}
    .query-header {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-start;
      margin-bottom: 12px;
    }}
    .eyebrow {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .query-header h2 {{
      margin: 2px 0 0;
      font-size: 24px;
      letter-spacing: 0;
    }}
    .badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      justify-content: flex-end;
    }}
    .badge {{
      border: 1px solid var(--line-strong);
      background: #fff;
      border-radius: 999px;
      padding: 4px 9px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .severity-critical, .severity-high, .severity-slow {{
      color: var(--red);
      border-color: #f0b4ad;
      background: #fff2f0;
    }}
    .severity-normal, .severity-ok {{
      color: var(--green);
      border-color: #b7e0d1;
      background: #effaf6;
    }}
    .pattern {{
      display: flex;
      gap: 10px;
      align-items: center;
      color: var(--red);
      background: #fff7ed;
      border: 1px solid #fed7aa;
      border-radius: 8px;
      padding: 10px 12px;
      margin: 0 0 12px;
      font-weight: 700;
    }}
    .pattern span {{
      color: var(--orange);
      font-size: 12px;
      text-transform: uppercase;
    }}
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 14px;
    }}
    .metric {{
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #fbfcfe;
      padding: 8px;
    }}
    .metric-label {{
      color: var(--muted);
      font-size: 11px;
      margin-bottom: 3px;
    }}
    .metric-value {{
      font-weight: 700;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .block {{
      border-top: 1px solid var(--line);
      padding-top: 14px;
      margin-top: 14px;
    }}
    .block-title, summary {{
      font-size: 15px;
      font-weight: 800;
      cursor: pointer;
    }}
    .plan-wrap {{
      margin-top: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: auto;
      max-height: 720px;
      background: #fff;
    }}
    .plan-table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 1180px;
      font-size: 12px;
    }}
    .plan-table th {{
      position: sticky;
      top: 0;
      background: #e8edf4;
      z-index: 1;
      color: #334155;
      text-align: left;
      font-weight: 800;
      border-bottom: 1px solid var(--line-strong);
      padding: 8px;
    }}
    .plan-table td {{
      border-bottom: 1px solid #edf1f6;
      padding: 7px 8px;
      vertical-align: top;
    }}
    .plan-table tr.hot td {{
      background: #fff1f0;
    }}
    .plan-table tr.warm td {{
      background: #fff8e8;
    }}
    .op-cell {{
      min-width: 280px;
      white-space: nowrap;
    }}
    .tree-spacer {{
      display: inline-block;
    }}
    .op-name {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-weight: 700;
    }}
    .row-toggle {{
      width: 22px;
      height: 22px;
      border: 1px solid var(--line-strong);
      border-radius: 5px;
      background: #fff;
      margin-right: 6px;
      cursor: pointer;
      font-weight: 800;
      line-height: 18px;
    }}
    .task-badge {{
      display: inline-flex;
      border-radius: 999px;
      padding: 2px 7px;
      font-weight: 800;
      white-space: nowrap;
    }}
    .task-root {{ background: #edf2ff; color: #1d4ed8; }}
    .task-tikv {{ background: #fff3bf; color: #92400e; }}
    .task-tiflash {{ background: #dcfce7; color: #166534; }}
    .task-tici {{ background: #f3e8ff; color: var(--violet); }}
    .num {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      white-space: nowrap;
    }}
    .strong {{ font-weight: 800; }}
    .operator-info {{
      min-width: 340px;
      color: #334155;
    }}
    .plan-detail-row pre {{
      margin: 0;
      padding: 12px;
      background: #0f172a;
      color: #e2e8f0;
      border-radius: 6px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }}
    .hidden {{ display: none; }}
    pre.sql, pre.raw-plan {{
      margin: 10px 0 0;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0f172a;
      color: #dbeafe;
      overflow: auto;
      max-height: 520px;
      white-space: pre;
      font-size: 12px;
      line-height: 1.45;
    }}
    pre.sql-wrap {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      word-break: break-word;
    }}
    .empty {{
      margin-top: 10px;
      color: var(--muted);
      border: 1px dashed var(--line-strong);
      padding: 14px;
      border-radius: 8px;
    }}
    .is-hidden {{ display: none !important; }}
    @media (max-width: 980px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .sidebar {{
        position: relative;
        height: auto;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }}
      .main {{ padding: 16px; }}
      .kpi-grid, .meta-grid, .summary-grid, .metrics-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .query-header {{ flex-direction: column; }}
      .badges {{ justify-content: flex-start; }}
    }}
  </style>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <h1>Query Plan Viewer</h1>
        <p>按慢查询查看指标、SQL 和结构化执行计划。</p>
      </div>
      <input class="search" id="search" placeholder="搜索 query / table / index" />
      <div class="filters">
        <button class="active" data-filter="all">全部</button>
        <button data-filter="slow">慢查询</button>
        <button data-filter="A">Group A</button>
        <button data-filter="B">Group B</button>
        <button data-filter="C">Group C</button>
        <button data-filter="D">Group D</button>
        <button data-filter="E">Group E</button>
        <button data-filter="other">Other</button>
      </div>
      <nav class="nav-list" id="navList">
        {render_sidebar(queries)}
      </nav>
    </aside>
    <main class="main">
      <section class="hero">
        <h1>PingCAP Query Performance Report</h1>
        <p>{html.escape(generated_note)}</p>
        <div class="source">Source: {source_label}</div>
        <div class="kpi-grid">
          <div class="kpi"><span>Queries parsed</span><strong>{len(queries)}</strong></div>
          <div class="kpi"><span>Slow / risky</span><strong>{slow_count}</strong></div>
          <div class="kpi"><span>Parsed load sum</span><strong>{top25_load:.2f}%</strong></div>
          <div class="kpi"><span>Worst avg latency</span><strong>Q#{max_avg_query.qid if max_avg_query else '-'} {max_avg / 1000:.1f}s</strong></div>
        </div>
        <div class="meta-grid">
          {meta_rows}
        </div>
      </section>
      <section class="summary-grid">
        {render_group_summary(patterns)}
      </section>
      <section id="queries">
        {query_cards}
      </section>
    </main>
  </div>
  <script>
    const buttons = Array.from(document.querySelectorAll('.filters button'));
    const search = document.getElementById('search');
    const cards = Array.from(document.querySelectorAll('.query-card'));
    const navItems = Array.from(document.querySelectorAll('.nav-item'));
    let activeFilter = 'all';

    function matchesFilter(el) {{
      if (activeFilter === 'all') return true;
      if (activeFilter === 'slow') return el.dataset.slow === 'true';
      return el.dataset.group === activeFilter;
    }}

    function matchesSearch(el) {{
      const term = search.value.trim().toLowerCase();
      if (!term) return true;
      return el.textContent.toLowerCase().includes(term);
    }}

    function applyFilters() {{
      cards.forEach(card => {{
        card.classList.toggle('is-hidden', !(matchesFilter(card) && matchesSearch(card)));
      }});
      navItems.forEach(item => {{
        const target = document.querySelector(item.getAttribute('href'));
        item.classList.toggle('is-hidden', !target || target.classList.contains('is-hidden'));
      }});
    }}

    buttons.forEach(button => {{
      button.addEventListener('click', () => {{
        activeFilter = button.dataset.filter;
        buttons.forEach(b => b.classList.toggle('active', b === button));
        applyFilters();
      }});
    }});
    search.addEventListener('input', applyFilters);

    document.addEventListener('click', event => {{
      const toggle = event.target.closest('.row-toggle');
      if (!toggle) return;
      const row = document.getElementById(toggle.dataset.target);
      if (!row) return;
      row.classList.toggle('hidden');
      toggle.textContent = row.classList.contains('hidden') ? '+' : '-';
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Path to the markdown report")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output HTML path. Defaults to <input stem>_viewer.html",
    )
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve() if args.output else source.with_name(source.stem + "_viewer.html")
    markdown = source.read_text(encoding="utf-8")
    output.write_text(build_html(markdown, source), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
