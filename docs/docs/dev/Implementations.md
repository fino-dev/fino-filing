---
sidebar_position: 3
title: Implementations
---

# Implementation overview

Summary of the current implementation by boundary. See [Codebase](/docs/dev/Codebase) for file locations.

## Collection boundary (Facade)

- **`Collection`** (`collection/collection.py`) — Single entry for add/get/search. Delegates to Storage, Catalog, and Locator.
  - **add(filing, content)**: Checks checksum, resolves path via Locator, indexes via Catalog (skip if same id), saves via Storage. Returns `(filing, path)`.
  - **get / get_filing / get_content / get_path**: Catalog for metadata, Locator for path, Storage for content.
  - **search(expr, limit, offset, order_by, desc)**: Delegates to `Catalog.search`. Uses Expr for WHERE.
- **Default setup**: If `storage`/`catalog` are not provided, uses `.fino/collection` under CWD with LocalStorage and Catalog(`index.db`).

## Catalog and indexing

- **`Catalog`** (`collection/catalog.py`) — DuckDB-backed index. Core columns: `id`, `source`, `checksum`, `name`, `is_zip`, `format`, `created_at`, `_filing_class`, `data` (JSON). Indexed fields from Filing are added as physical columns.
- **`FilingResolver`** (`collection/filing_resolver.py`) — Maps `_filing_class` (FQCN) to Filing subclass for restore. Built-in: register; fallback: dynamic import. `default_resolver` is used by Catalog; EDINETFiling and EDGARFiling are registered in `__init__.py`.
- **`register_filing_class`** — Convenience that registers a class with `default_resolver`.

## Storage and path

- **`Storage`** (`collection/storage.py`) — Protocol: `save(content, storage_key?)`, `load_by_path(relative_path)`, `base_dir`.
- **`LocalStorage`** (`collection/storages/local.py`) — Saves under `base_dir`; `storage_key` is optional (default behavior for compatibility).
- **`Locator`** (`collection/locator.py`) — Strategy: Filing → relative path. Default: `{source}/{id}{suffix}`; suffix from `format` or `is_zip` (e.g. `.xbrl`, `.zip`).

## Filing boundary

- **`Filing`** (`filing/filing.py`) — Document model with metaclass `FilingMeta`. Core fields: id, source, checksum, name, is_zip, format, created_at. Identity (for id generation) = core fields minus id/created_at/checksum plus any user-defined fields. Supports `to_dict` / `from_dict`, `get_indexed_fields()`, etc.
- **`Field`** (`filing/field.py`) — Descriptor and query DSL (e.g. `Field("x") == 1`, `in_()`, `between()`). Used in model definitions and in Expr.
- **`Expr`** (`filing/expr.py`) — WHERE abstraction: `sql` + `params`. Supports `&`, `|`, `~`. Catalog compiles to DuckDB.
- **`EDINETFiling`** / **`EDGARFiling`** — Built-in subclasses with source-specific fields; registered on `default_resolver`.

## Collector boundary

- **`BaseCollector`** (`collector/base.py`) — Template Method: `collect()` runs `fetch_documents()` → `parse_response(raw)` → `build_filing(parsed, raw)` → `add_to_collection(filing, content)`. Subclasses implement the three abstract methods.
- **`RawDocument`** — `content: bytes`, `meta: dict`. One item per fetch.
- **`Parsed`** — `dict[str, Any]`; intermediate before building a Filing.
- **Edger** (`collector/edger.py`): **EdgerConfig** (SEC/Bulk URLs, timeout, rate limit), **EdgerSecApi** (SEC Company Submissions API → EDGARFiling), **EdgerBulkData** (daily-index ZIPs → EDGARFiling), **EdgerCollector** (orchestrates strategies and calls `add_to_collection`).

## Errors

- **Core**: `FinoFilingException` (`core/error.py`).
- **Filing**: `FilingRequiredError`, `FieldValidationError`, `FieldImmutableError`, `FilingValidationError`, `FilingImmutableError` (`filing/error.py`).
- **Collection**: `CollectionChecksumMismatchError`, `LocatorPathResolutionError`, `CatalogRequiredValueError`, `CatalogAlreadyExistsError` (`collection/error.py`).

Public API and exception behavior are specified in [Spec: Exception](/docs/spec/api/Exception).
