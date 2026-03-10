# Collector APIs

The **Collector** boundary fetches documents from external APIs, parses them, builds Filing instances, and adds them to a Collection. It follows a Template Method: `collect()` runs fetch → parse → build_filing → add_to_collection per document.

## Public types

| Type                                | Description                                                                                                                 |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| [BaseCollector](./BaseCollector)    | Abstract base: `collect()`, `add_to_collection()`; subclasses implement `fetch_documents`, `parse_response`, `build_filing` |
| [RawDocument](./RawDocument-Parsed) | One fetched document: `content: bytes`, `meta: dict[str, Any]`                                                              |
| [Parsed](./RawDocument-Parsed)      | `dict[str, Any]`; intermediate structure before building a Filing                                                           |
| [EdgerConfig](./Edger/EdgerConfig)        | EDGAR config: timeout, User-Agent                                                                                           |
| [EdgerSecApi](./Edger/EdgerSecApi)        | Strategy: SEC Company Submissions API → fetch, parse, EDGARFiling                                                          |
| [EdgerBulkData](./Edger/EdgerBulkData)    | Strategy: Bulk daily-index (currently yields nothing; placeholder)                                                          |
| [EdgerCollector](./Edger/EdgerCollector)  | Orchestrates EdgerSecApi and EdgerBulkData; `collect()` adds to Collection                                                   |
| [EdinetConfig](./Edinet/EdinetConfig)      | EDINET API config: api_key, timeout（api_base は不要）                                                                      |
| [EdinetCollector](./Edinet/EdinetCollector) | 書類一覧API・書類取得API で EDINET 書類を取得し EDINETFiling として Collection に追加                                |

## Flow

1. **fetch_documents()** → yields `RawDocument` (content + meta).
2. **parse_response(raw)** → returns `Parsed` (dict).
3. **build_filing(parsed, raw)** → returns `Filing`.
4. **add_to_collection(filing, content)** → calls `Collection.add`; returns `(Filing, path)`.

Documents are processed one by one; partial results are persisted before a later failure.
