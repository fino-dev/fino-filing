# Field / DSL Design (DuckDB)

## Design goals

- Make full use of DuckDB’s **strong type system**
- **Type-safe DSL** driven by model definitions
- Allow **schema-less search** at the same time
- Do **not** expose concepts like “weak mode” to users

---

## 1. Core idea

### Field as “column reference”

Field:

- Holds a column name
- Exposes DSL operators
- Can hold type information when needed

But:

> Type is **not** required

---

## 2. Responsibility split (types)

| Element | Responsibility |
|---------|----------------|
| Annotated | Type declaration |
| Field | Metadata + DSL |
| Collection | Type resolution |
| SQL layer | DuckDB CAST strategy |

---

## 3. Type resolution strategy

### At model definition

```python
class Filing:
    revenue: Annotated[int, Field("revenue")]
```

At class analysis:

Inject `field._field_type = int`.

---

### Standalone Field in search

`Field("revenue") > 1_000_000`

- Type is None
- Collection context is used to resolve
- If unresolved, no CAST
- **Risk: type mismatch can yield unexpected query behavior**

---

### Standalone search with explicit type (optional)

`Field("revenue", _field_type=int) > 1_000_000`

- Enables DuckDB CAST
- Search without depending on the model

---

## 4. F() function

`def F(name: str) -> Field:` is considered unnecessary.

Reasons:

- Field itself is the column-reference DSL
- No need for a special “weak mode” concept
- Keeps the API simple

(Implementation may still have `F` in the field module; it is not in public `__all__`.)

---

## 5. No “weak mode” concept

Internally there is only the state:

`field._field_type is None`.

Users do **not** need to see:

- “weak mode”
- “strong mode”

---

## 6. DuckDB optimization

In DuckDB, JSON extraction is treated as VARCHAR.

So:

`json_extract(...) > 1000`

is unsafe.

When the type is known, generate:

`CAST(json_extract(...) AS BIGINT) > 1000`.

Comparing as string vs as integer changes semantics (e.g. string length vs numeric). To avoid mismatches with user intent, we need a way to specify type for standalone Field search.

---

## 7. Architecture (high level)

Model definition → Annotated parsing → Inject type into Field → Register with Collection → Build Expr → Collection resolves type → Generate DuckDB SQL with CAST

---

## 8. Principles

- Field is usable on its own
- Type is optional
- Type is resolved from context
- F() is unnecessary
- Use DuckDB types fully
- Do not expose internal “mode” to users

---

## Summary

Field = “named column reference”  
Type = “determined by context”  
DuckDB optimization = “responsibility of the SQL layer”

This gives: type-safe DSL, schema-less search, DuckDB optimization, and room for future extension.
