---
sidebar_position: 4
title: EdgarArchiveCollector
---

# EdgarArchiveCollector

Submissions の `recent` 提出を走査し、Archives からドキュメントを取得して `EdgarArchiveFiling` として保存する。

## Constructor

```python
EdgarArchiveCollector(collection: Collection, config: EdgarConfig) -> EdgarArchiveCollector
```

## collect / iter_collect（キーワード引数）

```python
collect(
    *,
    cik_list: list[str] | None = None,
    form_type_list: list[str] | None = None,
    limit_per_company: int | None = None,
    fetch_mode: EdgarDocumentsFetchMode = EdgarDocumentsFetchMode.PRIMARY_ONLY,
) -> list[tuple[EdgarArchiveFiling, str]]
```

- **cik_list**: 必須相当。空または `None` のときは何も収集しない。  
- **form_type_list**: 指定時は該当フォームのみ。  
- **limit_per_company**: CIK あたりの提出件数上限。  
- **fetch_mode**: `PRIMARY_ONLY`（代表ドキュメント中心）/ `FULL`（index.json に基づくフル ZIP 等）。

戻り値は `(EdgarArchiveFiling, 保存絶対パス)`。

## 内部フロー（概要）

各 CIK で Submissions を取得 → `recent` を検証・パース → Archives API でファイル取得 → `RawDocument` → `_parse_response` / `_build_filing`。
