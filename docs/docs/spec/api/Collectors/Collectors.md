# Collector APIs

The **Collector** boundary fetches documents from external APIs, parses them, builds Filing instances, and adds them to a Collection. It follows a Template Method: `collect()` runs fetch → parse → build_filing → add_to_collection per document.

## Public types

| Type                                | Description                                                                                                                 |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| [BaseCollector](/docs/spec/api/Collectors/Custom/BaseCollector) | Abstract base: `collect()`, `add_to_collection()`; subclasses implement `fetch_documents`, `parse_response`, `build_filing` |
| RawDocument / Parsed | One fetched document: `content: bytes`, `meta: dict`; Parsed = `dict[str, Any]` before building a Filing (see BaseCollector) |
| [EdgerConfig](/docs/spec/api/Collectors/Edger/EdgerConfig)     | EDGAR config: timeout, User-Agent                                                                                           |
| [Edger](/docs/spec/api/Collectors/Edger/Edger)                   | EDGAR boundary: client, strategies (Facts, Documents, Bulk)                                                                |
| [EdgerBulkCollector](/docs/spec/api/Collectors/Edger/EdgerBulkCollector) | Bulk daily-index strategy                                                                                          |
| [EdinetConfig](/docs/spec/api/Collectors/Edinet/EdinetConfig)  | EDINET API config: api_key, timeout（api_base は不要）                                                                      |
| [EdinetCollector](/docs/spec/api/Collectors/Edinet/EdinetCollector) | 書類一覧API・書類取得API で EDINET 書類を取得し EDINETFiling として Collection に追加                                |

## Flow

1. **fetch_documents()** → yields `RawDocument` (content + meta).
2. **parse_response(raw)** → returns `Parsed` (dict).
3. **build_filing(parsed, raw)** → returns `Filing`.
4. **add_to_collection(filing, content)** → calls `Collection.add`; returns `(Filing, path)`.

Documents are processed one by one; partial results are persisted before a later failure.
