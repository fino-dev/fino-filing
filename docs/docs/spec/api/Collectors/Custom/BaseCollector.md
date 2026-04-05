---
sidebar_position: 0
---

# BaseCollector

収集フローの抽象基底。拡張クラスは **`_fetch_documents`**, **`_parse_response`**, **`_build_filing`** を実装する。

## Constructor

```python
BaseCollector(collection: Collection) -> BaseCollector
```

## Methods（公開）

### iter_collect

```python
iter_collect(**criteria: Any) -> Iterator[tuple[Filing, str]]
```

`_fetch_documents(**criteria)` の各要素について `_parse_response` → `_build_filing(parsed, raw.content)` → `Collection.add` を行い、`(Filing, 保存先絶対パス)` を yield。

### collect

```python
collect(**criteria: Any) -> list[tuple[Filing, str]]
```

`list(iter_collect(**criteria))`。

## サブクラスで実装するメソッド

| Method | 説明 |
| ------ | ---- |
| `_fetch_documents(**kwargs)` | `Iterator[RawDocument]` |
| `_parse_response(raw: RawDocument)` | `Parsed` |
| `_build_filing(parsed: Parsed, content: bytes)` | `Filing` |

`criteria` / `kwargs` の意味は各 Collector が定義する（型安全のため具体クラスで `iter_collect` / `collect` をオーバーライドしてキーワード引数を固定している場合がある）。
