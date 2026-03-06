# テストマトリクス

公開API（`__all__`）および主要メソッドごとに、どの観点をどのテストで確認しているかを示す。空欄は未カバー。

## 凡例

- セル: `test/.../ファイル名.py` の `TestClassName`
- 観点: 正常系 / 異常系 / 境界 / 契約・不変条件

## マトリクス

| 公開API / メソッド | 正常系 | 異常系 | 境界 | 契約・不変条件 |
|-------------------|--------|--------|------|-----------------|
| **Filing** (init, get, set) | test/module/filing/filing/test_init_filing.py `TestFiling_Initialize`, test_init_extend.py 各クラス, test_init_edinet.py `TestFiling_Initialize_EDINET` | test/module/filing/test_filing_error.py 各Exceptionクラス, test_init_filing.py `TestFiling_Initialize` (lack_field, invalid_field), test_init_extend.py (lack, invalid) | test/module/filing/filing/test_none.py `TestFiling_Initialize_ExplicitNone` | test/module/filing/filing/test_init_filing.py `TestFiling_Initialize_ImmutableField`, test_extends_default_field.py, test_init_extend.py (immutable 系) |
| **Filing** (to_dict, from_dict) | test/module/filing/filing/test_filing_dict.py `TestFiling_ToDict`, `TestFiling_FromDict` | test_filing_dict.py `TestFiling_FromDict` (missing_fields_failed, invalid_type_failed) | — | test_filing_dict.py `TestFiling_ToDict_FromDict_RoundTrip` |
| **Filing** (get_indexed_fields, __repr__, __eq__) | test/module/filing/filing/test_filing_metadata.py `TestFiling_GetIndexedFields`, `TestFiling_Repr`; test_filing_eq.py `TestFiling_Eq`; test_filing_field.py `TestFiling_Field` | — | — | test_filing_eq.py (同値・異値) |
| **Field** | test/module/filing/field/test_init_field.py `TestField_Initialize` | test/module/filing/test_filing_error.py (Field 起因の Exception) | — | — |
| **Expr** | test/module/filing/expr/test_expr.py 各クラス | — | — | — |
| **Collection** (add) | test/module/collection/collection/test_add.py `TestCollection_Add` | test_add.py (checksum 不一致, 同一 id は上書きで検証) | — | test_add.py (継承 Filing の roundtrip, 同一 id 上書き) |
| **Collection** (get, get_filing, get_content) | test_get.py `TestCollection_Get`, test_get_filing.py `TestCollection_GetFiling`, test_get_content.py `TestCollection_GetContent` | test_get_filing.py (not_found), test_get_content.py (not_found), test_get.py (not_found) | — | test_get.py (EDINETFiling 復元) |
| **Collection** (search) | （Collection 経由で間接的に利用） | （未） | （未） | （未） |
| **Collection** (init) | test/module/collection/collection/test_init.py `TestCollection_Initialize` | — | — | — |
| **Catalog** (index, get) | Collection 経由で test_add, test_get 等で間接的にカバー | — | — | — |
| **Catalog** (index_batch, search, count, clear) | test/module/collection/catalog/test_catalog.py 各クラス | — | — | — |
| **FilingResolver** (register, resolve) | test/module/collection/test_filing_resolver.py `TestFilingResolver_Register_Resolve`, `TestDefaultResolver`, `TestRegisterFilingClass` | test_filing_resolver.py (resolve None/空文字/未登録) | — | — |
| **register_filing_class** | test_filing_resolver.py `TestRegisterFilingClass` | — | — | — |
| **default_resolver** | test_filing_resolver.py `TestDefaultResolver` | — | — | — |
| **Locator** (resolve) | test/module/collection/locator/test_resolve.py `TestLocator_Resolve` | （未） | — | — |
| **LocalStorage** | Collection 結合テストで間接的に使用 | （未） | — | — |
| **Storage** (Protocol) | — | — | — | — |
| **EDINETFiling** | test_init_edinet.py, test_add.py (add→get), test_get.py | — | — | test_get.py (復元型) |
| **EDGARFiling** | test/module/filing/filing/test_init_edgar.py `TestFiling_Initialize_EDGAR` | — | — | — |
| **FinoFilingException** (core) | — | test/module/core/test_core_error.py `TestFinoFilingException` | — | — |
| **CollectionChecksumMismatchError** | — | test_collection_error.py (例外の message)、test_add.py (add で発生する経路) | — | — |

## 参照

- 観点の定義: [testing-strategy.md](testing-strategy.md)
- 異常系の仕様: [exception-spec.md](exception-spec.md)
