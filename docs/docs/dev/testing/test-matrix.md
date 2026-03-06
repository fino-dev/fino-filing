# Test Matrix

Per public API (`__all__`) and main methods: which focus is covered by which test. Blank = not covered.

## Legend

- Cell: `test/.../file.py` → `TestClassName`
- Focus: Happy path / Failure / Boundary / Contract & invariants

## Matrix

| Public API / method | Happy path | Failure | Boundary | Contract & invariants |
|---------------------|------------|--------|----------|------------------------|
| **Filing** (init, get, set) | test_init_filing.py `TestFiling_Initialize`, test_init_extend.py, test_init_edinet.py `TestFiling_Initialize_EDINET` | test_filing_error.py, test_init_filing.py (lack_field, invalid_field), test_init_extend.py (lack, invalid) | test_none.py `TestFiling_Initialize_ExplicitNone` | test_init_filing.py `TestFiling_Initialize_ImmutableField`, test_extends_default_field.py, test_init_extend.py (immutable) |
| **Filing** (to_dict, from_dict) | test_filing_dict.py `TestFiling_ToDict`, `TestFiling_FromDict` | test_filing_dict.py (missing_fields_failed, invalid_type_failed) | — | test_filing_dict.py `TestFiling_ToDict_FromDict_RoundTrip` |
| **Filing** (get_indexed_fields, __repr__, __eq__) | test_filing_metadata.py, test_filing_eq.py, test_filing_field.py | — | — | test_filing_eq.py (equality / inequality) |
| **Field** | test_init_field.py `TestField_Initialize` | test_filing_error.py (Field-related exceptions) | — | — |
| **Expr** | test_expr.py | — | — | — |
| **Collection** (add) | test_add.py `TestCollection_Add` | test_add.py (checksum mismatch, same id overwrite) | — | test_add.py (Filing roundtrip, same id overwrite) |
| **Collection** (get, get_filing, get_content) | test_get.py, test_get_filing.py, test_get_content.py | test_get_filing.py (not_found), test_get_content.py (not_found), test_get.py (not_found) | — | test_get.py (EDINETFiling roundtrip) |
| **Collection** (search) | (via Collection indirectly) | (none) | (none) | (none) |
| **Collection** (init) | test_init.py `TestCollection_Initialize` | — | — | — |
| **Catalog** (index, get) | via test_add, test_get | — | — | — |
| **Catalog** (index_batch, search, count, clear) | test_catalog.py | — | — | — |
| **FilingResolver** (register, resolve) | test_filing_resolver.py | test_filing_resolver.py (resolve None/empty/unregistered) | — | — |
| **register_filing_class** | test_filing_resolver.py `TestRegisterFilingClass` | — | — | — |
| **default_resolver** | test_filing_resolver.py `TestDefaultResolver` | — | — | — |
| **Locator** (resolve) | test_resolve.py `TestLocator_Resolve` | (none) | — | — |
| **LocalStorage** | via Collection integration | (none) | — | — |
| **Storage** (Protocol) | — | — | — | — |
| **EDINETFiling** | test_init_edinet.py, test_add.py, test_get.py | — | — | test_get.py (roundtrip) |
| **EDGARFiling** | test_init_edgar.py `TestFiling_Initialize_EDGAR` | — | — | — |
| **FinoFilingException** (core) | — | test_core_error.py `TestFinoFilingException` | — | — |
| **CollectionChecksumMismatchError** | — | test_collection_error.py, test_add.py (add path) | — | — |

## See also

- Focus definitions: [testing-strategy](./testing-strategy)
- Exception spec: [Exception spec](/docs/spec/api/exception-spec)
