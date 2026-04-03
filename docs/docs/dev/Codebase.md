---
sidebar_position: 1
title: Codebase
---

# Codebase layout

## Package root

- **`src/fino_filing/`** — Main package. Public API is re-exported from `__init__.py` via `__all__`.

## Source structure

```
src/fino_filing/
├── __init__.py          # Public API (Collection, Filing, Catalog, Collector, etc.)
├── core/
│   └── error.py         # FinoFilingException base
├── collection/          # Collection boundary (Facade + storage/index)
│   ├── collection.py    # Collection (Facade)
│   ├── catalog.py      # Catalog (DuckDB index, search)
│   ├── filing_resolver.py  # FilingResolver, default_resolver, register_filing_class
│   ├── locator.py      # Locator (Filing → storage path)
│   ├── storage.py      # Storage Protocol
│   ├── storages/
│   │   └── local.py    # LocalStorage
│   └── error.py        # CollectionChecksumMismatchError, LocatorPathResolutionError, ...
├── filing/              # Filing boundary
│   ├── filing.py       # Filing, FilingMeta
│   ├── field.py        # Field (descriptor, DSL)
│   ├── meta.py         # FilingMeta implementation
│   ├── expr.py         # Expr (query expression)
│   ├── filing_edinet.py  # EDINETFiling
│   ├── filing_edger.py  # EDGARFiling, EDGARCompanyFactsFiling
│   └── error.py        # FilingRequiredError, FieldValidationError, ...
└── collector/           # Collector boundary
    ├── base.py         # BaseCollector, RawDocument, Parsed
    ├── edinet/         # EDINET 提出
    │   └── collector.py
    └── edger/          # SEC EDGAR（種別ごとサブパッケージ）
        ├── client.py
        ├── config.py
        ├── _helpers.py
        ├── archives/   # Archives 提出ファイル → EDGARFiling
        │   └── collector.py
        ├── facts/      # Company Facts → EDGARCompanyFactsFiling
        │   └── collector.py
        └── bulk/       # Bulk（スタブ）→ EDGARFiling
            └── collector.py
```
