# Collector APIs

外部 API から取得し、`Filing` を組み立てて `Collection.add` する層。**テンプレートメソッド**: 公開は `iter_collect(**criteria)` / `collect(**criteria)`。サブクラスは `_fetch_documents` / `_parse_response` / `_build_filing` を実装する。

## 公開型（パッケージルートから re-export）

| Type | 説明 |
| ---- | ---- |
| [BaseCollector](/docs/spec/api/Collectors/Custom/BaseCollector) | 上記フローの抽象基底 |
| `RawDocument` / `Parsed` | `RawDocument(content: bytes, meta: dict)`; `Parsed = dict[str, Any]` |
| [EdgarConfig](/docs/spec/api/Collectors/Edgar/EdgarConfig) / [EdgarClient](/docs/spec/api/Collectors/Edgar/EdgarClient) | SEC 用設定・HTTP クライアント（主に Collector 内部） |
| [EdgarArchiveCollector](/docs/spec/api/Collectors/Edgar/EdgarArchiveCollector) / [EdgarFactsCollector](/docs/spec/api/Collectors/Edgar/EdgarFactsCollector) / [EdgarBulkCollector](/docs/spec/api/Collectors/Edgar/EdgarBulkCollector) | SEC 収集 |
| [EdinetConfig](/docs/spec/api/Collectors/Edinet/EdinetConfig) / [EdinetCollector](/docs/spec/api/Collectors/Edinet/EdinetCollector) | EDINET 収集 |

## フロー（1 件ごと）

1. `_fetch_documents(**criteria)` → `RawDocument` を yield  
2. `_parse_response(raw)` → `Parsed`  
3. `_build_filing(parsed, content)` → `Filing`（`content` は `raw.content`）  
4. `_add_to_collection` → `Collection.add`  

途中で失敗しても、すでに yield 済みの分は Collection に残る。
