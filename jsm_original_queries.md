# JSM Original Queries

This file stores the original query texts currently covered by `jsm_single_query_latency_results.md`.

## 3. Sorting

### Query 2
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`numeric_value_1` = 846 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```

### Query 3
```sql
select `o`.`sequential_id`, `o`.`text_value_1`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' and ((not lower(`o`.`text_value_7`) = 'blue star' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f') and (`o`.`text_value_8` = 'Samsung' and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f'))
order by `o`.`text_value_1` asc
limit 1000
offset 0
```

### Query 4
```sql
select `o`.`sequential_id`, `o`.`text_value_7`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and ((not lower(`o`.`text_value_7`) = 'electrolux' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15') and (`o`.`text_value_8` = 'Amana' and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15'))
order by `o`.`text_value_7` asc
limit 1000
offset 0
```

### Query 5
```sql
select `o`.`sequential_id`, `o`.`text_value_8`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5' and ((not lower(`o`.`text_value_7`) = 'blue star' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5') and (`o`.`text_value_8` = 'Siemens' and `o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5'))
order by `o`.`text_value_8` asc
limit 1000
offset 0
```

### Query 6
```sql
select `o`.`sequential_id`, `o`.`numeric_value_4`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' and ((not lower(`o`.`text_value_7`) = 'ikea' or lower(`o`.`text_value_7`) = '􏿿') and `o`.`text_value_7` is not null and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f') and (`o`.`text_value_16` = 'Electrolux' and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f'))
order by `o`.`numeric_value_4` asc
limit 1000
offset 0
```

### Query 7
```sql
select `o`.`sequential_id`, `o`.`numeric_value_1`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f' and (`o`.`text_value_7` = 'LG' and `o`.`obj_type_id` = '571d993b-45b0-47e3-b9d0-0e65f44e853f'))
order by `o`.`numeric_value_1` asc
limit 1000
offset 0
```

### Query 8
```sql
select `o`.`sequential_id`, `o`.`numeric_value_3`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5' and (`o`.`text_value_7` = 'Blue Star' and `o`.`obj_type_id` = '4bc0e97a-1789-433d-8969-7fdd61d4c5b5'))
order by `o`.`numeric_value_3` asc
limit 1000
offset 0
```

### Query 9
```sql
select `o`.`sequential_id`, `o`.`numeric_value_2`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and (`o`.`text_value_7` = 'KitchenAid' and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`numeric_value_2` asc
limit 1000
offset 0
```

### Query 10
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and 0
order by `o`.`label` asc
limit 1000
offset 0
```

### Query 11
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

## 4. Relationship Traversal

### Depth 0 / Query 1
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

### Depth 0 / Query 2
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

### Depth 1 / Query 1
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

### Depth 1 / Query 2
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

### Depth 1 / Query 3
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

### Depth 1 / Query 6
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`text_value_24` = 'Electrolux' and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')) and exists (select 1 from `obj_relationship` `subR` inner join `obj` `subO1` on `subR`.`referenced_object_id` = `subO1`.`id` where `o`.`id` = `subR`.`object_id` and `subO1`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598'))
order by `o`.`label` asc
limit 1000
offset 0
```

## 5. JSON Attribute Queries

### Query 1
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b18eaa977c5b007289045d'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b18fffb43d5b006ad51967'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b1905d744c4d0069877712'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b19058977c5b0072891783'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('perf-user1111')))) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

### Query 2
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('account_id_for_admin_user'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('5b112e4164666649ccb90760'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('nonexistinguser')))) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

### Query 3
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('Normal user user211')))) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

### Query 4
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('account_id_for_admin_user'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('5b112e4164666649ccb90760'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('Normal user user217'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user111'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user211'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user311'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user411'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('user511')))) and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15'))
order by `o`.`label` asc
limit 1000
offset 0
```

### Query 5
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and ((JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('account_id_for_admin_user'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('5b112e4164666649ccb90760'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '<equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('uui999uee3331'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '</equation>."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('nonexistinguser1'))) or JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."87037b9c-c26e-4d07-9bc8-5085f330167b"', JSON_ARRAY('nonexistinguse2')))) and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15'))
order by `o`.`label` asc
limit 1000
offset 0
```

### Query 6
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and (`o`.`numeric_value_3` > 0 and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c') and (lower(`o`.`text_value_7`) = 'siemens' and left(`o`.`text_value_7`, 1) != '⁣' and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c') and (lower(`o`.`text_value_20`) like '%⁣4⁣%' and `o`.`text_value_20` != '􏿿' and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c') and (JSON_LENGTH(JSON_EXTRACT(`o`.`other_values_indexed`, CONCAT('$."', '7551dfe3-f09a-4551-ad6c-59478ed5388a', '"'))) > 0 and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

### Query 7
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c' and (JSON_CONTAINS(`o`.`other_values_indexed`, JSON_SET(CAST('{}' AS JSON), '$."7551dfe3-f09a-4551-ad6c-59478ed5388a"', JSON_ARRAY('61b1905d744c4d0069877712'))) and `o`.`obj_type_id` = '4812f881-af30-4227-afb7-107aedb7f40c'))
order by `o`.`label` asc
limit 1000
offset 0
```

### Query 8
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15' and ((`o`.`other_values_indexed` is null or JSON_EXTRACT(`o`.`other_values_indexed`, CONCAT('<equation>."', '87037b9c-c26e-4d07-9bc8-5085f330167b', '"')) is null or JSON_LENGTH(JSON_EXTRACT(`o`.`other_values_indexed`, CONCAT('</equation>."', '87037b9c-c26e-4d07-9bc8-5085f330167b', '"'))) = 0) and `o`.`obj_type_id` = 'bcf3698a-4175-42a9-8666-43d1bc8ecd15'))
order by `o`.`label` asc
limit 1000
offset 0
```

## 6. Range Queries

### Query 1
```sql
select `o`.`sequential_id`, `o`.`label`
from `obj` `o`
where `o`.`workspace_id` = '3264257b-7e21-44e2-ada3-fd1117ede598' and (`o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555') and (`o`.`numeric_value_1` > 600 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')) and (`o`.`numeric_value_3` > 0 and `o`.`obj_type_id` in ('4812f881-af30-4227-afb7-107aedb7f40c', '4bc0e97a-1789-433d-8969-7fdd61d4c5b5', '571d993b-45b0-47e3-b9d0-0e65f44e853f', 'bcf3698a-4175-42a9-8666-43d1bc8ecd15', 'cab76eba-265a-411c-8201-54d4ed4cf555')))
order by `o`.`label` asc
limit 1000
offset 0
```
