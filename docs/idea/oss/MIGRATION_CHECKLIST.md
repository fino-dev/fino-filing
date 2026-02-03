# fino Architecture Migration Checklist

現在の設計から新しい設計への移行チェックリスト

---

## Phase 1: パッケージ構造の再編成

### ディレクトリ構造の作成

- [ ] `fino/__init__.py` - 公開APIエクスポート
- [ ] `fino/client.py` - Edinet, Collectionクラス
- [ ] `fino/models.py` - Filing, FilingMetadataクラス
- [ ] `fino/types.py` - FormatType, DocumentType, DocumentTypeEnum
- [ ] `fino/builders.py` - CollectionSpecBuilder
- [ ] `fino/config.py` - FinoConfig, EdinetConfig等
- [ ] `fino/exceptions.py` - 例外階層
- [ ] `fino/plugins/__init__.py` - プラグインインターフェース
- [ ] `fino/plugins/storage.py` - StoragePlugin
- [ ] `fino/plugins/metadata.py` - MetadataPlugin
- [ ] `fino/plugins/registry.py` - PluginRegistry
- [ ] `fino/_internal/__init__.py` - 内部実装パッケージ
- [ ] `fino/_internal/adapters/__init__.py`
- [ ] `fino/_internal/adapters/edinet.py` - EdinetApiAdapter
- [ ] `fino/_internal/factories/__init__.py`
- [ ] `fino/_internal/factories/filing.py` - FilingFactory
- [ ] `fino/_internal/factories/client.py` - EdinetClientFactory
- [ ] `fino/_internal/validators/__init__.py`
- [ ] `fino/_internal/validators/filing.py` - FilingValidator
- [ ] `fino/_internal/collectors/__init__.py`
- [ ] `fino/_internal/collectors/manager.py` - CollectionManager
- [ ] `fino/_internal/strategies/__init__.py`
- [ ] `fino/_internal/strategies/storage.py` - LocalFileStorage, S3Storage, GCSStorage
- [ ] `fino/_internal/strategies/metadata.py` - SQLiteMetadata, PostgreSQLMetadata, DynamoDBMetadata

### 既存コードの移動

**application層 → 公開API**
- [ ] `application.Edinet` → `fino.client.Edinet`
- [ ] `application.Collection` → `fino.client.Collection`

**domain層 → models/types**
- [ ] `domain.Filing` → `fino.models.Filing`
- [ ] `domain.FilingMetadata` → `fino.models.FilingMetadata`
- [ ] `domain.Period` → `fino.models.Period`
- [ ] `domain.CollectionSpec` → `fino.models.CollectionSpec`
- [ ] `domain.SpecField` → `fino.types.SpecField`
- [ ] `domain.CustomSpecField` → `fino.models.CustomSpecField`
- [ ] `domain.FormatType` → `fino.types.FormatType`
- [ ] `domain.DocumentType` → `fino.types.DocumentType`
- [ ] `domain.DocumentTypeEnum` → `fino.types.DocumentTypeEnum`

**adapters層 → plugins + _internal**
- [ ] `adapters.interfaces.EdinetAdapter` → `fino._internal.adapters.edinet.EdinetApiAdapter`
- [ ] `adapters.interfaces.StorageAdapter` → `fino.plugins.storage.StoragePlugin`
- [ ] `adapters.interfaces.MetadataAdapter` → `fino.plugins.metadata.MetadataPlugin`
- [ ] `adapters.implementations.EdinetApiAdapter` → `fino._internal.adapters.edinet.EdinetApiAdapter`
- [ ] `adapters.implementations.LocalFileStorageAdapter` → `fino._internal.strategies.storage.LocalFileStorage`
- [ ] `adapters.implementations.S3StorageAdapter` → `fino._internal.strategies.storage.S3Storage`
- [ ] `adapters.implementations.SQLiteMetadataAdapter` → `fino._internal.strategies.metadata.SQLiteMetadata`
- [ ] `adapters.implementations.DynamoMetadataAdapter` → `fino._internal.strategies.metadata.DynamoDBMetadata`

**config層 → config**
- [ ] `config.EdinetConfig` → `fino.config.EdinetConfig`
- [ ] `config.StorageConfig` → `fino.config.StorageConfig`
- [ ] `config.MetadataConfig` → `fino.config.MetadataConfig`

---

## Phase 2: Pydanticモデル化

### 値オブジェクトのPydantic化

- [ ] `Filing` → `BaseModel` with `frozen=True`
  - [ ] フィールドに`Field()`でdescription追加
  - [ ] `open()`メソッドの保持
  - [ ] `validate()`をPydantic validatorに変更
  
- [ ] `Period` → `BaseModel` with `frozen=True`
  - [ ] `@field_validator`でstart_date <= end_dateを検証
  - [ ] `duration_days()`メソッド追加
  
- [ ] `DocumentType` → `BaseModel` with `frozen=True`
  - [ ] `from_code()`クラスメソッド追加（Factory）
  - [ ] `label_ja`フィールド追加
  
- [ ] `CollectionSpec` → `BaseModel` with `frozen=True`
  - [ ] `@model_validator`でdoc_id/format_type必須検証
  - [ ] `generate_path()`メソッド保持

### エンティティのPydantic化

- [ ] `FilingMetadata` → `BaseModel`
  - [ ] `doc_id`を主キーとして明示
  - [ ] `__hash__`、`__eq__`をオーバーライド
  - [ ] 全フィールドに`Field()`でメタデータ追加
  - [ ] Pydantic validatorで業務ロジック検証

### 設定のPydantic化

- [ ] `EdinetConfig` → `BaseSettings`
  - [ ] `env_prefix = "FINO_EDINET_"`
  - [ ] `from_env()`クラスメソッド
  
- [ ] `StorageConfig` → `BaseSettings`
  - [ ] `env_prefix = "FINO_STORAGE_"`
  
- [ ] `MetadataConfig` → `BaseSettings`
  - [ ] `env_prefix = "FINO_METADATA_"`
  
- [ ] `FinoConfig` → `BaseModel`
  - [ ] 全サブ設定を統合
  - [ ] `from_file(path: Path)`でTOML読み込み
  - [ ] `from_env()`で環境変数読み込み

---

## Phase 3: デザインパターンの実装

### Factory Pattern

- [ ] `FilingFactory`の実装
  - [ ] `from_metadata()` - メタデータからFiling生成
  - [ ] `from_dict()` - 辞書からFiling生成
  - [ ] `batch_from_catalog()` - カタログからバッチ生成
  
- [ ] `EdinetClientFactory`の実装
  - [ ] `create(config)` - 設定からクライアント生成
  - [ ] `from_env()` - 環境変数からクライアント生成
  
- [ ] `DocumentType.from_code()`の実装
  - [ ] コードから型へのマッピング
  - [ ] 不明なコードは`OTHER`にフォールバック

### Builder Pattern

- [ ] `CollectionSpecBuilder`の実装
  - [ ] `with_partition(*fields)` - パーティション指定
  - [ ] `with_file_name(*fields)` - ファイル名指定
  - [ ] `with_custom_field(name, value)` - カスタムフィールド追加
  - [ ] `build()` - CollectionSpec構築
  - [ ] デフォルト値の設定
  - [ ] バリデーション（doc_id/format_type必須）

### Strategy Pattern

**ストレージストラテジー**
- [ ] `LocalFileStorage`の実装
  - [ ] `save()`, `load()`, `exists()`, `delete()`, `list()`
  - [ ] パス管理、ディレクトリ自動作成
  
- [ ] `S3Storage`の実装
  - [ ] boto3統合
  - [ ] エラーハンドリング
  
- [ ] `GCSStorage`の実装（オプション）
  - [ ] google-cloud-storage統合

**メタデータストラテジー**
- [ ] `SQLiteMetadata`の実装
  - [ ] テーブル定義、インデックス
  - [ ] CRUD操作、検索機能
  
- [ ] `PostgreSQLMetadata`の実装
  - [ ] SQLAlchemy統合
  - [ ] コネクションプール
  
- [ ] `DynamoDBMetadata`の実装（オプション）
  - [ ] boto3統合

### Plugin Pattern

- [ ] `PluginRegistry`の実装
  - [ ] `register_storage()`, `register_metadata()`
  - [ ] `get_storage()`, `get_metadata()`
  - [ ] `discover_plugins()` - エントリーポイント発見
  
- [ ] プラグインインターフェースの定義
  - [ ] `StoragePlugin` (Protocol)
  - [ ] `MetadataPlugin` (Protocol)
  - [ ] `ValidatorPlugin` (Protocol)
  - [ ] `TransformerPlugin` (Protocol)

### Adapter Pattern

- [ ] `EdinetApiAdapter`の実装
  - [ ] `fetch_catalog()` - カタログ取得
  - [ ] `fetch_document()` - 文書取得
  - [ ] `fetch_metadata()` - メタデータ取得
  - [ ] リトライロジック
  - [ ] レート制限対応

---

## Phase 4: 公開APIの整備

### `fino/__init__.py`のエクスポート

```python
- [ ] Edinetクラスのエクスポート
- [ ] Collectionクラスのエクスポート
- [ ] Filingクラスのエクスポート
- [ ] FilingMetadataクラスのエクスポート
- [ ] CollectionSpecBuilderクラスのエクスポート
- [ ] FormatTypeのエクスポート
- [ ] DocumentTypeのエクスポート
- [ ] DocumentTypeEnumのエクスポート
- [ ] SpecFieldのエクスポート
- [ ] FinoConfigのエクスポート
- [ ] 例外クラスのエクスポート
- [ ] `__all__`リストの定義
- [ ] `__version__`の定義
```

### シンプルなAPI設計

- [ ] `Edinet`クラス
  - [ ] デフォルトコンストラクタ（引数なしで動作）
  - [ ] `sync_catalog()` - カタログ同期
  - [ ] `search(**conditions)` - 検索
  - [ ] `collect(**conditions)` - 収集
  - [ ] `get(document_id)` - 取得
  
- [ ] `Collection`クラス
  - [ ] `search(**conditions)` - 検索
  - [ ] `get(document_id)` - 取得
  - [ ] `all()` - 全件取得
  - [ ] `count(**conditions)` - 件数取得

### 型ヒントの完備

- [ ] 全ての公開関数・メソッドに型ヒント
- [ ] 戻り値の型ヒント
- [ ] ジェネリクスの活用（`list[Filing]`等）
- [ ] `py.typed`ファイルの配置

---

## Phase 5: 内部実装の整理

### 依存性の方向の確認

- [ ] 公開API → モデル → プラグインIF → 内部実装
- [ ] 内部実装は公開APIに依存しない
- [ ] 循環依存がないことを確認

### 内部モジュールの隠蔽

- [ ] `_internal`パッケージ内のモジュールは全て`_`プレフィックス
- [ ] `__init__.py`で内部シンボルをエクスポートしない
- [ ] ドキュメントに内部実装を記載しない

### コレクション管理の実装

- [ ] `CollectionManager`の実装
  - [ ] ストレージ・メタデータ戦略の注入
  - [ ] `collect_filing()` - 単一収集
  - [ ] `collect_batch()` - バッチ収集
  - [ ] エラーハンドリング
  - [ ] トランザクション管理

### バリデーターの実装

- [ ] `FilingValidator`の実装
  - [ ] `validate_metadata()` - メタデータ検証
  - [ ] `validate_spec()` - 仕様検証
  - [ ] `validate_filing()` - Filing検証
  - [ ] カスタムバリデーションルール

---

## Phase 6: 例外処理の統一

### 例外階層の定義

- [ ] `FinoException` - ベース例外
- [ ] `ValidationError` - バリデーションエラー
- [ ] `APIError` - API呼び出しエラー
- [ ] `StorageError` - ストレージエラー
- [ ] `MetadataError` - メタデータエラー
- [ ] `PluginError` - プラグインエラー

### エラーメッセージの改善

- [ ] 詳細なエラーメッセージ
- [ ] `details`辞書で追加情報
- [ ] スタックトレースの保持
- [ ] ユーザー向けの解決策の提示

### エラーハンドリング

- [ ] API呼び出しのリトライ
- [ ] 部分的な失敗の処理（`CollectResult`）
- [ ] ロギングの統合
- [ ] デバッグ情報の出力

---

## Phase 7: テストの整備

### ユニットテスト

- [ ] Pydanticモデルのバリデーションテスト
- [ ] Factoryのテスト
- [ ] Builderのテスト
- [ ] Validatorのテスト
- [ ] Strategyのテスト

### 統合テスト

- [ ] EDINET API統合テスト（モック使用）
- [ ] ストレージ統合テスト（各バックエンド）
- [ ] メタデータストア統合テスト（各バックエンド）
- [ ] エンドツーエンドテスト

### プラグインテスト

- [ ] プラグイン登録のテスト
- [ ] プラグイン発見のテスト
- [ ] カスタムプラグインのテスト

### 型チェック

- [ ] `mypy --strict`で全モジュールチェック
- [ ] 型エラーの修正
- [ ] `py.typed`の配置確認

---

## Phase 8: ドキュメント整備

### APIドキュメント

- [ ] 公開クラスのdocstring
- [ ] 公開メソッドのdocstring
- [ ] 型ヒントの説明
- [ ] 使用例の追加
- [ ] Sphinx/MkDocsでドキュメント生成

### チュートリアル

- [ ] クイックスタート
- [ ] 基本的な使い方
- [ ] カスタムプラグインの作成
- [ ] 設定のカスタマイズ
- [ ] トラブルシューティング

### 移行ガイド

- [ ] 既存コードからの移行手順
- [ ] 破壊的変更のリスト
- [ ] 互換性の維持方法

---

## Phase 9: パッケージング

### setup.py / pyproject.toml

- [ ] パッケージメタデータの設定
- [ ] 依存関係の定義
  - [ ] `pydantic >= 2.0`
  - [ ] `pydantic-settings`
  - [ ] `httpx`
  - [ ] オプショナル依存関係（boto3, sqlalchemy等）
- [ ] エントリーポイントの定義
  ```toml
  [project.entry-points."fino.storage"]
  local = "fino._internal.strategies.storage:LocalFileStorage"
  s3 = "fino._internal.strategies.storage:S3Storage"
  
  [project.entry-points."fino.metadata"]
  sqlite = "fino._internal.strategies.metadata:SQLiteMetadata"
  postgresql = "fino._internal.strategies.metadata:PostgreSQLMetadata"
  ```

### `py.typed`の配置

- [ ] `fino/py.typed` - 空ファイル
- [ ] mypy対応の確認

### README.md

- [ ] プロジェクト概要
- [ ] インストール方法
- [ ] クイックスタート
- [ ] 主要機能
- [ ] ライセンス

---

## Phase 10: 品質チェック

### コード品質

- [ ] `ruff check` - リンターチェック
- [ ] `ruff format` - フォーマッター
- [ ] `mypy --strict` - 型チェック
- [ ] カバレッジ >= 80%

### パフォーマンス

- [ ] バリデーションのオーバーヘッド計測
- [ ] バッチ処理の最適化
- [ ] メモリ使用量の確認

### セキュリティ

- [ ] APIキーの安全な管理
- [ ] 依存関係の脆弱性チェック
- [ ] 入力値のサニタイゼーション

---

## Phase 11: CI/CD

### GitHub Actions

- [ ] テスト自動化
- [ ] 型チェック自動化
- [ ] リンター自動化
- [ ] カバレッジレポート
- [ ] 自動リリース

### Pre-commit Hooks

- [ ] `ruff` - リンター
- [ ] `mypy` - 型チェック
- [ ] テスト実行

---

## Phase 12: リリース準備

### バージョニング

- [ ] セマンティックバージョニング採用
- [ ] CHANGELOGの作成
- [ ] 破壊的変更の明示

### PyPI公開

- [ ] テストPyPIで動作確認
- [ ] 本番PyPIに公開
- [ ] インストール確認

### ドキュメント公開

- [ ] Read the Docsにホスト
- [ ] GitHubリポジトリのREADME更新
- [ ] ブログ記事・リリースノート

---

## 完了条件

- [ ] 全てのチェック項目が完了
- [ ] テストが全てパス（カバレッジ >= 80%）
- [ ] `mypy --strict`がエラーなし
- [ ] ドキュメントが完備
- [ ] PyPIに公開済み
- [ ] 実際のプロジェクトで動作確認

---

## 推定工数

| Phase | 工数 | 備考 |
|-------|------|------|
| Phase 1-2 | 5-7日 | パッケージ再編成、Pydantic化 |
| Phase 3 | 3-5日 | デザインパターン実装 |
| Phase 4-5 | 3-4日 | 公開API整備、内部実装 |
| Phase 6 | 2-3日 | 例外処理統一 |
| Phase 7 | 5-7日 | テスト整備 |
| Phase 8 | 3-4日 | ドキュメント |
| Phase 9-12 | 2-3日 | パッケージング、リリース |
| **合計** | **23-33日** | 約1-1.5ヶ月 |

---

## 優先順位

### 高（MVP）

1. Phase 1-2: パッケージ再編成、Pydantic化
2. Phase 3: Factory/Builder実装
3. Phase 4: 公開API整備
4. Phase 7: 基本的なテスト
5. Phase 8: 最小限のドキュメント

### 中

6. Phase 3: Strategy/Plugin実装
7. Phase 5: 内部実装の整理
8. Phase 6: 例外処理統一
9. Phase 7: 包括的なテスト

### 低（将来）

10. Phase 9-12: パッケージング、リリース
11. 追加プラグインの実装
12. パフォーマンス最適化
