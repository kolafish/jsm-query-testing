# test issue

## Full Text Search Query 1

### Query Number
- Group: `Full Text Search`
- Query: `1`

### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (lower(`o`.`text_value_1`) like 'admiral-100008%' and `o`.`text_value_1` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

### Rewrite 1

This is the rewritten form that was actually used for the latency run in `obj_new`, without double quotes around the `AGAINST` argument.

```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
) and (`o`.`text_value_1` != '􏿿' and match(`o`.`text_value_1`) against('admiral-100008*' in boolean mode) and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
)))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Rewrite 1 Observed Result
- Latency: `1028ms`, `1025ms`, `1027ms`, `965ms`, `976ms`
- Row count: `1000`

#### Rewrite 1 EXPLAIN ANALYZE
```text
TopN_11    1000.00    1000    root    time:1.02s
└─Projection_23    3003067.36    214334    root    time:1.01s
  └─IndexLookUp_22    3003067.36    214334    root    time:1.02s, index_task: {total_time: 920.7ms, fetch_handle: 920.6ms}, table_task: {total_time: 823.9ms, num: 14, concurrency: 5}
    ├─ExchangeSender_21(Build)    0.00    214334    mpp[tiflash]    time:799.7ms
    │ └─Selection_19    0.00    214334    mpp[tiflash]
    │   └─IndexRangeScan_17    1000.00    214334    mpp[tiflash]    table:o, index:idx_obj_new_text_value_1_ngram(text_value_1)
    │       range:["8a6526e6-cd57-4216-bac6-358a6177d221","8a6526e6-cd57-4216-bac6-358a6177d221"], search func:or(istrue_with_null(fts_match_phrase("admiral", jsm_testcase2.obj_new.text_value_1)), istrue_with_null(fts_match_prefix("100008", jsm_testcase2.obj_new.text_value_1))), keep order:false
    └─Selection_20(Probe)    3003067.36    214334    cop[tikv]    total_time:722.9ms
      └─TableRowIDScan_18    0.00    214334    cop[tikv]    table:o
```

#### Rewrite 1 Notes
- The SQL text itself was not split, but the execution plan shows the internal search expression was widened to:
  - `fts_match_phrase("admiral")`
  - `OR fts_match_prefix("100008")`
- This produced a large candidate set of `214,334` rows before the query finished filtering and sorting.

### Rewrite 2

This version adds double quotes around the `AGAINST` argument.

```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
) and (`o`.`text_value_1` != '􏿿' and match(`o`.`text_value_1`) against('\"admiral-100008*\"' in boolean mode) and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
)))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Rewrite 2 Observed Result
- Latency: `6.71ms` from `EXPLAIN ANALYZE`
- Row count: `0`

#### Rewrite 2 EXPLAIN ANALYZE
```text
TopN_11    1000.00    0    root    time:6.71ms
└─Projection_23    3003067.36    0    root    time:6.68ms
  └─IndexLookUp_22    3003067.36    0    root    time:6.63ms
    ├─ExchangeSender_21(Build)    0.00    0    mpp[tiflash]    time:6.2ms
    │ └─Selection_19    0.00    0    mpp[tiflash]
    │   └─IndexRangeScan_17    1000.00    0    mpp[tiflash]    table:o, index:idx_obj_new_text_value_1_ngram(text_value_1)
    │       range:["8a6526e6-cd57-4216-bac6-358a6177d221","8a6526e6-cd57-4216-bac6-358a6177d221"], search func:fts_match_phrase("admiral 100008*", jsm_testcase2.obj_new.text_value_1), keep order:false
    └─Selection_20(Probe)    3003067.36    0    cop[tikv]
      └─TableRowIDScan_18    0.00    0    cop[tikv]    table:o
```

#### Rewrite 2 Notes
- Adding double quotes changed the internal search expression to a single phrase:
  - `fts_match_phrase("admiral 100008*")`
- In this version, `*` did not behave like an effective prefix match and the query returned `0` rows.

### Summary
- Without double quotes, the query matched too broadly and became slow because it effectively searched for:
  - `phrase("admiral")`
  - `OR prefix("100008")`
- With double quotes, the query became fast because it matched nothing:
  - `phrase("admiral 100008*")`
- The issue is not only the SQL text, but also how this version rewrites the FTS expression internally.
