---
sidebar_position: 1
---

# Usage Scenarios

## Basic usage

```python
from fino_filing import Collection, LocalStorage, Catalog

# Setup
storage = LocalStorage("./data")
catalog = Catalog("./index.db")
collection = Collection(storage=storage, catalog=catalog)

# Add a Filing (manual construction, or use EdinetCollector for API-driven ingestion)
from fino_filing import EDINETFiling

# EDINETFiling requires id, checksum, name, format, is_zip, created_at, and EDINET-specific fields; source is "EDINET".
filing = EDINETFiling(...)
collection.add(filing, b"...")

# Search
from fino_filing import Field
filings = collection.search(expr=Field("source") == "EDINET", limit=100, offset=0)

# Get metadata
filing = collection.get_filing("filing_id")
# Get file content (e.g. for arelle)
content = collection.get_content("filing_id")
# Or both
filing, content, path = collection.get("filing_id")
```

> Note: rebuild_index, verify_integrity, and migrate are not implemented yet. Use `EdinetCollector` for API-driven EDINET ingestion (see [Quick start](/docs/spec/Quick-start)).

## Automated scenario tests

Each row maps a user-facing story to a pytest module under `test/scenario/` (no live external API calls; collectors use mocks).

| User story | Test file |
|------------|-----------|
| Manual EDINET filing: add → search → get / get_content | `test/scenario/collection/test_manual_edinet_add_search_get.py` |
| Unknown filing id: get returns empty | `test/scenario/collection/test_get_unknown_id.py` |
| Field/Expr: `in_`, OR, NOT, `contains`, model fields, limit/offset/order | `test/scenario/collection/test_expr_multitype_search.py` |
| Custom `Filing` subclass (importable module): add → search → get | `test/scenario/collection/test_custom_filing_roundtrip.py` |
| Copy storage + catalog DB to new paths; reopen `Collection` | `test/scenario/collection/test_relocate_storage_catalog.py` |
| Edgar Company Facts: collect → get / search | `test/scenario/edgar/test_facts_collect_mocked.py` |
| Edgar archive primary document: collect → get / search | `test/scenario/edgar/test_archive_collect_mocked.py` |
| EDINET API path: collect (PDF) → get / search | `test/scenario/edinet/test_collect_mocked.py` |

**Out of scope for scenarios**: flows that depend on slow or bulk Edgar downloads over the real network; those remain covered under `test/module/` with mocks.
