# fino Architecture Redesign Guide

## 概要

このドキュメントは、4つの成功したPython OSSライブラリ(FastAPI、Pydantic、pytest、Typer)の設計思想を分析し、その知見をfinoライブラリの設計に適用したアーキテクチャ再設計の詳細ガイドです。

---

## 設計変更のサマリー

### 主要な変更点

| 項目                 | 変更前                                 | 変更後                                  | 参考OSS  |
| -------------------- | -------------------------------------- | --------------------------------------- | -------- |
| **パッケージ構造**   | 層ベース (application/domain/adapters) | 公開/内部分離 (fino/ + \_internal/)     | Pydantic |
| **公開API**          | 全てのクラスが公開                     | `__init__.py`で明示的エクスポート       | Typer    |
| **拡張性**           | 固定的なアダプター実装                 | プラグインシステム                      | pytest   |
| **デザインパターン** | 暗黙的                                 | 明示的(Factory/Builder/Strategy/Plugin) | 全て     |
| **型安全性**         | 基本的な型ヒント                       | Pydanticモデル、バリデーション          | Pydantic |
| **依存性の方向**     | 不明確                                 | 内向き(公開API → 内部実装)              | Pydantic |

---

## レイヤーアーキテクチャの詳細

### Layer 1: Public API (fino/**init**.py)

**役割**: ユーザーが直接使用するインターフェース

**公開クラス**:

- `Edinet`: メインクライアント
- `Collection`: コレクション管理
- `CollectionSpecBuilder`: ビルダー
- `Filing`: 開示書類モデル
- `FilingMetadata`: メタデータ
- `FormatType`, `DocumentType`: 型定義
- `FinoConfig`: 設定

**設計思想** (Typerスタイル):

```python
# fino/__init__.py
from .client import Edinet as Edinet
from .client import Collection as Collection
from .models import Filing as Filing
from .models import FilingMetadata as FilingMetadata
from .types import FormatType as FormatType
from .types import DocumentType as DocumentType
from .builders import CollectionSpecBuilder as CollectionSpecBuilder
from .config import FinoConfig as FinoConfig

__all__ = [
    "Edinet",
    "Collection",
    "Filing",
    "FilingMetadata",
    "FormatType",
    "DocumentType",
    "CollectionSpecBuilder",
    "FinoConfig",
]
```

**利点**:

- セマンティックバージョニングで後方互換性保証
- ユーザーが使うべきAPIが明確
- リファクタリングが容易

---

### Layer 2: Domain Models (fino.models, fino.types)

**役割**: ビジネスロジックとデータ構造の定義

#### 値オブジェクト (Value Objects)

**`Filing`** - イミュータブルな開示書類

```python
from pydantic import BaseModel, Field

class Filing(BaseModel):
    """開示書類(値オブジェクト)"""
    document_id: str = Field(..., description="文書ID")
    partition: tuple[str, ...] = Field(..., description="パーティション")
    file_name: str = Field(..., description="ファイル名")
    path: Path = Field(..., description="保存パス")
    format_type: FormatType = Field(..., description="フォーマット種別")
    metadata: FilingMetadata = Field(..., description="メタデータ")

    model_config = {"frozen": True}  # イミュータブル

    def open(self) -> IO[bytes]:
        """ファイルを開く"""
        ...
```

**設計判断**:

- `frozen=True`でイミュータブル化(金融データの改ざん防止)
- Pydanticで自動バリデーション
- 型ヒントで静的解析可能

**`Period`** - イミュータブルな期間

```python
class Period(BaseModel):
    """期間(値オブジェクト)"""
    start_date: date
    end_date: date

    model_config = {"frozen": True}

    @field_validator("end_date")
    @classmethod
    def validate_end_after_start(cls, v: date, info: ValidationInfo) -> date:
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be >= start_date")
        return v

    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days
```

**設計判断**:

- バリデーションロジックをモデルに組み込む(Pydanticスタイル)
- ビジネスルール(開始日 <= 終了日)を型レベルで保証

#### エンティティ (Entities)

**`FilingMetadata`** - 識別子を持つメタデータ

```python
class FilingMetadata(BaseModel):
    """開示書類メタデータ(エンティティ)"""
    seq_number: str
    doc_id: str  # 主キー
    parent_doc_id: str | None = None
    edinet_code: str
    sec_code: str | None = None
    period: Period
    submit_datetime: datetime
    filing_name: str
    document_type: DocumentType
    available_format_types: list[FormatType]

    def __hash__(self) -> int:
        return hash(self.doc_id)  # 識別子でハッシュ

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FilingMetadata):
            return False
        return self.doc_id == other.doc_id  # 識別子で比較
```

**設計判断**:

- `doc_id`を識別子として使用
- 等価性を識別子ベースで判定(DDD原則)

---

### Layer 3: Plugin Interfaces (fino.plugins)

**役割**: 拡張可能なバックエンドの抽象化

#### プラグインシステムの設計 (pytestスタイル)

**`StoragePlugin`** - ストレージバックエンド

```python
from abc import ABC, abstractmethod
from typing import Protocol

class StoragePlugin(Protocol):
    """ストレージプラグインインターフェース"""

    def save(self, path: Path, content: bytes) -> Path:
        """ファイルを保存"""
        ...

    def load(self, path: Path) -> bytes:
        """ファイルを読み込み"""
        ...

    def exists(self, path: Path) -> bool:
        """ファイルの存在確認"""
        ...

    def delete(self, path: Path) -> None:
        """ファイルを削除"""
        ...

    def list(self, prefix: Path) -> list[Path]:
        """ファイル一覧を取得"""
        ...
```

**設計判断**:

- `Protocol`を使用(ダックタイピング、Pydanticスタイル)
- 最小限のインターフェース(5メソッド)
- 実装クラスは継承不要

**`MetadataPlugin`** - メタデータストア

```python
class MetadataPlugin(Protocol):
    """メタデータプラグインインターフェース"""

    def save(self, filing: Filing) -> None:
        """メタデータを保存"""
        ...

    def save_batch(self, filings: list[Filing]) -> None:
        """バッチ保存"""
        ...

    def search(self, **conditions) -> list[Filing]:
        """検索"""
        ...

    def get(self, document_id: str) -> Filing:
        """ID指定で取得"""
        ...

    def count(self, **conditions) -> int:
        """件数取得"""
        ...
```

#### プラグイン登録システム (pytestスタイル)

**`PluginRegistry`**

```python
class PluginRegistry:
    """プラグイン登録・管理"""
    _storage_plugins: dict[str, type[StoragePlugin]] = {}
    _metadata_plugins: dict[str, type[MetadataPlugin]] = {}

    @classmethod
    def register_storage(cls, name: str, plugin: type[StoragePlugin]) -> None:
        """ストレージプラグイン登録"""
        cls._storage_plugins[name] = plugin

    @classmethod
    def register_metadata(cls, name: str, plugin: type[MetadataPlugin]) -> None:
        """メタデータプラグイン登録"""
        cls._metadata_plugins[name] = plugin

    @classmethod
    def get_storage(cls, name: str) -> type[StoragePlugin]:
        """ストレージプラグイン取得"""
        return cls._storage_plugins[name]

    @classmethod
    def discover_plugins(cls) -> None:
        """エントリーポイントからプラグイン発見"""
        import importlib.metadata

        for entry_point in importlib.metadata.entry_points(group="fino.storage"):
            plugin = entry_point.load()
            cls.register_storage(entry_point.name, plugin)

        for entry_point in importlib.metadata.entry_points(group="fino.metadata"):
            plugin = entry_point.load()
            cls.register_metadata(entry_point.name, plugin)
```

**使用例**:

```python
# プラグイン自動発見
PluginRegistry.discover_plugins()

# カスタムプラグイン登録
from my_plugin import MyCustomStorage
PluginRegistry.register_storage("custom", MyCustomStorage)

# プラグイン使用
storage_cls = PluginRegistry.get_storage("s3")
storage = storage_cls(bucket="my-bucket")
```

**`setup.py`でのプラグイン定義**:

```python
setup(
    name="fino-s3-storage",
    entry_points={
        "fino.storage": [
            "s3 = fino_s3.storage:S3Storage",
        ],
    },
)
```

**設計判断**:

- エントリーポイントベースの自動発見(pytestスタイル)
- 実行時登録もサポート(柔軟性)
- プラグイン名前空間で衝突回避

---

### Layer 4: Internal Implementation (fino.\_internal)

**役割**: 非公開の内部実装

#### パッケージ構成

```
fino/_internal/
├── __init__.py
├── adapters/
│   ├── __init__.py
│   └── edinet.py          # EDINET API統合
├── factories/
│   ├── __init__.py
│   ├── filing.py          # Filingファクトリー
│   └── client.py          # クライアントファクトリー
├── validators/
│   ├── __init__.py
│   └── filing.py          # バリデーションロジック
├── collectors/
│   ├── __init__.py
│   └── manager.py         # コレクション管理
└── strategies/
    ├── __init__.py
    ├── storage.py         # ストレージ実装
    └── metadata.py        # メタデータストア実装
```

#### Factory Pattern (Pydanticスタイル)

**`FilingFactory`**

```python
# fino/_internal/factories/filing.py
class FilingFactory:
    """Filing生成ファクトリー"""

    @staticmethod
    def from_metadata(
        metadata: FilingMetadata,
        spec: CollectionSpec,
        format_type: FormatType,
    ) -> Filing:
        """メタデータからFilingを生成"""
        path = spec.generate_path(metadata)
        partition = tuple(spec.render_partition(metadata))
        file_name = spec.render_file_name(metadata, format_type)

        return Filing(
            document_id=metadata.doc_id,
            partition=partition,
            file_name=file_name,
            path=path / file_name,
            format_type=format_type,
            metadata=metadata,
        )

    @staticmethod
    def from_dict(data: dict) -> Filing:
        """辞書からFilingを生成"""
        metadata = FilingMetadata.model_validate(data["metadata"])
        return Filing(
            document_id=data["document_id"],
            partition=tuple(data["partition"]),
            file_name=data["file_name"],
            path=Path(data["path"]),
            format_type=FormatType(data["format_type"]),
            metadata=metadata,
        )

    @staticmethod
    def batch_from_catalog(catalog: list[dict]) -> list[FilingMetadata]:
        """カタログからメタデータバッチ生成"""
        return [FilingMetadata.model_validate(item) for item in catalog]
```

**設計判断**:

- 静的メソッドで状態を持たない(Pydanticスタイル)
- 複数の生成方法を提供(from_metadata, from_dict, batch)
- Pydanticのバリデーションを活用

#### Strategy Pattern (FastAPIスタイル)

**ストレージストラテジー実装**

```python
# fino/_internal/strategies/storage.py
class LocalFileStorage:
    """ローカルファイルストレージ実装"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.root_path.mkdir(parents=True, exist_ok=True)

    def save(self, path: Path, content: bytes) -> Path:
        full_path = self.root_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return full_path

    def load(self, path: Path) -> bytes:
        return (self.root_path / path).read_bytes()

    def exists(self, path: Path) -> bool:
        return (self.root_path / path).exists()

    def delete(self, path: Path) -> None:
        (self.root_path / path).unlink(missing_ok=True)

    def list(self, prefix: Path) -> list[Path]:
        full_prefix = self.root_path / prefix
        if not full_prefix.exists():
            return []
        return [p.relative_to(self.root_path) for p in full_prefix.rglob("*") if p.is_file()]


class S3Storage:
    """S3ストレージ実装"""

    def __init__(self, bucket: str, prefix: str = "", **kwargs):
        import boto3
        self.bucket = bucket
        self.prefix = prefix
        self.client = boto3.client("s3", **kwargs)

    def save(self, path: Path, content: bytes) -> Path:
        key = f"{self.prefix}/{path}" if self.prefix else str(path)
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content)
        return Path(key)

    # ... 他のメソッド実装
```

**設計判断**:

- 各ストレージ実装が独立(Strategy Pattern)
- 同じインターフェース(StoragePlugin)を実装
- 実行時に切り替え可能(FastAPIスタイル)

---

### Layer 5: Configuration & Exceptions

#### 設定管理 (Pydantic BaseSettings)

**`FinoConfig`**

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class EdinetConfig(BaseSettings):
    """EDINET設定"""
    api_key: str | None = None
    base_url: str = "https://api.edinet-fsa.go.jp"
    timeout: int = 30
    retry_count: int = 3

    model_config = {
        "env_prefix": "FINO_EDINET_",
        "env_file": ".env",
    }

    @classmethod
    def from_env(cls) -> "EdinetConfig":
        return cls()


class FinoConfig(BaseModel):
    """fino全体設定"""
    edinet: EdinetConfig
    storage: StorageConfig
    metadata: MetadataConfig

    @classmethod
    def from_file(cls, path: Path) -> "FinoConfig":
        """ファイルから読み込み"""
        import tomli
        with open(path, "rb") as f:
            data = tomli.load(f)
        return cls.model_validate(data)

    @classmethod
    def from_env(cls) -> "FinoConfig":
        """環境変数から読み込み"""
        return cls(
            edinet=EdinetConfig.from_env(),
            storage=StorageConfig.from_env(),
            metadata=MetadataConfig.from_env(),
        )
```

**設計判断**:

- Pydantic BaseSettingsで環境変数を自動読み込み
- 型安全な設定管理
- TOML/環境変数の両方をサポート

#### 例外階層

```python
class FinoException(Exception):
    """finoベース例外"""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ValidationError(FinoException):
    """バリデーションエラー"""
    pass


class APIError(FinoException):
    """API呼び出しエラー"""
    pass


class StorageError(FinoException):
    """ストレージエラー"""
    pass


class MetadataError(FinoException):
    """メタデータエラー"""
    pass


class PluginError(FinoException):
    """プラグインエラー"""
    pass
```

---

## デザインパターンの適用

### 1. Factory Pattern (Pydanticスタイル)

**目的**: オブジェクト生成ロジックの一元化

**実装**:

- `FilingFactory`: メタデータからFilingを生成
- `EdinetClientFactory`: 設定からクライアントを生成
- `DocumentType.from_code()`: コードから型を生成

**利点**:

- 生成ロジックが一箇所に集約
- テストでモックオブジェクト作成が容易
- バリデーションを確実に実行

### 2. Builder Pattern (Typerスタイル)

**目的**: 複雑なオブジェクトの段階的構築

**実装**: `CollectionSpecBuilder`

```python
spec = (
    CollectionSpecBuilder()
    .with_partition(SpecField.EDINET_CODE, SpecField.PERIOD_START)
    .with_file_name(SpecField.DOC_ID, SpecField.DOCUMENT_TYPE)
    .with_custom_field("version", "v1")
    .build()
)
```

**利点**:

- メソッドチェーンで直感的
- デフォルト値を段階的にオーバーライド
- ビルド時にバリデーション実行

### 3. Strategy Pattern (FastAPIスタイル)

**目的**: アルゴリズムの切り替え

**実装**:

- `StorageStrategy`: ストレージバックエンドの切り替え
- `MetadataStrategy`: メタデータストアの切り替え

**利点**:

- 実行時に戦略を切り替え可能
- 新しい実装を追加しやすい
- テストで戦略をモックに差し替え可能

### 4. Plugin Pattern (pytestスタイル)

**目的**: 拡張可能なアーキテクチャ

**実装**: `PluginRegistry`、エントリーポイント

**利点**:

- ユーザーが独自のバックエンドを追加可能
- コアライブラリを変更せずに拡張
- プラグイン発見を自動化

### 5. Adapter Pattern (Pydanticスタイル)

**目的**: 外部システムの抽象化

**実装**: `EdinetApiAdapter`

**利点**:

- EDINET APIの詳細を隠蔽
- API変更時の影響を局所化
- テストでモックに差し替え可能

---

## 依存性の方向

### 原則: 依存性は内向きに

```
Public API (Edinet, Collection)
    ↓ uses
Domain Models (Filing, FilingMetadata)
    ↓ uses
Plugin Interfaces (StoragePlugin, MetadataPlugin)
    ↑ implements
Internal Implementation (_internal)
```

### 依存性逆転の原則 (DIP)

- `Edinet`は`StoragePlugin`に依存(抽象)
- `LocalFileStorage`は`StoragePlugin`を実装(具象)
- `Edinet`は`LocalFileStorage`を知らない

**利点**:

- 内部実装を変更しても公開APIは影響なし
- テストで依存関係を差し替え可能
- モジュール間の結合度が低い

---

## 型安全性の実現

### Pydanticモデルの活用

**自動バリデーション**:

```python
filing_metadata = FilingMetadata(
    seq_number="123",
    doc_id="S100ABCD",
    # ... 他のフィールド
    period=Period(
        start_date=date(2023, 4, 1),
        end_date=date(2023, 3, 31),  # エラー: start > end
    ),
)
# ValidationError: end_date must be >= start_date
```

**型チェック対応**:

- 全てのパブリックAPIに型ヒント
- ジェネリクスで型安全性を確保

---

## 使いやすさの向上

### シンプルなAPI (Typerスタイル)

**最小限のコード**:

```python
import fino

# デフォルト設定で即座に動作
edinet = fino.Edinet()

# 型ヒントでエディタ補完
filings = edinet.search(
    edinet_code="E12345",
    period_start="2023-04-01",
)

# メソッドチェーンで直感的
spec = (
    fino.CollectionSpecBuilder()
    .with_partition(fino.SpecField.EDINET_CODE)
    .with_file_name(fino.SpecField.DOC_ID)
    .build()
)
```

### 明確なエラーメッセージ

```python
try:
    edinet.collect(document_id="INVALID")
except fino.ValidationError as e:
    print(e.message)
    print(e.details)
    # {
    #   "field": "document_id",
    #   "error": "Invalid format",
    #   "expected": "S100XXXX",
    #   "received": "INVALID",
    # }
```

---

## 拡張性の実現

### プラグインシステム

**ユーザーがカスタムストレージを追加**:

```python
# my_custom_storage.py
class RedisStorage:
    """Redisストレージ実装"""
    def __init__(self, host: str, port: int):
        import redis
        self.client = redis.Redis(host=host, port=port)

    def save(self, path: Path, content: bytes) -> Path:
        self.client.set(str(path), content)
        return path

    # ... 他のメソッド

# 登録
fino.PluginRegistry.register_storage("redis", RedisStorage)

# 使用
edinet = fino.Edinet(storage="redis", storage_options={"host": "localhost", "port": 6379})
```

**setup.pyでプラグイン配布**:

```python
# fino-redis-storage/setup.py
setup(
    name="fino-redis-storage",
    entry_points={
        "fino.storage": [
            "redis = fino_redis.storage:RedisStorage",
        ],
    },
)
```

---

## まとめ

### 設計原則の適用

| 原則              | 適用方法                    | 参考OSS  |
| ----------------- | --------------------------- | -------- |
| **公開/内部分離** | `_internal/`ディレクトリ    | Pydantic |
| **型安全性**      | Pydanticモデル、型ヒント    | Pydantic |
| **シンプルさ**    | 最小限のAPI、デフォルト設定 | Typer    |
| **拡張性**        | プラグインシステム          | pytest   |
| **依存性注入**    | Strategy Pattern            | FastAPI  |

### 期待される効果

1. **保守性**: 内部実装の変更が公開APIに影響しない
2. **拡張性**: ユーザーが独自のバックエンドを追加可能
3. **使いやすさ**: シンプルで直感的なAPI
4. **型安全性**: 静的解析と実行時バリデーション
5. **開発者体験**: エディタ補完、明確なエラーメッセージ

### 次のステップ

1. **実装**: 新しいアーキテクチャに基づいた実装
2. **テスト**: 包括的なテストスイート
3. **ドキュメント**: APIドキュメント、チュートリアル
4. **プラグイン**: 標準プラグインの実装

---

## 参考リンク

- **Pydantic**: https://docs.pydantic.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **pytest**: https://docs.pytest.org/
- **Typer**: https://typer.tiangolo.com/
- **Python Packaging**: https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
