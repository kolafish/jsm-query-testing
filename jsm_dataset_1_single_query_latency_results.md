# JSM Query Results

Generated on 2026-04-20.

Scope:
- Start from `3. Sorting / Query 2`
- Apply session rewrite rules:
  - `obj -> obj_new`
  - `obj_relationship -> obj_relationship_new`
  - replace `workspace_id` / `obj_type_id` / `object_id` with real values that hit
  - use `UNHEX(REPLACE(...))` for `BINARY(16)` UUID columns
  - rewrite `LIKE` to `MATCH ... AGAINST` when applicable
  - add `ngram FULLTEXT` only when needed and possible
- Keep original query numbering even when a query errors or returns no rows after rewrite.
- For failed queries, preserve:
  - original query
  - actual query attempted
  - error or non-hit reason

Global note:
- `obj_new.other_values_indexed` is currently `NULL` for all rows (`COUNT(*) WHERE other_values_indexed IS NOT NULL = 0`).
- Because of that, JSON queries that require positive `JSON_CONTAINS(...)`, `JSON_LENGTH(...) > 0`, or direct key hits on `other_values_indexed` will not have matching rows after the mandatory `obj -> obj_new` rewrite.

## 3. Sorting

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
