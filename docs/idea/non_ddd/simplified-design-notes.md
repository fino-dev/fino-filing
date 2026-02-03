# 簡素化された設計 (DDD概念除去版)

## 概要

DDDの概念(Domain Layer、Facade、Adapter インターフェース、厳密なレイヤー分離)を取り除き、よりシンプルで実用的な設計に変更しました。

## 主な変更点

### 1. レイヤー構造の簡素化

**Before (DDD版)**:

```
Application Layer (Facade)
  ↓
Domain Layer (Models)
  ↓
Adapter Layer (Interfaces)
  ↓
Infrastructure (Implementations)
```

**After (簡素化版)**:

```
Services (ビジネスロジック)
  ↓
Repositories (データアクセス)
  ↓
Models (データ構造)
```

### 2. 削除した概念

#### ✗ Facade パターン

- `Edinet Facade` → `EdinetService`
- `Collection Facade` → `CollectionService`
- 単純なServiceクラスとして実装

#### ✗ Domain Model の厳密な分離

- `Collection Model` → `FilingRepository` に統合
- ビジネスロジックはServiceに配置

#### ✗ Adapter インターフェース

- `EdinetAdapter` (interface) → `EdinetClient` (concrete class)
- `StorageAdapter` (interface) → `FileStorage` (concrete class)
- `MetadataAdapter` (interface) → `MetadataStore` (concrete class)
- インターフェースなしで直接実装クラスを使用

#### ✗ 厳密なレイヤー境界

- 必要に応じて直接依存
- 依存性の注入は最小限

### 3. 新しいクラス構造

#### Services (公開API)

```python
# services/edinet_service.py
class EdinetService:
    """EDINET連携のメインAPI"""
    def __init__(self, api_key: str, filing_repo: FilingRepository):
        self.edinet_client = EdinetClient(api_key)
        self.filing_repo = filing_repo

    def sync_catalog(self) -> None:
        """カタログを同期"""
        catalog = self.edinet_client.fetch_catalog()
        # 処理...

    def collect(self, **conditions) -> CollectResult:
        """書類を収集"""
        filings = self.search(**conditions)
        results = []
        for filing in filings:
            content = self.edinet_client.fetch_document(filing.doc_id)
            saved = self.filing_repo.save(filing, content)
            results.append(saved)
        return CollectResult(collected=results)

# services/collection_service.py
class CollectionService:
    """コレクション管理API"""
    def __init__(self, filing_repo: FilingRepository):
        self.filing_repo = filing_repo

    def search(self, **conditions) -> list[Filing]:
        return self.filing_repo.search(**conditions)

    def get(self, document_id: str) -> Filing:
        return self.filing_repo.get(document_id)
```

#### Repositories (データアクセス)

```python
# repositories/filing_repository.py
class FilingRepository:
    """Filing のデータアクセス"""
    def __init__(
        self,
        storage: FileStorage,
        metadata_store: MetadataStore,
        spec: CollectionSpec
    ):
        self.storage = storage
        self.metadata_store = metadata_store
        self.spec = spec

    def save(self, filing: Filing, content: bytes) -> Filing:
        """書類を保存"""
        path = self.spec.generate_path(filing.metadata)
        self.storage.save(path, content)
        self.metadata_store.save(filing)
        return filing

    def search(self, **conditions) -> list[Filing]:
        return self.metadata_store.search(**conditions)

# repositories/edinet_client.py
class EdinetClient:
    """EDINET API クライアント"""
    def __init__(self, api_key: str, base_url: str = DEFAULT_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.session = httpx.Client()

    def fetch_catalog(self, date: date = None) -> list[dict]:
        """カタログ取得"""
        response = self.session.get(f"{self.base_url}/catalog")
        return response.json()

    def fetch_document(self, document_id: str, format_type: FormatType) -> bytes:
        """書類ファイル取得"""
        response = self.session.get(f"{self.base_url}/documents/{document_id}")
        return response.content

# repositories/file_storage.py
class FileStorage:
    """ファイルストレージ"""
    def __init__(self, root_path: Path, storage_type: str = "local"):
        self.root_path = root_path
        self.storage_type = storage_type

    def save(self, path: Path, content: bytes) -> Path:
        full_path = self.root_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return full_path

    def load(self, path: Path) -> bytes:
        full_path = self.root_path / path
        return full_path.read_bytes()

# repositories/metadata_store.py
class MetadataStore:
    """メタデータストア"""
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)

    def save(self, filing: Filing) -> None:
        """メタデータ保存"""
        # SQL insert...

    def search(self, **conditions) -> list[Filing]:
        """検索"""
        # SQL query...
```

#### Models (データ構造)

```python
# models/filing.py
class Filing(BaseModel):
    """書類エンティティ"""
    document_id: str
    partition: list[str]
    file_name: str
    path: Path
    format_type: FormatType
    metadata: FilingMetadata

    def open(self) -> IO[bytes]:
        """ファイルを開く"""
        return self.path.open('rb')

# models/filing_metadata.py
class FilingMetadata(BaseModel):
    """書類メタデータ"""
    seq_number: str
    doc_id: str
    edinet_code: str
    sec_code: str | None
    period: Period
    submit_datetime: datetime
    filing_name: str
    document_type: DocumentType
    available_format_types: list[FormatType]
```

### 4. 使用例

```python
import fino_edinet_collector as fec

# 設定
config = fec.Config(
    edinet_api_key="YOUR_API_KEY",
    storage_root_path="~/.edinet_files",
    storage_type="local",
    metadata_db_path="~/.edinet_files/metadata.db"
)

# Repositories のセットアップ
storage = fec.FileStorage(config.storage_root_path, config.storage_type)
metadata = fec.MetadataStore(config.metadata_db_path)
spec = fec.CollectionSpec(
    partition=[fec.SpecField.SEC_CODE, fec.SpecField.PERIOD_START],
    file_name=[fec.SpecField.DOC_ID]
)

filing_repo = fec.FilingRepository(storage, metadata, spec)

# Services
edinet = fec.EdinetService(config.edinet_api_key, filing_repo)
collection = fec.CollectionService(filing_repo)

# 使用
edinet.sync_catalog()
result = edinet.collect(document_type=fec.DocumentTypeEnum.ANNUAL_REPORT)

filings = collection.search(sec_code="1111")
filing = collection.get("S100XXXX")
```

## メリット

### シンプルさ

- レイヤーが3層から2層に削減
- インターフェースが不要
- 概念的な複雑さが減少

### 実装の容易さ

- 直接実装クラスを使用
- モックやテストが簡単
- 依存性注入が最小限

### 保守性

- クラス数が少ない
- 依存関係が明確
- リファクタリングしやすい

## デメリット

### 拡張性の低下

- ストレージの切り替えがやや面倒(クラス変更が必要)
- 複数実装の切り替えに柔軟性がない
- プラグインシステムの構築が難しい

### テストの柔軟性

- インターフェースがないのでモック作成が少し面倒
- ただし、具体クラスを直接モックできるので実用上は問題なし

### 将来の変更

- 要件が大きく変わると再設計が必要になる可能性
- ただし、現時点ではシンプルさを優先

## 推奨する使い分け

### 簡素化版を選ぶべきケース

- 小規模プロジェクト
- 単一ストレージ・単一DB
- チームが小さい
- 速い開発サイクル

### DDD版を選ぶべきケース

- 大規模プロジェクト
- 複数ストレージバックエンドの切り替えが必要
- プラグインシステムが必要
- 長期的な保守性を重視

## ファイル構成

```
src/fino_edinet_collector/
├── __init__.py
├── services/
│   ├── __init__.py
│   ├── edinet_service.py
│   └── collection_service.py
├── repositories/
│   ├── __init__.py
│   ├── filing_repository.py
│   ├── edinet_client.py
│   ├── file_storage.py
│   └── metadata_store.py
├── models/
│   ├── __init__.py
│   ├── filing.py
│   ├── filing_metadata.py
│   ├── collection_spec.py
│   └── types.py
└── config.py
```

## まとめ

DDDの概念を取り除くことで、より直感的でシンプルな設計になりました。小中規模のプロジェクトや、シンプルさを重視する場合にはこの設計が適しています。
