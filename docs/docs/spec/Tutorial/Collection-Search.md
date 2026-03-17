---
sidebar_position: 1
title: Collection Search
---

# Collection Search Tutorial

This article explains how to specify search conditions with `Collection.search(expr=...)`, with examples.

## Basic usage

Without any condition, `search` returns up to `limit` filings that are stored in the collection.

```python
results = collection.search(limit=10, offset=0)
```

You can control sort order with `order_by` and `desc` (default is `created_at` descending).

## Specifying conditions (expr)

Pass an **Expr** as `expr` to return only filings that match that condition. You build an Expr from **Field** operations.

```python
from fino_filing import Field

# Only filings whose source is "EDGAR"
results = collection.search(expr=(Field("source") == "EDGAR"), limit=10)
```

Use the same field names as in your Filing class (e.g. for `EDGARFiling`: `source`, `form_type`, `name`).

## Types of conditions

**Comparison** (`==`, `!=`, `>`, `>=`, `<`, `<=`):

```python
Field("source") == "EDGAR"
Field("created_at") >= start_date
```

**String** (contains / startswith / endswith):

```python
Field("name").contains("10-K")   # LIKE '%10-K%'
Field("name").startswith("annual_")
Field("name").endswith(".xml")
```

**Set** (IN / NOT IN):

```python
Field("source").in_(["EDGAR", "EDINET"])
Field("form_type").not_in(["OTHER"])
```

**Null**:

```python
Field("optional_field").is_null()
Field("required_field").is_not_null()
```

**Range**:

```python
Field("created_at").between(lo, hi)
```

## Compound conditions (AND / OR / NOT)

Combine multiple conditions into **one Expr** and pass it to `search`.

- **AND**: `&`
- **OR**: `|`
- **NOT**: `~`

```python
# source is EDGAR and name contains "10-K"
expr = (Field("source") == "EDGAR") & (Field("name").contains("10-K"))
results = collection.search(expr=expr, limit=10)

# source is EDGAR or EDINET
expr = (Field("source") == "EDGAR") | (Field("source") == "EDINET")
results = collection.search(expr=expr, limit=10)
```

## Counting matches (count)

Pass the same `expr` to `count` to get the number of matching filings.

```python
n = collection.count(expr=(Field("source") == "EDGAR"))
```

## See also

- How expressions are compiled (Expr → SQL, indexed fields): [Search Expression](../Search-Expression.md).
- API reference: [Field](../api/Filings/Field.md), [Expr](../api/Filings/Expr.md), [Collection](../api/Collections/Collection.md).
