---
sidebar_position: 1
title: EdgarConfig
---

# EdgarConfig

Edgar 用のユーザー設定。各 Collector のコンストラクタで渡す。SEC は有効な User-Agent を要求するため、`user_agent_email` は必須。

## Constructor

`HttpClientConfig` を継承する dataclass。**必須フィールドは `user_agent_email` のみ**。`rate_limit_delay`, `timeout`, `max_retries`, `retry_status_codes` 等は親クラスと同じ意味・既定値を持つ。

## 使用例

```python
from fino_filing import Collection, EdgarArchiveCollector, EdgarConfig

config = EdgarConfig(user_agent_email="your@email.com")
coll = Collection()
collector = EdgarArchiveCollector(coll, config)
collector.collect(cik_list=["320193"], limit_per_company=2)
```
