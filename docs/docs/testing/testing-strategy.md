# テスト戦略（観点・ケース・ツール）

## 0. テスト docstring 規約

- **テストクラス**: 被テスト対象を明示し、観点（正常系 / 異常系 / 境界）のうちどれを主に確認するかを1行で書く。
- **テストメソッド（異常系）**: 「仕様: （仕様の一文）」を必須とする。検証内容（例外型・戻り値・属性のうち何を assert するか）を書くとよい。
- **テストメソッド（正常系）**: 何を確認するかを1行で書く。

## 1. テストが確認すべき観点

### 1.1 観点の分類

| 観点 | 内容 | 現状の例 |
|------|------|----------|
| **正常系** | 契約どおりの入力で期待どおりの出力・副作用 | add/get/get_content, to_dict/from_dict, get_indexed_fields |
| **異常系** | 不正入力・欠損・型違いで適切な例外・戻り値 | FilingRequiredError, FieldValidationError, get_not_found |
| **境界・エッジ** | 空・None・空文字・最小/最大・重複 | test_none (explicit None), 重複 id は TODO |
| **契約・不変条件** | 永続化後の復元同一性、checksum 一致、immutable 違反 | add→get の roundtrip, checksum mismatch 例外 |
| **公開API** | `__all__` で公開しているクラス・関数の振る舞い | 各 module テストで一部対応。Expr, Resolver, EDGAR は未 or 薄い |

### 1.2 レイヤ別の重点

- **Filing / Field / Meta**: 正常・異常・境界（必須/省略可能/immutable/default）を網羅。型・メッセージまで断言。
- **Collection / Catalog**: 正常系に加え、not_found・checksum 不一致・重複 id（仕様確定後）。統合テスト寄りで可（AGENTS.md）。
- **Locator / Storage**: 拡張子・partition・storage_key の組み合わせ。異常系（不正 path 等）は必要に応じて。
- **FilingResolver**: register → resolve の対応、None/未登録、動的インポート成功・失敗。
- **Expr**: AND/OR/NOT の結合と params の順序・内容。Catalog の search との結合は統合で確認。

### 1.3 Collection の位置づけ

- **Collection はファサード**のため、単体ではテストしない。Collection の公開メソッド（add, get, get_filing, get_content, get_path, search）は、実の LocalStorage・Catalog・Locator を組み合わせた**結合テスト**で検証する。
- 委譲先（Catalog, Locator, LocalStorage）はそれぞれ単体でテストする。Collection のテストでは「ファサードとしての振る舞い」に集中する。

### 1.4 公開契約ベースのスコープ

- テストすべきは**実装の全パターン**ではなく、**公開API の契約として意味のあるパターン**に限定する。
- 同値類は代表値1つで代表し、`@pytest.mark.parametrize` で「同じロジック・異なる入力」をまとめる。

---

## 2. ケースの追加・再構成で心がけること

### 2.1 追加すべきケース（抜け・TODO の解消）

- **異常系の明確化**
  - `Collection.add`: 同一 id の重複追加（仕様: 上書き or 例外）→ テストで仕様を固定。
  - `get_content`: checksum 不一致時に `CollectionChecksumMismatchError` が発生する経路のテスト。
- **未カバー・薄いモジュール**
  - **Expr**: `__and__` / `__or__` / `__invert__` の結合結果（sql/params）のテスト。必要なら `Catalog.search(expr=...)` との統合。
  - **FilingResolver**: `register` → `resolve` 一致、`resolve(None)` → None、未登録名 → 動的解決 or None。`register_filing_class` の後方互換。
  - **EDGARFiling**: EDINETFiling と同様の init/roundtrip が 1 本あると安心。
  - **Catalog**: index_batch, search の limit/offset/order、count, clear（既存 module で触っていないメソッドの最低 1 本）。
- **コメントアウトされているシナリオ**
  - `test/scenario/collection/test_collection.py`, `test/module/collection/collection/test_init.py` の search 系、`test_search.py` の search 復元型。
  - 仕様が固まっていれば有効化し、未実装なら「未実装であること」をテストで明示するか、スキップで意図を残す。

### 2.2 再構成で揃えたいこと

- **クラス・メソッド単位の責務**: 1 テストクラス＝1 被テストクラス（または 1 メソッド群）。docstring で「正常系/異常系/境界」を一言書く。
- **parametrize の活用**: 同じロジックで入出力だけ変えるケース（例: 複数 Exception の message/attributes、複数 format の拡張子）は `@pytest.mark.parametrize` でまとめ、ケースの追加がしやすくする。
- **fixture の型**: `sample_filing` などは戻り値の型を `tuple[Filing, bytes]` と明示（conftest で既に利用しているので型ヒントを統一）。

---

## 3. カバレッジ

### 3.1 導入の是非

- **推奨する**: テストが「どのコードを通したか」を可視化できる。未テストのブランチ（特に異常系・エラーハンドリング）の洗い出しに有効。
- **目標の置き方**: いきなり 100% は不要。まずは **行カバレッジ** を計測し、**公開API（`__all__` のモジュール）とエラー経路** を重点的に上げる。
- **ツール**: `pytest-cov`。`pyproject.toml` の `[tool.pytest.ini_options]` と `[dependency-groups] test` に追加。

例（pyproject.toml）:

```toml
[tool.pytest.ini_options]
addopts = "--tb=short"
testpaths = ["test"]

[tool.coverage.run]
source = ["src/fino_filing"]
branch = true

[tool.coverage.report]
exclude_lines = ["pragma: no cover", "def __repr__", "raise NotImplementedError"]
```

- **branch カバレッジ**: 条件分岐の true/false を両方見たい場合に有効。まずは line のみでも可。

### 3.2 運用

- CI で `pytest --cov` を回し、閾値は「下げない」程度の緩い値（例: 80%）から始め、抜けているファイルを優先してテスト追加。

---

## 4. Mutation テスト

### 4.1 導入の是非

- **目的**: テストが「実装の変更」を検知できるかを見る。コードを意図的に壊して（mutate）テストが落ちるかで、テストの「有効性」を測る。
- **推奨**: カバレッジで「通った行」を押さえたあと、**信頼性をさらに高めたいモジュール**（Filing の検証・永続化・復元、Expr の結合、Resolver）に限定して導入するのが現実的。全体に毎回かけると実行時間が伸びる。
- **ツール**: `mutmut` が一般的。`pip` で追加し、対象パスを限定して実行する。

例:

```bash
mutmut run --paths-to-mutate=src/fino_filing/filing/ --runner "pytest test/module/filing -x"
```

### 4.2 運用

- まずは手動で週次や PR 前などに実行。mutation が「生き残る」（テストが落ちない）場合は、その箇所に対するテストを 1 本追加するか、その mutation を無視するかを判断。
- カバレッジと同様、CI に載せる場合は対象パスを絞り、タイムアウトを設けるとよい。

---

## 5. 優先順位の目安

1. **観点の埋め**: 異常系・境界（重複 id, checksum, None/未登録）の仕様を決め、テストで明示する。
2. **未カバー API**: Expr, FilingResolver, EDGARFiling, Catalog の主要メソッドに最低 1 本ずつ。
3. **parametrize と docstring**: 既存テストの重複を減らし、観点を docstring で揃える。
4. **カバレッジ導入**: pytest-cov で計測を始め、公開APIとエラー経路を重点的に上げる。
5. **Mutation**: コア（filing, expr, resolver）に限定して試し、生き残り mutation からテストを追加。

---

## 6. 参照

- [test-matrix.md](test-matrix.md): 公開API×観点ごとのテスト対応表。
- AGENTS.md: pytest 前提、新規ユースケースにテスト追加、adapters 層は統合テスト寄りで可。
- docs/archive/collection/scenario.md: Collection の利用シナリオ。シナリオテストの意図の基準。
