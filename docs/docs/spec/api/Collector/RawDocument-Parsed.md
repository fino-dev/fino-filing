---
sidebar_position: 2
title: RawDocument & Parsed
---

# RawDocument & Parsed

Types used inside the Collector flow between fetch and build_filing.

## RawDocument

```python
@dataclass(frozen=True)
class RawDocument:
    content: bytes
    meta: dict[str, Any]
```

- **content**: Raw bytes of the document (e.g. HTML, XBRL).
- **meta**: Source-specific metadata (e.g. `cik`, `accession_number`, `form_type`, `_origin` for Edger). Strategies set these; `parse_response` reads them to produce `Parsed`.

Returned by strategy `fetch_documents()`; passed to `parse_response` and `build_filing`.

## Parsed

```python
Parsed = dict[str, Any]
```

Intermediate structure between `parse_response(raw)` and `build_filing(parsed, raw)`. Keys should match the target Filing’s fields (core + subclass-specific). Used to construct the Filing and set checksum from `raw.content` if needed.
