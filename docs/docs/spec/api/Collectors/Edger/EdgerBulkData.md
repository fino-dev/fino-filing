---
sidebar_position: 5
title: EdgerBulkData
---

# EdgerBulkData

Strategy intended for EDGAR bulk daily-index data. Currently **does not yield any documents**; `fetch_documents` is a placeholder. Provides the same `parse_response` / `to_filing` contract as `EdgerSecApi` so `EdgerCollector` can use both strategies.

## Constructor

```python
EdgerBulkData(config: EdgerConfig) -> EdgerBulkData
```

## Methods

### fetch_documents

```python
fetch_documents(
    date_from: str | None = None,
    date_to: str | None = None,
    cik_list: list[str] | None = None,
    limit: int | None = None,
) -> Iterator[RawDocument]
```

Currently returns an empty iterator. Parameters are reserved for future use (date range, CIK filter, limit).

### parse_response

```python
parse_response(raw: RawDocument) -> Parsed
```

Same shape as `EdgerSecApi.parse_response`: maps `raw.meta` to Parsed dict for EDGARFiling. Raw documents from bulk should set `meta["_origin"] = "bulk"` so `EdgerCollector` delegates here.

### to_filing

```python
to_filing(parsed: Parsed, content: bytes) -> EDGARFiling
```

Builds `EDGARFiling` from `parsed` and `content`. Used by `EdgerCollector.build_filing` for bulk-origin raw documents.
