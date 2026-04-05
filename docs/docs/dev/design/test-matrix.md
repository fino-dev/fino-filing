---
sidebar_position: 5
title: Test matrix (overview)
---

High-level mapping only. Detailed behavior remains in `test/module/` and `test/scenario/` sources.

| Area | Module tests | Scenario tests |
|------|----------------|----------------|
| Collection (add / search / get) | `test/module/collection/` | `test/scenario/collection/` (Expr/custom/relocate 含む) |
| Filing / Field / Expr | `test/module/filing/` | — |
| Edgar Facts collector | `test/module/collector/edgar/facts/` | `test/scenario/edgar/test_facts_collect_mocked.py` |
| Edgar Archive collector | `test/module/collector/edgar/archive/` | `test/scenario/edgar/test_archive_collect_mocked.py` |
| Edgar Bulk collector | `test/module/collector/edgar/bulk/` | — (external bulk API; no scenario) |
| EDINET collector | `test/module/collector/edinet/` | `test/scenario/edinet/test_collect_mocked.py` |

## Exceptions

- Contract for raised errors: [Exception](/docs/spec/api/Exception).
