# Packageのインターフェース

## ユースケース

### 1. Getting Started Usecase（現状実装）

```python
import fino_filing as fec

# デフォルト: カレントディレクトリの .fino/collection に LocalStorage + Catalog
collection = fec.Collection()

# または明示指定
storage = fec.LocalStorage("/path/to/data")
catalog = fec.Catalog("/path/to/index.db")
collection = fec.Collection(storage=storage, catalog=catalog)

# Filing を追加（例: EDINETFiling）
filing = fec.EDINETFiling(
    source="edinet",
    name="doc.xbrl",
    checksum="sha256hex...",
    format="xbrl",
    is_zip=False,
    # 任意の indexed フィールド
)
content = b"..."
collection.add(filing, content)

# 検索（Expr API）
from fino_filing import Expr, Field
filings = collection.search(expr=Field("source") == "edinet", limit=100)

# ID で取得
filing = collection.get_filing("filing_id")
content = collection.get_content("filing_id")
# または一括
filing, content, path = collection.get("filing_id")
if filing:
    name = filing.name
# path は保存先の相対パス（str | None）
```

> 収集（EDINET API 連携・sync_catalog / collect）は今後実装予定。
