---
sidebar_position: 3
title: Expr
---

# Expr

WHERE-clause abstraction: holds a SQL fragment and bound parameters. Used by `Collection.search()` (via Catalog) to build DuckDB queries.

## Constructor

```python
Expr(sql: str, params: list[Any]) -> Expr
```

- **sql**: WHERE fragment (with `?` placeholders).
- **params**: Bind parameters in order.

## Attributes

| Attribute | Type      | Description    |
| --------- | --------- | -------------- |
| `sql`     | str       | WHERE fragment |
| `params`  | list[Any] | Parameters     |

## Operators

| Operator | Result | Example          |
| -------- | ------ | ---------------- |
| `&`      | AND    | `expr1 & expr2`  |
| `\|`     | OR     | `expr1 \| expr2` |
| `~`      | NOT    | `~expr`          |

Users typically build `Expr` via `Field` (e.g. `Field("source") == "Edgar"`), not by constructing `Expr` directly.

検索式の全体仕様・SQL 変換は [Collection Search](/docs/spec/Tutorial/Collection-Search) を参照。
