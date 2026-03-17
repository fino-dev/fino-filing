---
sidebar_position: 1
title: Catalog
---

# Catalog

DuckDB-backed index for filings. Stores core columns plus indexed fields as physical columns; extra fields in a JSON `data` column. Uses `FilingResolver` to restore Filing subclass from `_filing_class` (FQCN).

## Constructor

```python
Catalog(db_path: str, resolver: FilingResolver | None = None) -> Catalog
```

- **db_path**: Path to DuckDB file.
- **resolver**: Used to resolve `_filing_class` to a class on get/search. Defaults to `default_resolver` if `None`.

## Methods

### index

```python
index(filing: Filing) -> None
```

Inserts or replaces one filing. Adds physical columns for any new indexed fields of the filing’s class. Raises `CatalogRequiredValueError` if a core required value is missing/empty.

### index_batch

```python
index_batch(filings: list[Filing]) -> None
```

Bulk insert/replace. Ensures all indexed columns exist, then inserts in one batch.

### get

```python
get(id: str) -> Filing | None
```

Returns Filing instance (subclass resolved via resolver) or `None`.

### get_raw

```python
get_raw(id: str) -> dict[str, Any] | None
```

Returns merged dict (physical columns + `data` JSON) or `None`. No Filing instantiation.

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

WHERE from `expr`, ORDER BY `order_by` (column or `json_extract(data, '$....')`), LIMIT/OFFSET. Returns list of Filing instances. expr のコンパイル仕様は [Collection Search](../../Collection-Search.md) を参照。

### search_raw

```python
search_raw(sql: str, params: list[Any] | None = None) -> list[Any]
```

Executes raw SQL and returns fetched rows. Advanced use.

### count

```python
count(expr: Expr | None = None) -> int
```

Returns number of rows matching `expr` (or total if `expr` is None). expr のコンパイル仕様は [Collection Search](../../Collection-Search.md) を参照。

### stats

```python
stats() -> dict[str, Any]
```

Returns dict with keys e.g. `total`, `sources`, `earliest`, `latest`.

### clear

```python
clear() -> None
```

Deletes all rows.

### close

```python
close() -> None
```

Closes the DuckDB connection.
