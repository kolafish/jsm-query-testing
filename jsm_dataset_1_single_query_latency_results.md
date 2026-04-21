# JSM Query Results

Generated on 2026-04-20.

Scope:
- Apply session rewrite rules:
  - `obj -> obj_new`
  - `obj_relationship -> obj_relationship_new`
  - replace `workspace_id` / `obj_type_id` / `object_id` with real values that hit
  - use `UNHEX(REPLACE(...))` for `BINARY(16)` UUID columns
  - rewrite `LIKE` to `MATCH ... AGAINST` when applicable
  - add `ngram FULLTEXT` only when needed and possible
- If a query needs a `FULLTEXT` index that is not currently available, do not run it; record the required index instead.
- Keep original query numbering even when a query errors or returns no rows after rewrite.
- For failed queries, preserve:
  - original query
  - actual query attempted
  - error or non-hit reason

Global note:
- `obj_new.other_values_indexed` is currently `NULL` for all rows (`COUNT(*) WHERE other_values_indexed IS NOT NULL = 0`).
- Because of that, JSON queries that require positive `JSON_CONTAINS(...)`, `JSON_LENGTH(...) > 0`, or direct key hits on `other_values_indexed` will not have matching rows after the mandatory `obj -> obj_new` rewrite.
- Stale TiCI import tasks for `DDL 1180` were recovered by resetting job `402` task rows from `running` back to `init` in `tici.tici_import_jobs_task`.
- After recovery, these FULLTEXT indexes finished successfully:
  - `idx_obj_new_text_value_22_ngram_v2`
  - `idx_obj_new_label_ngram`
  - `idx_obj_new_text_value_1_ngram`

## 1. Basic Filters

### Query 1

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`numeric_value_1` = 548 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')) and (`o`.`numeric_value_3` = 3 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221'
  and `o`.`obj_type_id` in (
    unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
    unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
    unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
    unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-','')),
    unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-',''))
  )
  and `o`.`numeric_value_1` = 548
  and `o`.`numeric_value_3` = 3
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `30ms`, `21ms`, `22ms`, `22ms`, `23ms`
- Row count: `51`
- Notes: replaced `workspace_id` and `obj_type_id` with real matching values in `obj_new`.

### Query 2

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '571d993b-45b0-47e3-b9d0-0e65f44e853f') and (`o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' or `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c') and (`o`.`text_value_23` = 'KitchenAid' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '571d993b-45b0-47e3-b9d0-0e65f44e853f') and (`o`.`text_value_22` like '%Requirements%' and `o`.`text_value_22` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '571d993b-45b0-47e3-b9d0-0e65f44e853f')) and (`o`.`text_value_9` = 'Electrolux' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '571d993b-45b0-47e3-b9d0-0e65f44e853f')) and (`o`.`numeric_value_3` = 22 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '571d993b-45b0-47e3-b9d0-0e65f44e853f') or `o`.`numeric_value_1` = 720 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '571d993b-45b0-47e3-b9d0-0e65f44e853f'))))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265'
  and `o`.`obj_type_id` in (
    unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')),
    unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-',''))
  )
  and (`o`.`obj_type_id` = unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')) or `o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')))
  and `o`.`text_value_23` = 'KitchenAid'
  and `o`.`text_value_9` = 'Electrolux'
  and `o`.`text_value_22` != '􏿿'
  and match(`o`.`text_value_22`) against('"Requirements"' in boolean mode)
  and (`o`.`numeric_value_3` = 22 or `o`.`numeric_value_1` = 720)
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `2282ms`, `2323ms`, `2210ms`, `2311ms`, `2308ms`
- Row count: `9`
- Notes: the original nested predicate was normalized after the `MATCH AGAINST` rewrite to fix parenthesis imbalance and preserve semantics.

#### Slow Analysis
- `EXPLAIN ANALYZE` showed the query was slow because `match(text_value_22) against('"Requirements"' in boolean mode)` on `idx_obj_new_text_value_22_ngram_v2` produced a very large candidate set before the other predicates were applied.
- The `IndexRangeScan` on the FULLTEXT index returned `500,264` candidate rows for this workspace, and TiFlash spent about `1.48s` in this stage.
- The plan then performed an `IndexLookUp` back to TiKV for all `500,264` row IDs. The root `IndexLookUp` took about `2.33s`, and the probe-side TiKV selection scanned about `3.99 GB` of row data before reducing the result to `9` rows.
- Top-level plan highlights:
  - `TopN_11`: `2.33s`
  - `IndexLookUp_22`: `2.33s`
  - `IndexRangeScan_17` on `idx_obj_new_text_value_22_ngram_v2`: `500,264` rows
  - `Selection_20(Probe)` on TiKV: still processed `500,264` keys, final output `9` rows
- Predicate selectivity on the `MATCH` candidate set:
  - `MATCH(text_value_22="Requirements")`: `500,264`
  - plus `text_value_23='KitchenAid'`: `21,424`
  - plus `text_value_9='Electrolux'`: `21,529`
  - plus `obj_type_id in (...)`: `200,157`
  - plus `(numeric_value_3=22 or numeric_value_1=720)`: `9,240`
  - plus `text_value_23='KitchenAid' and text_value_9='Electrolux'`: `930`
  - plus `text_value_23='KitchenAid' and text_value_9='Electrolux' and obj_type_id in (...)`: `381`
  - all filters together: `9`
- Conclusion: the bottleneck was not `ORDER BY`, but the low selectivity of the `Requirements` FULLTEXT predicate. A better shape for this query is to first use the existing BTREE predicates on `text_value_23`, `text_value_9`, `obj_type_id`, and numeric columns to shrink the candidate set, then evaluate `text_value_22` on that small set.

### Query 3

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and 0
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `14ms`, `10ms`, `11ms`, `9ms`, `11ms`
- Row count: `0`
- Notes: `and 0` keeps the query empty after rewrite.

### Query 4

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and 0
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `14ms`, `10ms`, `11ms`, `9ms`, `11ms`
- Row count: `0`

### Query 5

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and 0
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `14ms`, `10ms`, `11ms`, `9ms`, `11ms`
- Row count: `0`

### Query 6

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and lower(`o`.`label`) like '%%')
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221'
  and `o`.`obj_type_id` in (
    unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
    unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
    unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
    unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
    unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
  )
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `30ms`, `19ms`, `16ms`, `15ms`, `15ms`
- Row count: `1000`
- Notes: `lower(label) like '%%'` is a tautology, so only the populated workspace and real `obj_type_id` filters matter.

### Query 7

#### Original Query
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`text_value_1`, `o`.`text_value_2`, `o`.`text_value_3`, `o`.`text_value_4`, `o`.`text_value_5`, `o`.`text_value_6`, `o`.`text_value_7`, `o`.`text_value_8`, `o`.`text_value_9`, `o`.`text_value_10`, `o`.`text_value_11`, `o`.`text_value_12`, `o`.`text_value_13`, `o`.`text_value_14`, `o`.`text_value_15`, `o`.`text_value_16`, `o`.`text_value_17`, `o`.`text_value_18`, `o`.`text_value_19`, `o`.`text_value_20`, `o`.`text_value_21`, `o`.`text_value_22`, `o`.`text_value_23`, `o`.`text_value_24`, `o`.`text_value_25`, `o`.`text_value_26`, `o`.`text_value_27`, `o`.`text_value_28`, `o`.`text_value_29`, `o`.`text_value_30`, `o`.`text_value_31`, `o`.`text_value_32`, `o`.`text_value_33`, `o`.`text_value_34`, `o`.`text_value_35`, `o`.`text_value_36`, `o`.`text_value_37`, `o`.`text_value_38`, `o`.`text_value_39`, `o`.`text_value_40`, `o`.`text_value_41`, `o`.`text_value_42`, `o`.`text_value_43`, `o`.`text_value_44`, `o`.`text_value_45`, `o`.`text_value_46`, `o`.`text_value_47`, `o`.`text_value_48`, `o`.`text_value_49`, `o`.`text_value_50`, `o`.`text_value_51`, `o`.`text_value_52`, `o`.`text_value_53`, `o`.`text_value_54`, `o`.`text_value_55`, `o`.`text_value_56`, `o`.`text_value_57`, `o`.`text_value_58`, `o`.`text_value_59`, `o`.`text_value_60`, `o`.`text_value_61`, `o`.`text_value_62`, `o`.`text_value_63`, `o`.`text_value_64`, `o`.`text_value_65`, `o`.`text_value_66`, `o`.`text_value_67`, `o`.`text_value_68`, `o`.`text_value_69`, `o`.`text_value_70`, `o`.`text_value_71`, `o`.`text_value_72`, `o`.`text_value_73`, `o`.`text_value_74`, `o`.`text_value_75`, `o`.`text_value_76`, `o`.`text_value_77`, `o`.`text_value_78`, `o`.`text_value_79`, `o`.`text_value_80`, `o`.`text_value_81`, `o`.`text_value_82`, `o`.`text_value_83`, `o`.`text_value_84`, `o`.`text_value_85`, `o`.`text_value_86`, `o`.`text_value_87`, `o`.`text_value_88`, `o`.`text_value_89`, `o`.`text_value_90`, `o`.`text_value_91`, `o`.`text_value_92`, `o`.`text_value_93`, `o`.`text_value_94`, `o`.`text_value_95`, `o`.`text_value_96`, `o`.`text_value_97`, `o`.`text_value_98`, `o`.`text_value_99`, `o`.`text_value_100`, `o`.`text_value_101`, `o`.`text_value_102`, `o`.`text_value_103`, `o`.`text_value_104`, `o`.`text_value_105`, `o`.`text_value_106`, `o`.`text_value_107`, `o`.`text_value_108`, `o`.`text_value_109`, `o`.`text_value_110`, `o`.`text_value_111`, `o`.`text_value_112`, `o`.`text_value_113`, `o`.`text_value_114`, `o`.`text_value_115`, `o`.`text_value_116`, `o`.`text_value_117`, `o`.`text_value_118`, `o`.`text_value_119`, `o`.`text_value_120`, `o`.`text_value_121`, `o`.`text_value_122`, `o`.`text_value_123`, `o`.`text_value_124`, `o`.`text_value_125`, `o`.`text_value_126`, `o`.`text_value_127`, `o`.`text_value_128`, `o`.`text_value_129`, `o`.`text_value_130`, `o`.`text_value_131`, `o`.`text_value_132`, `o`.`text_value_133`, `o`.`text_value_134`, `o`.`text_value_135`, `o`.`text_value_136`, `o`.`text_value_137`, `o`.`text_value_138`, `o`.`text_value_139`, `o`.`text_value_140`, `o`.`text_value_141`, `o`.`text_value_142`, `o`.`text_value_143`, `o`.`text_value_144`, `o`.`text_value_145`, `o`.`text_value_146`, `o`.`text_value_147`, `o`.`text_value_148`, `o`.`text_value_149`, `o`.`text_value_150`, `o`.`text_value_151`, `o`.`text_value_152`, `o`.`text_value_153`, `o`.`text_value_154`, `o`.`text_value_155`, `o`.`numeric_value_1`, `o`.`numeric_value_2`, `o`.`numeric_value_3`, `o`.`numeric_value_4`, `o`.`numeric_value_5`, `o`.`numeric_value_6`, `o`.`numeric_value_7`, `o`.`numeric_value_8`, `o`.`numeric_value_9`, `o`.`numeric_value_10`, `o`.`numeric_value_11`, `o`.`numeric_value_12`, `o`.`numeric_value_13`, `o`.`numeric_value_14`, `o`.`numeric_value_15`, `o`.`numeric_value_16`, `o`.`numeric_value_17`, `o`.`numeric_value_18`, `o`.`numeric_value_19`, `o`.`numeric_value_20`, `o`.`numeric_value_21`, `o`.`numeric_value_22`, `o`.`numeric_value_23`, `o`.`numeric_value_24`, `o`.`numeric_value_25`, `o`.`numeric_value_26`, `o`.`numeric_value_27`, `o`.`numeric_value_28`, `o`.`numeric_value_29`, `o`.`numeric_value_30`, `o`.`numeric_value_31`, `o`.`numeric_value_32`, `o`.`numeric_value_33`, `o`.`numeric_value_34`, `o`.`numeric_value_35`, `o`.`numeric_value_36`, `o`.`numeric_value_37`, `o`.`numeric_value_38`, `o`.`numeric_value_39`, `o`.`numeric_value_40`, `o`.`numeric_value_41`, `o`.`numeric_value_42`, `o`.`numeric_value_43`, `o`.`numeric_value_44`, `o`.`numeric_value_45`, `o`.`numeric_value_46`, `o`.`numeric_value_47`, `o`.`numeric_value_48`, `o`.`numeric_value_49`, `o`.`numeric_value_50`, `o`.`numeric_value_51`, `o`.`numeric_value_52`, `o`.`numeric_value_53`, `o`.`numeric_value_54`, `o`.`numeric_value_55`, `o`.`numeric_value_56`, `o`.`numeric_value_57`, `o`.`numeric_value_58`, `o`.`numeric_value_59`, `o`.`numeric_value_60`, `o`.`numeric_value_61`, `o`.`numeric_value_62`, `o`.`numeric_value_63`, `o`.`numeric_value_64`, `o`.`numeric_value_65`, `o`.`numeric_value_66`, `o`.`numeric_value_67`, `o`.`numeric_value_68`, `o`.`numeric_value_69`, `o`.`numeric_value_70`, `o`.`numeric_value_71`, `o`.`numeric_value_72`, `o`.`numeric_value_73`, `o`.`numeric_value_74`, `o`.`numeric_value_75`, `o`.`numeric_value_76`, `o`.`numeric_value_77`, `o`.`numeric_value_78`, `o`.`numeric_value_79`, `o`.`numeric_value_80`, `o`.`numeric_value_81`, `o`.`numeric_value_82`, `o`.`numeric_value_83`, `o`.`numeric_value_84`, `o`.`numeric_value_85`, `o`.`numeric_value_86`, `o`.`numeric_value_87`, `o`.`numeric_value_88`, `o`.`numeric_value_89`, `o`.`numeric_value_90`, `o`.`numeric_value_91`, `o`.`numeric_value_92`, `o`.`numeric_value_93`, `o`.`numeric_value_94`, `o`.`numeric_value_95`, `o`.`numeric_value_96`, `o`.`numeric_value_97`, `o`.`numeric_value_98`, `o`.`numeric_value_99`, `o`.`numeric_value_100`, `o`.`numeric_value_101`, `o`.`numeric_value_102`, `o`.`numeric_value_103`, `o`.`numeric_value_104`, `o`.`numeric_value_105`, `o`.`numeric_value_106`, `o`.`numeric_value_107`, `o`.`numeric_value_108`, `o`.`numeric_value_109`, `o`.`numeric_value_110`, `o`.`numeric_value_111`, `o`.`numeric_value_112`, `o`.`numeric_value_113`, `o`.`numeric_value_114`, `o`.`numeric_value_115`, `o`.`numeric_value_116`, `o`.`numeric_value_117`, `o`.`numeric_value_118`, `o`.`numeric_value_119`, `o`.`numeric_value_120`, `o`.`numeric_value_121`, `o`.`numeric_value_122`, `o`.`numeric_value_123`, `o`.`numeric_value_124`, `o`.`numeric_value_125`, `o`.`numeric_value_126`, `o`.`numeric_value_127`, `o`.`numeric_value_128`, `o`.`numeric_value_129`, `o`.`numeric_value_130`, `o`.`numeric_value_131`, `o`.`numeric_value_132`, `o`.`numeric_value_133`, `o`.`numeric_value_134`, `o`.`numeric_value_135`, `o`.`numeric_value_136`, `o`.`numeric_value_137`, `o`.`numeric_value_138`, `o`.`numeric_value_139`, `o`.`numeric_value_140`, `o`.`numeric_value_141`, `o`.`numeric_value_142`, `o`.`numeric_value_143`, `o`.`numeric_value_144`, `o`.`numeric_value_145`, `o`.`numeric_value_146`, `o`.`numeric_value_147`, `o`.`numeric_value_148`, `o`.`numeric_value_149`, `o`.`numeric_value_150`, `o`.`numeric_value_151`, `o`.`numeric_value_152`, `o`.`numeric_value_153`, `o`.`numeric_value_154`, `o`.`numeric_value_155`, `o`.`unique_value_ota_1`, `o`.`unique_value_1`, `o`.`unique_value_ota_2`, `o`.`unique_value_2`, `o`.`unique_value_ota_3`, `o`.`unique_value_3`, `o`.`unique_value_ota_4`, `o`.`unique_value_4`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' and lower(`o`.`label`) like '%qcewpvmssdry%')
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`text_value_1`, `o`.`text_value_2`, `o`.`text_value_3`, `o`.`text_value_4`, `o`.`text_value_5`, `o`.`text_value_6`, `o`.`text_value_7`, `o`.`text_value_8`, `o`.`text_value_9`, `o`.`text_value_10`, `o`.`text_value_11`, `o`.`text_value_12`, `o`.`text_value_13`, `o`.`text_value_14`, `o`.`text_value_15`, `o`.`text_value_16`, `o`.`text_value_17`, `o`.`text_value_18`, `o`.`text_value_19`, `o`.`text_value_20`, `o`.`text_value_21`, `o`.`text_value_22`, `o`.`text_value_23`, `o`.`text_value_24`, `o`.`text_value_25`, `o`.`text_value_26`, `o`.`text_value_27`, `o`.`text_value_28`, `o`.`text_value_29`, `o`.`text_value_30`, `o`.`text_value_31`, `o`.`text_value_32`, `o`.`text_value_33`, `o`.`text_value_34`, `o`.`text_value_35`, `o`.`text_value_36`, `o`.`text_value_37`, `o`.`text_value_38`, `o`.`text_value_39`, `o`.`text_value_40`, `o`.`text_value_41`, `o`.`text_value_42`, `o`.`text_value_43`, `o`.`text_value_44`, `o`.`text_value_45`, `o`.`text_value_46`, `o`.`text_value_47`, `o`.`text_value_48`, `o`.`text_value_49`, `o`.`text_value_50`, `o`.`text_value_51`, `o`.`text_value_52`, `o`.`text_value_53`, `o`.`text_value_54`, `o`.`text_value_55`, `o`.`text_value_56`, `o`.`text_value_57`, `o`.`text_value_58`, `o`.`text_value_59`, `o`.`text_value_60`, `o`.`text_value_61`, `o`.`text_value_62`, `o`.`text_value_63`, `o`.`text_value_64`, `o`.`text_value_65`, `o`.`text_value_66`, `o`.`text_value_67`, `o`.`text_value_68`, `o`.`text_value_69`, `o`.`text_value_70`, `o`.`text_value_71`, `o`.`text_value_72`, `o`.`text_value_73`, `o`.`text_value_74`, `o`.`text_value_75`, `o`.`text_value_76`, `o`.`text_value_77`, `o`.`text_value_78`, `o`.`text_value_79`, `o`.`text_value_80`, `o`.`text_value_81`, `o`.`text_value_82`, `o`.`text_value_83`, `o`.`text_value_84`, `o`.`text_value_85`, `o`.`text_value_86`, `o`.`text_value_87`, `o`.`text_value_88`, `o`.`text_value_89`, `o`.`text_value_90`, `o`.`text_value_91`, `o`.`text_value_92`, `o`.`text_value_93`, `o`.`text_value_94`, `o`.`text_value_95`, `o`.`text_value_96`, `o`.`text_value_97`, `o`.`text_value_98`, `o`.`text_value_99`, `o`.`text_value_100`, `o`.`text_value_101`, `o`.`text_value_102`, `o`.`text_value_103`, `o`.`text_value_104`, `o`.`text_value_105`, `o`.`text_value_106`, `o`.`text_value_107`, `o`.`text_value_108`, `o`.`text_value_109`, `o`.`text_value_110`, `o`.`text_value_111`, `o`.`text_value_112`, `o`.`text_value_113`, `o`.`text_value_114`, `o`.`text_value_115`, `o`.`text_value_116`, `o`.`text_value_117`, `o`.`text_value_118`, `o`.`text_value_119`, `o`.`text_value_120`, `o`.`text_value_121`, `o`.`text_value_122`, `o`.`text_value_123`, `o`.`text_value_124`, `o`.`text_value_125`, `o`.`text_value_126`, `o`.`text_value_127`, `o`.`text_value_128`, `o`.`text_value_129`, `o`.`text_value_130`, `o`.`text_value_131`, `o`.`text_value_132`, `o`.`text_value_133`, `o`.`text_value_134`, `o`.`text_value_135`, `o`.`text_value_136`, `o`.`text_value_137`, `o`.`text_value_138`, `o`.`text_value_139`, `o`.`text_value_140`, `o`.`text_value_141`, `o`.`text_value_142`, `o`.`text_value_143`, `o`.`text_value_144`, `o`.`text_value_145`, `o`.`text_value_146`, `o`.`text_value_147`, `o`.`text_value_148`, `o`.`text_value_149`, `o`.`text_value_150`, `o`.`text_value_151`, `o`.`text_value_152`, `o`.`text_value_153`, `o`.`text_value_154`, `o`.`text_value_155`, `o`.`numeric_value_1`, `o`.`numeric_value_2`, `o`.`numeric_value_3`, `o`.`numeric_value_4`, `o`.`numeric_value_5`, `o`.`numeric_value_6`, `o`.`numeric_value_7`, `o`.`numeric_value_8`, `o`.`numeric_value_9`, `o`.`numeric_value_10`, `o`.`numeric_value_11`, `o`.`numeric_value_12`, `o`.`numeric_value_13`, `o`.`numeric_value_14`, `o`.`numeric_value_15`, `o`.`numeric_value_16`, `o`.`numeric_value_17`, `o`.`numeric_value_18`, `o`.`numeric_value_19`, `o`.`numeric_value_20`, `o`.`numeric_value_21`, `o`.`numeric_value_22`, `o`.`numeric_value_23`, `o`.`numeric_value_24`, `o`.`numeric_value_25`, `o`.`numeric_value_26`, `o`.`numeric_value_27`, `o`.`numeric_value_28`, `o`.`numeric_value_29`, `o`.`numeric_value_30`, `o`.`numeric_value_31`, `o`.`numeric_value_32`, `o`.`numeric_value_33`, `o`.`numeric_value_34`, `o`.`numeric_value_35`, `o`.`numeric_value_36`, `o`.`numeric_value_37`, `o`.`numeric_value_38`, `o`.`numeric_value_39`, `o`.`numeric_value_40`, `o`.`numeric_value_41`, `o`.`numeric_value_42`, `o`.`numeric_value_43`, `o`.`numeric_value_44`, `o`.`numeric_value_45`, `o`.`numeric_value_46`, `o`.`numeric_value_47`, `o`.`numeric_value_48`, `o`.`numeric_value_49`, `o`.`numeric_value_50`, `o`.`numeric_value_51`, `o`.`numeric_value_52`, `o`.`numeric_value_53`, `o`.`numeric_value_54`, `o`.`numeric_value_55`, `o`.`numeric_value_56`, `o`.`numeric_value_57`, `o`.`numeric_value_58`, `o`.`numeric_value_59`, `o`.`numeric_value_60`, `o`.`numeric_value_61`, `o`.`numeric_value_62`, `o`.`numeric_value_63`, `o`.`numeric_value_64`, `o`.`numeric_value_65`, `o`.`numeric_value_66`, `o`.`numeric_value_67`, `o`.`numeric_value_68`, `o`.`numeric_value_69`, `o`.`numeric_value_70`, `o`.`numeric_value_71`, `o`.`numeric_value_72`, `o`.`numeric_value_73`, `o`.`numeric_value_74`, `o`.`numeric_value_75`, `o`.`numeric_value_76`, `o`.`numeric_value_77`, `o`.`numeric_value_78`, `o`.`numeric_value_79`, `o`.`numeric_value_80`, `o`.`numeric_value_81`, `o`.`numeric_value_82`, `o`.`numeric_value_83`, `o`.`numeric_value_84`, `o`.`numeric_value_85`, `o`.`numeric_value_86`, `o`.`numeric_value_87`, `o`.`numeric_value_88`, `o`.`numeric_value_89`, `o`.`numeric_value_90`, `o`.`numeric_value_91`, `o`.`numeric_value_92`, `o`.`numeric_value_93`, `o`.`numeric_value_94`, `o`.`numeric_value_95`, `o`.`numeric_value_96`, `o`.`numeric_value_97`, `o`.`numeric_value_98`, `o`.`numeric_value_99`, `o`.`numeric_value_100`, `o`.`numeric_value_101`, `o`.`numeric_value_102`, `o`.`numeric_value_103`, `o`.`numeric_value_104`, `o`.`numeric_value_105`, `o`.`numeric_value_106`, `o`.`numeric_value_107`, `o`.`numeric_value_108`, `o`.`numeric_value_109`, `o`.`numeric_value_110`, `o`.`numeric_value_111`, `o`.`numeric_value_112`, `o`.`numeric_value_113`, `o`.`numeric_value_114`, `o`.`numeric_value_115`, `o`.`numeric_value_116`, `o`.`numeric_value_117`, `o`.`numeric_value_118`, `o`.`numeric_value_119`, `o`.`numeric_value_120`, `o`.`numeric_value_121`, `o`.`numeric_value_122`, `o`.`numeric_value_123`, `o`.`numeric_value_124`, `o`.`numeric_value_125`, `o`.`numeric_value_126`, `o`.`numeric_value_127`, `o`.`numeric_value_128`, `o`.`numeric_value_129`, `o`.`numeric_value_130`, `o`.`numeric_value_131`, `o`.`numeric_value_132`, `o`.`numeric_value_133`, `o`.`numeric_value_134`, `o`.`numeric_value_135`, `o`.`numeric_value_136`, `o`.`numeric_value_137`, `o`.`numeric_value_138`, `o`.`numeric_value_139`, `o`.`numeric_value_140`, `o`.`numeric_value_141`, `o`.`numeric_value_142`, `o`.`numeric_value_143`, `o`.`numeric_value_144`, `o`.`numeric_value_145`, `o`.`numeric_value_146`, `o`.`numeric_value_147`, `o`.`numeric_value_148`, `o`.`numeric_value_149`, `o`.`numeric_value_150`, `o`.`numeric_value_151`, `o`.`numeric_value_152`, `o`.`numeric_value_153`, `o`.`numeric_value_154`, `o`.`numeric_value_155`, `o`.`unique_value_ota_1`, `o`.`unique_value_1`, `o`.`unique_value_ota_2`, `o`.`unique_value_2`, `o`.`unique_value_ota_3`, `o`.`unique_value_3`, `o`.`unique_value_ota_4`, `o`.`unique_value_4`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and (`o`.`obj_type_id` = unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')) and match(`o`.`label`) against('"Admiral-100000"' in boolean mode))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Result
- Latency: `30ms`, `25ms`, `25ms`, `26ms`, `26ms`
- Row count: `1`
- Notes: the original label fragment `qcewpvmssdry` had no hits in `obj_new`; a real label sample was used after `idx_obj_new_label_ngram` became available.

### Query 8

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and ((`o`.`numeric_value_1` != 137 or `o`.`numeric_value_1` is null) and `o`.`numeric_value_1` is not null and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')) and (`o`.`numeric_value_3` <= 50 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221'
  and `o`.`obj_type_id` in (
    unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
    unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
    unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
    unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
    unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
  )
  and `o`.`numeric_value_1` is not null
  and `o`.`numeric_value_1` != 137
  and `o`.`numeric_value_3` <= 50
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `254ms`, `95ms`, `118ms`, `116ms`, `112ms`
- Row count: `1000`
- Notes: simplified the nullable predicate to its equivalent `numeric_value_1 is not null and numeric_value_1 != 137`.

### Query 9

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and (`o`.`numeric_value_2` = 1 and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221'
  and `o`.`obj_type_id` = unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-',''))
  and `o`.`numeric_value_2` = 1
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `476ms`, `81ms`, `79ms`, `79ms`, `89ms`
- Row count: `1000`

### Query 10

#### Original Query
```sql
select `obj_relationship`.`workspace_id`, `obj_relationship`.`partition_id`, `obj_relationship`.`id`, `obj_relationship`.`object_id`, `obj_relationship`.`referenced_object_id`, `obj_relationship`.`object_type_attribute_id`, `obj_relationship`.`object_type_id`, `obj_relationship`.`referenced_object_type_id`
from `obj_relationship` `obj_relationship`
where `obj_relationship`.`object_id` = '6df297d1-c20f-35d2-9d0d-08939fd50f17'
```

#### Actual Query Run
```sql
select `obj_relationship`.`workspace_id`, `obj_relationship`.`partition_id`, `obj_relationship`.`id`, `obj_relationship`.`object_id`, `obj_relationship`.`referenced_object_id`, `obj_relationship`.`object_type_attribute_id`, `obj_relationship`.`object_type_id`, `obj_relationship`.`referenced_object_type_id`
from `obj_relationship_new` `obj_relationship`
where `obj_relationship`.`object_id` = unhex(replace('0000db1b-2c55-3677-be47-5087d500faba','-',''));
```

#### Result
- Latency: `186ms`, `129ms`, `127ms`, `128ms`, `128ms`
- Row count: `56`
- Notes: original `object_id` had no hits after rewrite; replaced with a real matching `BINARY(16)` UUID in `obj_relationship_new`.

### Query 11

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('224a0035-8ac2-4e01-b892-fa4c7a268523', '2c0cb0be-dda3-4f33-8979-441e073a3873', '3fe7df63-f9c1-4581-be1b-cd649fdbb6ce', '4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', '94c23b0c-1362-4e30-b392-9dc80eb80b27', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and `o`.`sequential_id` = 1000 and (`o`.`numeric_value_4` < 1672531200000 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')) and (`o`.`numeric_value_4` > 946684800000 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` in (
  unhex(replace('224a0035-8ac2-4e01-b892-fa4c7a268523','-','')),
  unhex(replace('2c0cb0be-dda3-4f33-8979-441e073a3873','-','')),
  unhex(replace('3fe7df63-f9c1-4581-be1b-cd649fdbb6ce','-','')),
  unhex(replace('f597b640-098b-4718-b2c1-6e68b9f54741','-','')),
  unhex(replace('fba8338d-44d7-4d9d-9775-08b0638e310b','-','')),
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('1b4004ba-e54e-4fe6-bd56-7275d83fb60f','-','')),
  unhex(replace('908d8850-2f03-4ffd-8227-b62205d198df','-','')),
  unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-',''))
) and `o`.`sequential_id` = 1000 and (`o`.`numeric_value_4` < 1672531200 and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-',''))
)) and (`o`.`numeric_value_4` > 946684800 and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-',''))
)))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `35ms`, `32ms`, `30ms`, `30ms`, `32ms`
- Row count: `1`
- Notes: `obj_new.numeric_value_4` stores seconds epoch, so the original millisecond bounds were rewritten to second-based bounds.

### Query 12

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and 0
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `14ms`, `10ms`, `11ms`, `9ms`, `11ms`
- Row count: `0`

### Query 13

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' or `o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5' or `o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' or `o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' or `o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = 'cab76eba-265a-411c-8201-54d4ed4cf555'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` in (
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-','')),
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))
) and (`o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')) or `o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')) or `o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')) or `o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-','')) or `o`.`numeric_value_5` in (2, 4, 9) and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `99ms`, `84ms`, `82ms`, `83ms`, `83ms`
- Row count: `1000`

### Query 14

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and 0
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `14ms`, `10ms`, `11ms`, `9ms`, `11ms`
- Row count: `0`

### Query 15

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and 0
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `14ms`, `10ms`, `11ms`, `9ms`, `11ms`
- Row count: `0`

### Query 16

#### Original Query
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'cab76eba-265a-411c-8201-54d4ed4cf555' and ((1 != 2 or `o`.`numeric_value_5` is null) and `o`.`numeric_value_5` is not null and `o`.`obj_type_id` = 'cab76eba-265a-411c-8201-54d4ed4cf555'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and ((1 != 2 or `o`.`numeric_value_5` is null) and `o`.`numeric_value_5` is not null and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `434ms`, `103ms`, `122ms`, `121ms`, `126ms`
- Row count: `1000`
- Notes: the predicate reduces to `numeric_value_5 is not null`; the rewritten query preserves the original shape.

### Query 17

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and 0
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `14ms`, `10ms`, `11ms`, `9ms`, `11ms`
- Row count: `0`

### Query 18

#### Original Query
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'cab76eba-265a-411c-8201-54d4ed4cf555' and ((1 != 2 or `o`.`numeric_value_5` is null) and `o`.`numeric_value_5` is not null and `o`.`obj_type_id` = 'cab76eba-265a-411c-8201-54d4ed4cf555'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and ((1 != 2 or `o`.`numeric_value_5` is null) and `o`.`numeric_value_5` is not null and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `434ms`, `103ms`, `122ms`, `121ms`, `126ms`
- Row count: `1000`

### Query 19

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and 0
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `14ms`, `10ms`, `11ms`, `9ms`, `11ms`
- Row count: `0`

## 2. Full Text Search

### Query 1

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (lower(`o`.`text_value_1`) like 'admiral-100008%' and `o`.`text_value_1` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Compatibility Notes
- This query shape is not safely equivalent to a FULLTEXT rewrite in the current build when the prefix contains token boundary characters such as `-`, whitespace, email punctuation, or URL punctuation.
- For a single analyzer token without token boundaries, the MySQL-compatible prefix form is:
  - `match(col) against('prefix*' in boolean mode)`
- A quick validation on `obj_new.text_value_7` showed:
  - `lower(text_value_7) like 'sam%'` -> `129,077`
  - `match(text_value_7) against('sam*' in boolean mode)` -> `129,077`
  - `match(text_value_7) against('"sam*"' in boolean mode)` -> `0`
- So, for a single token prefix, the correct rewrite is the unquoted form. Quoting the token changes the semantics.
- The original predicate in this query, `lower(text_value_1) like 'admiral-100008%'`, crosses a token boundary at `-`, so the rewrite is not semantically stable.

#### Token Boundary Behavior
- When the search literal contains a token boundary, the FTS layer no longer behaves like a plain string prefix match.
- For `admiral-100008*` without double quotes, the execution plan widened the search internally and did not preserve the original prefix semantics.
- For `"admiral-100008*"` with double quotes, the execution plan treated the whole literal as a phrase and did not produce the expected prefix behavior either.
- Conclusion: for this specific query, neither tested `MATCH ... AGAINST` form is equivalent to the original MySQL `LIKE 'prefix%'` predicate.

#### Tested Form 1
```sql
match(`o`.`text_value_1`) against('admiral-100008*' in boolean mode)
```

#### Tested Form 1 Observed Result
- Latency: `1028ms`, `1025ms`, `1027ms`, `965ms`, `976ms`
- Row count: `1000`
- Candidate rows before final output: `214,334`

#### Tested Form 1 EXPLAIN ANALYZE
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

#### Tested Form 2
```sql
match(`o`.`text_value_1`) against('"admiral-100008*"' in boolean mode)
```

#### Tested Form 2 Observed Result
- Latency: `6.71ms` from `EXPLAIN ANALYZE`
- Row count: `0`

#### Tested Form 2 EXPLAIN ANALYZE
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

#### Final Conclusion
- If the query string is a single token without token boundaries, use:
  - `match(col) against('prefix*' in boolean mode)`
- If the query string contains `-`, whitespace, or punctuation, do not assume a `MATCH ... AGAINST` rewrite is semantically equivalent to `LIKE 'prefix%'`.
- For this query, both tested rewrites are incorrect relative to the original SQL:
  - unquoted form: too broad
  - quoted form: too narrow

### Query 2

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (lower(`o`.`text_value_1`) like '%admiral-1000048%' and `o`.`text_value_1` != '\U0010ffff'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and (`o`.`obj_type_id` in (
  unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')),
  unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')),
  unhex(replace('fbf1f5ec-17a1-4645-8d33-b9e09ce76b32','-','')),
  unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-','')),
  unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-',''))
) and (`o`.`text_value_1` != '􏿿' and match(`o`.`text_value_1`) against('"admiral-100000"' in boolean mode)))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `26ms`, `21ms`, `20ms`, `22ms`, `21ms`
- Row count: `1`
- Notes: actual returning query uses `match(text_value_1) against('"admiral-100000"' in boolean mode)`.

### Query 3

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`text_value_4` like '%dr.omer.romaguera@emmerich-gibson.example%' and `o`.`text_value_4` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') or `o`.`text_value_5` like '%www.shelby-torp.info%' and `o`.`text_value_5` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
(
  select `o`.`sequential_id`, `o`.`label`
  from `obj_new` `o`
  where `o`.`workspace_id` = 'cafd5188-8a63-44e7-b4a9-e885c9664b9c'
    and `o`.`obj_type_id` in (
      unhex(replace('2077b614-8b6d-4ac6-9c71-f22f98319244','-','')),
      unhex(replace('3ba75b67-ac62-4e20-b481-02a537de994c','-','')),
      unhex(replace('49a19896-37fc-403d-ab07-200b57d5795a','-','')),
      unhex(replace('e0c8ce12-e18b-4499-af96-07e73c3a2ca8','-','')),
      unhex(replace('fba8338d-44d7-4d9d-9775-08b0638e310b','-',''))
    )
    and `o`.`text_value_4` != '􏿿'
    and match(`o`.`text_value_4`) against('"dr.omer.romaguera@emmerich-gibson.example"' in boolean mode)
)
union distinct
(
  select `o`.`sequential_id`, `o`.`label`
  from `obj_new` `o`
  where `o`.`workspace_id` = 'cafd5188-8a63-44e7-b4a9-e885c9664b9c'
    and `o`.`obj_type_id` in (
      unhex(replace('2077b614-8b6d-4ac6-9c71-f22f98319244','-','')),
      unhex(replace('3ba75b67-ac62-4e20-b481-02a537de994c','-','')),
      unhex(replace('49a19896-37fc-403d-ab07-200b57d5795a','-','')),
      unhex(replace('e0c8ce12-e18b-4499-af96-07e73c3a2ca8','-','')),
      unhex(replace('fba8338d-44d7-4d9d-9775-08b0638e310b','-',''))
    )
    and `o`.`text_value_5` != '􏿿'
    and match(`o`.`text_value_5`) against('"www.shelby-torp.info"' in boolean mode)
)
order by `label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `37ms`, `35ms`, `34ms`, `34ms`, `34ms`
- Row count: `1`
- Notes: this TiDB build cannot keep two different FULLTEXT columns inside a single `OR`, so the query was rewritten as `UNION DISTINCT`.

### Query 4

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`text_value_4` like '%maren.heller@welch.test%' and `o`.`text_value_4` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') or `o`.`text_value_5` like '%www.leonor-hamill.io%' and `o`.`text_value_5` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') or `o`.`text_value_10` = 'Fagor' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
(
  select `o`.`sequential_id`, `o`.`label`
  from `obj_new` `o`
  where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265'
    and `o`.`obj_type_id` in (
      unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')),
      unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')),
      unhex(replace('fbf1f5ec-17a1-4645-8d33-b9e09ce76b32','-','')),
      unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-','')),
      unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-',''))
    )
    and `o`.`text_value_4` != '􏿿'
    and match(`o`.`text_value_4`) against('"maren.heller@welch.test"' in boolean mode)
)
union distinct
(
  select `o`.`sequential_id`, `o`.`label`
  from `obj_new` `o`
  where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265'
    and `o`.`obj_type_id` in (
      unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')),
      unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')),
      unhex(replace('fbf1f5ec-17a1-4645-8d33-b9e09ce76b32','-','')),
      unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-','')),
      unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-',''))
    )
    and `o`.`text_value_5` != '􏿿'
    and match(`o`.`text_value_5`) against('"www.leonor-hamill.io"' in boolean mode)
)
union distinct
(
  select `o`.`sequential_id`, `o`.`label`
  from `obj_new` `o`
  where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265'
    and `o`.`obj_type_id` in (
      unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')),
      unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')),
      unhex(replace('fbf1f5ec-17a1-4645-8d33-b9e09ce76b32','-','')),
      unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-','')),
      unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-',''))
    )
    and `o`.`text_value_10` = 'Fagor'
)
order by `label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `127ms`, `76ms`, `81ms`, `79ms`, `79ms`
- Row count: `1000`

### Query 5

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`text_value_5` like '%www.royal-simonis.biz%' and `o`.`text_value_5` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3b4c201d-8244-416e-925d-f9608e001a2b' and (`o`.`obj_type_id` in (
  unhex(replace('81feda68-d5ab-4446-9beb-8f69400dc6c2','-','')),
  unhex(replace('f597b640-098b-4718-b2c1-6e68b9f54741','-','')),
  unhex(replace('c22f89dd-bd66-41de-ba0b-37040386366e','-','')),
  unhex(replace('bc138a47-90c4-4acb-a647-5b6fd613c2c4','-','')),
  unhex(replace('27a590c1-b3c8-44bc-a930-99f60f480dcf','-',''))
) and (`o`.`text_value_5` != '􏿿' and match(`o`.`text_value_5`) against('"www.royal-simonis.biz"' in boolean mode) and `o`.`obj_type_id` in (
  unhex(replace('81feda68-d5ab-4446-9beb-8f69400dc6c2','-','')),
  unhex(replace('f597b640-098b-4718-b2c1-6e68b9f54741','-','')),
  unhex(replace('c22f89dd-bd66-41de-ba0b-37040386366e','-','')),
  unhex(replace('bc138a47-90c4-4acb-a647-5b6fd613c2c4','-','')),
  unhex(replace('27a590c1-b3c8-44bc-a930-99f60f480dcf','-',''))
)))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `34ms`, `31ms`, `31ms`, `30ms`, `31ms`
- Row count: `1`

### Query 6

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and ((lower(`o`.`text_value_4`) like '%alpha.nolan@hills.example%' or lower(`o`.`text_value_4`) like '%fr.zena.ruecker@baumbach-runolfsson.test%' or lower(`o`.`text_value_4`) like '%holli.goodwin@cruickshank.test%' or lower(`o`.`text_value_4`) like '%dr.odell.feeney@dickens.example%') and `o`.`text_value_4` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '00eaf117-fdd6-4176-9926-45310e6b9f54' and (`o`.`obj_type_id` in (
  unhex(replace('76ab5017-9923-4642-a916-99903ad27935','-','')),
  unhex(replace('df9590fa-ac31-4b9c-8b4f-6210a1dfb9cd','-','')),
  unhex(replace('617eb6d9-e03f-4c96-b846-e29e6a69bd46','-','')),
  unhex(replace('647b5262-9317-479b-81e2-c6ffebce7991','-','')),
  unhex(replace('3f141668-d3ba-459d-be7a-61ef6e3d451d','-',''))
) and (match(`o`.`text_value_4`) against('"shayne.zboncak@schaden-morissette.test" "bart.kuvalis@breitenberg.example" "belva.smitham@monahan.example" "pablo.roberts@reilly.example"' in boolean mode) and `o`.`text_value_4` != '􏿿' and `o`.`obj_type_id` in (
  unhex(replace('76ab5017-9923-4642-a916-99903ad27935','-','')),
  unhex(replace('df9590fa-ac31-4b9c-8b4f-6210a1dfb9cd','-','')),
  unhex(replace('617eb6d9-e03f-4c96-b846-e29e6a69bd46','-','')),
  unhex(replace('647b5262-9317-479b-81e2-c6ffebce7991','-','')),
  unhex(replace('3f141668-d3ba-459d-be7a-61ef6e3d451d','-',''))
)))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `37ms`, `33ms`, `33ms`, `31ms`, `32ms`
- Row count: `4`
- Notes: the original four email phrases had no hits in `obj_new.text_value_4`; sampled real values were used to validate the same-column multi-phrase rewrite shape.

### Query 7

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (lower(`o`.`text_value_5`) like '%www.nick-bauch.name%' and `o`.`text_value_5` != '\U0010ffff' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '00eaf117-fdd6-4176-9926-45310e6b9f54' and (`o`.`obj_type_id` in (
  unhex(replace('76ab5017-9923-4642-a916-99903ad27935','-','')),
  unhex(replace('df9590fa-ac31-4b9c-8b4f-6210a1dfb9cd','-','')),
  unhex(replace('617eb6d9-e03f-4c96-b846-e29e6a69bd46','-','')),
  unhex(replace('647b5262-9317-479b-81e2-c6ffebce7991','-','')),
  unhex(replace('3f141668-d3ba-459d-be7a-61ef6e3d451d','-',''))
) and (`o`.`text_value_5` != '􏿿' and match(`o`.`text_value_5`) against('"www.nick-bauch.name"' in boolean mode) and `o`.`obj_type_id` in (
  unhex(replace('76ab5017-9923-4642-a916-99903ad27935','-','')),
  unhex(replace('df9590fa-ac31-4b9c-8b4f-6210a1dfb9cd','-','')),
  unhex(replace('617eb6d9-e03f-4c96-b846-e29e6a69bd46','-','')),
  unhex(replace('647b5262-9317-479b-81e2-c6ffebce7991','-','')),
  unhex(replace('3f141668-d3ba-459d-be7a-61ef6e3d451d','-',''))
)))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `32ms`, `29ms`, `30ms`, `29ms`, `29ms`
- Row count: `0`

## 3. Sorting

### Query 1

#### Original Query
```sql
select `o`.`sequential_id`, (case when `o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5' then `o`.`text_value_24` when `o`.`obj_type_id` = 'cab76eba-265a-411c-8201-54d4ed4cf555' then `o`.`text_value_24` when `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' then `o`.`text_value_24` when `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' then `o`.`text_value_24` when `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' then `o`.`text_value_24` else '􏿿' end) as `sorted_0`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`numeric_value_1` = 635 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `sorted_0` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, (case
  when `o`.`obj_type_id` = unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-','')) then `o`.`text_value_24`
  when `o`.`obj_type_id` = unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')) then `o`.`text_value_24`
  when `o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')) then `o`.`text_value_24`
  when `o`.`obj_type_id` = unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-','')) then `o`.`text_value_24`
  when `o`.`obj_type_id` = unhex(replace('fbf1f5ec-17a1-4645-8d33-b9e09ce76b32','-','')) then `o`.`text_value_24`
  else '􏿿'
end) as `sorted_0`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265'
  and (
    `o`.`obj_type_id` in (
      unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-','')),
      unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')),
      unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')),
      unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-','')),
      unhex(replace('fbf1f5ec-17a1-4645-8d33-b9e09ce76b32','-',''))
    )
    and (
      `o`.`numeric_value_1` = 635
      and `o`.`obj_type_id` in (
        unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-','')),
        unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')),
        unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')),
        unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-','')),
        unhex(replace('fbf1f5ec-17a1-4645-8d33-b9e09ce76b32','-',''))
      )
    )
  )
order by `sorted_0` asc
limit 1000
offset 0;
```

#### Result
- Latency: `51ms`, `46ms`, `44ms`, `45ms`, `45ms`
- Row count: `1000`
- Notes: the `CASE` branch `obj_type_id` values were rewritten together with the outer filters so that `sorted_0` stays meaningful after the dataset switch.

### Query 2

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`numeric_value_1` = 846 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
) and (`o`.`numeric_value_1` = 846 and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `51ms`, `31ms`, `31ms`, `30ms`, `29ms`
- Row count: `1000`
- Notes: `obj -> obj_new`; switched to populated workspace and real matching `obj_type_id` values.

### Query 3

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`text_value_1`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' and ((not lower(`o`.`text_value_7`) = 'blue star' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f') and (`o`.`text_value_8` = 'Samsung' and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f'))
order by `o`.`text_value_1` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`text_value_1`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and ((not lower(`o`.`text_value_7`) = 'blue star' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))) and (`o`.`text_value_8` = 'Samsung' and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`text_value_1` asc
limit 1000
offset 0;
```

#### Result
- Latency: `60ms`, `46ms`, `44ms`, `45ms`, `48ms`
- Row count: `1000`
- Notes: replaced single `obj_type_id` with a real populated value in the selected workspace.

### Query 4

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`text_value_7`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and ((not lower(`o`.`text_value_7`) = 'electrolux' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15') and (`o`.`text_value_8` = 'Amana' and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15'))
order by `o`.`text_value_7` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`text_value_7`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and (`o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')) and ((not lower(`o`.`text_value_7`) = 'electrolux' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-',''))) and (`o`.`text_value_8` = 'Amana' and `o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-',''))))
order by `o`.`text_value_7` asc
limit 1000
offset 0;
```

#### Result
- Latency: `51ms`, `48ms`, `45ms`, `43ms`, `42ms`
- Row count: `1000`

### Query 5

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`text_value_8`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5' and ((not lower(`o`.`text_value_7`) = 'blue star' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5') and (`o`.`text_value_8` = 'Siemens' and `o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5'))
order by `o`.`text_value_8` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`text_value_8`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and (`o`.`obj_type_id` = unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-','')) and ((not lower(`o`.`text_value_7`) = 'blue star' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-',''))) and (`o`.`text_value_8` = 'Siemens' and `o`.`obj_type_id` = unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-',''))))
order by `o`.`text_value_8` asc
limit 1000
offset 0;
```

#### Result
- Latency: `53ms`, `46ms`, `44ms`, `45ms`, `44ms`
- Row count: `1000`

### Query 6

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`numeric_value_4`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' and ((not lower(`o`.`text_value_7`) = 'ikea' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f') and (`o`.`text_value_16` = 'Electrolux' and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f'))
order by `o`.`numeric_value_4` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`numeric_value_4`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and (`o`.`obj_type_id` = unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')) and ((not lower(`o`.`text_value_7`) = 'ikea' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-',''))) and (`o`.`text_value_16` = 'Electrolux' and `o`.`obj_type_id` = unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-',''))))
order by `o`.`numeric_value_4` asc
limit 1000
offset 0;
```

#### Result
- Latency: `59ms`, `51ms`, `49ms`, `48ms`, `47ms`
- Row count: `1000`

### Query 7

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`numeric_value_1`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' and (`o`.`text_value_7` = 'LG' and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f'))
order by `o`.`numeric_value_1` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`numeric_value_1`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and (`o`.`text_value_7` = 'LG' and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`numeric_value_1` asc
limit 1000
offset 0;
```

#### Result
- Latency: `47ms`, `39ms`, `43ms`, `38ms`, `36ms`
- Row count: `1000`

### Query 8

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`numeric_value_3`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5' and (`o`.`text_value_7` = 'Blue Star' and `o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5'))
order by `o`.`numeric_value_3` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`numeric_value_3`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and (`o`.`text_value_7` = 'Blue Star' and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`numeric_value_3` asc
limit 1000
offset 0;
```

#### Result
- Latency: `48ms`, `42ms`, `40ms`, `39ms`, `50ms`
- Row count: `1000`

### Query 9

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`numeric_value_2`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and (`o`.`text_value_7` = 'KitchenAid' and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`numeric_value_2` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`numeric_value_2`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and (`o`.`obj_type_id` = unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-','')) and (`o`.`text_value_7` = 'KitchenAid' and `o`.`obj_type_id` = unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-',''))))
order by `o`.`numeric_value_2` asc
limit 1000
offset 0;
```

#### Result
- Latency: `52ms`, `44ms`, `43ms`, `43ms`, `43ms`
- Row count: `1000`

### Query 10

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and 0
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `14ms`, `12ms`, `13ms`, `12ms`, `13ms`
- Row count: `0`
- Notes: `and 0` keeps the query empty after rewrite.

### Query 11

#### Original Query
```sql
select `o`.`sequential_id`, `st`.`name`
from `obj` `o`
left join `status_type` `st`
on `st`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and `o`.`obj_type_id` in ('224a0035-8ac2-4e01-b892-fa4c7a268523', '2c0cb0be-dda3-4f33-8979-441e073a3873', '3fe7df63-f9c1-4581-be1b-cd649fdbb6ce', '4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', '94c23b0c-1362-4e30-b392-9dc80eb80b27', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`st`.`sequential_id` = `o`.`numeric_value_5` and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f')
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f'
group by `o`.`sequential_id`, `st`.`name`
order by `st`.`name` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `st`.`name`
from `obj_new` `o`
left join `status_type` `st`
on `st`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and `o`.`obj_type_id` in (
  unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')),
  unhex(replace('ffa5cafc-4d65-4b4e-8f7b-8312ae044e16','-','')),
  unhex(replace('fbf1f5ec-17a1-4645-8d33-b9e09ce76b32','-','')),
  unhex(replace('b57a7edf-4412-4810-9e52-eaaa8bebd9a4','-','')),
  unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-',''))
) and (`st`.`sequential_id` = `o`.`numeric_value_5` and `o`.`obj_type_id` = unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-','')))
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and `o`.`obj_type_id` = unhex(replace('743641da-c08d-4bdf-be89-63d44a1d2250','-',''))
group by `o`.`sequential_id`, `st`.`name`
order by `st`.`name` asc
limit 1000
offset 0;
```

#### Result
- Latency: `193ms`, `165ms`, `171ms`, `196ms`, `205ms`
- Row count: `1000`
- Notes: kept `status_type` unchanged; only rewrote the `obj` side to `obj_new` and replaced UUID filters with real populated values.

## 4. Relationship Traversal

### Depth 0 / Query 1

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`text_value_24` = 'Sharp' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')) and `o`.`id` in (select `subR`.`referenced_object_id`
from `obj_relationship` `subR`
inner join `obj` `subO1`
on `subR`.`object_id` = `subO1`.`id` and `subO1`.`obj_type_id` in ('224a0035-8ac2-4e01-b892-fa4c7a268523', '2c0cb0be-dda3-4f33-8979-441e073a3873', '3fe7df63-f9c1-4581-be1b-cd649fdbb6ce', '4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', '94c23b0c-1362-4e30-b392-9dc80eb80b27', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')
where `subO1`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`subO1`.`text_value_8` = 'Samsung' and `subO1`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555'))))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
) and (`o`.`text_value_24` = 'Sharp' and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
)) and `o`.`id` in (select `subR`.`referenced_object_id`
from `obj_relationship_new` `subR`
inner join `obj_new` `subO1`
on `subR`.`object_id` = `subO1`.`id` and `subO1`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
)
where `subO1`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`subO1`.`text_value_8` = 'Samsung' and `subO1`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `8451ms`, `627ms`, `612ms`, `613ms`, `617ms`
- Row count: `1000`
- Notes: `obj_relationship -> obj_relationship_new`; rewrote both object-type lists to populated UUIDs in the same workspace.

### Depth 0 / Query 2

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`id` in (select `subR`.`object_id`
from `obj_relationship` `subR`
inner join `obj_relationship` `subR1`
on `subR1`.`object_id` = `subR`.`referenced_object_id` and `subR`.`object_type_attribute_id` = '80360285-8551-49a0-a948-054987dbea6e' and `subR1`.`object_type_id` in ('224a0035-8ac2-4e01-b892-fa4c7a268523', '2c0cb0be-dda3-4f33-8979-441e073a3873', '3fe7df63-f9c1-4581-be1b-cd649fdbb6ce', '4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', '94c23b0c-1362-4e30-b392-9dc80eb80b27', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')
inner join `obj` `subO1`
on `subR1`.`referenced_object_id` = `subO1`.`id` and `subR1`.`object_type_attribute_id` = '1839b024-b917-4508-92ee-8c7d468c2725' and `subO1`.`obj_type_id` in ('224a0035-8ac2-4e01-b892-fa4c7a268523', '2c0cb0be-dda3-4f33-8979-441e073a3873', '3fe7df63-f9c1-4581-be1b-cd649fdbb6ce', '4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', '94c23b0c-1362-4e30-b392-9dc80eb80b27', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')
where `subO1`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`subO1`.`text_value_1` = 'Admiral-1000657' and `subO1`.`obj_type_id` = 'cab76eba-265a-411c-8201-54d4ed4cf555')) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221'
  and `o`.`obj_type_id` = unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-',''))
  and `o`.`id` in (
    select `subR`.`object_id`
    from `obj_relationship_new` `subR`
    inner join `obj_relationship_new` `subR1`
      on `subR1`.`object_id` = `subR`.`referenced_object_id`
    inner join `obj_new` `subO1`
      on `subR1`.`referenced_object_id` = `subO1`.`id`
    where `subR`.`object_type_attribute_id` = unhex(replace('71e507af-1523-42d0-882e-35dd9e05a4f0','-',''))
      and `subR1`.`object_type_attribute_id` = unhex(replace('b2403c80-b1d0-4cca-8b08-455d49f340b4','-',''))
      and `subR1`.`object_type_id` in (
        unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
        unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
        unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
        unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
        unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
      )
      and `subO1`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221'
      and `subO1`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))
      and `subO1`.`text_value_1` = 'Admiral-100206'
  )
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `477ms`, `405ms`, `387ms`, `386ms`, `390ms`
- Row count: `0`
- Reason: after rewrite to real `workspace_id` / `obj_type_id` / `object_type_attribute_id` values, this two-hop relationship shape did execute, but the sampled chain produced no matching outer rows.
- Notes: the original deeply nested parenthesized shape needed light normalization to run cleanly after UUID/binary rewrite.

### Depth 1 / Query 1

#### Original Query
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`text_value_1`, `o`.`text_value_2`, `o`.`text_value_3`, `o`.`text_value_4`, `o`.`text_value_5`, `o`.`text_value_6`, `o`.`text_value_7`, `o`.`text_value_8`, `o`.`text_value_9`, `o`.`text_value_10`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and exists (select 1
from `obj_relationship` `subR`
inner join `obj` `subO1`
on `subR`.`referenced_object_id` = `subO1`.`id` and `subO1`.`obj_type_id` in ('224a0035-8ac2-4e01-b892-fa4c7a268523', '2c0cb0be-dda3-4f33-8979-441e073a3873', '3fe7df63-f9c1-4581-be1b-cd649fdbb6ce', '4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', '94c23b0c-1362-4e30-b392-9dc80eb80b27', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')
where `o`.`id` = `subR`.`object_id` and `subO1`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and `subO1`.`label` = 'Admiral-1000153'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`text_value_1`, `o`.`text_value_2`, `o`.`text_value_3`, `o`.`text_value_4`, `o`.`text_value_5`, `o`.`text_value_6`, `o`.`text_value_7`, `o`.`text_value_8`, `o`.`text_value_9`, `o`.`text_value_10`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')) and exists (select 1
from `obj_relationship_new` `subR`
inner join `obj_new` `subO1`
on `subR`.`referenced_object_id` = `subO1`.`id` and `subO1`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
)
where `o`.`id` = `subR`.`object_id` and `subO1`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and `subO1`.`label` = 'Siemens-26785'))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `304ms`, `270ms`, `263ms`, `262ms`, `260ms`
- Row count: `120`
- Notes: original label did not hit in the sampled workspace, so it was replaced with a real referenced label `Siemens-26785`.

### Depth 1 / Query 2

#### Original Query
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' and exists (select 1
from `obj_relationship` `subR`
inner join `obj` `subO1`
on `subR`.`object_id` = `subO1`.`id` and `subO1`.`obj_type_id` in ('224a0035-8ac2-4e01-b892-fa4c7a268523', '2c0cb0be-dda3-4f33-8979-441e073a3873', '3fe7df63-f9c1-4581-be1b-cd649fdbb6ce', '4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', '94c23b0c-1362-4e30-b392-9dc80eb80b27', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')
where `o`.`id` = `subR`.`referenced_object_id` and `subO1`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`subO1`.`text_value_7` = 'LG' and `subO1`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555'))))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and exists (select 1
from `obj_relationship_new` `subR`
inner join `obj_new` `subO1`
on `subR`.`object_id` = `subO1`.`id` and `subO1`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
)
where `o`.`id` = `subR`.`referenced_object_id` and `subO1`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`subO1`.`text_value_7` = 'LG' and `subO1`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `680ms`, `644ms`, `642ms`, `639ms`, `646ms`
- Row count: `1000`

### Depth 1 / Query 3

#### Original Query
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and (exists (select 1
from `obj_relationship` `subR`
inner join `obj` `subO1`
on `subR`.`referenced_object_id` = `subO1`.`id` and `subR`.`object_type_attribute_id` in ('3eae60cd-b8eb-435a-81fe-bb289ae70079', '1839b024-b917-4508-92ee-8c7d468c2725', '26c1d48a-33a5-4991-a456-568f8efc9fa4') and `subO1`.`obj_type_id` in ('224a0035-8ac2-4e01-b892-fa4c7a268523', '2c0cb0be-dda3-4f33-8979-441e073a3873', '3fe7df63-f9c1-4581-be1b-cd649fdbb6ce', '4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', '94c23b0c-1362-4e30-b392-9dc80eb80b27', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')
where `o`.`id` = `subR`.`object_id` and `subO1`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`subO1`.`text_value_1` = 'Admiral-1000235' and `subO1`.`obj_type_id` = 'cab76eba-265a-411c-8201-54d4ed4cf555')) and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`workspace_id`, `o`.`partition_id`, `o`.`id`, `o`.`sequential_id`, `o`.`schema_id`, `o`.`schema_key`, `o`.`obj_type_id`, `o`.`external_id`, `o`.`label`, `o`.`has_avatar`, `o`.`created_on`, `o`.`updated_on`, `o`.`other_values`, `o`.`other_values_indexed`, `o`.`group_values`, `o`.`hash_key`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')) and (exists (select 1
from `obj_relationship_new` `subR`
inner join `obj_new` `subO1`
on `subR`.`referenced_object_id` = `subO1`.`id` and `subR`.`object_type_attribute_id` in (
  unhex(replace('71e507af-1523-42d0-882e-35dd9e05a4f0','-','')),
  unhex(replace('b2403c80-b1d0-4cca-8b08-455d49f340b4','-','')),
  unhex(replace('0dd6ad9f-89d1-441c-b355-ae2522533854','-',''))
) and `subO1`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
)
where `o`.`id` = `subR`.`object_id` and `subO1`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`subO1`.`text_value_1` = 'Admiral-100032' and `subO1`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')))) and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-',''))
)))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `312ms`, `286ms`, `276ms`, `258ms`, `264ms`
- Row count: `0`
- Reason: query runs after rewrite, but this OTA-set + sampled referenced object combination did not produce matches in `obj_new`.

### Depth 1 / Query 6

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`text_value_24` = 'Electrolux' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')) and exists (select 1 from `obj_relationship` `subR` inner join `obj` `subO1` on `subR`.`referenced_object_id` = `subO1`.`id` where `o`.`id` = `subR`.`object_id` and `subO1`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
) and (`o`.`text_value_24` = 'Electrolux' and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
)) and exists (select 1 from `obj_relationship_new` `subR` inner join `obj_new` `subO1` on `subR`.`referenced_object_id` = `subO1`.`id` where `o`.`id` = `subR`.`object_id` and `subO1`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221'))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `1543ms`, `1521ms`, `1524ms`, `1526ms`, `1531ms`
- Row count: `1000`

## 5. JSON Attribute Queries

### Query 1

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b18eaa977c5b007289045d'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b18fffb43d5b006ad51967'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b1905d744c4d0069877712'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b19058977c5b0072891783'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('perf-user1111')))) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b18eaa977c5b007289045d'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b18fffb43d5b006ad51967'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b1905d744c4d0069877712'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b19058977c5b0072891783'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('perf-user1111')))) and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `67ms`, `67ms`, `66ms`, `63ms`, `67ms`
- Row count: `0`
- Error: `ERROR 1105 (HY000): Invalid JSON path expression. The error is around character position 1.`
- Notes: TiDB rejects the `<equation>...` / `</equation>...` JSON path syntax in `JSON_SET(...)`.

### Query 2

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('account_id_for_admin_user'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('5b112e4164666649ccb90760'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('nonexistinguser')))) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('account_id_for_admin_user'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('5b112e4164666649ccb90760'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('nonexistinguser')))) and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `76ms`, `66ms`, `67ms`, `66ms`, `67ms`
- Row count: `0`
- Error: `ERROR 1105 (HY000): Invalid JSON path expression. The error is around character position 1.`

### Query 3

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('Normal user user211')))) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('Normal user user211')))) and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `64ms`, `62ms`, `63ms`, `65ms`, `68ms`
- Row count: `0`
- Error: `ERROR 1105 (HY000): Invalid JSON path expression. The error is around character position 1.`

### Query 4

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('account_id_for_admin_user'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('5b112e4164666649ccb90760'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('Normal user user217'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user111'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user211'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user311'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user411'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user511')))) and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and (`o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')) and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('account_id_for_admin_user'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('5b112e4164666649ccb90760'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('Normal user user217'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user111'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user211'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user311'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user411'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user511')))) and `o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `64ms`, `66ms`, `65ms`, `65ms`, `63ms`
- Row count: `0`
- Error: `ERROR 1105 (HY000): Invalid JSON path expression. The error is around character position 1.`

### Query 5

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('account_id_for_admin_user'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('5b112e4164666649ccb90760'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('nonexistinguser1'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('nonexistinguse2')))) and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and (`o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')) and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('account_id_for_admin_user'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('5b112e4164666649ccb90760'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('nonexistinguser1'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('nonexistinguse2')))) and `o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `64ms`, `63ms`, `66ms`, `64ms`, `63ms`
- Row count: `0`
- Error: `ERROR 1105 (HY000): Invalid JSON path expression. The error is around character position 1.`

### Query 6

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and (`o`.`numeric_value_3` > 0 and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c') and (lower(`o`.`text_value_7`) = 'siemens' and left(`o`.`text_value_7`, 1) != '⁣' and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c') and (lower(`o`.`text_value_20`) like '%⁣4⁣%' and `o`.`text_value_20` != '􏿿' and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c') and (JSON_LENGTH(JSON_EXTRACT(`o`.`other_values_indexed`, CONCAT('$."', '7551dfe3-f09a-4551-ad6c-59478ed5388a', '"'))) > 0 and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and (`o`.`numeric_value_3` > 0 and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))) and (lower(`o`.`text_value_7`) = 'siemens' and left(`o`.`text_value_7`, 1) != '⁣' and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))) and (lower(`o`.`text_value_20`) like '%⁣4⁣%' and `o`.`text_value_20` != '􏿿' and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))) and (JSON_LENGTH(JSON_EXTRACT(`o`.`other_values_indexed`, CONCAT('$."', '7551dfe3-f09a-4551-ad6c-59478ed5388a', '"'))) > 0 and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `1173ms`, `383ms`, `467ms`, `439ms`, `373ms`
- Row count: `0`
- Notes: query is syntactically valid after rewrite, but `other_values_indexed` is `NULL` for all rows on `obj_new`, so the `JSON_LENGTH(...) > 0` predicate eliminates everything.

### Query 7

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and (JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b1905d744c4d0069877712'))) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')) and (JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b1905d744c4d0069877712'))) and `o`.`obj_type_id` = unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `837ms`, `410ms`, `356ms`, `347ms`, `350ms`
- Row count: `0`
- Notes: this one parses, but still returns no rows because `other_values_indexed` is `NULL` everywhere on `obj_new`.

### Query 8

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and ((`o`.`other_values_indexed` is null or JSON_EXTRACT(`o`.`other_values_indexed`, CONCAT('<equation>."', '87037b9c-c26e-4d07-9bc8-5085f330167b', '"')) is null or JSON_LENGTH(JSON_EXTRACT(`o`.`other_values_indexed`, CONCAT('</equation>."', '87037b9c-c26e-4d07-9bc8-5085f330167b', '"'))) = 0) and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15'))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '9963b35f-9397-48ec-9403-adab57aef265' and (`o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-','')) and ((`o`.`other_values_indexed` is null or JSON_EXTRACT(`o`.`other_values_indexed`, CONCAT('<equation>."', '87037b9c-c26e-4d07-9bc8-5085f330167b', '"')) is null or JSON_LENGTH(JSON_EXTRACT(`o`.`other_values_indexed`, CONCAT('</equation>."', '87037b9c-c26e-4d07-9bc8-5085f330167b', '"'))) = 0) and `o`.`obj_type_id` = unhex(replace('bdb2ed93-a797-4c70-882e-63beb2aad85c','-',''))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `674ms`, `97ms`, `100ms`, `112ms`, `110ms`
- Row count: `1000`
- Notes: `obj -> obj_new`; kept the JSON path shape intact and only changed workspace / `obj_type_id`.

## 6. Range Queries

### Query 1

#### Original Query
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`numeric_value_1` > 600 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')) and (`o`.`numeric_value_3` > 0 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

#### Actual Query Run
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '8a6526e6-cd57-4216-bac6-358a6177d221' and (`o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
) and (`o`.`numeric_value_1` > 600 and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
)) and (`o`.`numeric_value_3` > 0 and `o`.`obj_type_id` in (
  unhex(replace('0dfb9fc6-e7c9-4115-bc56-b5baf679b071','-','')),
  unhex(replace('5734a061-b698-4c2a-94ec-700792c86400','-','')),
  unhex(replace('8af8cdb7-1a8b-4932-a466-0f60a68227f4','-','')),
  unhex(replace('bfc6489a-3cb1-43e6-9180-9367e7254edf','-','')),
  unhex(replace('e60ef1f1-dfdb-40b9-a0ac-77d0e4d9d69c','-',''))
))))
order by `o`.`label` asc
limit 1000
offset 0;
```

#### Result
- Latency: `82ms`, `58ms`, `54ms`, `54ms`, `54ms`
- Row count: `1000`

