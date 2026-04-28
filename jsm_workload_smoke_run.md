# JSM Workload Smoke Run

This document records the materialized read-only smoke run for `/Users/jin/Downloads/workload_queries.sql`.

- Target database: `jsm_assets3`
- Run location: AWS console host, using internal TiDB access through `127.0.0.1:45000`
- Materialized corpus: `bench/workload_smoke_corpus.json`
- Result JSON: `bench/results/workload_smoke_internal_20260428_verified.json`
- Workload note: the source file has 50 templates; 1 `INSERT ... SELECT` template was intentionally excluded from this read-only smoke corpus to avoid changing data.
- Rewrite note: `label_lower LIKE ...` was rewritten to `MATCH(label) AGAINST(...)` because `label_lower` is a virtual generated column that is always NULL in `jsm_assets3.obj_new`, while `label` already has `idx_fts_label` FULLTEXT NGRAM index.

## Summary

- Total read queries: `49`
- OK / row-count match: `49`
- Returned 0 rows: `10`
- Errors: `0`
- Timeouts: `0`
- Warmup p50: `7.664 ms`
- Warmup p95: `126.615 ms`
- Warmup p99: `196.997 ms`

## Key Findings

- The AWS-internal smoke run has no execution errors and no row-count mismatches after updating `expected_row_count` from the first internal run.
- `obj_new_queries_q13` is no longer the outlier after rewrite: it now returns `1` row in `12.997 ms`.
- The slowest smoke query is now `obj_new_queries_q11`: `1000` rows in `256.504 ms`.
- Current smoke results do not justify scaling before the first real concurrency ramp; the next step should be a small AWS-side QPS ramp and Grafana observation.

## Slowest Warmup Queries

| Query | Pattern | Rows | Latency ms |
| --- | --- | ---: | ---: |
| obj_new_queries_q11 | obj_new queries | 1000 | 256.504 |
| obj_new_queries_q12 | obj_new queries | 1000 | 132.531 |
| obj_new_queries_q15 | obj_new queries | 1000 | 126.752 |
| obj_new_queries_q14 | obj_new queries | 1000 | 126.409 |
| obj_new_queries_q10 | obj_new queries | 1000 | 97.289 |
| fts_match_q1 | FTS (MATCH) | 1 | 21.790 |
| schema_metadata_queries_q3 | Schema/metadata queries | 1 | 18.229 |
| obj_new_queries_q5 | obj_new queries | 1000 | 16.750 |
| fts_match_q2 | FTS (MATCH) | 1 | 14.707 |
| obj_new_queries_q1 | obj_new queries | 1 | 13.187 |

## Full Warmup Results

| Query | Pattern | Rows | Latency ms | Row-count match |
| --- | --- | ---: | ---: | --- |
| fts_match_q1 | FTS (MATCH) | 1 | 21.790 | yes |
| fts_match_q2 | FTS (MATCH) | 1 | 14.707 | yes |
| obj_new_queries_q1 | obj_new queries | 1 | 13.187 | yes |
| obj_new_queries_q2 | obj_new queries | 1 | 11.832 | yes |
| obj_new_queries_q3 | obj_new queries | 1 | 9.842 | yes |
| obj_new_queries_q4 | obj_new queries | 1000 | 11.519 | yes |
| obj_new_queries_q5 | obj_new queries | 1000 | 16.750 | yes |
| obj_new_queries_q6 | obj_new queries | 1 | 8.894 | yes |
| obj_new_queries_q7 | obj_new queries | 1 | 9.818 | yes |
| obj_new_queries_q8 | obj_new queries | 1 | 9.549 | yes |
| obj_new_queries_q9 | obj_new queries | 1 | 9.667 | yes |
| obj_new_queries_q10 | obj_new queries | 1000 | 97.289 | yes |
| obj_new_queries_q11 | obj_new queries | 1000 | 256.504 | yes |
| obj_new_queries_q12 | obj_new queries | 1000 | 132.531 | yes |
| obj_new_queries_q13 | obj_new queries | 1 | 12.997 | yes |
| obj_new_queries_q14 | obj_new queries | 1000 | 126.409 | yes |
| obj_new_queries_q15 | obj_new queries | 1000 | 126.752 | yes |
| obj_relationship_new_queries_q2 | obj_relationship_new queries | 22 | 9.888 | yes |
| obj_relationship_new_queries_q3 | obj_relationship_new queries | 22 | 6.029 | yes |
| obj_relationship_new_queries_q4 | obj_relationship_new queries | 22 | 7.664 | yes |
| obj_relationship_original_queries_q1 | obj_relationship (original) queries | 22 | 10.278 | yes |
| obj_relationship_original_queries_q2 | obj_relationship (original) queries | 22 | 6.878 | yes |
| schema_metadata_queries_q1 | Schema/metadata queries | 0 | 5.515 | yes |
| schema_metadata_queries_q2 | Schema/metadata queries | 18 | 8.449 | yes |
| schema_metadata_queries_q3 | Schema/metadata queries | 1 | 18.229 | yes |
| schema_metadata_queries_q4 | Schema/metadata queries | 9 | 5.682 | yes |
| schema_metadata_queries_q5 | Schema/metadata queries | 1 | 5.570 | yes |
| schema_metadata_queries_q6 | Schema/metadata queries | 1 | 4.109 | yes |
| schema_metadata_queries_q7 | Schema/metadata queries | 0 | 6.560 | yes |
| schema_metadata_queries_q8 | Schema/metadata queries | 1 | 5.677 | yes |
| schema_metadata_queries_q9 | Schema/metadata queries | 18 | 7.333 | yes |
| schema_metadata_queries_q10 | Schema/metadata queries | 18 | 7.492 | yes |
| schema_metadata_queries_q11 | Schema/metadata queries | 1 | 7.986 | yes |
| schema_metadata_queries_q12 | Schema/metadata queries | 1 | 3.986 | yes |
| schema_metadata_queries_q13 | Schema/metadata queries | 0 | 5.025 | yes |
| schema_metadata_queries_q14 | Schema/metadata queries | 15 | 5.313 | yes |
| schema_metadata_queries_q15 | Schema/metadata queries | 0 | 4.019 | yes |
| schema_metadata_queries_q16 | Schema/metadata queries | 0 | 4.879 | yes |
| schema_metadata_queries_q17 | Schema/metadata queries | 1 | 8.615 | yes |
| schema_metadata_queries_q18 | Schema/metadata queries | 1 | 4.635 | yes |
| schema_metadata_queries_q19 | Schema/metadata queries | 1 | 8.084 | yes |
| schema_metadata_queries_q20 | Schema/metadata queries | 1 | 6.091 | yes |
| schema_metadata_queries_q21 | Schema/metadata queries | 2 | 4.800 | yes |
| schema_metadata_queries_q22 | Schema/metadata queries | 0 | 5.304 | yes |
| schema_metadata_queries_q23 | Schema/metadata queries | 0 | 4.446 | yes |
| schema_metadata_queries_q24 | Schema/metadata queries | 0 | 4.742 | yes |
| schema_metadata_queries_q25 | Schema/metadata queries | 0 | 5.142 | yes |
| schema_metadata_queries_q26 | Schema/metadata queries | 0 | 5.592 | yes |
| schema_metadata_queries_q27 | Schema/metadata queries | 16 | 5.473 | yes |
