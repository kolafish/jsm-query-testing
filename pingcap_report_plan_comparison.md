# PingCAP Report Plan Comparison

Generated at: `2026-05-11T03:25:07.902635+00:00`

Source report: `reports/pingcap-query-performance-2026-05-06/full_report_for_pingcap.md`

Comparison checks stable plan shape: operator topology, storage task set, join operators, scanned tables, and index access paths. Runtime row counts and latency are intentionally ignored.

Summary: 一致 9, 兼容 6, 不一致 7, 错误 0, 未检查 3.

结论口径：`一致` 表示稳定 plan shape 和 access path 都一致；`兼容` 表示只差 Projection/Selection wrapper 或索引名但索引列一致；`不一致` 表示 join/task/index path 有实质差异；`未检查` 表示当前没有可用 sampled SQL。

## Query-Level Comparison

| Query | Pattern | 结论 | 主要差异 | 客户文档 plan | 当前集群 plan |
|---:|---|---|---|---|---|
| 1 |  | 未检查 | 当前没有 sampled SQL，所以没有抓到 current EXPLAIN；需要补样本后再比。 | cop[tikv], root; IndexLookUp -> IndexRangeScan -> TableRowIDScan; ct1_0.obj_type_attr_fk(obj_type_attr_id) | n/a |
| 2 | HIGH_COP_WAIT — IN() lookup | 一致 | Plan shape、task set、join/index access path 都一致。 | cop[tikv], root; IndexLookUp -> IndexRangeScan -> TableRowIDScan; obj_relationship.ix_obj_rel_object_id_without_partition(object_id) | cop[tikv], root; IndexLookUp -> IndexRangeScan -> TableRowIDScan; obj_relationship.ix_obj_rel_object_id_without_partition(object_id) |
| 3 | HIGH_COP_WAIT — deep IndexJoin chain (stats:pseudo) | 未检查 | 当前没有 sampled SQL，所以没有抓到 current EXPLAIN；需要补样本后再比。 | cop[tikv], root; IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> HashJoin -> TableReader -> TableFullScan -> IndexJoin -> Point_Get -> TableReader -> TableRangeScan -> TableReader -> TableRangeScan -> Ta... | n/a |
| 4 | EXCESSIVE_SCAN + JSON_CONTAINS post-filter | 一致 | Plan shape、task set、join/index access path 都一致。 | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) |
| 5 | EXCESSIVE_SCAN + JSON_CONTAINS post-filter | 一致 | Plan shape、task set、join/index access path 都一致。 | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) |
| 6 |  | 兼容 | 只差 Projection/Selection wrapper，核心读取路径一致。 | root; Batch_Point_Get; no index | root; Batch_Point_Get; no index |
| 7 |  | 一致 | Plan shape、task set、join/index access path 都一致。 | cop[tikv], root; IndexHashJoin -> Point_Get -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position) | cop[tikv], root; IndexHashJoin -> Point_Get -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position) |
| 8 | EXCESSIVE_SCAN — FTS + cross-storage post-filter | 兼容 | 仅 FTS 索引名不同，索引列相同：text_value_22；整体 plan shape 一致。 | cop[tici], cop[tikv], root; TopN -> IndexLookUp -> IndexRangeScan -> TopN -> TableRowIDScan; o.idx_fts_text_value_22(text_value_22) | cop[tici], cop[tikv], root; TopN -> IndexLookUp -> IndexRangeScan -> TopN -> TableRowIDScan; o.idx_fts_22(text_value_22) |
| 9 | HIGH_COP_WAIT — IN() lookup | 一致 | Plan shape、task set、join/index access path 都一致。 | cop[tikv], root; IndexLookUp -> IndexRangeScan -> TableRowIDScan; obj_relationship.ix_obj_rel_object_id_without_partition(object_id) | cop[tikv], root; IndexLookUp -> IndexRangeScan -> TableRowIDScan; obj_relationship.ix_obj_rel_object_id_without_partition(object_id) |
| 10 | EXCESSIVE_SCAN + JSON_CONTAINS post-filter | 兼容 | 只差 Projection/Selection wrapper，核心读取路径一致。 | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) |
| 11 |  | 兼容 | 只差 Projection/Selection wrapper，核心读取路径一致。 | root; Point_Get; no index | root; Point_Get; no index |
| 12 |  | 未检查 | 当前没有 sampled SQL，所以没有抓到 current EXPLAIN；需要补样本后再比。 | cop[tikv], root; IndexJoin -> IndexJoin -> IndexJoin -> HashJoin -> TableReader -> TableFullScan -> IndexJoin -> Point_Get -> TableReader -> TableRangeScan -> IndexLookUp -> IndexRangeScan -> TableRowIDScan -> IndexLookUp -> IndexRangeScan -> TableRowIDScan -... | n/a |
| 13 |  | 一致 | Plan shape、task set、join/index access path 都一致。 | cop[tikv], root; IndexHashJoin -> Batch_Point_Get -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position) | cop[tikv], root; IndexHashJoin -> Batch_Point_Get -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position) |
| 14 |  | 不一致 | 客户文档走 text_value_7_lower 复合索引 + IndexLookUp；当前走 TableRangeScan/TableReader，未走该索引。 | cop[tikv], root; TopN -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | cop[tikv], root; TopN -> TableReader -> TableRangeScan; TableRangeScan on o |
| 15 | HIGH_COP_WAIT — IndexLookUp fanout | 不一致 | 客户文档走 text_value_7_lower 复合索引 + IndexLookUp；当前走 TableRangeScan/TableReader，未走该索引。 | cop[tikv], root; TopN -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | cop[tikv], root; TopN -> TableReader -> TableRangeScan; TableRangeScan on o |
| 16 | HIGH_COP_WAIT — IndexLookUp fanout | 不一致 | 客户文档走 text_value_7_lower 复合索引 + IndexLookUp；当前走 TableRangeScan/TableReader，未走该索引。 | cop[tikv], root; TopN -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | cop[tikv], root; TopN -> TableReader -> TableRangeScan; TableRangeScan on o |
| 17 | EXCESSIVE_SCAN + JSON_CONTAINS post-filter | 一致 | Plan shape、task set、join/index access path 都一致。 | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) |
| 18 |  | 兼容 | 只差 Projection/Selection wrapper，核心读取路径一致。 | root; Batch_Point_Get; no index | root; Batch_Point_Get; no index |
| 19 | HIGH_COP_WAIT — IndexLookUp fanout | 不一致 | 客户文档走 text_value_7_lower 复合索引 + IndexLookUp；当前走 TableRangeScan/TableReader，未走该索引。 | cop[tikv], root; TopN -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | cop[tikv], root; TopN -> TableReader -> TableRangeScan; TableRangeScan on o |
| 20 |  | 一致 | Plan shape、task set、join/index access path 都一致。 | cop[tikv], root; IndexLookUp -> IndexRangeScan -> TableRowIDScan; otae1_0.obj_type_attr__workspace_id__sequential_id__idx(workspace_id, sequential_id) | cop[tikv], root; IndexLookUp -> IndexRangeScan -> TableRowIDScan; otae1_0.obj_type_attr__workspace_id__sequential_id__idx(workspace_id, sequential_id) |
| 21 |  | 不一致 | relationship 侧索引和读取方式不同：客户文档用 object_id 单列索引 + IndexLookUp；当前用 object_id/workspace_id/object_type_attribute_id/referenced_object_id 复合索引 + IndexReader，且 task 标记为 mpp[tiflash]。 | cop[tiflash], cop[tikv], root; TopN -> HashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> IndexHashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; subR.ix_obj_rel_object_id_without_partit... | cop[tikv], mpp[tiflash], root; TopN -> HashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> IndexHashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> IndexReader -> IndexRangeScan; subr.idx_obj_relationship_new_object_ws_ota_ref(object_id,... |
| 22 |  | 兼容 | 只差 Projection/Selection wrapper，核心读取路径一致。 | root; Batch_Point_Get; no index | root; Batch_Point_Get; no index |
| 23 |  | 一致 | Plan shape、task set、join/index access path 都一致。 | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | cop[tikv], root; Limit -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) |
| 24 |  | 不一致 | join 下推形态差异较大：客户文档是 root HashJoin/IndexHashJoin + TiKV/TiFlash 混合读取；当前主要是 mpp[tiflash]，没有检测到文档里的 relationship/object 索引路径。 | cop[tiflash], cop[tikv], root; TopN -> HashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> HashJoin -> HashJoin -> IndexHashJoin -> IndexReader -> IndexRangeScan -> IndexLookUp -> IndexRangeScan -> TableRowIDScan -> IndexHashJoin -> TableReader ->.... | mpp[tiflash], root; TopN -> TableReader -> ExchangeSender -> TopN -> HashJoin -> ExchangeReceiver -> ExchangeSender -> TableRangeScan -> ExchangeReceiver -> ExchangeSender -> HashJoin -> ExchangeReceiver -> ExchangeSender -> HashJoin -> ExchangeReceiver -> Ex... |
| 25 |  | 不一致 | 索引列不同：客户文档用 text_value_7_lower 复合索引；当前用 text_value_7/numeric_value_1/sequential_id 复合索引。整体算子拓扑接近，但 access path 不一致。 | cop[tikv], root; TopN -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | cop[tikv], root; TopN -> IndexLookUp -> IndexRangeScan -> TableRowIDScan; o.idx_obj_new_ws_ot_tv7_num1_seq(workspace_id, obj_type_id, text_value_7, numeric_value_1, sequential_id) |

<details>
<summary>Raw plan shape signatures</summary>

### Query 1

- Status: `pending`
- Source topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `ct1_0.obj_type_attr_fk(obj_type_attr_id)`
- Current plan: not captured yet.

### Query 2

- Status: `match`
- Source topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `obj_relationship.ix_obj_rel_object_id_without_partition(object_id)`
- Current sample: `s1`
- Current topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `obj_relationship.ix_obj_rel_object_id_without_partition(object_id)`

### Query 3

- Status: `pending`
- Source topology: `Projection -> Projection -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> HashJoin -> TableReader -> Selection -> TableFullScan -> IndexJoin -> Selection -> Point_Get -> TableReader -> Selection -> TableRangeScan -> TableReader -> Selection -> TableRangeScan -> TableReader -> Selection -> TableRangeScan -> TableReader -> Selection -> TableRangeScan -> TableReader -> Selection -> TableRangeScan -> IndexLookUp -> Selection -> IndexRangeSca...`
- Source task topology: `Projection[root] -> Projection[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> HashJoin[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableFullScan[cop[tikv]] -> IndexJoin[root] -> Selection[root] -> Point_Get[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]] -> TableReader...`
- Source indexes: `ct1_0.obj_type_fk(obj_type_id), ct2_0.obj_schema_fk(obj_schema_id), ct3_0.obj_type_fk(obj_type_id)`
- Current plan: not captured yet.

### Query 4

- Status: `match`
- Source topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 5

- Status: `match`
- Source topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 6

- Status: `compatible`
- Source topology: `Projection -> Batch_Point_Get`
- Source task topology: `Projection[root] -> Batch_Point_Get[root]`
- Source indexes: `n/a`
- Current sample: `s1`
- Current topology: `Batch_Point_Get`
- Current task topology: `Batch_Point_Get[root]`
- Current indexes: `n/a`

### Query 7

- Status: `match`
- Source topology: `Projection -> IndexHashJoin -> Selection -> Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexHashJoin[root] -> Selection[root] -> Point_Get[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position)`
- Current sample: `s1`
- Current topology: `Projection -> IndexHashJoin -> Selection -> Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexHashJoin[root] -> Selection[root] -> Point_Get[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position)`

### Query 8

- Status: `compatible`
- Source topology: `TopN -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> TopN -> Selection -> TableRowIDScan`
- Source task topology: `TopN[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tici]] -> IndexRangeScan[cop[tici]] -> TopN[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.idx_fts_text_value_22(text_value_22)`
- Current sample: `s1`
- Current topology: `TopN -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> TopN -> Selection -> TableRowIDScan`
- Current task topology: `TopN[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tici]] -> IndexRangeScan[cop[tici]] -> TopN[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.idx_fts_22(text_value_22)`

### Query 9

- Status: `match`
- Source topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `obj_relationship.ix_obj_rel_object_id_without_partition(object_id)`
- Current sample: `s1`
- Current topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `obj_relationship.ix_obj_rel_object_id_without_partition(object_id)`

### Query 10

- Status: `compatible`
- Source topology: `Projection -> Limit -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> Limit[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 11

- Status: `compatible`
- Source topology: `Projection -> Selection -> Point_Get`
- Source task topology: `Projection[root] -> Selection[root] -> Point_Get[root]`
- Source indexes: `n/a`
- Current sample: `s1`
- Current topology: `Point_Get`
- Current task topology: `Point_Get[root]`
- Current indexes: `n/a`

### Query 12

- Status: `pending`
- Source topology: `Projection -> Projection -> IndexJoin -> IndexJoin -> IndexJoin -> HashJoin -> TableReader -> Selection -> TableFullScan -> IndexJoin -> Selection -> Point_Get -> TableReader -> Selection -> TableRangeScan -> IndexLookUp -> Selection -> IndexRangeScan -> TableRowIDScan -> IndexLookUp -> IndexRangeScan -> TableRowIDScan -> TableReader -> TableRangeScan`
- Source task topology: `Projection[root] -> Projection[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> HashJoin[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableFullScan[cop[tikv]] -> IndexJoin[root] -> Selection[root] -> Point_Get[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]] -...`
- Source indexes: `ct1_0.ref_type_fk(ref_type_id), ct2_0.obj_schema_fk(obj_schema_id)`
- Current plan: not captured yet.

### Query 13

- Status: `match`
- Source topology: `Projection -> IndexHashJoin -> Selection -> Batch_Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexHashJoin[root] -> Selection[root] -> Batch_Point_Get[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position)`
- Current sample: `s1`
- Current topology: `Projection -> IndexHashJoin -> Selection -> Batch_Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexHashJoin[root] -> Selection[root] -> Batch_Point_Get[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position)`

### Query 14

- Status: `mismatch`
- Source topology: `TopN -> Selection -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `TopN[root] -> Selection[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> TableReader -> Selection -> TableRangeScan`
- Current task topology: `TopN[root] -> Selection[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]]`
- Current indexes: `n/a`

### Query 15

- Status: `mismatch`
- Source topology: `TopN -> Selection -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `TopN[root] -> Selection[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> TableReader -> Selection -> TableRangeScan`
- Current task topology: `TopN[root] -> Selection[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]]`
- Current indexes: `n/a`

### Query 16

- Status: `mismatch`
- Source topology: `Projection -> TopN -> Selection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> TopN[root] -> Selection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> TableReader -> Selection -> TableRangeScan`
- Current task topology: `TopN[root] -> Selection[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]]`
- Current indexes: `n/a`

### Query 17

- Status: `match`
- Source topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 18

- Status: `compatible`
- Source topology: `Projection -> Selection -> Batch_Point_Get`
- Source task topology: `Projection[root] -> Selection[root] -> Batch_Point_Get[root]`
- Source indexes: `n/a`
- Current sample: `s1`
- Current topology: `Selection -> Batch_Point_Get`
- Current task topology: `Selection[root] -> Batch_Point_Get[root]`
- Current indexes: `n/a`

### Query 19

- Status: `mismatch`
- Source topology: `TopN -> Selection -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `TopN[root] -> Selection[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> TableReader -> Selection -> TableRangeScan`
- Current task topology: `TopN[root] -> Selection[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]]`
- Current indexes: `n/a`

### Query 20

- Status: `match`
- Source topology: `Projection -> IndexLookUp -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `otae1_0.obj_type_attr__workspace_id__sequential_id__idx(workspace_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Projection -> IndexLookUp -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `otae1_0.obj_type_attr__workspace_id__sequential_id__idx(workspace_id, sequential_id)`

### Query 21

- Status: `mismatch`
- Source topology: `TopN -> HashJoin -> TableReader -> ExchangeSender -> Selection -> TableRangeScan -> IndexHashJoin -> TableReader -> ExchangeSender -> Selection -> TableRangeScan -> Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `TopN[root] -> HashJoin[root] -> TableReader[root] -> ExchangeSender[cop[tiflash]] -> Selection[cop[tiflash]] -> TableRangeScan[cop[tiflash]] -> IndexHashJoin[root] -> TableReader[root] -> ExchangeSender[cop[tiflash]] -> Selection[cop[tiflash]] -> TableRangeScan[cop[tiflash]] -> Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `subR.ix_obj_rel_object_id_without_partition(object_id)`
- Current sample: `s1`
- Current topology: `TopN -> HashJoin -> TableReader -> ExchangeSender -> Selection -> TableRangeScan -> IndexHashJoin -> TableReader -> ExchangeSender -> Selection -> TableRangeScan -> IndexReader -> IndexRangeScan`
- Current task topology: `TopN[root] -> HashJoin[root] -> TableReader[root] -> ExchangeSender[mpp[tiflash]] -> Selection[mpp[tiflash]] -> TableRangeScan[mpp[tiflash]] -> IndexHashJoin[root] -> TableReader[root] -> ExchangeSender[mpp[tiflash]] -> Selection[mpp[tiflash]] -> TableRangeScan[mpp[tiflash]] -> IndexReader[root] -> IndexRangeScan[cop[tikv]]`
- Current indexes: `subr.idx_obj_relationship_new_object_ws_ota_ref(object_id, workspace_id, object_type_attribute_id, referenced_object_id)`

### Query 22

- Status: `compatible`
- Source topology: `Projection -> Selection -> Batch_Point_Get`
- Source task topology: `Projection[root] -> Selection[root] -> Batch_Point_Get[root]`
- Source indexes: `n/a`
- Current sample: `s1`
- Current topology: `Selection -> Batch_Point_Get`
- Current task topology: `Selection[root] -> Batch_Point_Get[root]`
- Current indexes: `n/a`

### Query 23

- Status: `match`
- Source topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 24

- Status: `mismatch`
- Source topology: `TopN -> HashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> HashJoin -> HashJoin -> IndexHashJoin -> IndexReader -> IndexRangeScan -> Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan -> Projection -> IndexHashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan -> Projection -> IndexHashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `TopN[root] -> HashJoin[root] -> TableReader[root] -> ExchangeSender[cop[tiflash]] -> TableRangeScan[cop[tiflash]] -> HashJoin[root] -> HashJoin[root] -> IndexHashJoin[root] -> IndexReader[root] -> IndexRangeScan[cop[tikv]] -> Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]] -> Projection[root] -> IndexHashJoin[root] -> TableReader[root] -> ExchangeSender[cop[tiflash]] -> TableRangeScan[cop[tiflash]] -> Projection[root] -> IndexLookUp[root] -> Index...`
- Source indexes: `subO3.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id), subR.ix_obj_rel_referenced_object_id_without_partition(referenced_object_id), subR1.ix_obj_rel_referenced_object_id_without_partition(referenced_object_id), subR2.ix_obj_rel_referenced_object_id_without_partition(referenced_object_id)`
- Current sample: `s1`
- Current topology: `TopN -> TableReader -> ExchangeSender -> TopN -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> TableRangeScan -> ExchangeReceiver -> ExchangeSender -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> TableRangeScan -> TableFullScan -> Projection -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> TableRangeScan -> Exchang...`
- Current task topology: `TopN[root] -> TableReader[root] -> ExchangeSender[mpp[tiflash]] -> TopN[mpp[tiflash]] -> Projection[mpp[tiflash]] -> HashJoin[mpp[tiflash]] -> ExchangeReceiver[mpp[tiflash]] -> ExchangeSender[mpp[tiflash]] -> TableRangeScan[mpp[tiflash]] -> ExchangeReceiver[mpp[tiflash]] -> ExchangeSender[mpp[tiflash]] -> Projection[mpp[tiflash]] -> HashJoin[mpp[tiflash]] -> ExchangeReceiver[mpp[tiflash]] -> ExchangeSender[mpp[tiflash]] -> Projection[mpp[tiflash]] -> HashJoin[mpp[tiflash]] -> ExchangeReceiver[m...`
- Current indexes: `n/a`

### Query 25

- Status: `mismatch`
- Source topology: `Projection -> TopN -> Selection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> TopN[root] -> Selection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> IndexLookUp -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `TopN[root] -> Selection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.idx_obj_new_ws_ot_tv7_num1_seq(workspace_id, obj_type_id, text_value_7, numeric_value_1, sequential_id)`

</details>

