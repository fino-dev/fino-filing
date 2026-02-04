## 基本的な利用

```python
from fino_filing.collection import Collection, FlatLocalStorage, IndexDB

# 初期化
storage = FlatLocalStorage("./data")
index_db = IndexDB("./index.db")
collection = Collection(storage, index_db)

# Filing追加(Collectorから)
from fino_filing.edinet import EdinetCollector

collector = EdinetCollector(collection, api_key="...")
collector.collect_date(date(2024, 1, 15))

# 検索
filings = collection.find(source="edinet", document_type="120")

# 取得
filing = collection.get("edinet:S100XXXX:a1b2c3d4")
content = filing.get_content()
```

## DB ロスト復元

```python
# DBファイルが消失した想定
import os
os.remove("./index.db")

# 新しいDB作成
index_db = IndexDB("./index.db")
collection = Collection(storage, index_db)

# StorageのRegistryから再構築
collection.rebuild_index()

# 検索可能に復旧
filings = collection.find(source="edinet")
print(f"Recovered {len(filings)} filings")
```

## 整合性検証

```python
# 定期的な整合性チェック
issues = collection.verify_integrity()

if issues["checksum_mismatch"]:
    print(f"Checksum mismatches: {issues['checksum_mismatch']}")

if issues["missing_in_storage"]:
    print(f"Missing in storage: {issues['missing_in_storage']}")

if issues["missing_in_index"]:
    print(f"Missing in index: {issues['missing_in_index']}")
```

## Storage 移行

```python
from fino_filing.collection import FlatLocalStorage

# 別のStorageへ移行
new_storage = FlatLocalStorage("./data_new")
collection.migrate(new_storage)

# 移行後も同じAPIで操作可能
filings = collection.find(source="edgar")
```
