# PingCAP Query Performance Report

Files in this directory:

- `full_report_for_pingcap.md`: original Markdown report.
- `pingcap_query_plan_viewer.html`: generated static HTML query-plan viewer.
- `create_pingcap_query_viewer.py`: generator script for rebuilding the HTML from the Markdown report.

Regenerate the viewer:

```bash
python3 create_pingcap_query_viewer.py full_report_for_pingcap.md -o pingcap_query_plan_viewer.html
```
