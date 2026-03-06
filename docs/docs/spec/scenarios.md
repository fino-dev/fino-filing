# 利用シナリオ

## 基本的な利用

```python
from fino_filing import Collection, LocalStorage, Catalog

# 初期化
storage = LocalStorage("./data")
catalog = Catalog("./index.db")
collection = Collection(storage=storage, catalog=catalog)

# Filing 追加（現状は手動。EDINET API 連携の Collector は今後実装予定）
from fino_filing import EDINETFiling

filing = EDINETFiling(source="edinet", name="doc.xbrl", checksum="...", format="xbrl", is_zip=False)
collection.add(filing, b"...")

# 検索
from fino_filing import Expr, Field
filings = collection.search(expr=Field("source") == "edinet", limit=100, offset=0)

# 取得（メタデータ）
filing = collection.get_filing("filing_id")
# 取得（ファイル本体・arelle 等で解析する場合）
content = collection.get_content("filing_id")
# または一括
filing, content, path = collection.get("filing_id")
```

> Note: rebuild_index, verify_integrity, migrate は現在未実装。収集（EdinetCollector 等）は今後実装予定。
