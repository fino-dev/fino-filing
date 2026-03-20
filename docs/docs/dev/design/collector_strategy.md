# Collector Boundary 設計方針

## 設計ゴール

- **開示ソースごとに適切な形式**でドキュメントを取得し、Collection に保存する
- 共通フローは BaseCollector に集約し、具体は各 Collector で実装する
- ユーザーは **用途別の Collector を選ぶだけ**でよく、内部クライアントの切り替えを意識しなくてよい
- EDGAR の **全エンドポイントは単一の EdgerClient** が担い、各 Collector がメソッド呼び出しを切り替えて用途に応じた収集を行う

---

## 1. 基本思想

### Collector の責務

- **BaseCollector**: 収集の共通フロー（fetch → parse → build_filing → add_to_collection）を定義するテンプレート
- **EdinetCollector**: EDINET 用。XBRL そのまま取得 → Collection → Arelle modeling → DB のパイプラインに対応
- **EdgerFactsCollector**: ファクト・概念など**構造化データ（JSON）**を取得。`client.get_company_facts()` / `get_submissions()` 等を呼び出す
- **EdgerDocumentsCollector**: **提出書類（htm / iXBRL）**を取得。`client.get_filing_document()` を呼び出す
- **EdgerBulkCollector**: **一括取得**。`client.get_bulk()` を呼び出す

### 単一 EdgerClient の方針

3 つの Collector はすべて同一の `EdgerClient` を持つ。

- CIK 解決・accession_number 取得など**全 Collector で必要な前段処理**を EdgerClient に集約する
- エンドポイントごとにメソッドを用意し（`get_submissions` / `get_company_facts` / `get_filing_document` / `get_bulk`）、Collector 側がどのメソッドを呼ぶかで用途を切り替える
- レート制限・リトライ・User-Agent ヘッダーの組み立ても EdgerClient が内部管理する

### 用途別命名（EDGAR）

| Collector | 用途 | 使用する EdgerClient メソッド（例） |
| --------- | ---- | ---------------------------------- |
| **EdgerFactsCollector** | ファクト・概念など構造化データを取る | `get_submissions`, `get_company_facts` |
| **EdgerDocumentsCollector** | 提出書類（ドキュメント）を取る | `get_filing_document` |
| **EdgerBulkCollector** | 一括取得 | `get_bulk` |

---

## 2. EdgerConfig の方針

EdgerClient に必要な設定は最小限に抑える。

| 設定項目 | 値の所在 | 理由 |
| -------- | -------- | ---- |
| `user_agent_email` | ユーザー指定（必須） | SEC は識別用メールアドレスを User-Agent に含めることを要求するため、ユーザーごとに inject する |
| `timeout` | ユーザー指定（任意・デフォルト有） | ネットワーク環境に応じてユーザーが調整できるよう残す |
| API ベース URL / レート制限設定 | package 側デフォルト | EDGAR の仕様に準拠する固定値のため package で管理し、ユーザーに露出しない |

---

## 3. デザインパターン

| パターン | 役割 |
| -------- | ----- |
| **Template Method** | BaseCollector が `collect()` の骨格を定義し、`fetch_documents()` / `parse_response()` / `build_filing()` をサブクラスで差し替える |
| **共有クライアント** | `EdgerClient` が全エンドポイントの HTTP インフラを一元提供。3 つの Collector が共有し、メソッドの呼び出しで用途を切り替える |
| **Facade 連携** | Collector は Collection（Facade）を利用し、add のみで保存する |

---

## 4. 責務分離

| 要素 | 責務 |
| ---- | ---- |
| BaseCollector | 共通フロー、Collection への add、テンプレートメソッドの定義 |
| EdinetCollector | Edinet のオーケストレーション、EDINET 用の fetch/parse/build_filing |
| EdgerFactsCollector | EdgerClient の facts 系メソッドを呼び出し、構造化データを Collection に保存する |
| EdgerDocumentsCollector | EdgerClient の document 系メソッドを呼び出し、提出書類を Collection に保存する |
| EdgerBulkCollector | EdgerClient の bulk 系メソッドを呼び出し、一括データを Collection に保存する |
| Edinet | EDINET の config・API・形式・EDINETFiling への to_filing |
| EdgerClient | EDGAR 全エンドポイント対応の共通 HTTP クライアント。CIK 解決・レート制限・リトライを内部管理 |
| EdinetConfig | EDINET の設定（api_base, timeout） |
| EdgerConfig | ユーザー固有設定のみ（user_agent_email, timeout）。API URL 等は package デフォルト |
| Collection | 保存・検索の窓口（既存 Facade） |

---

## 5. パイプラインの違い

| 用途 | 流れ |
| ---- | ---- |
| EDINET | ダウンロード（XBRL）→ Collection → Arelle modeling → DB |
| EDGAR Facts | JSON API → Collection → （Arelle 不要）→ 正規化 → DB |
| EDGAR Documents | htm/iXBRL → Collection → Arelle 等 → DB |
| EDGAR Bulk | Bulk → Collection → 形式に応じた処理 → DB |

---

## 6. 設計原則まとめ

- 共通フローは BaseCollector（Template Method）に集約する
- EDGAR の HTTP 処理は **EdgerClient に一元化**。CIK 解決・accession 取得などの前段処理も EdgerClient が担う
- ユーザーは**用途別の Collector を選ぶだけ**。Collector 側でメソッドを切り替えるため、ユーザーにクライアントの違いを意識させない
- EdgerConfig は**ユーザー固有設定のみ**（`user_agent_email` 必須）。API ベース URL やレート制限は package 管理とする
- 既存の Collection / Filing 境界はそのまま利用する

---

## 参照

- クラス関連図: [architecture.puml](./architecture.puml)（Collector Boundary）
- Design 概要: [Design](/docs/dev/design/design)
