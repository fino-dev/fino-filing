---
sidebar_position: 0
title: Collector boundary
---

# Collector boundary

The **Collector** boundary fetches documents from external APIs, parses them, builds Filing instances, and adds them to a Collection. It follows a Template Method: `collect()` runs fetch → parse → build_filing → add_to_collection per document.

## Public types

| Type | Description |
|------|-------------|
| [BaseCollector](./BaseCollector) | Abstract base: `collect()`, `add_to_collection()`; subclasses implement `fetch_documents`, `parse_response`, `build_filing` |
| [RawDocument](./RawDocument-Parsed) | One fetched document: `content: bytes`, `meta: dict[str, Any]` |
| [Parsed](./RawDocument-Parsed) | `dict[str, Any]`; intermediate structure before building a Filing |
| [EdgerConfig](./EdgerConfig) | EDGAR config: SEC/Bulk URLs, timeout, rate limit, User-Agent |
| [EdgerSecApi](./EdgerSecApi) | Strategy: SEC Company Submissions API → fetch, parse, EDGARFiling |
| [EdgerBulkData](./EdgerBulkData) | Strategy: Bulk daily-index (currently yields nothing; placeholder) |
| [EdgerCollector](./EdgerCollector) | Orchestrates EdgerSecApi and EdgerBulkData; `collect()` adds to Collection |

## Flow

1. **fetch_documents()** → yields `RawDocument` (content + meta).
2. **parse_response(raw)** → returns `Parsed` (dict).
3. **build_filing(parsed, raw)** → returns `Filing`.
4. **add_to_collection(filing, content)** → calls `Collection.add`; returns `(Filing, path)`.

Documents are processed one by one; partial results are persisted before a later failure.
