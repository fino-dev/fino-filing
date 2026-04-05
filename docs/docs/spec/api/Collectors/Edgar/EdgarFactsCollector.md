---
sidebar_position: 3
title: EdgarFactsCollector
---

# EdgarFactsCollector

CIK ごとに Submissions と Company Facts API を呼び、正規化した JSON を `EdgarCompanyFactsFiling` として保存する。

## Constructor

```python
EdgarFactsCollector(collection: Collection, config: EdgarConfig) -> EdgarFactsCollector
```

## collect / iter_collect

```python
collect(
    *,
    cik_list: list[str] | None = None,
    limit: int | None = None,
) -> list[tuple[EdgarCompanyFactsFiling, str]]
```

- **cik_list**: 空または `None` のときは何も収集しない。  
- **limit**: 現状 `_fetch_documents` 内では未使用（将来用）。

Submissions / Company Facts が空や取得不能な場合は `CollectorNoContentError` などが送出されうる。
