# DuckDB前提における Field / DSL 設計方針まとめ

## 🎯 設計ゴール

- DuckDBの**強い型システムを最大活用**
- モデル定義ベースの**型安全DSL**
- 同時にスキーマレス検索も許容
- 「弱モード」などの概念をユーザーに露出しない

---

# 1️⃣ 基本思想

## Fieldは「列参照オブジェクト」

Fieldは：

- 列名を保持する
- DSL演算子を提供する
- 必要なら型情報も保持できる

しかし：

> 型は必須ではない

---

# 2️⃣ 型の責務分離

| 要素       | 責務               |
| ---------- | ------------------ |
| Annotated  | 型の宣言           |
| Field      | メタ情報 + DSL     |
| Collection | 型解決             |
| SQL生成層  | DuckDB向けCAST戦略 |

---

# 3️⃣ 型解決戦略

## モデル定義時

```python
class Filing:
    revenue: Annotated[int, Field("revenue")]
```

クラス解析時に：
`field._field_type = int`
を注入する。

---

単独Field検索時

Field("revenue") > 1_000_000

• 型はNone
• Collectionコンテキストで解決を試みる
• 解決不能ならCASTなし
• **型の不一致による期待する検索ができない懸念がある**

---

明示型付き単独検索（任意）

Field("revenue", \_field_type=int) > 1_000_000

• DuckDB用CASTが可能
• モデルに依存しない検索も可能

---

4️⃣ F()関数について

`def F(name: str) -> Field:` は設計上不要とする。

理由：
• Field自体が列参照DSL
• 特別な弱モード概念は不要
• APIを単純化できる

（実装には `F` が field モジュールに残っているが、公開API `__all__` には含めていない。）

---

5️⃣ 「弱モード」という概念は不要

内部的には：

`field._field_type is None`
という状態があるだけ。

ユーザーに：
• 弱モード
• 強モード
といった概念を見せる必要はない。

---

6️⃣ DuckDB最適化戦略

DuckDBではJSON抽出はVARCHAR扱いになる。

よって：
`json_extract(...) > 1000`
は危険。

型が分かる場合：
`CAST(json_extract(...) AS BIGINT) > 1000`
を生成する。

例えば文字列の場合数値と比較すると文字数での検索になるが、Intの場合は数値としての比較演算になる。
このような違いは、Userの意図と乖離する結果を引き起こす原因となるので、Field単独検索時にも型定義方法を提供する必要がある

---

7️⃣ 最終アーキテクチャ

Model定義
↓
Annotated解析
↓
Fieldに型注入
↓
Collection登録
↓
Expr生成
↓
Collectionが型解決
↓
DuckDB用CAST付きSQL生成

---

8️⃣ 設計原則まとめ

✅ Fieldは単体で使用可能
✅ 型は必須にしない
✅ 型はコンテキスト解決
✅ F()は不要
✅ DuckDBの型を最大活用する
✅ ユーザーに内部モード概念を露出しない

---

🔥 最終思想

Fieldは「名前付き列参照」
型は「コンテキストで決まる」
DuckDB最適化は「SQL生成層の責務」

この設計により：
• 型安全DSL
• スキーマレス検索
• DuckDB最適化
• 将来的な拡張性

すべてを両立できる。
