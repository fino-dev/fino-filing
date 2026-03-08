---
sidebar_position: 4
title: Design
---

# Design overview

High-level architecture of fino-filing. The implementation follows these boundaries.

## Boundaries

| Boundary       | Role                                                                | Main types                                                        |
| -------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **Collection** | Facade for add/get/search; delegates to Storage, Catalog, Locator   | `Collection`                                                      |
| **Catalog**    | Index (DuckDB); index/get/search; Filing restore via FilingResolver | `Catalog`, `FilingResolver`                                       |
| **Storage**    | Persist and load content by path                                    | `Storage` (Protocol), `LocalStorage`                              |
| **Locator**    | Resolve Filing → storage path (Strategy)                            | `Locator`                                                         |
| **Filing**     | Document model; Field/Expr for schema and query                     | `Filing`, `Field`, `Expr`, `EDINETFiling`, `EDGARFiling`          |
| **Collector**  | Fetch → parse → build_filing → add_to_collection (Template Method)  | `BaseCollector`, `EdgerCollector`, `EdgerSecApi`, `EdgerBulkData` |

## Patterns in use

- **Facade**: `Collection` is the single entry for storage and search.
- **Strategy**: `Locator` (path resolution); Edger uses separate strategies for SEC API vs Bulk.
- **Template Method**: `BaseCollector.collect()` defines the flow; subclasses implement fetch/parse/build_filing.
- **Adapter**: `Storage` protocol; `LocalStorage` adapts the file system.
- **Repository**: `Catalog` for index and search.

## Class diagram

A PlantUML class diagram is maintained in the repo:

- **Path**: `docs/docs/dev/design/architecture.puml` (or `design/architecture.puml`).

It describes Collection, Catalog, Storage, Locator, Filing, Field, Expr, Collector boundary, and error types. Render it with a PlantUML tool or IDE plugin to view.

## Further design docs

- Collector boundary and Edger multi-API strategy: see design notes in `src/fino_filing/collector/base.py` and `edger.py`.
- Field/DSL and DuckDB: see `filing/field.py` and `expr.py`; Catalog builds SQL from Expr.
