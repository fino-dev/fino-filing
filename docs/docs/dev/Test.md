---
sidebar_position: 5
title: Test
---

## Test Strategy

the Test is writtten as one of spec of this package. Therefore, all test case need to define how this pakcage should behaive.
the Module Test strategy us ti cinorehensively cover all behavior not class construction. and
The Scenario test strategy is to comprehensively cover critical use cases, exception patterns, and architectural boundaries.

## Test Module

- **`test/`** — pytest root (`pyproject.toml`: `testpaths = ["test"]`).
- **`test/module/`** — Unit/integration by layer:
  - `collection/` — Collection, Catalog, Locator, FilingResolver, storages
  - `filing/` — Filing, Field, Expr, EDINETFiling, EDGARFiling
  - `collector/` — BaseCollector, EdgerCollector, EdgerSecApi, EdgerBulkData
  - `core/` — Core errors
- **`test/scenario/`** — Scenario-style tests (e.g. collection flow).
- **`test/conftest.py`** — Shared fixtures.

## Dependencies

- **Runtime**: `duckdb` (Catalog index).
- **Test**: `pytest`, `pytest-cov`, `moto[s3]` (see `[dependency-groups]` in `pyproject.toml`).
