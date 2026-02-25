## 基本的な利用

```python
from fino_filing.collection import Collection, LocalStorage, Catalog

# 初期化
storage = LocalStorage("./data")
catalog = Catalog("./index.db")
collection = Collection(storage, catalog)

# Filing追加(Collectorから)
from fino_filing.edinet import EdinetCollector

collector = EdinetCollector(collection, api_key="...")
collector.collect_date(date(2024, 1, 15))

# 検索
filings = collection.find(expr=..., limit=100, offset=0)

# 取得（メタデータ）
filing = collection.get("edinet:S100XXXX:a1b2c3d4")
# 取得（ファイル本体・arelle等で解析する場合）
content = collection.get_content("edinet:S100XXXX:a1b2c3d4")
```

> Note: rebuild_index, verify_integrity, migrate は現在未実装

## 設計: 物理名・Partition の責務

- **Locator**: Filing のメタデータからストレージ用の論理キー（partition + ファイル名 + 拡張子）を決定する。拡張子は **format** が設定されていればそれを使用（空の場合は **is_zip** に応じて .zip / .xbrl）。ユーザーは Locator を差し替えることで partition やファイル名ルールをカスタマイズできる。
- **Storage**: 渡された `storage_key` をそのまま保存先として使用する。キー生成は行わない（LocalStorage は `storage_key` 未指定時のみ従来の checksum.zip で後方互換）。
