# Field クラスアクセスで Expr 左辺を可能にする設計

## 目的

- `EDINETFiling.source == "EDINET"` のように、デフォルト値を持つフィールドでもクラスアクセスで Expr を組み立てられるようにする。
- 既存の `Field("source") == EDINETFiling.source`（右辺でクラス定数として使う）は維持する。

## 現状

- クラスアクセス時、`_defaults` にそのフィールドがあれば **default の値**を返し、無ければ **Field** を返す（`field.py` の `__get__`）。
- このためデフォルトありのフィールドは左辺に置けず、`EDINETFiling.source == "EDINET"` は `True` になり Expr にならない。

## 方針: デフォルト付き Field 参照オブジェクト（案B）

クラスアクセスで default を返す代わりに、**「Field 参照 + デフォルト値」を持つオブジェクト**を返す。

- **左辺**: `EDINETFiling.source == "EDINET"` → 参照オブジェクトの `__eq__` が内部 Field に委譲し、`Field.__eq__("EDINET")` と同様の Expr を返す。
- **右辺**: `Field("source") == EDINETFiling.source` → `Field.__eq__` に渡る比較値が参照オブジェクトなので、**比較用リテラルを取り出すプロトコル**を用意し、その値で Expr を組み立てる。

後方互換の観点では「クラスアクセスで得るもの」の型が「値だけ」から「参照オブジェクト（値も取り出し可能）」に変わるが、右辺では従来どおり「値として解釈」できるようにするため、既存の検索式はそのまま動くようにする。

## 技術メモ

1. **参照オブジェクト**
  - 責務: 左辺では Field と同様に比較/文字列/集合演算を委譲して Expr を返す。右辺では「Expr に埋め込むリテラル」を返す。
  - 属性: 内部に `Field` と default の `value` を保持。
  - プロトコル: 右辺用に `__filing_expr_value__() -> Any` を定義し、Expr 生成時にこの戻り値をパラメータとして使う（Field の `_create_expr` 等で value を resolve する際に利用）。
2. **Field 側の変更**
  - `__get__`: `obj is None` かつ `self.name in defaults` のとき、default 値ではなく上記参照オブジェクトを返す。
  - Expr 生成パス（`_create_expr` または各 `__eq__` 等）で、比較値に `__filing_expr_value__` があれば呼び出してリテラルに変換してから SQL/params を組み立てる。
3. **参照オブジェクトの演算**
  - `__eq__`, `__ne__`, `__gt__`, `__ge__`, `__lt__`, `__le__` → いずれも内部 `field` の同メソッドに委譲。
  - `contains`, `startswith`, `endswith`, `in_`, `not_in`, `is_null`, `is_not_null`, `between` も同様に委譲。
  - 委譲先は `self.field` なので、indexed や name は既存の Field のまま利用される。
4. **公開範囲**
  - 参照オブジェクトは Field と Expr の利用者からは「クラスアクセスで得られる何か」としてだけ触れる。`__all__` に載せるかは任意（型ヒントや doc で言及するなら公開してもよい）。

## 実装単位とテスト

- **実装**: `field.py` を中心（参照オブジェクトのクラス、`Field.__get__` の変更、`_create_expr` 等での value resolve）。必要なら `expr.py` は触らず、value の resolve は Field 内で完結させる。
- **テスト**:
  - 既存: `test_search.py` の `Field("source") == EdgarFiling.source`、`test_filing_field.py` の `Filing.source` が Field であること。
  - 追加: デフォルトありサブクラスでクラスアクセスすると参照オブジェクトが返ること（または少なくとも `EDINETFiling.source == "EDINET"` が Expr になり、search で 1 件取れること）。右辺 `Field("source") == EDINETFiling.source` が従来どおり 1 件返ることを再確認。
- **シナリオ**: `collect_edgar_facts/test_1.py` と同様に、`EDINETFiling.source == "EDINET"` で search するケースを 1 件追加してもよい。

## ドキュメント

- `docs/docs/spec/api/Filings/Field.md`: クラスアクセス時に「Field またはデフォルト付き参照を返す」旨と、左辺・右辺の両方で Expr に使えることを追記。
- `docs/docs/spec/Tutorial/Collection-Search.md`: モデルベースの例として `EDINETFiling.source == "EDINET"` を追記（実装後に実施でよい）。

## 実施順序

1. 設計の確定（本ドキュメントのレビュー）
2. 参照オブジェクトのクラスと Field の変更（実装）
3. 上記テストの追加・既存テストの実行
4. ドキュメント更新

