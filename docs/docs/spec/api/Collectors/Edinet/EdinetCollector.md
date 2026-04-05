---
sidebar_position: 1
title: EdinetCollector
---

# EdinetCollector

書類一覧 API（日付ループ）→ 書類取得 API で `EDINETFiling` を保存する。内部で `EdinetClient` を生成する。

## Constructor

```python
EdinetCollector(collection: Collection, config: EdinetConfig) -> EdinetCollector
```

## collect / iter_collect

```python
collect(
    *,
    date_from: date,
    date_to: date,
    document_type: EDINET_DOCUMENT_DOWNLOAD_TYPE = EDINET_DOCUMENT_DOWNLOAD_TYPE.XBRL,
    limit: int | None = None,
) -> list[tuple[EDINETFiling, str]]
```

- **date_from** / **date_to**: 両端含む。`date_to < date_from` なら `CollectorDateRangeValidationError`。  
- **document_type**: `EDINET_DOCUMENT_DOWNLOAD_TYPE`（XBRL=1, PDF=2, …）。  
- **limit**: 全体の最大取得件数。`limit <= 0` なら `CollectorLimitValidationError`。  

一覧 API の `type` は実装固定で **METADATA_AND_LIST**（メタ＋書類一覧）。

## 内部

`_fetch_documents` → `_parse_response` → `_build_filing(parsed, content)`。書式・ZIP 判定はダウンロード種別とコンテンツから推論する。
