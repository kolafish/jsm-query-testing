# Dataset 1 QPS Benchmark Patterns

This page defines a small, representative QPS benchmark workload for dataset 1 based on the original query set in `jsm_original_queries.md`.

Assumptions:
- `obj -> obj_new`
- `obj_relationship -> obj_relationship_new`
- UUID columns stored as `BINARY(16)` are compared with `UNHEX(REPLACE(...))`
- For this benchmark set, text search uses `MATCH ... AGAINST` only when the source query pattern was originally `LIKE '%...%'`
- The JQL below is approximate user-facing intent, not a verbatim export from Jira

## Included Patterns

### Pattern 1: Scalar Filters Plus Label Sort

Representative JQL:
```jql
project = JSM AND customNumberA = 548 AND customNumberB = 3 ORDER BY summary
```

Representative SQL:
```sql
select o.sequential_id, o.label
from obj_new o
where o.workspace_id = '<workspace_id>'
  and o.obj_type_id in (
    unhex(replace('<obj_type_uuid_1>', '-', '')),
    unhex(replace('<obj_type_uuid_2>', '-', '')),
    unhex(replace('<obj_type_uuid_3>', '-', ''))
  )
  and o.numeric_value_1 = 548
  and o.numeric_value_3 = 3
order by o.label asc
limit 1000 offset 0;
```

Source shape:
- `1. Basic Filters / Query 1`

### Pattern 2: Rewritten Phrase Search From Original `LIKE '%...%'`

Representative JQL:
```jql
project = JSM AND summary ~ "admiral-100000" ORDER BY summary
```

Representative SQL:
```sql
select o.sequential_id, o.label
from obj_new o
where o.workspace_id = '<workspace_id>'
  and o.obj_type_id in (
    unhex(replace('<obj_type_uuid_1>', '-', '')),
    unhex(replace('<obj_type_uuid_2>', '-', '')),
    unhex(replace('<obj_type_uuid_3>', '-', ''))
  )
  and o.text_value_1 != '􏿿'
  and match(o.text_value_1) against('"admiral-100000"' in boolean mode)
order by o.label asc
limit 1000 offset 0;
```

Notes:
- This pattern intentionally covers the original `%...%` text-search family after rewrite to `MATCH ... AGAINST`
- It is the replacement for the standalone text equality / enum bucket in this benchmark set

Source shape:
- `2. Full Text Search / Query 2`

### Pattern 3: Multi-Column Phrase Search With `UNION DISTINCT`

Representative JQL:
```jql
project = JSM AND (email ~ "dr.omer.romaguera@emmerich-gibson.example" OR website ~ "www.shelby-torp.info") ORDER BY summary
```

Representative SQL:
```sql
(
  select o.sequential_id, o.label
  from obj_new o
  where o.workspace_id = '<workspace_id>'
    and o.obj_type_id in (
      unhex(replace('<obj_type_uuid_1>', '-', '')),
      unhex(replace('<obj_type_uuid_2>', '-', '')),
      unhex(replace('<obj_type_uuid_3>', '-', ''))
    )
    and o.text_value_4 != '􏿿'
    and match(o.text_value_4) against('"dr.omer.romaguera@emmerich-gibson.example"' in boolean mode)
)
union distinct
(
  select o.sequential_id, o.label
  from obj_new o
  where o.workspace_id = '<workspace_id>'
    and o.obj_type_id in (
      unhex(replace('<obj_type_uuid_1>', '-', '')),
      unhex(replace('<obj_type_uuid_2>', '-', '')),
      unhex(replace('<obj_type_uuid_3>', '-', ''))
    )
    and o.text_value_5 != '􏿿'
    and match(o.text_value_5) against('"www.shelby-torp.info"' in boolean mode)
)
order by label asc
limit 1000 offset 0;
```

Notes:
- This is the representative pattern when different FULLTEXT columns are combined with `OR`
- In current TiDB/TiCI behavior, keeping it as a single query with multiple `MATCH` predicates is less robust than splitting into `UNION DISTINCT`

Source shape:
- `2. Full Text Search / Query 3`

### Pattern 4: Sort On A Custom Field

Representative JQL:
```jql
project = JSM AND Brand = "LG" ORDER BY customNumberA
```

Representative SQL:
```sql
select o.sequential_id, o.numeric_value_1
from obj_new o
where o.workspace_id = '<workspace_id>'
  and o.obj_type_id = unhex(replace('<obj_type_uuid>', '-', ''))
  and o.text_value_7 = 'LG'
order by o.numeric_value_1 asc
limit 1000 offset 0;
```

Source shape:
- `3. Sorting / Query 7`

### Pattern 5: CASE-Based Sort Projection

Representative JQL:
```jql
project = JSM AND customNumberA = 635 ORDER BY customText24
```

Representative SQL:
```sql
select
  o.sequential_id,
  case
    when o.obj_type_id = unhex(replace('<obj_type_uuid_1>', '-', '')) then o.text_value_24
    when o.obj_type_id = unhex(replace('<obj_type_uuid_2>', '-', '')) then o.text_value_24
    when o.obj_type_id = unhex(replace('<obj_type_uuid_3>', '-', '')) then o.text_value_24
    else '􏿿'
  end as sorted_0
from obj_new o
where o.workspace_id = '<workspace_id>'
  and o.obj_type_id in (
    unhex(replace('<obj_type_uuid_1>', '-', '')),
    unhex(replace('<obj_type_uuid_2>', '-', '')),
    unhex(replace('<obj_type_uuid_3>', '-', ''))
  )
  and o.numeric_value_1 = 635
order by sorted_0 asc
limit 1000 offset 0;
```

Source shape:
- `3. Sorting / Query 1`

### Pattern 6: Direct Relationship Lookup

Representative JQL:
```jql
issue in linkedToObject("6df297d1-c20f-35d2-9d0d-08939fd50f17")
```

Representative SQL:
```sql
select
  r.workspace_id,
  r.partition_id,
  r.id,
  r.object_id,
  r.referenced_object_id,
  r.object_type_attribute_id,
  r.object_type_id,
  r.referenced_object_type_id
from obj_relationship_new r
where r.object_id = unhex(replace('<object_uuid>', '-', ''));
```

Source shape:
- `1. Basic Filters / Query 10`

### Pattern 7: Single-Hop Relationship Traversal

Representative JQL:
```jql
project = JSM AND Appliance = "Sharp" AND referencedBy(Brand = "Samsung")
```

Representative SQL:
```sql
select o.sequential_id, o.label
from obj_new o
where o.workspace_id = '<workspace_id>'
  and o.obj_type_id in (
    unhex(replace('<obj_type_uuid_1>', '-', '')),
    unhex(replace('<obj_type_uuid_2>', '-', '')),
    unhex(replace('<obj_type_uuid_3>', '-', ''))
  )
  and o.text_value_24 = 'Sharp'
  and o.id in (
    select r.referenced_object_id
    from obj_relationship_new r
    join obj_new o1
      on r.object_id = o1.id
    where o1.workspace_id = '<workspace_id>'
      and o1.text_value_8 = 'Samsung'
  )
order by o.label asc
limit 1000 offset 0;
```

Source shape:
- `4. Relationship Traversal / Depth 0 / Query 1`

### Pattern 8: Multi-Hop Relationship Traversal

Representative JQL:
```jql
project = JSM AND hasReferencePath(label = "Admiral-1000135", depth = 2) ORDER BY summary
```

Representative SQL:
```sql
select o.sequential_id, o.label
from obj_new o
where o.workspace_id = '<workspace_id>'
  and o.obj_type_id in (
    unhex(replace('<obj_type_uuid_1>', '-', '')),
    unhex(replace('<obj_type_uuid_2>', '-', '')),
    unhex(replace('<obj_type_uuid_3>', '-', ''))
  )
  and exists (
    select 1
    from obj_relationship_new r
    join obj_new o1
      on r.referenced_object_id = o1.id
    where o.id = r.object_id
      and o1.workspace_id = '<workspace_id>'
      and exists (
        select 1
        from obj_relationship_new r1
        join obj_new o2
          on r1.referenced_object_id = o2.id
        where o1.id = r1.object_id
          and o2.workspace_id = '<workspace_id>'
          and o2.label = 'Admiral-1000135'
      )
  )
order by o.label asc
limit 1000 offset 0;
```

Source shape:
- `4. Relationship Traversal / Depth 2 / Query 1`

### Pattern 9: Numeric Range Filter

Representative JQL:
```jql
project = JSM AND customNumberA > 600 AND customNumberB > 0 ORDER BY summary
```

Representative SQL:
```sql
select o.sequential_id, o.label
from obj_new o
where o.workspace_id = '<workspace_id>'
  and o.obj_type_id in (
    unhex(replace('<obj_type_uuid_1>', '-', '')),
    unhex(replace('<obj_type_uuid_2>', '-', '')),
    unhex(replace('<obj_type_uuid_3>', '-', ''))
  )
  and o.numeric_value_1 > 600
  and o.numeric_value_3 > 0
order by o.label asc
limit 1000 offset 0;
```

Source shape:
- `6. Range Queries / Query 1`

## Patterns Explicitly Not Included In This Benchmark

### Not Included 1: Standalone Text Equality Or Enum Filters

Reason:
- This benchmark replaces that bucket with rewritten `MATCH ... AGAINST` phrase-search queries originating from the original `LIKE '%...%'` workload

Examples from the original set:
- `text_value_23 = 'KitchenAid'`
- `text_value_9 = 'Electrolux'`

### Not Included 2: Raw `LIKE '%...%'` Or `LIKE 'prefix%'` Search As A Separate Bucket

Reason:
- This runbook wants the `%...%` family represented by `MATCH ... AGAINST`
- Prefix search with punctuation or token boundaries is not always semantically identical after rewrite, so a separate raw-`LIKE` bucket is intentionally omitted

Examples from the original set:
- `lower(o.text_value_1) like 'admiral-100008%'`
- `lower(o.text_value_1) like '%admiral-1000048%'`

### Not Included 3: JSON Attribute Queries

Reason:
- `other_values`, `other_values_indexed`, and `group_values` are all `NULL` in the current dataset
- Some original JSON paths are also invalid in current TiDB syntax

Examples from the original set:
- `JSON_CONTAINS(o.other_values_indexed, ...)`
- `JSON_LENGTH(JSON_EXTRACT(...)) > 0`

### Not Included 4: Constant-False Queries

Reason:
- Queries that collapse to `and 0` do not represent meaningful search workload for QPS tests

Examples from the original set:
- `1. Basic Filters / Query 3/4/5/12/14/15/17/19`
- `3. Sorting / Query 10`

### Not Included 5: Wide Detail Fetch / Hydration Queries

Reason:
- Queries that select a very wide object row are better treated as follow-up fetches after search, not as the main search-pattern QPS mix

Example from the original set:
- `1. Basic Filters / Query 7`

## Simple Benchmark Plan For The Current Environment

### Goal

Measure a small but realistic QPS mix against the current dataset 1 cluster, focusing on search and relationship traversal patterns rather than JSON or detail hydration.

### Scope For The First Pass

Use these patterns in the initial mixed workload:
- Pattern 1: Scalar filters plus label sort
- Pattern 2: Rewritten phrase search from original `LIKE '%...%'`
- Pattern 3: Multi-column phrase search with `UNION DISTINCT`
- Pattern 4: Sort on a custom field
- Pattern 6: Direct relationship lookup
- Pattern 7: Single-hop relationship traversal
- Pattern 9: Numeric range filter

Keep these out of the first mixed run:
- Pattern 5: CASE-based sort projection
- Pattern 8: Multi-hop relationship traversal

Reason:
- They are valid workload shapes, but they are more expensive and can dominate a first-pass QPS sanity run

### Query Set Construction

Prepare 5 to 20 concrete queries for each included pattern:
- Use real `workspace_id` values that return rows
- Use real `obj_type_id` values that return rows
- Use real phrase literals for the `MATCH ... AGAINST` queries
- Keep `limit 1000 offset 0` for consistency with the original workload

Store each concrete query as a plain SQL statement in a query corpus file.

### Recommended Mix

Start with this weighted mix:
- 25% Pattern 1
- 20% Pattern 2
- 15% Pattern 3
- 15% Pattern 4
- 10% Pattern 6
- 10% Pattern 7
- 5% Pattern 9

This keeps the first run dominated by common search patterns while still exercising `obj_relationship_new`.

### Simple Execution Plan

1. Warm up:
   - run every concrete query once serially
   - clear out obvious cold-start noise before measuring
2. Single-pattern sanity:
   - run each pattern separately at concurrency `1`, `4`, `8`, `16`
   - duration `3` to `5` minutes each
3. Mixed workload:
   - run the weighted mix at concurrency `8`, `16`, `32`
   - duration `10` minutes each
4. Relationship-heavy follow-up:
   - only if needed, add Pattern 8 and rerun a second mixed profile

### Tooling Suggestion

For a very simple first pass:
- use a short benchmark driver script on the workstation
- the script should:
  - hold a connection pool
  - randomly pick from the concrete query corpus using the target weights
  - record QPS, error count, p50, p95, and p99 latency

Why not rely on `mysqlslap` alone:
- it is fine for single-query or single-pattern smoke tests
- it is awkward for a weighted mixed workload with several SQL shapes

### What To Watch During The Run

At minimum capture:
- overall QPS
- p50 / p95 / p99 latency
- error count / timeout count

Also watch cluster-side hotspots:
- TiDB CPU and session count
- TiFlash CPU, scan throughput, and MPP task count
- TiKV coprocessor latency

### Success Criteria For A First Iteration

The first pass is good enough if it answers these questions:
- what QPS the current cluster can sustain for the mixed search workload
- which pattern becomes the first bottleneck
- whether relationship traversal queries dominate p95 / p99
- whether the rewritten `MATCH ... AGAINST` queries behave stably under concurrency
