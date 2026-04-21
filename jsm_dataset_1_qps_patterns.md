# Dataset 1 QPS 压测 Pattern

这页用于定义一组适合 dataset 1 的、规模较小但具有代表性的 QPS 压测 workload，来源是 `jsm_original_queries.md` 里的原始 query 集合。

约定：
- `obj -> obj_new`
- `obj_relationship -> obj_relationship_new`
- 对于存储为 `BINARY(16)` 的 UUID 列，统一使用 `UNHEX(REPLACE(...))` 比较
- 这次压测里，文本搜索只在原始 query 本来是 `LIKE '%...%'` 的情况下，才改写成 `MATCH ... AGAINST`
- 下面的 JQL 是近似的用户语义，不是 Jira 导出的逐字原文

## 纳入本次压测的 Pattern

### Pattern 1：标量过滤 + 按标题排序

对应的 JQL 示例：
```jql
project = JSM AND customNumberA = 548 AND customNumberB = 3 ORDER BY summary
```

对应的 SQL 模板：
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

来源形态：
- `1. Basic Filters / Query 1`

### Pattern 2：由原始 `LIKE '%...%'` 改写来的短语搜索

对应的 JQL 示例：
```jql
project = JSM AND summary ~ "admiral-100000" ORDER BY summary
```

对应的 SQL 模板：
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

说明：
- 这个 pattern 用来覆盖原始 `%...%` 文本搜索家族，在 rewrite 后统一走 `MATCH ... AGAINST`
- 本次压测里，原本“文本等值 / 枚举值过滤”的那一类不单独保留，改由这类 rewritten phrase search 来代表

来源形态：
- `2. Full Text Search / Query 2`

### Pattern 3：多列短语搜索，用 `UNION DISTINCT` 拼接

对应的 JQL 示例：
```jql
project = JSM AND (email ~ "dr.omer.romaguera@emmerich-gibson.example" OR website ~ "www.shelby-torp.info") ORDER BY summary
```

对应的 SQL 模板：
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

说明：
- 这个 pattern 代表“不同 FULLTEXT 列之间做 OR”的查询形态
- 按当前 TiDB/TiCI 的行为，这类查询拆成 `UNION DISTINCT` 通常比在单条 SQL 里并列多个 `MATCH` 更稳

来源形态：
- `2. Full Text Search / Query 3`

### Pattern 4：按自定义字段排序

对应的 JQL 示例：
```jql
project = JSM AND Brand = "LG" ORDER BY customNumberA
```

对应的 SQL 模板：
```sql
select o.sequential_id, o.numeric_value_1
from obj_new o
where o.workspace_id = '<workspace_id>'
  and o.obj_type_id = unhex(replace('<obj_type_uuid>', '-', ''))
  and o.text_value_7 = 'LG'
order by o.numeric_value_1 asc
limit 1000 offset 0;
```

来源形态：
- `3. Sorting / Query 7`

### Pattern 5：CASE 投影后的排序

对应的 JQL 示例：
```jql
project = JSM AND customNumberA = 635 ORDER BY customText24
```

对应的 SQL 模板：
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

来源形态：
- `3. Sorting / Query 1`

### Pattern 6：直接查关系表

对应的 JQL 示例：
```jql
issue in linkedToObject("6df297d1-c20f-35d2-9d0d-08939fd50f17")
```

对应的 SQL 模板：
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

来源形态：
- `1. Basic Filters / Query 10`

### Pattern 7：单跳关系遍历

对应的 JQL 示例：
```jql
project = JSM AND Appliance = "Sharp" AND referencedBy(Brand = "Samsung")
```

对应的 SQL 模板：
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

来源形态：
- `4. Relationship Traversal / Depth 0 / Query 1`

### Pattern 8：多跳关系遍历

对应的 JQL 示例：
```jql
project = JSM AND hasReferencePath(label = "Admiral-1000135", depth = 2) ORDER BY summary
```

对应的 SQL 模板：
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

来源形态：
- `4. Relationship Traversal / Depth 2 / Query 1`

### Pattern 9：数值范围过滤

对应的 JQL 示例：
```jql
project = JSM AND customNumberA > 600 AND customNumberB > 0 ORDER BY summary
```

对应的 SQL 模板：
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

来源形态：
- `6. Range Queries / Query 1`

## 明确不纳入本次压测的 Pattern

### 不纳入 1：单独的文本等值 / 枚举值过滤

原因：
- 这次压测不单独保留这个桶，而是用从原始 `LIKE '%...%'` 改写来的 `MATCH ... AGAINST` 短语搜索来代表文本类 workload

原始 query 中的例子：
- `text_value_23 = 'KitchenAid'`
- `text_value_9 = 'Electrolux'`

### 不纳入 2：原生 `LIKE '%...%'` 或 `LIKE 'prefix%'` 作为独立桶

原因：
- 这次 runbook 希望把 `%...%` 家族统一纳入 `MATCH ... AGAINST`
- 对带标点、连字符、分词边界的前缀搜索，rewrite 后不一定始终和原语义等价，因此不再单独保留 raw `LIKE` 桶

原始 query 中的例子：
- `lower(o.text_value_1) like 'admiral-100008%'`
- `lower(o.text_value_1) like '%admiral-1000048%'`

### 不纳入 3：JSON 属性过滤

原因：
- 当前数据集里 `other_values`、`other_values_indexed`、`group_values` 全部是 `NULL`
- 同时，一部分原始 JSON path 在当前 TiDB 语法下本身也不合法

原始 query 中的例子：
- `JSON_CONTAINS(o.other_values_indexed, ...)`
- `JSON_LENGTH(JSON_EXTRACT(...)) > 0`

### 不纳入 4：恒为 false 的 query

原因：
- 会被化简成 `and 0` 的 query，不代表有意义的搜索 workload，不适合放进 QPS 压测

原始 query 中的例子：
- `1. Basic Filters / Query 3/4/5/12/14/15/17/19`
- `3. Sorting / Query 10`

### 不纳入 5：宽行详情拉取 / hydration 查询

原因：
- 一次性把很多对象字段全部 select 出来的 query，更适合作为搜索后的详情拉取，不适合作为主搜索 workload pattern

原始 query 中的例子：
- `1. Basic Filters / Query 7`

## 当前环境下的一版简单压测计划

### 目标

在当前 dataset 1 集群上，测一版规模不大但足够真实的 QPS mix，重点观察搜索类和关系遍历类 workload，而不是 JSON 或对象详情拉取。

### 第一轮建议纳入的范围

第一轮 mixed workload 建议先用下面这些 pattern：
- Pattern 1：标量过滤 + 按标题排序
- Pattern 2：由原始 `LIKE '%...%'` 改写来的短语搜索
- Pattern 3：多列短语搜索，用 `UNION DISTINCT` 拼接
- Pattern 4：按自定义字段排序
- Pattern 6：直接查关系表
- Pattern 7：单跳关系遍历
- Pattern 9：数值范围过滤

第一轮先不要混进去：
- Pattern 5：CASE 投影后的排序
- Pattern 8：多跳关系遍历

原因：
- 这两类也是有效的 workload 形态，但更重，容易在第一轮 sanity run 里把整体 latency 和资源消耗拉偏

### Query Set 构造方式

每个纳入的 pattern，先准备 `5` 到 `20` 条具体 query：
- 用真实有返回值的 `workspace_id`
- 用真实有返回值的 `obj_type_id`
- 对 `MATCH ... AGAINST` 使用真实存在的短语字面量
- 保持 `limit 1000 offset 0`，和原始 workload 口径一致

建议把这些具体 query 按一条一条 SQL 的形式放进一个 query corpus 文件里。

### 推荐的混合比例

可以先从这组权重开始：
- 25% Pattern 1
- 20% Pattern 2
- 15% Pattern 3
- 15% Pattern 4
- 10% Pattern 6
- 10% Pattern 7
- 5% Pattern 9

这样第一轮会以常见搜索类查询为主，同时也能覆盖到 `obj_relationship_new` 的访问。

### 简单执行计划

1. 预热：
   - 每条具体 query 先串行跑 1 次
   - 先把明显的冷启动噪声压掉
2. 单 pattern 验证：
   - 每个 pattern 分别在并发 `1`、`4`、`8`、`16` 下跑
   - 每轮持续 `3` 到 `5` 分钟
3. 混合 workload：
   - 按上面的权重，在并发 `8`、`16`、`32` 下分别跑
   - 每轮持续 `10` 分钟
4. 关系型加压补充：
   - 如果需要，再把 Pattern 8 加进去，做第二轮 mixed profile

### 工具建议

如果只是做一版简单的第一轮压测：
- 建议在 workstation 上写一个很短的 benchmark driver 脚本
- 脚本只需要做到：
  - 维护连接池
  - 按目标权重随机选 query
  - 记录 QPS、错误数、p50、p95、p99

为什么不直接只用 `mysqlslap`：
- 它适合单 query 或单 pattern 的 smoke test
- 但对这种带权重的 mixed workload 支持比较别扭

### 压测时重点观察什么

最少需要记录：
- 总体 QPS
- p50 / p95 / p99 latency
- 错误数 / 超时数

同时建议关注集群侧热点：
- TiDB CPU 和 session 数
- TiFlash CPU、扫描吞吐、MPP task 数
- TiKV coprocessor latency

### 第一轮压测的成功标准

第一轮做到下面几点，就已经足够有价值：
- 大致知道当前集群能撑住多少 QPS 的混合搜索 workload
- 能看出最先变成瓶颈的是哪类 pattern
- 能判断关系遍历类 query 是否主导了 p95 / p99
- 能确认 rewritten `MATCH ... AGAINST` 查询在并发下是否稳定
