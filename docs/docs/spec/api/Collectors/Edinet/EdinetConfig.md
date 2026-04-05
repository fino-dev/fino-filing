---
sidebar_position: 0
title: EdinetConfig
---

# EdinetConfig

EDINET API 用のユーザー設定。Collector のコンストラクタで渡す。API のベース URL は固定のため `api_base` は持たない。

## Constructor

`HttpClientConfig` を継承。**必須は `api_key`**。EDINET 向けに `rate_limit_delay` 既定 `1.0`、`retry_backoff_factor` 既定 `10.0`、`max_retries` 既定 `2` など親クラスより控えめな既定を持つ。`timeout` 等は親と同じキーワードで指定可能。

## API key (Subscription-Key)

Use the value from EDINET as `api_key`. For account creation or contact updates, follow the instructions on the EDINET site (see also [account / contact](https://api.edinet-fsa.go.jp/api/auth/index.aspx?mode=1)).

To **reissue** an API key, open the official issuance screen:

- [EDINET API key issuance / reissue](https://api.edinet-fsa.go.jp/WEEE0090.aspx)

## 使用例

```python
from datetime import date

from fino_filing import Collection, EdinetCollector, EdinetConfig

config = EdinetConfig(api_key="your-subscription-key")
coll = Collection()
collector = EdinetCollector(coll, config)
collector.collect(date_from=date(2024, 1, 1), date_to=date(2024, 1, 31), limit=10)
```
