# 設計ルール

本プロジェクトは「軽量DDD + Clean Architecture」を採用する。

## レイヤー構成

以下の3層構成を採用する：

- domain  
  - 純粋なドメインモデル
  - Entity / ValueObject / Repository Interface を配置
  - 外部ライブラリやDBには依存しない

- application  
  - ユースケースを実装する層
  - domainのモデルとRepository interfaceを使用する
  - Facadeクラス（Edinet）はこの層に配置する

- adapters  
  - 外部システムとの接続を担当
  - EDINET API クライアント
  - 永続化実装（SQLite, DynamoDBなど）
  - domain/application に依存してよいが、逆方向の依存は禁止

依存方向：
domain ← application ← adapters

---

## Repository設計

- Repositoryのインターフェースは domain 層に定義する
- 実装クラスは adapters 層に配置する
- 実装は以下を想定する：
  - Local: SQLite（デフォルト）
  - Cloud: DynamoDB（将来拡張）

---

## 内部データストアの位置づけ

内部DBはキャッシュではなく「準公式データストア」として扱う。

- 初回はEDINET APIからフル同期
- 2回目以降は差分同期を基本とする
- 既存データは原則上書きしない（document_id単位で冪等性を確保）
- API上で削除されたデータもローカルからは削除しない

---

## EDINET APIクライアント

- adapters層に実装する
- 一部機能は application層の Facade 経由で公開APIとして利用可能にする
- 低レベルAPIクライアントは直接ユーザーに公開しない

---

## 公開APIポリシー

- 利用者が操作するのは Facade クラスのみ
- Facade以外のクラスは「内部実装」とみなす
- `__init__.py` にて公開範囲を明示的に制御する