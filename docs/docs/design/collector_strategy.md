# Collector Boundary 設計方針

## 設計ゴール

- **開示ソースごとに適切な形式**でドキュメントを取得し、Collection に保存する
- 共通フローは BaseCollector に集約し、具体は EdinetCollector / EdgerCollector で実装する
- **開示ソースごとの挙動の違い**（Filing 型・config・API）は Edinet / Edger 側のクラスで定義・吸収する
- Edger は複数 API・データ形式に対応するため、Edinet に合わせて制限せず、**それぞれに適した形で別々に実装**する

---

## 1. 基本思想

### Collector の責務

- **BaseCollector**: 収集の共通フロー（fetch → parse → build_filing → add_to_collection）を定義するテンプレート
- **EdinetCollector / EdgerCollector**: 上記フローを開示ソースごとに実装し、Collection と連携する

### 開示ソース仕様の吸収

開示ソースごとの違いは **Edinet / Edger 系クラス** に閉じる。

- **Edinet**: EDINET 用の config・API・レスポンス形式・EDINETFiling への変換
- **EdgerSecApi / EdgerBulkData**: EDGAR 用の config・複数 API/形式ごとの取得・パース・EDGARFiling への変換

Collector の具体実装は、これらを**オーケストレーション**し、Collection への保存まで行う。

---

## 2. デザインパターン


| パターン                | 役割                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Template Method** | BaseCollector が `collect()` の骨格を定義し、`fetch_documents()` / `parse_response()` / `build_filing()` をサブクラスで差し替える |
| **Strategy**        | Edinet, EdgerSecApi, EdgerBulkData が「取得・パース・Filing 生成」の戦略を encapsulate する                                    |
| **Facade 連携**       | Collector は Collection（Facade）を利用し、add のみで保存する。インスタンス化の際にCollection Instanceを受け取ることでそのCollectionと連携するようにする   |


---

## 3. 責務分離


| 要素                         | 責務                                                    |
| -------------------------- | ----------------------------------------------------- |
| BaseCollector              | 共通フロー、Collection への add、テンプレートメソッドの定義                 |
| EdinetCollector            | Edinet のオーケストレーション、EDINET 用の fetch/parse/build_filing |
| EdgerCollector             | EdgerSecApi / EdgerBulkData のオーケストレーション、API/形式ごとの収集   |
| Edinet                     | EDINET の config・API・形式・EDINETFiling への to_filing      |
| EdgerSecApi                | SEC API 用の取得・パース・EDGARFiling への to_filing             |
| EdgerBulkData              | Bulk データ用の取得・パース・EDGARFiling への to_filing             |
| EdinetConfig / EdgerConfig | 開示ソースごとの設定（API base, timeout 等）                       |
| Collection                 | 保存・検索の窓口（既存 Facade）                                   |


---

## 4. Edger の複数 API/形式対応

Edger は Edinet より API やデータ形式が多様である。

- **Edinet に合わせて 1 本化して制限しない**
- **EdgerSecApi**（SEC API 等）、**EdgerBulkData**（Bulk データ等）のように、**用途ごとに別クラスで実装**する
- 各クラスが「自分に適した形式」で取得・パース・EDGARFiling 生成を行う
- EdgerCollector はこれらを保持し、必要に応じて Sec / Bulk などを切り替えたり組み合わせたりしてオーケストレーションする

これにより、Edinet 側の単純な 1 ソース 1 形式の前提に Edger を無理に合わせず、それぞれに適した形で収集できる。

---

## 5. フロー概要

```
BaseCollector.collect()
  → fetch_documents()     # 具体で実装（Edinet / EdgerSecApi / EdgerBulkData に委譲可）
  → parse_response(raw)   # 開示ソース形式ごとにパース
  → build_filing(parsed) # EDINETFiling / EDGARFiling を生成
  → add_to_collection(filing, content)  # Collection.add へ委譲
```

---

## 6. 設計原則まとめ

- 共通機能は BaseCollector、開示ソース固有は Edinet / Edger* に分離する
- Filing 型・config・API の違いは Edinet / Edger クラスで仕様として定義・吸収する
- Collector はそれらをオーケストレーションし、Collection とだけ連携する
- Edger は複数 API/形式を別クラスで実装し、それぞれに適した形で収集する
- 既存の Collection / Filing 境界はそのまま利用する

---

## 参照

- クラス関連図: [architecture.puml](./architecture.puml)（Collector Boundary）
- Field/DSL 設計: [field_type_strategy.md](./field_type_strategy.md)

