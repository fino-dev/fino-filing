---
sidebar_position: 5
title: Test
---

## Test strategy

Tests are part of the package specification: each case documents expected behavior.

- **Module tests** — Cover behavior per class or API surface (including mocks), not constructors alone.
- **Scenario tests** — One **independent user story** per module under `test/scenario/` (Collection setup → persist → search/get). They avoid live SEC/EDINET HTTP; slow bulk-style APIs are not exercised here. See [testing-strategy](/docs/dev/design/testing-strategy) and [test-matrix](/docs/dev/design/test-matrix).

## Layout

- **`test/`** — pytest root (`pytest.toml`: `testpaths = ["test"]`).
- **`test/module/`** — By layer:
  - `collection/` — Collection, Catalog, Locator, FilingResolver, storages
  - `filing/` — Filing, Field, Expr, EDINETFiling, EdgarFiling
  - `collector/` — BaseCollector, EdinetCollector, EdgarFactsCollector, EdgarArchiveCollector, EdgarBulkCollector, etc.
  - `core/` — Core errors
- **`test/scenario/`** — Use-case scenarios (mirrors [Scenarios](/docs/spec/Usecase/scenarios) and [Quick start](/docs/spec/Quick-start) flows where applicable).
- **`test/conftest.py`** — Shared fixtures and `pytest_plugins` for collector response payloads used by scenarios and module collector tests.

## Dependencies

- **Runtime**: `duckdb` (Catalog index).
- **Test**: `pytest`, `pytest-cov`, `moto[s3]` (see `[dependency-groups]` in `pyproject.toml`).
