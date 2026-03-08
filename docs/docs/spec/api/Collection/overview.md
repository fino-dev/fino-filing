---
sidebar_position: 0
title: Collection boundary
---

# Collection boundary

The **Collection** boundary provides add, get, and search over filings. It is a facade over Storage (bytes), Catalog (index), and Locator (Filing → path).

## Public types

| Type | Description |
|------|-------------|
| [Collection](./Collection) | Main entry: `add`, `get`, `get_filing`, `get_content`, `get_path`, `search` |
| [Catalog](./Catalog) | DuckDB-backed index; `index`, `get`, `search`, etc. |
| [Storage](./Storage) | Protocol: `save(content, storage_key?)`, `load_by_path(relative_path)`, `base_dir` |
| [LocalStorage](./LocalStorage) | Storage implementation: saves under `base_dir`; `storage_key` is required |
| [FilingResolver](./FilingResolver) | Resolves `_filing_class` (FQCN) to Filing subclass for Catalog restore; `default_resolver`, `register_filing_class` |

## Default setup

If `Collection()` is called without `storage` or `catalog`, it uses `.fino/collection` under the current working directory: `LocalStorage(base_dir)` and `Catalog(index.db)`.

## Flow

- **add(filing, content)**: Checks SHA256 vs `filing.checksum`, resolves path via Locator, indexes via Catalog (skip if same id), saves bytes via Storage. Returns `(filing, path)`.
- **get / get_filing / get_content / get_path**: Catalog for metadata, Locator for path, Storage for content.
- **search(expr, limit, offset, order_by, desc)**: Delegates to Catalog; Expr is compiled to DuckDB WHERE.
