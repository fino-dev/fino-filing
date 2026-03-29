---
sidebar_position: 3
title: FilingResolver
---

# FilingResolver

Resolves a fully qualified class name (`_filing_class`) to a Filing subclass. Used by Catalog when restoring filings from the index.

## Instance

**default_resolver**: Module-level `FilingResolver()` used by Catalog when no custom resolver is passed. `EDINETFiling`, `EDGARFiling`, and `EDGARCompanyFactsFiling` are registered in `fino_filing.__init__`.

## Methods

### register

```python
register(cls: type[Filing]) -> None
```

Registers a Filing subclass under `f"{cls.__module__}.{cls.__qualname__}"`.

### resolve

```python
resolve(name: str | None) -> type[Filing] | None
```

1. Look up `name` in the internal registry.
2. If not found, try dynamic import by the FQCN.
3. If resolved, cache in registry and return the class; otherwise return `None` (caller may fall back to base `Filing`).

## Helper

```python
register_filing_class(name: str, cls: type[Filing]) -> None
```

Registers `cls` under `name` on `default_resolver`. Kept for backward compatibility; prefer `default_resolver.register(cls)`.
