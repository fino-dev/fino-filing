---
slug: design
---
# Design overview

High-level architecture of fino-filing. The implementation follows these boundaries.

## Boundaries

| Boundary       | Role                                                                | Main types                                                                                                 |
| -------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Collection** | Facade for add/get/search; delegates to Storage, Catalog, Locator   | `Collection`                                                                                               |
| **Catalog**    | Index (DuckDB); index/get/search; Filing restore via FilingResolver | `Catalog`, `FilingResolver`                                                                                |
| **Storage**    | Persist and load content by path                                    | `Storage` (Protocol), `LocalStorage`                                                                       |
| **Locator**    | Resolve Filing → storage path (Strategy)                            | `Locator`                                                                                                  |
| **Filing**     | Document model; Field/Expr for schema and query                     | `Filing`, `Field`, `Expr`, `EDINETFiling`, `EDGARFiling`                                                   |
| **Collector**  | Fetch → parse → build_filing → add_to_collection (Template Method)  | `BaseCollector`, `EdinetCollector`, `EdgerFactsCollector`, `EdgerDocumentsCollector`, `EdgerBulkCollector` |

## Patterns in use

- **Facade**: `Collection` is the single entry for storage and search.
- **Strategy**: `Locator` (path resolution); Edger uses separate strategies by usage: Facts (JSON API), Documents (htm/iXBRL), Bulk.
- **Template Method**: `BaseCollector.collect()` defines the flow; subclasses implement fetch/parse/build_filing.
- **Adapter**: `Storage` protocol; `LocalStorage` adapts the file system.
- **Repository**: `Catalog` for index and search.

## Class diagram

A PlantUML class diagram is maintained in the repo:

- **Path**: `docs/docs/dev/design/architecture.puml` (or `design/architecture.puml`).

It describes Collection, Catalog, Storage, Locator, Filing, Field, Expr, Collector boundary, and error types. Render it with a PlantUML tool or IDE plugin to view.

## Further design docs

- **Collector boundary (用途別)**: [collector_strategy](/docs/dev/design/collector_strategy). Edger は EdgerFactsCollector / EdgerDocumentsCollector / EdgerBulkCollector の 3 本。実装は `src/fino_filing/collector/base.py`, `edger.py`。
- Field/DSL and DuckDB: see `filing/field.py` and `expr.py`; Catalog builds SQL from Expr.
