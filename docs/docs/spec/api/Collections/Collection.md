---
sidebar_position: 0
title: Collection
---

# Collection

Facade for adding, retrieving, and searching filings. Delegates to Storage, Catalog, and Locator.

## Constructor

```python
Collection(
    storage: Storage | None = None,
    catalog: Catalog | None = None,
    locator: Locator | None = None,
) -> Collection
```

If `storage` or `catalog` is `None`, default is `.fino/collection` under CWD: `LocalStorage(default_dir)` and `Catalog(default_dir / "index.db")`. `locator` defaults to `Locator()`（相対パス: `{source}/{id}` + 拡張子は `format` / `is_zip` から決定）。

## Methods

### add

```python
add(filing: Filing, content: bytes) -> tuple[Filing, str]
```

- Verifies `hashlib.sha256(content).hexdigest() == filing.checksum`; otherwise raises `CollectionChecksumMismatchError`.
- Resolves path via Locator; raises `LocatorPathResolutionError` if resolution fails.
- If `filing.id` already exists in Catalog: index step is skipped, storage is overwritten.
- **Returns**: `(filing, path)` where `path` is the path where content was saved (absolute path from Storage).

### get

```python
get(id: str) -> tuple[Filing | None, bytes | None, str | None]
```

Returns `(filing, content, path)`. All three are `None` if `id` is not found.

### get_filing

```python
get_filing(id: str) -> Filing | None
```

Metadata only. Returns `None` if not found.

### get_content

```python
get_content(id: str) -> bytes | None
```

Raw content only. Returns `None` if not found or path/content unavailable.

### get_path

```python
get_path(id: str) -> str | None
```

Resolved storage path only. Returns `None` if filing not found or path cannot be resolved.

### search

```python
search(
    expr: Expr | None = None,
    limit: int = 100,
    offset: int = 0,
    order_by: str = "created_at",
    desc: bool = True,
) -> list[Filing]
```

Catalog に委譲。`expr` に Python の `bool` を渡すと `CatalogExprTypeError`。`order_by` はコア列・インデックス列、または `data` JSON 内キー。戻り値は `Filing` のリスト。
