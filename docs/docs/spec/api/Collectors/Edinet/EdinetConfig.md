---
sidebar_position: 0
title: EdinetConfig
---

# EdinetConfig

EDINET API 用のユーザー設定。Collector のコンストラクタで渡す。API のベース URL は固定のため `api_base` は持たない。

## Constructor

```python
EdinetConfig(
    api_key: str,
    timeout: int = 30,
) -> EdinetConfig
```

| 引数      | 型  | 既定     | 説明                                                   |
| --------- | --- | -------- | ------------------------------------------------------ |
| `api_key` | str | （必須） | EDINET API の Subscription-Key。リクエストヘッダで送る |
| `timeout` | int | 30       | HTTP リクエストのタイムアウト（秒）                    |

## 使用例

```python
from fino_filing import EdinetConfig, EdinetCollector
from fino_filing import Collection, LocalStorage, Catalog

config = EdinetConfig(api_key="your-subscription-key")
# collection は storage + catalog で構成
collector = EdinetCollector(collection, config)
collector.collect(date_from="2024-01-01", date_to="2024-01-31", limit=10)
```
