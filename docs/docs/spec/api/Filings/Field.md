---
sidebar_position: 2
title: Field
---

# Field

Descriptor and query DSL: defines field metadata and builds `Expr` for Catalog search (e.g. `Field("source") == "EDGAR"`).

## Constructor

```python
Field(
    name: str = "",
    _field_type: type | None = None,
    indexed: bool = False,
    immutable: bool = False,
    required: bool = False,
    description: str | None = None,
) -> Field
```

| Parameter     | Description                                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `name`        | Field name                                                                                                                            |
| `_field_type` | Python type for validation; in Filing subclasses this is often injected from `Annotated`                                              |
| `indexed`     | If True, Catalog stores as physical column and search uses column; else stored in JSON and search uses `json_extract(data, '$.name')` |
| `immutable`   | If True, value cannot be changed after init (Filing raises `FieldImmutableError`)                                                     |
| `required`    | If True, value must be set at init (Filing raises `FilingRequiredError` if missing/None)                                              |
| `description` | Optional description                                                                                                                  |

## Query DSL (return Expr)

Comparison: `==`, `!=`, `>`, `>=`, `<`, `<=`.

String: `contains(value: str)`, `startswith(value: str)`, `endswith(value: str)` (LIKE with `%`).

Set: `in_(values: list)`, `not_in(values: list)`.

Null: `is_null()`, `is_not_null()`.

Range: `between(lower, upper)`.

Examples:

```python
Field("source") == "EDGAR"
Field("form_type").in_(["10-K", "10-Q"])
Field("filing_date").between(d1, d2)
(Field("source") == "EDGAR") & (Field("form_type") == "10-K")
```

search/count での利用と・SQL 変換は [Collection Search](../../Collection-Search.md) を参照。

## Descriptor protocol

Used on Filing subclasses: `Field` is used inside `Annotated[str, Field(...)]`. On the class, `FilingClass.field_name` returns the `Field` (for building Expr); on the instance, `filing.field_name` returns the value.

## Method

| Method                               | Returns | Description                                                                   |
| ------------------------------------ | ------- | ----------------------------------------------------------------------------- |
| `validate_value(value: Any) -> None` | —       | Raises `FieldValidationError` if `value` is not compatible with `_field_type` |
