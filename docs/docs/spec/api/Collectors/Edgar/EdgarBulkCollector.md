---
sidebar_position: 5
title: EdgarBulkCollector
---

# EdgarBulkCollector

SEC の bulk 配布 ZIP を 1 本取得し、`EdgarBulkFiling` として保存する。

## Constructor

```python
EdgarBulkCollector(collection: Collection, config: EdgarConfig) -> EdgarBulkCollector
```

## collect / iter_collect

```python
collect(
    *,
    bulk_type: EdgarBulkType = EdgarBulkType.COMPANY_FACTS,
) -> list[tuple[EdgarBulkFiling, str]]
```

- **EdgarBulkType.COMPANY_FACTS**: `daily-index/xbrl/companyfacts.zip`  
- **EdgarBulkType.SUBMISSIONS**: `daily-index/bulkdata/submissions.zip`  

取得日は実行日（`date.today()`）が `bulk_date` に入る。
