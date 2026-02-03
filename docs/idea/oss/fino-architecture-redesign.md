# fino Architecture Redesign Analysis

## 現在の設計の課題分析

### 1. 公開APIと内部実装の分離が不明確
**問題点:**
- `application`、`domain`、`adapters`パッケージが全て同列に見える
- ユーザーがどのクラスを使うべきか不明確
- 内部実装の変更が公開APIに影響を与えやすい

**参考にすべきOSS:**
- **Pydantic**: `_internal/`ディレクトリで内部実装を完全分離
- **pytest**: `_pytest/`（内部）と`pytest/`（公開）の明確な分離

### 2. Clean Architecture的な層分離が過度
**問題点:**
- ライブラリにしては層が多すぎる（application/domain/adapters）
- シンプルさが失われている
- 小規模な変更にも多くのファイルを触る必要がある

**参考にすべきOSS:**
- **Typer**: シンプルな構造（main.py, core.py, models.py）
- **FastAPI**: 機能ごとのフラットな構造

### 3. 型安全性・バリデーションの仕組みが見えない
**問題点:**
- Pydanticモデルの使用が図に表現されていない
- バリデーションロジックの配置が不明確
- 型変換・正規化の責務が不明確

**参考にすべきOSS:**
- **Pydantic**: メタクラス、バリデーター、シリアライザーの明確な分離
- **FastAPI**: 型ヒントベースのバリデーション

### 4. 拡張ポイントが固定的
**問題点:**
- アダプター実装が固定的（EdinetApi, LocalFile, S3, SQLite, Dynamo）
- ユーザーが独自のバックエンドを追加しにくい
- プラグインシステムがない

**参考にすべきOSS:**
- **pytest**: 100以上のフックポイント、プラグイン発見メカニズム
- **FastAPI**: `dependency_overrides`、カスタムルートクラス

### 5. ファクトリー・ビルダーパターンの欠如
**問題点:**
- オブジェクト生成ロジックが散在
- 複雑な設定の構築方法が不明確
- テスト用のモックオブジェクト作成が困難

**参考にすべきOSS:**
- **Pydantic**: `create_model()`ファクトリー、`Field()`ファクトリー
- **Typer**: ファクトリー関数でClick型へ変換

## 改善方針

### 1. パッケージ構造の再編成
- **公開API**: `fino/__init__.py`でエクスポートするもののみ
- **内部実装**: `fino/_internal/`に完全分離
- **プラグイン**: `fino/plugins/`でインターフェース定義

### 2. デザインパターンの明示的な適用
- **Factory Pattern**: オブジェクト生成の一元化
- **Builder Pattern**: 複雑な設定の段階的構築
- **Strategy Pattern**: ストレージ・メタデータストアの切り替え
- **Plugin Pattern**: 拡張可能なバックエンド

### 3. 型安全性の強化
- Pydanticモデルの活用
- 値オブジェクトのイミュータブル化
- バリデーションロジックの明確化

### 4. 依存性の方向の整理
- 公開API → モデル → プラグインIF → 内部実装
- 内部実装は公開APIに依存しない

## 新しいアーキテクチャの特徴

### レイヤー構成

```
Layer 1: 公開API (fino.__init__.py)
  ↓
Layer 2: ドメインモデル (fino.models, fino.types)
  ↓
Layer 3: プラグインIF (fino.plugins)
  ↓
Layer 4: 内部実装 (fino._internal)
  ↓
Layer 5: 外部システム (EDINET API, Storage, Database)
```

### 依存性の方向
- 上位レイヤーが下位レイヤーに依存
- プラグインIFで依存性を逆転（DIP適用）
- 内部実装は公開APIに依存しない

### 拡張ポイント
- `StoragePlugin`: カスタムストレージバックエンド
- `MetadataPlugin`: カスタムメタデータストア
- `ValidatorPlugin`: カスタムバリデーション
- `TransformerPlugin`: カスタムデータ変換

これにより、成功したOSSライブラリと同等の設計品質を実現します。
