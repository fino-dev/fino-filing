---
sidebar_position: 1
title: EdgerConfig
---

# EdgerConfig

EDGAR 用のユーザー設定。各 Collector のコンストラクタで渡す。SEC は有効な User-Agent を要求するため、`user_agent_email` は必須。

## Constructor

```python
EdgerConfig(
    user_agent_email: str,
    timeout: int = 30,
) -> EdgerConfig
```

| 引数 | 型 | 既定 | 説明 |
|------|-----|------|------|
| `user_agent_email` | str | （必須） | SEC 連絡用メール。User-Agent は package 側で `fino-filing/0.1.0 (contact: {email})` の形で組み立てる |
| `timeout` | int | 30 | HTTP リクエストのタイムアウト（秒） |

## 使用例

```python
from fino_filing import EdgerConfig, EdgerDocumentsCollector
from fino_filing.collection import Collection

config = EdgerConfig(user_agent_email="your@email.com")
coll = Collection("/path/to/root")
collector = EdgerDocumentsCollector(coll, config)
collector.collect(cik_list=["320193"], limit_per_company=2)
```
