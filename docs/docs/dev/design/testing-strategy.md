---
sidebar_position: 4
title: Testing strategy
---

## Layers

- **`test/module/`** — Behavior per class or public API (including mocked collectors and Collection integration).
- **`test/scenario/`** — End-to-end **user stories** across public APIs only. Each file is one independent use case. Assertions focus on outcomes users care about (saved, searchable, retrievable).

## Scenario policy

- **No live SEC or EDINET HTTP** in default scenarios (stable CI). Collectors use mocked clients and fixture payloads shared with module tests.
- **Omitted by design**: scenarios that would call slow bulk APIs or other long-running external endpoints. Those flows stay in `test/module/` with mocks.

## Fixture sharing

- `test/conftest.py` uses `pytest_plugins` to load `module.collector.conftest` (e.g. `edgar_config`), `module.collector.edgar.conftest`, and `module.collector.edinet.conftest`, so scenario and collector tests share the same JSON payloads without duplication. Root `temp_collection` remains a plain `Collection`; `test/module/collector/conftest.py` still overrides it with `(Collection, Path)` under `test/module/collector/`.

## Optional live network

- If you add real-HTTP smoke tests later, mark them with `@pytest.mark.network` and exclude them from default runs (see `pytest.toml`).
