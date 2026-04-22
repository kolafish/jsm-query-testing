# JSM Assets3 Full Text LIKE vs MATCH Comparison

This document compares the original `LIKE` form and a `MATCH AGAINST` rewrite for the `Full Text Search` query group on `jsm_assets3.obj_new`.

- Table changes: `obj -> obj_new`
- UUID handling: binary UUID comparisons rewritten to `UNHEX(REPLACE(...))`
- Row count: `select count(*) from (<query>) q` on the actual query shape
- DB latency: `EXPLAIN ANALYZE` top operator time

## Index Coverage

| Column | FULLTEXT index |
| --- | --- |
| `text_value_1` | `idx_obj_new_text_value_1_ngram` (`NGRAM`) |
| `text_value_4` | `idx_obj_new_text_value_4_ngram` (`NGRAM`) |
| `text_value_5` | `idx_obj_new_text_value_5_ngram` (`NGRAM`) |
| `text_value_10` | none |

## Comparison

| Query | Column(s) | FULLTEXT index | LIKE rows | LIKE DB latency (ms) | MATCH rows | MATCH DB latency (ms) | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Full Text Search / Query 1 | `text_value_1` | idx_obj_new_text_value_1_ngram (NGRAM) | 5 | 41.5 | 1000 | 1110.0 | prefix LIKE; MATCH candidate uses boolean prefix syntax, not exact-equivalent for hyphenated prefix |
| Full Text Search / Query 2 | `text_value_1` | idx_obj_new_text_value_1_ngram (NGRAM) | 2 | 43.7 | 2 | 6.55 | contains semantics; MATCH uses quoted phrase |
| Full Text Search / Query 3 | `text_value_4 + text_value_5` | idx_obj_new_text_value_4_ngram (NGRAM); idx_obj_new_text_value_5_ngram (NGRAM) | 3 | 64.6 | 3 | 6.14 | cross-column OR rewritten as UNION DISTINCT |
| Full Text Search / Query 4 | `text_value_4 + text_value_5 + text_value_10` | idx_obj_new_text_value_4_ngram (NGRAM); idx_obj_new_text_value_5_ngram (NGRAM); text_value_10 has no FULLTEXT index | 1000 | 78.3 | 1000 | 89.7 | LIKE branches rewritten to MATCH; equality branch on text_value_10 kept as-is |
| Full Text Search / Query 5 | `text_value_5` | idx_obj_new_text_value_5_ngram (NGRAM) | 1 | 43.8 | 1 | 4.47 | contains semantics; MATCH uses quoted phrase |
| Full Text Search / Query 6 | `text_value_4` | idx_obj_new_text_value_4_ngram (NGRAM) | 4 | 80.9 | 4 | 9.51 | same-column OR rewritten to a single MATCH with multiple quoted phrases |
| Full Text Search / Query 7 | `text_value_5` | idx_obj_new_text_value_5_ngram (NGRAM) | 1 | 60.7 | 1 | 4.74 | contains semantics; MATCH uses quoted phrase |

## SQL

### Full Text Search / Query 1

**LIKE**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
       and (lower(`o`.`text_value_1`) like 'admiral-100008%'
            and `o`.`text_value_1` != '\U0010ffff'
            and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))))
order by `o`.`label` asc
limit 1000
offset 0;
```

**MATCH AGAINST**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
       and (match(`o`.`text_value_1`) against('admiral-100008*' in boolean mode)
            and `o`.`text_value_1` != '\U0010ffff'
            and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))))
order by `o`.`label` asc
limit 1000
offset 0;
```

### Full Text Search / Query 2

**LIKE**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
       and (lower(`o`.`text_value_1`) like '%admiral-1000048%'
            and `o`.`text_value_1` != '\U0010ffff'))
order by `o`.`label` asc
limit 1000
offset 0;
```

**MATCH AGAINST**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
       and (match(`o`.`text_value_1`) against('"admiral-1000048"' in boolean mode)
            and `o`.`text_value_1` != '\U0010ffff'))
order by `o`.`label` asc
limit 1000
offset 0;
```

### Full Text Search / Query 3

**LIKE**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-',''))) and (
    `o`.`text_value_4` like '%dr.omer.romaguera@emmerich-gibson.example%'
      and `o`.`text_value_4` != '\U0010ffff'
      and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
    or `o`.`text_value_5` like '%www.shelby-torp.info%'
      and `o`.`text_value_5` != '\U0010ffff'
      and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
  ))
order by `o`.`label` asc
limit 1000
offset 0;
```

**MATCH AGAINST**
```sql
(
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
  and `o`.`text_value_4` != '\U0010ffff'
  and match(`o`.`text_value_4`) against('"dr.omer.romaguera@emmerich-gibson.example"' in boolean mode)
)
union distinct
(
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
  and `o`.`text_value_5` != '\U0010ffff'
  and match(`o`.`text_value_5`) against('"www.shelby-torp.info"' in boolean mode)
)
order by `label` asc
limit 1000
offset 0;
```

### Full Text Search / Query 4

**LIKE**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-',''))) and (
    `o`.`text_value_4` like '%maren.heller@welch.test%'
      and `o`.`text_value_4` != '\U0010ffff'
      and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
    or `o`.`text_value_5` like '%www.leonor-hamill.io%'
      and `o`.`text_value_5` != '\U0010ffff'
      and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
    or `o`.`text_value_10` = 'Fagor'
      and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
  ))
order by `o`.`label` asc
limit 1000
offset 0;
```

**MATCH AGAINST**
```sql
(
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
  and `o`.`text_value_4` != '\U0010ffff'
  and match(`o`.`text_value_4`) against('"maren.heller@welch.test"' in boolean mode)
)
union distinct
(
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
  and `o`.`text_value_5` != '\U0010ffff'
  and match(`o`.`text_value_5`) against('"www.leonor-hamill.io"' in boolean mode)
)
union distinct
(
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
  and `o`.`text_value_10` = 'Fagor'
)
order by `label` asc
limit 1000
offset 0;
```

### Full Text Search / Query 5

**LIKE**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
       and (`o`.`text_value_5` like '%www.royal-simonis.biz%'
            and `o`.`text_value_5` != '\U0010ffff'
            and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))))
order by `o`.`label` asc
limit 1000
offset 0;
```

**MATCH AGAINST**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
       and (match(`o`.`text_value_5`) against('"www.royal-simonis.biz"' in boolean mode)
            and `o`.`text_value_5` != '\U0010ffff'
            and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))))
order by `o`.`label` asc
limit 1000
offset 0;
```

### Full Text Search / Query 6

**LIKE**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-',''))) and ((lower(`o`.`text_value_4`) like '%alpha.nolan@hills.example%'
      or lower(`o`.`text_value_4`) like '%fr.zena.ruecker@baumbach-runolfsson.test%'
      or lower(`o`.`text_value_4`) like '%holli.goodwin@cruickshank.test%'
      or lower(`o`.`text_value_4`) like '%dr.odell.feeney@dickens.example%')
      and `o`.`text_value_4` != '\U0010ffff'
      and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))))
order by `o`.`label` asc
limit 1000
offset 0;
```

**MATCH AGAINST**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-',''))) and (
       match(`o`.`text_value_4`) against('"alpha.nolan@hills.example" "fr.zena.ruecker@baumbach-runolfsson.test" "holli.goodwin@cruickshank.test" "dr.odell.feeney@dickens.example"' in boolean mode)
       and `o`.`text_value_4` != '\U0010ffff'
       and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))))
order by `o`.`label` asc
limit 1000
offset 0;
```

### Full Text Search / Query 7

**LIKE**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
       and (lower(`o`.`text_value_5`) like '%www.nick-bauch.name%'
            and `o`.`text_value_5` != '\U0010ffff'
            and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))))
order by `o`.`label` asc
limit 1000
offset 0;
```

**MATCH AGAINST**
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj_new` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'
  and (`o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))
       and (match(`o`.`text_value_5`) against('"www.nick-bauch.name"' in boolean mode)
            and `o`.`text_value_5` != '\U0010ffff'
            and `o`.`obj_type_id` in (unhex(replace('4812f881-af30-4227-afb7-107aedb7f40c','-','')), unhex(replace('4bc0e97a-1789-433d-8969-7fdd61d4c5b5','-','')), unhex(replace('571d993b-45b0-47e3-b9d0-0e65f44e853f','-','')), unhex(replace('bcf3698a-4175-42a9-8666-43d1bc8ecd15','-','')), unhex(replace('cab76eba-265a-411c-8201-54d4ed4cf555','-','')))))
order by `o`.`label` asc
limit 1000
offset 0;
```

