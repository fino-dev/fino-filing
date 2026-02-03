## 基本的な利用

```python
from fino_filing import Collection, LocalStorage, IndexDB, RegistryManager, CollectionSpec
from fino_filing.collection.spec import StandardIDStrategy, DateBasedPlacement

# 初期化
storage = LocalStorage("./data")
index_db = IndexDB("./index.db")
spec = CollectionSpec(
    id_strategy=StandardIDStrategy(),
    registry_strategy=DateBasedPlacement(),
)
registry_mgr = RegistryManager(storage, spec)

collection = Collection(storage, index_db, registry_mgr, spec)

# Filing追加（Collectorから）
from fino_filing.edinet import EdinetCollector

collector = EdinetCollector(collection, api_key="...")
collector.collect_date(date(2024, 1, 15))

# 検索
filings = collection.find(source="edinet", document_type="120")

# 取得
filing = collection.get("edinet:S100XXXX:a1b2c3d4")
content = filing.get_content()
```

## DBロスト復元

```python
# DBファイルが消失した想定
import os
os.remove("./index.db")

# 新しいDB作成
index_db = IndexDB("./index.db")

collection = Collection(storage, index_db, registry_mgr, spec)

# Registry から再構築
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

if issues["missing_payload"]:
    print(f"Missing payloads: {issues['missing_payload']}")

```

## Storage移行

```python
from fino_filing.storage import S3Storage

# S3への移行
s3_storage = S3Storage(bucket="my-filings", prefix="prod")
collection.migrate(s3_storage)

# 移行後も同じAPIで操作可能
filings = collection.find(source="edgar")

```

## カスタムSpec

```python
from fino_filing.collection.spec import SecureIDStrategy, HybridPlacement

# セキュアID + ハイブリッド配置
spec = CollectionSpec(
    id_strategy=SecureIDStrategy(),
    registry_strategy=HybridPlacement(),
)

collection = Collection(storage, index_db, registry_mgr, spec)
```
