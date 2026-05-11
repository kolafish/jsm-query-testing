# PingCAP Report Plan Comparison

Generated at: `2026-05-11T03:09:28.487886+00:00`

Source report: `reports/pingcap-query-performance-2026-05-06/full_report_for_pingcap.md`

Comparison checks the stable plan shape: operator topology, storage task set, join operators, scanned tables, and index access paths. Runtime row counts and latency are intentionally ignored.

## Summary

| Status | Count |
|---|---:|
| match | 9 |
| compatible | 6 |
| mismatch | 7 |
| error | 0 |
| pending | 3 |

## Query Plan Shape

| Query | Source pattern | Source task set | Source top operators | Source indexes | Current status | Difference |
|---:|---|---|---|---|---|---|
| 1 |  | cop[tikv], root | Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan | ct1_0.obj_type_attr_fk(obj_type_attr_id) | pending | current plan not captured |
| 2 | HIGH_COP_WAIT — IN() lookup | cop[tikv], root | Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan | obj_relationship.ix_obj_rel_object_id_without_partition(object_id) | match | n/a |
| 3 | HIGH_COP_WAIT — deep IndexJoin chain (stats:pseudo) | cop[tikv], root | Projection -> Projection -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> HashJoi... | ct1_0.obj_type_fk(obj_type_id), ct2_0.obj_schema_fk(obj_schema_id), ct3_0.obj_type_fk(obj_type_id) | pending | current plan not captured |
| 4 | EXCESSIVE_SCAN + JSON_CONTAINS post-filter | cop[tikv], root | Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | match | n/a |
| 5 | EXCESSIVE_SCAN + JSON_CONTAINS post-filter | cop[tikv], root | Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | match | n/a |
| 6 |  | root | Projection -> Batch_Point_Get | n/a | compatible | operator topology differs only by Projection wrapper |
| 7 |  | cop[tikv], root | Projection -> IndexHashJoin -> Selection -> Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position) | match | n/a |
| 8 | EXCESSIVE_SCAN — FTS + cross-storage post-filter | cop[tici], cop[tikv], root | TopN -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> TopN -> Selection -> TableRowIDScan | o.idx_fts_text_value_22(text_value_22) | compatible | index name differs but indexed columns match: source=['o.idx_fts_text_value_22(text_value_22)'] current=['o.idx_fts_22(text_value_22)'] |
| 9 | HIGH_COP_WAIT — IN() lookup | cop[tikv], root | Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan | obj_relationship.ix_obj_rel_object_id_without_partition(object_id) | match | n/a |
| 10 | EXCESSIVE_SCAN + JSON_CONTAINS post-filter | cop[tikv], root | Projection -> Limit -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | compatible | operator topology differs only by Projection wrapper |
| 11 |  | root | Projection -> Selection -> Point_Get | n/a | compatible | operator topology differs only by Projection wrapper |
| 12 |  | cop[tikv], root | Projection -> Projection -> IndexJoin -> IndexJoin -> IndexJoin -> HashJoin -> TableReader -> Selection -> TableFullScan -> IndexJoin -> Se... | ct1_0.ref_type_fk(ref_type_id), ct2_0.obj_schema_fk(obj_schema_id) | pending | current plan not captured |
| 13 |  | cop[tikv], root | Projection -> IndexHashJoin -> Selection -> Batch_Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position) | match | n/a |
| 14 |  | cop[tikv], root | TopN -> Selection -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | mismatch | operator topology differs; index access differs: source=['o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)'] current=[] |
| 15 | HIGH_COP_WAIT — IndexLookUp fanout | cop[tikv], root | TopN -> Selection -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | mismatch | operator topology differs; index access differs: source=['o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)'] current=[] |
| 16 | HIGH_COP_WAIT — IndexLookUp fanout | cop[tikv], root | Projection -> TopN -> Selection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | mismatch | operator topology differs; index access differs: source=['o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)'] current=[] |
| 17 | EXCESSIVE_SCAN + JSON_CONTAINS post-filter | cop[tikv], root | Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | match | n/a |
| 18 |  | root | Projection -> Selection -> Batch_Point_Get | n/a | compatible | operator topology differs only by Projection wrapper |
| 19 | HIGH_COP_WAIT — IndexLookUp fanout | cop[tikv], root | TopN -> Selection -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | mismatch | operator topology differs; index access differs: source=['o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)'] current=[] |
| 20 |  | cop[tikv], root | Projection -> IndexLookUp -> IndexRangeScan -> Selection -> TableRowIDScan | otae1_0.obj_type_attr__workspace_id__sequential_id__idx(workspace_id, sequential_id) | match | n/a |
| 21 |  | cop[tiflash], cop[tikv], root | TopN -> HashJoin -> TableReader -> ExchangeSender -> Selection -> TableRangeScan -> IndexHashJoin -> TableReader -> ExchangeSender -> Selec... | subR.ix_obj_rel_object_id_without_partition(object_id) | mismatch | operator topology differs; index access differs: source=['subR.ix_obj_rel_object_id_without_partition(object_id)'] current=['subr.idx_obj_relationship_new_object_ws_ota_ref(object_id, workspace_id, object_type_attribute... |
| 22 |  | root | Projection -> Selection -> Batch_Point_Get | n/a | compatible | operator topology differs only by Projection wrapper |
| 23 |  | cop[tikv], root | Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id) | match | n/a |
| 24 |  | cop[tiflash], cop[tikv], root | TopN -> HashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> HashJoin -> HashJoin -> IndexHashJoin -> IndexReader -> IndexRangeSc... | subO3.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id), subR.ix_obj_rel_referenced_object_id_without_partition(r... | mismatch | operator topology differs; task set differs: source=['cop[tiflash]', 'cop[tikv]', 'root'] current=['mpp[tiflash]', 'root']; join operators differ: source=['HashJoin', 'HashJoin', 'HashJoin', 'IndexHashJoin', 'IndexHashJ... |
| 25 |  | cop[tikv], root | Projection -> TopN -> Selection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan | o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower) | mismatch | index access differs: source=['o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)'] current=['o.idx_obj_new_ws_ot_tv7_num1_seq(workspace_id, obj_type_id, text_value_7, numeric_value_... |

## Details

### Query 1

- Source status: `pending`
- Source topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `ct1_0.obj_type_attr_fk(obj_type_attr_id)`
- Current plan: not captured yet.

### Query 2

- Source status: `match`
- Source topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `obj_relationship.ix_obj_rel_object_id_without_partition(object_id)`
- Current sample: `s1`
- Current topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `obj_relationship.ix_obj_rel_object_id_without_partition(object_id)`

### Query 3

- Source status: `pending`
- Source topology: `Projection -> Projection -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> IndexJoin -> HashJoin -> TableReader -> Selection -> TableFullScan -> IndexJoin -> Selection -> Point_Get -> TableReader -> Selection -> TableRangeScan -> TableReader -> Selection -> TableRangeScan -> TableReader -> Selection -> TableRangeScan -> TableReader -> Selection -> TableRangeScan -> TableReader -> Selection -> TableRangeScan -> IndexLookUp -> Selection -> IndexRangeSca...`
- Source task topology: `Projection[root] -> Projection[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> HashJoin[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableFullScan[cop[tikv]] -> IndexJoin[root] -> Selection[root] -> Point_Get[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]] -> TableReader...`
- Source indexes: `ct1_0.obj_type_fk(obj_type_id), ct2_0.obj_schema_fk(obj_schema_id), ct3_0.obj_type_fk(obj_type_id)`
- Current plan: not captured yet.

### Query 4

- Source status: `match`
- Source topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 5

- Source status: `match`
- Source topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 6

- Source status: `compatible`
- Source topology: `Projection -> Batch_Point_Get`
- Source task topology: `Projection[root] -> Batch_Point_Get[root]`
- Source indexes: `n/a`
- Current sample: `s1`
- Current topology: `Batch_Point_Get`
- Current task topology: `Batch_Point_Get[root]`
- Current indexes: `n/a`

### Query 7

- Source status: `match`
- Source topology: `Projection -> IndexHashJoin -> Selection -> Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexHashJoin[root] -> Selection[root] -> Point_Get[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position)`
- Current sample: `s1`
- Current topology: `Projection -> IndexHashJoin -> Selection -> Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexHashJoin[root] -> Selection[root] -> Point_Get[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position)`

### Query 8

- Source status: `compatible`
- Source topology: `TopN -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> TopN -> Selection -> TableRowIDScan`
- Source task topology: `TopN[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tici]] -> IndexRangeScan[cop[tici]] -> TopN[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.idx_fts_text_value_22(text_value_22)`
- Current sample: `s1`
- Current topology: `TopN -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> TopN -> Selection -> TableRowIDScan`
- Current task topology: `TopN[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tici]] -> IndexRangeScan[cop[tici]] -> TopN[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.idx_fts_22(text_value_22)`

### Query 9

- Source status: `match`
- Source topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `obj_relationship.ix_obj_rel_object_id_without_partition(object_id)`
- Current sample: `s1`
- Current topology: `Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `obj_relationship.ix_obj_rel_object_id_without_partition(object_id)`

### Query 10

- Source status: `compatible`
- Source topology: `Projection -> Limit -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> Limit[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 11

- Source status: `compatible`
- Source topology: `Projection -> Selection -> Point_Get`
- Source task topology: `Projection[root] -> Selection[root] -> Point_Get[root]`
- Source indexes: `n/a`
- Current sample: `s1`
- Current topology: `Point_Get`
- Current task topology: `Point_Get[root]`
- Current indexes: `n/a`

### Query 12

- Source status: `pending`
- Source topology: `Projection -> Projection -> IndexJoin -> IndexJoin -> IndexJoin -> HashJoin -> TableReader -> Selection -> TableFullScan -> IndexJoin -> Selection -> Point_Get -> TableReader -> Selection -> TableRangeScan -> IndexLookUp -> Selection -> IndexRangeScan -> TableRowIDScan -> IndexLookUp -> IndexRangeScan -> TableRowIDScan -> TableReader -> TableRangeScan`
- Source task topology: `Projection[root] -> Projection[root] -> IndexJoin[root] -> IndexJoin[root] -> IndexJoin[root] -> HashJoin[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableFullScan[cop[tikv]] -> IndexJoin[root] -> Selection[root] -> Point_Get[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]] -...`
- Source indexes: `ct1_0.ref_type_fk(ref_type_id), ct2_0.obj_schema_fk(obj_schema_id)`
- Current plan: not captured yet.

### Query 13

- Source status: `match`
- Source topology: `Projection -> IndexHashJoin -> Selection -> Batch_Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexHashJoin[root] -> Selection[root] -> Batch_Point_Get[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position)`
- Current sample: `s1`
- Current topology: `Projection -> IndexHashJoin -> Selection -> Batch_Point_Get -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexHashJoin[root] -> Selection[root] -> Batch_Point_Get[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `otae1_0.ix_ota_ot_and_position(workspace_id, object_type_id, ota_position)`

### Query 14

- Source status: `mismatch`
- Source topology: `TopN -> Selection -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `TopN[root] -> Selection[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> TableReader -> Selection -> TableRangeScan`
- Current task topology: `TopN[root] -> Selection[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]]`
- Current indexes: `n/a`

### Query 15

- Source status: `mismatch`
- Source topology: `TopN -> Selection -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `TopN[root] -> Selection[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> TableReader -> Selection -> TableRangeScan`
- Current task topology: `TopN[root] -> Selection[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]]`
- Current indexes: `n/a`

### Query 16

- Source status: `mismatch`
- Source topology: `Projection -> TopN -> Selection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> TopN[root] -> Selection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> TableReader -> Selection -> TableRangeScan`
- Current task topology: `TopN[root] -> Selection[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]]`
- Current indexes: `n/a`

### Query 17

- Source status: `match`
- Source topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 18

- Source status: `compatible`
- Source topology: `Projection -> Selection -> Batch_Point_Get`
- Source task topology: `Projection[root] -> Selection[root] -> Batch_Point_Get[root]`
- Source indexes: `n/a`
- Current sample: `s1`
- Current topology: `Selection -> Batch_Point_Get`
- Current task topology: `Selection[root] -> Batch_Point_Get[root]`
- Current indexes: `n/a`

### Query 19

- Source status: `mismatch`
- Source topology: `TopN -> Selection -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `TopN[root] -> Selection[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> TableReader -> Selection -> TableRangeScan`
- Current task topology: `TopN[root] -> Selection[root] -> TableReader[root] -> Selection[cop[tikv]] -> TableRangeScan[cop[tikv]]`
- Current indexes: `n/a`

### Query 20

- Source status: `match`
- Source topology: `Projection -> IndexLookUp -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `otae1_0.obj_type_attr__workspace_id__sequential_id__idx(workspace_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Projection -> IndexLookUp -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `otae1_0.obj_type_attr__workspace_id__sequential_id__idx(workspace_id, sequential_id)`

### Query 21

- Source status: `mismatch`
- Source topology: `TopN -> HashJoin -> TableReader -> ExchangeSender -> Selection -> TableRangeScan -> IndexHashJoin -> TableReader -> ExchangeSender -> Selection -> TableRangeScan -> Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `TopN[root] -> HashJoin[root] -> TableReader[root] -> ExchangeSender[cop[tiflash]] -> Selection[cop[tiflash]] -> TableRangeScan[cop[tiflash]] -> IndexHashJoin[root] -> TableReader[root] -> ExchangeSender[cop[tiflash]] -> Selection[cop[tiflash]] -> TableRangeScan[cop[tiflash]] -> Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `subR.ix_obj_rel_object_id_without_partition(object_id)`
- Current sample: `s1`
- Current topology: `TopN -> HashJoin -> TableReader -> ExchangeSender -> Selection -> TableRangeScan -> IndexHashJoin -> TableReader -> ExchangeSender -> Selection -> TableRangeScan -> IndexReader -> IndexRangeScan`
- Current task topology: `TopN[root] -> HashJoin[root] -> TableReader[root] -> ExchangeSender[mpp[tiflash]] -> Selection[mpp[tiflash]] -> TableRangeScan[mpp[tiflash]] -> IndexHashJoin[root] -> TableReader[root] -> ExchangeSender[mpp[tiflash]] -> Selection[mpp[tiflash]] -> TableRangeScan[mpp[tiflash]] -> IndexReader[root] -> IndexRangeScan[cop[tikv]]`
- Current indexes: `subr.idx_obj_relationship_new_object_ws_ota_ref(object_id, workspace_id, object_type_attribute_id, referenced_object_id)`

### Query 22

- Source status: `compatible`
- Source topology: `Projection -> Selection -> Batch_Point_Get`
- Source task topology: `Projection[root] -> Selection[root] -> Batch_Point_Get[root]`
- Source indexes: `n/a`
- Current sample: `s1`
- Current topology: `Selection -> Batch_Point_Get`
- Current task topology: `Selection[root] -> Batch_Point_Get[root]`
- Current indexes: `n/a`

### Query 23

- Source status: `match`
- Source topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`
- Current sample: `s1`
- Current topology: `Limit -> Projection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `Limit[root] -> Projection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id)`

### Query 24

- Source status: `mismatch`
- Source topology: `TopN -> HashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> HashJoin -> HashJoin -> IndexHashJoin -> IndexReader -> IndexRangeScan -> Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan -> Projection -> IndexHashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan -> Projection -> IndexHashJoin -> TableReader -> ExchangeSender -> TableRangeScan -> Projection -> IndexLookUp -> IndexRangeScan -> TableRowIDScan`
- Source task topology: `TopN[root] -> HashJoin[root] -> TableReader[root] -> ExchangeSender[cop[tiflash]] -> TableRangeScan[cop[tiflash]] -> HashJoin[root] -> HashJoin[root] -> IndexHashJoin[root] -> IndexReader[root] -> IndexRangeScan[cop[tikv]] -> Projection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> TableRowIDScan[cop[tikv]] -> Projection[root] -> IndexHashJoin[root] -> TableReader[root] -> ExchangeSender[cop[tiflash]] -> TableRangeScan[cop[tiflash]] -> Projection[root] -> IndexLookUp[root] -> Index...`
- Source indexes: `subO3.ix_obj_label_objtypeid_new(workspace_id, label, obj_type_id, sequential_id), subR.ix_obj_rel_referenced_object_id_without_partition(referenced_object_id), subR1.ix_obj_rel_referenced_object_id_without_partition(referenced_object_id), subR2.ix_obj_rel_referenced_object_id_without_partition(referenced_object_id)`
- Current sample: `s1`
- Current topology: `TopN -> TableReader -> ExchangeSender -> TopN -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> TableRangeScan -> ExchangeReceiver -> ExchangeSender -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> TableRangeScan -> TableFullScan -> Projection -> Projection -> HashJoin -> ExchangeReceiver -> ExchangeSender -> TableRangeScan -> Exchang...`
- Current task topology: `TopN[root] -> TableReader[root] -> ExchangeSender[mpp[tiflash]] -> TopN[mpp[tiflash]] -> Projection[mpp[tiflash]] -> HashJoin[mpp[tiflash]] -> ExchangeReceiver[mpp[tiflash]] -> ExchangeSender[mpp[tiflash]] -> TableRangeScan[mpp[tiflash]] -> ExchangeReceiver[mpp[tiflash]] -> ExchangeSender[mpp[tiflash]] -> Projection[mpp[tiflash]] -> HashJoin[mpp[tiflash]] -> ExchangeReceiver[mpp[tiflash]] -> ExchangeSender[mpp[tiflash]] -> Projection[mpp[tiflash]] -> HashJoin[mpp[tiflash]] -> ExchangeReceiver[m...`
- Current indexes: `n/a`

### Query 25

- Source status: `mismatch`
- Source topology: `Projection -> TopN -> Selection -> IndexLookUp -> Selection -> IndexRangeScan -> Selection -> TableRowIDScan`
- Source task topology: `Projection[root] -> TopN[root] -> Selection[root] -> IndexLookUp[root] -> Selection[cop[tikv]] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Source indexes: `o.ix_obj_composite_ot_lower_text_value_7(workspace_id, obj_type_id, text_value_7_lower)`
- Current sample: `s1`
- Current topology: `TopN -> Selection -> IndexLookUp -> IndexRangeScan -> Selection -> TableRowIDScan`
- Current task topology: `TopN[root] -> Selection[root] -> IndexLookUp[root] -> IndexRangeScan[cop[tikv]] -> Selection[cop[tikv]] -> TableRowIDScan[cop[tikv]]`
- Current indexes: `o.idx_obj_new_ws_ot_tv7_num1_seq(workspace_id, obj_type_id, text_value_7, numeric_value_1, sequential_id)`

