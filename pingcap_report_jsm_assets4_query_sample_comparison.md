# jsm_assets4 Query Sample Run vs PingCAP Report

Run time: 2026-05-08T07:17:04.390471+00:00

Source report: `/Users/jin/Downloads/full_report_for_pingcap.md`.

Notes:
- The source report contains normalized SQL with placeholders, so this run materialized representative parameter sets from `jsm_assets4`.
- Each runnable query uses up to three sampled parameter sets. Rows are fetched to the client; latency is client-observed SQL execution plus fetch time.
- Wide object queries are represented as `SELECT o.*` / `SELECT obj.*`; predicate, ordering, and limit shape are preserved.
- Queries whose referenced tables are absent from `jsm_assets4` are marked skipped.

## Summary

| Query | Source avg | Source max | Samples | OK | Rows avg | jsm_assets4 avg | jsm_assets4 p50 | jsm_assets4 max | Comparison | Status |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 2.7ms | 518.3ms | 0 | 0 | None | None | None | None | n/a | skipped |
| 2 | 320.8ms | 14332.3ms | 3 | 3 | 600 | 297.2 | 294.0 | 307.5 | 1.08x faster | ok |
| 3 | 36.3ms | 8652.6ms | 0 | 0 | None | None | None | None | n/a | skipped |
| 4 | 11882.9ms | 34102.7ms | 3 | 3 | 1000 | 516.5 | 520.3 | 535.5 | 23.01x faster | ok |
| 5 | 29101.7ms | 60034.6ms | 3 | 3 | 1000 | 545.8 | 511.6 | 622.1 | 53.32x faster | ok |
| 6 | 44.8ms | 927.9ms | 3 | 3 | 50 | 615.2 | 586.2 | 751.3 | 13.73x source | ok |
| 7 | 8.7ms | 487.0ms | 3 | 3 | 35 | 256.7 | 251.5 | 267.2 | 29.51x source | ok |
| 8 | 16983.6ms | 32291.9ms | 3 | 3 | 85.3 | 7311.3 | 8295.4 | 10450.6 | 2.32x faster | ok |
| 9 | 28.1ms | 10778.1ms | 3 | 3 | 24 | 264.6 | 269.0 | 270.2 | 9.42x source | ok |
| 10 | 41204.1ms | 51112.0ms | 3 | 3 | 863.7 | 4044.0 | 4201.1 | 5189.5 | 10.19x faster | ok |
| 11 | 17.0ms | 228.7ms | 3 | 3 | 1 | 259.7 | 258.1 | 263.1 | 15.28x source | ok |
| 12 | 10.2ms | 473.9ms | 0 | 0 | None | None | None | None | n/a | skipped |
| 13 | 29.8ms | 6157.8ms | 3 | 3 | 175 | 272.7 | 257.1 | 304.1 | 9.15x source | ok |
| 14 | 28809.4ms | 45421.2ms | 3 | 3 | 1000 | 396.6 | 415.1 | 428.4 | 72.64x faster | ok |
| 15 | 24650.8ms | 42060.9ms | 3 | 3 | 1000 | 371.2 | 365.4 | 383.9 | 66.41x faster | ok |
| 16 | 47800.9ms | 60019.8ms | 3 | 3 | 1000 | 2181.1 | 2545.5 | 2584.0 | 21.92x faster | ok |
| 17 | 29564.9ms | 37139.7ms | 3 | 3 | 1000 | 577.0 | 467.9 | 801.9 | 51.24x faster | ok |
| 18 | 3.7ms | 325.7ms | 3 | 3 | 5 | 262.3 | 263.8 | 278.3 | 70.89x source | ok |
| 19 | 39798.6ms | 60018.5ms | 3 | 3 | 1000 | 384.7 | 386.1 | 417.7 | 103.45x faster | ok |
| 20 | 17.8ms | 5900.3ms | 3 | 3 | 1 | 284.9 | 280.6 | 306.6 | 16.01x source | ok |
| 21 | 23577.6ms | 30859.8ms | 3 | 3 | 1000 | 4802.1 | 854.3 | 13053.8 | 4.91x faster | ok |
| 22 | 25.9ms | 233.2ms | 3 | 3 | 20 | 352.1 | 272.2 | 512.2 | 13.59x source | ok |
| 23 | 33550.1ms | 35378.6ms | 3 | 3 | 863.7 | 406.0 | 359.2 | 513.2 | 82.64x faster | ok |
| 24 | 60085.2ms | 60085.2ms | 3 | 3 | 1000 | 1754.4 | 1724.6 | 1906.4 | 34.25x faster | ok |
| 25 | 59691.1ms | 59691.1ms | 3 | 3 | 1000 | 1467.3 | 1007.5 | 2401.1 | 40.68x faster | ok |

## Skipped Queries

- Query #1: cdm_type_obj_type_attr is not present in jsm_assets4.
- Query #3: cdm_type_obj_type, cdm_type_obj_schema, and obj_schema_owner are not present in jsm_assets4.
- Query #12: cdm_type_ref_type, cdm_type_obj_schema, and obj_schema_owner are not present in jsm_assets4.

## Per-Query Details

### Query #1

- Source tables: `cdm_type_obj_type_attr`
- Source avg/max latency: `2.7ms` / `518.3ms`
- Source avg rows/cop tasks: `0` / `1`
- Status: `skipped`
- Reason: cdm_type_obj_type_attr is not present in jsm_assets4

### Query #2

- Source tables: `obj_relationship_new`
- Source avg/max latency: `320.8ms` / `14332.3ms`
- Source avg rows/cop tasks: `234` / `33`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=9963b35f-9397-48ec-9403-adab57aef265, object_ids=25 | 600 | 294.0 | ok |  |
| s2 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, object_ids=25 | 600 | 307.5 | ok |  |
| s3 | workspace=3b4c201d-8244-416e-925d-f9608e001a2b, object_ids=25 | 600 | 290.0 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT obj_relationship.workspace_id, obj_relationship.partition_id, obj_relationship.id, obj_relationship.object_id, obj_relationship.referenced_object_id, obj_relationship.object_type_attribute_id, obj_relationship.object_type_id, obj_relationship.referenced_object_type_id FROM obj_relationship_new obj_relationship WHERE obj_relationship.object_id IN (0x3f40fcbc926f42b5bc20da730309ad2b, 0xdda88265669e4c48b0e6e00af26a20c4, 0xb860827c2cf8478cb3c2c115ae3bf4fa, 0xe72f1c09f4bf481c9bb3c8787ecfdf61, 0x0477290f213745cba2e49a3b9c1063a1, 0x938c72ebbd0247f28af2954b87d4273a, 0xffeb740095474907b5a72a955a278dad, 0xa6f6de4e2a3849f696714170101b496e, 0x5089b29d482041bbae70c5a77ce430a0, 0xa2229702ab934cf6b294af60a9388f78, 0x09c34f9d3286446b932bda694bc00661, 0x3e3cdffbb97744aaafbd5ad8e6969184, 0xf43118e74278426895fae3b56ca33809, 0xe526c08a86454a008df483c9cc8584b6, 0x8421fd2b2d334669b1a8a4bbb0cd68ac, 0x3393824a3c524fe190a2fd9b63827d5d, 0x6a2b115700b443f69fc96e5240d7e731, 0x14e5fc0828a44d3fbe5613d3fd959d77, 0xa9ecfe3fd9924e5da0cc5b4cc7c7a2ad, 0x6c41d3d4711f464e915bbd068c8aea04, 0x45ca7e3ea94945258d3d2810999d1691, 0xeb2be313812541ab9ed12d1aeff51da9, 0xc58af05080a9422bb11e6268f605458a, 0xec59a60d7cf44607be26aa4708fc51a6, 0xf1c7050361584bdcb89ec23996a3a7ca);
```

</details>

### Query #3

- Source tables: `obj_type,cdm_type_obj_type,icon,obj_schema,cdm_type_obj_schema,obj_schema_property,obj_schema_owner`
- Source avg/max latency: `36.3ms` / `8652.6ms`
- Source avg rows/cop tasks: `1` / `6`
- Status: `skipped`
- Reason: cdm_type_obj_type, cdm_type_obj_schema, and obj_schema_owner are not present in jsm_assets4

### Query #4

- Source tables: `obj_new`
- Source avg/max latency: `11882.9ms` / `34102.7ms`
- Source avg rows/cop tasks: `1000` / `518`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=9963b35f-9397-48ec-9403-adab57aef265, obj_types=5 | 1000 | 493.8 | ok |  |
| s2 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, obj_types=5 | 1000 | 535.5 | ok |  |
| s3 | workspace=3b4c201d-8244-416e-925d-f9608e001a2b, obj_types=5 | 1000 | 520.3 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id='9963b35f-9397-48ec-9403-adab57aef265' AND (o.obj_type_id IN (0xc803e991dc8d4c96a8180a05c3a7ee7b, 0x79d1215ce2a04ecaa29b257eec19bb8d, 0xcaa0b57b5bca42d780f67b3831e81978, 0xf1e422765cd348969fee51389a43a639, 0xe9b4640efde64a4baba2d402fb8d3f93) AND ((o.numeric_value_5 IS NOT NULL AND o.obj_type_id = 0xc803e991dc8d4c96a8180a05c3a7ee7b) OR (o.numeric_value_5 IS NOT NULL AND o.obj_type_id = 0x79d1215ce2a04ecaa29b257eec19bb8d) OR (o.numeric_value_5 IS NOT NULL AND o.obj_type_id = 0xcaa0b57b5bca42d780f67b3831e81978) OR (o.numeric_value_5 IS NOT NULL AND o.obj_type_id = 0xf1e422765cd348969fee51389a43a639) OR (o.numeric_value_5 IS NOT NULL AND o.obj_type_id = 0xe9b4640efde64a4baba2d402fb8d3f93))) ORDER BY o.label ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #5

- Source tables: `obj_new`
- Source avg/max latency: `29101.7ms` / `60034.6ms`
- Source avg rows/cop tasks: `65` / `1821`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, obj_type_branches=5 | 1000 | 503.8 | ok |  |
| s2 | workspace=3b4c201d-8244-416e-925d-f9608e001a2b, obj_type_branches=5 | 1000 | 511.6 | ok |  |
| s3 | workspace=cafd5188-8a63-44e7-b4a9-e885c9664b9c, obj_type_branches=5 | 1000 | 622.1 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id='8a6526e6-cd57-4216-bac6-358a6177d221' AND (o.obj_type_id IN (0x81790b7da4ec44de85e1c94e50c497a7, 0x1bfa019ca2164e97b43331fe25d01325, 0xad3f4feadb96456da7bffc4cd63f05f4, 0x29ba27b2e1174ca3a0541b8e84c15d4e, 0x1d9d47a406e14befa85e456dcec5b67b) AND (((JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."1eee37c0-0f68-41e4-abfa-9b166b9a0a18"', JSON_ARRAY('jira-group1'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."1eee37c0-0f68-41e4-abfa-9b166b9a0a18"', JSON_ARRAY('jira-group15'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."42cf7e7a-80c9-472a-b5da-429c41632661"', JSON_ARRAY('61b1c18ec15977006a4ad662'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."42cf7e7a-80c9-472a-b5da-429c41632661"', JSON_ARRAY('61b1c7a1c510bc006b67a317')))) AND o.obj_type_id=0x81790b7da4ec44de85e1c94e50c497a7) OR ((JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."57bcd304-17ea-4e4b-9316-5d5193a72ba5"', JSON_ARRAY('61b192f0c15977006a48b4b6'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."bfa02459-ed27-4699-80be-74abd546f842"', JSON_ARRAY('jira-group2'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."57bcd304-17ea-4e4b-9316-5d5193a72ba5"', JSON_ARRAY('61b1b7c9744c4d0069892f45'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."bfa02459-ed27-4699-80be-74abd546f842"', JSON_ARRAY('jira-group12')))) AND o.obj_type_id=0x1bfa019ca2164e97b43331fe25d01325) OR ((JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."cb46cc57-4418-4849-b604-c321ad0e3a35"', JSON_ARRAY('61b1b873977c5b00728adbf2'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."e2876f3e-fbd0-42cb-bd16-8c3b5f5ecdb9"', JSON_ARRAY('jira-group15'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."cb46cc57-4418-4849-b604-c321ad0e3a35"', JSON_ARRAY('61b1c272ebce470067f024c0'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."e2876f3e-fbd0-42cb-bd16-8c3b5f5ecdb9"', JSON_ARRAY('jira-group13')))) AND o.obj_type_id=0xad3f4feadb96456da7bffc4cd63f05f4) OR ((JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."1ab70ec5-6043-4626-974e-2f1c9b2c1841"', JSON_ARRAY('61b193383618cd006f596d51'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."ca0f6d36-5cc2-4f2f-a9de-24e6601f9eb2"', JSON_ARRAY('jira-group8'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."1ab70ec5-6043-4626-974e-2f1c9b2c1841"', JSON_ARRAY('61b1bdaa657a05007060ed84'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."ca0f6d36-5cc2-4f2f-a9de-24e6601f9eb2"', JSON_ARRAY('jira-group9')))) AND o.obj_type_id=0x29ba27b2e1174ca3a0541b8e84c15d4e) OR ((JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."2a594586-2aed-43f5-9545-f20a1ac1fca9"', JSON_ARRAY('61b1c42b744c4d006989d575'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."afce7106-823a-4e74-bca5-e89e98f3c06a"', JSON_ARRAY('jira-group1'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."afce7106-823a-4e74-bca5-e89e98f3c06a"', JSON_ARRAY('jira-group2'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."afce7106-823a-4e74-bca5-e89e98f3c06a"', JSON_ARRAY('jira-group10')))) AND o.obj_type_id=0x1d9d47a406e14befa85e456dcec5b67b))) ORDER BY o.label ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #6

- Source tables: `obj_new`
- Source avg/max latency: `44.8ms` / `927.9ms`
- Source avg rows/cop tasks: `168` / `0`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=9963b35f-9397-48ec-9403-adab57aef265, ids=50 | 50 | 751.3 | ok |  |
| s2 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, ids=50 | 50 | 586.2 | ok |  |
| s3 | workspace=3b4c201d-8244-416e-925d-f9608e001a2b, ids=50 | 50 | 508.1 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT obj.* FROM obj_new obj WHERE obj.id IN (0x687c943e75034b308ad0a7200437bd6a, 0x012df2a994244650bf798c2a1dfd00a0, 0x76f30fd4a3da4761b6966c3dd8c11615, 0xac7713063b1840009ed93254816a3dc8, 0x457ec56e51b74accb4225426132e02c8, 0x800dfc7bd7bc44ff94fcfa37b8522d8f, 0x755b8f7c8a9749c2af9220a2163e4a7e, 0x088895fc8b4f4687a4d61ed86e0f496e, 0x4f118be964d04a1f9ebf1cd0a2eca8b9, 0x69c59817bcb64e6fb989af825320ee1e, 0x98ee7599b831458e9a305f53a701a834, 0x05021c826ad6499ea7b6c919c8481c65, 0x8d0693dfda2b483f89fbd2882d63e117, 0xb678b7d94f1647d398e20e849d9029bc, 0x82713fb7559142f185f4d6a0785380df, 0x92d38f8deffb4b58813348d82f127b0e, 0x41842febf7d2405ba3f0d455b4ec6ce3, 0x06c5c13c6f39475f917080670d6c3ef3, 0x311a751c91cd46ff9298918161962c88, 0xd14994a45abc4953a665c874abd2c0c8, 0xd21b6f92d1bd4df4bf309273e8e99857, 0xe561d36df58a4a4baee0bbfc198f2104, 0x48fceda44544436e91bc577c8c373661, 0x2739aa11500d4b2a9c68c41129cbee44, 0xa64186ddbef64fcca6c3e99bd1a3fa87, 0x6ca92bee65234caaa2783303beccf1ff, 0x456221cd83ce43cc972740f6b9cd1325, 0x515414589dd04f91970916ee73141391, 0x1392e5cc9e9544159b55418c1cbc1513, 0x2fe1bdb84f75411e8616f465eadc9a9b, 0x9eb65568a17b4b0da7b1d41a1e4bbc9d, 0xbdb193f9b49248349c1384cd70d65eda, 0xdeb03f0abd8c444e9d80b132974ca637, 0x0f13685937e6408390a141c33f3e07d5, 0x06c53d8d9283494ca15eda316681cd76, 0x34f957b108194d128a536340412b24ee, 0x6beea9ceffe6443888f00705b44a5f0b, 0x1c0f4b16447d4333bca72187c72874c1, 0x8eed871e1c884f72bb11ac0f947d7a3d, 0xdfca47df6c50416db3144e24cd3ae01a, 0x9af50714538a467a907fdabb37e52acc, 0x47a5982d1470446ab1a2076596cb4a57, 0x20da736aaaa546e6b29be7a684781c76, 0x235ae069332943b691155e78ada4fe11, 0xd900692d33f54e05b7c02a5a35f3c781, 0x06515de45e004a909d45a57c29a5e895, 0x5a840fe6ff8e48feac1beab11db9d4d1, 0xe2b77622524845e3930b3398a52c2250, 0x484549d7ad394bc1b19217c50b70d737, 0xc6abf937f80f415c812e1a27a7810ba6);
```

</details>

### Query #7

- Source tables: `obj_type_attr,obj_type`
- Source avg/max latency: `8.7ms` / `487.0ms`
- Source avg rows/cop tasks: `35` / `2`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=cafd5188-8a63-44e7-b4a9-e885c9664b9c, obj_type=89a756f6-0201-4cda-bec2-e6496b1d0018 | 35 | 267.2 | ok |  |
| s2 | workspace=9963b35f-9397-48ec-9403-adab57aef265, obj_type=e9b4640e-fde6-4a4b-aba2-d402fb8d3f93 | 35 | 251.5 | ok |  |
| s3 | workspace=9963b35f-9397-48ec-9403-adab57aef265, obj_type=caa0b57b-5bca-42d7-80f6-7b3831e81978 | 35 | 251.5 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT otae1_0.id, otae1_0.additional_value, otae1_0.aql, otae1_0.created, otae1_0.default_type_id, otae1_0.deleted_at, otae1_0.description, otae1_0.external_id, otae1_0.group_id_type_value, otae1_0.hidden, otae1_0.include_child_object_types, otae1_0.is_deleted, otae1_0.label, otae1_0.maximum_cardinality, otae1_0.minimum_cardinality, otae1_0.name, otae1_0.object_type_id, otae1_0.ota_position, otae1_0.options, otae1_0.pending, otae1_0.reference_object_type_id, otae1_0.reference_type_id, otae1_0.regex_validation, otae1_0.removable, otae1_0.sequential_id, otae1_0.suffix, otae1_0.summable, otae1_0.type, otae1_0.type_value, otae1_0.unique_attribute, otae1_0.updated, otae1_0.workspace_id FROM obj_type_attr otae1_0 LEFT JOIN obj_type ot1_0 ON ot1_0.id = otae1_0.object_type_id AND ot1_0.workspace_id = 'cafd5188-8a63-44e7-b4a9-e885c9664b9c' AND ot1_0.is_deleted = 0 AND ot1_0.is_deleted = 0 WHERE otae1_0.workspace_id = 'cafd5188-8a63-44e7-b4a9-e885c9664b9c' AND otae1_0.is_deleted = 0 AND ot1_0.id IN (0x89a756f602014cdabec2e6496b1d0018);
```

</details>

### Query #8

- Source tables: `obj_new`
- Source avg/max latency: `16983.6ms` / `32291.9ms`
- Source avg rows/cop tasks: `6` / `127`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=9963b35f-9397-48ec-9403-adab57aef265, obj_type=c803e991-dc8d-4c96-a818-0a05c3a7ee7b, text_value_22=⁣Operational⁣ | 36 | 10450.6 | ok |  |
| s2 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, obj_type=29ba27b2-e117-4ca3-a054-1b8e84c15d4e, text_value_22=⁣Operational⁣ | 200 | 3187.8 | ok |  |
| s3 | workspace=3b4c201d-8244-416e-925d-f9608e001a2b, obj_type=427ac8ba-5626-4168-99e6-0708472a9a7b, text_value_22=⁣Defined⁣ | 20 | 8295.4 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id='9963b35f-9397-48ec-9403-adab57aef265' AND (o.obj_type_id IN (0xf1e422765cd348969fee51389a43a639, 0x79d1215ce2a04ecaa29b257eec19bb8d, 0xe9b4640efde64a4baba2d402fb8d3f93, 0xcaa0b57b5bca42d780f67b3831e81978, 0xc803e991dc8d4c96a8180a05c3a7ee7b) AND (o.obj_type_id = 0xc803e991dc8d4c96a8180a05c3a7ee7b) AND (o.text_value_23 = '􏿿' AND MATCH(o.text_value_22) AGAINST ('"⁣Operational⁣"' IN BOOLEAN MODE) AND o.text_value_22 LIKE '%⁣Operational⁣%' AND o.text_value_22 != '' AND o.text_value_9 = 'Siemens' AND (o.numeric_value_3 = 47.000000000000000000000000000000 OR o.numeric_value_1 = 284.000000000000000000000000000000))) ORDER BY o.label ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #9

- Source tables: `obj_relationship_new`
- Source avg/max latency: `28.1ms` / `10778.1ms`
- Source avg rows/cop tasks: `8` / `6`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, object_id=e924cd02-dd14-4a20-9f43-6fa1eb207f14 | 24 | 269.0 | ok |  |
| s2 | workspace=9963b35f-9397-48ec-9403-adab57aef265, object_id=bbc3d110-0746-4491-8206-12ba77b7c56e | 24 | 254.7 | ok |  |
| s3 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, object_id=c3e6036a-54be-4ed5-a51d-f5542fb86088 | 24 | 270.2 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT obj_relationship.workspace_id, obj_relationship.partition_id, obj_relationship.id, obj_relationship.object_id, obj_relationship.referenced_object_id, obj_relationship.object_type_attribute_id, obj_relationship.object_type_id, obj_relationship.referenced_object_type_id FROM obj_relationship_new obj_relationship WHERE obj_relationship.object_id = 0xe924cd02dd144a209f436fa1eb207f14;
```

</details>

### Query #10

- Source tables: `obj_new`
- Source avg/max latency: `41204.1ms` / `51112.0ms`
- Source avg rows/cop tasks: `136` / `4324`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=134fa09e-62e8-4b23-be76-d1b2d01845cc, obj_type=05f273ff-2221-45a4-9742-dd58bb38be3e, json_terms=4 | 591 | 5189.5 | ok |  |
| s2 | workspace=134fa09e-62e8-4b23-be76-d1b2d01845cc, obj_type=0a79f4d5-1527-4f18-b770-be668a5fb0ad, json_terms=4 | 1000 | 4201.1 | ok |  |
| s3 | workspace=134fa09e-62e8-4b23-be76-d1b2d01845cc, obj_type=33516f75-3dd9-43d6-b121-a8bf408c69be, json_terms=4 | 1000 | 2741.5 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.* FROM obj_new o WHERE o.workspace_id='134fa09e-62e8-4b23-be76-d1b2d01845cc' AND (o.obj_type_id=0x05f273ff222145a49742dd58bb38be3e AND (JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1c51cd2e64c0071db7e9c'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1bc52d5986c006aa92795'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1907cd5986c006aa73474'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1c8eaef18ca0071f59a87')))) AND o.obj_type_id=0x05f273ff222145a49742dd58bb38be3e) ORDER BY o.label ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #11

- Source tables: `obj_new`
- Source avg/max latency: `17.0ms` / `228.7ms`
- Source avg rows/cop tasks: `1` / `0`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, sequential_id=1 | 1 | 263.1 | ok |  |
| s2 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, sequential_id=2 | 1 | 258.1 | ok |  |
| s3 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, sequential_id=3 | 1 | 257.8 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT obj.* FROM obj_new obj WHERE obj.workspace_id='00eaf117-fdd6-4176-9926-45310e6b9f54' AND obj.sequential_id = 1;
```

</details>

### Query #12

- Source tables: `ref_type,cdm_type_ref_type,obj_schema,cdm_type_obj_schema,obj_schema_property,obj_schema_owner`
- Source avg/max latency: `10.2ms` / `473.9ms`
- Source avg rows/cop tasks: `1` / `2`
- Status: `skipped`
- Reason: cdm_type_ref_type, cdm_type_obj_schema, and obj_schema_owner are not present in jsm_assets4

### Query #13

- Source tables: `obj_type_attr,obj_type`
- Source avg/max latency: `29.8ms` / `6157.8ms`
- Source avg rows/cop tasks: `175` / `2`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=9963b35f-9397-48ec-9403-adab57aef265, obj_types=5 | 175 | 304.1 | ok |  |
| s2 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, obj_types=5 | 175 | 256.9 | ok |  |
| s3 | workspace=3b4c201d-8244-416e-925d-f9608e001a2b, obj_types=5 | 175 | 257.1 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT otae1_0.id, otae1_0.additional_value, otae1_0.aql, otae1_0.created, otae1_0.default_type_id, otae1_0.deleted_at, otae1_0.description, otae1_0.external_id, otae1_0.group_id_type_value, otae1_0.hidden, otae1_0.include_child_object_types, otae1_0.is_deleted, otae1_0.label, otae1_0.maximum_cardinality, otae1_0.minimum_cardinality, otae1_0.name, otae1_0.object_type_id, otae1_0.ota_position, otae1_0.options, otae1_0.pending, otae1_0.reference_object_type_id, otae1_0.reference_type_id, otae1_0.regex_validation, otae1_0.removable, otae1_0.sequential_id, otae1_0.suffix, otae1_0.summable, otae1_0.type, otae1_0.type_value, otae1_0.unique_attribute, otae1_0.updated, otae1_0.workspace_id FROM obj_type_attr otae1_0 LEFT JOIN obj_type ot1_0 ON ot1_0.id = otae1_0.object_type_id AND ot1_0.workspace_id = '9963b35f-9397-48ec-9403-adab57aef265' AND ot1_0.is_deleted = 0 AND ot1_0.is_deleted = 0 WHERE otae1_0.workspace_id = '9963b35f-9397-48ec-9403-adab57aef265' AND otae1_0.is_deleted = 0 AND ot1_0.id IN (0x79d1215ce2a04ecaa29b257eec19bb8d, 0xc803e991dc8d4c96a8180a05c3a7ee7b, 0xcaa0b57b5bca42d780f67b3831e81978, 0xe9b4640efde64a4baba2d402fb8d3f93, 0xf1e422765cd348969fee51389a43a639);
```

</details>

### Query #14

- Source tables: `obj_new`
- Source avg/max latency: `28809.4ms` / `45421.2ms`
- Source avg rows/cop tasks: `1000` / `1697`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=77744fc5-c48e-44e8-a7f1-1213703b7707, text_value_8=Sharp | 1000 | 428.4 | ok |  |
| s2 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_8=LG | 1000 | 415.1 | ok |  |
| s3 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_8=LG | 1000 | 346.3 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.text_value_8 FROM obj_new o WHERE o.workspace_id='00eaf117-fdd6-4176-9926-45310e6b9f54' AND (o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707 AND ((NOT o.text_value_7_lower = '__not_sharp__' OR LOWER(o.text_value_7) = '􏿿') AND o.text_value_7 IS NOT NULL AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)  AND (o.text_value_8='Sharp' AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)) ORDER BY o.text_value_8 ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #15

- Source tables: `obj_new`
- Source avg/max latency: `24650.8ms` / `42060.9ms`
- Source avg rows/cop tasks: `1000` / `1225`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=77744fc5-c48e-44e8-a7f1-1213703b7707, text_value_8=Sharp | 1000 | 365.4 | ok |  |
| s2 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_8=LG | 1000 | 364.3 | ok |  |
| s3 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_8=LG | 1000 | 383.9 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.text_value_1 FROM obj_new o WHERE o.workspace_id='00eaf117-fdd6-4176-9926-45310e6b9f54' AND (o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707 AND ((NOT o.text_value_7_lower = '__not_sharp__' OR LOWER(o.text_value_7) = '􏿿') AND o.text_value_7 IS NOT NULL AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)  AND (o.text_value_8='Sharp' AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)) ORDER BY o.text_value_1 ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #16

- Source tables: `obj_new`
- Source avg/max latency: `47800.9ms` / `60019.8ms`
- Source avg rows/cop tasks: `500` / `1738`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=77744fc5-c48e-44e8-a7f1-1213703b7707, text_value_16=􏿿 | 1000 | 2584.0 | ok |  |
| s2 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_16=􏿿 | 1000 | 2545.5 | ok |  |
| s3 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_16=Amana | 1000 | 1413.8 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.* FROM obj_new o WHERE o.workspace_id='00eaf117-fdd6-4176-9926-45310e6b9f54' AND (o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707 AND ((NOT o.text_value_7_lower = '__not_sharp__' OR LOWER(o.text_value_7) = '􏿿') AND o.text_value_7 IS NOT NULL AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)  AND (o.text_value_16='􏿿' AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)) ORDER BY o.numeric_value_4 ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #17

- Source tables: `obj_new`
- Source avg/max latency: `29564.9ms` / `37139.7ms`
- Source avg rows/cop tasks: `0` / `2578`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=134fa09e-62e8-4b23-be76-d1b2d01845cc, obj_type=05f273ff-2221-45a4-9742-dd58bb38be3e, json_terms=8 | 1000 | 801.9 | ok |  |
| s2 | workspace=134fa09e-62e8-4b23-be76-d1b2d01845cc, obj_type=0a79f4d5-1527-4f18-b770-be668a5fb0ad, json_terms=8 | 1000 | 461.3 | ok |  |
| s3 | workspace=134fa09e-62e8-4b23-be76-d1b2d01845cc, obj_type=33516f75-3dd9-43d6-b121-a8bf408c69be, json_terms=8 | 1000 | 467.9 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id='134fa09e-62e8-4b23-be76-d1b2d01845cc' AND (o.obj_type_id=0x05f273ff222145a49742dd58bb38be3e AND (JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1c51cd2e64c0071db7e9c'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1bc52d5986c006aa92795'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1907cd5986c006aa73474'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1c8eaef18ca0071f59a87'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1b777fe9f3000681d6680'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1b998744c4d00698946ed'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1bd3a657a05007060e81f'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1bc692278e7006b9449e0')))) AND o.obj_type_id=0x05f273ff222145a49742dd58bb38be3e) ORDER BY o.label ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #18

- Source tables: `obj_type`
- Source avg/max latency: `3.7ms` / `325.7ms`
- Source avg rows/cop tasks: `4` / `0`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=9963b35f-9397-48ec-9403-adab57aef265, obj_types=5 | 5 | 244.8 | ok |  |
| s2 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, obj_types=5 | 5 | 263.8 | ok |  |
| s3 | workspace=3b4c201d-8244-416e-925d-f9608e001a2b, obj_types=5 | 5 | 278.3 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT ote1_0.* FROM obj_type ote1_0 WHERE ote1_0.workspace_id='9963b35f-9397-48ec-9403-adab57aef265' AND ote1_0.is_deleted = 0 AND ote1_0.id IN (0x79d1215ce2a04ecaa29b257eec19bb8d, 0xc803e991dc8d4c96a8180a05c3a7ee7b, 0xcaa0b57b5bca42d780f67b3831e81978, 0xe9b4640efde64a4baba2d402fb8d3f93, 0xf1e422765cd348969fee51389a43a639);
```

</details>

### Query #19

- Source tables: `obj_new`
- Source avg/max latency: `39798.6ms` / `60018.5ms`
- Source avg rows/cop tasks: `500` / `1758`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=77744fc5-c48e-44e8-a7f1-1213703b7707, text_value_16=􏿿 | 1000 | 417.7 | ok |  |
| s2 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_16=􏿿 | 1000 | 386.1 | ok |  |
| s3 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_16=Amana | 1000 | 350.2 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.numeric_value_4 FROM obj_new o WHERE o.workspace_id='00eaf117-fdd6-4176-9926-45310e6b9f54' AND (o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707 AND ((NOT o.text_value_7_lower = '__not_sharp__' OR LOWER(o.text_value_7) = '􏿿') AND o.text_value_7 IS NOT NULL AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)  AND (o.text_value_16='􏿿' AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)) ORDER BY o.numeric_value_4 ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #20

- Source tables: `obj_type_attr`
- Source avg/max latency: `17.8ms` / `5900.3ms`
- Source avg rows/cop tasks: `1` / `2`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, sequential_id=1 | 1 | 280.6 | ok |  |
| s2 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, sequential_id=2 | 1 | 306.6 | ok |  |
| s3 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, sequential_id=3 | 1 | 267.4 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT otae1_0.id, otae1_0.additional_value, otae1_0.aql, otae1_0.created, otae1_0.default_type_id, otae1_0.deleted_at, otae1_0.description, otae1_0.external_id, otae1_0.group_id_type_value, otae1_0.hidden, otae1_0.include_child_object_types, otae1_0.is_deleted, otae1_0.label, otae1_0.maximum_cardinality, otae1_0.minimum_cardinality, otae1_0.name, otae1_0.object_type_id, otae1_0.ota_position, otae1_0.options, otae1_0.pending, otae1_0.reference_object_type_id, otae1_0.reference_type_id, otae1_0.regex_validation, otae1_0.removable, otae1_0.sequential_id, otae1_0.suffix, otae1_0.summable, otae1_0.type, otae1_0.type_value, otae1_0.unique_attribute, otae1_0.updated, otae1_0.workspace_id FROM obj_type_attr otae1_0 WHERE otae1_0.workspace_id = '00eaf117-fdd6-4176-9926-45310e6b9f54' AND otae1_0.is_deleted = 0 AND otae1_0.sequential_id = 1;
```

</details>

### Query #21

- Source tables: `obj_new,obj_relationship_new`
- Source avg/max latency: `23577.6ms` / `30859.8ms`
- Source avg rows/cop tasks: `1000` / `2971`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, text_value_24=Bosch, sub_text_value_8=􏿿 | 1000 | 13053.8 | ok |  |
| s2 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, text_value_24=Bosch, sub_text_value_8=􏿿 | 1000 | 854.3 | ok |  |
| s3 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, text_value_24=KitchenAid, sub_text_value_8=􏿿 | 1000 | 498.3 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id='00eaf117-fdd6-4176-9926-45310e6b9f54' AND (o.obj_type_id IN (0x266009e95e414bafab14eef7ffe5f2e0, 0x7d9ffc8b03a94ef69bbfb2e5f939ba14, 0xdc814b704b9e458d94fe350ddfc49d98, 0x77744fc5c48e44e8a7f11213703b7707, 0xfa8499385ed14c6089b9adb37223c21c) AND (o.text_value_24='Bosch' AND o.obj_type_id IN (0x266009e95e414bafab14eef7ffe5f2e0, 0x7d9ffc8b03a94ef69bbfb2e5f939ba14, 0xdc814b704b9e458d94fe350ddfc49d98, 0x77744fc5c48e44e8a7f11213703b7707, 0xfa8499385ed14c6089b9adb37223c21c)) AND EXISTS (SELECT 1 FROM obj_relationship_new subr INNER JOIN obj_new subo1 ON subr.object_id=subo1.id AND subo1.obj_type_id IN (0x266009e95e414bafab14eef7ffe5f2e0, 0x7d9ffc8b03a94ef69bbfb2e5f939ba14, 0xdc814b704b9e458d94fe350ddfc49d98, 0x77744fc5c48e44e8a7f11213703b7707, 0xfa8499385ed14c6089b9adb37223c21c) WHERE o.id=subr.referenced_object_id AND subo1.workspace_id='00eaf117-fdd6-4176-9926-45310e6b9f54' AND subo1.text_value_8='􏿿')) ORDER BY o.label ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #22

- Source tables: `obj_new`
- Source avg/max latency: `25.9ms` / `233.2ms`
- Source avg rows/cop tasks: `20` / `0`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=9963b35f-9397-48ec-9403-adab57aef265, partition_id=1, sequential_ids=20 | 20 | 512.2 | ok |  |
| s2 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, partition_id=1, sequential_ids=20 | 20 | 271.9 | ok |  |
| s3 | workspace=3b4c201d-8244-416e-925d-f9608e001a2b, partition_id=1, sequential_ids=20 | 20 | 272.2 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT obj.* FROM obj_new obj WHERE obj.workspace_id='9963b35f-9397-48ec-9403-adab57aef265' AND obj.partition_id=1 AND obj.sequential_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20);
```

</details>

### Query #23

- Source tables: `obj_new`
- Source avg/max latency: `33550.1ms` / `35378.6ms`
- Source avg rows/cop tasks: `0` / `928`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=134fa09e-62e8-4b23-be76-d1b2d01845cc, obj_type=05f273ff-2221-45a4-9742-dd58bb38be3e, json_terms=4 | 591 | 513.2 | ok |  |
| s2 | workspace=134fa09e-62e8-4b23-be76-d1b2d01845cc, obj_type=0a79f4d5-1527-4f18-b770-be668a5fb0ad, json_terms=4 | 1000 | 359.2 | ok |  |
| s3 | workspace=134fa09e-62e8-4b23-be76-d1b2d01845cc, obj_type=33516f75-3dd9-43d6-b121-a8bf408c69be, json_terms=4 | 1000 | 345.5 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id='134fa09e-62e8-4b23-be76-d1b2d01845cc' AND (o.obj_type_id=0x05f273ff222145a49742dd58bb38be3e AND (JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1c51cd2e64c0071db7e9c'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1bc52d5986c006aa92795'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1907cd5986c006aa73474'))) OR JSON_CONTAINS(o.other_values_indexed, JSON_SET(CAST('{}' AS JSON), '$."adaac18e-cd3f-4fb6-8125-0ae7a7a2397b"', JSON_ARRAY('61b1c8eaef18ca0071f59a87')))) AND o.obj_type_id=0x05f273ff222145a49742dd58bb38be3e) ORDER BY o.label ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #24

- Source tables: `obj_new,obj_relationship_new`
- Source avg/max latency: `60085.2ms` / `60085.2ms`
- Source avg rows/cop tasks: `0` / `3147`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, depth3_label=Blue Star-158044 | 1000 | 1632.3 | ok |  |
| s2 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, depth3_label=Admiral-22554 | 1000 | 1906.4 | ok |  |
| s3 | workspace=8a6526e6-cd57-4216-bac6-358a6177d221, depth3_label=Sharp-51542 | 1000 | 1724.6 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.sequential_id, o.label FROM obj_new o WHERE o.workspace_id='8a6526e6-cd57-4216-bac6-358a6177d221' AND (o.obj_type_id IN (0x29ba27b2e1174ca3a0541b8e84c15d4e, 0xad3f4feadb96456da7bffc4cd63f05f4, 0x81790b7da4ec44de85e1c94e50c497a7, 0x1d9d47a406e14befa85e456dcec5b67b, 0x1bfa019ca2164e97b43331fe25d01325) AND EXISTS (SELECT 1 FROM obj_relationship_new subr INNER JOIN obj_new subo1 ON subr.referenced_object_id=subo1.id WHERE o.id=subr.object_id AND subo1.workspace_id='8a6526e6-cd57-4216-bac6-358a6177d221' AND EXISTS (SELECT 1 FROM obj_relationship_new subr1 INNER JOIN obj_new subo2 ON subr1.referenced_object_id=subo2.id WHERE subo1.id=subr1.object_id AND subo2.workspace_id='8a6526e6-cd57-4216-bac6-358a6177d221' AND EXISTS (SELECT 1 FROM obj_relationship_new subr2 INNER JOIN obj_new subo3 ON subr2.referenced_object_id=subo3.id WHERE subo2.id=subr2.object_id AND subo3.workspace_id='8a6526e6-cd57-4216-bac6-358a6177d221' AND subo3.label='Blue Star-158044')))) ORDER BY o.label ASC LIMIT 1000 OFFSET 0;
```

</details>

### Query #25

- Source tables: `obj_new`
- Source avg/max latency: `59691.1ms` / `59691.1ms`
- Source avg rows/cop tasks: `1000` / `3162`
- Status: `ok`

| Sample | Params | Rows | Latency ms | Status | Error |
|---|---|---:|---:|---|---|
| s1 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=77744fc5-c48e-44e8-a7f1-1213703b7707, text_value_8=Sharp | 1000 | 2401.1 | ok |  |
| s2 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_8=LG | 1000 | 1007.5 | ok |  |
| s3 | workspace=00eaf117-fdd6-4176-9926-45310e6b9f54, obj_type=fa849938-5ed1-4c60-89b9-adb37223c21c, text_value_8=LG | 1000 | 993.3 | ok |  |

<details>
<summary>Representative SQL</summary>

```sql
SELECT o.* FROM obj_new o WHERE o.workspace_id='00eaf117-fdd6-4176-9926-45310e6b9f54' AND (o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707 AND ((NOT o.text_value_7_lower = '__not_sharp__' OR LOWER(o.text_value_7) = '􏿿') AND o.text_value_7 IS NOT NULL AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)  AND (o.text_value_8='Sharp' AND o.obj_type_id=0x77744fc5c48e44e8a7f11213703b7707)) ORDER BY o.text_value_1 ASC LIMIT 1000 OFFSET 0;
```

</details>
