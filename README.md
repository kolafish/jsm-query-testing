# JSM Query Latency Tracking

This repository tracks rewritten single-query latency testing for the JSM query set.

Files:
- `jsm_dataset_1_single_query_latency_results.md`
  - latency results, row counts, actual executed SQL, and notes
- `jsm_original_queries.md`
  - original query texts covered by the current results document

Conventions:
- `obj -> obj_new`
- `obj_relationship -> obj_relationship_new`
- UUID filters are rewritten with `UNHEX(REPLACE(...))` for `BINARY(16)` columns
- `LIKE` is rewritten to `MATCH ... AGAINST` when applicable
- failures and zero-row cases are preserved with reasons

Status:
- this repo currently contains the original queries and the current single-query latency report that have already been executed in this session
- more queries can be appended incrementally
