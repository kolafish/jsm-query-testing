#!/usr/bin/env python3
import datetime as dt
import html
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
SUMMARY_PATH = HERE / "cluster_slow_query_summary.json"
OUTPUT_PATH = HERE / "cluster_slow_query_analysis.html"


def esc(value):
    return html.escape(str(value if value is not None else ""))


def compact_sql(sql):
    return re.sub(r"\s+", " ", sql or "").strip()


def fmt_int(value):
    return f"{float(value):,.0f}"


def fmt_s(value):
    return f"{float(value):,.1f}s"


def fmt_ms(value):
    return f"{float(value):,.1f}ms"


def fmt_pct(value):
    return f"{float(value):.1f}%"


def pattern_class(pattern):
    p = pattern.lower()
    if "json" in p:
        return "tag-json"
    if "relationship" in p:
        return "tag-rel"
    if "fts" in p:
        return "tag-fts"
    if "eav" in p:
        return "tag-eav"
    if "obj_new" in p:
        return "tag-obj"
    return "tag-other"


def tags(pattern_text):
    parts = [p.strip() for p in (pattern_text or "other").split(",") if p.strip()]
    return "".join(f'<span class="tag {pattern_class(p)}">{esc(p)}</span>' for p in parts[:5])


def diagnosis(record):
    p = (record.get("pattern") or "").lower()
    notes = []
    if "json filter" in p:
        notes.append(
            "JSON predicate is evaluated after scanning by object/order index, so each execution does many row lookups before filtering."
        )
    if "relationship semi-join" in p:
        notes.append(
            "Nested relationship semi-join has high fanout; plans show expensive index/table lookup work on obj_relationship_new."
        )
    if "fts" in p:
        notes.append(
            "FTS index is used, but it returns a large candidate set; TiKV table lookup and residual filters dominate the tail latency."
        )
    if "relationship lookup" in p:
        notes.append(
            "Per-query key count is not huge, but cop wait is high; this looks amplified by TiKV IO/scheduling pressure."
        )
    if "eav value filter" in p or ("obj_new" in p and "json" not in p):
        notes.append(
            "Filter and ORDER BY columns are not covered together, causing ordered range scans plus TableRowIDScan probes."
        )
    if not notes:
        notes.append("Review the full plan and compare estimate vs actual rows before changing indexes.")
    return notes[:3]


def recommendation(record):
    p = (record.get("pattern") or "").lower()
    if "json filter" in p:
        return "Evaluate multi-valued/generated-column style indexes for JSON paths, ideally combined with workspace_id, obj_type_id, and the dominant sort key."
    if "relationship semi-join" in p:
        return "Check covering indexes for join direction plus relationship attribute/type filters, and consider rewriting to start from the most selective side."
    if "fts" in p:
        return "Reduce post-FTS candidate volume by pushing selective filters closer to retrieval, or by adding a complementary filter/sort path."
    if "relationship lookup" in p:
        return "Use a covering relationship index where possible, and investigate TiKV hot-node IO because wait time exceeds processing time."
    if "eav" in p or "obj_new" in p:
        return "Create or validate compound indexes matching the common filter + ORDER BY combinations; avoid relying on label/order index followed by residual filtering."
    return "Use this digest as a drill-down candidate after the higher-load groups are addressed."


def metric_card(label, value, hint=""):
    return f"""
      <section class="metric">
        <div class="metric-label">{esc(label)}</div>
        <div class="metric-value">{esc(value)}</div>
        <div class="metric-hint">{esc(hint)}</div>
      </section>
    """


def bar(width, label=""):
    pct = max(0, min(100, float(width)))
    return f'<div class="bar"><span style="width:{pct:.2f}%"></span></div><span class="bar-label">{esc(label)}</span>'


def pattern_rows(patterns):
    rows = []
    for p in patterns[:10]:
        rows.append(
            f"""
            <tr>
              <td>{esc(p["pattern"])}</td>
              <td>{bar(p["load_pct"], fmt_pct(p["load_pct"]))}</td>
              <td class="num">{fmt_s(p["time_s"])}</td>
              <td class="num">{fmt_int(p["count"])}</td>
              <td class="num">{fmt_int(p["digests"])}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def digest_rows(records):
    rows = []
    for i, r in enumerate(records[:20], 1):
        sql = compact_sql(r.get("sample_sql", ""))
        rows.append(
            f"""
            <tr>
              <td class="rank">{i}</td>
              <td>{bar(r["load_pct"], fmt_pct(r["load_pct"]))}</td>
              <td class="num">{fmt_int(r["count"])}</td>
              <td class="num">{fmt_ms(r["avg_query_time_ms"])}</td>
              <td class="num">{fmt_ms(r["max_query_time_ms"])}</td>
              <td class="num">{fmt_int(r["avg_process_keys"])}</td>
              <td>{tags(r.get("pattern"))}</td>
              <td class="sql-brief">{esc(sql[:190] + ("..." if len(sql) > 190 else ""))}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def hotspot_rows(hotspots):
    rows = []
    top = hotspots[0]["sum_query_time_s"] if hotspots else 1
    for i, h in enumerate(hotspots[:10], 1):
        rows.append(
            f"""
            <tr>
              <td class="rank">{i}</td>
              <td><code>{esc(h["addr"])}</code></td>
              <td>{bar(h["sum_query_time_s"] / top * 100, fmt_s(h["sum_query_time_s"]))}</td>
              <td class="num">{fmt_int(h["rows"])}</td>
              <td class="num">{fmt_ms(h["avg_max_cop_wait_ms"])}</td>
              <td class="num">{fmt_ms(h["max_cop_wait_ms"])}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def detail_cards(records):
    cards = []
    for i, r in enumerate(records[:12], 1):
        notes = "".join(f"<li>{esc(n)}</li>" for n in diagnosis(r))
        idx = ", ".join(r.get("indexes") or []) or "No index listed in slow log"
        cards.append(
            f"""
            <details class="digest-card" {"open" if i <= 4 else ""}>
              <summary>
                <span class="digest-title">#{i} {esc((r.get("digest") or "")[:12])}</span>
                <span class="digest-meta">load {fmt_pct(r["load_pct"])} · avg {fmt_ms(r["avg_query_time_ms"])} · count {fmt_int(r["count"])}</span>
              </summary>
              <div class="digest-grid">
                <div>
                  <h3>Why It Is Slow</h3>
                  <ul>{notes}</ul>
                  <h3>Next Action</h3>
                  <p>{esc(recommendation(r))}</p>
                </div>
                <div class="stats-list">
                  <div><span>Max latency</span><b>{fmt_ms(r["max_query_time_ms"])}</b></div>
                  <div><span>Avg process keys</span><b>{fmt_int(r["avg_process_keys"])}</b></div>
                  <div><span>Avg requests</span><b>{fmt_int(r["avg_request_count"])}</b></div>
                  <div><span>Total read</span><b>{float(r["total_read_gib"]):,.1f} GiB</b></div>
                  <div><span>Max cop wait</span><b>{fmt_ms(r["max_cop_wait_ms"])}</b></div>
                  <div><span>Index</span><b>{esc(idx)}</b></div>
                </div>
              </div>
              <h3>Normalized SQL</h3>
              <pre class="sql">{esc(compact_sql(r.get("sample_sql", "")))}</pre>
              <h3>Plan Excerpt</h3>
              <pre class="plan">{esc(r.get("sample_plan_excerpt", ""))}</pre>
            </details>
            """
        )
    return "\n".join(cards)


def render(data):
    coverage = data.get("top_digest_coverage", {})
    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    title = "PingCAP Cluster Slow Query Analysis"
    css = """
    :root {
      --bg: #f6f7f9;
      --paper: #ffffff;
      --text: #17202a;
      --muted: #617083;
      --line: #dfe5ec;
      --blue: #2563eb;
      --teal: #0891b2;
      --green: #15803d;
      --amber: #b45309;
      --red: #b91c1c;
      --violet: #6d28d9;
      --shadow: 0 16px 38px rgba(15, 23, 42, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    header {
      background: #0f172a;
      color: #fff;
      padding: 34px 40px 30px;
      border-bottom: 5px solid #0e7490;
    }
    main { max-width: 1440px; margin: 0 auto; padding: 28px 32px 48px; }
    h1 { margin: 0 0 8px; font-size: 30px; line-height: 1.15; letter-spacing: 0; }
    h2 { margin: 34px 0 14px; font-size: 20px; letter-spacing: 0; }
    h3 { margin: 18px 0 8px; font-size: 14px; letter-spacing: 0; }
    p { margin: 0 0 12px; }
    code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    .subhead { color: #cbd5e1; max-width: 980px; font-size: 15px; }
    .meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; color: #dbeafe; }
    .pill { border: 1px solid rgba(255,255,255,.24); padding: 5px 10px; border-radius: 999px; }
    .summary {
      background: var(--paper);
      box-shadow: var(--shadow);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px 20px;
      margin-bottom: 24px;
    }
    .summary strong { color: #0f766e; }
    .metrics {
      display: grid;
      grid-template-columns: repeat(6, minmax(150px, 1fr));
      gap: 12px;
      margin-bottom: 26px;
    }
    .metric {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
      min-height: 112px;
    }
    .metric-label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
    .metric-value { margin-top: 8px; font-size: 26px; font-weight: 720; letter-spacing: 0; }
    .metric-hint { color: var(--muted); margin-top: 3px; font-size: 12px; }
    .panel {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      padding: 18px;
      margin-bottom: 22px;
      overflow: hidden;
    }
    .split {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(420px, .72fr);
      gap: 18px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      vertical-align: top;
      text-align: left;
    }
    th {
      color: #334155;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
      background: #f8fafc;
    }
    .num, .rank { text-align: right; font-variant-numeric: tabular-nums; }
    .rank { width: 44px; color: var(--muted); }
    .sql-brief { color: #334155; font-size: 12px; overflow-wrap: anywhere; }
    .bar { display: inline-block; width: 118px; height: 9px; background: #e2e8f0; border-radius: 999px; overflow: hidden; margin-right: 8px; vertical-align: middle; }
    .bar span { display: block; height: 100%; background: linear-gradient(90deg, var(--teal), var(--blue)); }
    .bar-label { font-variant-numeric: tabular-nums; color: #334155; }
    .tag {
      display: inline-block;
      margin: 0 4px 4px 0;
      padding: 2px 7px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 650;
      white-space: nowrap;
    }
    .tag-json { background: #fee2e2; color: var(--red); }
    .tag-rel { background: #ffedd5; color: var(--amber); }
    .tag-fts { background: #e0e7ff; color: var(--violet); }
    .tag-eav { background: #dcfce7; color: var(--green); }
    .tag-obj { background: #e0f2fe; color: #0369a1; }
    .tag-other { background: #f1f5f9; color: #475569; }
    .digest-card {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      margin: 14px 0;
      overflow: hidden;
    }
    .digest-card summary {
      cursor: pointer;
      display: flex;
      gap: 14px;
      justify-content: space-between;
      align-items: center;
      padding: 14px 18px;
      background: #f8fafc;
      border-bottom: 1px solid var(--line);
    }
    .digest-title { font-weight: 760; font-size: 15px; }
    .digest-meta { color: var(--muted); font-variant-numeric: tabular-nums; }
    .digest-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(320px, .85fr);
      gap: 20px;
      padding: 4px 18px 0;
    }
    .stats-list {
      display: grid;
      gap: 8px;
      margin-top: 16px;
    }
    .stats-list div {
      display: grid;
      grid-template-columns: 130px minmax(0, 1fr);
      gap: 10px;
      padding: 7px 9px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fbfdff;
    }
    .stats-list span { color: var(--muted); }
    .stats-list b { overflow-wrap: anywhere; }
    pre {
      margin: 8px 18px 18px;
      padding: 13px 14px;
      border: 1px solid #d8e0ea;
      border-radius: 8px;
      background: #0b1220;
      color: #dbeafe;
      overflow: auto;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-size: 12px;
      line-height: 1.55;
      max-height: 390px;
    }
    .plan { color: #d1fae5; }
    .footer {
      margin-top: 28px;
      color: var(--muted);
      font-size: 12px;
    }
    @media (max-width: 1100px) {
      header { padding: 28px 22px; }
      main { padding: 20px 16px 36px; }
      .metrics { grid-template-columns: repeat(2, minmax(150px, 1fr)); }
      .split, .digest-grid { grid-template-columns: 1fr; }
      table { min-width: 980px; }
      .panel { overflow-x: auto; }
    }
    """

    body = f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{esc(title)}</title>
      <style>{css}</style>
    </head>
    <body>
      <header>
        <h1>{esc(title)}</h1>
        <p class="subhead">Human-readable summary of the additional TiDB CLUSTER_SLOW_QUERY export. The report focuses on load concentration, repeated slow query patterns, hot TiKV cop wait nodes, and concrete optimization directions.</p>
        <div class="meta">
          <span class="pill">Time range: {esc(data["time_range"][0])} to {esc(data["time_range"][1])}</span>
          <span class="pill">Generated: {esc(generated)}</span>
          <span class="pill">DB: {esc(data.get("top_dbs", [["unknown"]])[0][0])}</span>
        </div>
      </header>
      <main>
        <section class="summary">
          <p><strong>One-sentence conclusion:</strong> the new slow queries are still dominated by obj_new JSON/EAV filtering, relationship fanout, and FTS candidate expansion, with high TiKV cop wait amplifying latency on hot nodes.</p>
          <p><strong>Primary action:</strong> mitigate TiKV IO pressure first while evaluating JSON multi-value/generated-column indexing, relationship covering indexes, and compound filter + sort indexes for the recurring obj_new patterns.</p>
        </section>

        <section class="metrics">
          {metric_card("Rows", fmt_int(data["rows"]), "slow log entries")}
          {metric_card("Distinct Digests", fmt_int(data["distinct_digests"]), "normalized SQL groups")}
          {metric_card("Total Query Time", fmt_s(data["total_query_time_s"]), "accumulated, concurrent")}
          {metric_card("Top 5 Coverage", fmt_pct(coverage.get("top_5_pct", 0)), "of total load")}
          {metric_card("Top 10 Coverage", fmt_pct(coverage.get("top_10_pct", 0)), "of total load")}
          {metric_card("Top 25 Coverage", fmt_pct(coverage.get("top_25_pct", 0)), "of total load")}
        </section>

        <section class="split">
          <div class="panel">
            <h2>Load By Pattern</h2>
            <table>
              <thead><tr><th>Pattern</th><th>Load</th><th>Total Time</th><th>Rows</th><th>Digests</th></tr></thead>
              <tbody>{pattern_rows(data.get("patterns", []))}</tbody>
            </table>
          </div>
          <div class="panel">
            <h2>TiKV cop_wait Hotspots</h2>
            <table>
              <thead><tr><th>#</th><th>TiKV</th><th>Associated Load</th><th>Rows</th><th>Avg Max Wait</th><th>Max Wait</th></tr></thead>
              <tbody>{hotspot_rows(data.get("cop_wait_hotspots", []))}</tbody>
            </table>
          </div>
        </section>

        <section class="panel">
          <h2>Top Digests By Load</h2>
          <table>
            <thead>
              <tr>
                <th>#</th><th>Load</th><th>Count</th><th>Avg Latency</th><th>Max Latency</th><th>Avg Keys</th><th>Pattern</th><th>SQL</th>
              </tr>
            </thead>
            <tbody>{digest_rows(data.get("top_by_load", []))}</tbody>
          </table>
        </section>

        <h2>Top Digest Details</h2>
        {detail_cards(data.get("top_by_load", []))}

        <section class="footer">
          Source: {esc(data.get("source", ""))}. Raw CSV zip is intentionally not committed to git because it is larger than GitHub's normal single-file limit.
        </section>
      </main>
    </body>
    </html>
    """
    return body


def main():
    data = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.write_text(render(data), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
