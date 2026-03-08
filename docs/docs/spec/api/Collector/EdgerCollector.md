---
sidebar_position: 6
title: EdgerCollector
---

# EdgerCollector

Concrete collector that uses `EdgerSecApi` and `EdgerBulkData` to fetch EDGAR documents and add them to a Collection. Implements `BaseCollector`: `fetch_documents` yields from SEC API then (when implemented) bulk; `parse_response` and `build_filing` delegate by `raw.meta["_origin"]` (`"sec"` or `"bulk"`).

## Constructor

```python
EdgerCollector(
    collection: Collection,
    edger_sec_api: EdgerSecApi,
    edger_bulk: EdgerBulkData,
    cik_list: list[str] | None = None,
) -> EdgerCollector
```

- **collection**: Collection to which filings and content are added.
- **edger_sec_api**: Strategy for SEC Company Submissions API.
- **edger_bulk**: Strategy for bulk data (currently yields nothing).
- **cik_list**: CIKs passed to `edger_sec_api.fetch_documents(cik_list=...)`. Default `[]` if `None`.

## Methods

### collect

```python
collect() -> list[tuple[Filing, str]]
```

Inherited from `BaseCollector`. Calls `fetch_documents()` (SEC API for each CIK in `cik_list`, then bulk); for each `RawDocument`, runs `parse_response` → `build_filing` → `add_to_collection`. Returns list of `(Filing, path)`. Partial results are saved if the loop stops early.

### fetch_documents

```python
fetch_documents(limit_per_company: int | None = None) -> Iterator[RawDocument]
```

Yields from `edger_sec_api.fetch_documents(cik_list=self._cik_list, limit_per_company=limit_per_company)`, then from `edger_bulk.fetch_documents(limit=limit_per_company)`. Used internally by `collect()`; base `collect()` calls `fetch_documents()` with no arguments, so `limit_per_company` is `None` unless a subclass overrides.

### parse_response / build_filing

Delegated to `EdgerSecApi` or `EdgerBulkData` based on `raw.meta.get("_origin", "sec")`. Produce `Parsed` and `EDGARFiling` respectively.
